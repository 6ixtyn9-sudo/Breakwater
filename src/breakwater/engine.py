"""Restart-safe guardian, universe scanner and guarded executor.

Upgrades:
- _frames() now honors BREAKWATER_SPOT_CANDLE_COUNT / BREAKWATER_PERP_CANDLE_COUNT
  (instead of hardcoding 300).
- research_pass() now supports multi-horizon research via BREAKWATER_RESEARCH_HORIZONS.
  When multiple horizons are used, slice_id is tagged with :h{horizon} to avoid
  collisions in the book (sync_book uses slice_id as the primary key).
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pandas as pd

from breakwater.account import (
    EquityValuator,
    unprotected_positions,
    validate_api_key_permissions,
)
from breakwater.config import Settings
from breakwater.discovery import prepare_pooled
from breakwater.execution import TradeExecutor
from breakwater.features import FEATURE_COLUMNS, candle_frame, compute_price_features
from breakwater.hip3 import read_hip3_universe
from breakwater.hip3_research import classify_market
from breakwater.hyperliquid import HyperliquidReadOnlyVenue
from breakwater.lane_gate import (
    compute_green_gate,
    filter_green_book_rows,
)
from breakwater.ledger import Ledger
from breakwater.market import (
    MarketCatalog,
    authoritative_server_time,
    fetch_recent_candles,
)
from breakwater.models import Candle, Lifecycle, PairType
from breakwater.monitor import SliceSignal, monitor_book, regime_of, signal_pair_type
from breakwater.paper_trade import append_log, read_positions, run_paper_cycle
from breakwater.perpdata import fetch_perp_candles, fetch_perp_candles_for_pair, pair_to_coin
from breakwater.promotion import PromotionRegistry
from breakwater.regime_tracker import (
    compute_regime_snapshot,
    regime_shift_dict,
    update_regime_state,
)
from breakwater.research_lifecycle import read_book
from breakwater.risk import RiskManager
from breakwater.risk_state import RiskStateStore
from breakwater.short_inventory import (
    compute_short_inventory,
    write_short_inventory,
)
from breakwater.status import append_status
from breakwater.strategy import detect_big_wave
from breakwater.universe import (
    UniverseSnapshot,
    has_direct_hyperliquid_perps,
    ingest_universe,
    is_legacy_universe,
    read_universe,
    write_universe,
)
from breakwater.validation import (
    AssetEdge,
    build_asset_edge_lookup,
    read_asset_edges,
    write_asset_edges,
)
from breakwater.valr import ValrClient


class GuardianHalt(RuntimeError):
    pass


def _coerce_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _fee_bps_env(name: str, default: str) -> float:
    try:
        value = float(os.getenv(name, default))
    except (TypeError, ValueError):
        return float(default)
    return value if math.isfinite(value) and value >= 0 else float(default)


def _research_max_pairs(default: int = 60) -> int:
    raw = _coerce_int(os.getenv("BREAKWATER_RESEARCH_MAX_PAIRS", str(default)), default)
    return max(8, min(200, raw))


def _compact_paper_status(paper_result: dict) -> dict:
    compact = {
        key: value
        for key, value in paper_result.items()
        if key not in {"counterfactual", "performance"}
    }
    performance = paper_result.get("performance") or {}
    compact["performance"] = {
        key: performance.get(key)
        for key in ("closed", "wins", "pnl_zar", "by_side", "by_exit")
    }
    counterfactual = paper_result.get("counterfactual") or {}
    compact["counterfactual"] = {
        key: counterfactual.get(key)
        for key in (
            "active_trackers",
            "completed",
            "completed_this_cycle",
            "state_error",
            "prospective_only",
            "limitations",
            "control",
            "by_policy",
        )
    }
    return compact


def _parse_horizons_env() -> list[int]:
    """Parse research horizons.

    Preferred:
      BREAKWATER_RESEARCH_HORIZONS="6,12,24"

    Fallback (existing behavior):
      BREAKWATER_RESEARCH_HORIZON_BARS="6"
    """
    raw = str(os.getenv("BREAKWATER_RESEARCH_HORIZONS", "")).strip()
    if raw:
        horizons: list[int] = []
        for chunk in raw.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            try:
                h = int(chunk)
            except ValueError:
                continue
            if h < 1:
                continue
            if h not in horizons:
                horizons.append(h)
        if horizons:
            # Safety clamp: avoid accidental huge runs from bad config.
            # Default stays 8; raise via BREAKWATER_RESEARCH_HORIZONS_MAX.
            max_h = _coerce_int(os.getenv("BREAKWATER_RESEARCH_HORIZONS_MAX", "8"), 8)
            max_h = max(1, min(24, max_h))
            return horizons[:max_h]

    horizon = _coerce_int(os.getenv("BREAKWATER_RESEARCH_HORIZON_BARS", "1"), 1)
    if horizon < 1:
        horizon = 1
    return [horizon]


def _hip3_decimal_env(name: str, default: str) -> Decimal:
    from decimal import InvalidOperation

    try:
        value = Decimal(os.getenv(name, default))
    except (InvalidOperation, TypeError, ValueError):
        value = Decimal(default)
    return value if value.is_finite() else Decimal(default)


def _read_json_quiet(path) -> dict:
    try:
        payload = json.loads(Path(path).read_text())
        return payload if isinstance(payload, dict) else {}
    except (OSError, ValueError, TypeError):
        return {}


def _read_discovered_objects(path) -> list:
    """Minimal duck-typed SHORT/LONG rows for the research audit helper."""
    import csv

    out = []
    if not Path(path).exists():
        return out
    try:
        with Path(path).open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                class _Row:
                    pass
                obj = _Row()
                obj.slice_id = str(row.get("slice_id") or "")
                obj.side = str(row.get("side") or "")
                obj.mean_ret_costadj = _coerce_float(row.get("mean_ret_costadj"), 0.0)
                obj.validated = False
                obj.fail_reasons = ""
                out.append(obj)
    except OSError:
        return []
    return out


def _coerce_float(value, default: float) -> float:
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return default


def _asset_edge_status_counts(
    lookup: dict[tuple[str, str], str],
) -> dict[str, int]:
    """Count per-asset verdicts in a lookup so operators can see the gate's effect.

    The lookup maps (slice_id, asset) -> asset_status. Counting the statuses
    makes it obvious whether the per-asset gate is actually discriminating
    (blocked > 0) or is largely decorative (most assets untested/allowed).
    """
    counts = {"green": 0, "blocked": 0, "untested": 0}
    for status in lookup.values():
        counts[status] = counts.get(status, 0) + 1
    return counts


def _short_research_audit(validated, discovered) -> dict:
    """Compact research-side SHORT audit.

    Returns how many shorts the discovery produced, how many validated, the
    best validated/eligible short edge, and the dominant reasons the rest
    failed. This makes "the system has no short inventory" a researched fact
    rather than an inference.
    """
    from collections import Counter

    shorts_validated = [row for row in validated if str(row.side).upper() == "SHORT"]
    shorts_discovered = [row for row in discovered if str(getattr(row, "side", "") or "").upper() == "SHORT"]
    shorts_ok = [row for row in shorts_validated if row.validated]

    floor = _coerce_float(os.getenv("BREAKWATER_MIN_NET_EDGE", "0.004"), 0.004)
    eligible = [row for row in shorts_validated if row.mean_ret_costadj >= floor]
    best = max(shorts_validated, key=lambda row: row.mean_ret_costadj, default=None)
    best_failing = max(
        [row for row in shorts_validated if not row.validated],
        key=lambda row: row.mean_ret_costadj,
        default=None,
    )

    reasons = Counter()
    for row in shorts_validated:
        for token in str(row.fail_reasons or "").split(","):
            token = token.strip()
            if token:
                reasons[token] += 1

    return {
        "shorts_discovered": len(shorts_discovered),
        "shorts_validated": len(shorts_validated),
        "shorts_passing": len(shorts_ok),
        "shorts_eligible_floor_bps": int(floor * 10_000),
        "shorts_eligible": len(eligible),
        "best_short_edge_bps": round(best.mean_ret_costadj * 10_000, 1) if best else 0.0,
        "best_short_fail_reasons": str(best.fail_reasons or "") if best else "",
        "best_short_n": int(getattr(best, "n", 0)) if best else 0,
        "best_short_breadth": int(getattr(best, "breadth_symbols_used", 0)) if best else 0,
        "best_short_regime_confounded": bool(getattr(best, "regime_confounded", False)) if best else False,
        "best_failing_short_edge_bps": round(best_failing.mean_ret_costadj * 10_000, 1) if best_failing else 0.0,
        "best_failing_short_fail_reasons": str(best_failing.fail_reasons or "") if best_failing else "",
        "short_fail_reasons": reasons.most_common(6),
    }


def _tag_slice_id(slice_id: str, horizon_bars: int, *, multi: bool) -> str:
    """Ensure slice_id is unique per horizon when multi-horizon research is enabled."""
    if not multi:
        return slice_id
    suffix = f":h{int(horizon_bars)}"
    text = str(slice_id)
    return text if text.endswith(suffix) else f"{text}{suffix}"


def _retag_candidates_for_horizon(candidates, *, horizon_bars: int, multi: bool):
    """Return new candidate objects with horizon-tagged slice_id if multi-horizon enabled.

    Works for both discovery.SliceStat and validation.ValidatedSlice because both are
    dataclasses and both include slice_id.
    """
    if not multi:
        return candidates
    retagged = []
    for row in candidates:
        payload = asdict(row)
        payload["slice_id"] = _tag_slice_id(payload["slice_id"], horizon_bars, multi=True)
        retagged.append(type(row)(**payload))
    return retagged


class BreakwaterEngine:
    def __init__(
        self,
        settings: Settings,
        *,
        client: ValrClient | None = None,
        perp_venue=None,
    ):
        self.settings = settings
        self.client = client or ValrClient(
            api_key=settings.api_key,
            api_secret=settings.api_secret,
            allow_writes=settings.writes_allowed,
        )
        self.ledger = Ledger(
            settings.ledger_path,
            high_water_seed=(
                settings.mandate.initial_equity_zar if settings.mandate else Decimal(0)
            ),
        )
        self.catalog = MarketCatalog(self.client)
        # Injected VALR clients are primarily offline tests/tools; keep their
        # explicit metadata path unless a PERP venue is also injected.
        self.perp_venue = (
            perp_venue
            if perp_venue is not None
            else (HyperliquidReadOnlyVenue() if client is None else None)
        )
        self.risk = RiskManager(settings.mandate) if settings.mandate else None
        self.risk_state = RiskStateStore(
            settings.risk_state_path,
            high_water_seed=(
                settings.mandate.initial_equity_zar if settings.mandate else Decimal(0)
            ),
        )
        self.registry = PromotionRegistry(settings.registry_path)

    def _server_state(self) -> tuple[datetime, dict]:
        status = self.client.exchange_status()
        if str(status.get("status", "")).lower() != "online":
            raise GuardianHalt("VALR exchange does not report online")
        server_time = authoritative_server_time(self.client.server_time())
        drift = abs((datetime.now(timezone.utc) - server_time).total_seconds())
        if drift > 30:
            raise GuardianHalt("runner clock differs from VALR by more than 30 seconds")
        return server_time, status

    def _universe(self) -> UniverseSnapshot:
        snapshot = read_universe(self.settings.universe_path)
        if (
            snapshot is not None
            and not is_legacy_universe(snapshot)
            and has_direct_hyperliquid_perps(snapshot)
        ):
            try:
                as_of = datetime.fromisoformat(snapshot.as_of)
                if datetime.now(timezone.utc) - as_of < timedelta(days=7):
                    return snapshot
            except (TypeError, ValueError):
                pass
        snapshot = ingest_universe(self.client, perp_venue=self.perp_venue)
        write_universe(self.settings.universe_path, snapshot)
        return snapshot

    def _frames(self, targets: list[tuple[str, str]], server_time: datetime):
        """Fetch frames for targets.

        Env:
          - BREAKWATER_SPOT_CANDLE_COUNT (default 300, max 5000)
          - BREAKWATER_PERP_CANDLE_COUNT (default 300, max 5000)

        Notes:
          - Spot supports counts > 300 because market.fetch_recent_candles() pages now.
          - Perps supports counts up to 5000 via Hyperliquid public API.
        """
        frames = {}
        errors = {}

        spot_count = _coerce_int(os.getenv("BREAKWATER_SPOT_CANDLE_COUNT", "300"), 300)
        perp_count = _coerce_int(os.getenv("BREAKWATER_PERP_CANDLE_COUNT", "300"), 300)

        spot_count = max(60, min(5000, spot_count))
        perp_count = max(60, min(5000, perp_count))

        for pair, kind in targets:
            if kind == "PERP":
                coin = pair_to_coin(pair) or (pair if ":" in pair else None)
                if coin is None:
                    # Designed skip (unmapped native pair). Not a fetch error.
                    continue
            else:
                coin = None
            try:
                if kind == "PERP":
                    # Native pairs resolve through the USDC mapping; HIP-3
                    # prefixed coins (dex:ASSET) are their own coin on the
                    # same public candle endpoint.
                    candles = (
                        fetch_perp_candles(coin, count=perp_count)
                        if ":" in pair
                        else fetch_perp_candles_for_pair(pair, count=perp_count)
                    )
                else:
                    candles = fetch_recent_candles(
                        self.client, pair, server_time, count=spot_count
                    )
                frame = candle_frame(candles)
                frame["symbol"] = pair.upper()
                frames[pair.upper()] = frame
            except Exception as exc:
                errors[pair.upper()] = f"{type(exc).__name__}: {exc}"[:140]

        return frames, errors

    def guardian(self) -> dict:
        server_time, exchange_status = self._server_state()
        specs = self.catalog.refresh()
        active_spot = self.catalog.active(PairType.SPOT)
        result = {
            "server_time": server_time.isoformat(),
            "exchange_status": exchange_status.get("status"),
            "active_spot_pairs": len(active_spot),
            "authenticated": self.settings.has_credentials,
            "mode": self.settings.mode,
        }
        if not self.settings.has_credentials:
            append_status(
                self.settings.status_path,
                "public_ok",
                self.settings.mode,
                json.dumps(result, sort_keys=True),
            )
            return result
        if self.risk is None:
            raise GuardianHalt("capital mandate is not configured for authenticated runs")
        key_info = self.client.current_api_key()
        permissions = validate_api_key_permissions(
            key_info, live=self.settings.mode == "live"
        )
        balances = self.client.balances()
        positions = self.client.open_positions()
        open_orders = self.client.open_orders()
        conditionals = self.client.conditional_orders() if positions else []
        missing_protection = unprotected_positions(positions, open_orders, conditionals)
        if missing_protection:
            pairs = ",".join(position.pair for position in missing_protection)
            append_status(
                self.settings.status_path,
                "unprotected_position",
                self.settings.mode,
                pairs,
            )
            raise GuardianHalt(f"open positions lack confirmed stop protection: {pairs}")
        perp_positions: list[dict] = []
        perp_error = None
        try:
            perp_positions = self.client.perps_positions()
        except Exception as exc:
            perp_error = f"{type(exc).__name__}: {exc}"
            if self.settings.mode == "live":
                raise GuardianHalt(f"perp position state is unverifiable: {exc}") from exc
        perps_api = "available" if perp_error is None else "unavailable"
        valuator = EquityValuator(self.client, specs)
        equity_zar = valuator.equity_zar(balances, positions)
        if perp_positions:
            usdc_zar = valuator.rate_to_zar("USDC")
            for row in perp_positions:
                margin = Decimal(str(row.get("margin") or 0))
                pnl = Decimal(str(row.get("unrealised_pnl") or 0))
                equity_zar += (margin + pnl) * usdc_zar
        high_water = self.risk_state.observe_equity(equity_zar)
        exposure_symbols = {position.pair for position in positions}
        exposure_symbols.update(str(row.get("pair") or "") for row in perp_positions)
        exposure_symbols.update(
            str(row.get("currencyPair") or row.get("pair") or "").upper()
            for row in open_orders
            if row.get("currencyPair") or row.get("pair")
        )
        risk_state = self.risk.check_account(
            equity_zar=equity_zar,
            high_water_zar=high_water,
            daily_pnl_zar=self.risk_state.daily_pnl(server_time),
            seven_day_pnl_zar=self.risk_state.seven_day_pnl(server_time),
            open_positions=len(exposure_symbols),
            aggregate_open_risk_zar=Decimal(0),
        )
        result.update(
            {
                "equity_zar": str(equity_zar.quantize(Decimal("0.01"))),
                "high_water_zar": str(high_water.quantize(Decimal("0.01"))),
                "positions": len(positions),
                "perp_positions": len(perp_positions),
                "perps_api": perps_api,
                "perp_state_error": perp_error,
                "open_orders": len(open_orders),
                "exposure_slots": len(exposure_symbols),
                "risk_allowed": risk_state.allowed,
                "risk_reasons": list(risk_state.reasons),
                "key_permissions": sorted(permissions),
                "key_ip_restricted": bool(key_info.get("allowedIpAddressCidr")),
                "mandate_configured": self.risk is not None,
            }
        )
        event_id = hashlib.sha256(
            f"guardian|{server_time.isoformat()}|{equity_zar}".encode()
        ).hexdigest()
        self.ledger.append(event_id=event_id, kind="guardian", payload=result)
        append_status(
            self.settings.status_path,
            "guardian_ok" if risk_state.allowed else "risk_halted",
            self.settings.mode,
            json.dumps(result, sort_keys=True),
        )
        return result

    def _hip3_paper_ready(self) -> bool:
        """True when the latest HIP-3 research run armed the paper book.

        The gate file is written by the HIP-3 research workflow; a missing or
        unreadable file fails closed (no HIP-3 paper entries).
        """
        try:
            payload = json.loads(self.settings.hip3_gate_path.read_text())
        except (OSError, ValueError, TypeError):
            return False
        return bool(payload.get("paper_ready"))

    @staticmethod
    def _hip3_group_from_slice(slice_id: str) -> str:
        head = str(slice_id).split(":", 1)[0]
        return head[len("hip3_"):] if head.startswith("hip3_") else head

    def short_inventory_audit(self, *, max_pairs: int = 12) -> dict:
        """On-demand same-cycle short observation.

        Unlike shadow_scan it does not touch paper, monitor, or the book. It
        fetches current frames, computes the native regime shift, and records
        validated SHORT slices whose feature state is active right now. The
        output is read-only and is persisted under research/short_inventory.json.
        """
        server_time, _ = self._server_state()
        self.catalog.refresh()
        universe = self._universe()
        targets = [
            (pair, kind)
            for kind in ("SPOT", "PERP")
            for pair in universe.ranked(kind, max_pairs)
        ]
        frames, frame_errors = self._frames(targets, server_time)
        frames_by_kind: dict[str, dict] = {"SPOT": {}, "PERP": {}}
        for pair, kind in targets:
            frame = frames.get(pair.upper())
            if frame is None:
                continue
            frames_by_kind[kind][pair.upper()] = frame

        regimes = {}
        for kind, bucket in frames_by_kind.items():
            for pair, frame in bucket.items():
                if frame is None or getattr(frame, "empty", True) or len(frame) < 200:
                    continue
                regimes[f"{kind}:{pair.upper()}"] = regime_of(frame)
        bear = sum(1 for value in regimes.values() if value == "bear")
        bull = sum(1 for value in regimes.values() if value == "bull")
        neutral = sum(1 for value in regimes.values() if value == "neutral")
        confirmed_bear = bool(bear / max(1, len(regimes)) >= 0.5 and bear > bull)

        short_inventory = compute_short_inventory(
            validated_path=self.settings.validated_path,
            discovered_path=self.settings.discovered_path,
            frames_by_kind=frames_by_kind,
            server_time=server_time,
            confirmed_bear=confirmed_bear,
        )
        if short_inventory.get("enabled"):
            write_short_inventory(
                self.settings.data_dir / "research" / "short_inventory.json",
                short_inventory,
            )
        return {
            "server_time": server_time.isoformat(),
            "regime_breadth": {"bear": bear, "bull": bull, "neutral": neutral},
            "confirmed_bear": confirmed_bear,
            "short_inventory": short_inventory,
            "frame_errors": frame_errors,
        }

    def hip3_short_audit(self, *, max_pairs: int = 60, apply_book: bool = False) -> dict:
        """On-demand HIP-3 short class-breadth audit (network required).

        Unlike the daily hip3-research run, this revalidates only SHORT rows on
        current HIP-3 class-pooled frames, so a single-name equity/index short
        that failed only ``breadth_ok`` can be upgraded without waiting for the
        03:40 cron. It is audit-only by default; ``apply_book`` (plus an
        existing paper-ready gate) is required to mutate validated/book state.
        """
        from breakwater.hip3 import read_hip3_universe
        from breakwater.hip3_research import (
            _apply_hip3_class_breadth,
            _candidate_rows,
            _stratified_select,
        )
        from breakwater.research_lifecycle import sync_book
        from breakwater.validation import read_validated, write_validated

        server_time, _ = self._server_state()
        self.catalog.refresh()
        universe = read_hip3_universe(self.settings.hip3_universe_path)
        if universe is None or not universe.rows:
            raise GuardianHalt("HIP-3 universe is missing; run hip3-discover first")

        native_venue = self.perp_venue or HyperliquidReadOnlyVenue()
        native_crypto = {instrument.coin.upper() for instrument in native_venue.instruments()}
        max_deviation = _hip3_decimal_env("BREAKWATER_HIP3_MAX_ORACLE_DEVIATION", "0.02")
        # Reuse the same selection/filtering as the HIP-3 research workflow.
        candidates = _candidate_rows(
            universe.rows,
            native_crypto=native_crypto,
            max_oracle_deviation=max_deviation,
        )
        selected = _stratified_select(
            candidates,
            max_pairs=max(8, min(150, max(8, max_pairs))),
        )
        if not selected:
            return {
                "server_time": server_time.isoformat(),
                "selected": 0,
                "error": "no active HIP-3 instruments passed pre-research safety gates",
            }

        targets = [(str(row.coin).upper(), "PERP") for row, _ in selected]
        frames, frame_errors = self._frames(targets, server_time)
        frames_by_class: dict[str, dict[str, pd.DataFrame]] = {}
        group_to_class: dict[str, str] = {}
        for row, market_class in selected:
            frame = frames.get(str(row.coin).upper())
            if frame is None or getattr(frame, "empty", True):
                continue
            group = f"{row.dex}_{market_class}_c{row.collateral_token}"
            frames_by_class.setdefault(market_class, {})[str(row.coin).upper()] = frame
            group_to_class[group] = market_class
        if not frames_by_class:
            return {
                "server_time": server_time.isoformat(),
                "selected": len(selected),
                "classes": 0,
                "error": "no HIP-3 frames could be fetched for the audit",
                "frame_errors": frame_errors,
            }

        validated = read_validated(self.settings.hip3_validated_path)
        discovered = _read_discovered_objects(self.settings.hip3_discovered_path)
        short_horizons = sorted({int(row.horizon_bars) for row in validated if str(row.side).upper() == "SHORT"})
        effective_cost = float(_hip3_decimal_env("BREAKWATER_HIP3_COST_BPS", "30"))
        merged = _apply_hip3_class_breadth(
            validated,
            frames_by_class=frames_by_class,
            group_to_class=group_to_class,
            effective_cost=effective_cost,
            horizons=short_horizons,
        )
        audit = _short_research_audit(merged, discovered)
        upgraded = [
            row
            for row in merged
            if str(row.side).upper() == "SHORT"
            and row.validated
            and str(getattr(row, "breadth_scope", "") or "") == "class"
        ]

        book_summary: dict = {"applied": False, "reason": "apply_book_flag_off"}
        if apply_book:
            gate = _read_json_quiet(self.settings.hip3_gate_path)
            paper_ready = bool((gate or {}).get("paper_ready"))
            if not paper_ready:
                book_summary = {"applied": False, "reason": "paper_gate_not_ready"}
            else:
                write_validated(self.settings.hip3_validated_path, merged)
                book_summary = sync_book(
                    validated_path=self.settings.hip3_validated_path,
                    book_path=self.settings.hip3_book_path,
                )
                book_summary = {"applied": True, **book_summary}

        result = {
            "server_time": server_time.isoformat(),
            "selected": len(selected),
            "classes": len(frames_by_class),
            "symbols_by_class": {
                market_class: len(frames)
                for market_class, frames in sorted(frames_by_class.items())
            },
            "short_horizons": short_horizons,
            "short_audit": audit,
            "class_upgraded_shorts": len(upgraded),
            "class_upgraded_ids": [str(row.slice_id) for row in upgraded[:20]],
            "book": book_summary,
            "frame_errors": frame_errors,
        }
        append_status(
            self.settings.hip3_status_path,
            "hip3_short_audit_done",
            self.settings.mode,
            json.dumps(result, sort_keys=True, default=str),
        )
        return result

    def shadow_scan(self, *, max_pairs: int = 12) -> dict:
        server_time, _ = self._server_state()
        self.catalog.refresh()
        universe = self._universe()
        book_rows = [
            row
            for row in read_book(self.settings.book_path)
            if row.get("status") == "monitored"
        ]
        # Green-account gate: a lane that has not printed positive paper P&L is
        # frozen (no new entries, no open continuation), and an individually
        # negative slice is blocked even inside a green lane.
        green_gate = compute_green_gate(self.settings.paper_log_path)
        book_rows, native_gate_blocked = filter_green_book_rows(book_rows, green_gate)
        lane_gate_blocked: list[dict] = list(native_gate_blocked)
        # Per-asset research map: which assets research proved carry (or do not
        # carry) each slice edge. Lookups are built lazily per lane so the gate
        # is only required when that lane is actually going to monitor/trade:
        # - native file is read only if the native book has monitored rows;
        # - HIP-3 file is read only if HIP-3 paper is active.
        # A missing file for a lane that IS active raises (fail-closed), so the
        # paper cycle never silently trades without the per-asset gate. A lane
        # that is not active does not need its file and must not crash the run.
        asset_edge_lookup: dict[tuple[str, str], str] = {}
        hip3_asset_edge_lookup: dict[tuple[str, str], str] = {}
        targets = [
            (pair, kind)
            for kind in ("SPOT", "PERP")
            for pair in universe.ranked(kind, max_pairs)
        ]
        seen = {(pair.upper(), kind) for pair, kind in targets}

        # HIP-3 paper path: opt-in (BREAKWATER_HIP3_PAPER) AND the research
        # run must have armed it in gate.json. Off by default, in which case
        # the native scan below runs exactly as before.
        hip3_active = False
        hip3_book_rows: list[dict] = []
        hip3_universe = None
        native_crypto: set[str] = set()
        hip3_flag = str(os.getenv("BREAKWATER_HIP3_PAPER", "0")).strip().lower() in {
            "1", "true", "yes", "on",
        }
        if hip3_flag and self._hip3_paper_ready():
            hip3_book_rows = [
                row
                for row in read_book(self.settings.hip3_book_path)
                if row.get("status") == "monitored"
            ]
            hip3_book_rows, hip3_gate_blocked = filter_green_book_rows(
                hip3_book_rows, green_gate
            )
            lane_gate_blocked.extend(hip3_gate_blocked)
            if hip3_book_rows:
                hip3_universe = read_hip3_universe(self.settings.hip3_universe_path)
                native_crypto = {
                    coin
                    for coin in (
                        pair_to_coin(pair) for pair in universe.symbols("PERP")
                    )
                    if coin
                }
                groups_in_book = {
                    self._hip3_group_from_slice(str(row["slice_id"]))
                    for row in hip3_book_rows
                }
                if hip3_universe is not None:
                    for row in hip3_universe.rows:
                        if not row.active:
                            continue
                        market_class = classify_market(
                            row.coin, native_crypto,
                            annotation_category=row.annotation_category,
                        )
                        group = f"{row.dex}_{market_class}_c{row.collateral_token}"
                        if group not in groups_in_book:
                            continue
                        key = (row.coin.upper(), "PERP")
                        if key not in seen:
                            targets.append((row.coin, "PERP"))
                            seen.add(key)
                    hip3_active = True

        for position in read_positions(
            self.settings.data_dir / "research" / "paper_positions.json"
        ):
            pair = str(position.get("pair") or "").upper()
            kind = str(position.get("kind") or "")
            if pair and kind and (pair, kind) not in seen:
                targets.append((pair, kind))
                seen.add((pair, kind))
        frames, frame_errors = self._frames(targets, server_time)
        frames_by_kind: dict[str, dict] = {"SPOT": {}, "PERP": {}}
        hip3_frames: dict[str, dict] = {}
        for pair, kind in targets:
            frame = frames.get(pair.upper())
            if frame is None:
                continue
            if kind == "PERP" and ":" in pair.upper():
                hip3_frames[pair.upper()] = frame
            else:
                frames_by_kind[kind][pair.upper()] = frame

        # Intraday regime-shift awareness. Detective only: it never promotes, it
        # only carries the current regime snapshot into this same paper cycle so
        # the system can (a) stop taking the wrong-direction entries and (b) exit
        # opposite-direction open positions when the macro game has flipped.
        # Hip-3 frames are excluded: calendar assets should not drive a crypto
        # regime call, and their own session gates already govern them.
        regime_shift = None
        native_regime_frames = {}
        if frames_by_kind.get("PERP"):
            native_regime_frames = {"PERP": frames_by_kind["PERP"]}
        elif frames_by_kind.get("SPOT"):
            native_regime_frames = frames_by_kind
        if native_regime_frames:
            regime_snapshot = compute_regime_snapshot(native_regime_frames)
            regime_shift = update_regime_state(
                self.settings.data_dir / "research" / "regime_state.json",
                regime_snapshot,
                now=server_time,
            )
        # Intraday short inventory: read-only observation of validated SHORT
        # slices (and clearly marked provisional fallback if opted in). It is
        # NEVER written to the book/paper; it only tells the system whether
        # there is a valid short it could arm when a bear macro shift confirms.
        short_inventory = None
        short_inventory_path = self.settings.data_dir / "research" / "short_inventory.json"
        if regime_shift is not None:
            short_inventory = compute_short_inventory(
                validated_path=self.settings.validated_path,
                discovered_path=self.settings.discovered_path,
                frames_by_kind=frames_by_kind,
                server_time=server_time,
                confirmed_bear=regime_shift.confirmed_bear,
            )
            if short_inventory.get("enabled"):
                write_short_inventory(short_inventory_path, short_inventory)
        signals: list[SliceSignal] = []
        blocked: list[dict] = []
        if book_rows:
            # Fail-closed for the active native lane.
            asset_edge_lookup = build_asset_edge_lookup(
                read_asset_edges(self.settings.asset_edges_path)
            )
            signals, blocked = monitor_book(
                book_rows,
                frames_by_kind,
                server_time=server_time,
                regime_shift=regime_shift,
                asset_edge_lookup=asset_edge_lookup,
            )
        elif not hip3_active:
            signals = self._big_wave_fallback(targets, frames, server_time)
        if hip3_active:
            # Fail-closed for the active HIP-3 lane.
            hip3_asset_edge_lookup = build_asset_edge_lookup(
                read_asset_edges(self.settings.hip3_asset_edges_path)
            )
            # Group-scoped matching: a HIP-3 slice validated on one
            # dex/class/collateral group must only fire on frames from that
            # group, never on native frames or other HIP-3 groups.
            groups_rows: dict[str, list[dict]] = {}
            for row in hip3_book_rows:
                groups_rows.setdefault(
                    self._hip3_group_from_slice(str(row["slice_id"])), []
                ).append(row)
            groups_frames: dict[str, dict] = {}
            if hip3_universe is not None:
                for coin, frame in hip3_frames.items():
                    row = next(
                        (u for u in hip3_universe.rows if u.coin.upper() == coin),
                        None,
                    )
                    if row is None:
                        continue
                    market_class = classify_market(
                        row.coin, native_crypto,
                        annotation_category=row.annotation_category,
                    )
                    groups_frames.setdefault(
                        f"{row.dex}_{market_class}_c{row.collateral_token}", {}
                    )[coin] = frame
            for group, rows in groups_rows.items():
                group_frames = groups_frames.get(group)
                if not group_frames:
                    continue
                group_signals, group_blocked = monitor_book(
                    rows,
                    {"PERP": group_frames},
                    server_time=server_time,
                    regime_shift=regime_shift,
                    asset_edge_lookup=hip3_asset_edge_lookup,
                )
                signals.extend(group_signals)
                blocked.extend(group_blocked)
        paper_result = None
        if self.settings.mode in {"shadow", "live"} and self.risk is not None:
            valuator = EquityValuator(self.client, self.catalog.refresh())
            try:
                usdc_zar = valuator.rate_to_zar("USDC")
            except Exception:
                usdc_zar = Decimal("16.29")
            book_slice_ids = {
                str(row["slice_id"]) for row in book_rows
            } | {str(row["slice_id"]) for row in hip3_book_rows}
            paper_result = run_paper_cycle(
                signals=signals,
                frames=frames,
                policy=self.risk.policy,
                usdc_zar=usdc_zar,
                positions_path=self.settings.data_dir
                / "research"
                / "paper_positions.json",
                log_path=self.settings.paper_log_path,
                cooldown_path=self.settings.cooldown_path,
                book_path=self.settings.book_path,
                book_slice_ids=book_slice_ids,
                server_time=server_time,
                hip3_book_path=self.settings.hip3_book_path if hip3_active else None,
                regime_shift=regime_shift,
                green_gate=green_gate,
            )
            def _append_blocked(entry: dict, guard: str) -> None:
                append_log(
                    self.settings.paper_log_path,
                    {
                        "closed_at": server_time.isoformat(),
                        "signal_id": "",
                        "pair": str(entry.get("pair") or ""),
                        "kind": str(entry.get("kind") or ""),
                        "slice_id": str(entry.get("slice_id") or ""),
                        "side": str(entry.get("side") or ""),
                        "entry_price": "",
                        "exit_price": "",
                        "stop_price": "",
                        "notional_zar": "0",
                        "pnl_zar": "0",
                        "outcome": "skipped",
                        "bars_held": "0",
                        "exit_reason": str(entry.get("reason") or guard),
                        "entry_guard": guard,
                        "regime": str(entry.get("regime") or ""),
                    },
                )

            for entry in blocked:
                _append_blocked(entry, str(entry.get("guard", "regime_blocked")))
            for entry in lane_gate_blocked:
                _append_blocked(
                    entry,
                    (
                        "lane_frozen"
                        if entry.get("reason") == "lane_not_green"
                        else "slice_not_green"
                    ),
                )
            paper_result["regime_blocked"] = len(blocked)
            paper_result["lane_gate_blocked"] = len(lane_gate_blocked)
            paper_result["session_blocked"] = sum(
                1 for entry in blocked if entry.get("guard") == "session_blocked"
            )
            paper_result["asset_not_green_blocked"] = sum(
                1 for entry in blocked if entry.get("guard") == "asset_not_green"
            )
        payloads = []
        for signal in signals:
            payload = {
                **{key: str(value) for key, value in asdict(signal).items()},
                "pair_type": signal_pair_type(signal.kind).value,
            }
            payloads.append(payload)
            self.ledger.append(
                event_id=signal.signal_id,
                kind="shadow_signal",
                payload=payload,
                strategy_id=signal.slice_id,
                pair=signal.pair,
            )
        errors = [{"pair": pair, "error": error} for pair, error in sorted(frame_errors.items())]
        result = {
            "server_time": server_time.isoformat(),
            "universe_symbols": {
                kind: len(universe.symbols(kind)) for kind in ("SPOT", "PERP")
            },
            "regime_shift": regime_shift_dict(regime_shift) if regime_shift is not None else None,
            "green_gate": green_gate.summary,
            "per_asset_gate": {
                "native_rows": len(asset_edge_lookup),
                "native": _asset_edge_status_counts(asset_edge_lookup),
                "hip3_rows": len(hip3_asset_edge_lookup),
                "hip3": _asset_edge_status_counts(hip3_asset_edge_lookup),
                "asset_not_green_blocked": sum(
                    1 for entry in blocked if entry.get("guard") == "asset_not_green"
                ),
            },
            "short_inventory": (
                {
                    "candidates": short_inventory.get("candidates"),
                    "eligible": short_inventory.get("eligible"),
                    "observations": short_inventory.get("observations"),
                    "armable": short_inventory.get("armable"),
                    "armable_slices": short_inventory.get("armable_slices", []),
                    "armable_pairs": short_inventory.get("armable_pairs", []),
                }
                if short_inventory is not None
                else None
            ),
            "book_slices": len(book_rows),
            "hip3_paper": {
                "active": hip3_active,
                "book_slices": len(hip3_book_rows),
            },
            "pairs_checked": len(frames),
            "pair_errors": errors,
            "signals": payloads,
            "regime_blocked": len(blocked),
            "paper": paper_result,
            "mode": self.settings.mode,
        }
        status_detail = {
            "pairs_checked": len(frames),
            "signals": len(signals),
            "errors": len(errors),
            "pair_errors": errors[:8],
            "regime_blocked": len(blocked),
            "lane_gate_blocked": len(lane_gate_blocked),
            "asset_not_green_blocked": sum(
                1 for entry in blocked if entry.get("guard") == "asset_not_green"
            ),
        }
        if regime_shift is not None:
            status_detail["regime_shift"] = regime_shift_dict(regime_shift)
        status_detail["green_gate"] = green_gate.summary
        status_detail["per_asset_gate"] = {
            "native_rows": len(asset_edge_lookup),
            "native": _asset_edge_status_counts(asset_edge_lookup),
            "hip3_rows": len(hip3_asset_edge_lookup),
            "hip3": _asset_edge_status_counts(hip3_asset_edge_lookup),
        }
        if short_inventory is not None:
            status_detail["short_inventory"] = {
                "candidates": short_inventory.get("candidates"),
                "eligible": short_inventory.get("eligible"),
                "observations": short_inventory.get("observations"),
                "armable": short_inventory.get("armable"),
                "armable_slices": short_inventory.get("armable_slices", []),
                "armable_pairs": short_inventory.get("armable_pairs", []),
                "confirmed_bear": short_inventory.get("confirmed_bear"),
                "promote_enabled": short_inventory.get("promote_enabled"),
            }
        if paper_result is not None:
            status_detail["paper"] = _compact_paper_status(paper_result)
            # Hard no-action telemetry: when the book produced signals but the
            # paper cycle opened none, name the dominant blocker. This turns
            # "the system is doing nothing" into a diagnosable event rather
            # than an inference from several CSV files.
            if signals and int(paper_result.get("opened") or 0) == 0:
                funnel = {
                    "regime_blocked": int(paper_result.get("regime_blocked", len(blocked)) or 0),
                    "aggregate_risk_cap_skips": int(paper_result.get("aggregate_risk_cap_skips") or 0),
                    "aggregate_risk_unknown_skips": int(paper_result.get("aggregate_risk_unknown_skips") or 0),
                    "slice_full": int(paper_result.get("slice_full") or 0),
                    "pair_held": int(paper_result.get("pair_held") or 0),
                    "slot_full": int(paper_result.get("slot_full") or 0),
                    "skipped": int(paper_result.get("skipped") or 0),
                    "lane_gate_blocked": int(paper_result.get("lane_gate_blocked", len(lane_gate_blocked)) or 0),
                }
                dominant = max(funnel, key=funnel.get)
                status_detail["no_action_reason"] = dominant
                status_detail["no_action_funnel"] = funnel
        append_status(
            self.settings.status_path,
            "shadow_scan_done",
            self.settings.mode,
            json.dumps(status_detail, sort_keys=True),
        )
        return result

    def _big_wave_fallback(
        self,
        targets: list[tuple[str, str]],
        frames: dict,
        server_time: datetime,
    ) -> list[SliceSignal]:
        signals: list[SliceSignal] = []
        for pair, kind in targets:
            frame = frames.get(pair.upper())
            if frame is None or frame.empty:
                continue
            pair_type = PairType.SPOT if kind == "SPOT" else PairType.FUTURE
            signal = detect_big_wave(
                self._candles_from_frame(frame),
                pair=pair.upper(),
                pair_type=pair_type,
                server_time=server_time,
            )
            if signal is None:
                continue
            signals.append(
                SliceSignal(
                    signal_id=signal.signal_id,
                    pair=pair.upper(),
                    kind=kind,
                    slice_id="big-wave",
                    feature="big-wave",
                    state=0,
                    side=signal.side,
                    observed_at=signal.observed_at,
                    bar_start=signal.candle_start,
                    entry_price=signal.entry_price,
                    stop_price=signal.stop_price,
                    atr=signal.atr,
                    edge=0.0,
                )
            )
        return signals

    def _candles_from_frame(self, frame) -> list[Candle]:
        candles = []
        for _, row in frame.iterrows():
            candles.append(
                Candle(
                    pair=str(row["symbol"]),
                    period_seconds=3600,
                    start=row["start"],
                    open=Decimal(str(row["open"])),
                    high=Decimal(str(row["high"])),
                    low=Decimal(str(row["low"])),
                    close=Decimal(str(row["close"])),
                    volume=Decimal(str(row["volume"])),
                )
            )
        return candles

    def operational_pass(self, *, max_pairs: int = 12) -> dict:
        guardian = self.guardian()
        scan = self.shadow_scan(max_pairs=max_pairs)
        result = {"guardian": guardian, "scan": scan, "execution": None}
        if self.settings.mode != "live":
            return result
        if guardian.get("risk_allowed") is not True:
            raise GuardianHalt("account risk gate blocks live execution")
        if guardian.get("exposure_slots", 0) != 0:
            return result
        specs = self.catalog.refresh()
        for payload in scan["signals"]:
            if payload.get("slice_id") != "big-wave":
                continue
            strategy_id = f"big-wave-{payload['pair']}-{str(payload['side']).lower()}"
            if self.registry.lifecycle(strategy_id) is not Lifecycle.LIVE_CAPPED:
                continue
            pair = str(payload["pair"])
            spec = specs[pair]
            summary = self.client.market_summary(pair)
            signal = detect_big_wave(
                fetch_recent_candles(
                    self.client,
                    pair,
                    datetime.fromisoformat(scan["server_time"]),
                ),
                pair=pair,
                pair_type=spec.pair_type,
                server_time=datetime.fromisoformat(scan["server_time"]),
                source_candidate_id=payload.get("source_candidate_id"),
            )
            if signal is None or signal.signal_id != payload["signal_id"]:
                raise GuardianHalt("signal changed during pre-execution confirmation")
            valuator = EquityValuator(self.client, specs)
            quote_to_zar = valuator.rate_to_zar(spec.quote_currency)
            plan = self.risk.plan_order(
                signal,
                spec,
                summary,
                quote_to_zar=quote_to_zar,
                equity_zar=Decimal(str(guardian["equity_zar"])),
            )
            receipt = TradeExecutor(self.client).execute(plan)
            execution = {
                "strategy_id": strategy_id,
                "signal_id": signal.signal_id,
                "pair": pair,
                "entry_order_id": receipt.entry_order_id,
                "protection_order_id": receipt.protection_order_id,
                "filled_quantity": str(receipt.filled_quantity),
                "average_price": str(receipt.average_price),
            }
            self.ledger.append(
                event_id=f"entry-{receipt.entry_order_id}",
                kind="live_entry",
                payload=execution,
                strategy_id=strategy_id,
                pair=pair,
            )
            append_status(
                self.settings.status_path,
                "live_entry_protected",
                self.settings.mode,
                json.dumps(execution, sort_keys=True),
            )
            result["execution"] = execution
            break
        return result

    def research_pass(self, *, max_pairs: int | None = None) -> dict:
        if max_pairs is None:
            max_pairs = _research_max_pairs()
        server_time, _ = self._server_state()
        self.catalog.refresh()
        universe = self._universe()

        from breakwater.discovery import _slice_stats, write_discovered
        from breakwater.research_lifecycle import sync_book
        from breakwater.validation import validate_slices, write_validated

        write_universe(self.settings.universe_path, universe)
        spot_targets = [(pair, "SPOT") for pair in universe.ranked("SPOT", max_pairs)]
        perp_targets = [(pair, "PERP") for pair in universe.ranked("PERP", max_pairs)]
        all_targets = spot_targets + perp_targets

        frames, frame_errors = self._frames(all_targets, server_time)
        if not frames:
            raise GuardianHalt(
                "no research frames could be fetched; refusing to overwrite "
                "research artifacts with empty results"
            )

        horizons = _parse_horizons_env()
        multi = len(horizons) > 1

        discovered = []
        validated = []
        asset_edges: list[AssetEdge] = []

        # Round-trip execution cost in bps, shared with the paper engine
        # (BREAKWATER_SPOT_FEE_BPS / BREAKWATER_PERP_FEE_BPS). Spot is VALR
        # spot fiat-quoted tier 1 (70 bps); perp is Hyperliquid base tier
        # (9 bps). See the cost-model comment in paper_trade.py.
        spot_cost_bps = _fee_bps_env("BREAKWATER_SPOT_FEE_BPS", "70")
        perp_cost_bps = _fee_bps_env("BREAKWATER_PERP_FEE_BPS", "9")
        for kind, cost_bps in (("SPOT", spot_cost_bps), ("PERP", perp_cost_bps)):
            # IMPORTANT: only include frames that actually exist (avoid KeyError).
            kind_frames = {}
            for pair, k in all_targets:
                if k != kind:
                    continue
                frame = frames.get(pair.upper())
                if frame is None:
                    continue
                kind_frames[pair.upper()] = frame

            pooled = _pool_frames(kind_frames)

            for horizon_bars in horizons:
                prepared = prepare_pooled(
                    pooled, FEATURE_COLUMNS, cost_bps, horizon_bars=horizon_bars
                )
                found = _slice_stats(
                    prepared, kind, FEATURE_COLUMNS, horizon_bars=horizon_bars
                )

                # Make IDs horizon-unique if multi-horizon research is enabled.
                found = _retag_candidates_for_horizon(
                    found, horizon_bars=horizon_bars, multi=multi
                )

                checked = validate_slices(prepared, found, asset_edges=asset_edges)

                discovered.extend(found)
                validated.extend(checked)

        write_discovered(self.settings.discovered_path, discovered)
        write_validated(self.settings.validated_path, validated)
        write_asset_edges(self.settings.asset_edges_path, asset_edges)

        # Research-side short audit: the daily pass must say plainly whether it
        # produced any short that qualifies. Shorts that cleared the floor but
        # failed on breadth/regime are reported so the operator knows *why* the
        # system has no short inventory, rather than only seeing zero.
        short_audit = _short_research_audit(validated, discovered)

        book_summary = sync_book(
            validated_path=self.settings.validated_path,
            book_path=self.settings.book_path,
            now=server_time,
        )

        # Record knob state in the committed research_done payload
        validation_require_bonferroni = os.getenv(
            "BREAKWATER_VALIDATION_REQUIRE_BONFERRONI", ""
        )
        validation_relaxed_min_passes = os.getenv(
            "BREAKWATER_VALIDATION_RELAXED_MIN_PASSES", ""
        )
        # Optional knobs (may be blank if not set)
        validation_strict_pass_floor = os.getenv("BREAKWATER_VALIDATION_STRICT_PASS_FLOOR", "")
        breadth_min_symbols = os.getenv("BREAKWATER_BREADTH_MIN_SYMBOLS", "")
        breadth_min_rows_per_symbol = os.getenv("BREAKWATER_BREADTH_MIN_ROWS_PER_SYMBOL", "")
        breadth_min_positive_fraction = os.getenv("BREAKWATER_BREADTH_MIN_POSITIVE_FRACTION", "")
        promotion_min_passes = os.getenv("BREAKWATER_PROMOTION_MULTI_HORIZON_MIN_PASSES", "")
        promotion_select = os.getenv("BREAKWATER_PROMOTION_MULTI_HORIZON_SELECT", "")
        promotion_require_contiguous = os.getenv(
            "BREAKWATER_PROMOTION_MULTI_HORIZON_REQUIRE_CONTIGUOUS", ""
        )
        min_net_edge = os.getenv("BREAKWATER_MIN_NET_EDGE", "")

        # Summarize dominant fail reasons (compact; durable)
        from collections import Counter

        fail_tokens = Counter()
        for row in validated:
            for tok in str(getattr(row, "fail_reasons", "") or "").split(","):
                tok = tok.strip()
                if tok:
                    fail_tokens[tok] += 1

        result = {
            "server_time": server_time.isoformat(),
            "universe": {k: len(universe.symbols(k)) for k in ("SPOT", "PERP")},
            "pairs_researched": len(frames),
            "frame_errors": [
                {"pair": pair, "error": error}
                for pair, error in sorted(frame_errors.items())
            ],
            "research_horizons": horizons,
            "spot_candle_count": _coerce_int(os.getenv("BREAKWATER_SPOT_CANDLE_COUNT", "300"), 300),
            "perp_candle_count": _coerce_int(os.getenv("BREAKWATER_PERP_CANDLE_COUNT", "300"), 300),
            "discovery_state_quantiles": os.getenv("BREAKWATER_DISCOVERY_STATE_QUANTILES", ""),
            "discovery_rolling_min_periods": os.getenv("BREAKWATER_DISCOVERY_ROLLING_MIN_PERIODS", ""),
            "discovered_slices": len(discovered),
            "validated_slices": len([row for row in validated if row.validated]),
            "regime_confounded_slices": len(
                [row for row in validated if row.regime_confounded]
            ),
            "hostile_unproven_slices": len(
                [row for row in validated if row.hostile_unproven]
            ),
            "per_asset_edges": {
                "rows": len(asset_edges),
                "green": sum(1 for row in asset_edges if row.asset_status == "green"),
                "blocked": sum(1 for row in asset_edges if row.asset_status == "blocked"),
                "untested": sum(1 for row in asset_edges if row.asset_status == "untested"),
            },
            "short_audit": short_audit,
            "validation_require_bonferroni": validation_require_bonferroni,
            "validation_relaxed_min_passes": validation_relaxed_min_passes,
            "book": book_summary,
        }

        # status.csv detail is capped (4000 chars); keep knobs early.
        status_detail = {
            "server_time": server_time.isoformat(),
            "pairs_researched": len(frames),
            "frame_errors": len(frame_errors),
            "pair_errors": [
                {"pair": pair, "error": error}
                for pair, error in sorted(frame_errors.items())
            ][:8],
            "research_horizons": horizons,
            "discovered_slices": len(discovered),
            "validated_slices": len([row for row in validated if row.validated]),
            "regime_confounded_slices": len([row for row in validated if row.regime_confounded]),
            "hostile_unproven_slices": len([row for row in validated if row.hostile_unproven]),
            "per_asset_edges": {
                "rows": len(asset_edges),
                "green": sum(1 for row in asset_edges if row.asset_status == "green"),
                "blocked": sum(1 for row in asset_edges if row.asset_status == "blocked"),
                "untested": sum(1 for row in asset_edges if row.asset_status == "untested"),
            },
            "short_audit": short_audit,
            "fail_top": fail_tokens.most_common(6),
            "knobs": {
                "BREAKWATER_MIN_NET_EDGE": min_net_edge,
                "BREAKWATER_VALIDATION_REQUIRE_BONFERRONI": validation_require_bonferroni,
                "BREAKWATER_VALIDATION_RELAXED_MIN_PASSES": validation_relaxed_min_passes,
                "BREAKWATER_VALIDATION_STRICT_PASS_FLOOR": validation_strict_pass_floor,
                "BREAKWATER_BREADTH_MIN_SYMBOLS": breadth_min_symbols,
                "BREAKWATER_BREADTH_MIN_ROWS_PER_SYMBOL": breadth_min_rows_per_symbol,
                "BREAKWATER_BREADTH_MIN_POSITIVE_FRACTION": breadth_min_positive_fraction,
                "BREAKWATER_PROMOTION_MULTI_HORIZON_MIN_PASSES": promotion_min_passes,
                "BREAKWATER_PROMOTION_MULTI_HORIZON_SELECT": promotion_select,
                "BREAKWATER_PROMOTION_MULTI_HORIZON_REQUIRE_CONTIGUOUS": promotion_require_contiguous,
                "BREAKWATER_RESEARCH_MAX_PAIRS": str(max_pairs),
                "BREAKWATER_SPOT_CANDLE_COUNT": os.getenv("BREAKWATER_SPOT_CANDLE_COUNT", ""),
                "BREAKWATER_PERP_CANDLE_COUNT": os.getenv("BREAKWATER_PERP_CANDLE_COUNT", ""),
            },
            "book": book_summary,
        }
        append_status(
            self.settings.status_path,
            "research_done",
            self.settings.mode,
            json.dumps(status_detail, sort_keys=True),
        )
        return result

    def health(self) -> dict:
        """Local one-glance heartbeat; performs no network calls.

        Standing lesson (green != live): a green workflow run is not proof
        that anything traded or that the book is alive. This digest
        surfaces universe freshness, book composition and paper activity
        from the committed state files.
        """
        from collections import Counter

        result: dict = {"mode": self.settings.mode}
        snapshot = read_universe(self.settings.universe_path)
        if snapshot is None:
            result["universe"] = {"status": "missing"}
        else:
            age_hours = None
            try:
                as_of = datetime.fromisoformat(snapshot.as_of)
                age_hours = round(
                    (datetime.now(timezone.utc) - as_of).total_seconds() / 3600,
                    1,
                )
            except (TypeError, ValueError):
                pass
            result["universe"] = {
                "status": ("ok" if age_hours is not None and age_hours < 168 else "stale"),
                "age_hours": age_hours,
                "spot_symbols": len(snapshot.symbols("SPOT")),
                "perp_symbols": len(snapshot.symbols("PERP")),
            }
        book_rows = read_book(self.settings.book_path)
        result["book"] = {
            "rows": len(book_rows),
            "statuses": dict(Counter(row.get("status") for row in book_rows)),
            "kinds": dict(Counter(row.get("kind") for row in book_rows)),
            "sides": dict(Counter(row.get("side") for row in book_rows)),
            "hostile_unproven": sum(
                1 for row in book_rows if row.get("hostile_unproven") == "True"
            ),
        }
        positions = read_positions(self.settings.data_dir / "research" / "paper_positions.json")
        result["paper_open_positions"] = len(positions)
        result["paper_positions"] = [
            {
                "pair": position.get("pair"),
                "side": position.get("side"),
                "bars_held": position.get("bars_held"),
            }
            for position in positions
        ]
        return result

    def startup_assertions(self) -> None:
        if self.settings.mode == "live" and not self.settings.writes_allowed:
            raise GuardianHalt("live mode is not armed")
        if self.settings.mode == "live" and not self.settings.has_credentials:
            raise GuardianHalt("live mode requires VALR credentials")
        if self.settings.mode == "live" and self.risk is None:
            raise GuardianHalt("live mode requires a configured capital mandate")
        if self.settings.mode == "live":
            live = [
                row
                for row in self.registry.load()["strategies"].values()
                if row.get("lifecycle") == Lifecycle.LIVE_CAPPED.value
            ]
            if not live:
                raise GuardianHalt("no strategy has passed the live-capped promotion gate")


def _pool_frames(frames: dict):
    import pandas as pd

    parts = []
    for pair, frame in frames.items():
        if frame is None or frame.empty:
            continue
        featured = compute_price_features(frame)
        featured["symbol"] = pair.upper()
        parts.append(featured)
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True)
