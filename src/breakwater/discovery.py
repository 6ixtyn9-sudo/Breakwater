"""Market-state slice discovery on pooled universe bars.

Features are binned into expanding quantile states per symbol. Each
(feature, state, side) combination is a candidate slice whose cost-adjusted
forward returns are measured across the pooled universe. Candidates are
ranked with a Bonferroni correction applied to the number of slices tested.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from decimal import Decimal

import numpy as np
import pandas as pd


DISCOVERY_HEADERS = [
    "slice_id",
    "kind",
    "feature",
    "state",
    "side",
    "n",
    "mean_ret_costadj",
    "median_ret_costadj",
    "hit_rate",
    "t_stat",
    "p_value",
    "bonferroni_pass",
    "horizon_bars",
]

MIN_SLICE_ROWS = 30
ROLLING_MIN_PERIODS = 200
ALPHA = Decimal("0.05")


@dataclass(frozen=True)
class SliceStat:
    slice_id: str
    kind: str
    feature: str
    state: int
    side: str
    n: int
    mean_ret_costadj: float
    median_ret_costadj: float
    hit_rate: float
    t_stat: float
    p_value: float
    bonferroni_pass: bool
    horizon_bars: int


def _normal_p(t_stat: float) -> float:
    return 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(t_stat) / math.sqrt(2.0))))


def bin_states(
    frame: pd.DataFrame,
    columns: list[str],
    *,
    bins: int = 3,
    min_periods: int = ROLLING_MIN_PERIODS,
) -> pd.DataFrame:
    df = frame.copy()
    for column in columns:
        series = df[column]
        df[f"state_{column}"] = np.nan
        values = series.to_numpy()
        states = np.full(len(values), np.nan)
        for index in range(min_periods, len(values)):
            window = values[: index + 1]
            finite = window[np.isfinite(window)]
            if len(finite) < min_periods:
                continue
            thresholds = np.quantile(finite, [1 / bins, 2 / bins])
            value = values[index]
            if not np.isfinite(value):
                continue
            if value <= thresholds[0]:
                states[index] = 0
            elif value <= thresholds[1]:
                states[index] = 1
            else:
                states[index] = 2
        df[f"state_{column}"] = states
    return df


def discover_slices(
    frame: pd.DataFrame,
    *,
    kind: str,
    feature_columns: list[str],
    cost_bps: float,
    horizon_bars: int = 1,
) -> list[SliceStat]:
    if frame.empty:
        return []
    prepared = prepare_pooled(frame, feature_columns, cost_bps, horizon_bars)
    return _slice_stats(prepared, kind, feature_columns, horizon_bars)


def prepare_pooled(
    frame: pd.DataFrame,
    feature_columns: list[str],
    cost_bps: float,
    horizon_bars: int = 1,
) -> pd.DataFrame:
    cost = cost_bps / 10000.0
    if "symbol" not in frame.columns:
        raise ValueError("pooled frame must carry a symbol column")

    from breakwater.features import forward_mae_atr

    parts = []
    for _, group in frame.groupby("symbol", sort=False):
        binned = bin_states(group, feature_columns)
        close = binned["close"]

        binned["fwd_ret"] = (close.shift(-horizon_bars) / close - 1.0) - cost

        # New: MAE measured over the same horizon as forward returns
        binned["fwd_mae_atr"] = forward_mae_atr(binned, horizon=horizon_bars)

        # Keep legacy 5-bar MAE for backward compatibility
        binned["fwd_mae_atr_5"] = forward_mae_atr(binned, horizon=5)

        parts.append(binned)

    if not parts:
        return frame.iloc[0:0].copy()
    return pd.concat(parts, ignore_index=True)


def _slice_stats(
    prepared: pd.DataFrame,
    kind: str,
    feature_columns: list[str],
    horizon_bars: int,
) -> list[SliceStat]:
    candidates: list[SliceStat] = []
    for feature in feature_columns:
        state_column = f"state_{feature}"
        for state in (0, 1, 2):
            subset = prepared.dropna(subset=[state_column, "fwd_ret"])
            mask = subset[state_column] == state
            returns = subset.loc[mask, "fwd_ret"].to_numpy()
            n = len(returns)
            if n < MIN_SLICE_ROWS:
                continue
            mean = float(np.mean(returns))
            std = float(np.std(returns, ddof=1)) if n > 1 else 0.0
            t_stat = mean / (std / math.sqrt(n)) if std > 0 else 0.0
            p_value = _normal_p(t_stat)
            side = "LONG" if mean > 0 else "SHORT"
            candidates.append(
                SliceStat(
                    slice_id=f"{feature}:{state}:{side}",
                    kind=kind,
                    feature=feature,
                    state=state,
                    side=side,
                    n=n,
                    mean_ret_costadj=mean,
                    median_ret_costadj=float(np.median(returns)),
                    hit_rate=float(np.mean(returns > 0)),
                    t_stat=t_stat,
                    p_value=p_value,
                    bonferroni_pass=False,
                    horizon_bars=horizon_bars,
                )
            )

    if candidates:
        threshold = float(ALPHA) / len(candidates)
        flagged = [
            asdict(stat)
            | {
                "bonferroni_pass": stat.p_value < threshold
                and stat.n >= MIN_SLICE_ROWS
            }
            for stat in candidates
        ]
        candidates = [SliceStat(**row) for row in flagged]

    return sorted(
        candidates,
        key=lambda stat: (not stat.bonferroni_pass, -stat.mean_ret_costadj),
    )


def write_discovered(path, slices: list[SliceStat]) -> None:
    _write_slice_rows(path, [asdict(stat) for stat in slices], DISCOVERY_HEADERS)


def _write_slice_rows(path, rows: list[dict], headers: list[str]) -> None:
    import csv
    import os
    import tempfile

    path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(file_descriptor, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise
