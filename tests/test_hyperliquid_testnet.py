from decimal import Decimal

import pytest

from breakwater.hyperliquid_testnet import (
    TESTNET_ACK,
    HyperliquidTestnetBlocked,
    HyperliquidTestnetExecutor,
    ProtectionCanaryPlan,
    deterministic_cloid,
)
from breakwater.models import Side
from breakwater.perp_venue import (
    PerpAccountSnapshot,
    PerpInstrument,
    PerpOpenOrder,
    PerpVenuePosition,
)

ACCOUNT = "0x" + "1" * 40
AGENT = "0x" + "2" * 40


def instrument():
    return PerpInstrument(
        venue="hyperliquid",
        symbol="ETHUSDC",
        coin="ETH",
        asset_id=1,
        size_decimals=3,
        max_price_decimals=3,
        max_significant_figures=5,
        max_leverage=Decimal("25"),
        min_notional=Decimal("10"),
        mark_price=Decimal("2000"),
        oracle_price=Decimal("2000"),
        funding_rate=Decimal(0),
        open_interest=Decimal("1"),
        day_notional_volume=Decimal("1000"),
    )


def position():
    return PerpVenuePosition(
        symbol="ETHUSDC",
        coin="ETH",
        side=Side.BUY,
        quantity=Decimal("0.01"),
        entry_price=Decimal("2000"),
        mark_price=Decimal("2000"),
        notional=Decimal("20"),
        unrealised_pnl=Decimal(0),
        liquidation_price=Decimal("1500"),
        leverage=Decimal("2"),
    )


def stop_order():
    return PerpOpenOrder(
        symbol="ETHUSDC",
        coin="ETH",
        order_id="stop",
        client_order_id="0xstop",
        side=Side.SELL,
        price=Decimal("1980"),
        quantity=Decimal("0.01"),
        original_quantity=Decimal("0.01"),
        reduce_only=True,
        is_trigger=True,
        is_position_tpsl=True,
        order_type="Stop Market",
        trigger_price=Decimal("1980"),
        trigger_condition="Price below 1980",
        timestamp_ms=1,
    )


def snapshot(positions=(), orders=()):
    return PerpAccountSnapshot(
        venue="hyperliquid",
        address=ACCOUNT,
        account_value=Decimal("1000"),
        withdrawable=Decimal("1000"),
        total_margin_used=Decimal(0),
        total_notional_position=Decimal(0),
        positions=tuple(positions),
        open_orders=tuple(orders),
    )


class Venue:
    testnet = True

    def __init__(self, snapshots):
        self.snapshots = list(snapshots)

    def instruments(self):
        return (instrument(),)

    def account_snapshot(self, address):
        assert address == ACCOUNT
        return self.snapshots.pop(0)


class Exchange:
    def __init__(self, protection_error=False):
        self.calls = []
        self.protection_error = protection_error

    def market_open(self, *args, **kwargs):
        self.calls.append(("open", args, kwargs))
        return {
            "status": "ok",
            "response": {
                "data": {
                    "statuses": [
                        {"filled": {"oid": 7, "totalSz": "0.01", "avgPx": "2000"}}
                    ]
                }
            },
        }

    def bulk_orders(self, requests, grouping):
        self.calls.append(("protect", requests, grouping))
        statuses = (
            [{"error": "bad stop"}]
            if self.protection_error
            else [{"resting": {"oid": 8}}, {"resting": {"oid": 9}}]
        )
        return {"status": "ok", "response": {"data": {"statuses": statuses}}}

    def market_close(self, coin):
        self.calls.append(("close", coin))
        return {
            "status": "ok",
            "response": {
                "data": {
                    "statuses": [
                        {"filled": {"oid": 10, "totalSz": "0.01", "avgPx": "1999"}}
                    ]
                }
            },
        }

    def bulk_cancel_by_cloid(self, requests):
        self.calls.append(("cancel", requests))
        return {"status": "ok"}


def executor(venue, exchange=None):
    return HyperliquidTestnetExecutor(
        exchange=exchange or Exchange(),
        venue=venue,
        account_address=ACCOUNT,
        agent_address=AGENT,
        cloid_factory=lambda value: value,
        acknowledgement=TESTNET_ACK,
    )


def test_deterministic_cloids_are_stable_and_role_specific():
    assert deterministic_cloid("run-1", "entry") == deterministic_cloid("run-1", "entry")
    assert deterministic_cloid("run-1", "entry") != deterministic_cloid("run-1", "stop")
    assert len(deterministic_cloid("run-1", "entry")) == 34


def test_executor_refuses_master_key_and_missing_ack():
    with pytest.raises(HyperliquidTestnetBlocked, match="acknowledgement"):
        HyperliquidTestnetExecutor(
            exchange=Exchange(),
            venue=Venue([]),
            account_address=ACCOUNT,
            agent_address=AGENT,
            cloid_factory=str,
            acknowledgement="off",
        )
    with pytest.raises(HyperliquidTestnetBlocked, match="master key"):
        HyperliquidTestnetExecutor(
            exchange=Exchange(),
            venue=Venue([]),
            account_address=ACCOUNT,
            agent_address=ACCOUNT,
            cloid_factory=str,
            acknowledgement=TESTNET_ACK,
        )


def test_open_attaches_and_verifies_native_reduce_only_protection():
    venue = Venue(
        [
            snapshot(),
            snapshot([position()]),
            snapshot([position()], [stop_order()]),
        ]
    )
    exchange = Exchange()
    receipt = executor(venue, exchange).open_with_native_protection(
        ProtectionCanaryPlan(
            run_id="mechanism-1",
            symbol="ETHUSDC",
            side=Side.BUY,
            quantity=Decimal("0.01"),
        )
    )
    assert receipt.protection_verified is True
    assert receipt.stop_price == Decimal("1980.0")
    assert receipt.target_price == Decimal("2040.0")
    protection_call = [call for call in exchange.calls if call[0] == "protect"][0]
    assert protection_call[2] == "positionTpsl"
    assert all(request["reduce_only"] for request in protection_call[1])


def test_protection_failure_forces_emergency_close():
    venue = Venue([snapshot(), snapshot([position()])])
    exchange = Exchange(protection_error=True)
    with pytest.raises(HyperliquidTestnetBlocked, match="rejected"):
        executor(venue, exchange).open_with_native_protection(
            ProtectionCanaryPlan(
                run_id="mechanism-2",
                symbol="ETHUSDC",
                side=Side.BUY,
                quantity=Decimal("0.01"),
            )
        )
    assert any(call[0] == "close" for call in exchange.calls)


def test_canary_hard_caps_notional_and_requires_flat_account():
    with pytest.raises(HyperliquidTestnetBlocked, match="25 USDC"):
        executor(Venue([snapshot()])).open_with_native_protection(
            ProtectionCanaryPlan(
                run_id="too-large",
                symbol="ETHUSDC",
                side=Side.BUY,
                quantity=Decimal("0.02"),
            )
        )
    with pytest.raises(HyperliquidTestnetBlocked, match="otherwise flat"):
        executor(Venue([snapshot([position()])])).open_with_native_protection(
            ProtectionCanaryPlan(
                run_id="not-flat",
                symbol="ETHUSDC",
                side=Side.BUY,
                quantity=Decimal("0.01"),
            )
        )
