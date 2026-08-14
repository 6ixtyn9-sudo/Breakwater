from datetime import datetime, timedelta, timezone
from decimal import Decimal

from breakwater.models import Candle, PairType, Side
from breakwater.strategy import detect_big_wave


def frame(direction="up", count=90):
    start = datetime(2026, 8, 10, tzinfo=timezone.utc)
    rows = []
    price = Decimal("100")
    for index in range(count):
        drift = Decimal("0.25") if direction == "up" else Decimal("-0.25")
        open_price = price
        close = price + drift
        high = max(open_price, close) + Decimal("0.1")
        low = min(open_price, close) - Decimal("0.1")
        if index == count - 1:
            close = close + (Decimal("3") if direction == "up" else Decimal("-3"))
            high = max(high, close + Decimal("0.1"))
            low = min(low, close - Decimal("0.1"))
        rows.append(Candle(
            pair="ETHUSDTPERP",
            period_seconds=3600,
            start=start + timedelta(hours=index),
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=Decimal("100") + index,
        ))
        price = close
    return rows


def test_detects_long_big_wave():
    rows = frame("up")
    now = rows[-1].complete_at()
    signal = detect_big_wave(
        rows, pair="ETHUSDTPERP", pair_type=PairType.FUTURE, server_time=now
    )
    assert signal is not None
    assert signal.side is Side.BUY
    assert signal.stop_price < signal.entry_price


def test_detects_short_big_wave_for_perpetual():
    rows = frame("down")
    now = rows[-1].complete_at()
    signal = detect_big_wave(
        rows, pair="ETHUSDTPERP", pair_type=PairType.FUTURE, server_time=now
    )
    assert signal is not None
    assert signal.side is Side.SELL
    assert signal.stop_price > signal.entry_price


def test_spot_does_not_short():
    rows = frame("down")
    now = rows[-1].complete_at()
    assert detect_big_wave(
        rows, pair="ETHZAR", pair_type=PairType.SPOT, server_time=now
    ) is None


def test_current_open_candle_cannot_trigger():
    rows = frame("up")
    now = rows[-1].start + timedelta(minutes=30)
    signal = detect_big_wave(
        rows, pair="ETHUSDTPERP", pair_type=PairType.FUTURE, server_time=now
    )
    assert signal is None or signal.candle_start < rows[-1].start


def test_allowed_side_filters_signal():
    rows = frame("up")
    now = rows[-1].complete_at()
    assert detect_big_wave(
        rows,
        pair="ETHUSDTPERP",
        pair_type=PairType.FUTURE,
        server_time=now,
        allowed_side=Side.SELL,
    ) is None
