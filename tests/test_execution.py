from decimal import Decimal

import pytest

from breakwater.execution import (
    PerpetualActivationBlocked,
    SpotMarginActivationBlocked,
    TradeExecutor,
)
from breakwater.models import OrderPlan, PairType, Side


def plan(pair_type=PairType.SPOT, side=Side.BUY):
    return OrderPlan(
        signal_id="signal",
        pair="ETHZAR" if pair_type is PairType.SPOT else "ETHUSDTPERP",
        pair_type=pair_type,
        side=side,
        quantity=Decimal("0.01"),
        entry_price=Decimal("100"),
        stop_price=Decimal("90") if side is Side.BUY else Decimal("105"),
        stop_limit_price=Decimal("88") if side is Side.BUY else Decimal("107.1"),
        notional_quote=Decimal("1"),
        notional_zar=Decimal("1"),
        risk_zar=Decimal("0.1"),
        customer_order_id="bw-signal",
    )


class Client:
    def __init__(self):
        self.closed = []

    def order_types(self, pair):
        return {"LIMIT", "MARKET", "STOP_LOSS_LIMIT"}

    def margin_status(self):
        return {"ok": True}

    def leverage(self, pair):
        return {"pair": pair, "maxLeverage": "5"}

    def place_limit(self, body):
        return {"id": "entry"}

    def completed_order(self, order_id):
        return {
            "orderStatusType": "Filled",
            "totalExecutedQuantity": "0.01",
            "averagePrice": "100",
        }

    def place_spot_stop_limit(self, body):
        return {"id": "stop"}

    def active_order(self, pair, order_id):
        return {"orderStatusType": "Active"}

    def place_market(self, body):
        self.closed.append(body)
        return {"id": "close"}


def test_perpetual_live_entry_is_hard_locked():
    with pytest.raises(PerpetualActivationBlocked, match="TPSL"):
        TradeExecutor(Client()).execute(plan(PairType.FUTURE))


def test_spot_entry_requires_confirmed_stop():
    receipt = TradeExecutor(Client()).execute(plan())
    assert receipt.entry_order_id == "entry"
    assert receipt.protection_order_id == "stop"


def test_missing_stop_id_triggers_emergency_close():
    client = Client()
    client.place_spot_stop_limit = lambda body: {}
    with pytest.raises(Exception, match="protection"):
        TradeExecutor(client).execute(plan())
    assert client.closed


def test_spot_margin_short_is_blocked_by_default(monkeypatch):
    monkeypatch.delenv("BREAKWATER_ENABLE_SPOT_MARGIN_SHORTS", raising=False)
    monkeypatch.delenv("BREAKWATER_SPOT_MARGIN_ACK", raising=False)
    with pytest.raises(SpotMarginActivationBlocked):
        TradeExecutor(Client()).execute(plan(PairType.SPOT, side=Side.SELL))


def test_spot_margin_short_executes_when_enabled(monkeypatch):
    monkeypatch.setenv("BREAKWATER_ENABLE_SPOT_MARGIN_SHORTS", "1")
    monkeypatch.setenv("BREAKWATER_SPOT_MARGIN_ACK", "I_ACCEPT_BREAKWATER_SPOT_MARGIN_RISK")

    receipt = TradeExecutor(Client()).execute(plan(PairType.SPOT, side=Side.SELL))
    assert receipt.entry_order_id == "entry"
    assert receipt.protection_order_id == "stop"
