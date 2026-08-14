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
from breakwater.status import append_status  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command", choices=["guardian", "shadow-scan", "operate", "research"]
    )
    parser.add_argument("--max-pairs", type=int, default=12)
    args = parser.parse_args()
    settings = get_settings()
    try:
        engine = BreakwaterEngine(settings)
        engine.startup_assertions()
        if args.command == "guardian":
            result = engine.guardian()
        elif args.command == "operate":
            result = engine.operational_pass(max_pairs=args.max_pairs)
        elif args.command == "research":
            result = engine.research_pass(max_pairs=30)
        else:
            result = engine.shadow_scan(max_pairs=args.max_pairs)
    except Exception as exc:
        detail = f"{type(exc).__name__}: {exc}"
        try:
            append_status(settings.status_path, "failed", settings.mode, detail)
        except Exception:
            pass
        print(json.dumps({"ok": False, "error": detail}, indent=2))
        return 2 if isinstance(exc, GuardianHalt) else 1
    print(json.dumps({"ok": True, "result": result}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
