"""Account-loss boundaries, order planning and perp sizing.

Policy values are supplied by the operator through environment variables and
are never compiled into this repository. RiskManager only ever receives a
fully-populated RiskPolicy.

Spot margin note:
- Cash spot shorts are not meaningful (you cannot sell what you do not have).
- VALR Spot Margin can enable short exposure by borrowing.
- Breakwater allows planning spot SELL orders only when explicitly enabled by
  operator environment gates (see `_spot_margin_shorts_enabled()`).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from decimal import Decimal

from breakwater.decimal_utils import ceil_to_step, floor_to_step
from breakwater.models import MarketSummary, OrderPlan, PairSpec, PairType, PerpSymbol, Side, Signal


def _env_bool(name: str, default: str = "0") -> bool:
    value = str(os.getenv(name, default)).strip().lower()
    return value in {"1", "true", "yes", "y", "on"}


def _spot_margin_ack_ok() -> bool:
    return os.getenv("BREAKWATER_SPOT_MARGIN_ACK", "off") == "I_ACCEPT_BREAKWATER_SPOT_MARGIN_RISK"


def _spot_margin_shorts_enabled() -> bool:
    return _env_bool("BREAKWATER_ENABLE_SPOT_MARGIN_SHORTS", "0") and _spot_margin_ack_ok()


@dataclass(frozen=True)
class RiskPolicy:
    initial_equity_zar: Decimal
    absolute_equity_floor_zar: Decimal
    max_total_loss_zar: Decimal
    max_drawdown_fraction: Decimal
    risk_per_trade_zar: Decimal
    daily_loss_limit_zar: Decimal
    seven_day_loss_limit_zar: Decimal
    max_aggregate_open_risk_zar: Decimal
    max_position_notional_zar: Decimal
    max_effective_leverage: Decimal
    perp_leverage_cap: Decimal
    max_positions: int


@dataclass(frozen=True)
class RiskState:
    allowed: bool
    reasons: tuple[str, ...]
    equity_zar: Decimal
    high_water_zar: Decimal


class RiskManager:
    def __init__(self, policy: RiskPolicy):
        self.policy = policy

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

        # Spot short (SELL) is only allowed when spot margin shorts are explicitly enabled.
        if spec.pair_type is PairType.SPOT and signal.side is Side.SELL and not _spot_margin_shorts_enabled():
            raise ValueError("spot short entries require spot margin enablement (BREAKWATER_ENABLE_SPOT_MARGIN_SHORTS + ACK)")

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

    def plan_perp_order(
        self,
        signal: Signal,
        perp: PerpSymbol,
        *,
        quote_to_zar: Decimal,
        equity_zar: Decimal,
    ) -> OrderPlan:
        p = self.policy
        if signal.pair != perp.pair:
            raise ValueError("signal and perp symbol must match")
        if signal.risk_per_unit <= 0 or quote_to_zar <= 0 or equity_zar <= 0:
            raise ValueError("risk, conversion and equity must be positive")
        if perp.min_notional <= 0 or perp.mark_price <= 0:
            raise ValueError("perp symbol metadata is incomplete")

        leverage = min(p.perp_leverage_cap, perp.max_leverage)
        if leverage <= 0:
            raise ValueError("perp pair has no valid leverage")

        risk_notional_usdc = p.risk_per_trade_zar / quote_to_zar
        notional_cap_usdc = min(
            p.max_position_notional_zar / quote_to_zar,
            equity_zar * p.max_effective_leverage / quote_to_zar,
        )
        if notional_cap_usdc < perp.min_notional:
            raise ValueError("perp minimum notional exceeds the configured notional cap")

        notional_usdc = min(risk_notional_usdc, notional_cap_usdc)
        notional_usdc = max(notional_usdc, perp.min_notional)

        margin_usdc = notional_usdc / leverage
        if margin_usdc < perp.min_margin:
            notional_usdc = perp.min_margin * leverage

        if notional_usdc > notional_cap_usdc:
            raise ValueError("minimum perp margin forces notional above the cap")

        stop_fraction = signal.risk_per_unit / signal.entry_price
        risk_zar = notional_usdc * stop_fraction * quote_to_zar
        if risk_zar > p.risk_per_trade_zar:
            raise ValueError("perp minimum order exceeds per-trade risk")

        quantity = notional_usdc / signal.entry_price
        quantity = Decimal(quantity).quantize(Decimal(1).scaleb(-perp.price_decimal_places))
        if quantity <= 0:
            raise ValueError("perp quantity rounds to zero")

        risk_zar = quantity * signal.risk_per_unit * quote_to_zar
        if risk_zar > p.risk_per_trade_zar:
            raise ValueError("perp minimum order exceeds per-trade risk")

        customer_order_id = f"bw-{signal.signal_id}"[:50]
        return OrderPlan(
            signal_id=signal.signal_id,
            pair=signal.pair,
            pair_type=PairType.FUTURE,
            side=signal.side,
            quantity=quantity,
            entry_price=signal.entry_price,
            stop_price=signal.stop_price,
            stop_limit_price=signal.stop_price,
            notional_quote=notional_usdc,
            notional_zar=notional_usdc * quote_to_zar,
            risk_zar=risk_zar,
            customer_order_id=customer_order_id,
        )
