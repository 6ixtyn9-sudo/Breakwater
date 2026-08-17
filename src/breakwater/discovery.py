"""Market-state slice discovery on pooled universe bars.

Features are binned into expanding quantile states per symbol. Each
(feature, state) combination is a candidate slice. Discovery evaluates BOTH
trade directions correctly:

- raw forward return: r = close[t+h]/close[t] - 1
- LONG net:  r - cost
- SHORT net: -r - cost

We choose the direction with the higher net mean for that (feature, state)
and record that slice as LONG or SHORT accordingly. Bonferroni correction
is conservatively applied as if we had tested both directions
(2 * number_of_slices).

Session audit (UTC): we attach a coarse `session_utc` label to each bar and
report per-session stats for each slice (audit-only; does not change slice
eligibility or validation logic).

Upgrade:
- bin_states is now vectorized using pandas expanding quantiles (O(n) per feature),
  replacing the prior O(n^2) python loop.

Env knobs:
- BREAKWATER_DISCOVERY_MIN_SLICE_ROWS (default 30)
- BREAKWATER_DISCOVERY_ROLLING_MIN_PERIODS (default 200)
- BREAKWATER_DISCOVERY_STATE_QUANTILES (default "0.333333,0.666666")
  Two cutpoints -> 3 states (0,1,2). Recommend "0.2,0.8" to emphasize tails.
- BREAKWATER_DISCOVERY_ALPHA (default "0.05")
"""

from __future__ import annotations

import math
import os
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation

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

SESSION_ASIA = "asia"  # 00-07 UTC
SESSION_EU = "eu"      # 08-15 UTC
SESSION_US = "us"      # 16-23 UTC


def _env_int(name: str, default: int) -> int:
    raw = str(os.getenv(name, "")).strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_decimal(name: str, default: Decimal) -> Decimal:
    raw = str(os.getenv(name, "")).strip()
    if not raw:
        return default
    try:
        val = Decimal(raw)
    except InvalidOperation:
        return default
    return val if val.is_finite() else default


def _parse_two_quantiles(text: str, default: tuple[float, float]) -> tuple[float, float]:
    raw = str(text or "").strip()
    if not raw:
        return default
    try:
        parts = [float(p.strip()) for p in raw.split(",") if p.strip()]
    except ValueError:
        return default
    if len(parts) != 2:
        return default
    q0, q1 = parts[0], parts[1]
    if not (0.0 < q0 < q1 < 1.0):
        return default
    return float(q0), float(q1)


MIN_SLICE_ROWS = _env_int("BREAKWATER_DISCOVERY_MIN_SLICE_ROWS", 30)
ROLLING_MIN_PERIODS = _env_int("BREAKWATER_DISCOVERY_ROLLING_MIN_PERIODS", 200)
ALPHA = _env_decimal("BREAKWATER_DISCOVERY_ALPHA", Decimal("0.05"))
STATE_Q0, STATE_Q1 = _parse_two_quantiles(
    os.getenv("BREAKWATER_DISCOVERY_STATE_QUANTILES", "0.333333,0.666666"),
    default=(1 / 3, 2 / 3),
)


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
    # Two-sided normal approximation (kept consistent with current implementation)
    return 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(t_stat) / math.sqrt(2.0))))


def _utc_session_labels(start_series: pd.Series) -> pd.Series:
    stamps = pd.to_datetime(start_series, utc=True, errors="coerce")
    hour = stamps.dt.hour.fillna(-1).astype(int)
    session = pd.Series("unknown", index=start_series.index, dtype="object")
    session[(hour >= 0) & (hour <= 7)] = SESSION_ASIA
    session[(hour >= 8) & (hour <= 15)] = SESSION_EU
    session[(hour >= 16) & (hour <= 23)] = SESSION_US
    return session


def _net_returns(raw_returns: np.ndarray, side: str, cost: float) -> np.ndarray:
    """Returns are oriented so profitable returns are > 0 for BOTH sides."""
    if side == "LONG":
        return raw_returns - cost
    return (-raw_returns) - cost


