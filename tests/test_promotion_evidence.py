from datetime import datetime, timezone
from decimal import Decimal

from breakwater.models import Lifecycle
from breakwater.promotion import PromotionEvidence
from breakwater.promotion_evidence import (
    ResearchEvidence,
    build_evidence,
    dedupe_by_signal,
    evaluate,
    load_research_evidence,
    real_closes,
    summarise,
)

HEADER = (
    "closed_at,signal_id,pair,kind,slice_id,side,pnl_zar,outcome,pnl_outcome,"
    "exit_reason,net_r\n"
)


def close(signal_id, pnl, day, reason="target", net_r="1.0"):
    return (
        f"2026-09-{day:02d}T06:00:00+00:00,{signal_id},LINKZAR,SPOT,feat:0:LONG,LONG,"
        f"{pnl},win,win,{reason},{net_r}\n"
    )


def write_ledger(tmp_path, body):
    path = tmp_path / "log.csv"
    path.write_text(HEADER + body)
    return path


def test_real_closes_use_the_gate_population(tmp_path):
    from breakwater.promotion_evidence import read_ledger

    path = write_ledger(
        tmp_path,
        close("s1", 5.0, 1)
        + "2026-09-02T06:00:00+00:00,s2,LINKZAR,SPOT,feat:0:LONG,LONG,0,skipped,,adverse,\n"
        + close("s3", -2.0, 3, reason="stop")
        + close("s4", 3.0, 4, reason="slice_gap"),
    )
    rows = read_ledger(path)
    closes = real_closes(rows)
    # The skipped guard row and the slice_gap fill are both outside the gate's
    # population - the same set daily_print and lane_gate read.
    assert [row["signal_id"] for row in closes] == ["s1", "s3"]


def test_duplicate_signal_closes_are_counted_once():
    closes = [
        {"signal_id": "s1", "closed_at": "2026-09-01T00:00:00+00:00", "pnl_zar": "10"},
        {"signal_id": "s1", "closed_at": "2026-09-02T00:00:00+00:00", "pnl_zar": "10"},
        {"signal_id": "s1", "closed_at": "2026-09-03T00:00:00+00:00", "pnl_zar": "10"},
        {"signal_id": "s2", "closed_at": "2026-09-04T00:00:00+00:00", "pnl_zar": "-4"},
    ]
    deduped = dedupe_by_signal(closes)
    assert len(deduped) == 2
    card = summarise(deduped)
    assert card.trades == 2
    assert card.net_zar == 6.0
    # The raw figure is still available and still bigger: 30 - 4 = 26.
    assert summarise(closes).net_zar == 26.0


def test_scorecard_reports_profit_factor_drawdown_and_span():
    closes = [
        {"signal_id": "a", "closed_at": "2026-09-01T00:00:00+00:00", "pnl_zar": "100", "net_r": "2"},
        {"signal_id": "b", "closed_at": "2026-09-05T00:00:00+00:00", "pnl_zar": "-50", "net_r": "-1"},
        {"signal_id": "c", "closed_at": "2026-09-16T00:00:00+00:00", "pnl_zar": "25", "net_r": "0.5"},
    ]
    card = summarise(closes, seed_zar=1000.0)
    assert card.trades == 3
    assert card.wins == 2
    assert card.losses == 1
    assert card.net_zar == 75.0
    assert round(card.expectancy_zar, 4) == 25.0
    assert round(card.profit_factor, 4) == 2.5
    assert card.shadow_days == 15
    # Equity: 1100 -> 1050 -> 1075. Drawdown from the 1100 peak is 50/1100.
    assert round(card.max_drawdown, 6) == round(50 / 1100, 6)
    assert round(card.mean_net_r, 4) == 0.5


def test_evidence_maps_research_fields_and_leaves_canary_counters_at_zero():
    card = summarise(
        [
            {"signal_id": "a", "closed_at": "2026-09-01T00:00:00+00:00", "pnl_zar": "5"},
            {"signal_id": "b", "closed_at": "2026-09-04T00:00:00+00:00", "pnl_zar": "5"},
        ]
    )
    evidence = build_evidence(
        strategy_id="paper:feat:0:LONG",
        card=card,
        research=ResearchEvidence(observations=9000, fold_windows=5, fold_passes=3),
    )
    assert evidence.backtest_trades == 9000
    assert evidence.validation_trades == 2
    assert evidence.walk_forward_windows == 5
    assert evidence.walk_forward_passes == 3
    assert evidence.shadow_trades == 2
    assert evidence.shadow_expectancy == Decimal("5.0")
    # Paper cannot manufacture the live counters.
    assert evidence.reconciliation_passes == 0
    assert evidence.protection_passes == 0


