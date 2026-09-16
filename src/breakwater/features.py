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
    # Composite features: cross-feature interactions that capture non-linear
    # relationships single features miss.  Discovery bins these the same way
    # as base features; walk-forward + breadth guards prevent overfitting.
    "feat_vol_trend",       # vol_regime × trend_slope: trending in volatility
    "feat_ret_vol",         # ret_20 × vol_regime: momentum-volatility interaction
    "feat_ext_strength",    # ext_vs_ma_20 × trend_strength: reversion vs trend
    # --- New feature families: fundamentally different signal sources ---
    # Volume features (order flow proxy)
    "feat_vol_sma_ratio",   # volume / SMA(volume,20): unusual volume events
    "feat_buy_vol_ratio",   # (close-low)/(high-low): buying vs selling pressure
    "feat_vol_breakout",    # volume ratio × extension: volume-confirmed breakouts
    # RSI features (momentum oscillator, not trend)
    "feat_rsi_14",          # RSI(14): overbought/oversold
    "feat_rsi_divergence",  # RSI slope vs price slope: momentum divergence
    # Price structure (where price closes in range)
    "feat_close_position",  # (close-low)/(high-low): close location in bar
    "feat_close_pos_ma",    # SMA of close_position: sustained buying/selling
    # Momentum persistence
    "feat_ret_sign_streak", # consecutive same-sign returns: momentum persistence
    "feat_ret_autocorr",    # return autocorrelation: momentum vs mean-reversion regime
    # Session awareness (time-of-day edge)
    "feat_hour_utc",        # hour of day (0-23): session-specific patterns
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

    # Composite features: cross-feature interactions
    # Fill NaN with 0 before multiplying to avoid NaN propagation:
    # if one component is NaN, the composite should be 0 (neutral), not NaN.
    df["feat_vol_trend"] = df["feat_vol_regime"].fillna(0) * df["feat_trend_slope_20"].fillna(0)
    df["feat_ret_vol"] = df["feat_ret_20"].fillna(0) * df["feat_vol_regime"].fillna(0)
    df["feat_ext_strength"] = df["feat_ext_vs_ma_20"].fillna(0) * df["feat_trend_strength_20"].fillna(0)

    # --- New feature families ---

    # Volume features: order flow proxy
    vol = df["volume"].astype(float)
    vol_sma20 = vol.rolling(20).mean()
    df["feat_vol_sma_ratio"] = vol / vol_sma20.replace(0, np.nan)
    bar_range = (high - low).replace(0, np.nan)
    df["feat_buy_vol_ratio"] = (close - low) / bar_range
    # Volume breakout: volume surge × price extension (volume confirms breakout)
    df["feat_vol_breakout"] = (
        df["feat_vol_sma_ratio"].fillna(0) * df["feat_ext_vs_ma_20"].fillna(0)
    )

    # RSI features: momentum oscillator
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_gain = gain.ewm(span=14, adjust=False).mean()
    avg_loss = loss.ewm(span=14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["feat_rsi_14"] = 100.0 - (100.0 / (1.0 + rs))

    # RSI divergence: RSI slope vs price slope (when they disagree = divergence)
    def _slope_14(series: pd.Series) -> float:
        values = series.to_numpy()
        if len(values) < 14 or not np.isfinite(values).all():
            return np.nan
        x = np.arange(len(values), dtype=float)
        gradient, _ = np.polyfit(x, values, 1)
        return float(gradient)

    rsi_slope = df["feat_rsi_14"].rolling(14).apply(_slope_14, raw=False)
    price_slope = close.rolling(14).apply(_slope_14, raw=False)
    # Normalize slopes by their magnitude for comparability
    df["feat_rsi_divergence"] = rsi_slope - price_slope.fillna(0)

    # Price structure: where price closes in its range
    df["feat_close_position"] = (close - low) / bar_range
    df["feat_close_pos_ma"] = df["feat_close_position"].rolling(10).mean()

    # Momentum persistence: consecutive same-sign returns
    def _sign_streak(returns: pd.Series) -> float:
        """Count consecutive same-sign returns ending at current bar."""
        signs = np.sign(returns.to_numpy())
        streak = 0.0
        for s in reversed(signs):
            if np.isnan(s) or s == 0:
                break
            if streak == 0:
                streak = s
            elif np.sign(streak) == np.sign(s):
                streak += np.sign(streak)
            else:
                break
        return streak

    df["feat_ret_sign_streak"] = ret_1.rolling(20).apply(_sign_streak, raw=False)

    # Return autocorrelation: positive = momentum, negative = mean-reversion
    df["feat_ret_autocorr"] = ret_1.rolling(20).apply(
        lambda x: float(pd.Series(x).autocorr(lag=1)) if len(x) >= 5 else np.nan,
        raw=False,
    )

    # Session awareness: hour of day (for session-specific pattern discovery)
    if "start" in df.columns:
        df["feat_hour_utc"] = pd.to_datetime(df["start"]).dt.hour.astype(float)

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
