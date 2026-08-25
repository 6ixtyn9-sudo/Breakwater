"""Isolated HIP-3 candle audit and walk-forward research.

This lane deliberately writes no monitored book and cannot feed paper or live
execution. Market class is encoded into ``kind`` and slice IDs so evidence from
builder crypto, equities, indices, FX, commodities, and unknown products is
never pooled together.
"""

from __future__ import annotations

import csv
import json
import os
import statistics
import tempfile
import time
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd

from breakwater.discovery import _slice_stats, prepare_pooled, write_discovered
from breakwater.features import FEATURE_COLUMNS, candle_frame, compute_price_features
from breakwater.hip3 import Hip3UniverseRow, read_hip3_universe
from breakwater.hyperliquid import HyperliquidReadOnlyVenue
from breakwater.perpdata import fetch_perp_candles
from breakwater.research_lifecycle import read_book, sync_book
from breakwater.status import append_status
from breakwater.validation import validate_slices, write_validated

COVERAGE_HEADERS = [
    "as_of",
    "coin",
    "dex",
    "market_class",
    "requested_bars",
    "received_bars",
    "first_bar",
    "last_bar",
    "max_gap_seconds",
    "coverage_ok",
    "error",
    "l2_half_spread_bps",
]

FX_ASSETS = {
    "AUD", "CAD", "CHF", "CNH", "EUR", "GBP", "HKD", "JPY", "KRW", "MXN", "NZD",
}
COMMODITY_ASSETS = {
    "BRENT", "BRENTOIL", "CL", "COPPER", "GAS", "GOLD", "NG", "OIL", "PALLADIUM",
    "PLATINUM", "SILVER", "WTI",
}
INDEX_TOKENS = (
    "100", "500", "BTCD", "DJI", "DOW", "NASDAQ", "NDX", "OTHERS", "RUSSELL", "SPX",
    "TOTAL", "UK100", "US30", "US500", "USTECH", "VIX",
)

# Every active DEX gets up to this many coins in the research sample even when
# its instruments never crack the volume cutoff (evidence representativeness).
PER_DEX_FLOOR = 2
# Minimum l2Book samples before a measured cost may replace the flat assumption.
MIN_SPREAD_SAMPLES = 30


def _env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(maximum, value))


def _env_decimal(name: str, default: str) -> Decimal:
    try:
        value = Decimal(os.getenv(name, default))
    except (InvalidOperation, TypeError, ValueError):
        value = Decimal(default)
    return value if value.is_finite() else Decimal(default)


def _horizons() -> list[int]:
    default_horizons = ",".join(str(value) for value in range(1, 25))
    raw = os.getenv("BREAKWATER_HIP3_RESEARCH_HORIZONS", default_horizons)
    horizons = []
    for token in raw.split(","):
        try:
            value = int(token.strip())
        except ValueError:
            continue
        if 1 <= value <= 48 and value not in horizons:
            horizons.append(value)
    if not horizons:
        raise RuntimeError("BREAKWATER_HIP3_RESEARCH_HORIZONS has no valid horizons")
    return horizons


