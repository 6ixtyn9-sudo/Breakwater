#!/usr/bin/env python3
"""Authenticated VALR Perps connectivity canary.

Reads VALR_API_KEY and VALR_API_SECRET from the environment or .env and
probes every read endpoint Breakwater uses, printing status codes and
short response snippets. It performs no writes. Run it locally after
creating a key to verify permissions and endpoint behaviour in one step.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import requests  # noqa: E402

from breakwater.config import get_settings  # noqa: E402
from breakwater.valr import ValrClient  # noqa: E402

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


def raw_probe(client: ValrClient, label: str, path: str) -> None:
    try:
        headers = client._headers("GET", path, "")
        response = requests.get(BASE + path, headers=headers, timeout=15)
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
    probe(client, "GET /simple-futures/symbol-info (public)", client.perps_symbol_info)
    probe(client, "GET /simple-futures/status", client.perps_status)
    probe(client, "GET /simple-futures/ticker", client.perps_ticker)
    probe(client, "GET /simple-futures/candles BTCUSDC", client.perps_candles, "BTCUSDC")
    probe(client, "GET /simple-futures/positions", client.perps_positions)
    probe(client, "GET /simple-futures/orders", client.perps_orders)
    probe(client, "GET /simple-futures/account", client.perps_account)
    print("---")
    raw_probe(client, "candles interval=1h&limit=5", "/simple-futures/candles/BTCUSDC?interval=1h&limit=5")
    raw_probe(client, "candles interval=60&limit=5", "/simple-futures/candles/BTCUSDC?interval=60&limit=5")
    raw_probe(client, "candles timeframe=1h&limit=5", "/simple-futures/candles/BTCUSDC?timeframe=1h&limit=5")
    raw_probe(client, "candles periodSeconds=3600&limit=5", "/simple-futures/candles/BTCUSDC?periodSeconds=3600&limit=5")
    raw_probe(client, "candles no query", "/simple-futures/candles/BTCUSDC")
    raw_probe(client, "klines interval=1h&limit=5", "/simple-futures/klines/BTCUSDC?interval=1h&limit=5")
    print("---")
    print("No account writes were performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
