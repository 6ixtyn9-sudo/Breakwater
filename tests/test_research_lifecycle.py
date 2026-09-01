from datetime import datetime, timedelta, timezone

from breakwater.research_lifecycle import (
    MONITORED,
    apply_signal_feedback,
    read_book,
    sync_book,
)
from breakwater.validation import ValidatedSlice, write_validated


def validated_row(
    mean=0.001,
    n=80,
    validated=True,
    side="LONG",
    *,
    slice_id="feat:0:LONG",
    horizon_bars=1,
):
    return ValidatedSlice(
        slice_id=slice_id,
        kind="SPOT",
        feature="feat",
        state=0,
        side=side,
        folds=5,
        walk_forward_pass_pattern="11111",
        walk_forward_pass_count=5,
        fold_mean_rets="0.001,0.001,0.001,0.001,0.001",
        fold_sizes="20,20,20,20,20",
        n=n,
        mean_ret_costadj=mean,
        p_value=0.001,
        validated=validated,
        horizon_bars=horizon_bars,
    )


def test_sync_book_promotes_validated_slices(tmp_path):
    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"
    write_validated(validated_path, [validated_row()])
    summary = sync_book(validated_path=validated_path, book_path=book_path)
    assert summary["monitored"] == 1
    rows = read_book(book_path)
    assert rows[0]["status"] == MONITORED
    assert rows[0]["slice_id"] == "feat:0:LONG"


def test_sync_book_skips_too_few_rows(tmp_path):
    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"
    write_validated(validated_path, [validated_row(n=30)])
    summary = sync_book(validated_path=validated_path, book_path=book_path)
    assert summary["monitored"] == 0


def test_sync_book_multi_horizon_gate_promotes_only_if_two_horizons_pass(tmp_path, monkeypatch):
    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE", "0")
    monkeypatch.setenv("BREAKWATER_PROMOTION_MULTI_HORIZON_MIN_PASSES", "2")
    monkeypatch.setenv("BREAKWATER_PROMOTION_MULTI_HORIZON_SELECT", "edge_per_bar")

    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"

    rows = [
        validated_row(slice_id="feat:0:LONG:h6", horizon_bars=6, mean=0.00120),
        validated_row(slice_id="feat:0:LONG:h12", horizon_bars=12, mean=0.00130),
    ]
    write_validated(validated_path, rows)

    summary = sync_book(validated_path=validated_path, book_path=book_path)
    assert summary["monitored"] == 1

    book = read_book(book_path)
    assert len(book) == 1
    # edge_per_bar prefers h6 here (0.0012/6 > 0.0013/12)
    assert book[0]["slice_id"] == "feat:0:LONG:h6"


def test_sync_book_multi_horizon_gate_filters_thin_single_horizon(tmp_path, monkeypatch):
    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE", "0")
    monkeypatch.setenv("BREAKWATER_PROMOTION_MULTI_HORIZON_MIN_PASSES", "2")
    monkeypatch.setenv("BREAKWATER_PROMOTION_MULTI_HORIZON_SELECT", "edge_per_bar")

    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"

    write_validated(validated_path, [validated_row(slice_id="feat:0:LONG:h6", horizon_bars=6, mean=0.00120)])
    summary = sync_book(validated_path=validated_path, book_path=book_path)
    assert summary["monitored"] == 0
    assert read_book(book_path) == []


