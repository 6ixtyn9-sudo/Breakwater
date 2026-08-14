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
    }]})])
    symbols = client.perps_symbol_info()
    assert len(symbols) == 1
    assert symbols[0].pair == "BTCUSDC"
    assert symbols[0].min_notional == 11
    assert symbols[0].max_leverage == 10


def test_perp_candles_map_tolerant_schema():
    client = client_with([Response(payload=[
        {"t": 1786705200000, "o": "10", "h": "11", "l": "9.5", "c": "10.5", "v": "100"}
    ])])
    candles = client.perps_candles("BTCUSDC")
    assert len(candles) == 1
    assert candles[0].pair == "BTCUSDC"
    assert str(candles[0].close) == "10.5"


def test_perp_candles_fail_closed_on_unknown_schema():
    client = client_with([Response(payload=[{"something": "else"}])])
    with pytest.raises(ValrError, match="schema"):
        client.perps_candles("BTCUSDC")


def test_perp_positions_normalize_venue_fields():
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


def test_perp_positions_fail_closed_on_unknown_schema():
    client = client_with([Response(payload=[{"mystery": True}])])
    with pytest.raises(ValrError, match="schema"):
        client.perps_positions()


def test_perp_endpoints_require_authentication():
    session = Session([Response(status=401, payload={"code": -93, "message": "Unauthorized"})])
    client = ValrClient("key", "secret", session=session)
    with pytest.raises(Exception):
        client.perps_orders()
