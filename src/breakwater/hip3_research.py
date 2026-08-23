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
    raw = os.getenv("BREAKWATER_HIP3_RESEARCH_HORIZONS", "6,12,24")
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


def classify_market(coin: str, native_crypto: set[str]) -> str:
    asset = str(coin).split(":", 1)[-1].upper()
    if asset in native_crypto:
        return "builder_crypto"
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
    max_pairs: int,
    max_oracle_deviation: Decimal,
) -> list[tuple[Hip3UniverseRow, str]]:
    candidates = []
    for row in rows:
        if not row.active or row.day_notional_volume <= 0:
            continue
        if row.oracle_price <= 0 or row.oracle_mark_deviation_fraction > max_oracle_deviation:
            continue
        market_class = classify_market(row.coin, native_crypto)
        # Native crypto already has a validator-operated research lane. Builder
        # duplicates remain inventoried but are excluded from HIP-3 research.
        if market_class == "builder_crypto":
            continue
        candidates.append((row, market_class))
    candidates.sort(key=lambda item: (-item[0].day_notional_volume, item[0].coin))
    return candidates[:max_pairs]


def run_hip3_research(
    *,
    universe_path: Path,
    coverage_path: Path,
    discovered_path: Path,
    validated_path: Path,
    status_path: Path,
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
    sleep_seconds = float(_env_decimal("BREAKWATER_CANDLE_PAGE_SLEEP_SECONDS", "0.05"))
    selected = _candidate_rows(
        universe.rows,
        native_crypto=native_crypto,
        max_pairs=max_pairs,
        max_oracle_deviation=max_deviation,
    )
    if not selected:
        raise RuntimeError("no active HIP-3 instruments passed pre-research safety gates")

    observed = datetime.now(timezone.utc).isoformat()
    coverage_rows = []
    frames_by_group: dict[str, dict[str, pd.DataFrame]] = {}
    for row, market_class in selected:
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
                }
            )
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)
    _write_coverage(coverage_path, coverage_rows)

    horizons = _horizons()
    discovered = []
    validated = []
    researched_by_group = {}
    for research_group, frames in sorted(frames_by_group.items()):
        pooled = _pool(frames)
        researched_by_group[research_group] = len(frames)
        kind = f"HIP3_{research_group.upper()}"
        for horizon in horizons:
            prepared = prepare_pooled(
                pooled, FEATURE_COLUMNS, cost_bps, horizon_bars=horizon
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
    result = {
        "as_of": observed,
        "universe_as_of": universe.as_of,
        "selected": len(selected),
        "coverage_ok": sum(bool(row["coverage_ok"]) for row in coverage_rows),
        "coverage_failed": sum(not bool(row["coverage_ok"]) for row in coverage_rows),
        "researched_by_group": researched_by_group,
        "horizons": horizons,
        "cost_bps": cost_bps,
        "discovered_slices": len(discovered),
        "walk_forward_validated": sum(row.validated for row in validated),
        "fail_top": fail_tokens.most_common(8),
        "promotion_enabled": False,
        "paper_enabled": False,
        "classification_status": "provisional",
    }
    append_status(
        status_path,
        "hip3_research_done",
        "readonly",
        json.dumps(result, sort_keys=True),
    )
    return result