def test_sync_book_multi_horizon_gate_does_not_wipe_existing_kind(tmp_path, monkeypatch):
    """If a kind has promotable rows but fails the multi-horizon gate, it must carry forward."""
    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE", "0")
    monkeypatch.setenv("BREAKWATER_PROMOTION_MULTI_HORIZON_MIN_PASSES", "2")
    monkeypatch.setenv("BREAKWATER_PROMOTION_MULTI_HORIZON_SELECT", "edge_per_bar")

    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"

    from breakwater.research_lifecycle import _write_book

    existing_row = {
        "slice_id": "feat:0:LONG",
        "kind": "SPOT",
        "feature": "feat",
        "state": "0",
        "side": "LONG",
        "status": "monitored",
        "validated_at": "",
        "last_signal_bar": "",
        "paper_trades": "7",
        "paper_wins": "3",
        "paper_losses": "4",
        "paper_pnl_zar": "-0.10",
        "cooldown_until": "",
        "mean_ret_costadj": "0.001000",
        "n": "100",
        "p_value": "0.000001",
        "horizon_bars": "1",
        "stop_atr_mult": "2.000",
        "source": "validated_walk_forward",
        "hostile_unproven": "False",
    }
    _write_book(book_path, [existing_row])

    # One promotable horizon validates, but fails multi-horizon gate (min_passes=2).
    write_validated(validated_path, [validated_row(slice_id="feat:0:LONG:h6", horizon_bars=6, mean=0.00120)])

    summary = sync_book(validated_path=validated_path, book_path=book_path)
    assert summary["monitored"] == 0
    rows = read_book(book_path)
    assert len(rows) == 1
    assert rows[0]["slice_id"] == "feat:0:LONG"
    assert rows[0]["paper_trades"] == "7"


def test_sync_book_demotes_stale_monitored_slices(tmp_path):
    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"
    write_validated(validated_path, [validated_row()])
    sync_book(validated_path=validated_path, book_path=book_path)
    now = datetime.now(timezone.utc)
    apply_signal_feedback(
        book_path,
        "feat:0:LONG",
        bar_epoch=int((now - timedelta(days=10)).timestamp()),
        outcome="win",
        pnl_zar=1.0,
        now=now,
    )
    summary = sync_book(validated_path=validated_path, book_path=book_path, now=now)
    assert summary["decayed"] == 1


def test_stopout_sets_cooldown_then_recovers(tmp_path):
    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"
    write_validated(validated_path, [validated_row()])
    sync_book(validated_path=validated_path, book_path=book_path)
    now = datetime.now(timezone.utc)
    apply_signal_feedback(
        book_path,
        "feat:0:LONG",
        bar_epoch=int(now.timestamp()),
        outcome="loss",
        pnl_zar=-2.0,
        stopout=True,
        now=now,
    )
    rows = read_book(book_path)
    assert rows[0]["status"] == "cooldown"
    assert int(rows[0]["cooldown_until"]) > int(now.timestamp())
    assert rows[0]["paper_losses"] == "1"


def test_book_carries_stop_calibration_and_provenance(tmp_path):
    from breakwater.research_lifecycle import PROVENANCE_VALIDATED

    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"
    write_validated(validated_path, [validated_row()])
    sync_book(validated_path=validated_path, book_path=book_path)
    rows = read_book(book_path)
    assert rows[0]["stop_atr_mult"]
    assert float(rows[0]["stop_atr_mult"]) >= 1.5
    assert rows[0]["source"] == PROVENANCE_VALIDATED


def test_sync_book_preserves_kind_when_validated_but_not_promoted(tmp_path):
    """Regression: if a kind has validated rows, but none pass promotion filters
    (MIN_BOOK_ROWS / min edge), sync_book must NOT wipe that kind's existing book.
    """
    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"

    from breakwater.research_lifecycle import _write_book

    existing_row = {
        "slice_id": "feat:0:LONG",
        "kind": "SPOT",
        "feature": "feat",
        "state": "0",
        "side": "LONG",
        "status": "monitored",
        "validated_at": "",
        "last_signal_bar": "",
        "paper_trades": "7",
        "paper_wins": "3",
        "paper_losses": "4",
        "paper_pnl_zar": "-0.10",
        "cooldown_until": "",
        "mean_ret_costadj": "0.001000",
        "n": "100",
        "p_value": "0.000001",
        "horizon_bars": "1",
        "stop_atr_mult": "2.000",
        "source": "validated_walk_forward",
        "hostile_unproven": "False",
    }
    _write_book(book_path, [existing_row])
    # Validated row exists (so SPOT is "validated") but it cannot promote due to MIN_BOOK_ROWS.
    write_validated(validated_path, [validated_row(n=30, validated=True)])

    summary = sync_book(validated_path=validated_path, book_path=book_path)
    assert summary["validated"] == 1
    assert summary["monitored"] == 0
    assert summary["carried_kinds"] == ["SPOT"]
    rows = read_book(book_path)
    assert len(rows) == 1
    assert rows[0]["slice_id"] == "feat:0:LONG"
    assert rows[0]["paper_trades"] == "7"
    assert rows[0]["status"] == "monitored"


