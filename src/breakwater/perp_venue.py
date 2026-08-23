"""Venue-neutral perpetual market and account contracts.

Venue adapters normalize data into these models. Strategy and risk code must
not depend on venue response schemas, asset IDs, signing rules, or precision
rules. Write methods belong to a separate executor so a read-only client can
never become live because of a configuration typo.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from breakwater.models import Candle, Side


class PerpVenueError(RuntimeError):
    """A venue response or transport could not be safely interpreted."""


class PerpWriteBlocked(PerpVenueError):
    """A write was attempted through a read-only venue boundary."""


@dataclass(frozen=True)
class PerpInstrument:
    venue: str
    symbol: str
    coin: str
    asset_id: int
    size_decimals: int
    max_price_decimals: int
    max_significant_figures: int
    max_leverage: Decimal
    min_notional: Decimal
    mark_price: Decimal
    oracle_price: Decimal
    funding_rate: Decimal
    open_interest: Decimal
    day_notional_volume: Decimal
    active: bool = True

    @property
    def size_step(self) -> Decimal:
        return Decimal(1).scaleb(-self.size_decimals)


@dataclass(frozen=True)
class PerpVenuePosition:
    symbol: str
    coin: str
    side: Side
    quantity: Decimal
    entry_price: Decimal
    mark_price: Decimal
    notional: Decimal
    unrealised_pnl: Decimal
    liquidation_price: Decimal | None
    leverage: Decimal


@dataclass(frozen=True)
class PerpOpenOrder:
    symbol: str
    coin: str
    order_id: str
    client_order_id: str | None
    side: Side
    price: Decimal
    quantity: Decimal
    original_quantity: Decimal
    reduce_only: bool
    is_trigger: bool
    is_position_tpsl: bool
    order_type: str
    trigger_price: Decimal | None
    trigger_condition: str | None
    timestamp_ms: int


@dataclass(frozen=True)
class PerpAccountSnapshot:
    venue: str
    address: str
    account_value: Decimal
    withdrawable: Decimal
    total_margin_used: Decimal
    total_notional_position: Decimal
    positions: tuple[PerpVenuePosition, ...]
    open_orders: tuple[PerpOpenOrder, ...]


@dataclass(frozen=True)
class PerpCoverage:
    tradable: tuple[str, ...]
    unavailable: tuple[str, ...]
    intentionally_excluded: tuple[str, ...]


@dataclass(frozen=True)
class PerpProtectionStatus:
    protected_symbols: tuple[str, ...]
    unprotected_symbols: tuple[str, ...]

    @property
    def all_protected(self) -> bool:
        return not self.unprotected_symbols


def assess_native_stop_protection(snapshot: PerpAccountSnapshot) -> PerpProtectionStatus:
    """Fail closed unless each position has enough native reduce-only stop size."""
    protected: list[str] = []
    unprotected: list[str] = []
    for position in snapshot.positions:
        closing_side = Side.SELL if position.side is Side.BUY else Side.BUY
        stop_size = sum(
            (
                order.quantity
                for order in snapshot.open_orders
                if order.symbol == position.symbol
                and order.side is closing_side
                and order.reduce_only
                and order.is_trigger
                and "stop" in order.order_type.lower()
            ),
            Decimal(0),
        )
        if stop_size >= position.quantity:
            protected.append(position.symbol)
        else:
            unprotected.append(position.symbol)
    return PerpProtectionStatus(
        protected_symbols=tuple(sorted(protected)),
        unprotected_symbols=tuple(sorted(unprotected)),
    )


class ReadOnlyPerpVenue(Protocol):
    name: str

    def instruments(self) -> tuple[PerpInstrument, ...]: ...

    def candles(self, symbol: str, *, interval: str, count: int) -> list[Candle]: ...

    def account_snapshot(self, address: str) -> PerpAccountSnapshot: ...

    def coverage(self, symbols: list[str]) -> PerpCoverage: ...

    def health(self) -> dict: ...
