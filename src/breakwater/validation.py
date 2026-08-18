"""Walk-forward validation of discovered slices.

Fixes the remaining "quant trap" issues:

1) Execution-aligned returns:
   Validate using a stop-aware trade return that matches paper execution:
   - entry at close[t]
   - stop at +/- stop_atr_mult * ATR(14)
   - stop triggers if breached within the NEXT horizon bars (excludes entry bar)
   - if not stopped, exit at close[t+h]
   - subtract constant cost
2) Side-selection leakage:
   Discovery chooses side using the full sample. Validation now re-chooses side
   on a training-only window and requires the candidate side to match that
   training-side.

3) Pooled-row illusion:
   Requires symbol breadth: the edge must exist across many symbols, not just
   a pooled burst.
4) Latest-fold brittleness + horizon overlap leakage:
   Uses a recency-window mean gate in addition to fold pass count, and purges
   the last `horizon_bars` rows of each fold from evaluation so forward windows
   don't cross fold boundaries.

No new knobs: uses only existing validation env vars.

CSV schema note:
- We append optional diagnostic columns to validated_slices.csv so operators can
  see *why* a row failed validation (temporal/direction/breadth/recency/mean/confound).
- Backwards compatible: read_validated() accepts older files that don't have these columns.
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
    # --- Diagnostics (optional; filled by validate_slices; kept for operator visibility) ---
    "required_passes",
    "latest_fold_passes",
    "temporal_pass",
    "direction_ok",
    "breadth_ok",
    "recency_ok",
    "mean_positive",
    "side_train",
    "fail_reasons",
    # --- Parameters / attributes ---
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

# --- Hard-coded strength rules (no new knobs) ---
TRAIN_FRACTION = 0.60

RECENCY_FRACTION = 0.20
RECENCY_MIN_ROWS = 20

BREADTH_MIN_SYMBOLS = 8
BREADTH_MIN_ROWS_PER_SYMBOL = 30
BREADTH_MIN_POSITIVE_FRACTION = 0.60


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

    # --- Diagnostics (optional; for operator visibility) ---
    required_passes: int = 0
    latest_fold_passes: bool = False
    temporal_pass: bool = False
    direction_ok: bool = False
    breadth_ok: bool = False
    recency_ok: bool = False
    mean_positive: bool = False
    side_train: str = ""
    fail_reasons: str = ""

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
    hostile_returns = net_hostile_returns[np.isfinite(net_hostile_returns)]
    hostile_n = len(hostile_returns)
    hostile_mean = float(np.mean(hostile_returns)) if hostile_n else 0.0
    if hostile_n < HOSTILE_MIN_ROWS:
        return hostile_n, hostile_mean, False, True
    return hostile_n, hostile_mean, hostile_mean <= 0.0, False


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


def _forward_extremes_excluding_entry_bar(
    high: pd.Series,
    low: pd.Series,
    horizon_bars: int,
) -> tuple[pd.Series, pd.Series]:
    """Min low / max high over the NEXT `horizon_bars` bars (excludes the entry bar)."""
    if horizon_bars < 1:
        raise ValueError("horizon_bars must be >= 1")

    low_next = low.shift(-1)
    high_next = high.shift(-1)
    fwd_min_low = low_next.rolling(horizon_bars).min().shift(-(horizon_bars - 1))
    fwd_max_high = high_next.rolling(horizon_bars).max().shift(-(horizon_bars - 1))
    return fwd_min_low, fwd_max_high


def _compute_stop_aware_net_returns(
    subset: pd.DataFrame,
    *,
    horizon_bars: int,
    stop_atr_mult: float,
    cost: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (net_long, net_short) arrays aligned to subset index."""
    n = len(subset)
    net_long = np.full(n, np.nan, dtype=float)
    net_short = np.full(n, np.nan, dtype=float)

    for _, g in subset.groupby("symbol", sort=False):
        g = g.sort_values("start")
        idx = g.index.to_numpy()
        close = g["close"].astype(float)
        high = g["high"].astype(float)
        low = g["low"].astype(float)

        atr = _atr14(g).replace(0, np.nan)
        fwd_close = close.shift(-horizon_bars)

        fwd_min_low, fwd_max_high = _forward_extremes_excluding_entry_bar(high, low, horizon_bars)

        stop_long = close - stop_atr_mult * atr
        hit_long = fwd_min_low <= stop_long
        exit_long = np.where(hit_long.to_numpy(dtype=bool), stop_long.to_numpy(), fwd_close.to_numpy())
        gross_long = (exit_long - close.to_numpy()) / close.to_numpy()
        net_l = gross_long - cost

        stop_short = close + stop_atr_mult * atr
        hit_short = fwd_max_high >= stop_short
        exit_short = np.where(hit_short.to_numpy(dtype=bool), stop_short.to_numpy(), fwd_close.to_numpy())
        gross_short = (exit_short - close.to_numpy()) / close.to_numpy() * (-1.0)
        net_s = gross_short - cost

        # Write back aligned to global subset order
        pos = subset.index.get_indexer(idx)
        net_long[pos] = net_l
        net_short[pos] = net_s

    return net_long, net_short


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


