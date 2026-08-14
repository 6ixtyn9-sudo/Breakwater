from datetime import datetime, timezone
from decimal import Decimal

import pytest

from breakwater.models import (
    MarketSummary,
    PairSpec,
    PairType,
    Side,
    Signal,
)
from breakwater.risk import RiskManager


def market(pair="ETHUSDTPERP"):
    return MarketSummary(
        pair=pair,
        bid=Decimal("99.9"),
        ask=Decimal("100.1"),
        last=Decimal("100"),
        mark=Decimal("100"),
        quote_volume=Decimal("100000"),
        timestamp=datetime.now(timezone.utc),
    )


def spec(pair_type=PairType.FUTURE, min_base="0.001", min_quote="1"):
    return PairSpec(
        symbol="ETHUSDTPERP" if pair_type is PairType.FUTURE else "ETHZAR",
        base_currency="ETH",
        quote_currency="USDT" if pair_type is PairType.FUTURE else "ZAR",
        active=True,
        min_base=Decimal(min_base),
        max_base=Decimal("100"),
        min_quote=Decimal(min_quote),
        max_quote=Decimal("100000"),
        tick_size=Decimal("0.1"),
        base_decimal_places=3,
        pair_type=pair_type,
    )


def signal(pair="ETHUSDTPERP", pair_type=PairType.FUTURE, side=Side.BUY):
    now = datetime.now(timezone.utc)
    return Signal(
        signal_id="abc123",
        pair=pair,
        pair_type=pair_type,
        side=side,
        observed_at=now,
        candle_start=now,
        entry_price=Decimal("100"),
        stop_price=Decimal("95") if side is Side.BUY else Decimal("105"),
        atr=Decimal("2.5"),
        score=Decimal("3"),
    )


def test_absolute_equity_floor_halts():
    state = RiskManager().check_account(
        equity_zar=Decimal("222.07"),
        high_water_zar=Decimal("331.45"),
        daily_pnl_zar=Decimal(0),
        seven_day_pnl_zar=Decimal(0),
        open_positions=0,
        aggregate_open_risk_zar=Decimal(0),
    )
    assert not state.allowed
    assert "absolute equity floor reached" in state.reasons


def test_high_water_drawdown_halts_after_growth():
    state = RiskManager().check_account(
        equity_zar=Decimal("268"),
        high_water_zar=Decimal("400"),
        daily_pnl_zar=Decimal(0),
        seven_day_pnl_zar=Decimal(0),
        open_positions=0,
        aggregate_open_risk_zar=Decimal(0),
    )
    assert not state.allowed
    assert "high-water drawdown limit reached" in state.reasons


def test_daily_and_position_limits_halt():
    state = RiskManager().check_account(
        equity_zar=Decimal("300"),
        high_water_zar=Decimal("331.45"),
        daily_pnl_zar=Decimal("-9.94"),
        seven_day_pnl_zar=Decimal("-5"),
        open_positions=1,
        aggregate_open_risk_zar=Decimal(0),
    )
    assert not state.allowed
    assert "daily loss limit reached" in state.reasons
    assert "maximum position count reached" in state.reasons


def test_order_plan_is_bounded_by_risk_and_notional():
    plan = RiskManager().plan_order(
        signal(), spec(), market(), quote_to_zar=Decimal("16"), equity_zar=Decimal("331.45")
    )
    assert plan.risk_zar <= Decimal("3.31")
    assert plan.notional_zar <= Decimal("99.43")
    assert plan.quantity >= Decimal("0.001")


def test_minimum_order_that_breaks_risk_is_rejected():
    with pytest.raises(ValueError, match="exceeds"):
        RiskManager().plan_order(
            signal(),
            spec(min_base="1", min_quote="100"),
            market(),
            quote_to_zar=Decimal("16"),
            equity_zar=Decimal("331.45"),
        )


def test_spot_short_is_rejected():
    spot_signal = signal(pair="ETHZAR", pair_type=PairType.SPOT, side=Side.SELL)
    spot_market = market("ETHZAR")
    with pytest.raises(ValueError, match="spot short"):
        RiskManager().plan_order(
            spot_signal, spec(PairType.SPOT), spot_market,
            quote_to_zar=Decimal(1), equity_zar=Decimal("331.45"),
        )


def test_chased_signal_is_rejected():
    moved = MarketSummary(
        **{**market().__dict__, "ask": Decimal("102"), "bid": Decimal("101.9")}
    )
    with pytest.raises(ValueError, match="moved"):
        RiskManager().plan_order(
            signal(), spec(), moved,
            quote_to_zar=Decimal("16"), equity_zar=Decimal("331.45"),
        )
