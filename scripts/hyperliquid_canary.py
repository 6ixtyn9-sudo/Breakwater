#!/usr/bin/env python3
"""Read-only Hyperliquid readiness canary.

Uses only the public ``HYPERLIQUID_ACCOUNT_ADDRESS``. It does not load a
private key, sign an action, or call the exchange write endpoint.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402

from breakwater.hyperliquid import HyperliquidReadOnlyVenue  # noqa: E402
from breakwater.paper_trade import read_positions  # noqa: E402
from breakwater.perp_venue import assess_native_stop_protection  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Hyperliquid readiness canary")
    parser.add_argument(
        "--testnet",
        action="store_true",
        help="query Hyperliquid testnet rather than mainnet",
    )
    parser.add_argument(
        "--data-dir",
        default=os.getenv("BREAKWATER_DATA_DIR", "localdata"),
        help="Breakwater state directory used only for symbol coverage",
    )
    args = parser.parse_args()
    load_dotenv(ROOT / ".env", override=False)

    configured_network = os.getenv("BREAKWATER_HYPERLIQUID_NETWORK", "mainnet").lower()
    if configured_network not in {"mainnet", "testnet"}:
        raise RuntimeError("BREAKWATER_HYPERLIQUID_NETWORK must be mainnet or testnet")
    testnet = args.testnet or configured_network == "testnet"
    venue = HyperliquidReadOnlyVenue(testnet=testnet)

    print(json.dumps(venue.health(), sort_keys=True))
    positions_path = Path(args.data_dir) / "research" / "paper_positions.json"
    paper_symbols = [
        str(position.get("pair") or "")
        for position in read_positions(positions_path)
        if str(position.get("kind") or "") == "PERP"
    ]
    coverage = venue.coverage(paper_symbols)
    print(
        json.dumps(
            {
                "paper_symbol_coverage": {
                    "tradable": coverage.tradable,
                    "unavailable": coverage.unavailable,
                    "intentionally_excluded": coverage.intentionally_excluded,
                }
            },
            sort_keys=True,
        )
    )

    address = os.getenv("HYPERLIQUID_ACCOUNT_ADDRESS", "").strip()
    if not address:
        print("No HYPERLIQUID_ACCOUNT_ADDRESS configured; account inspection skipped.")
        print("No writes were performed; the Hyperliquid write path remains code-locked.")
        return 0

    snapshot = venue.account_snapshot(address)
    protection = assess_native_stop_protection(snapshot)
    print(
        json.dumps(
            {
                "account": snapshot.address,
                "account_value_usdc": str(snapshot.account_value),
                "withdrawable_usdc": str(snapshot.withdrawable),
                "margin_used_usdc": str(snapshot.total_margin_used),
                "notional_usdc": str(snapshot.total_notional_position),
                "positions": [
                    {
                        "symbol": position.symbol,
                        "side": position.side.value,
                        "quantity": str(position.quantity),
                        "entry": str(position.entry_price),
                        "mark": str(position.mark_price),
                        "liquidation": (
                            str(position.liquidation_price)
                            if position.liquidation_price is not None
                            else None
                        ),
                    }
                    for position in snapshot.positions
                ],
                "open_orders": len(snapshot.open_orders),
                "native_stop_protection": {
                    "all_protected": protection.all_protected,
                    "protected": protection.protected_symbols,
                    "unprotected": protection.unprotected_symbols,
                },
            },
            sort_keys=True,
        )
    )
    print("No writes were performed; the Hyperliquid write path remains code-locked.")
    return 0 if protection.all_protected else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
