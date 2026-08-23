#!/usr/bin/env python3
"""Rewrite Actions workflows to separate Variables from genuine Secrets.

Run only after the consolidated ``BREAKWATER_MANDATE_JSON`` repository secret
has been created. The script never calls GitHub and never reads secret values;
it only rewrites workflow expressions in the checkout.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ROOT / ".github" / "workflows" / "guardian.yml",
    ROOT / ".github" / "workflows" / "paper.yml",
    ROOT / ".github" / "workflows" / "research.yml",
)

MANDATE_ENV_NAMES = (
    "BREAKWATER_INITIAL_EQUITY_ZAR",
    "BREAKWATER_ABSOLUTE_EQUITY_FLOOR_ZAR",
    "BREAKWATER_MAX_TOTAL_LOSS_ZAR",
    "BREAKWATER_MAX_TOTAL_DRAWDOWN_FRACTION",
    "BREAKWATER_RISK_PER_TRADE_ZAR",
    "BREAKWATER_DAILY_LOSS_LIMIT_ZAR",
    "BREAKWATER_SEVEN_DAY_LOSS_LIMIT_ZAR",
    "BREAKWATER_MAX_AGGREGATE_OPEN_RISK_ZAR",
    "BREAKWATER_MAX_POSITION_NOTIONAL_ZAR",
    "BREAKWATER_MAX_EFFECTIVE_LEVERAGE",
    "BREAKWATER_PERP_LEVERAGE_CAP",
    "BREAKWATER_MAX_POSITIONS",
)

NON_SECRET_NAMES = (
    "BREAKWATER_BREADTH_MIN_POSITIVE_FRACTION",
    "BREAKWATER_BREADTH_MIN_ROWS_PER_SYMBOL",
    "BREAKWATER_BREADTH_MIN_SYMBOLS",
    "BREAKWATER_CONCENTRATED_MIN_MEAN",
    "BREAKWATER_CONCENTRATED_PROMOTE",
    "BREAKWATER_DISCOVERY_STATE_QUANTILES",
    "BREAKWATER_ENABLE_SPOT_MARGIN_SHORTS",
    "BREAKWATER_MIN_NET_EDGE",
    "BREAKWATER_PAPER_ENTRY_MODE",
    "BREAKWATER_PAPER_MAX_AGGREGATE_OPEN_RISK_ZAR",
    "BREAKWATER_PAPER_R_GATE",
    "BREAKWATER_PAPER_SELECTION_MODE",
    "BREAKWATER_PAPER_SESSIONS",
    "BREAKWATER_PERP_CANDLE_COUNT",
    "BREAKWATER_PROMOTION_MULTI_HORIZON_MIN_PASSES",
    "BREAKWATER_PROMOTION_MULTI_HORIZON_SELECT",
    "BREAKWATER_RESEARCH_HORIZONS",
    "BREAKWATER_RESEARCH_HORIZON_BARS",
    "BREAKWATER_RESEARCH_MAX_PAIRS",
    "BREAKWATER_SPOT_CANDLE_COUNT",
    "BREAKWATER_SPOT_MARGIN_ACK",
    "BREAKWATER_VALIDATION_RELAXED_MIN_PASSES",
    "BREAKWATER_VALIDATION_STRICT_PASS_FLOOR",
)

ALLOWED_SECRET_REFERENCES = {
    "VALR_API_KEY",
    "VALR_API_SECRET",
    "BREAKWATER_MANDATE_JSON",
}


def migrate_workflow_text(text: str) -> str:
    for name in NON_SECRET_NAMES:
        text = re.sub(
            rf"secrets\.{name}\s*\|\|\s*vars\.{name}",
            f"vars.{name}",
            text,
        )
    text = text.replace(
        "BREAKWATER_LIVE_ACK: ${{ secrets.BREAKWATER_LIVE_ACK }}",
        "BREAKWATER_LIVE_ACK: ${{ vars.BREAKWATER_LIVE_ACK || 'off' }}",
    )
    text = text.replace(
        "${{ vars.BREAKWATER_PAPER_EQUITY_SEED || "
        "secrets.BREAKWATER_INITIAL_EQUITY_ZAR || '2000' }}",
        "${{ vars.BREAKWATER_PAPER_EQUITY_SEED || '2000' }}",
    )

    lines = text.splitlines()
    output = []
    mandate_added = False
    for line in lines:
        stripped = line.strip()
        if any(stripped.startswith(f"{name}:") for name in MANDATE_ENV_NAMES):
            if not mandate_added:
                indentation = line[: len(line) - len(line.lstrip())]
                output.append(
                    indentation
                    + "BREAKWATER_MANDATE_JSON: ${{ secrets.BREAKWATER_MANDATE_JSON }}"
                )
                mandate_added = True
            continue
        output.append(line)
    migrated = "\n".join(output) + ("\n" if text.endswith("\n") else "")

    referenced_secrets = set(re.findall(r"secrets\.([A-Z0-9_]+)", migrated))
    unexpected = referenced_secrets - ALLOWED_SECRET_REFERENCES
    if unexpected:
        raise RuntimeError(
            "workflow still references non-approved secrets: " + ", ".join(sorted(unexpected))
        )
    return migrated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit nonzero when workflows still need migration; do not write files",
    )
    args = parser.parse_args()
    changed = []
    for path in WORKFLOWS:
        original = path.read_text()
        migrated = migrate_workflow_text(original)
        if migrated != original:
            changed.append(path)
            if not args.check:
                path.write_text(migrated)
    if args.check and changed:
        for path in changed:
            print(path.relative_to(ROOT))
        return 1
    for path in changed:
        print(f"migrated {path.relative_to(ROOT)}")
    if not changed:
        print("Actions configuration is already migrated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
