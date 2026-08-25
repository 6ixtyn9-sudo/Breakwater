from decimal import Decimal

import pytest

from breakwater.perpdata import (
    fetch_perp_candles,
    fetch_perp_candles_for_pair,
    pair_to_coin,
)


class FakeResponse:
    def __init__(self, payload, status=200, headers=None):
        self._payload = payload
        self.status_code = status
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def post(self, url, json=None, timeout=None):
        self.calls.append((url, json, timeout))
        return FakeResponse(self.payload)


class FlakySession:
    """Returns queued HTTP statuses (e.g. 429 bursts) before a 200 payload."""

    def __init__(self, payload, statuses):
        self.payload = payload
        self.statuses = list(statuses)
        self.calls = 0

    def post(self, url, json=None, timeout=None):
        self.calls += 1
        status = self.statuses.pop(0) if self.statuses else 200
        return FakeResponse(self.payload, status=status, headers={"Retry-After": "1"})


def candle_payload():
    return [
        {"t": 1786579200000, "T": 1786582799999, "s": "BTC", "i": "1h",
         "o": "63467.0", "c": "63550.0", "h": "63700.0", "l": "63449.0",
         "v": "1539.52942", "n": 9162},
        {"t": 1786582800000, "T": 1786586399999, "s": "BTC", "i": "1h",
         "o": "63550.0", "c": "63434.0", "h": "63617.0", "l": "63364.0",
         "v": "905.12428", "n": 6665},
    ]


def test_pair_to_coin_maps_valr_symbols():
    assert pair_to_coin("BTCUSDC") == "BTC"
    assert pair_to_coin("ethusdc") == "ETH"
    assert pair_to_coin("xyz:SNDKUSDC") is None
    assert pair_to_coin("BTCUSDT") is None
    assert pair_to_coin("KPEPEUSDC") == "kPEPE"


def test_fetch_perp_candles_maps_hyperliquid_schema():
    session = FakeSession(candle_payload())
    candles = fetch_perp_candles("BTC", interval="1h", count=2, session=session)
    assert len(candles) == 2
    assert candles[0].pair == "BTCUSDC"
    assert candles[0].period_seconds == 3600
    assert candles[0].close == Decimal("63550.0")
    assert candles[0].volume == Decimal("1539.52942")
    url, body, _ = session.calls[0]
    assert url == "https://api.hyperliquid.xyz/info"
    assert body["type"] == "candleSnapshot"
    assert body["req"]["coin"] == "BTC"
    assert body["req"]["interval"] == "1h"
    assert body["req"]["endTime"] - body["req"]["startTime"] == 3600 * 1000


def test_fetch_perp_candles_rejects_unknown_schema():
    session = FakeSession([{"mystery": True}])
    with pytest.raises(RuntimeError, match="schema"):
        fetch_perp_candles("BTC", interval="1h", count=2, session=session)


def test_fetch_perp_candles_retries_rate_limit_and_server_errors(monkeypatch):
    import breakwater.perpdata as perpdata

    slept = []
    monkeypatch.setattr(perpdata.time, "sleep", lambda seconds: slept.append(seconds))
    session = FlakySession(candle_payload(), [429, 503])
    candles = fetch_perp_candles("BTC", interval="1h", count=2, session=session)
    assert len(candles) == 2
    assert session.calls == 3
    assert len(slept) == 2


def test_fetch_perp_candles_gives_up_after_three_attempts(monkeypatch):
    import breakwater.perpdata as perpdata

    monkeypatch.setattr(perpdata.time, "sleep", lambda seconds: None)
    session = FlakySession([], [429, 429, 429])
    with pytest.raises(RuntimeError, match="429"):
        fetch_perp_candles("BTC", interval="1h", count=2, session=session)
    assert session.calls == 3


def test_fetch_perp_candles_preserves_hip3_dex_prefix():
    session = FakeSession(candle_payload())
    fetch_perp_candles("xyz:NVDA", interval="1h", count=2, session=session)
    assert session.calls[0][1]["req"]["coin"] == "xyz:NVDA"


def test_fetch_perp_candles_for_pair_skips_builder_pairs():
    with pytest.raises(ValueError, match="no Hyperliquid coin mapping"):
        fetch_perp_candles_for_pair("xyz:SNDKUSDC")
