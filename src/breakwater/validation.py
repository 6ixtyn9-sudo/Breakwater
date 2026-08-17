"""Walk-forward validation of discovered slices.

Fix (core):
- Validation now scores and validates slices using a stop-aware forward trade model
  matching paper trading for horizon-based slices:
    - Entry at close[t]
    - Stop at +/- stop_atr_mult * ATR(14)
    - Exit at stop if breached within horizon, else exit at close[t+h]
    - Directional gross return minus cost => net return

This replaces the prior close-to-close-only net return metric during validation,
eliminating research/execution mismatch.

No new knobs. CSV schema unchanged.
"""

from __future__ import annotations

import csv
import math
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


def _env_bool(name: str, default: str = "0") -> bool:
    value = str(os.getenv(name, default)).strip().lower()
    return value in {"1", "true", "yes", "y", "on"}


def _coerce_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


REQUIRE_BONFERRONI = _env_bool("BREAKWATER_VALIDATION_REQUIRE_BONFERRONI", "1")
RELAXED_MIN_PASSES = _coerce_int(os.getenv("BREAKWATER_VALIDATION_RELAXED_MIN_PASSES", "4"), 4)


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


def _normal_p(t_stat: float) -> float:
    return 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(t_stat) / math.sqrt(2.0))))


def _fold_pass(net_returns: np.ndarray) -> bool:
    if len(net_returns) < MIN_ROWS_PER_FOLD:
        return False
    # Keep legacy behavior (sign-based); promotion floor already enforces effect size.
    return float(np.mean(net_returns)) > 0.0


def _regime_series(frame: pd.DataFrame) -> pd.Series:
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


def _hostile_regime_check(net_hostile_returns: np.ndarray) -> tuple[int, float, bool, bool]:
    hostile_n = len(net_hostile_returns)
    hostile_mean = float(np.mean(net_hostile_returns)) if hostile_n else 0.0
    if hostile_n < HOSTILE_MIN_ROWS:
        return hostile_n, hostile_mean, False, True
    return hostile_n, hostile_mean, hostile_mean <= 0, False


def _calibrate_stop_atr_mult(prepared: pd.DataFrame, candidate, state_column: str) -> float:
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


