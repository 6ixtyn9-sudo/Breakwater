from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from breakwater.market import (
    MarketStateError,
    authoritative_server_time,
    completed_candles,
    require_tradeable_market,
)
from breakwater.models import Candle, MarketSummary, PairSpec, PairType


def candle(start, period=3600):
    return Candle(
        pair="ETHUSDTPERP",
        period_seconds=period,
        start=start,
        open=Decimal("100"),
        high=Decimal("101"),
        low=Decimal("99"),
        close=Decimal("100"),
        volume=Decimal("10"),
    )


def test_server_time_accepts_epoch_seconds():
    value = authoritative_server_time({"epochTime": 1786697596})
    assert value == datetime.fromtimestamp(1786697596, tz=timezone.utc)


def test_server_time_accepts_epoch_milliseconds():
    value = authoritative_server_time({"epochTime": 1786697596000})
    assert value == datetime.fromtimestamp(1786697596, tz=timezone.utc)


def test_incomplete_candle_is_removed():
    now = datetime(2026, 8, 14, 10, 30, tzinfo=timezone.utc)
    rows = [
        candle(now - timedelta(hours=2)),
        candle(now - timedelta(minutes=30)),
    ]
    assert completed_candles(rows, now) == [rows[0]]


def test_market_requires_fresh_summary():
    spec = PairSpec(
        "ETHUSDTPERP", "ETH", "USDT", True,
        Decimal("0.001"), Decimal("10"), Decimal("1"), Decimal("10000"),
        Decimal("0.1"), 3, PairType.FUTURE,
    )
    now = datetime.now(timezone.utc)
    summary = MarketSummary(
        "ETHUSDTPERP", Decimal("100"), Decimal("100.1"), Decimal("100"),
        Decimal("100"), Decimal("100000"), now - timedelta(minutes=5),
    )
    with pytest.raises(MarketStateError, match="stale"):
        require_tradeable_market(spec, summary, now)


def test_market_rejects_wide_spread():
    spec = PairSpec(
        "ETHUSDTPERP", "ETH", "USDT", True,
        Decimal("0.001"), Decimal("10"), Decimal("1"), Decimal("10000"),
        Decimal("0.1"), 3, PairType.FUTURE,
    )
    now = datetime.now(timezone.utc)
    summary = MarketSummary(
        "ETHUSDTPERP", Decimal("90"), Decimal("110"), Decimal("100"),
        Decimal("100"), Decimal("100000"), now,
    )
    with pytest.raises(MarketStateError, match="spread"):
        require_tradeable_market(spec, summary, now)