def _symbol_breadth_ok(subset: pd.DataFrame, slice_mask: np.ndarray, net_values: np.ndarray) -> bool:
    if "symbol" not in subset.columns:
        return False
    df = subset.loc[slice_mask, ["symbol"]].copy()
    if df.empty:
        return False
    df["net"] = net_values[slice_mask]
    df = df[np.isfinite(df["net"].to_numpy())]
    if df.empty:
        return False
    means = []
    for sym, g in df.groupby("symbol"):
        if len(g) < BREADTH_MIN_ROWS_PER_SYMBOL:
            continue
        means.append(float(g["net"].mean()))

    if len(means) < BREADTH_MIN_SYMBOLS:
        return False
    pos_frac = float(np.mean(np.array(means) > 0.0))
    return pos_frac >= BREADTH_MIN_POSITIVE_FRACTION


def _recency_ok(subset: pd.DataFrame, slice_mask: np.ndarray, net_values: np.ndarray) -> bool:
    n_total = len(subset)
    if n_total <= 0:
        return False
    window = int(max(RECENCY_MIN_ROWS, round(n_total * RECENCY_FRACTION)))
    window = min(window, n_total)

    recency_mask = np.zeros(n_total, dtype=bool)
    recency_mask[n_total - window : n_total] = True
    values = net_values[slice_mask & recency_mask]
    values = values[np.isfinite(values)]
    if len(values) < RECENCY_MIN_ROWS:
        return False
    return float(np.mean(values)) > 0.0


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
        subset = rows.dropna(subset=[state_column, "close", "high", "low"]).copy()
        subset = subset.sort_values("start").reset_index(drop=True)

        horizon_bars = int(candidate.horizon_bars)
        stop_atr_mult = float(_calibrate_stop_atr_mult(prepared, candidate, state_column))

        net_long, net_short = _compute_stop_aware_net_returns(
            subset,
            horizon_bars=horizon_bars,
            stop_atr_mult=stop_atr_mult,
            cost=cost,
        )
        # Slice mask and validity
        slice_mask = (subset[state_column].to_numpy() == candidate.state)
        valid_long = np.isfinite(net_long)
        valid_short = np.isfinite(net_short)
        slice_mask_long = slice_mask & valid_long
        slice_mask_short = slice_mask & valid_short

        # --- Side-selection leakage fix: choose direction on training window only ---
        n_total = len(subset)
        train_end = int(max(1, round(TRAIN_FRACTION * n_total)))
        train_mask = np.zeros(n_total, dtype=bool)
        train_mask[:train_end] = True
        long_train = net_long[slice_mask_long & train_mask]
        short_train = net_short[slice_mask_short & train_mask]
        mean_long_train = float(np.mean(long_train)) if len(long_train) else -1e9
        mean_short_train = float(np.mean(short_train)) if len(short_train) else -1e9
        side_train = "LONG" if mean_long_train >= mean_short_train else "SHORT"

        direction_ok = (str(candidate.side).upper() == side_train)

        # Candidate-side net series
        net_values = net_long if str(candidate.side).upper() == "LONG" else net_short
        valid = np.isfinite(net_values)
        slice_mask = slice_mask & valid

        slice_net = net_values[slice_mask]
        n_slice = int(len(slice_net))
        mean_net = float(np.mean(slice_net)) if n_slice else 0.0
        mean_positive = mean_net > 0.0

        # Symbol-breadth check (pooled illusion fix)
        breadth_ok = _symbol_breadth_ok(subset, slice_mask, net_values)
        # Recency check (latest-fold brittleness fix)
        recency_ok = _recency_ok(subset, slice_mask, net_values)

        # Symbol-level p-value (more conservative than pooled rows)
        # Compute mean net per symbol for slice rows, then t-stat across symbols.
        symbol_means = []
        if "symbol" in subset.columns and n_slice:
            df_sym = subset.loc[slice_mask, ["symbol"]].copy()
            df_sym["net"] = net_values[slice_mask]
            for sym, g in df_sym.groupby("symbol"):
                if len(g) >= BREADTH_MIN_ROWS_PER_SYMBOL:
                    symbol_means.append(float(g["net"].mean()))
        if len(symbol_means) >= 2:
            m = float(np.mean(symbol_means))
            s = float(np.std(symbol_means, ddof=1))
            t_stat = m / (s / math.sqrt(len(symbol_means))) if s > 0 else 0.0
            p_value = _normal_p(t_stat)
        else:
            p_value = float(candidate.p_value)

        # Walk-forward folds + horizon-overlap purge
        fold_ids = np.linspace(0, len(subset), FOLD_COUNT + 1).astype(int)
        fold_results = []
        fold_means = []
        fold_sizes = []

        for fold in range(FOLD_COUNT):
            fold_mask = np.zeros(len(subset), dtype=bool)
            start = int(fold_ids[fold])
            end = int(fold_ids[fold + 1])
            fold_mask[start:end] = True
            # Purge last horizon bars so forward windows do not cross into next fold
            purge = horizon_bars
            if purge > 0 and end > start:
                purge_start = max(start, end - purge)
                fold_mask[purge_start:end] = False

            fold_returns = net_values[slice_mask & fold_mask]
            passed = _fold_pass(fold_returns)
            fold_results.append("1" if passed else "0")
            fold_means.append(float(np.mean(fold_returns)) if len(fold_returns) else 0.0)
            fold_sizes.append(int(len(fold_returns)))

        pattern = "".join(fold_results)
        pass_count = pattern.count("1")
        latest_passes = bool(pattern[-1] == "1") if pattern else False

        strict_required = max(3, int(0.75 * FOLD_COUNT))
        relaxed_required = max(strict_required, min(FOLD_COUNT, max(1, RELAXED_MIN_PASSES)))
        required_passes = int(strict_required if REQUIRE_BONFERRONI else relaxed_required)

        # Replace "latest fold must pass" with (recency OR latest) to reduce brittleness
        temporal_pass = (pass_count >= required_passes) and (recency_ok or latest_passes)
        bonferroni_ok = True
        if REQUIRE_BONFERRONI:
            bonferroni_ok = bool(getattr(candidate, "bonferroni_pass", False))
            temporal_pass = temporal_pass and bonferroni_ok

        # Hostile regime check using the same stop-aware net returns
        hostile_label = "bear" if str(candidate.side).upper() == "LONG" else "bull"
        hostile_mask = slice_mask & (subset["regime_row"].to_numpy() == hostile_label)
        hostile_net = net_values[hostile_mask]
        hostile_n, hostile_mean, confounded, hostile_unproven = _hostile_regime_check(hostile_net)

        asia_n, asia_mean, asia_hit = _session_stats_from_net(subset, slice_mask, SESSION_ASIA, net_values)
        eu_n, eu_mean, eu_hit = _session_stats_from_net(subset, slice_mask, SESSION_EU, net_values)
        us_n, us_mean, us_hit = _session_stats_from_net(subset, slice_mask, SESSION_US, net_values)

        is_validated = (
            temporal_pass
            and direction_ok
            and breadth_ok
            and (not confounded)
            and mean_positive
        )

        # Reasons: include the gate *names* that were not satisfied.
        reasons: list[str] = []
        if not temporal_pass:
            reasons.append("temporal_pass")
        if REQUIRE_BONFERRONI and not bonferroni_ok:
            reasons.append("bonferroni_pass")
        if not direction_ok:
            reasons.append("direction_ok")
        if not breadth_ok:
            reasons.append("breadth_ok")
        if confounded:
            reasons.append("regime_confounded")
        if not mean_positive:
            reasons.append("mean_net<=0")
        fail_reasons = ",".join(reasons)

        validated.append(
            ValidatedSlice(
                slice_id=candidate.slice_id,
                kind=candidate.kind,
                feature=candidate.feature,
                state=int(candidate.state),
                side=str(candidate.side).upper(),
                folds=FOLD_COUNT,
                walk_forward_pass_pattern=pattern,
                walk_forward_pass_count=int(pass_count),
                fold_mean_rets=",".join(f"{value:.6f}" for value in fold_means),
                fold_sizes=",".join(str(size) for size in fold_sizes),
                n=n_slice,
                mean_ret_costadj=float(mean_net),
                p_value=float(p_value),
                validated=bool(is_validated),
                required_passes=int(required_passes),
                latest_fold_passes=bool(latest_passes),
                temporal_pass=bool(temporal_pass),
                direction_ok=bool(direction_ok),
                breadth_ok=bool(breadth_ok),
                recency_ok=bool(recency_ok),
                mean_positive=bool(mean_positive),
                side_train=str(side_train),
                fail_reasons=str(fail_reasons),
                horizon_bars=horizon_bars,
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

        # Treat these as optional so older validated_slices.csv files still read.
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
            # Diagnostics (optional)
            "required_passes",
            "latest_fold_passes",
            "temporal_pass",
            "direction_ok",
            "breadth_ok",
            "recency_ok",
            "mean_positive",
            "side_train",
            "fail_reasons",
        }
        required = set(VALIDATED_HEADERS) - optional
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise RuntimeError("validated slices file has an unsupported schema")

        fieldnames = set(reader.fieldnames or [])
        has_stop = "stop_atr_mult" in fieldnames
        has_hostile = "hostile_n" in fieldnames
        has_unproven = "hostile_unproven" in fieldnames
        has_session = "session_asia_n" in fieldnames
        has_diag = "temporal_pass" in fieldnames or "fail_reasons" in fieldnames

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
                    required_passes=int(row["required_passes"]) if has_diag and row.get("required_passes") else 0,
                    latest_fold_passes=(row.get("latest_fold_passes") == "True") if has_diag else False,
                    temporal_pass=(row.get("temporal_pass") == "True") if has_diag else False,
                    direction_ok=(row.get("direction_ok") == "True") if has_diag else False,
                    breadth_ok=(row.get("breadth_ok") == "True") if has_diag else False,
                    recency_ok=(row.get("recency_ok") == "True") if has_diag else False,
                    mean_positive=(row.get("mean_positive") == "True") if has_diag else False,
                    side_train=str(row.get("side_train") or "") if has_diag else "",
                    fail_reasons=str(row.get("fail_reasons") or "") if has_diag else "",
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
