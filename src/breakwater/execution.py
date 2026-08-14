"""Synchronous guarded execution; perpetual writes remain locked pending TPSL proof."""

from __future__ import annotations

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
        if plan.side is not Side.BUY:
            raise ExecutionError("spot execution only supports long entries")
        order_types = self.client.order_types(plan.pair)
        if "LIMIT" not in order_types or "STOP_LOSS_LIMIT" not in order_types:
            raise ExecutionError("pair lacks required limit and stop-loss support")
        entry = self.client.place_limit({
            "side": "BUY",
            "quantity": plain(plan.quantity),
            "price": plain(plan.entry_price),
            "pair": plan.pair,
            "postOnly": False,
            "timeInForce": "FOK",
            "customerOrderId": plan.customer_order_id,
        })
        order_id = str(entry.get("id", ""))
        if not order_id:
            raise ExecutionError("VALR entry response did not include an order id")
        state = self._completed(order_id)
        status = str(state.get("orderStatusType", "")).lower()
        filled = Decimal(str(state.get("totalExecutedQuantity") or 0))
        average = Decimal(str(state.get("averagePrice") or 0))
        if status != "filled" or filled <= 0 or average <= 0:
            raise ExecutionError(f"spot entry did not fill completely: {status}")
        protection = self.client.place_spot_stop_limit({
            "side": "SELL",
            "quantity": plain(filled),
            "price": plain(plan.stop_limit_price),
            "stopPrice": plain(plan.stop_price),
            "pair": plan.pair,
            "type": "STOP_LOSS_LIMIT",
            "timeInForce": "GTC",
            "customerOrderId": f"{plan.customer_order_id}-stop"[:50],
        })
        protection_id = str(protection.get("id", ""))
        if not protection_id:
            self._emergency_close(plan.pair, filled)
            raise ExecutionError("protection response did not include an order id")
        try:
            active = self.client.active_order(plan.pair, protection_id)
        except Exception as exc:
            self._emergency_close(plan.pair, filled)
            raise ExecutionError("could not confirm protection order") from exc
        active_status = str(active.get("orderStatusType", "")).lower()
        if active_status not in {"active", "placed"}:
            self._emergency_close(plan.pair, filled)
            raise ExecutionError(f"protection order is not active: {active_status}")
        return ExecutionReceipt(order_id, protection_id, filled, average)

    def _emergency_close(self, pair: str, quantity: Decimal) -> None:
        try:
            response = self.client.place_market({
                "side": "SELL",
                "baseAmount": plain(quantity),
                "pair": pair,
            })
            order_id = str(response.get("id", ""))
            if not order_id:
                raise ExecutionError("emergency close returned no order id")
            state = self._completed(order_id)
            if str(state.get("orderStatusType", "")).lower() != "filled":
                raise ExecutionError("emergency close was not filled")
        except Exception as exc:
            raise ExecutionError(
                "protection failed and emergency close could not be confirmed"
            ) from exc
