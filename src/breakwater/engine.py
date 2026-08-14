"""Restart-safe guardian and shadow scanner."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal

from breakwater.account import (
    EquityValuator,
    unprotected_positions,
    validate_api_key_permissions,
)
from breakwater.config import INITIAL_EQUITY_ZAR, Settings
from breakwater.execution import TradeExecutor
from breakwater.ledger import Ledger
from breakwater.market import (
    MarketCatalog,
    authoritative_server_time,
    fetch_recent_candles,
    require_tradeable_market,
)
from breakwater.models import Lifecycle, PairType
from breakwater.price_bridge import candidate_pairs, load_candidates
from breakwater.promotion import PromotionRegistry
from breakwater.risk import RiskManager
from breakwater.risk_state import RiskStateStore
from breakwater.status import append_status
from breakwater.strategy import detect_big_wave
from breakwater.valr import ValrClient


class GuardianHalt(RuntimeError):
    pass


def _flatten_balance_groups(rows: list[dict]) -> list[dict]:
    flattened = []
    for row in rows:
        balances = row.get("balances")
        if not isinstance(balances, list):
            raise GuardianHalt("all-account balance response is malformed")
        flattened.extend(balances)
    return flattened


class BreakwaterEngine:
    def __init__(self, settings: Settings, *, client: ValrClient | None = None):
        self.settings = settings
        self.client = client or ValrClient(
            api_key=settings.api_key,
            api_secret=settings.api_secret,
            subaccount_id=settings.subaccount_id,
            allow_writes=settings.writes_allowed,
        )
        self.ledger = Ledger(settings.ledger_path)
        self.catalog = MarketCatalog(self.client)
        self.risk = RiskManager()
        self.risk_state = RiskStateStore(settings.risk_state_path)
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

    def guardian(self) -> dict:
        server_time, exchange_status = self._server_state()
        specs = self.catalog.refresh()
        active_spot = self.catalog.active(PairType.SPOT)
        active_futures = self.catalog.active(PairType.FUTURE)
        result = {
            "server_time": server_time.isoformat(),
            "exchange_status": exchange_status.get("status"),
            "active_spot_pairs": len(active_spot),
            "active_futures_pairs": len(active_futures),
            "authenticated": self.settings.has_credentials,
            "mode": self.settings.mode,
        }
        if not self.settings.has_credentials:
            append_status(
                self.settings.status_path, "public_ok", self.settings.mode,
                json.dumps(result, sort_keys=True),
            )
            return result

        key_client = (
            ValrClient(
                api_key=self.settings.api_key,
                api_secret=self.settings.api_secret,
                allow_writes=False,
            )
            if self.settings.subaccount_id else self.client
        )
        key_info = key_client.current_api_key()
        permissions = validate_api_key_permissions(
            key_info, live=self.settings.mode == "live"
        )
        is_subaccount_key = key_info.get("isSubAccount") is True
        if is_subaccount_key and self.settings.subaccount_id:
            raise GuardianHalt("subaccount key must not also configure VALR_SUBACCOUNT_ID")

        balances = self.client.balances()
        positions = self.client.open_positions()
        open_orders = self.client.open_orders()
        conditionals = self.client.conditional_orders() if positions else []
        missing_protection = unprotected_positions(positions, open_orders, conditionals)
        if missing_protection:
            pairs = ",".join(position.pair for position in missing_protection)
            append_status(
                self.settings.status_path, "unprotected_position", self.settings.mode, pairs
            )
            raise GuardianHalt(f"open positions lack confirmed stop protection: {pairs}")

        if is_subaccount_key:
            if self.settings.mode == "live":
                raise GuardianHalt(
                    "live mode requires a main-account key so global equity can be verified"
                )
            global_balances = balances
        else:
            global_client = ValrClient(
                api_key=self.settings.api_key,
                api_secret=self.settings.api_secret,
                allow_writes=False,
            )
            global_balances = _flatten_balance_groups(global_client.all_account_balances())

        valuator = EquityValuator(self.client, specs)
        equity_zar = valuator.equity_zar(global_balances, positions)
        high_water = self.risk_state.observe_equity(equity_zar)
        exposure_symbols = {position.pair for position in positions}
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
        result.update({
            "equity_zar": str(equity_zar.quantize(Decimal("0.01"))),
            "high_water_zar": str(high_water.quantize(Decimal("0.01"))),
            "positions": len(positions),
            "open_orders": len(open_orders),
            "exposure_slots": len(exposure_symbols),
            "risk_allowed": risk_state.allowed,
            "risk_reasons": list(risk_state.reasons),
            "key_is_subaccount": is_subaccount_key,
            "key_permissions": sorted(permissions),
            "key_ip_restricted": bool(key_info.get("allowedIpAddressCidr")),
        })
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
        specs = self.catalog.refresh()
        active_spot = {spec.symbol for spec in self.catalog.active(PairType.SPOT)}
        active_futures = self.catalog.active_perpetual_symbols()
        candidates = load_candidates(self.settings.candidates_path)
        targets = []
        for candidate in candidates:
            for pair in candidate_pairs(candidate, active_spot, active_futures):
                targets.append((pair, candidate.side, candidate.candidate_id))
        if not targets:
            targets = [(pair, None, None) for pair in sorted(active_futures)]
        seen = set()
        signals = []
        errors = []
        for pair, allowed_side, candidate_id in targets:
            if pair in seen or len(seen) >= max_pairs:
                continue
            seen.add(pair)
            try:
                spec = specs[pair]
                summary = self.client.market_summary(pair)
                require_tradeable_market(spec, summary, server_time)
                candles = fetch_recent_candles(self.client, pair, server_time)
                signal = detect_big_wave(
                    candles,
                    pair=pair,
                    pair_type=spec.pair_type,
                    server_time=server_time,
                    allowed_side=allowed_side,
                    source_candidate_id=candidate_id,
                )
                if signal is None:
                    continue
                lifecycle = self.registry.lifecycle(f"big-wave-{pair}-{signal.side.value.lower()}")
                payload = {
                    **asdict(signal),
                    "pair_type": signal.pair_type.value,
                    "side": signal.side.value,
                    "lifecycle": lifecycle.value,
                }
                for key, value in list(payload.items()):
                    if isinstance(value, (Decimal, datetime)):
                        payload[key] = str(value)
                self.ledger.append(
                    event_id=signal.signal_id,
                    kind="shadow_signal",
                    payload=payload,
                    strategy_id=f"big-wave-{pair}-{signal.side.value.lower()}",
                    pair=pair,
                )
                signals.append(payload)
            except Exception as exc:
                errors.append({"pair": pair, "error": f"{type(exc).__name__}: {exc}"})
        result = {
            "server_time": server_time.isoformat(),
            "pairs_checked": len(seen),
            "signals": signals,
            "errors": errors,
            "mode": self.settings.mode,
        }
        if seen and len(errors) == len(seen):
            raise GuardianHalt("every VALR-native market scan failed")
        append_status(
            self.settings.status_path,
            "shadow_scan_done",
            self.settings.mode,
            json.dumps({
                "pairs_checked": len(seen),
                "signals": len(signals),
                "errors": len(errors),
            }, sort_keys=True),
        )
        return result

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
            strategy_id = (
                f"big-wave-{payload['pair']}-{str(payload['side']).lower()}"
            )
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

    def startup_assertions(self) -> None:
        if self.settings.mode == "live" and not self.settings.writes_allowed:
            raise GuardianHalt("live mode is not armed")
        if self.settings.mode == "live" and not self.settings.has_credentials:
            raise GuardianHalt("live mode requires VALR credentials")
        if self.settings.mode == "live" and INITIAL_EQUITY_ZAR != Decimal("331.45"):
            raise GuardianHalt("compiled initial equity boundary changed unexpectedly")
        if self.settings.mode == "live":
            live = [
                row for row in self.registry.load()["strategies"].values()
                if row.get("lifecycle") == Lifecycle.LIVE_CAPPED.value
            ]
            if not live:
                raise GuardianHalt("no strategy has passed the live-capped promotion gate")
