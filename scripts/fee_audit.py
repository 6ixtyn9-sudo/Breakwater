#!/usr/bin/env python3
"""One-shot fee audit: the cost model vs. the venue's published schedule
vs. (with VALR credentials) the account's actual fee tier.

Run from the repo root:

    PYTHONPATH=src python3 scripts/fee_audit.py

No network is needed for the public facts. With VALR_API_KEY /
VALR_API_SECRET present (.env or environment) the account's live fee
schedule is printed so the modeled bps can be verified, not assumed.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env", override=False)

MODELED_SPOT = os.getenv("BREAKWATER_SPOT_FEE_BPS", "70")
MODELED_PERP = os.getenv("BREAKWATER_PERP_FEE_BPS", "9")

PUBLISHED = (
    "VALR spot fiat-quoted (BTCZAR ...) tier 1, 0 volume:   taker 35 bps/side  -> 70 bps round trip",
    "VALR spot fiat-quoted tier 2, 50k USDT 30d:            taker 25 bps/side  -> 50 bps round trip",
    "VALR spot fiat-quoted tier 3, 250k USDT 30d:           taker 13 bps/side  -> 26 bps round trip",
    "Hyperliquid perp base tier:                            taker 4.5 bps/side -> 9 bps round trip",
)


def _compact(rows: object) -> list[dict]:
    out: list[dict] = []
    if isinstance(rows, list):
        for row in rows[:25]:
            if isinstance(row, dict):
                picked = {
                    key: row[key]
                    for key in (
                        "instrument",
                        "pair",
                        "currencyPair",
                        "maker_fee",
                        "taker_fee",
                        "makerFee",
                        "takerFee",
                    )
                    if key in row
                }
                if picked:
                    out.append(picked)
    return out


def main() -> int:
    print("== Breakwater cost model (round-trip bps, charged once per closed trade) ==")
    print(f"  SPOT (VALR crypto-ZAR):   modeled {MODELED_SPOT} bps")
    print(f"  PERP (Hyperliquid):       modeled {MODELED_PERP} bps")
    print()
    print("== Published venue schedules (base tier, taker both sides) ==")
    for line in PUBLISHED:
        print(f"  {line}")
    print()

    api_key = os.getenv("VALR_API_KEY", "").strip()
    api_secret = os.getenv("VALR_API_SECRET", "").strip()
    if not (api_key and api_secret):
        print("VALR credentials not found (VALR_API_KEY / VALR_API_SECRET in .env or env).")
        print("Account tier not verified. A paper account with no live volume sits at")
        print("VALR tier 1, where the modeled 70 bps spot round trip is the honest value.")
        return 0

    from breakwater.valr import ValrClient

    client = ValrClient(api_key=api_key, api_secret=api_secret)
    rows = client.trade_fees()
    compact = _compact(rows)
    if compact:
        print("== VALR account fee schedule (live, first 25 rows) ==")
        for row in compact:
            print(f"  {row}")
    else:
        print("== VALR account fee schedule (live, raw) ==")
        print(json.dumps(rows, indent=2)[:4000])
    print()
    print("Compare the taker rate for your *ZAR pairs against the modeled spot bps:")
    print(f"round trip = 2 x taker one-way. Override with BREAKWATER_SPOT_FEE_BPS if it differs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
