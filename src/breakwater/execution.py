"""Synchronous guarded execution; perpetual writes remain locked pending TPSL proof.

Spot margin note:
VALR offers Spot Margin Trading which can enable long/short exposure by borrowing
real balances. Breakwater can execute spot-margin shorts, but it is disabled by
default and requires explicit operator acknowledgement via environment gates.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from decimal import Decimal

from breakwater.decimal_utils import plain
from breakwater.models import OrderPlan, PairType, Side
from breakwater.valr import ValrClient, ValrError


class ExecutionError(RuntimeError):
    pass


class PerpetualActivationBlocked(ExecutionError):
    pass


class SpotMarginActivationBlocked(ExecutionError):
    pass


def _env_bool(name: str, default: str = "0") -> bool:
    value = str(os.getenv(name, default)).strip().lower()
    return value in {"1", "true", "yes", "y", "on"}


def _spot_margin_ack_ok() -> bool:
    return os.getenv("BREAKWATER_SPOT_MARGIN_ACK", "off") == "I_ACCEPT_BREAKWATER_SPOT_MARGIN_RISK"


def _spot_margin_shorts_enabled() -> bool:
    # Two-key turn style: feature flag + explicit risk acknowledgement
    return _env_bool("BREAKWATER_ENABLE_SPOT_MARGIN_SHORTS", "0") and _spot_margin_ack_ok()


@dataclass(frozen=True)
class ExecutionReceipt:
    entry_order_id: str
    protection_order_id: str
    filled_quantity: Decimal
    average_price: Decimal


class TradeExecutor:
    def __init__(self, client: ValrClient):
        self.client = client

    def _completed(self, order_id: str, timeout_seconds: int = 20) -> dict:
        deadline = time.monotonic() + timeout_seconds
        last_error = None
        while time.monotonic() < deadline:
            try:
                state = self.client.completed_order(order_id)
            except ValrError as exc:
                last_error = exc
                time.sleep(0.5)
                continue
            status = str(state.get("orderStatusType", "")).lower()
            if status in {"filled", "cancelled", "canceled", "failed", "partially filled"}:
                return state
            time.sleep(0.5)
        raise ExecutionError(f"entry order did not become terminal: {last_error}")

    def execute(self, plan: OrderPlan) -> ExecutionReceipt:
        if plan.pair_type is PairType.FUTURE:
            raise PerpetualActivationBlocked(
                "perpetual live entry is locked until VALR conditionalOrderData "
                "has passed an authenticated canary and reduce-only TPSL verification"
            )

        # Spot execution
        if plan.side is Side.BUY:
            return self._execute_spot_long(plan)

        # Spot short => margin short (hard-gated)
        if plan.side is Side.SELL:
            return self._execute_spot_margin_short(plan)

        raise ExecutionError(f"unsupported side: {plan.side}")

    def _execute_spot_long(self, plan: OrderPlan) -> ExecutionReceipt:
        order_types = self.client.order_types(plan.pair)
        if "LIMIT" not in order_types or "STOP_LOSS_LIMIT" not in order_types:
            raise ExecutionError("pair lacks required limit and stop-loss support")

        entry = self.client.place_limit(
            {
                "side": "BUY",
                "quantity": plain(plan.quantity),
                "price": plain(plan.entry_price),
                "pair": plan.pair,
                "postOnly": False,
                "timeInForce": "FOK",
                "customerOrderId": plan.customer_order_id,
            }
        )
        order_id = str(entry.get("id", ""))
        if not order_id:
            raise ExecutionError("VALR entry response did not include an order id")

        state = self._completed(order_id)
        status = str(state.get("orderStatusType", "")).lower()
        filled = Decimal(str(state.get("totalExecutedQuantity") or 0))
        average = Decimal(str(state.get("averagePrice") or 0))
        if status != "filled" or filled <= 0 or average <= 0:
            raise ExecutionError(f"spot entry did not fill completely: {status}")

        protection = self.client.place_spot_stop_limit(
            {
                "side": "SELL",
                "quantity": plain(filled),
                "price": plain(plan.stop_limit_price),
                "stopPrice": plain(plan.stop_price),
                "pair": plan.pair,
                "type": "STOP_LOSS_LIMIT",
                "timeInForce": "GTC",
                "customerOrderId": f"{plan.customer_order_id}-stop"[:50],
            }
        )
        protection_id = str(protection.get("id", ""))
        if not protection_id:
            self._emergency_close_long(plan.pair, filled)
            raise ExecutionError("protection response did not include an order id")

        try:
            active = self.client.active_order(plan.pair, protection_id)
        except Exception as exc:
            self._emergency_close_long(plan.pair, filled)
            raise ExecutionError("could not confirm protection order") from exc

        active_status = str(active.get("orderStatusType", "")).lower()
        if active_status not in {"active", "placed"}:
            self._emergency_close_long(plan.pair, filled)
            raise ExecutionError(f"protection order is not active: {active_status}")

        return ExecutionReceipt(order_id, protection_id, filled, average)

    def _execute_spot_margin_short(self, plan: OrderPlan) -> ExecutionReceipt:
        if not _spot_margin_shorts_enabled():
            raise SpotMarginActivationBlocked(
                "spot margin shorts are disabled; set BREAKWATER_ENABLE_SPOT_MARGIN_SHORTS=1 "
                "and BREAKWATER_SPOT_MARGIN_ACK=I_ACCEPT_BREAKWATER_SPOT_MARGIN_RISK"
            )

        # Canary: margin endpoints must be accessible (indicates margin is enabled for the account/subaccount).
        # We do not assume a response schema; success is "request works and returns a dict".
        try:
            status = self.client.margin_status()
            if not isinstance(status, dict):
                raise SpotMarginActivationBlocked("VALR margin status response is malformed")
            lev = self.client.leverage(plan.pair)
            if not isinstance(lev, dict):
                raise SpotMarginActivationBlocked("VALR leverage response is malformed")
        except Exception as exc:
            raise SpotMarginActivationBlocked("VALR margin endpoints are not accessible") from exc

        order_types = self.client.order_types(plan.pair)
        if "LIMIT" not in order_types or "STOP_LOSS_LIMIT" not in order_types:
            raise ExecutionError("pair lacks required limit and stop-loss support")

        # Margin short entry: SELL base. If balance is insufficient, VALR margin engine borrows automatically.
        entry = self.client.place_limit(
            {
                "side": "SELL",
                "quantity": plain(plan.quantity),
                "price": plain(plan.entry_price),
                "pair": plan.pair,
                "postOnly": False,
                "timeInForce": "FOK",
                "customerOrderId": plan.customer_order_id,
            }
        )
        order_id = str(entry.get("id", ""))
        if not order_id:
            raise ExecutionError("VALR entry response did not include an order id")

        state = self._completed(order_id)
        status = str(state.get("orderStatusType", "")).lower()
        filled = Decimal(str(state.get("totalExecutedQuantity") or 0))
        average = Decimal(str(state.get("averagePrice") or 0))
        if status != "filled" or filled <= 0 or average <= 0:
            raise ExecutionError(f"spot short entry did not fill completely: {status}")

        # Protection for short: BUY stop-loss limit (trigger above, buy back).
        protection = self.client.place_spot_stop_limit(
            {
                "side": "BUY",
                "quantity": plain(filled),
                "price": plain(plan.stop_limit_price),
                "stopPrice": plain(plan.stop_price),
                "pair": plan.pair,
                "type": "STOP_LOSS_LIMIT",
                "timeInForce": "GTC",
                "customerOrderId": f"{plan.customer_order_id}-stop"[:50],
            }
        )
        protection_id = str(protection.get("id", ""))
        if not protection_id:
            self._emergency_close_short(plan.pair, filled, plan.stop_limit_price)
            raise ExecutionError("protection response did not include an order id")

        try:
            active = self.client.active_order(plan.pair, protection_id)
        except Exception as exc:
            self._emergency_close_short(plan.pair, filled, plan.stop_limit_price)
            raise ExecutionError("could not confirm protection order") from exc

        active_status = str(active.get("orderStatusType", "")).lower()
        if active_status not in {"active", "placed"}:
            self._emergency_close_short(plan.pair, filled, plan.stop_limit_price)
            raise ExecutionError(f"protection order is not active: {active_status}")

        return ExecutionReceipt(order_id, protection_id, filled, average)

    def _emergency_close_long(self, pair: str, quantity: Decimal) -> None:
        """Emergency close of a long (SELL base)."""
        try:
            response = self.client.place_market(
                {
                    "side": "SELL",
                    "baseAmount": plain(quantity),
                    "pair": pair,
                }
            )
            order_id = str(response.get("id", ""))
            if not order_id:
                raise ExecutionError("emergency close returned no order id")
            state = self._completed(order_id)
            if str(state.get("orderStatusType", "")).lower() != "filled":
                raise ExecutionError("emergency close was not filled")
        except Exception as exc:
            raise ExecutionError("protection failed and emergency close could not be confirmed") from exc

    def _emergency_close_short(self, pair: str, quantity: Decimal, price_hint: Decimal) -> None:
        """Emergency close of a short (BUY back base).

        VALR market BUY orders commonly use quoteAmount; we therefore estimate a quote amount
        using the stop-limit price and a buffer.
        """
        try:
            # Buffer to reduce risk of insufficient quote amount on a fast spike.
            quote_amount = (quantity * price_hint) * Decimal("1.05")
            response = self.client.place_market(
                {
                    "side": "BUY",
                    "quoteAmount": plain(quote_amount),
                    "pair": pair,
                }
            )
            order_id = str(response.get("id", ""))
            if not order_id:
                raise ExecutionError("emergency close returned no order id")
            state = self._completed(order_id)
            if str(state.get("orderStatusType", "")).lower() != "filled":
                raise ExecutionError("emergency close was not filled")
        except Exception as exc:
            raise ExecutionError("protection failed and emergency close could not be confirmed") from exc
