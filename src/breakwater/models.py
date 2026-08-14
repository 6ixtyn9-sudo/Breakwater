"""Canonical venue-independent models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import StrEnum

from breakwater.decimal_utils import D


class PairType(StrEnum):
    SPOT = "SPOT"
    FUTURE = "FUTURE"


class Side(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class Lifecycle(StrEnum):
    RESEARCH_ONLY = "research_only"
    SHADOW_CANDIDATE = "shadow_candidate"
    SHADOW_VALIDATED = "shadow_validated"
    CANARY_ELIGIBLE = "canary_eligible"
    LIVE_CAPPED = "live_capped"
    SUSPENDED = "suspended"
    RETIRED = "retired"


@dataclass(frozen=True)
class PairSpec:
    symbol: str
    base_currency: str
    quote_currency: str
    active: bool
    min_base: Decimal
    max_base: Decimal
    min_quote: Decimal
    max_quote: Decimal
    tick_size: Decimal
    base_decimal_places: int
    pair_type: PairType

    @classmethod
    def from_payload(cls, row: dict) -> "PairSpec":
        pair_type = PairType(str(row["currencyPairType"]).upper())
        symbol = str(row["symbol"]).upper().strip()
        if not symbol:
            raise ValueError("pair symbol is empty")
        return cls(
            symbol=symbol,
            base_currency=str(row["baseCurrency"]).upper(),
            quote_currency=str(row["quoteCurrency"]).upper(),
            active=row.get("active") is True,
            min_base=D(row["minBaseAmount"], field="minBaseAmount"),
            max_base=D(row["maxBaseAmount"], field="maxBaseAmount"),
            min_quote=D(row["minQuoteAmount"], field="minQuoteAmount"),
            max_quote=D(row["maxQuoteAmount"], field="maxQuoteAmount"),
            tick_size=D(row["tickSize"], field="tickSize"),
            base_decimal_places=int(row["baseDecimalPlaces"]),
            pair_type=pair_type,
        )

    @property
    def quantity_step(self) -> Decimal:
        return Decimal(1).scaleb(-self.base_decimal_places)


@dataclass(frozen=True)
class MarketSummary:
    pair: str
    bid: Decimal
    ask: Decimal
    last: Decimal
    mark: Decimal
    quote_volume: Decimal
    timestamp: datetime

    @classmethod
    def from_payload(cls, row: dict) -> "MarketSummary":
        timestamp = datetime.fromisoformat(str(row["created"]).replace("Z", "+00:00"))
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        return cls(
            pair=str(row["currencyPair"]).upper(),
            bid=D(row["bidPrice"], field="bidPrice"),
            ask=D(row["askPrice"], field="askPrice"),
            last=D(row["lastTradedPrice"], field="lastTradedPrice"),
            mark=D(row.get("markPrice") or row["lastTradedPrice"], field="markPrice"),
            quote_volume=D(row.get("quoteVolume") or 0, field="quoteVolume"),
            timestamp=timestamp.astimezone(timezone.utc),
        )

    @property
    def spread_fraction(self) -> Decimal:
        midpoint = (self.ask + self.bid) / Decimal(2)
        return (self.ask - self.bid) / midpoint if midpoint > 0 else Decimal("Infinity")


@dataclass(frozen=True)
class Candle:
    pair: str
    period_seconds: int
    start: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    @classmethod
    def from_payload(cls, row: dict) -> "Candle":
        start = datetime.fromisoformat(str(row["startTime"]).replace("Z", "+00:00"))
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        return cls(
            pair=str(row["currencyPairSymbol"]).upper(),
            period_seconds=int(row["bucketPeriodInSeconds"]),
            start=start.astimezone(timezone.utc),
            open=D(row["open"], field="open"),
            high=D(row["high"], field="high"),
            low=D(row["low"], field="low"),
            close=D(row["close"], field="close"),
            volume=D(row.get("volume") or 0, field="volume"),
        )

    def complete_at(self) -> datetime:
        from datetime import timedelta

        return self.start + timedelta(seconds=self.period_seconds)


@dataclass(frozen=True)
class PerpSymbol:
    pair: str
    base_asset: str
    max_leverage: Decimal
    min_notional: Decimal
    min_margin: Decimal
    mark_price: Decimal
    price_decimal_places: int

    @classmethod
    def from_payload(cls, row: dict) -> "PerpSymbol":
        pair = str(row.get("currencyPair") or row.get("symbol") or "").upper()
        if not pair:
            raise ValueError("perp symbol row is missing its pair")
        return cls(
            pair=pair,
            base_asset=str(row.get("baseAsset") or pair.replace("USDC", "")).upper(),
            max_leverage=D(row.get("maxLeverage") or 1, field="maxLeverage"),
            min_notional=D(row.get("minNotional") or 0, field="minNotional"),
            min_margin=D(row.get("minMarginAmount") or 0, field="minMarginAmount"),
            mark_price=D(row.get("markPrice") or 0, field="markPrice"),
            price_decimal_places=int(row.get("priceDecimalPlaces") or 6),
        )


@dataclass(frozen=True)
class Position:
    pair: str
    side: Side
    quantity: Decimal
    average_entry_price: Decimal
    unrealised_pnl: Decimal
    position_id: str

    @classmethod
    def from_payload(cls, row: dict) -> "Position":
        quantity = D(row["quantity"], field="quantity")
        if quantity <= 0:
            raise ValueError("position quantity must be positive")
        return cls(
            pair=str(row.get("pair") or row.get("currencyPair")).upper(),
            side=Side(str(row["side"]).upper()),
            quantity=quantity,
            average_entry_price=D(row["averageEntryPrice"], field="averageEntryPrice"),
            unrealised_pnl=D(row.get("unrealisedPnl") or 0, field="unrealisedPnl"),
            position_id=str(row["positionId"]),
        )


@dataclass(frozen=True)
class Signal:
    signal_id: str
    pair: str
    pair_type: PairType
    side: Side
    observed_at: datetime
    candle_start: datetime
    entry_price: Decimal
    stop_price: Decimal
    atr: Decimal
    score: Decimal
    source_candidate_id: str | None = None

    @property
    def risk_per_unit(self) -> Decimal:
        return abs(self.entry_price - self.stop_price)


@dataclass(frozen=True)
class OrderPlan:
    signal_id: str
    pair: str
    pair_type: PairType
    side: Side
    quantity: Decimal
    entry_price: Decimal
    stop_price: Decimal
    stop_limit_price: Decimal
    notional_quote: Decimal
    notional_zar: Decimal
    risk_zar: Decimal
    customer_order_id: str
