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
