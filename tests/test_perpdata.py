from decimal import Decimal

import pytest

from breakwater.perpdata import (
    fetch_perp_candles,
    fetch_perp_candles_for_pair,
    pair_to_coin,
)


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def post(self, url, json=None, timeout=None):
        self.calls.append((url, json, timeout))
        return FakeResponse(self.payload)


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


def test_fetch_perp_candles_rejects_unknown_schema():
    session = FakeSession([{"mystery": True}])
    with pytest.raises(RuntimeError, match="schema"):
        fetch_perp_candles("BTC", interval="1h", count=2, session=session)


def test_fetch_perp_candles_for_pair_skips_builder_pairs():
    with pytest.raises(ValueError, match="no Hyperliquid coin mapping"):
        fetch_perp_candles_for_pair("xyz:SNDKUSDC")
