from dataclasses import replace
from decimal import Decimal

from breakwater.hip3 import Hip3UniverseRow
from breakwater.hip3_research import (
    MIN_SPREAD_SAMPLES,
    _candidate_rows,
    _hip3_paper_evidence,
    _horizons,
    _methodology_parity,
    _promotion_gate,
    _stratified_select,
    classify_market,
    l2_half_spread_bps,
    measured_round_trip_cost_bps,
)


def row(coin="xyz:NVDA", **changes):
    base = Hip3UniverseRow(
        dex=coin.split(":", 1)[0],
        dex_full_name="DEX",
        deployer="0x1",
        oracle_updater="0x2",
        coin=coin,
        collateral_token=0,
        active=True,
        liquidity_rank=1,
        day_notional_volume=Decimal("100000"),
        mark_price=Decimal("100"),
        oracle_price=Decimal("100"),
        previous_day_price=Decimal("99"),
        oracle_mark_deviation_fraction=Decimal("0"),
        funding_rate=Decimal("0"),
        open_interest=Decimal("10"),
        max_leverage=Decimal("10"),
        size_decimals=3,
        margin_mode="strictIsolated",
        growth_mode="enabled",
        as_of="2026-08-23T00:00:00+00:00",
    )
    return replace(base, **changes)


def test_hip3_default_horizons_match_native_perp_sweep(monkeypatch):
    monkeypatch.delenv("BREAKWATER_HIP3_RESEARCH_HORIZONS", raising=False)
    assert _horizons() == list(range(1, 25))


def test_methodology_parity_reports_drift(monkeypatch):
    expected_env = {
        "BREAKWATER_DISCOVERY_ROLLING_MIN_PERIODS": "200",
        "BREAKWATER_DISCOVERY_STATE_QUANTILES": "0.333333,0.666666",
        "BREAKWATER_VALIDATION_REQUIRE_BONFERRONI": "0",
        "BREAKWATER_VALIDATION_RELAXED_MIN_PASSES": "2",
        "BREAKWATER_VALIDATION_STRICT_PASS_FLOOR": "3",
        "BREAKWATER_BREADTH_MIN_SYMBOLS": "6",
        "BREAKWATER_BREADTH_MIN_ROWS_PER_SYMBOL": "10",
        "BREAKWATER_BREADTH_MIN_POSITIVE_FRACTION": "0.40",
    }
    for name, value in expected_env.items():
        monkeypatch.setenv(name, value)
    parity = _methodology_parity(
        max_pairs=60, candle_count=1000, horizons=list(range(1, 25))
    )
    assert parity["status"] == "parity"
    monkeypatch.setenv("BREAKWATER_BREADTH_MIN_SYMBOLS", "5")
    drifted = _methodology_parity(
        max_pairs=60, candle_count=1000, horizons=list(range(1, 25))
    )
    assert drifted["status"] == "mismatch"
    assert drifted["mismatches"] == ["breadth_min_symbols"]


def test_market_classes_keep_builder_crypto_out_of_equity_pool():
    native = {"BTC", "ETH", "SOL"}
    assert classify_market("hyna:BTC", native) == "builder_crypto"
    assert classify_market("xyz:EUR", native) == "fx"
    assert classify_market("xyz:BRENTOIL", native) == "commodity"
    assert classify_market("xyz:SP500", native) == "index"
    assert classify_market("xyz:NVDA", native) == "provisional_equity"
    assert classify_market("xyz:NVDA", native, "equities") == "equity"
    assert classify_market("xyz:PRIVATE", native, "preipo") == "preipo"
    assert classify_market("hyna:BTC", native, "equities") == "builder_crypto"


def test_research_candidates_fail_closed_on_oracle_and_activity():
    rows = (
        row("xyz:NVDA", day_notional_volume=Decimal("200000")),
        row("hyna:BTC", day_notional_volume=Decimal("300000")),
        row("xyz:TSLA", oracle_mark_deviation_fraction=Decimal("0.03")),
        row("xyz:AMZN", active=False),
        row("xyz:META", day_notional_volume=Decimal("0")),
    )
    candidates = _candidate_rows(
        rows,
        native_crypto={"BTC"},
        max_oracle_deviation=Decimal("0.02"),
    )
    assert [(item.coin, market_class) for item, market_class in candidates] == [
        ("xyz:NVDA", "provisional_equity")
    ]


