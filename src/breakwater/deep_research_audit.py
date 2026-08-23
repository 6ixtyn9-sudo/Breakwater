"""Manual deep-history challenger for native PERP and HIP-3 research.

Outputs are local, Git-ignored audit artifacts. This module cannot promote,
paper-trade, or execute. It reuses Breakwater's feature, state, stop and return
logic while testing 5,000 bars, horizons 1-48 and a frozen recency weighting.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
import time
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd

from breakwater.discovery import _slice_stats, prepare_pooled
from breakwater.features import FEATURE_COLUMNS, candle_frame, compute_price_features
from breakwater.hip3 import read_hip3_universe
from breakwater.hip3_research import _candidate_rows
from breakwater.hyperliquid import HyperliquidReadOnlyVenue
from breakwater.perpdata import fetch_perp_candles
from breakwater.validation import _calibrate_stop_atr_mult

WEIGHTS = (1.0, 0.5, 0.25, 0.125, 0.0625)
AUDIT_HEADERS = [
    "lane", "group", "feature", "state", "side", "horizon_bars", "n",
    "recent_n", "recent_1000_mean", "full_5000_mean", "weighted_5000_mean",
    "weighted_effective_n", "block_bootstrap_p", "symbols_used",
    "positive_symbol_fraction", "cluster_count", "positive_cluster_fraction",
    "stop_atr_mult", "preliminary_pass", "plateau_start", "plateau_end",
    "plateau_width", "audit_pass", "blockers",
]


@dataclass(frozen=True)
class AuditGroup:
    lane: str
    name: str
    coins: tuple[str, ...]
    cost_bps: float


def _atomic_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=AUDIT_HEADERS)
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def _weights(age: np.ndarray) -> np.ndarray:
    buckets = np.minimum(np.floor(age / 1000).astype(int), 4)
    return np.asarray([WEIGHTS[index] for index in buckets], dtype=float)


def _block_bootstrap_p(frame: pd.DataFrame, *, seed_text: str, replicates: int = 300) -> float:
    if frame.empty:
        return 1.0
    stamps = pd.to_datetime(frame["start"], utc=True)
    origin = stamps.min()
    blocks = ((stamps - origin).dt.total_seconds() // (48 * 3600)).astype(int)
    work = frame.assign(_block=blocks)
    aggregated = work.groupby("_block").apply(
        lambda group: pd.Series(
            {
                "weighted_sum": float((group["net"] * group["weight"]).sum()),
                "weight": float(group["weight"].sum()),
            }
        ),
        include_groups=False,
    )
    if len(aggregated) < 3:
        return 1.0
    seed = int(hashlib.sha256(seed_text.encode()).hexdigest()[:16], 16)
    rng = np.random.default_rng(seed)
    indexes = rng.integers(0, len(aggregated), size=(replicates, len(aggregated)))
    sums = aggregated["weighted_sum"].to_numpy()[indexes].sum(axis=1)
    denominators = aggregated["weight"].to_numpy()[indexes].sum(axis=1)
    means = np.divide(sums, denominators, out=np.zeros_like(sums), where=denominators > 0)
    return float((np.count_nonzero(means <= 0) + 1) / (replicates + 1))


def _cluster_breadth(frame: pd.DataFrame) -> tuple[int, float]:
    symbol_means = frame.groupby("symbol")["net"].mean()
    symbols = list(symbol_means.index)
    if not symbols:
        return 0, 0.0
    if len(symbols) == 1:
        return 1, float(symbol_means.iloc[0] > 0)
    pivot = frame.pivot_table(index="start", columns="symbol", values="net", aggfunc="mean")
    correlation = pivot.corr(min_periods=10)
    parent = {symbol: symbol for symbol in symbols}

    def find(symbol):
        while parent[symbol] != symbol:
            parent[symbol] = parent[parent[symbol]]
            symbol = parent[symbol]
        return symbol

    def union(left, right):
        a, b = find(left), find(right)
        if a != b:
            parent[b] = a

    for index, left in enumerate(symbols):
        for right in symbols[index + 1 :]:
            value = correlation.loc[left, right] if left in correlation.index and right in correlation else np.nan
            if np.isfinite(value) and value >= 0.80:
                union(left, right)
    clusters: dict[str, list[float]] = {}
    for symbol in symbols:
        clusters.setdefault(find(symbol), []).append(float(symbol_means[symbol]))
    positives = sum(float(np.mean(values)) > 0 for values in clusters.values())
    return len(clusters), positives / len(clusters)


def _net_returns_from_prepared(
    subset: pd.DataFrame, *, stop_atr_mult: float, cost: float
) -> tuple[np.ndarray, np.ndarray]:
    """Use horizon columns already computed by ``prepare_pooled``.

    Validation recomputes ATR and forward rolling extremes for each candidate.
    In the 48-horizon audit that repeats identical expensive work hundreds of
    times. These prepared columns are mathematically identical and vary only by
    horizon, while stop distance remains candidate-specific.
    """
    close = subset["close"].to_numpy(dtype=float)
    atr = subset["atr_14"].to_numpy(dtype=float)
    fwd_close = subset["fwd_close_h"].to_numpy(dtype=float)
    fwd_min = subset["fwd_min_low_h"].to_numpy(dtype=float)
    fwd_max = subset["fwd_max_high_h"].to_numpy(dtype=float)

    stop_long = close - stop_atr_mult * atr
    target_long = close + 2.0 * (close - stop_long)
    exit_long = np.where(fwd_max >= target_long, target_long, fwd_close)
    exit_long = np.where(fwd_min <= stop_long, stop_long, exit_long)
    net_long = (exit_long - close) / close - cost

    stop_short = close + stop_atr_mult * atr
    target_short = close - 2.0 * (stop_short - close)
    exit_short = np.where(fwd_min <= target_short, target_short, fwd_close)
    exit_short = np.where(fwd_max >= stop_short, stop_short, exit_short)
    net_short = (exit_short - close) / close * -1.0 - cost

    # Match validation exactly: unavailable early ATR/extremes simply mean no
    # stop/target hit and fall through to the finite horizon close.
    invalid = ~(np.isfinite(close) & np.isfinite(fwd_close))
    net_long[invalid] = np.nan
    net_short[invalid] = np.nan
    return net_long, net_short


def _evaluate(prepared: pd.DataFrame, candidate, *, lane: str, group: str) -> dict:
    state_column = f"state_{candidate.feature}"
    subset = prepared.dropna(subset=[state_column, "close", "high", "low", "bar_age"])
    subset = subset.sort_values("start").reset_index(drop=True)
    stop = float(_calibrate_stop_atr_mult(prepared, candidate, state_column))
    cost = float(subset["cost"].iloc[0]) if len(subset) else 0.0
    long_net, short_net = _net_returns_from_prepared(
        subset, stop_atr_mult=stop, cost=cost
    )
    values = long_net if str(candidate.side).upper() == "LONG" else short_net
    mask = (subset[state_column].to_numpy() == candidate.state) & np.isfinite(values)
    selected = subset.loc[mask, ["start", "symbol", "bar_age"]].copy()
    selected["net"] = values[mask]
    selected["weight"] = _weights(selected["bar_age"].to_numpy(dtype=float))
    n = len(selected)
    recent = selected[selected["bar_age"] < 1000]
    full_mean = float(selected["net"].mean()) if n else 0.0
    recent_mean = float(recent["net"].mean()) if len(recent) else 0.0
    weight_sum = float(selected["weight"].sum())
    weighted_mean = (
        float((selected["net"] * selected["weight"]).sum() / weight_sum) if weight_sum else 0.0
    )
    weight_sq = float((selected["weight"] ** 2).sum())
    effective_n = weight_sum * weight_sum / weight_sq if weight_sq else 0.0
    symbol_means = selected.groupby("symbol")["net"].mean() if n else pd.Series(dtype=float)
    positive_fraction = float((symbol_means > 0).mean()) if len(symbol_means) else 0.0
    preliminary = bool(
        len(recent) >= 60
        and recent_mean > 0
        and weighted_mean > 0
        and full_mean > -0.001
        and effective_n >= 200
        and len(symbol_means) >= 6
        and positive_fraction >= 0.40
    )
    bootstrap_p = 1.0
    cluster_count = 0
    positive_cluster_fraction = 0.0
    if preliminary:
        identity = f"{lane}|{group}|{candidate.feature}|{candidate.state}|{candidate.side}|{candidate.horizon_bars}"
        bootstrap_p = _block_bootstrap_p(selected, seed_text=identity)
        cluster_count, positive_cluster_fraction = _cluster_breadth(selected)
        preliminary = bool(
            bootstrap_p <= 0.20
            and cluster_count >= 2
            and positive_cluster_fraction >= 0.50
        )
    blockers = [
        "selection_holdout_not_complete",
        "funding_not_modeled",
        "slippage_not_modeled",
        "point_in_time_universe_incomplete",
    ]
    if lane == "hip3":
        blockers.extend(
            ["historical_oracle_quality_missing", "calendar_model_missing", "cost_model_provisional"]
        )
    return {
        "lane": lane,
        "group": group,
        "feature": candidate.feature,
        "state": candidate.state,
        "side": candidate.side,
        "horizon_bars": candidate.horizon_bars,
        "n": n,
        "recent_n": len(recent),
        "recent_1000_mean": f"{recent_mean:.10f}",
        "full_5000_mean": f"{full_mean:.10f}",
        "weighted_5000_mean": f"{weighted_mean:.10f}",
        "weighted_effective_n": f"{effective_n:.2f}",
        "block_bootstrap_p": f"{bootstrap_p:.6f}",
        "symbols_used": len(symbol_means),
        "positive_symbol_fraction": f"{positive_fraction:.6f}",
        "cluster_count": cluster_count,
        "positive_cluster_fraction": f"{positive_cluster_fraction:.6f}",
        "stop_atr_mult": f"{stop:.6f}",
        "preliminary_pass": preliminary,
        "plateau_start": "",
        "plateau_end": "",
        "plateau_width": 0,
        "audit_pass": False,
        "blockers": ",".join(blockers),
    }


def _attach_plateaus(rows: list[dict]) -> None:
    families: dict[tuple, list[dict]] = {}
    for row in rows:
        key = (row["lane"], row["group"], row["feature"], row["state"], row["side"])
        families.setdefault(key, []).append(row)
    for family in families.values():
        by_horizon = {int(row["horizon_bars"]): row for row in family}
        passing = sorted(h for h, row in by_horizon.items() if row["preliminary_pass"])
        runs: list[list[int]] = []
        for horizon in passing:
            if not runs or horizon != runs[-1][-1] + 1:
                runs.append([horizon])
            else:
                runs[-1].append(horizon)
        for run in runs:
            if len(run) < 3:
                continue
            for horizon in run:
                row = by_horizon[horizon]
                row["plateau_start"] = run[0]
                row["plateau_end"] = run[-1]
                row["plateau_width"] = len(run)
                row["audit_pass"] = True


def _fetch_group(
    group: AuditGroup, *, candle_count: int, sleep_seconds: float
) -> tuple[pd.DataFrame, dict[str, str]]:
    parts = []
    errors: dict[str, str] = {}
    for coin in group.coins:
        candles = None
        last_error = None
        for attempt in range(3):
            try:
                candles = fetch_perp_candles(coin, interval="1h", count=candle_count)
                break
            except Exception as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(0.5 * (attempt + 1))
        if candles is None:
            errors[coin] = f"{type(last_error).__name__}: {last_error}"[:180]
            continue
        frame = candle_frame(candles).sort_values("start").drop_duplicates("start")
        if len(frame) < min(3000, int(candle_count * 0.75)):
            errors[coin] = f"insufficient_history:{len(frame)}"
            continue
        featured = compute_price_features(frame)
        featured["symbol"] = coin
        featured["bar_age"] = np.arange(len(featured) - 1, -1, -1)
        parts.append(featured)
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)
    pooled = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    return pooled, errors


def _groups(lane: str, *, max_pairs: int, data_dir: Path) -> list[AuditGroup]:
    venue = HyperliquidReadOnlyVenue()
    native = sorted(
        (item for item in venue.instruments() if item.active),
        key=lambda item: (-item.day_notional_volume, item.coin),
    )
    groups = []
    if lane in {"native", "all"}:
        groups.append(
            AuditGroup("native", "native_crypto_c0", tuple(item.coin for item in native[:max_pairs]), 26.0)
        )
    if lane in {"hip3", "all"}:
        universe = read_hip3_universe(data_dir / "hip3" / "universe.csv")
        if universe is None:
            raise RuntimeError("HIP-3 universe is missing; run hip3-discover first")
        native_coins = {item.coin.upper() for item in native}
        selected = _candidate_rows(
            universe.rows,
            native_crypto=native_coins,
            max_pairs=max_pairs,
            max_oracle_deviation=Decimal("0.02"),
        )
        grouped: dict[str, list[str]] = {}
        for row, market_class in selected:
            name = f"{row.dex}_{market_class}_c{row.collateral_token}"
            grouped.setdefault(name, []).append(row.coin)
        groups.extend(
            AuditGroup("hip3", name, tuple(coins), 30.0)
            for name, coins in sorted(grouped.items())
        )
    return groups


def run_deep_research_audit(
    *, lane: str,
    data_dir: Path,
    output_dir: Path,
    max_pairs: int = 60,
    candle_count: int = 5000,
) -> dict:
    if lane not in {"native", "hip3", "all"}:
        raise ValueError("deep audit lane must be native, hip3, or all")
    groups = _groups(lane, max_pairs=max_pairs, data_dir=data_dir)
    rows = []
    group_summary = {}
    fetch_errors: dict[str, str] = {}
    sleep_seconds = float(os.getenv("BREAKWATER_CANDLE_PAGE_SLEEP_SECONDS", "0.05"))
    for group in groups:
        pooled, errors = _fetch_group(
            group, candle_count=candle_count, sleep_seconds=sleep_seconds
        )
        fetch_errors.update(errors)
        group_summary[f"{group.lane}:{group.name}"] = (
            int(pooled["symbol"].nunique()) if not pooled.empty else 0
        )
        if pooled.empty:
            continue
        for horizon in range(1, 49):
            prepared = prepare_pooled(
                pooled, FEATURE_COLUMNS, group.cost_bps, horizon_bars=horizon
            )
            candidates = _slice_stats(
                prepared, f"DEEP_{group.name.upper()}", FEATURE_COLUMNS, horizon_bars=horizon
            )
            rows.extend(
                _evaluate(prepared, candidate, lane=group.lane, group=group.name)
                for candidate in candidates
            )
    if not any(group_summary.values()):
        detail = "; ".join(f"{coin}={error}" for coin, error in list(fetch_errors.items())[:5])
        raise RuntimeError(f"deep audit fetched no usable candle histories: {detail}")
    _attach_plateaus(rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    _atomic_csv(output_dir / "candidates.csv", rows)
    summary = {
        "lane": lane,
        "promotion_enabled": False,
        "candles_requested": candle_count,
        "horizons": [1, 48],
        "weights_per_1000_hours": list(WEIGHTS),
        "groups": group_summary,
        "fetch_error_count": len(fetch_errors),
        "fetch_errors": fetch_errors,
        "candidates": len(rows),
        "preliminary_passes": sum(bool(row["preliminary_pass"]) for row in rows),
        "plateau_passes": sum(bool(row["audit_pass"]) for row in rows),
        "families_with_plateaus": len(
            {
                (row["lane"], row["group"], row["feature"], row["state"], row["side"])
                for row in rows
                if row["audit_pass"]
            }
        ),
        "output": str(output_dir / "candidates.csv"),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary
