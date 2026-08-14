"""Immutable account-loss boundaries and order planning."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from breakwater.config import (
    ABSOLUTE_EQUITY_FLOOR_ZAR,
    DAILY_LOSS_LIMIT_ZAR,
    INITIAL_EQUITY_ZAR,
    MAX_AGGREGATE_OPEN_RISK_ZAR,
    MAX_EFFECTIVE_LEVERAGE,
    MAX_POSITION_NOTIONAL_ZAR,
    MAX_POSITIONS,
    MAX_TOTAL_DRAWDOWN_FRACTION,
    MAX_TOTAL_LOSS_ZAR,
    RISK_PER_TRADE_ZAR,
    SEVEN_DAY_LOSS_LIMIT_ZAR,
)
from breakwater.decimal_utils import ceil_to_step, floor_to_step
from breakwater.models import MarketSummary, OrderPlan, PairSpec, PairType, Side, Signal


@dataclass(frozen=True)
class RiskPolicy:
    initial_equity_zar: Decimal = INITIAL_EQUITY_ZAR
    absolute_equity_floor_zar: Decimal = ABSOLUTE_EQUITY_FLOOR_ZAR
    max_total_loss_zar: Decimal = MAX_TOTAL_LOSS_ZAR
    max_drawdown_fraction: Decimal = MAX_TOTAL_DRAWDOWN_FRACTION
    risk_per_trade_zar: Decimal = RISK_PER_TRADE_ZAR
    daily_loss_limit_zar: Decimal = DAILY_LOSS_LIMIT_ZAR
    seven_day_loss_limit_zar: Decimal = SEVEN_DAY_LOSS_LIMIT_ZAR
    max_aggregate_open_risk_zar: Decimal = MAX_AGGREGATE_OPEN_RISK_ZAR
    max_position_notional_zar: Decimal = MAX_POSITION_NOTIONAL_ZAR
    max_effective_leverage: Decimal = MAX_EFFECTIVE_LEVERAGE
    max_positions: int = MAX_POSITIONS


@dataclass(frozen=True)
class RiskState:
    allowed: bool
    reasons: tuple[str, ...]
    equity_zar: Decimal
    high_water_zar: Decimal


class RiskManager:
    def __init__(self, policy: RiskPolicy | None = None):
        self.policy = policy or RiskPolicy()

    def check_account(
        self,
        *,
        equity_zar: Decimal,
        high_water_zar: Decimal,
        daily_pnl_zar: Decimal,
        seven_day_pnl_zar: Decimal,
        open_positions: int,
        aggregate_open_risk_zar: Decimal,
    ) -> RiskState:
        p = self.policy
        reasons = []
        if equity_zar <= p.absolute_equity_floor_zar:
            reasons.append("absolute equity floor reached")
        if p.initial_equity_zar - equity_zar >= p.max_total_loss_zar:
            reasons.append("maximum lifetime loss reached")
        if high_water_zar > 0:
            drawdown = (high_water_zar - equity_zar) / high_water_zar
            if drawdown >= p.max_drawdown_fraction:
                reasons.append("high-water drawdown limit reached")
        if daily_pnl_zar <= -p.daily_loss_limit_zar:
            reasons.append("daily loss limit reached")
        if seven_day_pnl_zar <= -p.seven_day_loss_limit_zar:
            reasons.append("seven-day loss limit reached")
        if open_positions >= p.max_positions:
            reasons.append("maximum position count reached")
        if aggregate_open_risk_zar > p.max_aggregate_open_risk_zar:
            reasons.append("aggregate open risk exceeds limit")
        return RiskState(
            allowed=not reasons,
            reasons=tuple(reasons),
            equity_zar=equity_zar,
            high_water_zar=high_water_zar,
        )

    def plan_order(
        self,
        signal: Signal,
        spec: PairSpec,
        summary: MarketSummary,
        *,
        quote_to_zar: Decimal,
        equity_zar: Decimal,
    ) -> OrderPlan:
        p = self.policy
        if spec.symbol != signal.pair or summary.pair != signal.pair:
            raise ValueError("signal, metadata and summary pairs must match")
        if signal.risk_per_unit <= 0 or quote_to_zar <= 0 or equity_zar <= 0:
            raise ValueError("risk, conversion and equity must be positive")
        if spec.pair_type is PairType.SPOT and signal.side is Side.SELL:
            raise ValueError("spot short entries are prohibited")
        executable_price = summary.ask if signal.side is Side.BUY else summary.bid
        slippage = abs(executable_price - signal.entry_price) / signal.entry_price
        if slippage > Decimal("0.01"):
            raise ValueError("market moved more than one percent beyond the signal")

        risk_per_base_zar = signal.risk_per_unit * quote_to_zar
        risk_quantity = p.risk_per_trade_zar / risk_per_base_zar
        notional_cap_zar = min(p.max_position_notional_zar, equity_zar * p.max_effective_leverage)
        notional_quantity = notional_cap_zar / (signal.entry_price * quote_to_zar)
        quantity = floor_to_step(min(risk_quantity, notional_quantity), spec.quantity_step)
        quantity = min(quantity, spec.max_base)
        if quantity < spec.min_base:
            raise ValueError("pair minimum quantity exceeds the risk-sized order")

        notional_quote = quantity * signal.entry_price
        if notional_quote < spec.min_quote:
            quantity = ceil_to_step(spec.min_quote / signal.entry_price, spec.quantity_step)
            notional_quote = quantity * signal.entry_price
        if quantity < spec.min_base or quantity > spec.max_base:
            raise ValueError("quantity is outside VALR pair limits")
        if notional_quote < spec.min_quote or notional_quote > spec.max_quote:
            raise ValueError("notional is outside VALR pair limits")

        notional_zar = notional_quote * quote_to_zar
        risk_zar = quantity * signal.risk_per_unit * quote_to_zar
        if notional_zar > notional_cap_zar:
            raise ValueError("minimum valid order exceeds notional cap")
        if risk_zar > p.risk_per_trade_zar:
            raise ValueError("minimum valid order exceeds per-trade risk")

        if signal.side is Side.BUY:
            stop_limit = floor_to_step(signal.stop_price * Decimal("0.98"), spec.tick_size)
        else:
            stop_limit = ceil_to_step(signal.stop_price * Decimal("1.02"), spec.tick_size)
        if stop_limit <= 0:
            raise ValueError("stop-limit price is invalid")

        customer_order_id = f"bw-{signal.signal_id}"[:50]
        return OrderPlan(
            signal_id=signal.signal_id,
            pair=signal.pair,
            pair_type=signal.pair_type,
            side=signal.side,
            quantity=quantity,
            entry_price=signal.entry_price,
            stop_price=signal.stop_price,
            stop_limit_price=stop_limit,
            notional_quote=notional_quote,
            notional_zar=notional_zar,
            risk_zar=risk_zar,
            customer_order_id=customer_order_id,
        )
