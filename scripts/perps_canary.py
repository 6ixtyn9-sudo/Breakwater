#!/usr/bin/env python3
"""Authenticated VALR Perps connectivity canary.

Reads VALR_API_KEY and VALR_API_SECRET from the environment or .env and
probes every read endpoint Breakwater uses, printing status codes and
short response snippets. It performs no writes. Run it locally after
creating a key to verify permissions and endpoint behaviour in one step.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import requests  # noqa: E402

from breakwater.config import get_settings  # noqa: E402
from breakwater.valr import ValrClient, sign_request  # noqa: E402

BASE = "https://api.valr.com"


def probe(client: ValrClient, label: str, func, *args) -> None:
    try:
        payload = func(*args)
        if isinstance(payload, list):
            snippet = f"list of {len(payload)} rows"
            if payload:
                snippet += f" first={str(payload[0])[:100]}"
        elif isinstance(payload, dict):
            snippet = "keys=" + ",".join(sorted(str(key) for key in payload.keys())[:8])
        else:
            snippet = str(payload)[:100]
        print(f"OK    {label}: {snippet}")
    except Exception as exc:
        print(f"FAIL  {label}: {type(exc).__name__}: {exc}")


def signed_headers(client: ValrClient, path: str) -> dict:
    timestamp = int(time.time() * 1000)
    return {
        "Content-Type": "application/json",
        "X-VALR-API-KEY": client.api_key or "",
        "X-VALR-TIMESTAMP": str(timestamp),
        "X-VALR-SIGNATURE": sign_request(
            client.api_secret or "", timestamp, "GET", path
        ),
    }


def raw_probe(client: ValrClient, label: str, path: str, query: str = "") -> None:
    try:
        headers = signed_headers(client, path)
        response = requests.get(BASE + path + query, headers=headers, timeout=15)
        print(f"RAW   {label}: HTTP {response.status_code} {response.text[:140]}")
    except Exception as exc:
        print(f"RAW   {label}: transport error {type(exc).__name__}: {exc}")


def main() -> int:
    settings = get_settings()
    if not settings.has_credentials:
        print("No VALR_API_KEY / VALR_API_SECRET found in the environment or .env")
        return 1
    client = ValrClient(
        api_key=settings.api_key,
        api_secret=settings.api_secret,
        allow_writes=False,
    )
    print(
        f"Key loaded: {len(settings.api_key)} chars, starts with "
        f"{settings.api_key[:4]}... (secret hidden)"
    )
    print("---")
    probe(client, "GET /v1/account/api-keys/current (permissions)", client.current_api_key)
    print("---")
    symbols = client.perps_symbol_info()
    print(f"Perps symbol-info: {len(symbols)} symbols (public)")
    top = sorted(symbols, key=lambda s: (-s.volume, -s.open_interest))[:10]
    for rank, symbol in enumerate(top, start=1):
        print(
            f"  {rank:>2} {symbol.pair:<14} mark={symbol.mark_price:<12} "
            f"vol={symbol.volume:<14} oi={symbol.open_interest:<14} "
            f"lev={symbol.max_leverage}x funding={symbol.funding_rate}"
        )
    print("---")
    probe(client, "GET /simple-futures/status", client.perps_status)
    probe(client, "GET /simple-futures/ticker", client.perps_ticker)
    probe(client, "GET /simple-futures/candles BTCUSDC", client.perps_candles, "BTCUSDC")
    probe(client, "GET /simple-futures/positions", client.perps_positions)
    probe(client, "GET /simple-futures/orders", client.perps_orders)
    probe(client, "GET /simple-futures/account", client.perps_account)
    print("---")
    print("Raw probes (signature over the path, query excluded):")
    raw_probe(client, "symbol-info/BTCUSDC", "/simple-futures/symbol-info/BTCUSDC")
    raw_probe(client, "candles interval=1h", "/simple-futures/candles/BTCUSDC", "?interval=1h&limit=5")
    raw_probe(client, "candles no query", "/simple-futures/candles/BTCUSDC")
    raw_probe(client, "klines interval=1h", "/simple-futures/klines/BTCUSDC", "?interval=1h&limit=5")
    raw_probe(client, "orderbook", "/simple-futures/orderbook/BTCUSDC")
    raw_probe(client, "trades", "/simple-futures/trades/BTCUSDC")
    raw_probe(client, "funding", "/simple-futures/funding/BTCUSDC")
    raw_probe(client, "mark-price", "/simple-futures/mark-price/BTCUSDC")
    raw_probe(client, "positions", "/simple-futures/positions")
    raw_probe(client, "orders", "/simple-futures/orders")
    raw_probe(client, "account", "/simple-futures/account")
    raw_probe(client, "margin/account", "/simple-futures/margin/account")
    print("---")
    print("No account writes were performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