def test_sync_book_preserves_kinds_without_fresh_validation(tmp_path):
    """Standing lesson (rerun wipe): a run that produces no validated rows for
    a kind must not wipe that kind's existing book rows."""
    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"
    from breakwater.research_lifecycle import _write_book

    perp_row = {
        "slice_id": "perp:0:SHORT",
        "kind": "PERP",
        "feature": "feat",
        "state": "0",
        "side": "SHORT",
        "status": "monitored",
        "validated_at": "",
        "last_signal_bar": "",
        "paper_trades": "2",
        "paper_wins": "1",
        "paper_losses": "1",
        "paper_pnl_zar": "-0.50",
        "cooldown_until": "",
        "mean_ret_costadj": "0.002500",
        "n": "120",
        "p_value": "0.000001",
        "horizon_bars": "1",
        "stop_atr_mult": "2.500",
        "source": "validated_walk_forward",
        "hostile_unproven": "False",
    }
    _write_book(book_path, [perp_row])
    write_validated(validated_path, [validated_row()])
    summary = sync_book(validated_path=validated_path, book_path=book_path)
    assert summary["carried_kinds"] == ["PERP"]
    rows = read_book(book_path)
    assert {row["slice_id"] for row in rows} == {"feat:0:LONG", "perp:0:SHORT"}
    carried = next(row for row in rows if row["slice_id"] == "perp:0:SHORT")
    assert carried["paper_trades"] == "2"
    assert carried["status"] == "monitored"


def test_concentrated_promote_takes_fail_only_breadth_fat_family(tmp_path, monkeypatch):
    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE", "0.002")
    monkeypatch.setenv("BREAKWATER_CONCENTRATED_PROMOTE", "1")
    monkeypatch.setenv("BREAKWATER_CONCENTRATED_MIN_MEAN", "0.004")
    monkeypatch.setenv("BREAKWATER_PROMOTION_MULTI_HORIZON_MIN_PASSES", "2")
    monkeypatch.setenv("BREAKWATER_PROMOTION_MULTI_HORIZON_SELECT", "edge_per_bar")

    def fat(slice_id, horizon, mean):
        row = validated_row(mean=mean, n=2200, validated=False, slice_id=slice_id, horizon_bars=horizon)
        return ValidatedSlice(
            **{
                **row.__dict__,
                "temporal_pass": True,
                "direction_ok": True,
                "mean_positive": True,
                "breadth_ok": False,
                "breadth_symbols_used": 17,
                "fail_reasons": "breadth_ok",
                "regime_confounded": False,
            }
        )

    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"
    write_validated(validated_path, [fat("feat:2:LONG:h18", 18, 0.0042), fat("feat:2:LONG:h24", 24, 0.0059)])
    summary = sync_book(validated_path=validated_path, book_path=book_path)
    assert summary["concentrated"] == 2
    assert summary["monitored"] == 1
    book = read_book(book_path)
    assert book[0]["slice_id"] == "feat:2:LONG:h24"
    assert book[0]["source"] == "validated_concentrated"


