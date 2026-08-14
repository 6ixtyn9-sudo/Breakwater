from decimal import Decimal

import pytest

from breakwater.valr import ValrClient, ValrError


class Response:
    def __init__(self, status=200, payload=None):
        self.status_code = status
        self._payload = payload
        self.text = ""
        self.content = b"x" if payload is not None else b""

    def json(self):
        return self._payload


class Session:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def client_with(responses):
    return ValrClient("key", "secret", session=Session(responses))


def test_perp_symbol_info_parses_venue_payload():
    client = client_with([Response(payload={"symbols": [{
        "currencyPair": "BTCUSDC",
        "baseAsset": "BTC",
        "maxLeverage": "10",
        "minNotional": "11",
        "minMarginAmount": "2",
        "markPrice": "1500",
        "priceDecimalPlaces": 6,
        "volume": "500000",
        "openInterest": "900",
        "fundingRate": "0.00001",
    }]})])
    symbols = client.perps_symbol_info()
    assert len(symbols) == 1
    assert symbols[0].pair == "BTCUSDC"
    assert symbols[0].min_notional == 11
    assert symbols[0].max_leverage == 10
    assert symbols[0].volume == 500000
    assert symbols[0].open_interest == 900
    assert symbols[0].funding_rate == Decimal("0.00001")


def test_perp_position_history_normalizes_venue_fields():
    client = client_with([Response(payload=[{
        "pair": "BTCUSDC",
        "side": "LONG",
        "quantity": "0.01",
        "entryPrice": "1500",
        "unrealisedPnl": "2.5",
        "margin": "5",
    }])])
    positions = client.perps_positions()
    assert positions[0]["pair"] == "BTCUSDC"
    assert positions[0]["side"] == "BUY"
    assert positions[0]["margin"] == 5


def test_perp_position_history_fails_closed_on_unknown_schema():
    client = client_with([Response(payload=[{"mystery": True}])])
    with pytest.raises(ValrError, match="schema"):
        client.perps_positions()


def test_perp_account_endpoints_use_app_paths():
    client = client_with([
        Response(payload=[]),
        Response(payload=[]),
        Response(payload={}),
        Response(payload={}),
    ])
    assert client.perps_position_history() == []
    assert client.perps_position_timeline() == []
    assert client.perps_settings() == {}
    assert client.perps_address() == {}
    paths = [call[0][1] for call in client.session.calls]
    assert paths == [
        "https://api.valr.com/simple-futures/position-history",
        "https://api.valr.com/simple-futures/position-timeline",
        "https://api.valr.com/simple-futures/settings",
        "https://api.valr.com/simple-futures/address",
    ]
