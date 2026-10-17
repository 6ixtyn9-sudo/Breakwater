"""Market-neutral spread evidence (research-only, advisory).

Why this exists
---------------
Residualized discovery (see ``discovery.py``) showed that the strongest
benchmark-relative edge in the book is often a SHORT that fails validation on
exactly one gate, ``mean_net<=0``: the raw mean is negative because the
sample's market drift is positive.  ``mean_positive`` on raw returns is the
right gate for an *outright* directional trade, but it is itself a beta gate --
it admits longs in bull samples and rejects shorts in them.  A cross-sectional
signal traded outright is beta-dependent by construction.

The instrument that captures a cross-sectional signal *without* beta is the
spread: long the symbols in one state, short the symbols in the opposite
state, dollar-neutral, same horizon, same stop rule, on perps.  This module
measures that spread on the pooled research frames so the operator can see --
before any engine is built -- whether it is worth building.

What it computes
----------------
For each feature and each pairing (long state 2 / short state 0, and the
reverse), per bar ``t``:

    long_leg(t)  = mean fwd_trade_net_long  over symbols in long_state  at t
    short_leg(t) = mean fwd_trade_net_short over symbols in short_state at t
    spread(t)    = 0.5 * (long_leg(t) + short_leg(t))

``spread`` is the return per unit of gross notional (half long, half short).
Both legs are the same stop-aware, cost-adjusted trade model the directional
research uses, so a 9 bps perp round trip is paid on each leg.  Bars with
fewer than ``MIN_LEG_SYMBOLS`` names on either side are skipped.

Statistics are reported on the per-bar series and -- because hourly bars with
an ``h``-bar horizon overlap -- also on a stride-``h`` non-overlapping
subsample (``t_nonoverlap``).  Walk-forward folds, worst fold, recency, max
drawdown and correlation with the universe return (neutrality check) round it
out.  ``qualifies`` is the suggested go/no-go flag; it feeds no gate.

Not modelled (blockers for any live decision): funding payments, borrow (n/a
on perps), execution slippage on thin names, and leg-fill asymmetry.
"""

from __future__ import annotations

import math
import os
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

SPREAD_HEADERS = [
    "spread_id",
    "kind",
    "feature",
    "long_state",
    "short_state",
    "horizon_bars",
    "n_bars",
    "n_nonoverlap",
    "mean_ret_costadj",
    "long_leg_mean",
    "short_leg_mean",
    "hit_rate",
    "t_naive",
    "t_nonoverlap",
    "fold_pattern",
    "fold_pass_count",
    "worst_fold_mean",
    "recent_mean",
    "max_drawdown",
    "market_corr",
    "avg_n_long",
    "avg_n_short",
    "qualifies",
    "fail_reasons",
]


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


MIN_LEG_SYMBOLS = max(2, _env_int("BREAKWATER_SPREAD_MIN_LEG_SYMBOLS", 3))
FOLD_COUNT = 5
MIN_NONOVERLAP = max(10, _env_int("BREAKWATER_SPREAD_MIN_NONOVERLAP", 30))
MIN_T_NONOVERLAP = _env_float("BREAKWATER_SPREAD_MIN_T", 2.0)
MIN_FOLD_PASSES = max(1, _env_int("BREAKWATER_SPREAD_MIN_FOLD_PASSES", 4))
MAX_MARKET_CORR = _env_float("BREAKWATER_SPREAD_MAX_MARKET_CORR", 0.30)
RECENCY_FRACTION = 0.20
PAIRINGS: tuple[tuple[int, int], ...] = ((2, 0), (0, 2))


@dataclass(frozen=True)
class SpreadStat:
    spread_id: str
    kind: str
    feature: str
    long_state: int
    short_state: int
    horizon_bars: int
    n_bars: int
    n_nonoverlap: int
    mean_ret_costadj: float
    long_leg_mean: float
    short_leg_mean: float
    hit_rate: float
    t_naive: float
    t_nonoverlap: float
    fold_pattern: str
    fold_pass_count: int
    worst_fold_mean: float
    recent_mean: float
    max_drawdown: float
    market_corr: float
    avg_n_long: float
    avg_n_short: float
    qualifies: bool
    fail_reasons: str


