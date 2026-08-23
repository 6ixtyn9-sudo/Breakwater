#!/usr/bin/env python3
"""Breakwater command-line entry point."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from breakwater.config import get_settings  # noqa: E402
from breakwater.engine import BreakwaterEngine, GuardianHalt  # noqa: E402
from breakwater.hip3 import HyperliquidHip3Discovery, write_hip3_universe  # noqa: E402
from breakwater.status import append_status  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=["guardian", "shadow-scan", "operate", "research", "hip3-discover", "health"],
    )
    parser.add_argument("--max-pairs", type=int, default=12)
    args = parser.parse_args()
    settings = None
    try:
        settings = get_settings()
        if args.command == "health":
            result = BreakwaterEngine(settings).health()
        elif args.command == "hip3-discover":
            snapshot = HyperliquidHip3Discovery().discover()
            write_hip3_universe(settings.hip3_universe_path, snapshot)
            result = {
                "as_of": snapshot.as_of,
                "dexs": len(snapshot.dexs),
                "instruments": len(snapshot.rows),
                "active": sum(row.active for row in snapshot.rows),
                "top_by_dex": {
                    dex.name: [
                        row.coin
                        for row in snapshot.rows
                        if row.dex == dex.name and row.active
                    ][:10]
                    for dex in snapshot.dexs
                },
            }
            append_status(
                settings.hip3_status_path,
                "hip3_discovery_done",
                "readonly",
                json.dumps(result, sort_keys=True),
            )
        else:
            engine = BreakwaterEngine(settings)
            engine.startup_assertions()
            if args.command == "guardian":
                result = engine.guardian()
            elif args.command == "operate":
                result = engine.operational_pass(max_pairs=args.max_pairs)
            elif args.command == "research":
                result = engine.research_pass()
            else:
                result = engine.shadow_scan(max_pairs=args.max_pairs)
    except Exception as exc:
        detail = f"{type(exc).__name__}: {exc}"
        if settings is not None:
            try:
                failure_path = (
                    settings.hip3_status_path
                    if args.command == "hip3-discover"
                    else settings.status_path
                )
                append_status(failure_path, "failed", settings.mode, detail)
            except Exception:
                pass
        print(json.dumps({"ok": False, "error": detail}, indent=2))
        return 2 if isinstance(exc, GuardianHalt) else 1
    print(json.dumps({"ok": True, "result": result}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
