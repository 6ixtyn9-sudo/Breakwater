"""Testnet-only Hyperliquid execution boundary.

The module uses the official SDK lazily, so normal Breakwater operation does
not import signing dependencies. It accepts only a dedicated API/agent key,
refuses the master key by comparing derived addresses, and is structurally
pinned to the Hyperliquid testnet endpoint.

This is mechanism-canary infrastructure, not a live executor. Mainnet cannot
be selected through configuration or arguments in this module.
"""

from __future__ import annotations

import fcntl
import hashlib
import os
import re
import tempfile
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path

from breakwater.hyperliquid import HyperliquidReadOnlyVenue, validate_account_address
from breakwater.models import Side
from breakwater.perp_venue import (
    PerpAccountSnapshot,
    PerpInstrument,
    PerpVenueError,
    assess_native_stop_protection,
)

TESTNET_ACK = "I_ACCEPT_BREAKWATER_HYPERLIQUID_TESTNET_ORDERS"
_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
_PRIVATE_KEY = re.compile(r"^(?:0x)?[0-9a-fA-F]{64}$")


class HyperliquidTestnetBlocked(PerpVenueError):
    pass


@dataclass(frozen=True)
class ProtectionCanaryPlan:
    run_id: str
    symbol: str
    side: Side
    quantity: Decimal
    stop_fraction: Decimal = Decimal("0.01")
    target_fraction: Decimal = Decimal("0.02")
    max_notional_usdc: Decimal = Decimal("25")
    max_slippage: Decimal = Decimal("0.01")


@dataclass(frozen=True)
class ProtectionCanaryReceipt:
    run_id: str
    symbol: str
    entry_order_id: str
    entry_client_order_id: str
    stop_client_order_id: str
    target_client_order_id: str
    filled_quantity: Decimal
    average_price: Decimal
    stop_price: Decimal
    target_price: Decimal
    protection_verified: bool


def deterministic_cloid(run_id: str, role: str) -> str:
    if not _RUN_ID.fullmatch(str(run_id)):
        raise ValueError("run_id must be 1-64 safe identifier characters")
    digest = hashlib.sha256(f"breakwater:hl-testnet:{run_id}:{role}".encode()).hexdigest()
    return f"0x{digest[:32]}"


def _round_price(price: Decimal, instrument: PerpInstrument) -> Decimal:
    if price <= 0 or not price.is_finite():
        raise ValueError("price must be positive and finite")
    decimal_quantum = Decimal(1).scaleb(-instrument.max_price_decimals)
    significant_quantum = Decimal(1).scaleb(price.adjusted() - instrument.max_significant_figures + 1)
    quantum = max(decimal_quantum, significant_quantum)
    return price.quantize(quantum, rounding=ROUND_HALF_EVEN)


def _response_statuses(response: dict, *, operation: str) -> list[dict]:
    try:
        if response["status"] != "ok":
            raise HyperliquidTestnetBlocked(f"{operation} was not accepted")
        statuses = response["response"]["data"]["statuses"]
    except (KeyError, TypeError) as exc:
        raise HyperliquidTestnetBlocked(f"{operation} response is malformed") from exc
    if not isinstance(statuses, list) or not statuses:
        raise HyperliquidTestnetBlocked(f"{operation} returned no order statuses")
    for status in statuses:
        if not isinstance(status, dict):
            raise HyperliquidTestnetBlocked(f"{operation} order status is malformed")
        if status.get("error"):
            raise HyperliquidTestnetBlocked(f"{operation} rejected: {status['error']}")
    return statuses


