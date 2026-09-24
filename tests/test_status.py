import csv
import json

import pytest

from breakwater.status import DETAIL_CHAR_LIMIT, _fit_detail, append_status


def test_status_is_bounded_and_keeps_header(tmp_path):
    path = tmp_path / "status.csv"
    for index in range(5):
        append_status(path, "stage", "shadow", str(index), keep=3)
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 3
    assert rows[-1]["detail"] == "4"


def test_malformed_status_schema_fails_closed(tmp_path):
    path = tmp_path / "status.csv"
    path.write_text("wrong,columns\n1,2\n")
    with pytest.raises(RuntimeError, match="unsupported schema"):
        append_status(path, "stage", "shadow")


def test_fit_detail_passes_small_detail_through_untouched():
    assert _fit_detail("4") == "4"
    assert _fit_detail("") == ""
    payload = {"paper": {"closed": 1}, "signals": 3}
    text = json.dumps(payload, sort_keys=True)
    assert _fit_detail(text) == text
    assert _fit_detail(payload) == text


def test_fit_detail_bounds_big_payload_and_names_its_loss():
    # green_gate.blocked_slices is the bulkiest value and (with sorted keys)
    # sits before paper - the old 4000-char cut always destroyed paper. The
    # bound must drop the bulkiest keys instead and say so, so paper survives.
    paper = {"aggregate_risk_cap_zar": "100.0", "closed": 7, "new_signals": 2}
    payload = {
        "errors": 0,
        "signals": 3,
        "paper": paper,
        "green_gate": {
            "blocked_slices": {f"feat_{i:05d}": "slice_pnl=-13.68" for i in range(8000)}
        },
        "pair_errors": [{"pair": f"P{i:05d}USDC", "error": "HTTPError: 429"} for i in range(3000)],
    }
    original = json.dumps(payload, sort_keys=True, default=str)
    assert len(original) > DETAIL_CHAR_LIMIT
    fitted = _fit_detail(original)
    assert len(fitted) <= DETAIL_CHAR_LIMIT
    parsed = json.loads(fitted)  # valid JSON, never cut mid-string
    assert parsed["paper"] == paper
    assert parsed["signals"] == 3
    assert "green_gate" not in parsed
    assert "pair_errors" not in parsed
    assert parsed["_truncated"] == {
        "dropped_keys": ["green_gate", "pair_errors"],
        "original_length": len(original),
    }


def test_fit_detail_stays_valid_json_for_pathological_payloads():
    # One huge value: drop it, keep the rest, and name the loss.
    text = json.dumps({"paper": {"closed": 1}, "blob": "x" * 200_000})
    parsed = json.loads(_fit_detail(text))
    assert parsed["paper"] == {"closed": 1}
    assert parsed["_truncated"] == {
        "dropped_keys": ["blob"],
        "original_length": len(text),
    }
    # Even when every payload key must go, the column is valid JSON that
    # names its own loss.
    text = json.dumps({"only": "z" * 200_000})
    parsed = json.loads(_fit_detail(text))
    assert parsed == {"_truncated": {"dropped_keys": ["only"], "original_length": len(text)}}
    # Oversized non-JSON strings can only be hard-bounded at the limit.
    assert len(_fit_detail("y" * 200_000)) == DETAIL_CHAR_LIMIT


def test_append_status_stores_bounded_valid_json(tmp_path):
    path = tmp_path / "status.csv"
    payload = {
        "signals": 3,
        "paper": {"closed": 7},
        "green_gate": {
            "blocked_slices": {f"feat_{i:05d}": "slice_pnl=-13.68" for i in range(8000)}
        },
    }
    original = json.dumps(payload, sort_keys=True)
    append_status(path, "shadow_scan_done", "shadow", original)
    with path.open(newline="") as handle:
        row = list(csv.DictReader(handle))[-1]
    detail = json.loads(row["detail"])  # valid JSON, never cut mid-string
    assert detail["paper"] == {"closed": 7}
    assert detail["signals"] == 3
    assert detail["_truncated"] == {
        "dropped_keys": ["green_gate"],
        "original_length": len(original),
    }
