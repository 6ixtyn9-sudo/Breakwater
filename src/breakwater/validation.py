"""Walk-forward validation of discovered slices.

Pooled research rows are split into contiguous time folds. A slice passes a
fold when that fold carries enough rows and its mean cost-adjusted forward
return keeps the slice's sign. A slice is validated only when most folds
pass and the most recent fold passes, so the evidence includes recency.

Standing lesson (regime confound): chronological folds cannot tell a
durable price-state edge from a regime artifact. Every slice is therefore
also tested against HOSTILE regime rows: bear rows for long slices, bull
rows for short slices. A slice whose hostile-regime mean return opposes
its side is marked regime-confounded and is not validated.

Session audit (UTC): if `session_utc` exists in prepared rows, validation
outputs per-session n/mean/hit-rate for each slice (audit-only; does not
change validation decisions).
"""

from __future__ import annotations

import csv
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd


VALIDATED_HEADERS = [
    "slice_id",
    "kind",
    "feature",
    "state",
    "side",
    "folds",
    "walk_forward_pass_pattern",
    "walk_forward_pass_count",
    "fold_mean_rets",
    "fold_sizes",
    "n",
    "mean_ret_costadj",
    "p_value",
    "validated",
    "horizon_bars",
    "stop_atr_mult",
    "hostile_n",
    "hostile_mean_ret",
    "regime_confounded",
    "hostile_unproven",
    # Session breakdown (UTC; audit-only)
    "session_asia_n",
    "session_asia_mean_ret_costadj",
    "session_asia_hit_rate",
    "session_eu_n",
    "session_eu_mean_ret_costadj",
    "session_eu_hit_rate",
    "session_us_n",
    "session_us_mean_ret_costadj",
    "session_us_hit_rate",
]

MIN_ROWS_PER_FOLD = 20
FOLD_COUNT = 5
HOSTILE_MIN_ROWS = 20
STOP_ATR_FLOOR = 1.5
STOP_ATR_CEIL = 3.5

SESSION_ASIA = "asia"
SESSION_EU = "eu"
SESSION_US = "us"


@dataclass(frozen=True)
class ValidatedSlice:
    slice_id: str
    kind: str
    feature: str
    state: int
    side: str
    folds: int
    walk_forward_pass_pattern: str
    walk_forward_pass_count: int
    fold_mean_rets: str
    fold_sizes: str
    n: int
    mean_ret_costadj: float
    p_value: float
    validated: bool
    horizon_bars: int
    stop_atr_mult: float = 2.0
    hostile_n: int = 0
    hostile_mean_ret: float = 0.0
    regime_confounded: bool = False
    hostile_unproven: bool = False

    # Session breakdown (audit-only)
    session_asia_n: int = 0
    session_asia_mean_ret_costadj: float = 0.0
    session_asia_hit_rate: float = 0.0
    session_eu_n: int = 0
    session_eu_mean_ret_costadj: float = 0.0
    session_eu_hit_rate: float = 0.0
    session_us_n: int = 0
    session_us_mean_ret_costadj: float = 0.0
    session_us_hit_rate: float = 0.0


def _fold_pass(returns: np.ndarray, side: str) -> bool:
    if len(returns) < MIN_ROWS_PER_FOLD:
        return False
    mean = float(np.mean(returns))
    if side == "LONG":
        return mean > 0
    return mean < 0


def _regime_series(frame: pd.DataFrame) -> pd.Series:
    """Per-row bull / bear / neutral / unknown from the SMA-50/200 prior."""
    close = frame["close"].astype(float)
    sma50 = close.rolling(50).mean()
    sma200 = close.rolling(200).mean()
    labels = pd.Series("neutral", index=frame.index)
    labels[(sma50 > sma200) & (close > sma50)] = "bull"
    labels[(sma50 < sma200) & (close < sma50)] = "bear"
    labels[sma200.isna()] = "unknown"
    return labels


def _attach_regime_labels(prepared: pd.DataFrame) -> pd.DataFrame:
    if prepared.empty or "symbol" not in prepared.columns:
        return prepared
    parts = []
    for _, group in prepared.groupby("symbol", sort=False):
        labelled = group.sort_values("start").copy()
        labelled["regime_row"] = _regime_series(labelled)
        parts.append(labelled)
    return pd.concat(parts, ignore_index=True)


