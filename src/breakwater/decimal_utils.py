"""Fixed-point helpers for exchange prices, quantities and balances."""

from __future__ import annotations

from decimal import ROUND_DOWN, ROUND_UP, Decimal, InvalidOperation


class DecimalValueError(ValueError):
    pass


def D(value, *, field: str = "value") -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise DecimalValueError(f"{field} is not a decimal") from exc
    if not number.is_finite():
        raise DecimalValueError(f"{field} must be finite")
    return number


def floor_to_step(value: Decimal, step: Decimal) -> Decimal:
    if step <= 0:
        raise DecimalValueError("step must be positive")
    units = (value / step).to_integral_value(rounding=ROUND_DOWN)
    return units * step


def ceil_to_step(value: Decimal, step: Decimal) -> Decimal:
    if step <= 0:
        raise DecimalValueError("step must be positive")
    units = (value / step).to_integral_value(rounding=ROUND_UP)
    return units * step


def plain(value: Decimal) -> str:
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"
