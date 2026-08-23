#!/usr/bin/env python3
"""Staged Hyperliquid testnet native-protection canary.

No action is submitted unless ``open-protected`` or ``close`` is selected and
the exact testnet acknowledgement plus a dedicated agent key are present in
the process environment. Mainnet is not a supported endpoint in this script.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from decimal import ROUND_CEILING, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from breakwater.hyperliquid import HyperliquidReadOnlyVenue  # noqa: E402
from breakwater.hyperliquid_testnet import (  # noqa: E402
    HyperliquidTestnetExecutor,
    ProtectionCanaryPlan,
)
from breakwater.models import Side  # noqa: E402
from breakwater.perp_venue import assess_native_stop_protection  # noqa: E402

STATE_PATH = ROOT / "localdata" / ".hyperliquid-testnet-canary.json"


def _snapshot(address: str) -> int:
    venue = HyperliquidReadOnlyVenue(testnet=True)
    snapshot = venue.account_snapshot(address)
    protection = assess_native_stop_protection(snapshot)
    print(
        json.dumps(
            {
                "network": "testnet",
                "writes_allowed": False,
                "account": snapshot.address,
                "account_value_usdc": str(snapshot.account_value),
                "positions": [
                    {
                        "symbol": position.symbol,
                        "side": position.side.value,
                        "quantity": str(position.quantity),
                        "entry_price": str(position.entry_price),
                        "mark_price": str(position.mark_price),
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
    return 0 if protection.all_protected else 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Hyperliquid testnet mechanism canary")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("inspect", help="read-only testnet account inspection")
    plan_parser = subparsers.add_parser(
        "plan", help="calculate a precision-aligned mock-USDC canary quantity"
    )
    plan_parser.add_argument("--symbol", default="ETHUSDC")
    plan_parser.add_argument("--notional", default="15")

    open_parser = subparsers.add_parser(
        "open-protected", help="open one capped testnet position and attach native SL/TP"
    )
    open_parser.add_argument("--run-id", required=True)
    open_parser.add_argument("--symbol", default="ETHUSDC")
    open_parser.add_argument("--side", choices=["BUY", "SELL"], default="BUY")
    open_parser.add_argument("--quantity", required=True)
    open_parser.add_argument("--stop-fraction", default="0.01")
    open_parser.add_argument("--target-fraction", default="0.02")
    open_parser.add_argument("--max-notional", default="25")
    open_parser.add_argument(
        "--execute",
        action="store_true",
        help="required confirmation; without it no signer is loaded and no action is submitted",
    )

    close_parser = subparsers.add_parser(
        "close", help="market-close and cancel the staged testnet canary"
    )
    close_parser.add_argument("--execute", action="store_true", required=True)
    args = parser.parse_args()

    address = os.getenv("HYPERLIQUID_TESTNET_ACCOUNT_ADDRESS", "").strip()
    if not address:
        raise RuntimeError("HYPERLIQUID_TESTNET_ACCOUNT_ADDRESS is missing")
    if args.command == "inspect":
        return _snapshot(address)
    if args.command == "plan":
        desired_notional = Decimal(args.notional)
        if desired_notional < Decimal("10") or desired_notional > Decimal("25"):
            raise RuntimeError("planned testnet notional must be between 10 and 25 mock USDC")
        venue = HyperliquidReadOnlyVenue(testnet=True)
        normalized = str(args.symbol).upper()
        matches = [
            instrument
            for instrument in venue.instruments()
            if instrument.symbol == normalized and instrument.active
        ]
        if len(matches) != 1:
            raise RuntimeError(f"testnet instrument unavailable: {normalized}")
        instrument = matches[0]
        units = (desired_notional / instrument.mark_price / instrument.size_step).to_integral_value(
            rounding=ROUND_CEILING
        )
        quantity = units * instrument.size_step
        estimated_notional = quantity * instrument.mark_price
        if estimated_notional > Decimal("25"):
            raise RuntimeError("precision-aligned canary would exceed the 25 mock-USDC cap")
        print(
            json.dumps(
                {
                    "network": "testnet",
                    "symbol": instrument.symbol,
                    "mark_price": str(instrument.mark_price),
                    "size_step": str(instrument.size_step),
                    "quantity": str(quantity),
                    "estimated_notional_usdc": str(estimated_notional),
                },
                sort_keys=True,
            )
        )
        return 0

    if not args.execute:
        raise RuntimeError("write command requires --execute")
    executor = HyperliquidTestnetExecutor.from_environment()
    if args.command == "open-protected":
        if STATE_PATH.exists():
            raise RuntimeError("a staged canary record already exists; inspect or close it first")
        plan = ProtectionCanaryPlan(
            run_id=args.run_id,
            symbol=args.symbol,
            side=Side(args.side),
            quantity=Decimal(args.quantity),
            stop_fraction=Decimal(args.stop_fraction),
            target_fraction=Decimal(args.target_fraction),
            max_notional_usdc=Decimal(args.max_notional),
        )
        receipt = executor.open_with_native_protection(plan)
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(
            json.dumps(
                {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "run_id": receipt.run_id,
                    "symbol": receipt.symbol,
                    "entry_order_id": receipt.entry_order_id,
                    "entry_client_order_id": receipt.entry_client_order_id,
                    "stop_client_order_id": receipt.stop_client_order_id,
                    "target_client_order_id": receipt.target_client_order_id,
                    "filled_quantity": str(receipt.filled_quantity),
                    "average_price": str(receipt.average_price),
                    "stop_price": str(receipt.stop_price),
                    "target_price": str(receipt.target_price),
                    "protection_verified": receipt.protection_verified,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        print(STATE_PATH.read_text(), end="")
        return 0

    if not STATE_PATH.exists():
        raise RuntimeError("no staged canary record exists")
    state = json.loads(STATE_PATH.read_text())
    executor.close_and_cancel(
        symbol=str(state["symbol"]),
        stop_client_order_id=str(state["stop_client_order_id"]),
        target_client_order_id=str(state["target_client_order_id"]),
    )
    STATE_PATH.unlink()
    print("Testnet canary position closed, protection orders canceled, account verified flat.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
