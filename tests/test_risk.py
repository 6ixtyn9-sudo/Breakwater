
```python
from datetime import datetime, timezone
from decimal import Decimal
import os

import pytest

from breakwater.models import (
    MarketSummary,
    PairSpec,
    PairType,
    PerpSymbol,
    Side,
    Signal,
)
from breakwater.risk import RiskManager, RiskPolicy


def policy(**overrides):
    values = dict(
        initial_equity_zar=Decimal("331.45"),
        absolute_equity_floor_zar=Decimal("222.07"),
        max_total_loss_zar=Decimal("109.38"),
        max_drawdown_fraction=Decimal("0.33"),
        risk_per_trade_zar=Decimal("6.63"),
        daily_loss_limit_zar=Decimal("9.94"),
        seven_day_loss_limit_zar=Decimal("19.89"),
        max_aggregate_open_risk_zar=Decimal("6.63"),
        max_position_notional_zar=Decimal("200.00"),
        max_effective_leverage=Decimal("1"),
        perp_leverage_cap=Decimal("3"),
        max_positions=1,
    )
    values.update(overrides)
    return RiskPolicy(**values)


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


def perp(pair="BTCUSDC"):
    return PerpSymbol(
        pair=pair,
        base_asset="BTC",
        max_leverage=Decimal("10"),
        min_notional=Decimal("11"),
        min_margin=Decimal("2"),
        mark_price=Decimal("1500"),
        price_decimal_places=5,
    )


def test_absolute_equity_floor_halts():
    state = RiskManager(policy()).check_account(
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
    state = RiskManager(policy()).check_account(
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
    state = RiskManager(policy()).check_account(
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
    plan = RiskManager(policy()).plan_order(
        signal(), spec(), market(), quote_to_zar=Decimal("16"), equity_zar=Decimal("331.45")
    )
    assert plan.risk_zar <= Decimal("6.63")
    assert plan.notional_zar <= Decimal("200.00")
    assert plan.quantity >= Decimal("0.001")


def test_minimum_order_that_breaks_risk_is_rejected():
    with pytest.raises(ValueError, match="exceeds"):
        RiskManager(policy()).plan_order(
            signal(),
            spec(min_base="1", min_quote="100"),
            market(),
            quote_to_zar=Decimal("16"),
            equity_zar=Decimal("331.45"),
        )


def test_spot_short_is_rejected_by_default(monkeypatch):
    monkeypatch.delenv("BREAKWATER_ENABLE_SPOT_MARGIN_SHORTS", raising=False)
    monkeypatch.delenv("BREAKWATER_SPOT_MARGIN_ACK", raising=False)

    spot_signal = signal(pair="ETHZAR", pair_type=PairType.SPOT, side=Side.SELL)
    spot_market = market("ETHZAR")
    with pytest.raises(ValueError, match="spot short"):
        RiskManager(policy()).plan_order(
            spot_signal, spec(PairType.SPOT), spot_market,
            quote_to_zar=Decimal(1), equity_zar=Decimal("331.45"),
        )


def test_spot_short_is_allowed_when_margin_gates_enabled(monkeypatch):
    monkeypatch.setenv("BREAKWATER_ENABLE_SPOT_MARGIN_SHORTS", "1")
    monkeypatch.setenv("BREAKWATER_SPOT_MARGIN_ACK", "I_ACCEPT_BREAKWATER_SPOT_MARGIN_RISK")

    spot_signal = signal(pair="ETHZAR", pair_type=PairType.SPOT, side=Side.SELL)
    spot_market = market("ETHZAR")
    plan = RiskManager(policy(max_effective_leverage=Decimal("3"))).plan_order(
        spot_signal, spec(PairType.SPOT), spot_market,
        quote_to_zar=Decimal(1), equity_zar=Decimal("331.45"),
    )
    assert plan.side is Side.SELL
    assert plan.stop_limit_price > plan.stop_price  # short stop limit should be above stop


def test_chased_signal_is_rejected():
    moved = MarketSummary(
        **{**market().__dict__, "ask": Decimal("102"), "bid": Decimal("101.9")}
    )
    with pytest.raises(ValueError, match="moved"):
        RiskManager(policy()).plan_order(
            signal(), spec(), moved,
            quote_to_zar=Decimal("16"), equity_zar=Decimal("331.45"),
        )


def tight_signal(pair="BTCUSDC", side=Side.BUY):
    now = datetime.now(timezone.utc)
    return Signal(
        signal_id="perp1",
        pair=pair,
        pair_type=PairType.FUTURE,
        side=side,
        observed_at=now,
        candle_start=now,
        entry_price=Decimal("100"),
        stop_price=Decimal("98") if side is Side.BUY else Decimal("102"),
        atr=Decimal("1"),
        score=Decimal("3"),
    )


def test_perp_plan_respects_minimum_notional_and_leverage_cap():
    plan = RiskManager(policy()).plan_perp_order(
        tight_signal(pair="BTCUSDC"), perp(),
        quote_to_zar=Decimal("16.29"), equity_zar=Decimal("331.45"),
    )
    assert plan.notional_quote >= Decimal("11")
    assert plan.notional_zar <= Decimal("200.00")
    assert plan.risk_zar <= Decimal("6.63")


def test_perp_plan_short_side_is_allowed():
    plan = RiskManager(policy()).plan_perp_order(
        tight_signal(pair="BTCUSDC", side=Side.SELL), perp(),
        quote_to_zar=Decimal("16.29"), equity_zar=Decimal("331.45"),
    )
    assert plan.side is Side.SELL


def test_perp_minimum_notional_above_cap_is_rejected():
    with pytest.raises(ValueError, match="minimum notional"):
        RiskManager(policy(max_position_notional_zar=Decimal("10"))).plan_perp_order(
            tight_signal(pair="BTCUSDC"), perp(),
            quote_to_zar=Decimal("16.29"), equity_zar=Decimal("331.45"),
        )


def test_perp_minimum_order_with_wide_stop_breaks_risk():
    with pytest.raises(ValueError, match="exceeds per-trade risk"):
        RiskManager(policy()).plan_perp_order(
            signal(pair="BTCUSDC"), perp(),
            quote_to_zar=Decimal("16.29"), equity_zar=Decimal("331.45"),
        )