def _sorted_candidates(rows):
    items = [(r, "provisional_equity") for r in rows]
    return sorted(items, key=lambda item: (-item[0].day_notional_volume, item[0].coin))


def test_stratified_select_represents_small_dexs_within_budget():
    rows = [
        row(f"xyz:S{i}", day_notional_volume=Decimal(v))
        for i, v in enumerate((900, 800, 700, 600, 500, 400, 300))
    ]
    rows.append(row("para:P1", day_notional_volume=Decimal(200)))
    rows.append(row("para:P2", day_notional_volume=Decimal(150)))
    rows.append(row("io:I1", day_notional_volume=Decimal(100)))
    candidates = _sorted_candidates(rows)
    selected = _stratified_select(candidates, max_pairs=5)
    coins = [r.coin for r, _ in selected]
    assert len(coins) == 5
    assert "para:P1" in coins and "para:P2" in coins and "io:I1" in coins
    # The lowest-volume top picks were displaced by the floor picks.
    assert "xyz:S2" not in coins and "xyz:S4" not in coins
    assert coins == [r.coin for r, _ in _stratified_select(candidates, max_pairs=5)]


def test_stratified_select_is_noop_when_all_dexs_already_represented():
    rows = [row(f"xyz:S{i}", day_notional_volume=Decimal(100 - i)) for i in range(5)]
    selected = _stratified_select(_sorted_candidates(rows), max_pairs=3)
    assert [r.coin for r, _ in selected] == ["xyz:S0", "xyz:S1", "xyz:S2"]


def test_stratified_select_never_grows_the_budget():
    rows = [row(f"xyz:S{i}", day_notional_volume=Decimal(900 - i)) for i in range(3)]
    for dex in ("a1", "a2", "a3", "a4"):
        rows.append(row(f"{dex}:C1", day_notional_volume=Decimal(50)))
        rows.append(row(f"{dex}:C2", day_notional_volume=Decimal(40)))
    selected = _stratified_select(_sorted_candidates(rows), max_pairs=3)
    assert len(selected) == 3
    # Volume order is preserved inside the final pick.
    volumes = [r.day_notional_volume for r, _ in selected]
    assert volumes == sorted(volumes, reverse=True)


def test_measured_round_trip_cost_requires_minimum_samples():
    assert measured_round_trip_cost_bps([10.0], base_taker_fee_bps=4.5) is None
    spreads = [10.0] * MIN_SPREAD_SAMPLES
    assert measured_round_trip_cost_bps(spreads, base_taker_fee_bps=4.5) == 29.0
    # The round trip crosses the spread twice and pays the taker fee per leg.
    spreads = [5.0] * MIN_SPREAD_SAMPLES
    assert measured_round_trip_cost_bps(spreads, base_taker_fee_bps=4.5) == 19.0


_EMPTY_EVIDENCE = {
    "closed_trades": 0,
    "pnl_zar": 0.0,
    "ghost_rows": 0,
    "minimum_trades": 25,
}


def _gate_kwargs(**overrides):
    kwargs = dict(
        selected=[(row("xyz:NVDA", annotation_category="equities"), "equity")],
        spread_samples=[],
        assumed_cost_bps=30.0,
        measured_cost_bps=None,
        base_taker_fee_bps=4.5,
        confirmed_collateral_token=None,
        paper_evidence=dict(_EMPTY_EVIDENCE),
    )
    kwargs.update(overrides)
    return kwargs


def test_promotion_gate_reports_all_six_blockers_and_shrinks_on_evidence():
    gate = _promotion_gate(**_gate_kwargs())
    assert len(gate["blockers"]) == 6
    assert not gate["paper_ready"]
    assert not gate["live_ready"]
    assert {b["name"] for b in gate["blockers"]} == {
        "market_classification_not_fully_authoritative",
        "market_calendars_not_enforced",
        "historical_oracle_quality_not_available",
        "effective_costs_not_measured",
        "collateral_tokens_not_resolved",
        "no_hip3_paper_evidence",
    }
    gate2 = _promotion_gate(**_gate_kwargs(confirmed_collateral_token=0))
    assert "market_classification_not_fully_authoritative" not in gate2["paper_unresolved"]
    assert "collateral_tokens_not_resolved" not in gate2["paper_unresolved"]
    gate3 = _promotion_gate(
        **_gate_kwargs(
            confirmed_collateral_token=0,
            measured_cost_bps=29.0,
            spread_samples=[10.0] * MIN_SPREAD_SAMPLES,
        )
    )
    assert gate3["paper_unresolved"] == []
    assert gate3["live_unresolved"] == [
        "market_calendars_not_enforced",
        "historical_oracle_quality_not_available",
        "no_hip3_paper_evidence",
    ]


