"""Multi-year offline backtest: fetch data, run H1 (trend + trail) and
H2 (funding carry), write localdata/backtest/{summary.md,*.csv}.

    PYTHONPATH=src python scripts/backtest.py fetch   # populate localdata/backtest/data (gitignored)
    PYTHONPATH=src python scripts/backtest.py run     # score and write results
    PYTHONPATH=src python scripts/backtest.py all

Pre-registered parameters and pass criteria live in breakwater.backtest.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# scripts/breakwater.py shadows the package when this file runs as a script
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from breakwater import backtest  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["fetch", "run", "all"])
    parser.add_argument("--data-root", default="localdata", help="directory holding backtest/ (default: localdata)")
    parser.add_argument("--coins", default=",".join(backtest.UNIVERSE))
    args = parser.parse_args(argv)
    root = Path(args.data_root)
    coins = [c.strip().upper() for c in args.coins.split(",") if c.strip()]
    if args.command in {"fetch", "all"}:
        manifest = backtest.fetch_all(root, coins=coins)
        print(json.dumps(manifest, indent=2))
    if args.command in {"run", "all"}:
        result = backtest.run(root, coins=coins)
        print((root / "backtest" / "summary.md").read_text())
        print(json.dumps({"h1": result["h1"].get("verdict"), "h2": result["h2"].get("verdict")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
