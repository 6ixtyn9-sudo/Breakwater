#!/usr/bin/env python3
"""Evaluate versioned strategy evidence and update the promotion registry."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from breakwater.config import get_settings  # noqa: E402
from breakwater.promotion import (  # noqa: E402
    PromotionEvidence,
    PromotionGate,
    PromotionRegistry,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    settings = get_settings()
    payload = json.loads(args.evidence.read_text())
    rows = payload if isinstance(payload, list) else payload.get("strategies", [])
    if not isinstance(rows, list):
        raise RuntimeError("promotion evidence must contain a strategy list")
    gate = PromotionGate()
    registry = PromotionRegistry(settings.registry_path)
    decisions = []
    for row in rows:
        evidence = PromotionEvidence.from_dict(row)
        decision = gate.evaluate(evidence, live_armed=settings.writes_allowed)
        registry.update(decision, evidence)
        decisions.append({
            "strategy_id": decision.strategy_id,
            "lifecycle": decision.lifecycle.value,
            "reasons": list(decision.reasons),
        })
    print(json.dumps(decisions, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
