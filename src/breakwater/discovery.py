"""Market-state slice discovery on pooled universe bars.

Upgrade (core):
- Discovery now scores candidates using a stop-aware forward trade model that
  matches paper trading for horizon-based slices:
    - Entry at close[t]
    - Stop at +/- DISCOVERY_STOP_ATR_MULT * ATR(14)
    - Exit at stop if breached within horizon, else exit at close[t+h]
    - Directional gross return minus cost => net return
  This reduces research/execution mismatch.

Notes:
- This is still just discovery: validation recalibrates stop_atr_mult per slice
  using fwd_mae_atr distribution and re-scores there.
- Schema stays the same.

Upgrade (alpha vs beta):
- Discovery now residualizes forward trade returns against an equal-weight,
  leave-one-out cross-sectional benchmark built from the pooled universe at
  each bar.  Significance (t/p, Bonferroni) is computed on the *residual*
  (alpha) return, not the raw directional return.  Raw ``fwd_ret_raw`` on a
  LONG candidate in a bull period is mostly market beta, which made beta look
  like a validated edge and made SHORT candidates structurally unable to pass.
  ``mean_ret_costadj`` stays the raw cost-adjusted trade return (what you would
  actually earn); ``mean_resid_costadj`` / ``alpha_t_stat`` / ``alpha_p_value``
  carry the benchmark-relative evidence.
- Set BREAKWATER_DISCOVERY_RESIDUALIZE=0 to restore raw-return scoring.

Env knobs (existing):
- BREAKWATER_DISCOVERY_MIN_SLICE_ROWS (default 30)
- BREAKWATER_DISCOVERY_ROLLING_MIN_PERIODS (default 200)
- BREAKWATER_DISCOVERY_STATE_QUANTILES (default "0.333333,0.666666")
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
    # Benchmark-relative (alpha) evidence; append-only
    "mean_resid_costadj",
    "alpha_t_stat",
    "alpha_p_value",
    "market_mean_ret",
    "residualized",
]

SESSION_ASIA = "asia"  # 00-07 UTC
SESSION_EU = "eu"      # 08-15 UTC
SESSION_US = "us"      # 16-23 UTC

# Fixed stop multiple for discovery scoring only (validation recalibrates per slice)
# Reduced from 2.0 to 1.5 to match engine fix and cut risk_fraction 5.99% ARB
DISCOVERY_STOP_ATR_MULT = 1.5


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


def _env_bool(name: str, default: str = "0") -> bool:
    return str(os.getenv(name, default)).strip().lower() in {"1", "true", "yes", "on"}


MIN_SLICE_ROWS = _env_int("BREAKWATER_DISCOVERY_MIN_SLICE_ROWS", 30)
# Score candidates on benchmark-residualized (alpha) returns rather than raw
# directional returns.  Raw returns reward market beta in trending periods.
RESIDUALIZE = _env_bool("BREAKWATER_DISCOVERY_RESIDUALIZE", "1")
# Minimum number of peers at a bar before a cross-sectional benchmark is
# trusted.  Below this the benchmark is 0 (residual == raw) because there is
# no cross-section to residualize against.
MARKET_MIN_PEERS = max(1, _env_int("BREAKWATER_DISCOVERY_MARKET_MIN_PEERS", 2))
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
    # Benchmark-relative (alpha) evidence
    mean_resid_costadj: float = 0.0
    alpha_t_stat: float = 0.0
    alpha_p_value: float = 1.0
    market_mean_ret: float = 0.0
    residualized: bool = False


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
    if bins != 3:
        raise ValueError("Breakwater bin_states currently supports bins=3 only")

    df = frame.copy()
    for column in columns:
        series = df[column].astype(float)
        df[f"state_{column}"] = np.nan

        if len(series) < min_periods:
            continue

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


def _atr14(df: pd.DataFrame) -> pd.Series:
    close = df["close"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    high_low = high - low
    high_close_prev = (high - close.shift(1)).abs()
    low_close_prev = (low - close.shift(1)).abs()
    true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
    return true_range.rolling(14).mean()


def _trade_net_cols(
    df: pd.DataFrame,
    *,
    horizon_bars: int,
    stop_atr_mult: float,
    cost: float,
) -> pd.DataFrame:
    """Attach stop-aware net returns for LONG and SHORT (directional, cost-adjusted)."""
    out = df.copy()

    close = out["close"].astype(float)
    high = out["high"].astype(float)
    low = out["low"].astype(float)

    atr = _atr14(out).replace(0, np.nan)
    out["atr_14"] = atr

    fwd_close = close.shift(-horizon_bars)
    out["fwd_close_h"] = fwd_close

    low_next = low.shift(-1)
    high_next = high.shift(-1)
    fwd_min_low = low_next.rolling(horizon_bars).min().shift(-(horizon_bars - 1))
    fwd_max_high = high_next.rolling(horizon_bars).max().shift(-(horizon_bars - 1))
    out["fwd_min_low_h"] = fwd_min_low
    out["fwd_max_high_h"] = fwd_max_high

    # LONG
    stop_long = close - stop_atr_mult * atr
    hit_long = fwd_min_low <= stop_long
    exit_long = np.where(hit_long.to_numpy(dtype=bool), stop_long.to_numpy(), fwd_close.to_numpy())
    gross_long = (exit_long - close.to_numpy()) / close.to_numpy()
    net_long = gross_long - cost

    # SHORT
    stop_short = close + stop_atr_mult * atr
    hit_short = fwd_max_high >= stop_short
    exit_short = np.where(hit_short.to_numpy(dtype=bool), stop_short.to_numpy(), fwd_close.to_numpy())
    gross_short = (exit_short - close.to_numpy()) / close.to_numpy() * (-1.0)
    net_short = gross_short - cost

    out["fwd_trade_net_long"] = net_long
    out["fwd_trade_net_short"] = net_short
    return out


def attach_market_benchmark(prepared: pd.DataFrame) -> pd.DataFrame:
    """Attach an equal-weight, leave-one-out cross-sectional benchmark.

    For every bar ``start`` the benchmark is the mean raw forward return of the
    *other* symbols in the pooled universe at that bar.  Leave-one-out keeps a
    symbol's own idiosyncratic move out of its benchmark so thin universes do
    not mechanically shrink every residual toward zero.

    Columns added:
    - ``market_peers``             number of peer symbols used
    - ``fwd_ret_market``           benchmark forward return (0 when no peers)
    - ``fwd_ret_resid``            fwd_ret_raw - fwd_ret_market
    - ``fwd_trade_net_long_resid`` fwd_trade_net_long - fwd_ret_market
    - ``fwd_trade_net_short_resid`` fwd_trade_net_short + fwd_ret_market

    A LONG residual is "did this trade beat holding the universe"; a SHORT
    residual is "did shorting this beat shorting the universe".  Both are
    zero-mean under pure beta, which is exactly the property discovery needs.
    """
    if prepared.empty or "fwd_ret_raw" not in prepared.columns or "start" not in prepared.columns:
        return prepared
    out = prepared.copy()
    raw = out["fwd_ret_raw"].astype(float)
    finite = raw.where(np.isfinite(raw))
    key = out["start"]
    group = finite.groupby(key)
    total = group.transform("sum")
    count = group.transform("count")
    own_finite = finite.notna()
    peers = (count - own_finite.astype(int)).clip(lower=0)
    loo_sum = total - finite.fillna(0.0)
    market = np.where(peers >= MARKET_MIN_PEERS, loo_sum / peers.replace(0, np.nan), 0.0)
    market = np.nan_to_num(np.asarray(market, dtype=float), nan=0.0)
    out["market_peers"] = peers.astype(int).to_numpy()
    out["fwd_ret_market"] = market
    out["fwd_ret_resid"] = raw.to_numpy() - market
    if "fwd_trade_net_long" in out.columns:
        out["fwd_trade_net_long_resid"] = out["fwd_trade_net_long"].astype(float).to_numpy() - market
    if "fwd_trade_net_short" in out.columns:
        out["fwd_trade_net_short_resid"] = out["fwd_trade_net_short"].astype(float).to_numpy() + market
    return out


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
    *,
    cost_bps_for_symbol=None,
) -> pd.DataFrame:
    default_cost = cost_bps / 10000.0
    if "symbol" not in frame.columns:
        raise ValueError("pooled frame must carry a symbol column")

    from breakwater.features import forward_mae_atr

    parts = []
    for symbol, group in frame.groupby("symbol", sort=False):
        if cost_bps_for_symbol is not None:
            cost = float(cost_bps_for_symbol(str(symbol))) / 10000.0
        else:
            cost = default_cost
        group = group.sort_values("start").reset_index(drop=True)
        binned = bin_states(group, feature_columns)

        if "start" in binned.columns:
            binned["session_utc"] = _utc_session_labels(binned["start"])
        else:
            binned["session_utc"] = "unknown"

        close = binned["close"].astype(float)

        # Raw forward return (kept for compatibility / validation calibration)
        binned["fwd_ret_raw"] = (close.shift(-horizon_bars) / close) - 1.0
        binned["fwd_ret"] = binned["fwd_ret_raw"]
        binned["cost"] = float(cost)

        # MAE in ATR units (used to calibrate stop_atr_mult in validation)
        binned["fwd_mae_atr"] = forward_mae_atr(binned, horizon=horizon_bars)
        binned["fwd_mae_atr_5"] = forward_mae_atr(binned, horizon=5)

        # Stop-aware trade net returns (discovery uses fixed stop multiple)
        binned = _trade_net_cols(
            binned,
            horizon_bars=horizon_bars,
            stop_atr_mult=float(DISCOVERY_STOP_ATR_MULT),
            cost=float(cost),
        )

        parts.append(binned)

    if not parts:
        return frame.iloc[0:0].copy()
    pooled = pd.concat(parts, ignore_index=True)
    # Cross-sectional benchmark needs the whole universe at once.
    return attach_market_benchmark(pooled)


def _session_stats_from_col(
    subset: pd.DataFrame,
    slice_mask: pd.Series,
    session_label: str,
    ret_col: str,
) -> tuple[int, float, float]:
    if "session_utc" not in subset.columns:
        return 0, 0.0, 0.0
    session_mask = subset["session_utc"] == session_label
    values = subset.loc[slice_mask & session_mask, ret_col].to_numpy()
    values = values[np.isfinite(values)]
    n = len(values)
    if n == 0:
        return 0, 0.0, 0.0
    return n, float(np.mean(values)), float(np.mean(values > 0))


def _stat_block(returns: np.ndarray) -> tuple[float, float, float, float, float]:
    returns = returns[np.isfinite(returns)]
    n = len(returns)
    mean = float(np.mean(returns)) if n else 0.0
    median = float(np.median(returns)) if n else 0.0
    hit = float(np.mean(returns > 0)) if n else 0.0
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
    effective_tests = 0

    use_resid = bool(
        RESIDUALIZE
        and "fwd_trade_net_long_resid" in prepared.columns
        and "fwd_trade_net_short_resid" in prepared.columns
    )

    for feature in feature_columns:
        state_column = f"state_{feature}"
        for state in (0, 1, 2):
            subset = prepared.dropna(subset=[state_column, "fwd_trade_net_long", "fwd_trade_net_short"])
            mask = subset[state_column] == state

            long_net = subset.loc[mask, "fwd_trade_net_long"].to_numpy()
            short_net = subset.loc[mask, "fwd_trade_net_short"].to_numpy()

            n_long = int(np.isfinite(long_net).sum())
            n_short = int(np.isfinite(short_net).sum())

            long_mean, long_median, long_hit, long_t, long_p = _stat_block(long_net)
            short_mean, short_median, short_hit, short_t, short_p = _stat_block(short_net)

            if use_resid:
                long_resid = subset.loc[mask, "fwd_trade_net_long_resid"].to_numpy()
                short_resid = subset.loc[mask, "fwd_trade_net_short_resid"].to_numpy()
                market_vals = subset.loc[mask, "fwd_ret_market"].to_numpy()
                market_vals = market_vals[np.isfinite(market_vals)]
                market_mean = float(np.mean(market_vals)) if len(market_vals) else 0.0
                long_rmean, _, _, long_rt, long_rp = _stat_block(long_resid)
                short_rmean, _, _, short_rt, short_rp = _stat_block(short_resid)
            else:
                market_mean = 0.0
                long_rmean, long_rt, long_rp = long_mean, long_t, long_p
                short_rmean, short_rt, short_rp = short_mean, short_t, short_p

            # Emit each direction independently — a state with enough
            # LONG rows but not enough SHORT rows should still produce a
            # LONG candidate.  Requiring both sides to meet the floor
            # halves yield for asymmetric features.
            for side, n, mean, median, hit_rate, t_stat, p_value, ret_col, rmean, rt, rp in (
                ("LONG", n_long, long_mean, long_median, long_hit, long_t, long_p, "fwd_trade_net_long", long_rmean, long_rt, long_rp),
                ("SHORT", n_short, short_mean, short_median, short_hit, short_t, short_p, "fwd_trade_net_short", short_rmean, short_rt, short_rp),
            ):
                if n < MIN_SLICE_ROWS:
                    continue

                asia_n, asia_mean, asia_hit = _session_stats_from_col(
                    subset, mask, SESSION_ASIA, ret_col
                )
                eu_n, eu_mean, eu_hit = _session_stats_from_col(
                    subset, mask, SESSION_EU, ret_col
                )
                us_n, us_mean, us_hit = _session_stats_from_col(
                    subset, mask, SESSION_US, ret_col
                )

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
                        mean_resid_costadj=rmean,
                        alpha_t_stat=rt,
                        alpha_p_value=rp,
                        market_mean_ret=market_mean,
                        residualized=use_resid,
                    )
                )
            effective_tests += 2

    if candidates:
        threshold = float(ALPHA) / max(1, effective_tests)
        flagged = []
        for stat in candidates:
            # Significance is judged on the benchmark-relative (alpha) return so
            # that a state which merely coincides with a trending market cannot
            # pass.  The raw trade return must still be positive: relative
            # outperformance that loses money outright is not tradeable.
            passed = (
                (stat.alpha_p_value < threshold)
                and (stat.n >= MIN_SLICE_ROWS)
                and (stat.mean_resid_costadj > 0)
                and (stat.mean_ret_costadj > 0)
            )
            row = asdict(stat)
            row["bonferroni_pass"] = bool(passed)
            flagged.append(row)
        candidates = [SliceStat(**row) for row in flagged]

    return sorted(
        candidates,
        key=lambda stat: (not stat.bonferroni_pass, -stat.mean_resid_costadj, -stat.mean_ret_costadj),
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