def test_paper_stage_never_requires_paper_evidence():
    # The deadlock guard: the paper stage arms without its own output.
    gate = _promotion_gate(
        **_gate_kwargs(
            confirmed_collateral_token=0,
            measured_cost_bps=29.0,
            spread_samples=[10.0] * MIN_SPREAD_SAMPLES,
            paper_evidence=dict(_EMPTY_EVIDENCE),
        )
    )
    assert gate["paper_ready"] is True
    assert gate["live_ready"] is False


def test_paper_evidence_blocker_resolves_only_at_threshold_with_profit():
    full = dict(_EMPTY_EVIDENCE, closed_trades=25, ghost_rows=25, pnl_zar=1.0)
    gate = _promotion_gate(
        **_gate_kwargs(confirmed_collateral_token=0, paper_evidence=full)
    )
    assert "no_hip3_paper_evidence" not in gate["live_unresolved"]
    for change in (
        dict(closed_trades=24),
        dict(ghost_rows=24),
        dict(pnl_zar=0.0),
        dict(pnl_zar=-1.0),
    ):
        short = {**full, **change}
        gate = _promotion_gate(
            **_gate_kwargs(confirmed_collateral_token=0, paper_evidence=short)
        )
        assert "no_hip3_paper_evidence" in gate["live_unresolved"], change


def test_hip3_paper_evidence_counts_only_hip3_rows():
    paper = [
        {"slice_id": "hip3_xyz_index_c0:feat_x:1:LONG:h24", "outcome": "win", "pnl_zar": "1.5"},
        {"slice_id": "hip3_xyz_index_c0:feat_x:1:LONG:h24", "outcome": "loss", "pnl_zar": "-0.5"},
        {"slice_id": "feat_x:1:LONG:h24", "outcome": "win", "pnl_zar": "9.9"},
        {"slice_id": "hip3_xyz_index_c0:feat_x:1:LONG:h24", "outcome": "skipped", "pnl_zar": "0"},
    ]
    cf = [
        {"slice_id": "hip3_xyz_index_c0:feat_x:1:LONG:h24", "policy": "target_2r_trail_1r"},
        {"slice_id": "feat_x:1:LONG:h24", "policy": "target_2r_trail_1r"},
    ]
    assert _hip3_paper_evidence(paper, cf) == {
        "closed_trades": 2,
        "pnl_zar": 1.0,
        "ghost_rows": 1,
        "minimum_trades": 25,
    }


def test_promotion_gate_flags_provisional_classification():
    gate = _promotion_gate(
        **_gate_kwargs(selected=[(row("xyz:NVDA"), "provisional_equity")])
    )
    assert "market_classification_not_fully_authoritative" in gate["paper_unresolved"]
    gate = _promotion_gate(
        **_gate_kwargs(selected=[(row("xyz:NVDA", annotation_category="equities"), "equity")])
    )
    assert "market_classification_not_fully_authoritative" not in gate["paper_unresolved"]


def test_l2_half_spread_bps_measures_mid_relative_spread():
    book = {
        "coin": "xyz:NVDA",
        "levels": [[{"px": "100", "sz": "5"}], [{"px": "100.2", "sz": "5"}]],
    }
    value = l2_half_spread_bps(book)
    assert value is not None
    assert abs(value - (0.1 / 100.1) * 10_000) < 1e-9


def test_l2_half_spread_bps_fails_open_on_missing_or_malformed_book():
    assert l2_half_spread_bps(None) is None
    assert l2_half_spread_bps("levels") is None
    assert l2_half_spread_bps({"levels": []}) is None
    assert l2_half_spread_bps({"levels": [[{"px": "100"}]]}) is None
    assert l2_half_spread_bps({"levels": [[], []]}) is None
    assert l2_half_spread_bps({"levels": [[{"px": "abc"}], [{"px": "100"}]]}) is None
    assert l2_half_spread_bps({"levels": [[{"sz": "5"}], [{"px": "100"}]]}) is None
    assert l2_half_spread_bps({"levels": [[{"px": "0"}], [{"px": "100"}]]}) is None
