import numpy as np
import pandas as pd

from breakwater.discovery import SliceStat, prepare_pooled
from breakwater.validation import (
    FOLD_COUNT,
    read_validated,
    validate_slices,
    write_validated,
)


def rising_frame(n=400):
    rng = np.random.default_rng(5)
    close = 100 + np.cumsum(np.full(n, 0.02)) + rng.normal(0, 0.05, n)
    return pd.DataFrame({
        "start": pd.date_range("2026-06-01", periods=n, freq="h", tz="UTC"),
        "symbol": "RISER",
        "open": close - 0.2,
        "high": close + 0.4,
        "low": close - 0.4,
        "close": close,
        "volume": rng.uniform(10, 50, n),
    })


def candidate(kind="SPOT", state=0, side="LONG"):
    return SliceStat(
        slice_id=f"close:{state}:{side}",
        kind=kind,
        feature="close",
        state=state,
        side=side,
        n=200,
        mean_ret_costadj=0.001 if side == "LONG" else -0.001,
        median_ret_costadj=0.001,
        hit_rate=0.6,
        t_stat=4.0,
        p_value=0.0001,
        bonferroni_pass=True,
        horizon_bars=1,
    )


def test_validated_slice_with_consistent_rising_returns():
    frame = rising_frame()
    prepared = prepare_pooled(frame, ["close"], cost_bps=0.0, horizon_bars=1)
    rows = validate_slices(prepared, [candidate(state=0, side="LONG")])
    assert rows
    assert rows[0].folds == FOLD_COUNT
    assert len(rows[0].walk_forward_pass_pattern) == FOLD_COUNT


def test_validation_requires_latest_fold_pass():
    frame = rising_frame()
    prepared = prepare_pooled(frame, ["close"], cost_bps=0.0, horizon_bars=1)
    rows = validate_slices(prepared, [candidate(state=0, side="SHORT")])
    if rows:
        assert rows[0].validated is False


def test_validated_roundtrip_through_csv(tmp_path):
    frame = rising_frame()
    prepared = prepare_pooled(frame, ["close"], cost_bps=0.0, horizon_bars=1)
    rows = validate_slices(prepared, [candidate(state=0, side="LONG")])
    path = tmp_path / "validated.csv"
    write_validated(path, rows)
    loaded = read_validated(path)
    assert len(loaded) == len(rows)
    assert loaded[0].slice_id == rows[0].slice_id
    assert loaded[0].walk_forward_pass_pattern == rows[0].walk_forward_pass_pattern


def test_stop_atr_mult_is_calibrated_within_bounds():
    frame = rising_frame()
    prepared = prepare_pooled(frame, ["close"], cost_bps=0.0, horizon_bars=1)
    assert "fwd_mae_atr_5" in prepared.columns
    rows = validate_slices(prepared, [candidate(state=0, side="LONG")])
    assert rows
    assert 1.5 <= rows[0].stop_atr_mult <= 3.5


def test_read_validated_tolerates_legacy_schema_without_stop_column(tmp_path):
    frame = rising_frame()
    prepared = prepare_pooled(frame, ["close"], cost_bps=0.0, horizon_bars=1)
    rows = validate_slices(prepared, [candidate(state=0, side="LONG")])
    path = tmp_path / "validated.csv"
    write_validated(path, rows)
    import csv

    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        legacy_headers = [name for name in reader.fieldnames if name != "stop_atr_mult"]
        legacy_rows = [
            {name: value for name, value in row.items() if name != "stop_atr_mult"}
            for row in reader
        ]
    legacy_path = tmp_path / "legacy.csv"
    with legacy_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=legacy_headers)
        writer.writeheader()
        writer.writerows(legacy_rows)
    loaded = read_validated(legacy_path)
    assert len(loaded) == len(rows)
    assert loaded[0].stop_atr_mult == 2.0
