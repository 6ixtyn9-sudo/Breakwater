from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "merge_book_on_conflict.py"
spec = importlib.util.spec_from_file_location("merge_book_on_conflict", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_merge_rows_composition_wins_membership_paper_wins_counters():
    composition = [
        {"slice_id": "A", "kind": "PERP", "status": "monitored", "paper_trades": "0", "paper_pnl_zar": "0", "edge": "9"},
        {"slice_id": "N", "kind": "PERP", "status": "monitored", "paper_trades": "0", "paper_pnl_zar": "0", "edge": "8"},
    ]
    paper = [
        {"slice_id": "A", "kind": "PERP", "status": "cooldown", "paper_trades": "4", "paper_pnl_zar": "-1.5", "cooldown_until": "123", "edge": "1"},
        {"slice_id": "D", "kind": "PERP", "status": "monitored", "paper_trades": "9", "paper_pnl_zar": "-9", "edge": "1"},
    ]
    merged, applied = mod.merge_rows(composition, paper)
    assert [r["slice_id"] for r in merged] == ["A", "N"]
    assert applied == 1
    a, n = merged
    assert a["edge"] == "9" and a["paper_trades"] == "4" and a["paper_pnl_zar"] == "-1.5"
    assert a["status"] == "cooldown" and a["cooldown_until"] == "123"
    assert n["paper_trades"] == "0" and n["status"] == "monitored"


def test_merge_rows_is_keyed_by_kind_and_does_not_import_status_without_cooldown():
    composition = [
        {"slice_id": "A", "kind": "PERP", "status": "decayed", "paper_trades": "4", "paper_pnl_zar": "-5"},
        {"slice_id": "A", "kind": "SPOT", "status": "monitored", "paper_trades": "0", "paper_pnl_zar": "0"},
    ]
    paper = [
        {"slice_id": "A", "kind": "PERP", "status": "monitored", "paper_trades": "5", "paper_pnl_zar": "-6", "cooldown_until": ""},
    ]
    merged, applied = mod.merge_rows(composition, paper)
    assert applied == 1
    perp, spot = merged
    # research's 'decayed' verdict survives; paper only adds counters
    assert perp["status"] == "decayed" and perp["paper_trades"] == "5"
    assert spot["paper_trades"] == "0"


def test_cli_round_trip(tmp_path):
    header = "slice_id,kind,status,paper_trades,cooldown_until,edge\n"
    (tmp_path / "comp.csv").write_text(header + "A,PERP,monitored,0,,9\nN,PERP,monitored,0,,8\n")
    (tmp_path / "paper.csv").write_text(header + "A,PERP,cooldown,2,55,1\nD,PERP,monitored,7,,1\n")
    out = tmp_path / "out.csv"
    rc = mod.main(["--composition", str(tmp_path / "comp.csv"), "--paper-fields", str(tmp_path / "paper.csv"), "--out", str(out)])
    assert rc == 0
    assert out.read_text() == header + "A,PERP,cooldown,2,55,9\nN,PERP,monitored,0,,8\n"
