"""Price-style evidence gates for automatic strategy lifecycle changes."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from breakwater.decimal_utils import D
from breakwater.models import Lifecycle

SCHEMA_VERSION = "breakwater.promotion.v1"


@dataclass(frozen=True)
class PromotionEvidence:
    strategy_id: str
    valr_native: bool
    costs_included: bool
    completed_bar_only: bool
    backtest_trades: int
    validation_trades: int
    walk_forward_windows: int
    walk_forward_passes: int
    net_expectancy: Decimal
    profit_factor: Decimal
    max_drawdown: Decimal
    shadow_trades: int
    shadow_days: int
    shadow_expectancy: Decimal
    reconciliation_passes: int
    protection_passes: int
    unresolved_events: int

    @classmethod
    def from_dict(cls, row: dict) -> "PromotionEvidence":
        return cls(
            strategy_id=str(row["strategy_id"]),
            valr_native=row.get("valr_native") is True,
            costs_included=row.get("costs_included") is True,
            completed_bar_only=row.get("completed_bar_only") is True,
            backtest_trades=int(row.get("backtest_trades", 0)),
            validation_trades=int(row.get("validation_trades", 0)),
            walk_forward_windows=int(row.get("walk_forward_windows", 0)),
            walk_forward_passes=int(row.get("walk_forward_passes", 0)),
            net_expectancy=D(row.get("net_expectancy", 0)),
            profit_factor=D(row.get("profit_factor", 0)),
            max_drawdown=D(row.get("max_drawdown", 1)),
            shadow_trades=int(row.get("shadow_trades", 0)),
            shadow_days=int(row.get("shadow_days", 0)),
            shadow_expectancy=D(row.get("shadow_expectancy", 0)),
            reconciliation_passes=int(row.get("reconciliation_passes", 0)),
            protection_passes=int(row.get("protection_passes", 0)),
            unresolved_events=int(row.get("unresolved_events", 0)),
        )


@dataclass(frozen=True)
class PromotionDecision:
    strategy_id: str
    lifecycle: Lifecycle
    reasons: tuple[str, ...]


class PromotionGate:
    def evaluate(self, evidence: PromotionEvidence, *, live_armed: bool) -> PromotionDecision:
        base_reasons = []
        if not evidence.valr_native:
            base_reasons.append("not validated on VALR-native data")
        if not evidence.costs_included:
            base_reasons.append("fees, spread, slippage and funding not included")
        if not evidence.completed_bar_only:
            base_reasons.append("completed-bar contract not proven")
        if evidence.backtest_trades < 30:
            base_reasons.append("fewer than 30 backtest trades")
        if evidence.validation_trades < 10:
            base_reasons.append("fewer than 10 validation trades")
        if evidence.walk_forward_windows < 3 or evidence.walk_forward_passes < 2:
            base_reasons.append("walk-forward evidence insufficient")
        if evidence.net_expectancy <= 0:
            base_reasons.append("net expectancy is not positive")
        if evidence.profit_factor < Decimal("1.2"):
            base_reasons.append("profit factor below 1.2")
        if evidence.max_drawdown > Decimal("0.20"):
            base_reasons.append("research drawdown above 20 percent")
        if base_reasons:
            return PromotionDecision(
                evidence.strategy_id, Lifecycle.RESEARCH_ONLY, tuple(base_reasons)
            )

        shadow_reasons = []
        if evidence.shadow_trades < 10:
            shadow_reasons.append("fewer than 10 shadow trades")
        if evidence.shadow_days < 14:
            shadow_reasons.append("fewer than 14 shadow days")
        if evidence.shadow_expectancy <= 0:
            shadow_reasons.append("shadow expectancy is not positive")
        if shadow_reasons:
            return PromotionDecision(
                evidence.strategy_id, Lifecycle.SHADOW_CANDIDATE, tuple(shadow_reasons)
            )

        safety_reasons = []
        if evidence.reconciliation_passes < 20:
            safety_reasons.append("fewer than 20 reconciliation passes")
        if evidence.protection_passes < 10:
            safety_reasons.append("fewer than 10 protection checks")
        if evidence.unresolved_events:
            safety_reasons.append("unresolved lifecycle events exist")
        if safety_reasons:
            return PromotionDecision(
                evidence.strategy_id, Lifecycle.SHADOW_VALIDATED, tuple(safety_reasons)
            )
        if not live_armed:
            return PromotionDecision(
                evidence.strategy_id,
                Lifecycle.CANARY_ELIGIBLE,
                ("global live gate is not armed",),
            )
        return PromotionDecision(evidence.strategy_id, Lifecycle.LIVE_CAPPED, ())


class PromotionRegistry:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> dict:
        if not self.path.exists():
            return {"schema_version": SCHEMA_VERSION, "strategies": {}}
        try:
            payload = json.loads(self.path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"promotion registry is unreadable: {exc}") from exc
        if payload.get("schema_version") != SCHEMA_VERSION:
            raise RuntimeError("promotion registry schema is unsupported")
        if not isinstance(payload.get("strategies"), dict):
            raise RuntimeError("promotion registry strategies must be an object")
        return payload

    def lifecycle(self, strategy_id: str) -> Lifecycle:
        row = self.load()["strategies"].get(strategy_id)
        return Lifecycle(row["lifecycle"]) if row else Lifecycle.RESEARCH_ONLY

    def update(self, decision: PromotionDecision, evidence: PromotionEvidence) -> None:
        payload = self.load()
        serialised = asdict(evidence)
        for key, value in list(serialised.items()):
            if isinstance(value, Decimal):
                serialised[key] = str(value)
        payload["strategies"][decision.strategy_id] = {
            "lifecycle": decision.lifecycle.value,
            "reasons": list(decision.reasons),
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            "evidence": serialised,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        temporary.replace(self.path)