def bin_states(
    frame: pd.DataFrame,
    columns: list[str],
    *,
    bins: int = 3,
    min_periods: int = ROLLING_MIN_PERIODS,
) -> pd.DataFrame:
    """Attach state_{feature} columns.

    Breakwater uses exactly 3 states (0,1,2).
    - We keep `bins` for backward signature compatibility.
    - We fail loudly if bins != 3 to prevent silent nonsense.
    """
    if bins != 3:
        raise ValueError("Breakwater bin_states currently supports bins=3 only")

    df = frame.copy()
    for column in columns:
        series = df[column].astype(float)
        df[f"state_{column}"] = np.nan

        if len(series) < min_periods:
            continue

        # Vectorized expanding quantile thresholds
        t0 = series.expanding(min_periods=min_periods).quantile(STATE_Q0).to_numpy()
        t1 = series.expanding(min_periods=min_periods).quantile(STATE_Q1).to_numpy()
        v = series.to_numpy()

        ok = np.isfinite(v) & np.isfinite(t0) & np.isfinite(t1)
        states = np.full(len(v), np.nan)

        idx = np.where(ok)[0]
        if len(idx):
            vv = v[idx]
            a = t0[idx]
            b = t1[idx]
            states[idx] = np.where(vv <= a, 0, np.where(vv <= b, 1, 2))

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
        group = group.sort_values("start").reset_index(drop=True)
        binned = bin_states(group, feature_columns)

        if "start" in binned.columns:
            binned["session_utc"] = _utc_session_labels(binned["start"])
        else:
            binned["session_utc"] = "unknown"

        close = binned["close"].astype(float)

        # Raw forward return (no cost, no side)
        binned["fwd_ret_raw"] = (close.shift(-horizon_bars) / close) - 1.0

        # Legacy column name preserved
        binned["fwd_ret"] = binned["fwd_ret_raw"]

        # Cost carried as a constant column so validation can compute net returns too
        binned["cost"] = float(cost)

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
    *,
    side: str,
    cost: float,
) -> tuple[int, float, float]:
    if "session_utc" not in subset.columns:
        return 0, 0.0, 0.0
    session_mask = subset["session_utc"] == session_label
    raw = subset.loc[slice_mask & session_mask, "fwd_ret_raw"].to_numpy()
    n = len(raw)
    if n == 0:
        return 0, 0.0, 0.0
    net = _net_returns(raw, side, cost)
    return n, float(np.mean(net)), float(np.mean(net > 0))


def _stat_block(returns: np.ndarray) -> tuple[float, float, float, float, float]:
    n = len(returns)
    mean = float(np.mean(returns))
    median = float(np.median(returns))
    hit = float(np.mean(returns > 0))
    std = float(np.std(returns, ddof=1)) if n > 1 else 0.0
    t_stat = mean / (std / math.sqrt(n)) if std > 0 else 0.0
    p_value = _normal_p(t_stat)
    return mean, median, hit, t_stat, p_value


def _slice_stats(
    prepared: pd.DataFrame,
    kind: str,
    feature_columns: list[str],
    horizon_bars: int,
) -> list[SliceStat]:
    candidates: list[SliceStat] = []

    # Conservative: treat each (feature,state) as if we tested 2 hypotheses (LONG + SHORT)
    effective_tests = 0

    for feature in feature_columns:
        state_column = f"state_{feature}"
        for state in (0, 1, 2):
            subset = prepared.dropna(subset=[state_column, "fwd_ret_raw"])
            mask = subset[state_column] == state

            raw = subset.loc[mask, "fwd_ret_raw"].to_numpy()
            n = len(raw)
            if n < MIN_SLICE_ROWS:
                continue

            cost = float(subset["cost"].iloc[0]) if "cost" in subset.columns and len(subset) else 0.0

            long_net = _net_returns(raw, "LONG", cost)
            short_net = _net_returns(raw, "SHORT", cost)

            long_mean, long_median, long_hit, long_t, long_p = _stat_block(long_net)
            short_mean, short_median, short_hit, short_t, short_p = _stat_block(short_net)

            # Choose the side with the higher net mean
            if long_mean >= short_mean:
                side = "LONG"
                mean, median, hit_rate, t_stat, p_value = long_mean, long_median, long_hit, long_t, long_p
            else:
                side = "SHORT"
                mean, median, hit_rate, t_stat, p_value = short_mean, short_median, short_hit, short_t, short_p

            asia_n, asia_mean, asia_hit = _session_stats(subset, mask, SESSION_ASIA, side=side, cost=cost)
            eu_n, eu_mean, eu_hit = _session_stats(subset, mask, SESSION_EU, side=side, cost=cost)
            us_n, us_mean, us_hit = _session_stats(subset, mask, SESSION_US, side=side, cost=cost)

            candidates.append(
                SliceStat(
                    slice_id=f"{feature}:{state}:{side}",
                    kind=kind,
                    feature=feature,
                    state=state,
                    side=side,
                    n=n,
                    mean_ret_costadj=mean,
                    median_ret_costadj=median,
                    hit_rate=hit_rate,
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
            effective_tests += 2

    if candidates:
        threshold = float(ALPHA) / max(1, effective_tests)

        flagged = []
        for stat in candidates:
            passed = (stat.p_value < threshold) and (stat.n >= MIN_SLICE_ROWS) and (stat.mean_ret_costadj > 0)
            row = asdict(stat)
            row["bonferroni_pass"] = bool(passed)
            flagged.append(row)

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
    file_descriptor, temporary_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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
