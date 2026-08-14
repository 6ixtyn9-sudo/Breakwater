from datetime import datetime, timedelta, timezone

from breakwater.research_lifecycle import (
    MONITORED,
    apply_signal_feedback,
    read_book,
    sync_book,
)
from breakwater.validation import ValidatedSlice, write_validated


def validated_row(mean=0.001, n=80, validated=True, side="LONG"):
    return ValidatedSlice(
        slice_id="feat:0:LONG",
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
        horizon_bars=1,
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


def test_sync_book_demotes_stale_monitored_slices(tmp_path):
    validated_path = tmp_path / "validated.csv"
    book_path = tmp_path / "book.csv"
    write_validated(validated_path, [validated_row()])
    sync_book(validated_path=validated_path, book_path=book_path)
    now = datetime.now(timezone.utc)
    apply_signal_feedback(
        book_path, "feat:0:LONG",
        bar_epoch=int((now - timedelta(days=10)).timestamp()),
        outcome="win", pnl_zar=1.0, now=now,
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
        book_path, "feat:0:LONG",
        bar_epoch=int(now.timestamp()),
        outcome="loss", pnl_zar=-2.0, now=now,
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


def test_sync_book_preserves_kinds_without_fresh_validation(tmp_path):
    """Price lesson (rerun wipe): a run that produces no validated rows for
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
        "mean_ret_costadj": "-0.001000",
        "n": "120",
        "p_value": "0.000001",
        "horizon_bars": "1",
        "stop_atr_mult": "2.500",
        "source": "validated_walk_forward",
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
    }
    _write_book(book_path, [existing_row])
    write_validated(validated_path, [])
    summary = sync_book(validated_path=validated_path, book_path=book_path)
    assert summary["validated"] == 0
    rows = read_book(book_path)
    assert len(rows) == 1
    assert rows[0]["slice_id"] == "feat:0:LONG"
    assert rows[0]["paper_trades"] == "1"

