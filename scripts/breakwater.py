#!/usr/bin/env python3
"""Breakwater command-line entry point."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from breakwater.config import get_settings  # noqa: E402
from breakwater.deep_research_audit import run_deep_research_audit  # noqa: E402
from breakwater.engine import BreakwaterEngine, GuardianHalt  # noqa: E402
from breakwater.hip3 import (  # noqa: E402
    HyperliquidHip3Discovery,
    write_hip3_dexs,
    write_hip3_universe,
)
from breakwater.hip3_research import run_hip3_research  # noqa: E402
from breakwater.status import append_status  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=[
            "guardian", "shadow-scan", "operate", "research",
            "hip3-discover", "hip3-research", "deep-research-audit", "health",
        ],
    )
    parser.add_argument("--max-pairs", type=int)
    parser.add_argument("--lane", choices=["native", "hip3", "all"], default="native")
    parser.add_argument("--candle-count", type=int, default=5000)
    parser.add_argument("--output-dir", default="localdata/deep_audit")
    args = parser.parse_args()
    max_pairs = args.max_pairs if args.max_pairs is not None else (
        60 if args.command == "deep-research-audit" else 12
    )
    settings = None
    try:
        settings = get_settings()
        if args.command == "health":
            result = BreakwaterEngine(settings).health()
        elif args.command == "deep-research-audit":
            output_dir = Path(args.output_dir)
            if not output_dir.is_absolute():
                output_dir = Path.cwd() / output_dir
            result = run_deep_research_audit(
                lane=args.lane,
                data_dir=settings.data_dir,
                output_dir=output_dir,
                max_pairs=max(8, min(150, max_pairs)),
                candle_count=max(3000, min(5000, args.candle_count)),
            )
        elif args.command == "hip3-discover":
            snapshot = HyperliquidHip3Discovery().discover()
            write_hip3_universe(settings.hip3_universe_path, snapshot)
            write_hip3_dexs(settings.hip3_dexs_path, snapshot)
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
        elif args.command == "hip3-research":
            result = run_hip3_research(
                universe_path=settings.hip3_universe_path,
                coverage_path=settings.hip3_coverage_path,
                discovered_path=settings.hip3_discovered_path,
                validated_path=settings.hip3_validated_path,
                status_path=settings.hip3_status_path,
                book_path=settings.hip3_book_path,
                gate_path=settings.hip3_gate_path,
                paper_log_path=settings.paper_log_path,
                counterfactual_log_path=(
                    settings.data_dir / "research" / "paper_counterfactual_log.csv"
                ),
            )
        else:
            engine = BreakwaterEngine(settings)
            engine.startup_assertions()
            if args.command == "guardian":
                result = engine.guardian()
            elif args.command == "operate":
                result = engine.operational_pass(max_pairs=max_pairs)
            elif args.command == "research":
                result = engine.research_pass()
            else:
                result = engine.shadow_scan(max_pairs=max_pairs)
    except Exception as exc:
        detail = f"{type(exc).__name__}: {exc}"
        if settings is not None and args.command != "deep-research-audit":
            try:
                failure_path = (
                    settings.hip3_status_path
                    if args.command in {"hip3-discover", "hip3-research"}
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
