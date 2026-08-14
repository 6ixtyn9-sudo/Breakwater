"""Price-state features on completed VALR candles.

The research grain is one bar per symbol: OHLCV inputs, descriptive
price-state features, and forward return windows. Features are descriptive
rather than strategy rules; slice discovery tests which feature states carry
stable forward behaviour.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "feat_ext_vs_ma_10",
    "feat_ext_vs_ma_20",
    "feat_ext_vs_ma_50",
    "feat_atr_norm_ext",
    "feat_ret_1",
    "feat_ret_3",
    "feat_ret_5",
    "feat_ret_10",
    "feat_ret_20",
    "feat_realized_vol_20",
    "feat_vol_regime",
    "feat_trend_slope_20",
    "feat_trend_strength_20",
]


def candle_frame(candles) -> pd.DataFrame:
    frame = pd.DataFrame([
        {
            "start": candle.start,
            "open": float(candle.open),
            "high": float(candle.high),
            "low": float(candle.low),
            "close": float(candle.close),
            "volume": float(candle.volume),
        }
        for candle in candles
    ])
    if frame.empty:
        return frame
    return frame.sort_values("start").reset_index(drop=True)


def compute_price_features(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    df = frame.sort_values("start").reset_index(drop=True).copy()
    close = df["close"]
    high = df["high"]
    low = df["low"]

    for period in (10, 20, 50):
        sma = close.rolling(period).mean()
        df[f"feat_ext_vs_ma_{period}"] = (close / sma) - 1.0

    high_low = high - low
    high_close_prev = (high - close.shift(1)).abs()
    low_close_prev = (low - close.shift(1)).abs()
    true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
    atr = true_range.rolling(14).mean()
    sma_20 = close.rolling(20).mean()
    df["feat_atr_norm_ext"] = (close - sma_20) / atr.replace(0, np.nan)

    for period in (1, 3, 5, 10, 20):
        df[f"feat_ret_{period}"] = close.pct_change(period)

    ret_1 = df["feat_ret_1"]
    df["feat_realized_vol_20"] = ret_1.rolling(20).std()
    vol_60 = ret_1.rolling(60).std()
    df["feat_vol_regime"] = df["feat_realized_vol_20"] / vol_60.replace(0, np.nan)

    def slope(series: pd.Series) -> float:
        values = series.to_numpy()
        if len(values) < 20 or not np.isfinite(values).all():
            return np.nan
        x = np.arange(len(values), dtype=float)
        gradient, _ = np.polyfit(x, values, 1)
        return float(gradient / values[-1]) if values[-1] != 0 else np.nan

    def strength(series: pd.Series) -> float:
        values = series.to_numpy()
        if len(values) < 20 or not np.isfinite(values).all():
            return np.nan
        x = np.arange(len(values), dtype=float)
        gradient, intercept = np.polyfit(x, values, 1)
        fitted = gradient * x + intercept
        residuals = np.sum((values - fitted) ** 2)
        total = np.sum((values - np.mean(values)) ** 2)
        return float(1 - (residuals / total)) if total > 0 else np.nan

    df["feat_trend_slope_20"] = close.rolling(20).apply(slope, raw=False)
    df["feat_trend_strength_20"] = close.rolling(20).apply(strength, raw=False)
    return df


def forward_returns(frame: pd.DataFrame, *, horizon: int = 1) -> pd.Series:
    close = frame["close"]
    return close.shift(-horizon) / close - 1.0


def forward_mae_atr(frame: pd.DataFrame, *, horizon: int = 5) -> pd.Series:
    """Max adverse excursion over the next `horizon` bars, in ATR units.

    Long entries risk the lowest low ahead; short entries risk the highest
    high ahead. Values are clipped at 0 and normalised by the 14-bar ATR,
    matching the volatility unit the stop model uses.
    """
    close = frame["close"]
    high = frame["high"]
    low = frame["low"]
    high_low = high - low
    high_close_prev = (high - close.shift(1)).abs()
    low_close_prev = (low - close.shift(1)).abs()
    true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
    atr = true_range.rolling(14).mean()
    fwd_min_low = low.rolling(horizon).min().shift(-horizon)
    fwd_max_high = high.rolling(horizon).max().shift(-horizon)
    mae_long = (close - fwd_min_low) / atr.replace(0, np.nan)
    mae_short = (fwd_max_high - close) / atr.replace(0, np.nan)
    combined = pd.concat([mae_long, mae_short], axis=1).max(axis=1).clip(lower=0.0)
    return combined
