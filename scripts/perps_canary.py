#!/usr/bin/env python3
"""Authenticated VALR Perps connectivity canary.

Reads VALR_API_KEY and VALR_API_SECRET from the environment or .env and
probes the endpoints the VALR web application itself uses, printing
status codes and short response snippets. It performs no writes. Perp
market data comes from the Hyperliquid public info API and needs no
VALR credentials at all.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import requests  # noqa: E402

from breakwater.config import get_settings  # noqa: E402
from breakwater.perpdata import fetch_perp_candles_for_pair  # noqa: E402
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
    client = ValrClient(
        api_key=settings.api_key,
        api_secret=settings.api_secret,
        allow_writes=False,
    )
    print("Perp market data (public, no VALR credentials needed):")
    try:
        candles = fetch_perp_candles_for_pair("BTCUSDC", interval="1h", count=3)
        print(f"OK    hyperliquid candles BTCUSDC: {len(candles)} rows, last close={candles[-1].close}")
    except Exception as exc:
        print(f"FAIL  hyperliquid candles BTCUSDC: {type(exc).__name__}: {exc}")
    print("---")
    symbols = client.perps_symbol_info()
    print(f"VALR perps symbol-info: {len(symbols)} symbols (public)")
    top = sorted(symbols, key=lambda s: (-s.volume, -s.open_interest))[:10]
    for rank, symbol in enumerate(top, start=1):
        print(
            f"  {rank:>2} {symbol.pair:<14} mark={symbol.mark_price:<12} "
            f"vol={symbol.volume:<14} lev={symbol.max_leverage}x"
        )
    print("---")
    if not settings.has_credentials:
        print("No VALR credentials found: skipping account-scope probes.")
        return 0
    print(
        f"Key loaded: {len(settings.api_key)} chars, starts with "
        f"{settings.api_key[:4]}... (secret hidden)"
    )
    print("---")
    probe(client, "GET /v1/account/api-keys/current (permissions)", client.current_api_key)
    print("---")
    print("VALR perps account endpoints (as used by the VALR web app):")
    probe(client, "GET /simple-futures/position-history", client.perps_position_history)
    probe(client, "GET /simple-futures/position-timeline", client.perps_position_timeline)
    probe(client, "GET /simple-futures/settings", client.perps_settings)
    probe(client, "GET /simple-futures/address", client.perps_address)
    print("---")
    print("Raw probes (signature over the path, query excluded):")
    raw_probe(client, "position-history", "/simple-futures/position-history")
    raw_probe(client, "settings", "/simple-futures/settings")
    raw_probe(client, "address", "/simple-futures/address")
    print("---")
    print(
        "Verdict: if the account routes above return 401 code -93 with a valid "
        "key, VALR Perps trading is currently web-session-only and is not yet "
        "available to API keys. Breakwater records perps_api on every guardian "
        "run and will detect automatically when this changes."
    )
    print("No account writes were performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
