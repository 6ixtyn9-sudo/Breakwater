"""Skip/guard rows must not live in the committed ledger.

The ledger was 99.85% skip rows (~1 MB/day) and heading for GitHub's 100 MB
blob limit.  Skips go to weekly sidecars, older weeks gzip, and a legacy
mixed ledger is split once, in place, without changing any realised-PnL read.
"""

from __future__ import annotations

import csv
import gzip
from decimal import Decimal

from breakwater.paper_trade import (
    PAPER_LOG_HEADERS,
    _realised_paper_pnl,
    append_log,
    iter_paper_log,
    rotate_skips_out_of_log,
    skip_log_dir,
)


def _row(closed_at, outcome, pnl="0", reason="asset_not_green"):
    row = {h: "" for h in PAPER_LOG_HEADERS}
    row.update({
        "closed_at": closed_at,
        "signal_id": f"sig-{closed_at}-{outcome}",
        "pair": "BTCUSDC",
        "kind": "PERP",
        "slice_id": "feat_ret_1:0:LONG:h12",
        "side": "BUY",
        "notional_zar": "0" if outcome == "skipped" else "100",
        "pnl_zar": pnl,
        "outcome": outcome,
        "exit_reason": reason if outcome == "skipped" else "horizon",
        "entry_guard": reason if outcome == "skipped" else "",
    })
    return row


def _read(path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt", newline="") as h:
            return list(csv.DictReader(h))
    with path.open(newline="") as h:
        return list(csv.DictReader(h))


def test_append_log_routes_skips_to_weekly_sidecar(tmp_path):
    ledger = tmp_path / "research" / "paper_trade_log.csv"
    append_log(ledger, _row("2026-10-16T05:00:00+00:00", "win", "3.5"))
    append_log(ledger, _row("2026-10-16T05:00:00+00:00", "skipped"))
    append_log(ledger, _row("2026-10-16T06:00:00+00:00", "skipped", reason="risk_cap"))
    append_log(ledger, _row("2026-10-16T07:00:00+00:00", "loss", "-1.5"))

    ledger_rows = _read(ledger)
    assert [r["outcome"] for r in ledger_rows] == ["win", "loss"]
    skip_file = skip_log_dir(ledger) / "2026-W42.csv"  # 2026-10-16 is ISO week 42
    skips = _read(skip_file)
    assert [r["exit_reason"] for r in skips] == ["asset_not_green", "risk_cap"]
    assert _realised_paper_pnl(ledger) == Decimal("2.0")


def test_week_rollover_gzips_previous_week(tmp_path):
    ledger = tmp_path / "paper_trade_log.csv"
    append_log(ledger, _row("2026-10-11T23:00:00+00:00", "skipped"))  # Sunday, W41
    append_log(ledger, _row("2026-10-12T00:00:00+00:00", "skipped"))  # Monday, W42
    d = skip_log_dir(ledger)
    assert not (d / "2026-W41.csv").exists()
    assert (d / "2026-W41.csv.gz").exists()
    assert (d / "2026-W42.csv").exists()
    assert len(_read(d / "2026-W41.csv.gz")) == 1
    # Ledger never created: no trades were written.
    assert not ledger.exists()


def test_rotate_legacy_mixed_ledger_is_lossless_and_idempotent(tmp_path):
    ledger = tmp_path / "paper_trade_log.csv"
    rows = [
        _row("2026-09-14T15:30:33+00:00", "skipped"),                   # W38
        _row("2026-09-14T16:30:33+00:00", "win", "4.0"),
        _row("2026-09-20T10:00:00+00:00", "skipped", reason="session"),  # W38 (Sunday)
        _row("2026-10-02T10:00:00+00:00", "loss", "-2.5"),
        _row("2026-10-15T17:00:32+00:00", "skipped", reason="edge_cap"), # W42
    ]
    with ledger.open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=PAPER_LOG_HEADERS)
        w.writeheader()
        w.writerows(rows)
    pnl_before = _realised_paper_pnl(ledger)

    assert rotate_skips_out_of_log(ledger) == 3
    assert [r["outcome"] for r in _read(ledger)] == ["win", "loss"]
    assert _realised_paper_pnl(ledger) == pnl_before == Decimal("1.5")

    d = skip_log_dir(ledger)
    assert sorted(p.name for p in d.iterdir()) == ["2026-W38.csv.gz", "2026-W42.csv"]
    assert [r["exit_reason"] for r in _read(d / "2026-W38.csv.gz")] == ["asset_not_green", "session"]
    assert [r["exit_reason"] for r in _read(d / "2026-W42.csv")] == ["edge_cap"]

    # Second pass: nothing to move, nothing changes.
    assert rotate_skips_out_of_log(ledger) == 0
    assert sorted(p.name for p in d.iterdir()) == ["2026-W38.csv.gz", "2026-W42.csv"]

    # Full journal is still recoverable, oldest month first.
    everything = list(iter_paper_log(ledger, include_skips=True))
    assert len(everything) == 5
    assert [r["outcome"] for r in everything[:2]] == ["win", "loss"]
    assert len(list(iter_paper_log(ledger))) == 2

    # Appending after rotation keeps going into the open month.
    append_log(ledger, _row("2026-10-16T01:00:00+00:00", "skipped"))
    assert len(_read(d / "2026-W42.csv")) == 2


def test_rotate_missing_ledger_is_noop(tmp_path):
    assert rotate_skips_out_of_log(tmp_path / "nope.csv") == 0
