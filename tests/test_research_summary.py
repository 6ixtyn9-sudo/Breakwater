"""The merge job must leave a research_done row that describes the merged
files, so the daily print's section 8 is not blind under sharding."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

from test_research_lifecycle import validated_row

from breakwater.config import get_settings
from breakwater.research_lifecycle import sync_book
from breakwater.spread_research import write_spreads
from breakwater.validation import ValidatedSlice, write_asset_edges, write_validated

ROOT = Path(__file__).resolve().parents[1]


def _load_script():
    spec = importlib.util.spec_from_file_location("research_summary", ROOT / "scripts" / "research_summary.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["research_summary"] = module
    spec.loader.exec_module(module)
    return module


def _short_row(slice_id="feat:2:SHORT", mean=0.0012):
    return ValidatedSlice(**{**validated_row(mean=mean, validated=False, side="SHORT", slice_id=slice_id).__dict__, "fail_reasons": "mean_net<=0"})


def _seed(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("BREAKWATER_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("BREAKWATER_RESEARCH_SHARD", raising=False)
    research = tmp_path / "research"
    research.mkdir(parents=True)
    rows = [
        validated_row(),
        validated_row(slice_id="feat:1:LONG:h24", horizon_bars=24, validated=False),
        _short_row(),
    ]
    write_validated(research / "validated_slices.csv", rows)
    with (research / "discovered_slices.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["slice_id", "kind", "side"])
        writer.writeheader()
        writer.writerows([{"slice_id": r.slice_id, "kind": r.kind, "side": r.side} for r in rows])
    write_spreads(research / "spread_slices.csv", [])
    # Book first: an asset_edges file beside the pool makes sync_book
    # per-asset-aware and an empty one would block every promotion.
    sync_book(validated_path=research / "validated_slices.csv", book_path=research / "monitored_slices.csv")
    write_asset_edges(research / "asset_edges.csv", [])
    monkeypatch.setenv("BREAKWATER_MODE", "readonly")
    return get_settings()


def test_build_payload_describes_merged_files(tmp_path, monkeypatch):
    settings = _seed(tmp_path, monkeypatch)
    module = _load_script()
    payload = module.build_payload(settings)
    assert payload["source"] == "merged_shards"
    assert payload["discovered_slices"] == 3
    assert payload["validated_slices"] == 1
    assert payload["validated_by_kind_side"] == {"SPOT:LONG": 1}
    assert payload["research_horizons"] == [1, 24]
    assert payload["short_audit"]["shorts_discovered"] == 1
    assert payload["short_audit"]["shorts_passing"] == 0
    assert payload["short_audit"]["best_failing_short_fail_reasons"] == "mean_net<=0"
    assert payload["spread_research"] == {"rows": 0, "qualifying": 0, "best": []}
    assert payload["book"]["rows"] == 1 and payload["book"]["in_validated_pool"] == 1
    assert payload["frame_errors"] == "not propagated from shards"
    # Must fit the status detail cap with room to spare.
    assert len(json.dumps(payload)) < 8000


def test_main_appends_once_per_merged_file_set(tmp_path, monkeypatch, capsys):
    settings = _seed(tmp_path, monkeypatch)
    module = _load_script()
    assert module.main() == 0
    assert module.main() == 0
    rows = [r for r in csv.DictReader(settings.status_path.open(newline="")) if r["stage"] == "research_done"]
    assert len(rows) == 1
    detail = json.loads(rows[0]["detail"])
    assert detail["validated_slices"] == 1
    out = capsys.readouterr().out
    assert "appended research_done" in out and "already current" in out


def test_main_is_a_noop_without_merged_files(tmp_path, monkeypatch):
    monkeypatch.setenv("BREAKWATER_DATA_DIR", str(tmp_path))
    module = _load_script()
    assert module.main() == 0
    assert not (tmp_path / "status.csv").exists()


def test_commit_state_runs_research_summary_for_research_role():
    text = (ROOT / "scripts" / "commit_state.sh").read_text()
    assert "scripts/research_summary.py" in text
    assert "localdata/research/spread_slices.csv" in text


def test_backfill_slice_memory_seeds_from_trade_log_without_overwriting(tmp_path):
    spec = importlib.util.spec_from_file_location("backfill_slice_memory", ROOT / "scripts" / "backfill_slice_memory.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    from breakwater.research_lifecycle import _write_memory, read_memory

    research = tmp_path / "research"
    research.mkdir()
    with (research / "paper_trade_log.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["closed_at", "slice_id", "kind", "outcome", "exit_reason", "pnl_zar"])
        writer.writeheader()
        writer.writerows([
            {"closed_at": "2026-10-01T00:00", "slice_id": "a:0:LONG:h12", "kind": "PERP", "outcome": "loss", "exit_reason": "stop", "pnl_zar": "-4"},
            {"closed_at": "2026-10-02T00:00", "slice_id": "a:0:LONG:h12", "kind": "PERP", "outcome": "win", "exit_reason": "target", "pnl_zar": "1"},
            {"closed_at": "2026-10-03T00:00", "slice_id": "a:0:LONG:h12", "kind": "PERP", "outcome": "loss", "exit_reason": "horizon", "pnl_zar": "-2"},
            {"closed_at": "2026-10-03T00:00", "slice_id": "a:0:LONG:h12", "kind": "SPOT", "outcome": "win", "exit_reason": "target", "pnl_zar": "9"},
            {"closed_at": "2026-10-03T00:00", "slice_id": "b:1:LONG:h24", "kind": "PERP", "outcome": "loss", "exit_reason": "not_book", "pnl_zar": "-9"},
        ])
    _write_memory(research / "slice_memory.csv", {("a:0:LONG:h12", "SPOT"): {
        "slice_id": "a:0:LONG:h12", "kind": "SPOT", "paper_trades": "7", "times_dropped": "2",
    }})
    added, total = module.backfill(research)
    assert (added, total) == (1, 2)
    memory = read_memory(research / "slice_memory.csv")
    perp = memory[("a:0:LONG:h12", "PERP")]
    assert (perp["paper_trades"], perp["paper_wins"], perp["paper_losses"], perp["paper_pnl_zar"]) == ("3", "1", "2", "-5.0000")
    assert perp["last_drop_reason"] == "backfilled_from_trade_log"
    assert memory[("a:0:LONG:h12", "SPOT")]["paper_trades"] == "7"  # existing entry untouched
    assert ("b:1:LONG:h24", "PERP") not in memory  # not_book exits are not real closes
    assert module.backfill(research) == (0, 2)
