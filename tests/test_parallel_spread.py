from breakwater.parallel_spread import (
    ParallelSpreadPaths,
    SpreadRunEvidence,
    evaluate_research_gate,
)


def _run(run_id: str, **overrides) -> SpreadRunEvidence:
    values = {
        "run_id": run_id,
        "spread_id": "feat_vwap_dist:L2S0:h12",
        "kind": "PERP",
        "research_qualifies": True,
        "n_nonoverlap": 31,
        "mean_ret_costadj": 0.0016,
        "t_nonoverlap": 2.1,
        "fold_pass_count": 4,
        "worst_fold_mean": -0.0001,
        "market_corr": -0.1,
        "avg_n_long": 8.0,
        "avg_n_short": 7.0,
        "long_alpha_bps": 2.0,
        "short_alpha_bps": 3.0,
    }
    values.update(overrides)
    return SpreadRunEvidence(**values)


def test_research_gate_requires_three_runs():
    result = evaluate_research_gate([_run("r1"), _run("r2")])
    assert not result.ready
    assert result.reasons == ("need_three_consecutive_runs",)


def test_research_gate_accepts_three_persistent_passing_runs():
    result = evaluate_research_gate([_run("r1"), _run("r2"), _run("r3")])
    assert result.ready
    assert result.reasons == ()


def test_research_gate_fails_closed_on_one_weak_run_or_changed_spread():
    rows = [
        _run("r1"),
        _run("r2", mean_ret_costadj=0.00125),
        _run("r3", spread_id="feat_macd_12_26:L0S2:h24"),
    ]
    result = evaluate_research_gate(rows)
    assert not result.ready
    assert "spread_id_not_persistent" in result.reasons
    assert "run_2_mean_below_15bps" in result.reasons


def test_research_gate_rejects_non_perp_evidence():
    result = evaluate_research_gate(
        [_run("r1"), _run("r2"), _run("r3", kind="HIP3")]
    )
    assert not result.ready
    assert "non_perp_evidence" in result.reasons


def test_research_gate_rejects_unqualified_source_rows():
    result = evaluate_research_gate(
        [_run("r1"), _run("r2", research_qualifies=False), _run("r3")]
    )
    assert not result.ready
    assert "run_2_research_row_not_qualified" in result.reasons


def test_research_gate_fails_closed_on_missing_numeric_evidence():
    rows = [
        _run("r1"),
        _run("r2", mean_ret_costadj=None),
        _run("r3"),
    ]
    result = evaluate_research_gate(rows)
    assert not result.ready
    assert "run_2_invalid_mean_ret_costadj" in result.reasons


def test_parallel_storage_is_disjoint_from_baseline_paths(tmp_path):
    data_dir = tmp_path / "localdata"
    paths = ParallelSpreadPaths.under(data_dir)
    baseline = [
        data_dir / "research" / "paper_trade_log.csv",
        data_dir / "research" / "slice_memory.csv",
        data_dir / "promotion_registry.json",
    ]

    paths.assert_disjoint_from(baseline)
    assert paths.root == data_dir / "parallel_spread"
    assert len(set(paths.files)) == 4
    assert all(path.parent == paths.root for path in paths.files)