class HyperliquidTestnetExecutor:
    """Official-SDK wrapper that can only submit Hyperliquid testnet actions."""

    def __init__(
        self,
        *,
        exchange,
        venue: HyperliquidReadOnlyVenue,
        account_address: str,
        agent_address: str,
        cloid_factory,
        acknowledgement: str,
    ):
        if not venue.testnet:
            raise HyperliquidTestnetBlocked("signed executor requires a testnet read venue")
        if acknowledgement != TESTNET_ACK:
            raise HyperliquidTestnetBlocked("Hyperliquid testnet acknowledgement is missing")
        self.account_address = validate_account_address(account_address)
        self.agent_address = validate_account_address(agent_address)
        if self.account_address.lower() == self.agent_address.lower():
            raise HyperliquidTestnetBlocked(
                "agent address equals account address; never give Breakwater the master key"
            )
        self.exchange = exchange
        self.venue = venue
        self.cloid_factory = cloid_factory
        self._thread_lock = threading.Lock()
        lock_name = f"breakwater-hl-{self.agent_address.lower()}.nonce.lock"
        self._nonce_lock_path = Path(tempfile.gettempdir()) / lock_name

    @classmethod
    def from_environment(cls) -> "HyperliquidTestnetExecutor":
        account_address = os.getenv("HYPERLIQUID_TESTNET_ACCOUNT_ADDRESS", "").strip()
        private_key = os.getenv("HYPERLIQUID_TESTNET_AGENT_PRIVATE_KEY", "").strip()
        acknowledgement = os.getenv("BREAKWATER_HYPERLIQUID_TESTNET_ACK", "")
        if not account_address:
            raise HyperliquidTestnetBlocked("HYPERLIQUID_TESTNET_ACCOUNT_ADDRESS is missing")
        if not _PRIVATE_KEY.fullmatch(private_key):
            raise HyperliquidTestnetBlocked(
                "HYPERLIQUID_TESTNET_AGENT_PRIVATE_KEY must be a dedicated 32-byte agent key"
            )
        try:
            from eth_account import Account
            from hyperliquid.exchange import Exchange
            from hyperliquid.utils import constants
            from hyperliquid.utils.types import Cloid
        except ImportError as exc:
            raise HyperliquidTestnetBlocked(
                "install the pinned signing extra with: pip install -e '.[hyperliquid]'"
            ) from exc

        wallet = Account.from_key(private_key)
        exchange = Exchange(
            wallet,
            base_url=constants.TESTNET_API_URL,
            account_address=account_address,
        )
        venue = HyperliquidReadOnlyVenue(testnet=True)
        return cls(
            exchange=exchange,
            venue=venue,
            account_address=account_address,
            agent_address=wallet.address,
            cloid_factory=Cloid.from_str,
            acknowledgement=acknowledgement,
        )

    @contextmanager
    def _write_slot(self):
        """Serialize SDK timestamp nonces across threads and local processes."""
        with self._thread_lock:
            with self._nonce_lock_path.open("a+") as handle:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
                try:
                    handle.seek(0)
                    raw = handle.read().strip()
                    last_ms = int(raw) if raw.isdigit() else 0
                    while int(time.time() * 1000) <= last_ms:
                        time.sleep(0.001)
                    yield
                    used_ms = int(time.time() * 1000)
                    handle.seek(0)
                    handle.truncate()
                    handle.write(str(used_ms))
                    handle.flush()
                    os.fsync(handle.fileno())
                finally:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def _instrument(self, symbol: str) -> PerpInstrument:
        normalized = str(symbol).upper().strip()
        matches = [item for item in self.venue.instruments() if item.symbol == normalized and item.active]
        if len(matches) != 1:
            raise HyperliquidTestnetBlocked(f"testnet instrument is unavailable: {normalized}")
        return matches[0]

    @staticmethod
    def _validate_plan(plan: ProtectionCanaryPlan, instrument: PerpInstrument) -> None:
        if not _RUN_ID.fullmatch(plan.run_id):
            raise HyperliquidTestnetBlocked("canary run_id is invalid")
        if plan.quantity <= 0 or not plan.quantity.is_finite():
            raise HyperliquidTestnetBlocked("canary quantity must be positive and finite")
        if plan.quantity % instrument.size_step != 0:
            raise HyperliquidTestnetBlocked(
                f"quantity must align to {instrument.symbol} size step {instrument.size_step}"
            )
        for name, value in (
            ("stop_fraction", plan.stop_fraction),
            ("target_fraction", plan.target_fraction),
            ("max_slippage", plan.max_slippage),
        ):
            if value <= 0 or value > Decimal("0.05") or not value.is_finite():
                raise HyperliquidTestnetBlocked(f"{name} must be greater than 0 and at most 0.05")
        notional = plan.quantity * instrument.mark_price
        if notional < instrument.min_notional:
            raise HyperliquidTestnetBlocked(
                f"canary notional {notional} is below venue minimum {instrument.min_notional}"
            )
        if notional > plan.max_notional_usdc or plan.max_notional_usdc > Decimal("25"):
            raise HyperliquidTestnetBlocked("canary notional exceeds the hard 25 USDC testnet cap")

    def _snapshot(self) -> PerpAccountSnapshot:
        return self.venue.account_snapshot(self.account_address)

    def _confirm_position(self, symbol: str, attempts: int = 10) -> PerpAccountSnapshot:
        for attempt in range(attempts):
            snapshot = self._snapshot()
            if any(position.symbol == symbol for position in snapshot.positions):
                return snapshot
            if attempt + 1 < attempts:
                time.sleep(0.5)
        raise HyperliquidTestnetBlocked("entry fill did not reconcile to account position state")

    def _emergency_close(self, coin: str) -> None:
        try:
            with self._write_slot():
                response = self.exchange.market_close(coin)
            _response_statuses(response, operation="emergency close")
        except Exception as exc:
            raise HyperliquidTestnetBlocked(
                "protection failed and emergency testnet close could not be confirmed"
            ) from exc

    def _emergency_close_if_open(self, symbol: str, coin: str) -> None:
        try:
            snapshot = self._snapshot()
        except Exception as exc:
            raise HyperliquidTestnetBlocked(
                "entry response was uncertain and account state could not be reconciled"
            ) from exc
        if any(position.symbol == symbol for position in snapshot.positions):
            self._emergency_close(coin)

    def open_with_native_protection(
        self, plan: ProtectionCanaryPlan
    ) -> ProtectionCanaryReceipt:
        instrument = self._instrument(plan.symbol)
        self._validate_plan(plan, instrument)
        initial = self._snapshot()
        if initial.positions or initial.open_orders:
            raise HyperliquidTestnetBlocked(
                "mechanism canary requires an otherwise flat testnet account with no open orders"
            )

        entry_cloid_text = deterministic_cloid(plan.run_id, "entry")
        entry_cloid = self.cloid_factory(entry_cloid_text)
        with self._write_slot():
            entry_response = self.exchange.market_open(
                instrument.coin,
                plan.side is Side.BUY,
                float(plan.quantity),
                px=float(instrument.mark_price),
                slippage=float(plan.max_slippage),
                cloid=entry_cloid,
            )
        try:
            statuses = _response_statuses(entry_response, operation="testnet entry")
            filled = statuses[0].get("filled")
            if not isinstance(filled, dict):
                raise HyperliquidTestnetBlocked("testnet IOC entry did not fill")
            order_id = str(filled["oid"])
            filled_quantity = Decimal(str(filled["totalSz"]))
            average_price = Decimal(str(filled["avgPx"]))
        except Exception:
            self._emergency_close_if_open(instrument.symbol, instrument.coin)
            raise

        try:
            snapshot = self._confirm_position(instrument.symbol)
            matching = [position for position in snapshot.positions if position.symbol == instrument.symbol]
            if len(matching) != 1 or len(snapshot.positions) != 1:
                raise HyperliquidTestnetBlocked("testnet account position state is ambiguous")
            position = matching[0]
            if position.side is not plan.side or position.quantity != filled_quantity:
                raise HyperliquidTestnetBlocked("testnet position does not match the confirmed fill")

            direction = Decimal(1) if plan.side is Side.BUY else Decimal(-1)
            stop_price = _round_price(
                average_price * (Decimal(1) - direction * plan.stop_fraction), instrument
            )
            target_price = _round_price(
                average_price * (Decimal(1) + direction * plan.target_fraction), instrument
            )
            stop_cloid_text = deterministic_cloid(plan.run_id, "stop")
            target_cloid_text = deterministic_cloid(plan.run_id, "target")
            is_closing_buy = plan.side is Side.SELL
            requests = [
                {
                    "coin": instrument.coin,
                    "is_buy": is_closing_buy,
                    "sz": float(filled_quantity),
                    "limit_px": float(stop_price),
                    "order_type": {
                        "trigger": {
                            "triggerPx": float(stop_price),
                            "isMarket": True,
                            "tpsl": "sl",
                        }
                    },
                    "reduce_only": True,
                    "cloid": self.cloid_factory(stop_cloid_text),
                },
                {
                    "coin": instrument.coin,
                    "is_buy": is_closing_buy,
                    "sz": float(filled_quantity),
                    "limit_px": float(target_price),
                    "order_type": {
                        "trigger": {
                            "triggerPx": float(target_price),
                            "isMarket": True,
                            "tpsl": "tp",
                        }
                    },
                    "reduce_only": True,
                    "cloid": self.cloid_factory(target_cloid_text),
                },
            ]
            with self._write_slot():
                protection_response = self.exchange.bulk_orders(
                    requests, grouping="positionTpsl"
                )
            protection_statuses = _response_statuses(
                protection_response, operation="native testnet protection"
            )
            if len(protection_statuses) != 2 or not all(
                "resting" in status for status in protection_statuses
            ):
                raise HyperliquidTestnetBlocked("native testnet protection did not rest")

            protected_snapshot = self._snapshot()
            protection = assess_native_stop_protection(protected_snapshot)
            if instrument.symbol in protection.unprotected_symbols:
                raise HyperliquidTestnetBlocked("native reduce-only stop could not be verified")
            return ProtectionCanaryReceipt(
                run_id=plan.run_id,
                symbol=instrument.symbol,
                entry_order_id=order_id,
                entry_client_order_id=entry_cloid_text,
                stop_client_order_id=stop_cloid_text,
                target_client_order_id=target_cloid_text,
                filled_quantity=filled_quantity,
                average_price=average_price,
                stop_price=stop_price,
                target_price=target_price,
                protection_verified=True,
            )
        except Exception:
            self._emergency_close(instrument.coin)
            raise

    def close_and_cancel(
        self, *, symbol: str, stop_client_order_id: str, target_client_order_id: str
    ) -> None:
        """Close a staged canary and remove its known protection orders."""
        instrument = self._instrument(symbol)
        snapshot = self._snapshot()
        matching = [position for position in snapshot.positions if position.symbol == symbol]
        if len(matching) > 1 or len(snapshot.positions) != len(matching):
            raise HyperliquidTestnetBlocked("refusing cleanup with unrelated testnet positions")
        if matching:
            self._emergency_close(instrument.coin)
        cancel_requests = [
            {
                "coin": instrument.coin,
                "cloid": self.cloid_factory(stop_client_order_id),
            },
            {
                "coin": instrument.coin,
                "cloid": self.cloid_factory(target_client_order_id),
            },
        ]
        with self._write_slot():
            self.exchange.bulk_cancel_by_cloid(cancel_requests)
        final = self._snapshot()
        if final.positions or final.open_orders:
            raise HyperliquidTestnetBlocked("testnet canary cleanup did not leave the account flat")