def test_sync_book_keeps_green_paper_slice_when_kind_promotes_other_family(tmp_path, monkeypatch):
    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE", "0")
    monkeypatch.setenv("BREAKWATER_PROMOTION_MULTI_HORIZON_MIN_PASSES", "1")
    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"
    from breakwater.research_lifecycle import _write_book

    hunt = {
        "slice_id": "feat_ext_vs_ma_50:2:LONG:h21",
        "kind": "PERP",
        "feature": "feat_ext_vs_ma_50",
        "state": "2",
        "side": "LONG",
        "status": "monitored",
        "validated_at": "",
        "last_signal_bar": str(int(datetime.now(timezone.utc).timestamp())),
        "paper_trades": "5",
        "paper_wins": "5",
        "paper_losses": "0",
        "paper_pnl_zar": "34.80",
        "cooldown_until": "",
        "mean_ret_costadj": "0.005465",
        "n": "2282",
        "p_value": "0.65",
        "horizon_bars": "21",
        "stop_atr_mult": "3.500",
        "source": "validated_concentrated",
        "hostile_unproven": "True",
        "edge_is_directional_net": "True",
    }
    _write_book(book_path, [hunt])
    other = validated_row(mean=0.003, n=80, slice_id="other:0:LONG:h6", horizon_bars=6)
    other = ValidatedSlice(**{**other.__dict__, "kind": "PERP"})
    write_validated(validated_path, [other])
    summary = sync_book(validated_path=validated_path, book_path=book_path)
    ids = {row["slice_id"] for row in read_book(book_path)}
    assert "feat_ext_vs_ma_50:2:LONG:h21" in ids
    assert "other:0:LONG:h6" in ids
    assert summary["paper_protected"] == 1


def test_sync_book_never_wipes_on_empty_validated(tmp_path):
    """A totally empty validated file (data failure) leaves the book intact."""
    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"
    from breakwater.research_lifecycle import _write_book

    existing_row = {
        "slice_id": "feat:0:LONG",
        "kind": "SPOT",
        "feature": "feat",
        "state": "0",
        "side": "LONG",
        "status": "monitored",
        "validated_at": "",
        "last_signal_bar": "",
        "paper_trades": "1",
        "paper_wins": "0",
        "paper_losses": "1",
        "paper_pnl_zar": "-1.20",
        "cooldown_until": "",
        "mean_ret_costadj": "0.001000",
        "n": "100",
        "p_value": "0.000001",
        "horizon_bars": "1",
        "stop_atr_mult": "2.000",
        "source": "validated_walk_forward",
        "hostile_unproven": "False",
    }
    _write_book(book_path, [existing_row])
    write_validated(validated_path, [])
    summary = sync_book(validated_path=validated_path, book_path=book_path)
    assert summary["validated"] == 0
    rows = read_book(book_path)
    assert len(rows) == 1
    assert rows[0]["slice_id"] == "feat:0:LONG"
    assert rows[0]["paper_trades"] == "1"


def test_min_net_edge_floor_is_kind_aware(monkeypatch):
    """Spot's floor is driven by its (much higher) cost; perp's by the static bar."""
    from breakwater import research_lifecycle as rl

    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE", "0.002")
    monkeypatch.setenv("BREAKWATER_SPOT_FEE_BPS", "70")
    monkeypatch.setenv("BREAKWATER_PERP_FEE_BPS", "9")
    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE_COST_MULT", "2")
    # Spot: cost term 2 x 70 bps = 140 bps dominates the static 20 bps.
    assert rl._min_net_edge_floor("SPOT") == 0.014
    # Perp: cost term 2 x 9 bps = 18 bps sits below the static 20 bps.
    assert rl._min_net_edge_floor("PERP") == 0.002