def _hostile_regime_check(
    side: str, hostile_returns: np.ndarray
) -> tuple[int, float, bool, bool]:
    """Return (hostile_n, hostile_mean, confounded, unproven).

    A slice is confounded when it has at least HOSTILE_MIN_ROWS hostile rows
    and the hostile-regime mean return opposes the slice's side. When the
    hostile evidence is too thin to test at all, the slice is marked
    hostile_unproven: it may pass temporally, but the audit trail records
    that its regime independence was never demonstrated.
    """
    hostile_n = len(hostile_returns)
    hostile_mean = float(np.mean(hostile_returns)) if hostile_n else 0.0
    if hostile_n < HOSTILE_MIN_ROWS:
        return hostile_n, hostile_mean, False, True
    if side == "LONG":
        return hostile_n, hostile_mean, hostile_mean <= 0, False
    return hostile_n, hostile_mean, hostile_mean >= 0, False


def _calibrate_stop_atr_mult(prepared: pd.DataFrame, candidate, state_column: str) -> float:
    """90th percentile of the slice's adverse-atr distribution, clamped.

    The percentile (not an in-sample optimum) avoids overfitting the stop
    to the worst historical bar; the clamp keeps stops within sane bounds
    for both sleepy and wild symbols.
    """
    mae_col = "fwd_mae_atr" if "fwd_mae_atr" in prepared.columns else "fwd_mae_atr_5"
    if mae_col not in prepared.columns:
        return 2.0
    subset = prepared.dropna(subset=[state_column, mae_col])
    mask = subset[state_column] == candidate.state
    values = subset.loc[mask, mae_col].to_numpy()
    if len(values) < MIN_ROWS_PER_FOLD:
        return 2.0

    percentile = float(np.percentile(values, 90))
    return min(STOP_ATR_CEIL, max(STOP_ATR_FLOOR, percentile))


def _session_stats(
    subset: pd.DataFrame,
    slice_mask: np.ndarray,
    session_label: str,
) -> tuple[int, float, float]:
    if "session_utc" not in subset.columns:
        return 0, 0.0, 0.0
    sess = subset["session_utc"].to_numpy()
    values = subset.loc[(slice_mask & (sess == session_label)).astype(bool), "fwd_ret"].to_numpy()
    n = len(values)
    if n == 0:
        return 0, 0.0, 0.0
    return n, float(np.mean(values)), float(np.mean(values > 0))


def validate_slices(
    prepared: pd.DataFrame,
    candidates,
) -> list[ValidatedSlice]:
    if prepared.empty or not candidates:
        return []
    labelled = _attach_regime_labels(prepared)
    rows = (
        labelled.dropna(subset=["fwd_ret"])
        .sort_values("start")
        .reset_index(drop=True)
    )

    validated: list[ValidatedSlice] = []
    for candidate in candidates:
        state_column = f"state_{candidate.feature}"
        if state_column not in rows.columns:
            continue

        subset = rows.dropna(subset=[state_column])
        mask = (subset[state_column] == candidate.state).to_numpy()

        fold_ids = np.linspace(0, len(subset), FOLD_COUNT + 1).astype(int)
        fold_results = []
        fold_means = []
        fold_sizes = []

        for fold in range(FOLD_COUNT):
            fold_mask = np.zeros(len(subset), dtype=bool)
            fold_mask[fold_ids[fold] : fold_ids[fold + 1]] = True
            fold_returns = subset.loc[(mask & fold_mask).astype(bool), "fwd_ret"].to_numpy()
            passed = _fold_pass(fold_returns, candidate.side)
            fold_results.append("1" if passed else "0")
            fold_means.append(float(np.mean(fold_returns)) if len(fold_returns) else 0.0)
            fold_sizes.append(len(fold_returns))

        pattern = "".join(fold_results)
        pass_count = pattern.count("1")
        latest_passes = pattern[-1] == "1"
        temporal_pass = (
            pass_count >= max(3, int(0.75 * FOLD_COUNT))
            and latest_passes
            and candidate.bonferroni_pass
        )

        hostile_label = "bear" if candidate.side == "LONG" else "bull"
        hostile_mask = mask & (subset["regime_row"].to_numpy() == hostile_label)
        hostile_returns = subset.loc[hostile_mask, "fwd_ret"].to_numpy()
        hostile_n, hostile_mean, confounded, hostile_unproven = _hostile_regime_check(
            candidate.side, hostile_returns
        )

        asia_n, asia_mean, asia_hit = _session_stats(subset, mask, SESSION_ASIA)
        eu_n, eu_mean, eu_hit = _session_stats(subset, mask, SESSION_EU)
        us_n, us_mean, us_hit = _session_stats(subset, mask, SESSION_US)

        validated.append(
            ValidatedSlice(
                slice_id=candidate.slice_id,
                kind=candidate.kind,
                feature=candidate.feature,
                state=candidate.state,
                side=candidate.side,
                folds=FOLD_COUNT,
                walk_forward_pass_pattern=pattern,
                walk_forward_pass_count=pass_count,
                fold_mean_rets=",".join(f"{value:.6f}" for value in fold_means),
                fold_sizes=",".join(str(size) for size in fold_sizes),
                n=candidate.n,
                mean_ret_costadj=candidate.mean_ret_costadj,
                p_value=candidate.p_value,
                validated=temporal_pass and not confounded,
                horizon_bars=candidate.horizon_bars,
                stop_atr_mult=_calibrate_stop_atr_mult(prepared, candidate, state_column),
                hostile_n=hostile_n,
                hostile_mean_ret=hostile_mean,
                regime_confounded=confounded,
                hostile_unproven=hostile_unproven,
                session_asia_n=asia_n,
                session_asia_mean_ret_costadj=asia_mean,
                session_asia_hit_rate=asia_hit,
                session_eu_n=eu_n,
                session_eu_mean_ret_costadj=eu_mean,
                session_eu_hit_rate=eu_hit,
                session_us_n=us_n,
                session_us_mean_ret_costadj=us_mean,
                session_us_hit_rate=us_hit,
            )
        )

    return sorted(validated, key=lambda row: (not row.validated, -row.mean_ret_costadj))


