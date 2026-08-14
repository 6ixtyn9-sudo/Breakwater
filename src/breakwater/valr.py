"""Minimal VALR REST adapter with signed requests and a hard write gate."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from urllib.parse import urlencode

import requests

from breakwater.models import Candle, MarketSummary, PairSpec, PerpSymbol, Position

BASE_URL = "https://api.valr.com"


class ValrError(RuntimeError):
    pass


class ValrAuthenticationError(ValrError):
    pass


class ValrWriteBlocked(ValrError):
    pass


def sign_request(
    api_secret: str,
    timestamp_ms: int | str,
    verb: str,
    path: str,
    body: str = "",
    subaccount_id: str | None = None,
) -> str:
    payload = (
        f"{timestamp_ms}{verb.upper()}{path}{body}"
        f"{subaccount_id or ''}"
    ).encode()
    return hmac.new(api_secret.encode(), payload, hashlib.sha512).hexdigest()


@dataclass
class ValrClient:
    api_key: str | None = None
    api_secret: str | None = None
    subaccount_id: str | None = None
    allow_writes: bool = False
    timeout: float = 20.0
    session: Any = None

    def __post_init__(self) -> None:
        if bool(self.api_key) != bool(self.api_secret):
            raise ValrAuthenticationError("VALR API key and secret must be configured together")
        if self.session is None:
            self.session = requests.Session()
        if BASE_URL != "https://api.valr.com":
            raise RuntimeError("VALR base URL is not the production HTTPS endpoint")

    def _headers(self, verb: str, path: str, body: str) -> dict[str, str]:
        if not self.api_key or not self.api_secret:
            raise ValrAuthenticationError("authenticated VALR request requires credentials")
        timestamp = int(time.time() * 1000)
        headers = {
            "Content-Type": "application/json",
            "X-VALR-API-KEY": self.api_key,
            "X-VALR-TIMESTAMP": str(timestamp),
            "X-VALR-SIGNATURE": sign_request(
                self.api_secret, timestamp, verb, path, body, self.subaccount_id
            ),
        }
        if self.subaccount_id:
            headers["X-VALR-SUB-ACCOUNT-ID"] = self.subaccount_id
        return headers

    def _request(
        self,
        verb: str,
        path: str,
        *,
        body: dict | None = None,
        authenticated: bool = False,
        write: bool = False,
    ):
        verb = verb.upper()
        if not path.startswith("/"):
            raise ValueError("VALR path must begin with a slash")
        if write and not self.allow_writes:
            raise ValrWriteBlocked("VALR write request blocked by Breakwater live gate")
        payload = json.dumps(body, separators=(",", ":")) if body is not None else ""
        attempts = 3 if verb == "GET" else 1
        last_error = None
        for attempt in range(attempts):
            headers = (
                self._headers(verb, path, payload)
                if authenticated else {"Content-Type": "application/json"}
            )
            try:
                response = self.session.request(
                    verb,
                    BASE_URL + path,
                    headers=headers,
                    data=payload or None,
                    timeout=self.timeout,
                )
            except requests.RequestException as exc:
                last_error = exc
                if attempt + 1 < attempts:
                    time.sleep(0.25 * (2 ** attempt))
                    continue
                raise ValrError(f"VALR request failed: {exc}") from exc
            if response.status_code in {401, 403}:
                raise ValrAuthenticationError(
                    f"VALR authentication rejected request with HTTP {response.status_code}"
                )
            if response.status_code == 429 and attempt + 1 < attempts:
                time.sleep(0.5 * (2 ** attempt))
                continue
            if response.status_code < 200 or response.status_code >= 300:
                text = str(getattr(response, "text", ""))[:500]
                raise ValrError(f"VALR HTTP {response.status_code}: {text}")
            if response.status_code == 204 or not getattr(response, "content", b""):
                return None
            try:
                return response.json()
            except ValueError as exc:
                raise ValrError("VALR returned non-JSON content") from exc
        raise ValrError(f"VALR request failed: {last_error}")

    def server_time(self) -> dict:
        return self._request("GET", "/v1/public/time")

    def exchange_status(self) -> dict:
        return self._request("GET", "/v1/public/status")

    def pairs(self, pair_type: str | None = None) -> list[PairSpec]:
        suffix = f"/{pair_type.upper()}" if pair_type else ""
        rows = self._request("GET", f"/v1/public/pairs{suffix}")
        if not isinstance(rows, list):
            raise ValrError("VALR pairs response is malformed")
        return [PairSpec.from_payload(row) for row in rows]

    def market_summary(self, pair: str) -> MarketSummary:
        row = self._request("GET", f"/v1/public/{pair.upper()}/marketsummary")
        if not isinstance(row, dict):
            raise ValrError("VALR market summary is malformed")
        return MarketSummary.from_payload(row)

    def market_summaries(self) -> list[MarketSummary]:
        rows = self._request("GET", "/v1/public/marketsummary")
        if not isinstance(rows, list):
            raise ValrError("VALR all-market summaries response is malformed")
        return [MarketSummary.from_payload(row) for row in rows]

    def order_types(self, pair: str) -> set[str]:
        rows = self._request("GET", f"/v1/public/{pair.upper()}/ordertypes")
        if not isinstance(rows, list):
            raise ValrError("VALR order types response is malformed")
        return {str(value).upper() for value in rows}

    def candles(
        self,
        pair: str,
        *,
        period_seconds: int,
        start_epoch: int,
        end_epoch: int,
        limit: int = 300,
    ) -> list[Candle]:
        if period_seconds not in {60, 300, 900, 1800, 3600, 21600, 86400}:
            raise ValueError("unsupported VALR candle period")
        if limit < 1 or limit > 300:
            raise ValueError("VALR candle limit must be between 1 and 300")
        query = urlencode({
            "periodSeconds": period_seconds,
            "startTime": start_epoch,
            "endTime": end_epoch,
            "limit": limit,
        })
        rows = self._request("GET", f"/v1/public/{pair.upper()}/buckets?{query}")
        if not isinstance(rows, list):
            raise ValrError("VALR candle response is malformed")
        return [Candle.from_payload(row) for row in rows]

    def futures_info(self) -> list[dict]:
        rows = self._request("GET", "/v1/public/futures/info")
        if not isinstance(rows, list):
            raise ValrError("VALR futures info response is malformed")
        return rows

    def risk_limits(self, pair: str) -> list[dict]:
        rows = self._request("GET", f"/v1/public/risklimit/{pair.upper()}")
        if not isinstance(rows, list):
            raise ValrError("VALR risk limits response is malformed")
        return rows

    def balances(self) -> list[dict]:
        rows = self._request(
            "GET", "/v1/account/balances?excludeZeroBalances=true", authenticated=True
        )
        if not isinstance(rows, list):
            raise ValrError("VALR balances response is malformed")
        return rows

    def all_account_balances(self) -> list[dict]:
        if self.subaccount_id:
            raise ValrAuthenticationError(
                "all-account balances require an unscoped main-account client"
            )
        rows = self._request("GET", "/v1/account/balances/all", authenticated=True)
        if not isinstance(rows, list):
            raise ValrError("VALR all-account balances response is malformed")
        return rows

    def current_api_key(self) -> dict:
        row = self._request("GET", "/v1/account/api-keys/current", authenticated=True)
        if not isinstance(row, dict):
            raise ValrError("VALR current API key response is malformed")
        return row

    def trade_fees(self) -> list[dict]:
        rows = self._request("GET", "/v1/account/fees/trade", authenticated=True)
        if not isinstance(rows, list):
            raise ValrError("VALR fee response is malformed")
        return rows

    def open_orders(self) -> list[dict]:
        rows = self._request("GET", "/v1/orders/open", authenticated=True)
        if not isinstance(rows, list):
            raise ValrError("VALR open orders response is malformed")
        return rows

    def open_positions(self) -> list[Position]:
        rows = self._request("GET", "/v1/positions/open", authenticated=True)
        if not isinstance(rows, list):
            raise ValrError("VALR open positions response is malformed")
        return [Position.from_payload(row) for row in rows]

    def conditional_orders(self) -> list[dict]:
        rows = self._request("GET", "/v1/conditionals", authenticated=True)
        if not isinstance(rows, list):
            raise ValrError("VALR conditional orders response is malformed")
        return rows

    def margin_status(self) -> dict:
        row = self._request("GET", "/v1/margin/account/status", authenticated=True)
        if not isinstance(row, dict):
            raise ValrError("VALR margin status response is malformed")
        return row

    def leverage(self, pair: str) -> dict:
        row = self._request(
            "GET", f"/v1/margin/leverage/{pair.upper()}", authenticated=True
        )
        if not isinstance(row, dict):
            raise ValrError("VALR leverage response is malformed")
        return row

    def active_order(self, pair: str, order_id: str) -> dict:
        row = self._request(
            "GET", f"/v1/orders/{pair.upper()}/orderid/{order_id}", authenticated=True
        )
        if not isinstance(row, dict):
            raise ValrError("VALR active order response is malformed")
        return row

    def completed_order(self, order_id: str) -> dict:
        row = self._request(
            "GET", f"/v1/orders/history/summary/orderid/{order_id}", authenticated=True
        )
        if not isinstance(row, dict):
            raise ValrError("VALR completed order response is malformed")
        return row

    def place_limit(self, body: dict) -> dict:
        return self._request(
            "POST", "/v2/orders/limit", body=body, authenticated=True, write=True
        )

    def place_market(self, body: dict) -> dict:
        return self._request(
            "POST", "/v2/orders/market", body=body, authenticated=True, write=True
        )

    def place_spot_stop_limit(self, body: dict) -> dict:
        return self._request(
            "POST", "/v2/orders/stop/limit", body=body, authenticated=True, write=True
        )

    def cancel_order(self, pair: str, order_id: str) -> dict:
        return self._request(
            "DELETE",
            "/v2/orders/order",
            body={"orderId": order_id, "pair": pair.upper()},
            authenticated=True,
            write=True,
        )

    def perps_symbol_info(self) -> list[PerpSymbol]:
        rows = self._request("GET", "/simple-futures/symbol-info")
        if not isinstance(rows, dict) or not isinstance(rows.get("symbols"), list):
            raise ValrError("VALR perps symbol-info response is malformed")
        return [PerpSymbol.from_payload(row) for row in rows["symbols"]]

    def perps_candles(
        self, pair: str, *, interval: str = "1h", limit: int = 220
    ) -> list[Candle]:
        query = urlencode({"interval": interval, "limit": limit})
        rows = self._request(
            "GET", f"/simple-futures/candles/{pair.upper()}?{query}", authenticated=True
        )
        if not isinstance(rows, list):
            raise ValrError("VALR perps candles response is malformed")
        candles = []
        for row in rows:
            candles.append(_perp_candle(row, pair.upper(), interval))
        return candles

    def perps_positions(self) -> list[dict]:
        rows = self._request("GET", "/simple-futures/positions", authenticated=True)
        if not isinstance(rows, list):
            raise ValrError("VALR perps positions response is malformed")
        return [_perp_position(row) for row in rows]

    def perps_orders(self) -> list[dict]:
        rows = self._request("GET", "/simple-futures/orders", authenticated=True)
        if not isinstance(rows, list):
            raise ValrError("VALR perps orders response is malformed")
        return [_perp_order(row) for row in rows]

    def perps_account(self) -> dict:
        row = self._request("GET", "/simple-futures/account", authenticated=True)
        if not isinstance(row, dict):
            raise ValrError("VALR perps account response is malformed")
        return row

    def perps_ticker(self) -> list[dict]:
        rows = self._request("GET", "/simple-futures/ticker", authenticated=True)
        if not isinstance(rows, list):
            raise ValrError("VALR perps ticker response is malformed")
        return rows

    def perps_status(self) -> dict:
        row = self._request("GET", "/simple-futures/status", authenticated=True)
        if not isinstance(row, dict):
            raise ValrError("VALR perps status response is malformed")
        return row


def _first(row: dict, *names: str):
    for name in names:
        if name in row and row[name] is not None:
            return row[name]
    return None


def _number(value, field: str) -> Decimal:
    return Decimal(str(value))


def _perp_time(row: dict, pair: str, interval: str) -> datetime:
    value = _first(row, "t", "ts", "time", "timestamp", "openTime", "startTime")
    if value is None:
        raise ValrError(f"VALR perps candle for {pair} has no timestamp")
    text = str(value)
    try:
        epoch_ms = int(text)
        if epoch_ms < 10_000_000_000:
            epoch_ms *= 1000
        return datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)
    except ValueError:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)


def _perp_candle(row: dict, pair: str, interval: str) -> Candle:
    close = _first(row, "c", "close")
    if close is None:
        raise ValrError(
            "VALR perps candle schema is unrecognized; update the client mapping"
        )
    return Candle(
        pair=pair,
        period_seconds={"1h": 3600, "4h": 14400, "1d": 86400}.get(interval, 3600),
        start=_perp_time(row, pair, interval),
        open=_number(_first(row, "o", "open") or close, "open"),
        high=_number(_first(row, "h", "high") or close, "high"),
        low=_number(_first(row, "l", "low") or close, "low"),
        close=_number(close, "close"),
        volume=_number(_first(row, "v", "volume") or 0, "volume"),
    )


def _perp_position(row: dict) -> dict:
    pair = str(_first(row, "pair", "symbol", "currencyPair", "coin") or "")
    if not pair:
        raise ValrError(
            "VALR perps position schema is unrecognized; update the client mapping"
        )
    side = str(_first(row, "side", "direction") or "").upper()
    if side in {"LONG", "UP", "BUY"}:
        side = "BUY"
    elif side in {"SHORT", "DOWN", "SELL"}:
        side = "SELL"
    return {
        "pair": pair.upper(),
        "side": side,
        "quantity": _number(_first(row, "quantity", "size", "amount") or 0, "quantity"),
        "entry_price": _number(
            _first(row, "entryPrice", "averageEntryPrice", "entryPx") or 0, "entry"
        ),
        "unrealised_pnl": _number(
            _first(row, "unrealisedPnl", "unrealizedPnl", "uPnl") or 0, "pnl"
        ),
        "margin": _number(_first(row, "margin", "marginUsed") or 0, "margin"),
    }


def _perp_order(row: dict) -> dict:
    pair = str(_first(row, "pair", "symbol", "currencyPair", "coin") or "")
    if not pair:
        raise ValrError(
            "VALR perps order schema is unrecognized; update the client mapping"
        )
    return {
        "pair": pair.upper(),
        "order_id": str(_first(row, "orderId", "id") or ""),
        "side": str(_first(row, "side", "direction") or "").upper(),
        "quantity": _number(_first(row, "quantity", "size", "amount") or 0, "quantity"),
        "price": _number(_first(row, "price", "limitPrice") or 0, "price"),
        "status": str(_first(row, "status", "state") or "").upper(),
    }
