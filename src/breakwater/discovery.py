"""Market-state slice discovery on pooled universe bars.

Features are binned into expanding quantile states per symbol. Each
(feature, state, side) combination is a candidate slice whose cost-adjusted
forward returns are measured across the pooled universe. Candidates are
ranked with a Bonferroni correction applied to the number of slices tested.

Session audit (UTC): each prepared row is tagged into a coarse UTC session
bucket (asia/eu/us). Discovery outputs include per-session counts/means/hit
rates for each slice. This is audit-only; it does not change which slices
exist or how they are ranked.
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

MIN_SLICE_ROWS = 30
ROLLING_MIN_PERIODS = 200
ALPHA = Decimal("0.05")

SESSION_ASIA = "asia"  # 00-07 UTC
SESSION_EU = "eu"      # 08-15 UTC
SESSION_US = "us"      # 16-23 UTC


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


def _utc_session_labels(start_series: pd.Series) -> pd.Series:
    stamps = pd.to_datetime(start_series, utc=True, errors="coerce")
    hour = stamps.dt.hour.fillna(-1).astype(int)

    session = pd.Series("unknown", index=start_series.index, dtype="object")
    session[(hour >= 0) & (hour <= 7)] = SESSION_ASIA
    session[(hour >= 8) & (hour <= 15)] = SESSION_EU
    session[(hour >= 16) & (hour <= 23)] = SESSION_US
    return session


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

        if "start" in binned.columns:
            binned["session_utc"] = _utc_session_labels(binned["start"])
        else:
            binned["session_utc"] = "unknown"

        close = binned["close"]
        binned["fwd_ret"] = (close.shift(-horizon_bars) / close - 1.0) - cost

        # MAE measured over the same horizon as forward returns
        binned["fwd_mae_atr"] = forward_mae_atr(binned, horizon=horizon_bars)

        # Keep legacy 5-bar MAE for backward compatibility
        binned["fwd_mae_atr_5"] = forward_mae_atr(binned, horizon=5)

        parts.append(binned)

    if not parts:
        return frame.iloc[0:0].copy()
    return pd.concat(parts, ignore_index=True)


def _session_stats(
    subset: pd.DataFrame,
    slice_mask: pd.Series,
    session_label: str,
) -> tuple[int, float, float]:
    if "session_utc" not in subset.columns:
        return 0, 0.0, 0.0
    session_mask = subset["session_utc"] == session_label
    values = subset.loc[slice_mask & session_mask, "fwd_ret"].to_numpy()
    n = len(values)
    if n == 0:
        return 0, 0.0, 0.0
    return n, float(np.mean(values)), float(np.mean(values > 0))


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

            asia_n, asia_mean, asia_hit = _session_stats(subset, mask, SESSION_ASIA)
            eu_n, eu_mean, eu_hit = _session_stats(subset, mask, SESSION_EU)
            us_n, us_mean, us_hit = _session_stats(subset, mask, SESSION_US)

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