def test_min_net_edge_floor_static_bar_raises_perp(monkeypatch):
    from breakwater import research_lifecycle as rl

    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE", "0.004")
    monkeypatch.setenv("BREAKWATER_SPOT_FEE_BPS", "70")
    monkeypatch.setenv("BREAKWATER_PERP_FEE_BPS", "9")
    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE_COST_MULT", "2")
    assert rl._min_net_edge_floor("PERP") == 0.004
    assert rl._min_net_edge_floor("SPOT") == 0.014


def test_min_net_edge_floor_mult_zero_disables_cost_term(monkeypatch):
    from breakwater import research_lifecycle as rl

    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE", "0.002")
    monkeypatch.setenv("BREAKWATER_SPOT_FEE_BPS", "70")
    monkeypatch.setenv("BREAKWATER_PERP_FEE_BPS", "9")
    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE_COST_MULT", "0")
    assert rl._min_net_edge_floor("SPOT") == 0.002
    assert rl._min_net_edge_floor("PERP") == 0.002


def test_pool_edge_floor_percentile():
    from breakwater import research_lifecycle as rl

    pool = list(range(1, 101))
    assert rl._pool_edge_floor(pool, 0.25) == 75  # top 25% of 1..100 starts at 75
    assert rl._pool_edge_floor(pool, 0.0) == 0.0
    assert rl._pool_edge_floor([1, 2, 3], 0.25) == 0.0  # too small to trust


def _perp_row(mean_bps, *, slice_id, validated=False, n=100):
    return ValidatedSlice(
        slice_id=slice_id,
        kind="PERP",
        feature="feat",
        state=0,
        side="LONG",
        folds=5,
        walk_forward_pass_pattern="11111",
        walk_forward_pass_count=5,
        fold_mean_rets="0.001,0.001,0.001,0.001,0.001",
        fold_sizes="20,20,20,20,20",
        n=n,
        mean_ret_costadj=mean_bps / 10000.0,
        p_value=0.001,
        validated=validated,
        horizon_bars=1,
    )


def _autotune_env(monkeypatch):
    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE", "0.002")
    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE_COST_MULT", "0")
    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE_TOP_QUANTILE", "0.25")


def test_autotune_bar_rises_with_a_fat_pool(tmp_path, monkeypatch):
    """Static bar is 20 bps, but the pool's top-25% mark sits at 30 bps, so
    the effective bar rises to 30: a 25 bps slice is refused, 35 bps passes."""
    _autotune_env(monkeypatch)
    pool = (
        [_perp_row(10, slice_id=f"p10:{i}") for i in range(10)]
        + [_perp_row(20, slice_id=f"p20:{i}") for i in range(10)]
        + [_perp_row(30, slice_id=f"p30:{i}") for i in range(10)]
        + [_perp_row(40, slice_id=f"p40:{i}") for i in range(8)]
        + [_perp_row(25, slice_id="mid:25:LONG", validated=True)]
        + [_perp_row(35, slice_id="top:35:LONG", validated=True)]
    )
    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"
    write_validated(validated_path, pool)
    summary = sync_book(validated_path=validated_path, book_path=book_path)
    assert summary["net_edge_floor_enter_bps"]["PERP"] == "30.0"
    assert summary["promotable"] == 1
    rows = read_book(book_path)
    assert [r["slice_id"] for r in rows] == ["top:35:LONG"]


def test_autotune_bar_never_stricter_than_static_in_thin_pool(tmp_path, monkeypatch):
    """A thin pool (top-25% mark ~15 bps) must not tighten the bar below the
    static 20 bps guarantee: the 25 bps slice still promotes."""
    _autotune_env(monkeypatch)
    pool = (
        [_perp_row(5, slice_id=f"t5:{i}") for i in range(13)]
        + [_perp_row(10, slice_id=f"t10:{i}") for i in range(13)]
        + [_perp_row(15, slice_id=f"t15:{i}") for i in range(13)]
        + [_perp_row(25, slice_id="solo:25:LONG", validated=True)]
    )
    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"
    write_validated(validated_path, pool)
    summary = sync_book(validated_path=validated_path, book_path=book_path)
    assert summary["net_edge_floor_enter_bps"]["PERP"] == "20.0"
    assert summary["monitored"] == 1
    assert read_book(book_path)[0]["slice_id"] == "solo:25:LONG"


