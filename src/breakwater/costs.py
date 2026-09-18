"""Venue round-trip costs.

VALR Pro Trading, tier 1, taker both sides
(https://support.valr.com/hc/en-us/articles/360015777451-What-are-VALR-s-charges):

  Spot Fiat Quote (BTCZAR, ETHZAR, ...):  0.350% / side -> 70 bps RT
  Spot Crypto Quote (BTCUSDT, XRPUSDC):   0.100% / side -> 20 bps RT

Hyperliquid native perp base taker is 4.5 bps / side -> 9 bps RT.

A single BREAKWATER_SPOT_FEE_BPS=70 is honest for ZAR and a lie for USDT/USDC.
Research and paper must cost the pair, not the kind.
"""

from __future__ import annotations

import math
import os
from decimal import Decimal, InvalidOperation

FIAT_QUOTES = frozenset({"ZAR", "USD", "EUR", "GBP", "AUD", "CAD", "JPY", "CHF", "NGN"})
CRYPTO_QUOTES = frozenset({"USDT", "USDC", "BTC", "ETH", "USDC.E"})


def _env_float(name: str, default: str) -> float:
    try:
        value = float(os.getenv(name, default))
    except (TypeError, ValueError):
        value = float(default)
    return value if math.isfinite(value) and value >= 0 else float(default)


def _env_decimal(name: str, default: str) -> Decimal:
    try:
        value = Decimal(str(os.getenv(name, default)))
    except (InvalidOperation, TypeError, ValueError):
        value = Decimal(default)
    return value if value.is_finite() and value >= 0 else Decimal(default)


def quote_of(symbol: str) -> str:
    text = str(symbol or "").upper().replace("/", "")
    for quote in ("USDT", "USDC", "USD", "ZAR", "EUR", "GBP", "BTC", "ETH"):
        if text.endswith(quote) and len(text) > len(quote):
            return quote
    return ""


def is_fiat_quoted(symbol: str) -> bool:
    quote = quote_of(symbol)
    return quote in FIAT_QUOTES or quote == "USD"


def spot_round_trip_bps(symbol: str | None = None) -> float:
    """Taker-taker round trip in bps for a VALR spot pair."""
    fiat = _env_float("BREAKWATER_SPOT_FEE_BPS", "70")
    crypto = _env_float("BREAKWATER_SPOT_CRYPTO_FEE_BPS", "20")
    if not symbol:
        return fiat
    return fiat if is_fiat_quoted(symbol) else crypto


def spot_round_trip_decimal(symbol: str | None = None) -> Decimal:
    fiat = _env_decimal("BREAKWATER_SPOT_FEE_BPS", "70")
    crypto = _env_decimal("BREAKWATER_SPOT_CRYPTO_FEE_BPS", "20")
    if not symbol:
        return fiat
    return fiat if is_fiat_quoted(symbol) else crypto


def perp_round_trip_bps() -> float:
    return _env_float("BREAKWATER_PERP_FEE_BPS", "9")


def kind_round_trip_bps(kind: str, symbol: str | None = None) -> float:
    if str(kind).strip().upper() == "SPOT":
        return spot_round_trip_bps(symbol)
    return perp_round_trip_bps()