def test_live_capped_is_unreachable_on_paper_evidence_alone():
    card = summarise(
        [
            {
                "signal_id": f"s{i}",
                "closed_at": f"2026-09-{i + 1:02d}T00:00:00+00:00",
                "pnl_zar": "10",
            }
            for i in range(15)
        ]
    )
    evidence = build_evidence(
        strategy_id="paper:feat:0:LONG",
        card=card,
        research=ResearchEvidence(observations=9000, fold_windows=5, fold_passes=3),
    )
    # Even a clean 15-day, 15-trade record with good expectancy stops at
    # shadow_validated: the reconciliation and protection counters belong to
    # the live canary.
    decision = evaluate(evidence, live_armed=True)
    assert decision.lifecycle is Lifecycle.SHADOW_VALIDATED
    assert "fewer than 20 reconciliation passes" in decision.reasons

    armed = evaluate(evidence, live_armed=False)
    assert armed.lifecycle is Lifecycle.SHADOW_VALIDATED


def test_short_shadow_history_is_named_exactly():
    card = summarise(
        [
            {
                "signal_id": f"s{i}",
                "closed_at": f"2026-09-{i + 1:02d}T00:00:00+00:00",
                "pnl_zar": "10",
            }
            for i in range(12)
        ]
    )
    evidence = build_evidence(
        strategy_id="paper:feat:0:LONG",
        card=card,
        research=ResearchEvidence(observations=9000, fold_windows=5, fold_passes=3),
    )
    decision = evaluate(evidence, live_armed=True)
    assert decision.lifecycle is Lifecycle.SHADOW_CANDIDATE
    assert decision.reasons == ("fewer than 14 shadow days",)


def test_research_evidence_reads_fold_count_not_a_fold_list(tmp_path):
    data = tmp_path / "localdata"
    (data / "research").mkdir(parents=True)
    (data / "research" / "validated_slices.csv").write_text(
        "slice_id,n,folds,walk_forward_pass_pattern,walk_forward_pass_count\n"
        "feat:0:LONG,9964,5,01011,3\n"
    )
    evidence = load_research_evidence(data)
    assert evidence["feat:0:LONG"] == ResearchEvidence(
        observations=9964, fold_windows=5, fold_passes=3
    )


def test_research_evidence_falls_back_to_the_pass_pattern(tmp_path):
    data = tmp_path / "localdata"
    (data / "research").mkdir(parents=True)
    (data / "research" / "validated_slices.csv").write_text(
        "slice_id,n,folds,walk_forward_pass_pattern,walk_forward_pass_count\n"
        "feat:0:LONG,100,,10010,2\n"
    )
    evidence = load_research_evidence(data)
    assert evidence["feat:0:LONG"].fold_windows == 5


def test_promotion_evidence_is_importable_without_a_registry():
    """The module must never require the registry to compute a verdict."""
    assert PromotionEvidence is not None
    assert datetime.now(timezone.utc).tzinfo is not None


def test_registry_writer_records_the_verdict_without_arming_live(tmp_path):
    """A registry row can exist; LIVE_CAPPED still needs the deliberate arm."""
    from breakwater.promotion import PromotionRegistry

    card = summarise(
        [
            {
                "signal_id": f"s{i}",
                "closed_at": f"2026-09-{i + 1:02d}T00:00:00+00:00",
                "pnl_zar": "10",
            }
            for i in range(15)
        ]
    )
    evidence = build_evidence(
        strategy_id="paper:feat:0:LONG",
        card=card,
        research=ResearchEvidence(observations=9000, fold_windows=5, fold_passes=3),
    )
    registry = PromotionRegistry(tmp_path / "promotion_registry.json")
    decision = evaluate(evidence, live_armed=False)
    registry.update(decision, evidence)

    payload = registry.load()
    row = payload["strategies"]["paper:feat:0:LONG"]
    assert row["lifecycle"] == Lifecycle.SHADOW_VALIDATED.value
    assert "fewer than 20 reconciliation passes" in row["reasons"]
    assert row["evidence"]["shadow_trades"] == 15
    # Nothing in the file is live_capped, so live mode stays blocked.
    assert all(
        entry["lifecycle"] != Lifecycle.LIVE_CAPPED.value
        for entry in payload["strategies"].values()
    )
    assert registry.lifecycle("paper:feat:0:LONG") is Lifecycle.SHADOW_VALIDATED