def test_concentrated_path_respects_cost_linked_floor(monkeypatch):
    """The hunt path must not be a backdoor: a spot edge above the static 40
    bps bar but below the cost-linked 140 bps floor is not promotable."""
    from breakwater import research_lifecycle as rl

    monkeypatch.setenv("BREAKWATER_CONCENTRATED_PROMOTE", "1")
    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE", "0.004")
    monkeypatch.setenv("BREAKWATER_SPOT_FEE_BPS", "70")
    monkeypatch.setenv("BREAKWATER_PERP_FEE_BPS", "9")
    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE_COST_MULT", "2")

    def row(kind):
        # 50 bps net: above the static 40 bps bar, below spot's 140 bps.
        return ValidatedSlice(
            slice_id=f"feat:0:LONG:{kind}",
            kind=kind,
            feature="feat",
            state=0,
            side="LONG",
            folds=5,
            walk_forward_pass_pattern="11111",
            walk_forward_pass_count=5,
            fold_mean_rets="0.001,0.001,0.001,0.001,0.001",
            fold_sizes="400,400,400,400,400",
            n=5000,
            mean_ret_costadj=0.005,
            p_value=0.001,
            validated=False,
            temporal_pass=True,
            direction_ok=True,
            breadth_ok=False,
            breadth_symbols_used=20,
            mean_positive=True,
            fail_reasons="breadth_ok",
        )

    assert rl._is_concentrated_candidate(row("PERP")) is True
    assert rl._is_concentrated_candidate(row("SPOT")) is False


def _hip3_validated_row(slice_id, blended_bps, us_bps):
    return ValidatedSlice(
        slice_id=slice_id,
        kind="PERP",
        feature="feat",
        state=2,
        side="LONG",
        folds=5,
        walk_forward_pass_pattern="11111",
        walk_forward_pass_count=5,
        fold_mean_rets="0.001,0.001,0.001,0.001,0.001",
        fold_sizes="20,20,20,20,20",
        n=2000,
        mean_ret_costadj=blended_bps / 10000.0,
        p_value=0.001,
        validated=True,
        horizon_bars=12,
        session_us_n=4000,
        session_us_mean_ret_costadj=us_bps / 10000.0,
        session_us_hit_rate=0.5,
    )


def test_hip3_promotion_requires_session_matched_edge(tmp_path, monkeypatch):
    """A calendar-asset slice whose edge does not exist in the tradable
    (US) session is not promoted, even when the blended edge passes the
    quality bar. 24/7 classes are unaffected."""
    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE", "0")
    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE_COST_MULT", "0")

    rows = [
        # EU/pre-market-only edge (the realized_vol_20:h12 shape): US 7.0
        # bps is < 50% of the 25.4 bps blend -> session gate refuses.
        _hip3_validated_row("hip3_xyz_equity_c0:feat_a:2:LONG:h12", 25.4, 7.0),
        # Matched edge: US 50.4 of 56.3 blended -> promoted.
        _hip3_validated_row("hip3_xyz_equity_c0:feat_b:1:LONG:h19", 56.3, 50.4),
        # 24/7 class: blended edge IS the tradable edge -> unaffected.
        _hip3_validated_row("hip3_hyna_builder_crypto_c0:feat_c:2:LONG:h6", 25.4, 7.0),
    ]
    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"
    write_validated(validated_path, rows)
    summary = sync_book(validated_path=validated_path, book_path=book_path)

    assert summary["session_gate_blocked"] == 1
    ids = {row["slice_id"] for row in read_book(book_path)}
    assert "hip3_xyz_equity_c0:feat_a:2:LONG:h12" not in ids
    assert "hip3_xyz_equity_c0:feat_b:1:LONG:h19" in ids
    assert "hip3_hyna_builder_crypto_c0:feat_c:2:LONG:h6" in ids


