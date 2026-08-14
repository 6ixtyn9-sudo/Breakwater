import json

import pytest
import requests

from breakwater.valr import (
    ValrAuthenticationError,
    ValrClient,
    ValrError,
    ValrWriteBlocked,
)


class Response:
    def __init__(self, status=200, payload=None, text=""):
        self.status_code = status
        self._payload = payload
        self.text = text
        self.content = b"x" if payload is not None else b""

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
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


def test_key_with_whitespace_is_rejected_before_sending():
    client = ValrClient("some\nkey", "secret", session=Session([]))
    with pytest.raises(ValrAuthenticationError, match="whitespace"):
        client.current_api_key()


def test_public_request_needs_no_credentials():
    session = Session([Response(payload={"status": "online"})])
    client = ValrClient(session=session)
    assert client.exchange_status() == {"status": "online"}
    headers = session.calls[0][1]["headers"]
    assert "X-VALR-API-KEY" not in headers


def test_authenticated_request_is_signed(monkeypatch):
    monkeypatch.setattr("time.time", lambda: 1234.5)
    session = Session([Response(payload=[])])
    client = ValrClient("key", "secret", subaccount_id="42", session=session)
    assert client.open_orders() == []
    headers = session.calls[0][1]["headers"]
    assert headers["X-VALR-API-KEY"] == "key"
    assert headers["X-VALR-SUB-ACCOUNT-ID"] == "42"
    assert headers["X-VALR-TIMESTAMP"] == "1234500"
    assert headers["X-VALR-SIGNATURE"]


def test_write_is_blocked_by_default():
    client = ValrClient("key", "secret", session=Session([]))
    with pytest.raises(ValrWriteBlocked):
        client.place_market({"side": "BUY", "pair": "BTCZAR", "quoteAmount": "10"})


def test_auth_failure_is_not_converted_to_empty_state():
    client = ValrClient(
        "key", "secret", session=Session([Response(status=403, payload={})])
    )
    with pytest.raises(ValrAuthenticationError):
        client.balances()


def test_malformed_json_fails_closed():
    client = ValrClient(session=Session([Response(payload=ValueError("bad"))]))
    with pytest.raises(ValrError, match="non-JSON"):
        client.exchange_status()


def test_get_retries_network_failure(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda value: None)
    session = Session([
        requests.ConnectionError("offline"),
        Response(payload={"status": "online"}),
    ])
    client = ValrClient(session=session)
    assert client.exchange_status()["status"] == "online"
    assert len(session.calls) == 2


def test_write_body_is_canonical_json(monkeypatch):
    monkeypatch.setattr("time.time", lambda: 1)
    session = Session([Response(status=201, payload={"id": "one"})])
    client = ValrClient("key", "secret", allow_writes=True, session=session)
    result = client.place_limit({"side": "BUY", "quantity": "1"})
    assert result == {"id": "one"}
    body = session.calls[0][1]["data"]
    assert body == json.dumps({"side": "BUY", "quantity": "1"}, separators=(",", ":"))


def test_all_account_balances_refuses_scoped_client():
    client = ValrClient("key", "secret", subaccount_id="42", session=Session([]))
    with pytest.raises(ValrAuthenticationError, match="unscoped"):
        client.all_account_balances()
