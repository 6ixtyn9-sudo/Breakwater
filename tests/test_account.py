from decimal import Decimal

import pytest

from breakwater.account import (
    AccountStateError,
    EquityValuator,
    unprotected_positions,
    validate_api_key_permissions,
)
from breakwater.models import PairSpec, PairType, Position, Side


class Client:
    def market_summary(self, pair):
        from datetime import datetime, timezone

        from breakwater.models import MarketSummary

        return MarketSummary(
            pair, Decimal("16"), Decimal("16.1"), Decimal("16"),
            Decimal("16"), Decimal("100000"), datetime.now(timezone.utc),
        )


def spec():
    return PairSpec(
        "ETHUSDTPERP", "ETH", "USDT", True,
        Decimal("0.001"), Decimal("10"), Decimal("1"), Decimal("10000"),
        Decimal("0.1"), 3, PairType.FUTURE,
    )


def position(side=Side.BUY):
    return Position(
        "ETHUSDTPERP", side, Decimal("0.01"), Decimal("1000"),
        Decimal("1"), "position-one",
    )


def test_equity_uses_fixed_point_conversion_and_unrealized_pnl():
    usdt_zar = PairSpec(
        "USDTZAR", "USDT", "ZAR", True,
        Decimal("1"), Decimal("100000"), Decimal("10"), Decimal("1000000"),
        Decimal("0.0001"), 4, PairType.SPOT,
    )
    valuator = EquityValuator(
        Client(), {"ETHUSDTPERP": spec(), "USDTZAR": usdt_zar}
    )
    equity = valuator.equity_zar(
        [
            {"currency": "ZAR", "total": "100"},
            {"currency": "USDT", "total": "10"},
        ],
        [position()],
    )
    assert equity == Decimal("276")


def test_long_position_requires_sell_stop():
    pos = position(Side.BUY)
    conditionals = [{
        "pair": "ETHUSDTPERP", "side": "SELL", "type": "STOP_LOSS",
        "status": "ACTIVE",
    }]
    assert unprotected_positions([pos], [], conditionals) == []


def test_wrong_side_stop_does_not_protect():
    pos = position(Side.BUY)
    conditionals = [{
        "pair": "ETHUSDTPERP", "side": "BUY", "type": "STOP_LOSS",
        "status": "ACTIVE",
    }]
    assert unprotected_positions([pos], [], conditionals) == [pos]


def test_cancelled_stop_does_not_protect():
    pos = position(Side.SELL)
    conditionals = [{
        "pair": "ETHUSDTPERP", "side": "BUY", "type": "STOP_LOSS",
        "status": "CANCELLED",
    }]
    assert unprotected_positions([pos], [], conditionals) == [pos]


def test_live_key_requires_exact_view_and_trade_scope():
    assert validate_api_key_permissions(
        {"permissions": ["View access", "Trade"]}, live=True
    ) == {"view access", "trade"}


@pytest.mark.parametrize("permission", ["Withdraw", "Internal Transfer", "Link bank account"])
def test_dangerous_api_key_permission_is_rejected(permission):
    with pytest.raises(AccountStateError, match="forbidden"):
        validate_api_key_permissions(
            {"permissions": ["View access", permission]}, live=False
        )
