"""VALR-native catalog, time and candle completeness checks."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from breakwater.decimal_utils import D
from breakwater.models import Candle, MarketSummary, PairSpec, PairType
from breakwater.valr import ValrClient, ValrError


class MarketStateError(RuntimeError):
    pass


def authoritative_server_time(payload: dict) -> datetime:
    if not isinstance(payload, dict) or "epochTime" not in payload:
        raise MarketStateError("VALR server time response is incomplete")
    epoch = D(payload["epochTime"], field="epochTime")
    if epoch <= 0:
        raise MarketStateError("VALR server time is invalid")
    seconds = epoch / Decimal(1000) if epoch > Decimal("100000000000") else epoch
    return datetime.fromtimestamp(float(seconds), tz=timezone.utc)


def completed_candles(candles: list[Candle], server_time: datetime) -> list[Candle]:
    if server_time.tzinfo is None:
        raise MarketStateError("server time must be timezone-aware")
    complete = [candle for candle in candles if candle.complete_at() <= server_time]
    return sorted(complete, key=lambda candle: candle.start)


class MarketCatalog:
    def __init__(self, client: ValrClient):
        self.client = client
        self._specs: dict[str, PairSpec] = {}

    def refresh(self) -> dict[str, PairSpec]:
        specs = self.client.pairs()
        if not specs:
            raise MarketStateError("VALR returned no pair metadata")
        self._specs = {spec.symbol: spec for spec in specs}
        return dict(self._specs)

    def get(self, pair: str) -> PairSpec:
        if not self._specs:
            self.refresh()
        try:
            return self._specs[pair.upper()]
        except KeyError as exc:
            raise MarketStateError(f"unknown VALR pair {pair}") from exc

    def active(self, pair_type: PairType | None = None) -> list[PairSpec]:
        if not self._specs:
            self.refresh()
        return sorted(
            [
                spec for spec in self._specs.values()
                if spec.active and (pair_type is None or spec.pair_type == pair_type)
            ],
            key=lambda spec: spec.symbol,
        )

    def active_perpetual_symbols(self) -> set[str]:
        info = self.client.futures_info()
        symbols = {str(row.get("currencyPair", "")).upper() for row in info}
        metadata = {spec.symbol for spec in self.active(PairType.FUTURE)}
        if symbols != metadata:
            raise MarketStateError(
                "VALR futures-info and active pair metadata disagree"
            )
        return symbols


def market_is_fresh(
    summary: MarketSummary,
    server_time: datetime,
    *,
    max_age: timedelta = timedelta(minutes=2),
) -> bool:
    age = server_time - summary.timestamp
    return timedelta(0) <= age <= max_age


def require_tradeable_market(
    spec: PairSpec,
    summary: MarketSummary,
    server_time: datetime,
    *,
    max_spread_fraction: Decimal = Decimal("0.01"),
    min_quote_volume: Decimal = Decimal("1000"),
) -> None:
    if not spec.active:
        raise MarketStateError(f"{spec.symbol} is inactive")
    if summary.pair != spec.symbol:
        raise MarketStateError("market summary pair does not match metadata")
    if not market_is_fresh(summary, server_time):
        raise MarketStateError(f"{spec.symbol} market summary is stale")
    if summary.bid <= 0 or summary.ask <= summary.bid:
        raise MarketStateError(f"{spec.symbol} has an invalid order book spread")
    if summary.spread_fraction > max_spread_fraction:
        raise MarketStateError(f"{spec.symbol} spread exceeds configured limit")
    if summary.quote_volume < min_quote_volume:
        raise MarketStateError(f"{spec.symbol} quote volume is too low")


def fetch_recent_candles(
    client: ValrClient,
    pair: str,
    server_time: datetime,
    *,
    period_seconds: int = 3600,
    count: int = 220,
) -> list[Candle]:
    if count < 2 or count > 300:
        raise ValueError("candle count must be between 2 and 300")
    end = int(server_time.timestamp())
    start = end - period_seconds * (count + 2)
    try:
        candles = client.candles(
            pair,
            period_seconds=period_seconds,
            start_epoch=start,
            end_epoch=end,
            limit=count,
        )
    except ValrError as exc:
        raise MarketStateError(f"could not fetch {pair} candles: {exc}") from exc
    complete = completed_candles(candles, server_time)
    if len(complete) < 60:
        raise MarketStateError(f"insufficient completed candles for {pair}")
    return complete[-count:]
