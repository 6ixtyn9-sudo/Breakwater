import json
from decimal import Decimal

import pytest

from breakwater.models import Lifecycle
from breakwater.promotion import (
    PromotionDecision,
    PromotionEvidence,
    PromotionGate,
    PromotionRegistry,
)


def evidence(**changes):
    values = {
        "strategy_id": "big-wave-ETHUSDTPERP-sell",
        "valr_native": True,
        "costs_included": True,
        "completed_bar_only": True,
        "backtest_trades": 50,
        "validation_trades": 20,
        "walk_forward_windows": 5,
        "walk_forward_passes": 4,
        "net_expectancy": Decimal("0.01"),
        "profit_factor": Decimal("1.5"),
        "max_drawdown": Decimal("0.1"),
        "shadow_trades": 20,
        "shadow_days": 30,
        "shadow_expectancy": Decimal("0.01"),
        "reconciliation_passes": 30,
        "protection_passes": 20,
        "unresolved_events": 0,
    }
    values.update(changes)
    return PromotionEvidence(**values)


def test_strong_evidence_stops_at_canary_when_live_not_armed():
    decision = PromotionGate().evaluate(evidence(), live_armed=False)
    assert decision.lifecycle is Lifecycle.CANARY_ELIGIBLE


def test_strong_evidence_auto_promotes_when_live_is_armed():
    decision = PromotionGate().evaluate(evidence(), live_armed=True)
    assert decision.lifecycle is Lifecycle.LIVE_CAPPED


def test_price_only_evidence_cannot_promote():
    decision = PromotionGate().evaluate(evidence(valr_native=False), live_armed=True)
    assert decision.lifecycle is Lifecycle.RESEARCH_ONLY


def test_unresolved_lifecycle_stays_shadow_validated():
    decision = PromotionGate().evaluate(evidence(unresolved_events=1), live_armed=True)
    assert decision.lifecycle is Lifecycle.SHADOW_VALIDATED


def test_registry_is_atomic_and_round_trips(tmp_path):
    path = tmp_path / "registry.json"
    registry = PromotionRegistry(path)
    decision = PromotionDecision("strategy", Lifecycle.LIVE_CAPPED, ())
    item = evidence(strategy_id="strategy")
    registry.update(decision, item)
    assert registry.lifecycle("strategy") is Lifecycle.LIVE_CAPPED
    assert not path.with_suffix(".json.tmp").exists()


def test_corrupt_registry_fails_closed(tmp_path):
    path = tmp_path / "registry.json"
    path.write_text("not-json")
    with pytest.raises(RuntimeError, match="unreadable"):
        PromotionRegistry(path).load()


def test_wrong_registry_schema_fails_closed(tmp_path):
    path = tmp_path / "registry.json"
    path.write_text(json.dumps({"schema_version": "wrong", "strategies": {}}))
    with pytest.raises(RuntimeError, match="unsupported"):
        PromotionRegistry(path).load()