def _t_stat(values: np.ndarray) -> float:
    values = values[np.isfinite(values)]
    n = len(values)
    if n < 2:
        return 0.0
    sd = float(np.std(values, ddof=1))
    if sd <= 0:
        return 0.0
    return float(np.mean(values)) / (sd / math.sqrt(n))


def _max_drawdown(values: np.ndarray) -> float:
    if len(values) == 0:
        return 0.0
    equity = np.cumsum(values)
    peak = np.maximum.accumulate(np.concatenate([[0.0], equity]))[1:]
    return float(np.max(peak - equity)) if len(equity) else 0.0


def _leg_series(
    frame: pd.DataFrame,
    state_column: str,
    state: int,
    value_column: str,
    codes: np.ndarray,
    n_groups: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Per-bar mean of ``value_column`` over rows in ``state``; (mean, count)."""
    values = frame[value_column].to_numpy(dtype=float)
    in_state = (frame[state_column].to_numpy(dtype=float) == float(state)) & np.isfinite(values)
    total = np.bincount(codes[in_state], weights=values[in_state], minlength=n_groups)
    count = np.bincount(codes[in_state], minlength=n_groups).astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        mean = np.where(count > 0, total / np.where(count > 0, count, 1.0), np.nan)
    return mean, count


def spread_stats(
    prepared: pd.DataFrame,
    *,
    kind: str,
    feature_columns: list[str],
    horizon_bars: int,
) -> list[SpreadStat]:
    """Compute dollar-neutral spread evidence for every feature and pairing."""
    required = {"start", "symbol", "fwd_trade_net_long", "fwd_trade_net_short"}
    if prepared is None or prepared.empty or not required <= set(prepared.columns):
        return []

    from breakwater.discovery import _group_codes

    frame = prepared.sort_values("start").reset_index(drop=True)
    codes, n_groups = _group_codes(frame["start"])
    # Bar order == first appearance order after the sort above.
    first_pos = np.full(n_groups, -1, dtype=np.int64)
    seen = np.zeros(n_groups, dtype=bool)
    for position, code in enumerate(codes):
        if not seen[code]:
            seen[code] = True
            first_pos[code] = position
    bar_order = np.argsort(first_pos)

    # Universe return per bar for the neutrality check.
    if "fwd_ret_raw" in frame.columns:
        raw = frame["fwd_ret_raw"].to_numpy(dtype=float)
        ok = np.isfinite(raw)
        tot = np.bincount(codes[ok], weights=raw[ok], minlength=n_groups)
        cnt = np.bincount(codes[ok], minlength=n_groups).astype(float)
        with np.errstate(divide="ignore", invalid="ignore"):
            market = np.where(cnt > 0, tot / np.where(cnt > 0, cnt, 1.0), np.nan)
    else:
        market = np.full(n_groups, np.nan)

    out: list[SpreadStat] = []
    stride = max(1, int(horizon_bars))

    for feature in feature_columns:
        state_column = f"state_{feature}"
        if state_column not in frame.columns:
            continue
        for long_state, short_state in PAIRINGS:
            long_mean, long_n = _leg_series(frame, state_column, long_state, "fwd_trade_net_long", codes, n_groups)
            short_mean, short_n = _leg_series(frame, state_column, short_state, "fwd_trade_net_short", codes, n_groups)

            valid = (long_n >= MIN_LEG_SYMBOLS) & (short_n >= MIN_LEG_SYMBOLS)
            valid &= np.isfinite(long_mean) & np.isfinite(short_mean)
            order = bar_order[valid[bar_order]]
            n_bars = int(len(order))
            if n_bars == 0:
                continue

            long_leg = long_mean[order]
            short_leg = short_mean[order]
            spread = 0.5 * (long_leg + short_leg)
            mkt = market[order]

            mean = float(np.mean(spread))
            hit = float(np.mean(spread > 0))
            t_naive = _t_stat(spread)

            non_overlap = spread[::stride]
            n_nonoverlap = int(len(non_overlap))
            t_non = _t_stat(non_overlap)

            # Walk-forward folds with horizon purge at each fold end.
            fold_edges = np.linspace(0, n_bars, FOLD_COUNT + 1).astype(int)
            pattern = []
            fold_means = []
            for fold in range(FOLD_COUNT):
                start, end = int(fold_edges[fold]), int(fold_edges[fold + 1])
                end_purged = max(start, end - stride) if fold < FOLD_COUNT - 1 else end
                chunk = spread[start:end_purged]
                if len(chunk) == 0:
                    pattern.append("0")
                    fold_means.append(0.0)
                    continue
                fm = float(np.mean(chunk))
                fold_means.append(fm)
                pattern.append("1" if fm > 0 else "0")
            fold_pattern = "".join(pattern)
            fold_pass_count = fold_pattern.count("1")
            worst_fold = float(min(fold_means)) if fold_means else 0.0

            recent_n = max(1, int(round(RECENCY_FRACTION * n_bars)))
            recent_mean = float(np.mean(spread[-recent_n:]))

            drawdown = _max_drawdown(non_overlap)

            finite_mkt = np.isfinite(mkt)
            if finite_mkt.sum() >= 3 and np.std(spread[finite_mkt]) > 0 and np.std(mkt[finite_mkt]) > 0:
                market_corr = float(np.corrcoef(spread[finite_mkt], mkt[finite_mkt])[0, 1])
            else:
                market_corr = 0.0

            reasons: list[str] = []
            if n_nonoverlap < MIN_NONOVERLAP:
                reasons.append("n_nonoverlap")
            if mean <= 0:
                reasons.append("mean<=0")
            if t_non < MIN_T_NONOVERLAP:
                reasons.append("t_nonoverlap")
            if fold_pass_count < MIN_FOLD_PASSES:
                reasons.append("folds")
            if abs(market_corr) > MAX_MARKET_CORR:
                reasons.append("market_corr")
            qualifies = not reasons

            out.append(
                SpreadStat(
                    spread_id=f"{feature}:L{long_state}S{short_state}:h{int(horizon_bars)}",
                    kind=str(kind),
                    feature=str(feature),
                    long_state=int(long_state),
                    short_state=int(short_state),
                    horizon_bars=int(horizon_bars),
                    n_bars=n_bars,
                    n_nonoverlap=n_nonoverlap,
                    mean_ret_costadj=mean,
                    long_leg_mean=float(np.mean(long_leg)),
                    short_leg_mean=float(np.mean(short_leg)),
                    hit_rate=hit,
                    t_naive=t_naive,
                    t_nonoverlap=t_non,
                    fold_pattern=fold_pattern,
                    fold_pass_count=int(fold_pass_count),
                    worst_fold_mean=worst_fold,
                    recent_mean=recent_mean,
                    max_drawdown=drawdown,
                    market_corr=market_corr,
                    avg_n_long=float(np.mean(long_n[order])),
                    avg_n_short=float(np.mean(short_n[order])),
                    qualifies=bool(qualifies),
                    fail_reasons=",".join(reasons),
                )
            )

    return sorted(out, key=lambda s: (not s.qualifies, -s.t_nonoverlap))


def write_spreads(path, rows: list[SpreadStat]) -> None:
    """Atomic CSV write; always writes a header so shard uploads never miss."""
    from pathlib import Path

    from breakwater.discovery import _write_slice_rows

    _write_slice_rows(Path(path), [asdict(row) for row in rows], SPREAD_HEADERS)


def read_spreads(path) -> list[dict]:
    import csv
    from pathlib import Path

    path = Path(path)
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))
