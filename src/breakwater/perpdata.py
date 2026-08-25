"""Hyperliquid public market data for VALR Perps pairs.

VALR Perps executes on Hyperliquid. Market data such as candles is served
by Hyperliquid's public info API and needs no VALR credentials, which the
VALR web application itself relies on.

HIP-3 builder venues (VALR symbols like ``xyz:NVDAUSDC``) *do* have a
Hyperliquid coin id (``xyz:NVDA``). This crypto research/paper path still
skips them on purpose: they are equity/commodity/index oracles, not the
crypto book. They occupy volume-rank slots but are dropped from the
window rather than replaced by tail dust, and must not inflate pair-error counts.
A later dedicated HIP-3 pass can map them; do not mix them into this pool.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from decimal import Decimal

import requests

from breakwater.models import Candle

HYPERLIQUID_INFO_URL = "https://api.hyperliquid.xyz/info"

# VALR/base upper -> Hyperliquid info coin (case-sensitive on a few names).
HL_COIN_ALIASES = {
    "KPEPE": "kPEPE",
}

INTERVAL_SECONDS = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
}


def pair_to_coin(pair: str) -> str | None:
    symbol = str(pair).upper().strip()
    if ":" in symbol or not symbol.endswith("USDC"):
        return None
    coin = symbol[:-4]
    if not coin:
        return None
    return HL_COIN_ALIASES.get(coin, coin)


def _api_coin(coin: str) -> str:
    text = str(coin).strip()
    if ":" in text:
        dex, asset = text.split(":", 1)
        if not dex or not asset:
            raise ValueError("HIP-3 coin must include DEX and asset around ':'")
        return f"{dex.lower()}:{asset}"
    upper = text.upper()
    return HL_COIN_ALIASES.get(upper, upper)


def fetch_perp_candles_for_pair(pair: str, **kwargs) -> list[Candle]:
    coin = pair_to_coin(pair)
    if coin is None:
        raise ValueError(
            f"{pair} has no Hyperliquid coin mapping and cannot be researched yet"
        )
    return fetch_perp_candles(coin, **kwargs)


def fetch_perp_candles(
    coin: str,
    *,
    interval: str = "1h",
    count: int = 220,
    session: requests.Session | None = None,
    info_url: str = HYPERLIQUID_INFO_URL,
) -> list[Candle]:
    if interval not in INTERVAL_SECONDS:
        raise ValueError("unsupported perp candle interval")
    if count < 2 or count > 5000:
        raise ValueError("perp candle count must be between 2 and 5000")
    period_ms = INTERVAL_SECONDS[interval] * 1000
    end_ms = int(time.time() * 1000)
    # Hyperliquid treats both boundaries as inclusive. A span of ``count``
    # intervals can therefore request count + 1 candles and the 5,000-bar
    # boundary returns HTTP 500. Use count - 1 intervals for at most count rows.
    start_ms = end_ms - period_ms * (count - 1)
    payload = {
        "type": "candleSnapshot",
        "req": {
            "coin": _api_coin(coin),
            "interval": interval,
            "startTime": start_ms,
            "endTime": end_ms,
        },
    }
    requester = session or requests
    # The public /info API rate-limits bursts (HTTP 429) and occasionally
    # 5xx under load. Retry with backoff (honouring Retry-After) instead of
    # failing the pair for the whole cycle. getattr keeps test doubles that
    # do not model status codes working as before.
    response = None
    for attempt in range(3):
        response = requester.post(info_url, json=payload, timeout=20)
        status = getattr(response, "status_code", 200)
        if status in (429, 500, 502, 503, 504) and attempt + 1 < 3:
            headers = getattr(response, "headers", None) or {}
            retry_after = headers.get("Retry-After")
            try:
                delay = float(retry_after)
            except (TypeError, ValueError):
                delay = 1.0 * (attempt + 1)
            time.sleep(max(delay, 0.1))
            continue
        break
    response.raise_for_status()
    rows = response.json()
    if not isinstance(rows, list):
        raise RuntimeError("hyperliquid candle response is malformed")
    candles = []
    for row in rows:
        try:
            candles.append(Candle(
                pair=f"{coin.upper()}USDC",
                period_seconds=INTERVAL_SECONDS[interval],
                start=datetime.fromtimestamp(int(row["t"]) / 1000, tz=timezone.utc),
                open=Decimal(str(row["o"])),
                high=Decimal(str(row["h"])),
                low=Decimal(str(row["l"])),
                close=Decimal(str(row["c"])),
                volume=Decimal(str(row["v"])),
            ))
        except (KeyError, TypeError, ValueError):
            raise RuntimeError("hyperliquid candle schema is unrecognized")
    return candles