def _asset_edge_row(slice_id="feat:0:LONG", asset="A", mean=0.01, status="green", n=80):
    from breakwater.validation import AssetEdge
    return AssetEdge(slice_id=slice_id, asset=asset, kind="SPOT", feature="feat", state=0,
        side="LONG", horizon_bars=1, n=n, mean_ret_costadj=mean, folds_positive=5,
        folds_with_rows=5, fold_positive_fraction=1.0, asset_status=status, reason="")


def test_sync_book_per_asset_green_breadth_blocks_thin_slice(tmp_path):
    """< MIN_GREEN green assets -> not promoted even though pooled mean passes."""
    from breakwater.research_lifecycle import MIN_GREEN_ASSETS_FOR_PROMOTION
    from breakwater.validation import write_asset_edges
    vp = tmp_path / "validated.csv"
    bp = tmp_path / "book.csv"
    ap = tmp_path / "asset_edges.csv"
    write_validated(vp, [validated_row(mean=0.01)])
    edges = [_asset_edge_row(asset=f"A{i}", mean=0.01, status="green") for i in range(2)]
    edges += [_asset_edge_row(asset=f"B{i}", mean=-0.01, status="blocked") for i in range(8)]
    write_asset_edges(ap, edges)
    s = sync_book(validated_path=vp, book_path=bp)
    assert s["per_asset_aware"] is True and s["monitored"] == 0 and s["blocked_for_green_breadth"] == 1
    assert MIN_GREEN_ASSETS_FOR_PROMOTION > 2 and read_book(bp) == []


def test_sync_book_per_asset_promo_edge_not_pooled(tmp_path, monkeypatch):
    """Green-only mean used, not pooled: slice not promoted when green edge low."""
    from breakwater.validation import write_asset_edges
    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE", "0.004")
    vp = tmp_path / "validated.csv"
    bp = tmp_path / "book.csv"
    ap = tmp_path / "asset_edges.csv"
    write_validated(vp, [validated_row(mean=0.01)])
    edges = [_asset_edge_row(asset=f"A{i}", mean=0.001, status="green") for i in range(5)]
    edges += [_asset_edge_row(asset=f"B{i}", mean=-0.01, status="blocked") for i in range(5)]
    write_asset_edges(ap, edges)
    s = sync_book(validated_path=vp, book_path=bp)
    assert s["monitored"] == 0 and read_book(bp) == []
    pd = tmp_path / "no_asset"
    pd.mkdir()
    vp2 = pd / "validated.csv"
    bp2 = pd / "book.csv"
    write_validated(vp2, [validated_row(mean=0.01)])
    s2 = sync_book(validated_path=vp2, book_path=bp2)
    assert s2["monitored"] == 1


def test_sync_book_per_asset_promotes_and_records_green(tmp_path):
    """Enough green assets + passing green-only edge -> promotes, records n_green."""
    from breakwater.validation import write_asset_edges
    vp = tmp_path / "validated.csv"
    bp = tmp_path / "book.csv"
    ap = tmp_path / "asset_edges.csv"
    write_validated(vp, [validated_row(mean=0.01)])
    edges = [_asset_edge_row(asset=f"A{i}", mean=0.01, status="green") for i in range(6)]
    edges += [_asset_edge_row(asset=f"B{i}", mean=-0.01, status="blocked") for i in range(4)]
    write_asset_edges(ap, edges)
    s = sync_book(validated_path=vp, book_path=bp)
    assert s["monitored"] == 1 and s["green_assets_total"] == 6 and s["promoted_green_fraction_mean"] == 0.6
    rows = read_book(bp)
    assert rows[0]["n_green"] == "6" and rows[0]["green_frac"] == "0.600"