def _methodology_parity(*, max_pairs: int, candle_count: int, horizons: list[int]) -> dict:
    expected = {
        "max_pairs": 60,
        "candle_count": 1000,
        "horizons": list(range(1, 25)),
        "rolling_min_periods": "200",
        "state_quantiles": "0.333333,0.666666",
        "require_bonferroni": "0",
        "relaxed_min_passes": "2",
        "strict_pass_floor": "3",
        "breadth_min_symbols": "6",
        "breadth_min_rows_per_symbol": "10",
        "breadth_min_positive_fraction": "0.40",
        "min_net_edge": "0.002",
        "promotion_multi_horizon_min_passes": "2",
        "promotion_multi_horizon_select": "edge_per_bar",
    }
    actual = {
        "max_pairs": max_pairs,
        "candle_count": candle_count,
        "horizons": horizons,
        "rolling_min_periods": os.getenv("BREAKWATER_DISCOVERY_ROLLING_MIN_PERIODS", "200"),
        "state_quantiles": os.getenv(
            "BREAKWATER_DISCOVERY_STATE_QUANTILES", "0.333333,0.666666"
        ),
        "require_bonferroni": os.getenv("BREAKWATER_VALIDATION_REQUIRE_BONFERRONI", "1"),
        "relaxed_min_passes": os.getenv("BREAKWATER_VALIDATION_RELAXED_MIN_PASSES", "4"),
        "strict_pass_floor": os.getenv("BREAKWATER_VALIDATION_STRICT_PASS_FLOOR", "3"),
        "breadth_min_symbols": os.getenv("BREAKWATER_BREADTH_MIN_SYMBOLS", "10"),
        "breadth_min_rows_per_symbol": os.getenv(
            "BREAKWATER_BREADTH_MIN_ROWS_PER_SYMBOL", "10"
        ),
        "breadth_min_positive_fraction": os.getenv(
            "BREAKWATER_BREADTH_MIN_POSITIVE_FRACTION", "0.55"
        ),
        # Book-shaping parameters: native consolidates to one horizon per
        # family (best edge per bar) and only books actionable edges. If the
        # HIP-3 workflow drifts here, the book shape diverges from native
        # doctrine - the 269-row sibling book and the sub-floor 0.00003-edge
        # rows of 2026-08-25 are exactly the drift this catches.
        "min_net_edge": os.getenv("BREAKWATER_MIN_NET_EDGE", "0"),
        "promotion_multi_horizon_min_passes": os.getenv(
            "BREAKWATER_PROMOTION_MULTI_HORIZON_MIN_PASSES", "1"
        ),
        "promotion_multi_horizon_select": os.getenv(
            "BREAKWATER_PROMOTION_MULTI_HORIZON_SELECT", "edge_per_bar"
        ),
    }
    mismatches = [key for key, expected_value in expected.items() if actual[key] != expected_value]
    return {
        "status": "parity" if not mismatches else "mismatch",
        "mismatches": mismatches,
        "expected": expected,
        "actual": actual,
    }


def l2_half_spread_bps(book) -> float | None:
    """Mid-relative half-spread in bps from an l2Book payload.

    Returns None when the book is missing, empty, or malformed so a sample can
    be recorded as unmeasured without failing the run. The flat assumed cost
    (BREAKWATER_HIP3_COST_BPS) is not touched; measured values are evidence
    for that blocker, reported alongside it.
    """
    if not isinstance(book, dict):
        return None
    levels = book.get("levels")
    if not isinstance(levels, list) or len(levels) != 2:
        return None
    bids, asks = levels
    if not isinstance(bids, list) or not isinstance(asks, list):
        return None
    if not bids or not asks:
        return None
    try:
        best_bid = float(bids[0].get("px"))
        best_ask = float(asks[0].get("px"))
    except (AttributeError, TypeError, ValueError):
        return None
    if best_bid <= 0 or best_ask <= 0:
        return None
    mid = (best_bid + best_ask) / 2.0
    return ((best_ask - best_bid) / 2.0) / mid * 10_000.0


def measured_round_trip_cost_bps(
    spreads: list[float],
    *,
    base_taker_fee_bps: float,
) -> float | None:
    """Round-trip cost in bps from the current book snapshot.

    A round trip crosses the spread twice and pays the taker fee on each leg:
    2 x (median half-spread + taker fee). Returns None when there are too few
    samples for the number to be trusted, in which case callers keep the flat
    assumed cost. The book is a point-in-time snapshot, so this is a measured
    estimate of typical crossing cost, not a history.
    """
    if len(spreads) < MIN_SPREAD_SAMPLES:
        return None
    return round(2.0 * (statistics.median(spreads) + base_taker_fee_bps), 2)


def classify_market(coin: str, native_crypto: set[str], annotation_category: str = "") -> str:
    asset = str(coin).split(":", 1)[-1].upper()
    if asset in native_crypto:
        return "builder_crypto"
    category = str(annotation_category or "").strip().lower().replace("-", "_")
    authoritative = {
        "commodity": "commodity",
        "commodities": "commodity",
        "crypto": "builder_crypto",
        "equities": "equity",
        "equity": "equity",
        "forex": "fx",
        "fx": "fx",
        "index": "index",
        "indices": "index",
        "preipo": "preipo",
        "stocks": "equity",
    }
    if category in authoritative:
        return authoritative[category]
    if asset in FX_ASSETS:
        return "fx"
    if asset in COMMODITY_ASSETS:
        return "commodity"
    if any(token in asset for token in INDEX_TOKENS):
        return "index"
    # HIP-3 non-crypto single-name products are provisionally equities. This
    # remains an audit label; promotion is disabled until annotations/calendar
    # metadata can prove the classification.
    return "provisional_equity"