def _atr14(df: pd.DataFrame) -> pd.Series:
    close = df["close"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    high_low = high - low
    high_close_prev = (high - close.shift(1)).abs()
    low_close_prev = (low - close.shift(1)).abs()
    true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
    return true_range.rolling(14).mean()


def _trade_net_series_for_candidate(
    subset: pd.DataFrame,
    *,
    side: str,
    horizon_bars: int,
    stop_atr_mult: float,
    cost: float,
) -> pd.Series:
    """Compute per-row stop-aware net returns (directional, cost-adjusted), per symbol."""
    net = pd.Series(np.nan, index=subset.index, dtype=float)

    direction = 1.0 if side == "LONG" else -1.0

    for _, g in subset.groupby("symbol", sort=False):
        g = g.sort_values("start")

        close = g["close"].astype(float)
        high = g["high"].astype(float)
        low = g["low"].astype(float)

        atr = g["atr_14"] if "atr_14" in g.columns else _atr14(g)
        atr = atr.replace(0, np.nan)

        fwd_close = g["fwd_close_h"] if "fwd_close_h" in g.columns else close.shift(-horizon_bars)
        fwd_min_low = g["fwd_min_low_h"] if "fwd_min_low_h" in g.columns else low.rolling(horizon_bars).min().shift(-horizon_bars)
        fwd_max_high = g["fwd_max_high_h"] if "fwd_max_high_h" in g.columns else high.rolling(horizon_bars).max().shift(-horizon_bars)

        if side == "LONG":
            stop = close - stop_atr_mult * atr
            hit = fwd_min_low <= stop
        else:
            stop = close + stop_atr_mult * atr
            hit = fwd_max_high >= stop

        exit_price = np.where(hit.to_numpy(dtype=bool), stop.to_numpy(), fwd_close.to_numpy())
        gross_dir = ((exit_price - close.to_numpy()) / close.to_numpy()) * direction
        net_dir = gross_dir - float(cost)

        series = pd.Series(net_dir, index=g.index)
        net.loc[g.index] = series

    return net


def _session_stats_from_net(
    subset: pd.DataFrame,
    slice_mask: np.ndarray,
    session_label: str,
    net_values: np.ndarray,
) -> tuple[int, float, float]:
    if "session_utc" not in subset.columns:
        return 0, 0.0, 0.0
    sess = subset["session_utc"].to_numpy()
    values = net_values[slice_mask & (sess == session_label)]
    values = values[np.isfinite(values)]
    n = len(values)
    if n == 0:
        return 0, 0.0, 0.0
    return n, float(np.mean(values)), float(np.mean(values > 0))


def validate_slices(prepared: pd.DataFrame, candidates) -> list[ValidatedSlice]:
    if prepared.empty or not candidates:
        return []

    labelled = _attach_regime_labels(prepared)
    rows = (
        labelled.dropna(subset=["close", "high", "low"])
        .sort_values("start")
        .reset_index(drop=True)
    )
    cost = float(rows["cost"].iloc[0]) if "cost" in rows.columns and len(rows) else 0.0

    validated: list[ValidatedSlice] = []

    for candidate in candidates:
        state_column = f"state_{candidate.feature}"
        if state_column not in rows.columns:
            continue

        subset = rows.dropna(subset=[state_column, "close", "high", "low"])
        slice_mask = (subset[state_column] == candidate.state).to_numpy(dtype=bool)

        stop_atr_mult = _calibrate_stop_atr_mult(prepared, candidate, state_column)

        net_series = _trade_net_series_for_candidate(
            subset,
            side=str(candidate.side),
            horizon_bars=int(candidate.horizon_bars),
            stop_atr_mult=float(stop_atr_mult),
            cost=float(cost),
        )
        net_values = net_series.to_numpy()

        # Only consider rows where the net return is defined (horizon exists, ATR exists)
        valid = np.isfinite(net_values)
        slice_mask = slice_mask & valid

        slice_net = net_values[slice_mask]
        n = int(len(slice_net))
        mean_net = float(np.mean(slice_net)) if n else 0.0
        std = float(np.std(slice_net, ddof=1)) if n > 1 else 0.0
        t_stat = mean_net / (std / math.sqrt(n)) if std > 0 else 0.0
        p_value = _normal_p(t_stat)

        # Walk-forward folds over time (subset already sorted by start)
        fold_ids = np.linspace(0, len(subset), FOLD_COUNT + 1).astype(int)
        fold_results: list[str] = []
        fold_means: list[float] = []
        fold_sizes: list[int] = []

        for fold in range(FOLD_COUNT):
            fold_mask = np.zeros(len(subset), dtype=bool)
            fold_mask[fold_ids[fold] : fold_ids[fold + 1]] = True

            fold_returns = net_values[slice_mask & fold_mask]
            passed = _fold_pass(fold_returns)

            fold_results.append("1" if passed else "0")
            fold_means.append(float(np.mean(fold_returns)) if len(fold_returns) else 0.0)
            fold_sizes.append(int(len(fold_returns)))

        pattern = "".join(fold_results)
        pass_count = pattern.count("1")
        latest_passes = pattern[-1] == "1"

        strict_required = max(3, int(0.75 * FOLD_COUNT))
        relaxed_required = max(strict_required, min(FOLD_COUNT, max(1, RELAXED_MIN_PASSES)))
        required_passes = strict_required if REQUIRE_BONFERRONI else relaxed_required

        temporal_pass = (pass_count >= required_passes) and latest_passes
        if REQUIRE_BONFERRONI:
            temporal_pass = temporal_pass and bool(candidate.bonferroni_pass)

        hostile_label = "bear" if str(candidate.side) == "LONG" else "bull"
        hostile_mask = slice_mask & (subset["regime_row"].to_numpy() == hostile_label)
        hostile_net = net_values[hostile_mask]
        hostile_net = hostile_net[np.isfinite(hostile_net)]
        hostile_n, hostile_mean, confounded, hostile_unproven = _hostile_regime_check(hostile_net)

        asia_n, asia_mean, asia_hit = _session_stats_from_net(subset, slice_mask, SESSION_ASIA, net_values)
        eu_n, eu_mean, eu_hit = _session_stats_from_net(subset, slice_mask, SESSION_EU, net_values)
        us_n, us_mean, us_hit = _session_stats_from_net(subset, slice_mask, SESSION_US, net_values)

        validated.append(
            ValidatedSlice(
                slice_id=candidate.slice_id,
                kind=candidate.kind,
                feature=candidate.feature,
                state=int(candidate.state),
                side=str(candidate.side),
                folds=FOLD_COUNT,
                walk_forward_pass_pattern=pattern,
                walk_forward_pass_count=int(pass_count),
                fold_mean_rets=",".join(f"{value:.6f}" for value in fold_means),
                fold_sizes=",".join(str(size) for size in fold_sizes),
                n=n,
                mean_ret_costadj=mean_net,
                p_value=float(p_value),
                validated=(temporal_pass and not confounded and mean_net > 0.0),
                horizon_bars=int(candidate.horizon_bars),
                stop_atr_mult=float(stop_atr_mult),
                hostile_n=int(hostile_n),
                hostile_mean_ret=float(hostile_mean),
                regime_confounded=bool(confounded),
                hostile_unproven=bool(hostile_unproven),
                session_asia_n=int(asia_n),
                session_asia_mean_ret_costadj=float(asia_mean),
                session_asia_hit_rate=float(asia_hit),
                session_eu_n=int(eu_n),
                session_eu_mean_ret_costadj=float(eu_mean),
                session_eu_hit_rate=float(eu_hit),
                session_us_n=int(us_n),
                session_us_mean_ret_costadj=float(us_mean),
                session_us_hit_rate=float(us_hit),
            )
        )

    return sorted(validated, key=lambda row: (not row.validated, -row.mean_ret_costadj))


def read_validated(path: Path) -> list[ValidatedSlice]:
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
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
        out = []
        for row in reader:
            out.append(
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
        return out


def write_validated(path, rows: list[ValidatedSlice]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(row) for row in rows]
    file_descriptor, temporary_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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
