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


def test_open_stop_risk_is_measured_from_the_live_book():
    """The leash: distance from price to the resting stop, times quantity."""
    from breakwater.account import aggregate_open_stop_risk_zar

    positions = [
        Position(
            pair="BTCUSDC",
            side=Side.BUY,
            quantity=Decimal("0.01"),
            average_entry_price=Decimal("60000"),
            unrealised_pnl=Decimal("0"),
            position_id="p1",
        )
    ]
    rows = [
        {
            "currencyPair": "BTCUSDC",
            "side": "SELL",
            "type": "STOP_LOSS_LIMIT",
            "stopPrice": "57000",
            "status": "ACTIVE",
        }
    ]
    risk, unknown = aggregate_open_stop_risk_zar(
        positions,
        [],
        rows,
        last_price=lambda pair: Decimal("60000"),
        quote_to_zar=lambda currency: Decimal("16.29"),
    )
    # 0.01 x 3000 USDC of stop distance x 16.29 ZAR/USDC
    assert risk == Decimal("488.7000")
    assert unknown == []

    # Without a conversion path the number is not a ZAR number, so it is
    # reported in quote currency rather than silently mislabelled.
    raw, _ = aggregate_open_stop_risk_zar(
        positions, [], rows, last_price=lambda pair: Decimal("60000")
    )
    assert raw == Decimal("30.00")


def test_stop_already_through_the_market_is_locked_gain_not_risk():
    from breakwater.account import aggregate_open_stop_risk_zar

    positions = [
        Position(
            pair="BTCZAR",
            side=Side.BUY,
            quantity=Decimal("0.01"),
            average_entry_price=Decimal("100000"),
            unrealised_pnl=Decimal("0"),
            position_id="p1",
        )
    ]
    rows = [
        {
            "currencyPair": "BTCZAR",
            "side": "SELL",
            "type": "STOP_LOSS_LIMIT",
            "stopPrice": "105000",
            "status": "ACTIVE",
        }
    ]
    risk, unknown = aggregate_open_stop_risk_zar(
        positions, [], rows, last_price=lambda pair: Decimal("100000")
    )
    assert risk == Decimal(0)
    assert unknown == []


def test_unpriceable_stop_is_reported_unknown_not_zero():
    """A leash you cannot measure must not read as 'no risk'."""
    from breakwater.account import aggregate_open_stop_risk_zar

    positions = [
        Position(
            pair="BTCZAR",
            side=Side.BUY,
            quantity=Decimal("0.01"),
            average_entry_price=Decimal("100000"),
            unrealised_pnl=Decimal("0"),
            position_id="p1",
        )
    ]
    risk, unknown = aggregate_open_stop_risk_zar(
        positions, [], [], last_price=lambda pair: Decimal("100000")
    )
    assert risk == Decimal(0)
    assert unknown == ["BTCZAR: stop price unavailable"]


def test_missing_fx_rate_is_reported_unknown():
    from breakwater.account import aggregate_open_stop_risk_zar

    positions = [
        Position(
            pair="BTCUSDC",
            side=Side.BUY,
            quantity=Decimal("0.01"),
            average_entry_price=Decimal("60000"),
            unrealised_pnl=Decimal("0"),
            position_id="p1",
        )
    ]
    rows = [
        {
            "currencyPair": "BTCUSDC",
            "side": "SELL",
            "type": "STOP_LOSS_LIMIT",
            "stopPrice": "57000",
            "status": "ACTIVE",
        }
    ]

    def boom(currency):
        raise AccountStateError("no active VALR conversion path from USDC to ZAR")

    _, unknown = aggregate_open_stop_risk_zar(
        positions, [], rows, last_price=lambda pair: Decimal("60000"), quote_to_zar=boom
    )
    assert unknown == ["BTCUSDC: no conversion path from USDC"]


def test_unknown_aggregate_risk_fails_closed_in_the_policy():
    from breakwater.risk import RiskManager, RiskPolicy

    policy = RiskPolicy(
        initial_equity_zar=Decimal("1000"),
        absolute_equity_floor_zar=Decimal("100"),
        max_total_loss_zar=Decimal("500"),
        max_drawdown_fraction=Decimal("0.5"),
        risk_per_trade_zar=Decimal("10"),
        daily_loss_limit_zar=Decimal("50"),
        seven_day_loss_limit_zar=Decimal("100"),
        max_aggregate_open_risk_zar=Decimal("100"),
        max_position_notional_zar=Decimal("200"),
        max_effective_leverage=Decimal("1"),
        perp_leverage_cap=Decimal("3"),
        max_positions=5,
    )
    state = RiskManager(policy).check_account(
        equity_zar=Decimal("1000"),
        high_water_zar=Decimal("1000"),
        daily_pnl_zar=Decimal(0),
        seven_day_pnl_zar=Decimal(0),
        open_positions=1,
        aggregate_open_risk_zar=Decimal(0),
        aggregate_open_risk_unknown=True,
    )
    assert state.allowed is False
    assert "aggregate open risk is unknown" in state.reasons

    allowed = RiskManager(policy).check_account(
        equity_zar=Decimal("1000"),
        high_water_zar=Decimal("1000"),
        daily_pnl_zar=Decimal(0),
        seven_day_pnl_zar=Decimal(0),
        open_positions=1,
        aggregate_open_risk_zar=Decimal("50"),
    )
    assert allowed.allowed is True
