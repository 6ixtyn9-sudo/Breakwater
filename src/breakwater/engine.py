"""Restart-safe guardian, universe scanner and guarded executor."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from breakwater.account import (
    EquityValuator,
    unprotected_positions,
    validate_api_key_permissions,
)
from breakwater.config import Settings
from breakwater.discovery import prepare_pooled
from breakwater.execution import TradeExecutor
from breakwater.features import FEATURE_COLUMNS, candle_frame, compute_price_features
from breakwater.ledger import Ledger
from breakwater.market import (
    MarketCatalog,
    authoritative_server_time,
    fetch_recent_candles,
)
from breakwater.models import Candle, Lifecycle, PairType
from breakwater.monitor import SliceSignal, monitor_book, signal_pair_type
from breakwater.paper_trade import append_log, read_positions, run_paper_cycle
from breakwater.perpdata import fetch_perp_candles_for_pair
from breakwater.promotion import PromotionRegistry
from breakwater.research_lifecycle import read_book
from breakwater.risk import RiskManager
from breakwater.risk_state import RiskStateStore
from breakwater.status import append_status
from breakwater.strategy import detect_big_wave
from breakwater.universe import (
    UniverseSnapshot,
    ingest_universe,
    is_legacy_universe,
    read_universe,
    write_universe,
)
from breakwater.valr import ValrClient


class GuardianHalt(RuntimeError):
    pass


def _coerce_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_horizons_env() -> list[int]:
    """Parse research horizons.

    Supported env:
      - BREAKWATER_RESEARCH_HORIZONS="6,12,24"  (preferred)
      - BREAKWATER_RESEARCH_HORIZON_BARS="6"    (fallback)

    Returns a de-duplicated list preserving input order (after cleaning).
    """
    raw = str(os.getenv("BREAKWATER_RESEARCH_HORIZONS", "")).strip()
    if raw:
        parts = []
        for chunk in raw.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            try:
                value = int(chunk)
            except ValueError:
                continue
            if value >= 1 and value not in parts:
                parts.append(value)
        if parts:
            return parts

    # Fallback
    single = _coerce_int(os.getenv("BREAKWATER_RESEARCH_HORIZON_BARS", "1"), 1)
    if single < 1:
        single = 1
    return [single]


def _slice_id_with_horizon(slice_id: str, horizon_bars: int, *, multi: bool) -> str:
    """Make slice IDs horizon-unique when multi-horizon is enabled."""
    if not multi:
        return slice_id
    suffix = f":h{int(horizon_bars)}"
    if str(slice_id).endswith(suffix):
        return slice_id
    return f"{slice_id}{suffix}"


def _retag_discovered_with_horizon(found, *, horizon_bars: int, multi: bool):
    """Return a list of SliceStat with slice_id tagged when needed."""
    if not multi:
        return found
    tagged = []
    for row in found:
        payload = asdict(row)
        payload["slice_id"] = _slice_id_with_horizon(payload["slice_id"], horizon_bars, multi=True)
        tagged.append(type(row)(**payload))
    return tagged


class BreakwaterEngine:
    def __init__(self, settings: Settings, *, client: ValrClient | None = None):
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
        if snapshot is not None and not is_legacy_universe(snapshot):
            try:
                as_of = datetime.fromisoformat(snapshot.as_of)
                if datetime.now(timezone.utc) - as_of < timedelta(days=7):
                    return snapshot
            except (TypeError, ValueError):
                pass
        snapshot = ingest_universe(self.client)
        write_universe(self.settings.universe_path, snapshot)
        return snapshot

    def _frames(self, targets: list[tuple[str, str]], server_time: datetime):
        frames = {}
        errors = {}

        def _coerce_int_local(value, default: int) -> int:
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        spot_count = _coerce_int_local(os.getenv("BREAKWATER_SPOT_CANDLE_COUNT", "300"), 300)
        perp_count = _coerce_int_local(os.getenv("BREAKWATER_PERP_CANDLE_COUNT", "300"), 300)

        # Safety clamps (spot paging supports up to 5000; perps already supports up to 5000)
        spot_count = max(60, min(5000, spot_count))
        perp_count = max(60, min(5000, perp_count))

        for pair, kind in targets:
            try:
                if kind == "PERP":
                    candles = fetch_perp_candles_for_pair(pair, count=perp_count)
                else:
                    candles = fetch_recent_candles(self.client, pair, server_time, count=spot_count)
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

    def shadow_scan(self, *, max_pairs: int = 12) -> dict:
        server_time, _ = self._server_state()
        self.catalog.refresh()
        universe = self._universe()
        book_rows = [
            row
            for row in read_book(self.settings.book_path)
            if row.get("status") == "monitored"
        ]
        targets = [
            (pair, kind)
            for kind in ("SPOT", "PERP")
            for pair in universe.ranked(kind, max_pairs)
        ]
        frames, frame_errors = self._frames(targets, server_time)
        frames_by_kind: dict[str, dict] = {"SPOT": {}, "PERP": {}}
        for pair, kind in targets:
            frame = frames.get(pair.upper())
            if frame is not None:
                frames_by_kind[kind][pair.upper()] = frame

        signals: list[SliceSignal] = []
        blocked: list[dict] = []
        if book_rows:
            signals, blocked = monitor_book(
                book_rows, frames_by_kind, server_time=server_time
            )
        else:
            signals = self._big_wave_fallback(targets, frames, server_time)

        paper_result = None
        if self.settings.mode in {"shadow", "live"} and self.risk is not None:
            valuator = EquityValuator(self.client, self.catalog.refresh())
            try:
                usdc_zar = valuator.rate_to_zar("USDC")
            except Exception:
                usdc_zar = Decimal("16.29")
            book_slice_ids = {str(row["slice_id"]) for row in book_rows}
            paper_result = run_paper_cycle(
                signals=signals,
                frames=frames,
                policy=self.risk.policy,
                usdc_zar=usdc_zar,
                positions_path=self.settings.data_dir / "research" / "paper_positions.json",
                log_path=self.settings.paper_log_path,
                cooldown_path=self.settings.cooldown_path,
                book_path=self.settings.book_path,
                book_slice_ids=book_slice_ids,
                server_time=server_time,
            )
            for entry in blocked:
                append_log(
                    self.settings.paper_log_path,
                    {
                        "closed_at": server_time.isoformat(),
                        "signal_id": "",
                        "pair": entry["pair"],
                        "kind": entry["kind"],
                        "slice_id": entry["slice_id"],
                        "side": entry["side"],
                        "entry_price": "",
                        "exit_price": "",
                        "stop_price": "",
                        "notional_zar": "0",
                        "pnl_zar": "0",
                        "outcome": "skipped",
                        "bars_held": "0",
                        "exit_reason": "regime",
                        "entry_guard": "regime_blocked",
                        "regime": entry["regime"],
                    },
                )
            paper_result["regime_blocked"] = len(blocked)

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
            "universe_symbols": {kind: len(universe.symbols(kind)) for kind in ("SPOT", "PERP")},
            "book_slices": len(book_rows),
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
            "regime_blocked": len(blocked),
        }
        if paper_result is not None:
            status_detail["paper"] = paper_result
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

    def research_pass(self, *, max_pairs: int = 30) -> dict:
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

        for kind, cost_bps in (("SPOT", 20.0), ("PERP", 26.0)):
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

                found = _retag_discovered_with_horizon(found, horizon_bars=horizon_bars, multi=multi)

                checked = validate_slices(prepared, found)
                discovered.extend(found)
                validated.extend(checked)

        write_discovered(self.settings.discovered_path, discovered)
        write_validated(self.settings.validated_path, validated)

        book_summary = sync_book(
            validated_path=self.settings.validated_path,
            book_path=self.settings.book_path,
            now=server_time,
        )

        validation_require_bonferroni = os.getenv("BREAKWATER_VALIDATION_REQUIRE_BONFERRONI", "")
        validation_relaxed_min_passes = os.getenv("BREAKWATER_VALIDATION_RELAXED_MIN_PASSES", "")

        spot_count = _coerce_int(os.getenv("BREAKWATER_SPOT_CANDLE_COUNT", "300"), 300)
        perp_count = _coerce_int(os.getenv("BREAKWATER_PERP_CANDLE_COUNT", "300"), 300)

        discovered_positive_mean = sum(1 for row in discovered if float(getattr(row, "mean_ret_costadj", 0.0)) > 0.0)
        discovered_bonf_pass = sum(1 for row in discovered if bool(getattr(row, "bonferroni_pass", False)))

        result = {
            "server_time": server_time.isoformat(),
            "universe": {k: len(universe.symbols(k)) for k in ("SPOT", "PERP")},
            "pairs_researched": len(frames),
            "frame_errors": [{"pair": pair, "error": error} for pair, error in sorted(frame_errors.items())],
            "research_horizons": horizons,
            "spot_candle_count": spot_count,
            "perp_candle_count": perp_count,
            "discovery_state_quantiles": os.getenv("BREAKWATER_DISCOVERY_STATE_QUANTILES", ""),
            "discovery_rolling_min_periods": os.getenv("BREAKWATER_DISCOVERY_ROLLING_MIN_PERIODS", ""),
            "discovered_slices": len(discovered),
            "discovered_positive_mean": discovered_positive_mean,
            "discovered_bonferroni_pass": discovered_bonf_pass,
            "validated_slices": len([row for row in validated if row.validated]),
            "regime_confounded_slices": len([row for row in validated if row.regime_confounded]),
            "hostile_unproven_slices": len([row for row in validated if row.hostile_unproven]),
            "validation_require_bonferroni": validation_require_bonferroni,
            "validation_relaxed_min_passes": validation_relaxed_min_passes,
            "book": book_summary,
        }

        append_status(
            self.settings.status_path,
            "research_done",
            self.settings.mode,
            json.dumps(result, sort_keys=True),
        )
        return result

    def health(self) -> dict:
        """Local one-glance heartbeat; performs no network calls."""
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
            "hostile_unproven": sum(1 for row in book_rows if row.get("hostile_unproven") == "True"),
        }
        positions = read_positions(self.settings.data_dir / "research" / "paper_positions.json")
        result["paper_open_positions"] = len(positions)
        result["paper_positions"] = [
            {"pair": position.get("pair"), "side": position.get("side"), "bars_held": position.get("bars_held")}
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