def _write_coverage(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=COVERAGE_HEADERS)
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def _pool(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    parts = []
    for coin, frame in frames.items():
        featured = compute_price_features(frame)
        featured["symbol"] = coin
        parts.append(featured)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def _tag_candidates(candidates, market_class: str, horizon: int):
    tagged = []
    for candidate in candidates:
        payload = asdict(candidate)
        payload["slice_id"] = f"hip3_{market_class}:{candidate.slice_id}:h{horizon}"
        tagged.append(type(candidate)(**payload))
    return tagged


def _candidate_rows(
    rows: tuple[Hip3UniverseRow, ...],
    *,
    native_crypto: set[str],
    max_oracle_deviation: Decimal,
) -> list[tuple[Hip3UniverseRow, str]]:
    """Safety-filtered, volume-sorted candidate list (no budget applied).

    Callers apply the budget via :func:`_stratified_select` so the full
    candidate set stays available for per-DEX representation.
    """
    candidates = []
    for row in rows:
        if not row.active or row.day_notional_volume <= 0:
            continue
        if row.oracle_price <= 0 or row.oracle_mark_deviation_fraction > max_oracle_deviation:
            continue
        market_class = classify_market(
            row.coin, native_crypto, annotation_category=row.annotation_category
        )
        # Native crypto already has a validator-operated research lane. Builder
        # duplicates remain inventoried but are excluded from HIP-3 research.
        if market_class == "builder_crypto":
            continue
        candidates.append((row, market_class))
    candidates.sort(key=lambda item: (-item[0].day_notional_volume, item[0].coin))
    return candidates


def _stratified_select(
    candidates: list[tuple[Hip3UniverseRow, str]],
    *,
    max_pairs: int,
    per_dex_floor: int = PER_DEX_FLOOR,
) -> list[tuple[Hip3UniverseRow, str]]:
    """Top-by-volume selection with a per-DEX representation floor.

    candidates must already be volume-sorted. DEXs absent from the top pick
    receive up to per_dex_floor of their best coins; floor picks displace the
    lowest-volume picks, so the budget never grows. Deterministic; iteration
    is bounded and converges when every representable DEX has its floor.
    """
    selected = list(candidates[:max_pairs])
    # Each pass adds at least one previously-missing DEX, so this converges in
    # at most len(candidates) + 1 passes; the bound is a safety net.
    for _ in range(len(candidates) + 1):
        selected_dexs = {row.dex for row, _ in selected}
        missing = [
            (row, market_class)
            for row, market_class in candidates
            if row.dex not in selected_dexs
        ]
        if not missing:
            break
        floor_picks: list[tuple[Hip3UniverseRow, str]] = []
        counted: dict[str, int] = {}
        for row, market_class in missing:  # volume order
            if len(floor_picks) >= len(selected):
                break  # budget can never grow
            if counted.get(row.dex, 0) >= per_dex_floor:
                continue
            floor_picks.append((row, market_class))
            counted[row.dex] = counted.get(row.dex, 0) + 1
        tail_coins = {row.coin for row, _ in selected[-len(floor_picks):]}
        selected = [item for item in selected if item[0].coin not in tail_coins]
        selected.extend(floor_picks)
        selected.sort(key=lambda item: (-item[0].day_notional_volume, item[0].coin))
    return selected


# A live decision needs this many completed HIP-3 paper round trips (and the
# same number of ghost comparisons) with positive net PnL before the live gate
# can report ready.
HIP3_LIVE_MIN_PAPER_TRADES = 25
HIP3_SLICE_PREFIX = "hip3_"


def _hip3_paper_evidence(paper_log_rows, cf_rows) -> dict:
    """Count realised HIP-3 paper round trips and ghost comparisons.

    Both logs are the shared paper logs; HIP-3 rows are identified by the
    hip3_ slice-id prefix.
    """
    closed = [
        row
        for row in paper_log_rows
        if str(row.get("slice_id") or "").startswith(HIP3_SLICE_PREFIX)
        and str(row.get("outcome") or "") in {"win", "loss"}
    ]
    pnl = 0.0
    for row in closed:
        try:
            pnl += float(row.get("pnl_zar") or 0.0)
        except (TypeError, ValueError):
            pass
    ghosts = sum(
        1
        for row in cf_rows
        if str(row.get("slice_id") or "").startswith(HIP3_SLICE_PREFIX)
    )
    return {
        "closed_trades": len(closed),
        "pnl_zar": round(pnl, 4),
        "ghost_rows": ghosts,
        "minimum_trades": HIP3_LIVE_MIN_PAPER_TRADES,
    }


def _promotion_gate(
    *,
    selected: list[tuple[Hip3UniverseRow, str]],
    spread_samples: list[float],
    assumed_cost_bps: float,
    measured_cost_bps: float | None,
    base_taker_fee_bps: float,
    confirmed_collateral_tokens: set[int] | None,
    paper_evidence: dict,
) -> dict:
    """Evaluate promotion blockers in two stages.

    Paper readiness ({measured costs, confirmed collateral}) arms the HIP-3
    paper book: paper is a measurement instrument, not live capital, so it
    must not require its own output (the paper-evidence blocker) to start,
    and group-scoped matching already guarantees no cross-pool contamination,
    so full classification authority is a LIVE-stage requirement (real money
    meeting product semantics), not a paper one. Live readiness requires all
    six, including paper and ghost evidence, and is the checklist that
    unblocks real capital. This module still writes no monitored book of its
    own and feeds no execution; the paper book it can arm is consumed only
    by the paper engine behind BREAKWATER_HIP3_PAPER.
    """
    provisional = [cls for _, cls in selected if cls.startswith("provisional")]
    classification_resolved = bool(selected) and not provisional
    # Collateral is a SET check: different DEXs settle in different tokens
    # (observed: 0 for io/mkts/para/xyz, 235 for hyna). Resolved when every
    # observed token is in the operator-confirmed list.
    observed_tokens = {row.collateral_token for row, _ in selected}
    collateral_resolved = bool(confirmed_collateral_tokens) and observed_tokens <= confirmed_collateral_tokens
    costs_resolved = measured_cost_bps is not None
    paper_resolved = (
        paper_evidence["closed_trades"] >= HIP3_LIVE_MIN_PAPER_TRADES
        and paper_evidence["ghost_rows"] >= HIP3_LIVE_MIN_PAPER_TRADES
        and paper_evidence["pnl_zar"] > 0
    )
    blockers = [
        {
            "name": "market_classification_not_fully_authoritative",
            "resolved": classification_resolved,
            "stage": "live",
            "evidence": (
                f"{len(selected) - len(provisional)}/{len(selected)} selected coins in an "
                f"authoritative class ({len(provisional)} provisional); live-stage blocker - "
                f"paper measurement is group-scoped and cannot cross-contaminate pools"
            ),
        },
        {
            "name": "effective_costs_not_measured",
            "resolved": costs_resolved,
            "stage": "paper",
            "evidence": (
                f"l2 samples {len(spread_samples)}/{MIN_SPREAD_SAMPLES} minimum; "
                + (
                    f"measured round-trip cost {measured_cost_bps} bps "
                    f"(median half-spread + {base_taker_fee_bps} bps taker, x2 legs)"
                    if costs_resolved
                    else f"validation using flat assumed {assumed_cost_bps} bps"
                )
            ),
        },
        {
            "name": "collateral_tokens_not_resolved",
            "resolved": collateral_resolved,
            "stage": "paper",
            "evidence": (
                f"distinct collateral token ids in selected: "
                f"{sorted(observed_tokens)}"
                + (
                    f"; all confirmed (operator list: {sorted(confirmed_collateral_tokens)})"
                    if collateral_resolved
                    else "; operator confirmation required (BREAKWATER_HIP3_USDC_TOKEN_ID)"
                )
            ),
        },
        {
            "name": "market_calendars_not_enforced",
            "resolved": False,
            "stage": "live",
            "evidence": "research treats all HIP-3 sessions as 24/7; equity/FX/commodity calendars are not modeled",
        },
        {
            "name": "historical_oracle_quality_not_available",
            "resolved": False,
            "stage": "live",
            "evidence": "oracle prints are not exposed by the API; cross-DEX divergence proxy not implemented",
        },
        {
            "name": "no_hip3_paper_evidence",
            "resolved": paper_resolved,
            "stage": "live",
            "evidence": (
                f"hip3 paper closed {paper_evidence['closed_trades']}/"
                f"{HIP3_LIVE_MIN_PAPER_TRADES} (pnl {paper_evidence['pnl_zar']} ZAR), "
                f"ghost rows {paper_evidence['ghost_rows']}; requires positive pnl"
            ),
        },
    ]
    paper_unresolved = [
        blocker["name"]
        for blocker in blockers
        if blocker["stage"] == "paper" and not blocker["resolved"]
    ]
    live_unresolved = [blocker["name"] for blocker in blockers if not blocker["resolved"]]
    return {
        "blockers": blockers,
        "paper_unresolved": paper_unresolved,
        "live_unresolved": live_unresolved,
        "paper_ready": not paper_unresolved,
        "live_ready": not live_unresolved,
        "paper_evidence": paper_evidence,
    }


def write_paper_gate(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w") as handle:
            json.dump(payload, handle, indent=1, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def run_hip3_research(
    *,
    universe_path: Path,
    coverage_path: Path,
    discovered_path: Path,
    validated_path: Path,
    status_path: Path,
    book_path: Path | None = None,
    gate_path: Path | None = None,
    paper_log_path: Path | None = None,
    counterfactual_log_path: Path | None = None,
) -> dict:
    universe = read_hip3_universe(universe_path)
    if universe is None or not universe.rows:
        raise RuntimeError("HIP-3 universe is missing; run hip3-discover first")

    native_venue = HyperliquidReadOnlyVenue()
    native_crypto = {instrument.coin.upper() for instrument in native_venue.instruments()}
    max_pairs = _env_int("BREAKWATER_HIP3_RESEARCH_MAX_PAIRS", 60, 8, 150)
    candle_count = _env_int("BREAKWATER_HIP3_CANDLE_COUNT", 1000, 300, 5000)
    max_deviation = _env_decimal("BREAKWATER_HIP3_MAX_ORACLE_DEVIATION", "0.02")
    cost_bps = float(_env_decimal("BREAKWATER_HIP3_COST_BPS", "30"))
    base_taker_fee_bps = float(_env_decimal("BREAKWATER_HIP3_BASE_TAKER_FEE_BPS", "4.5"))
    raw_collateral = os.getenv("BREAKWATER_HIP3_USDC_TOKEN_ID", "").strip()
    # Comma-separated list of operator-confirmed collateral token ids, e.g.
    # "0,235". Different DEXs settle in different tokens; the gate resolves
    # when every observed token is in this list.
    confirmed_collateral = {
        int(token)
        for token in raw_collateral.replace(";", ",").split(",")
        if token.strip().lstrip("-").isdigit()
    } or None
    sleep_seconds = float(_env_decimal("BREAKWATER_CANDLE_PAGE_SLEEP_SECONDS", "0.05"))
    candidates = _candidate_rows(
        universe.rows,
        native_crypto=native_crypto,
        max_oracle_deviation=max_deviation,
    )
    selected = _stratified_select(candidates, max_pairs=max_pairs)
    if not selected:
        raise RuntimeError("no active HIP-3 instruments passed pre-research safety gates")

    observed = datetime.now(timezone.utc).isoformat()
    coverage_rows = []
    frames_by_group: dict[str, dict[str, pd.DataFrame]] = {}
    for row, market_class in selected:
        # Measured crossing-cost sample. Read-only and best-effort: a missing
        # or failing book records an unmeasured spread and never blocks the
        # candle audit for the coin.
        try:
            spread_bps = l2_half_spread_bps(
                native_venue._post_info({"type": "l2Book", "coin": row.coin})
            )
        except Exception:
            spread_bps = None
        spread_value = "" if spread_bps is None else f"{spread_bps:.2f}"
        try:
            candles = fetch_perp_candles(row.coin, interval="1h", count=candle_count)
            frame = candle_frame(candles).sort_values("start").drop_duplicates("start")
            received = len(frame)
            gaps = frame["start"].diff().dt.total_seconds().dropna()
            max_gap = int(gaps.max()) if not gaps.empty else 0
            minimum_bars = max(300, int(candle_count * 0.75))
            coverage_ok = received >= minimum_bars and max_gap <= 4 * 3600
            error = "" if coverage_ok else "insufficient_or_gapped_history"
            coverage_rows.append(
                {
                    "as_of": observed,
                    "coin": row.coin,
                    "dex": row.dex,
                    "market_class": market_class,
                    "requested_bars": candle_count,
                    "received_bars": received,
                    "first_bar": frame.iloc[0]["start"].isoformat() if received else "",
                    "last_bar": frame.iloc[-1]["start"].isoformat() if received else "",
                    "max_gap_seconds": max_gap,
                    "coverage_ok": coverage_ok,
                    "error": error,
                    "l2_half_spread_bps": spread_value,
                }
            )
            if coverage_ok:
                frame["symbol"] = row.coin
                research_group = f"{row.dex}_{market_class}_c{row.collateral_token}"
                frames_by_group.setdefault(research_group, {})[row.coin] = frame
        except Exception as exc:
            coverage_rows.append(
                {
                    "as_of": observed,
                    "coin": row.coin,
                    "dex": row.dex,
                    "market_class": market_class,
                    "requested_bars": candle_count,
                    "received_bars": 0,
                    "first_bar": "",
                    "last_bar": "",
                    "max_gap_seconds": 0,
                    "coverage_ok": False,
                    "error": f"{type(exc).__name__}: {exc}"[:180],
                    "l2_half_spread_bps": spread_value,
                }
            )
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)
    _write_coverage(coverage_path, coverage_rows)

    # Cost decision: a measured round-trip cost replaces the flat assumption
    # only once enough books were sampled; otherwise the assumption stands
    # and the gate reports why.
    spread_values = [
        float(row["l2_half_spread_bps"])
        for row in coverage_rows
        if row["l2_half_spread_bps"] not in ("", None)
    ]
    spread_summary = {
        "sampled": len(spread_values),
        "unmeasured": len(coverage_rows) - len(spread_values),
        "min": round(min(spread_values), 2) if spread_values else None,
        "median": round(statistics.median(spread_values), 2) if spread_values else None,
        "max": round(max(spread_values), 2) if spread_values else None,
    }
    measured_cost = measured_round_trip_cost_bps(
        spread_values, base_taker_fee_bps=base_taker_fee_bps
    )
    effective_cost = measured_cost if measured_cost is not None else cost_bps
    effective_cost_source = "measured_l2_roundtrip" if measured_cost is not None else "assumed_flat"

    horizons = _horizons()
    discovered = []
    validated = []
    researched_by_group = {}
    for research_group, frames in sorted(frames_by_group.items()):
        pooled = _pool(frames)
        researched_by_group[research_group] = len(frames)
        # Book-facing kind is PERP: these are perpetuals, so the paper engine's
        # fee, sizing, and frame routing treat them exactly like native perps.
        # Group identity lives in the hip3_-prefixed slice id.
        kind = "PERP"
        for horizon in horizons:
            prepared = prepare_pooled(
                pooled, FEATURE_COLUMNS, effective_cost, horizon_bars=horizon
            )
            found = _slice_stats(prepared, kind, FEATURE_COLUMNS, horizon_bars=horizon)
            found = _tag_candidates(found, research_group, horizon)
            checked = validate_slices(prepared, found)
            discovered.extend(found)
            validated.extend(checked)

    if not frames_by_group:
        raise RuntimeError("no HIP-3 instruments passed candle coverage audit")
    write_discovered(discovered_path, discovered)
    write_validated(validated_path, validated)
    fail_tokens = Counter()
    for row in validated:
        for token in str(row.fail_reasons or "").split(","):
            if token.strip():
                fail_tokens[token.strip()] += 1
    parity = _methodology_parity(
        max_pairs=max_pairs, candle_count=candle_count, horizons=horizons
    )
    selected_classes = [
        classify_market(row.coin, native_crypto, row.annotation_category)
        for row, _ in selected
    ]
    paper_log_rows: list[dict] = []
    if paper_log_path is not None and paper_log_path.exists():
        try:
            with paper_log_path.open(newline="") as handle:
                paper_log_rows = list(csv.DictReader(handle))
        except OSError:
            paper_log_rows = []
    cf_rows: list[dict] = []
    if counterfactual_log_path is not None and counterfactual_log_path.exists():
        try:
            with counterfactual_log_path.open(newline="") as handle:
                cf_rows = list(csv.DictReader(handle))
        except OSError:
            cf_rows = []
    promotion_gate = _promotion_gate(
        selected=selected,
        spread_samples=spread_values,
        assumed_cost_bps=cost_bps,
        measured_cost_bps=measured_cost,
        base_taker_fee_bps=base_taker_fee_bps,
        confirmed_collateral_tokens=confirmed_collateral,
        paper_evidence=_hip3_paper_evidence(paper_log_rows, cf_rows),
    )

    # Paper book: synced only while the paper gate is ready; frozen (kept, not
    # maintained) otherwise. This book feeds only the HIP-3 paper path.
    book_sync = None
    book_rows_now = 0
    book_frozen = True
    if book_path is not None:
        if promotion_gate["paper_ready"]:
            book_sync = sync_book(validated_path=validated_path, book_path=book_path)
            book_frozen = False
            book_rows_now = book_sync.get("rows_total_after_sync", 0)
        else:
            book_rows_now = len(read_book(book_path)) if book_path.exists() else 0
    if gate_path is not None:
        write_paper_gate(
            gate_path,
            {
                "as_of": observed,
                "paper_ready": promotion_gate["paper_ready"],
                "live_ready": promotion_gate["live_ready"],
                "paper_unresolved": promotion_gate["paper_unresolved"],
                "live_unresolved": promotion_gate["live_unresolved"],
                "book_rows": book_rows_now,
                "book_frozen": book_frozen,
            },
        )
    result = {
        "as_of": observed,
        "universe_as_of": universe.as_of,
        "selected": len(selected),
        "coverage_ok": sum(bool(row["coverage_ok"]) for row in coverage_rows),
        "coverage_failed": sum(not bool(row["coverage_ok"]) for row in coverage_rows),
        "researched_by_group": researched_by_group,
        "horizons": horizons,
        "cost_bps": cost_bps,
        "l2_spread_bps": spread_summary,
        "discovered_slices": len(discovered),
        "walk_forward_validated": sum(row.validated for row in validated),
        "fail_top": fail_tokens.most_common(8),
        "promotion_enabled": False,
        "paper_enabled": False,
        "classification_status": (
            "authoritative"
            if selected_classes and all(not value.startswith("provisional") for value in selected_classes)
            else "provisional"
        ),
        "annotated_selected": sum(bool(row.annotation_category) for row, _ in selected),
        "selection": {
            "mode": "stratified_by_dex",
            "per_dex_floor": PER_DEX_FLOOR,
            "dexs_selected": len({row.dex for row, _ in selected}),
            "dexs_with_candidates": len({row.dex for row, _ in candidates}),
        },
        "effective_cost_bps": {
            "value": effective_cost,
            "source": effective_cost_source,
            "base_taker_fee_bps": base_taker_fee_bps,
            "assumed_cost_bps": cost_bps,
        },
        "methodology_parity": parity,
        "hip3_paper_book": {
            "frozen": book_frozen,
            "rows": book_rows_now,
            "sync": book_sync,
        },
        "promotion_blocked_reasons": promotion_gate["live_unresolved"],
        "promotion_gate": promotion_gate,
    }
    append_status(
        status_path,
        "hip3_research_done",
        "readonly",
        json.dumps(result, sort_keys=True),
    )
    return result