def read_validated(path: Path) -> list[ValidatedSlice]:
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)

        # Backward compatibility: these are optional in older validated files.
        optional = {
            "stop_atr_mult",
            "hostile_n",
            "hostile_mean_ret",
            "regime_confounded",
            "hostile_unproven",
            "session_asia_n",
            "session_asia_mean_ret_costadj",
            "session_asia_hit_rate",
            "session_eu_n",
            "session_eu_mean_ret_costadj",
            "session_eu_hit_rate",
            "session_us_n",
            "session_us_mean_ret_costadj",
            "session_us_hit_rate",
        }
        required = set(VALIDATED_HEADERS) - optional
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise RuntimeError("validated slices file has an unsupported schema")

        fieldnames = set(reader.fieldnames or [])
        has_stop = "stop_atr_mult" in fieldnames
        has_hostile = "hostile_n" in fieldnames
        has_unproven = "hostile_unproven" in fieldnames
        has_session = "session_asia_n" in fieldnames

        rows = []
        for row in reader:
            rows.append(
                ValidatedSlice(
                    slice_id=str(row["slice_id"]),
                    kind=str(row["kind"]),
                    feature=str(row["feature"]),
                    state=int(row["state"]),
                    side=str(row["side"]),
                    folds=int(row["folds"]),
                    walk_forward_pass_pattern=str(row["walk_forward_pass_pattern"]),
                    walk_forward_pass_count=int(row["walk_forward_pass_count"]),
                    fold_mean_rets=str(row["fold_mean_rets"]),
                    fold_sizes=str(row["fold_sizes"]),
                    n=int(row["n"]),
                    mean_ret_costadj=float(row["mean_ret_costadj"]),
                    p_value=float(row["p_value"]),
                    validated=row["validated"] == "True",
                    horizon_bars=int(row["horizon_bars"]),
                    stop_atr_mult=float(row["stop_atr_mult"]) if has_stop else 2.0,
                    hostile_n=int(row["hostile_n"]) if has_hostile else 0,
                    hostile_mean_ret=float(row["hostile_mean_ret"]) if has_hostile else 0.0,
                    regime_confounded=(row.get("regime_confounded") == "True" if has_hostile else False),
                    hostile_unproven=(row.get("hostile_unproven") == "True" if has_unproven else False),
                    session_asia_n=int(row["session_asia_n"]) if has_session and row.get("session_asia_n") else 0,
                    session_asia_mean_ret_costadj=float(row["session_asia_mean_ret_costadj"]) if has_session and row.get("session_asia_mean_ret_costadj") else 0.0,
                    session_asia_hit_rate=float(row["session_asia_hit_rate"]) if has_session and row.get("session_asia_hit_rate") else 0.0,
                    session_eu_n=int(row["session_eu_n"]) if has_session and row.get("session_eu_n") else 0,
                    session_eu_mean_ret_costadj=float(row["session_eu_mean_ret_costadj"]) if has_session and row.get("session_eu_mean_ret_costadj") else 0.0,
                    session_eu_hit_rate=float(row["session_eu_hit_rate"]) if has_session and row.get("session_eu_hit_rate") else 0.0,
                    session_us_n=int(row["session_us_n"]) if has_session and row.get("session_us_n") else 0,
                    session_us_mean_ret_costadj=float(row["session_us_mean_ret_costadj"]) if has_session and row.get("session_us_mean_ret_costadj") else 0.0,
                    session_us_hit_rate=float(row["session_us_hit_rate"]) if has_session and row.get("session_us_hit_rate") else 0.0,
                )
            )
        return rows


def write_validated(path, rows: list[ValidatedSlice]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(row) for row in rows]
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(file_descriptor, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=VALIDATED_HEADERS)
            writer.writeheader()
            writer.writerows(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise
