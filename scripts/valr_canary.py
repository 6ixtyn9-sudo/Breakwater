#!/usr/bin/env python3
"""Prove the VALR spot order path, without taking a position.

    # safe: read-only preflight, shows the exact order it would send
    PYTHONPATH=src python3 scripts/valr_canary.py

    # sends two orders that cannot fill, confirms and cancels, leaves nothing
    BREAKWATER_CANARY_ACK=I_ACCEPT_BREAKWATER_CANARY_ORDERS \
      PYTHONPATH=src python3 scripts/valr_canary.py --arm

Dry run is the default and never contacts a write endpoint. Arming needs the
acknowledgement above AND `--arm`, and deliberately does NOT need
`BREAKWATER_MODE=live` — testing the plumbing must not require arming the
strategy. See breakwater.order_canary for why each order is safe by construction.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from breakwater.config import get_settings  # noqa: E402
from breakwater.order_canary import (  # noqa: E402
    CANARY_ACKNOWLEDGEMENT,
    CanaryAborted,
    CanaryResidual,
    canary_ack_ok,
    run_canary,
)
from breakwater.valr import ValrClient, ValrError  # noqa: E402

RECEIPT_NAME = "valr_spot_canary.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--pair", default="XRPZAR", help="VALR spot pair (default XRPZAR)")
    parser.add_argument(
        "--arm",
        action="store_true",
        help="actually place the two canary orders (also needs BREAKWATER_CANARY_ACK)",
    )
    parser.add_argument(
        "--no-receipt", action="store_true", help="do not write the receipt file"
    )
    args = parser.parse_args(argv)

    settings = get_settings()
    if not settings.has_credentials:
        print("VALR_API_KEY and VALR_API_SECRET are not configured.", file=sys.stderr)
        return 2

    armed = args.arm and canary_ack_ok()
    if args.arm and not armed:
        print(
            f"--arm requires BREAKWATER_CANARY_ACK={CANARY_ACKNOWLEDGEMENT}\n"
            f"Running the read-only preflight instead.\n",
            file=sys.stderr,
        )

    # Writes are enabled only for an armed run, and gated on the canary's own
    # acknowledgement rather than the engine's live switch.
    client = ValrClient(
        api_key=settings.api_key,
        api_secret=settings.api_secret,
        allow_writes=armed,
    )

    receipt = None if args.no_receipt else settings.data_dir / RECEIPT_NAME

    print(f"VALR spot order-path canary — {args.pair.upper()}")
    print("mode: ARMED (orders will be sent)" if armed else "mode: dry run (no orders)")
    print()

    try:
        report = run_canary(client, args.pair, armed=armed, receipt_path=receipt)
    except CanaryResidual as exc:
        # The one failure that needs a human right now.
        print(f"\n!! RESIDUAL RISK: {exc}", file=sys.stderr)
        return 3
    except CanaryAborted as exc:
        print(f"ABORTED before sending anything: {exc}", file=sys.stderr)
        return 1
    except ValrError as exc:
        print(f"VALR error: {exc}", file=sys.stderr)
        return 1

    if report.plan is not None:
        # The plan that was actually used, not a second fetch of a moving book.
        print("Order placed (or, in a dry run, the order that would be):")
        for line in report.plan.render():
            print(f"  {line}")
        print()

    for step in report.steps:
        print(f"  {step.render()}")

    if report.proven:
        print("\nProven by this run:")
        for item in report.proven:
            print(f"  + {item}")
    if report.still_unproven:
        print("\nStill unproven (needs a funded canary, not this one):")
        for item in report.still_unproven:
            print(f"  - {item}")

    if report.residual_order_ids:
        print(
            f"\n!! ORDERS STILL OPEN: {report.residual_order_ids}"
            f"\n!! Cancel them in the VALR UI now.",
            file=sys.stderr,
        )
        return 3

    if receipt is not None:
        print(f"\nReceipt: {receipt}")
    print(f"\n{'CANARY GREEN' if report.ok else 'CANARY FAILED'}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
