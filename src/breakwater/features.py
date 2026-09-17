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
    # --- NEW: Neutral-regime & Asia-session features (Sep 17) ---
    # Range trading: position in 20-bar high/low range, best for 66% neutral regime
    "feat_range_pos_20",    # (close - low20)/(high20 - low20): 0=low, 1=high
    "feat_bb_width_20",     # (BB_upper - BB_lower)/SMA20: bandwidth, low=squeeze
    "feat_bb_pos_20",       # (close - BB_lower)/(BB_upper - BB_lower): pos in BB
    "feat_atr_ratio",       # ATR14/ATR50: <1 contraction, >1 expansion
    "feat_squeeze",         # bb_width * atr_ratio: low=squeeze, breakout imminent
    "feat_time_since_high_20", # bars since 20-bar high /20: 0=at high
    "feat_time_since_low_20",  # bars since 20-bar low /20: 0=at low
    "feat_vol_contraction", # realized_vol20 / realized_vol60: <1 contraction
    "feat_trend_neutral",   # 1 - abs(slope)/0.001 clipped: 1=neutral, 0=trending
    "feat_asia_vol",        # vol_regime when Asia (0-7 UTC) else 0: Asia low vol
    "feat_donchian_break",  # (close - high20_prev)/ATR: breakout strength
    "feat_mean_rev_strength", # -ext_vs_ma_20 / realized_vol: mean reversion strength
    # --- NEW: Gap & Intraday features for HIP-3 & native (Sep 17) ---
    "feat_gap",             # (open - close_prev)/ATR: overnight gap
    "feat_intraday_mom",    # (close - open)/(high - low): intraday momentum
    "feat_hl_range",        # (high - low)/close: high-low range
    "feat_overnight_ret",   # (open - close_prev)/close_prev: overnight return
    "feat_vol_of_vol",      # std(realized_vol_20,20): vol of vol
    "feat_price_accel",     # ret_1 - ret_1_prev: price acceleration
    "feat_vol_breakout_strength", # vol_sma_ratio * abs(ret_1): volume-confirmed move
    # --- NEW: Additional neutral & intraday features (Sep 17) - 10 more for 66% neutral ---
    "feat_zscore_20",       # (close - SMA20)/std20: z-score mean reversion
    "feat_stoch_k_14",      # (close - low14)/(high14 - low14): stochastic %K
    "feat_williams_r_14",   # (high14 - close)/(high14 - low14): Williams %R
    "feat_rsi_7",           # RSI(7): short-term momentum
    "feat_vwap_dist",       # (close - VWAP)/VWAP: distance from VWAP
    "feat_range_expansion", # (high-low)/ATR14: range expansion vs ATR
    "feat_gap_fill_ratio",  # (close - open)/(open - close_prev): gap fill
    "feat_keltner_pos",     # (close - KC_lower)/(KC_upper - KC_lower): Keltner pos
    "feat_cci_20",          # CCI(20): commodity channel index for range
    "feat_adx_14",          # ADX(14): trend strength, low=neutral regime
    # --- NEW: 15 more for 70 total — universal neutral & Asia session ---
    "feat_atr_percent",     # ATR14/close: ATR as % of price
    "feat_kc_width",        # (KC_upper - KC_lower)/EMA20: Keltner width
    "feat_bb_squeeze_20",   # BB_width / KC_width: squeeze indicator
    "feat_vol_roc_20",      # volume / volume_prev_20 -1: volume ROC
    "feat_price_roc_5",     # close / close_prev_5 -1: price ROC 5
    "feat_ema_cross_10_20", # EMA10 - EMA20 / close: EMA cross
    "feat_macd_12_26",      # EMA12 - EMA26: MACD line
    "feat_donchian_width_20", # (high20 - low20)/ATR: Donchian width
    "feat_asia_range",      # hl_range when Asia else 0: Asia session range
    "feat_session_mom",     # intraday_mom * vol_regime: session momentum
    "feat_vwap_upper_dist", # (high - VWAP)/VWAP: upper wick vs VWAP
    "feat_vwap_lower_dist", # (low - VWAP)/VWAP: lower wick vs VWAP
    "feat_rsi_21",          # RSI(21): longer momentum
    "feat_stoch_d_14",      # SMA(stoch_k_14,3): stochastic %D
    "feat_range_pos_50",    # (close - low50)/(high50 - low50): longer range pos
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
        # Optimized: use linear regression formula instead of polyfit
        # x = 0..19, mean_x=9.5, var_x constant
        # gradient = cov(x,y)/var(x), we compute via dot product
        # This is ~5x faster than np.polyfit
        x = np.arange(20, dtype=float)
        y = values
        # Use precomputed denominator for x=0..19
        # sum_x=190, sum_x2=2470, n=20, denom=13300
        sum_y = np.sum(y)
        sum_xy = np.dot(x, y)
        # numerator = n*sum_xy - sum_x*sum_y
        numerator = 20 * sum_xy - 190 * sum_y
        gradient = numerator / 13300.0
        return float(gradient / y[-1]) if y[-1] != 0 else np.nan

    def strength(series: pd.Series) -> float:
        values = series.to_numpy()
        if len(values) < 20 or not np.isfinite(values).all():
            return np.nan
        # Optimized R^2 calculation without polyfit
        x = np.arange(20, dtype=float)
        y = values
        sum_y = np.sum(y)
        sum_xy = np.dot(x, y)
        sum_x = 190.0
        sum_x2 = 2470.0
        n = 20.0
        # slope
        numerator = n * sum_xy - sum_x * sum_y
        gradient = numerator / 13300.0
        intercept = (sum_y - gradient * sum_x) / n
        fitted = gradient * x + intercept
        residuals = np.sum((y - fitted) ** 2)
        total = np.sum((y - np.mean(y)) ** 2)
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
    else:
        df["feat_hour_utc"] = np.nan

    # --- NEW: Neutral-regime & Asia-session features (Sep 17) ---
    # Range position: (close - low20)/(high20 - low20), 0=at low, 1=at high
    high_20 = high.rolling(20).max()
    low_20 = low.rolling(20).min()
    range_20 = (high_20 - low_20).replace(0, np.nan)
    df["feat_range_pos_20"] = (close - low_20) / range_20

    # Bollinger Bands: width and position
    sma_20 = close.rolling(20).mean()
    std_20 = close.rolling(20).std()
    bb_upper = sma_20 + 2.0 * std_20
    bb_lower = sma_20 - 2.0 * std_20
    bb_range = (bb_upper - bb_lower).replace(0, np.nan)
    df["feat_bb_width_20"] = (bb_upper - bb_lower) / sma_20.replace(0, np.nan)
    df["feat_bb_pos_20"] = (close - bb_lower) / bb_range

    # ATR ratio: ATR14 / ATR50, <1 contraction, >1 expansion
    atr_50 = true_range.rolling(50).mean()
    df["feat_atr_ratio"] = atr / atr_50.replace(0, np.nan)

    # Squeeze: bb_width * atr_ratio, low = squeeze
    df["feat_squeeze"] = df["feat_bb_width_20"].fillna(0) * df["feat_atr_ratio"].fillna(0)

    # Time since high/low — OPTIMIZED O(n) instead of rolling apply O(n*window)
    # Previous version used rolling(20).apply(argmax) which is very slow for 38 features.
    # New: vectorized loop tracking last high/low occurrence.
    high_20_for_time = high_20  # from above
    low_20_for_time = low_20
    # is_new_high when close == high_20 (within tolerance)
    # Use close values, not high, for time since close high
    close_high_20 = close.rolling(20).max()
    close_low_20 = close.rolling(20).min()
    is_close_high = (close == close_high_20)
    is_close_low = (close == close_low_20)

    # O(n) loop in Python is still faster than rolling apply with Python func
    # For 1000 bars, loop 1000 times vs apply 1000 times with overhead each
    n = len(df)
    time_high = np.full(n, np.nan)
    time_low = np.full(n, np.nan)
    last_high_idx = -1000
    last_low_idx = -1000
    close_vals = close.to_numpy()
    is_high_vals = is_close_high.to_numpy()
    is_low_vals = is_close_low.to_numpy()
    for i in range(n):
        if i < 19:
            continue
        if is_high_vals[i]:
            last_high_idx = i
            time_high[i] = 0.0
        else:
            if last_high_idx >= 0:
                diff = i - last_high_idx
                time_high[i] = float(min(diff, 20)) / 20.0
            else:
                time_high[i] = 1.0  # never seen high in window
        if is_low_vals[i]:
            last_low_idx = i
            time_low[i] = 0.0
        else:
            if last_low_idx >= 0:
                diff = i - last_low_idx
                time_low[i] = float(min(diff, 20)) / 20.0
            else:
                time_low[i] = 1.0

    df["feat_time_since_high_20"] = time_high
    df["feat_time_since_low_20"] = time_low

    # Vol contraction: realized_vol20 / realized_vol60
    vol_60 = ret_1.rolling(60).std()
    df["feat_vol_contraction"] = df["feat_realized_vol_20"] / vol_60.replace(0, np.nan)

    # Trend neutral: 1 - abs(slope)/0.001 clipped, 1=neutral, 0=trending
    slope_abs = df["feat_trend_slope_20"].abs()
    df["feat_trend_neutral"] = (1.0 - (slope_abs / 0.001).clip(upper=1.0)).fillna(0)

    # Asia vol: vol_regime when Asia (0-7 UTC) else 0
    # Use hour if available, else 0
    if "feat_hour_utc" in df.columns:
        is_asia = df["feat_hour_utc"].between(0, 7)
        df["feat_asia_vol"] = df["feat_vol_regime"].where(is_asia, 0.0)
    else:
        df["feat_asia_vol"] = 0.0

    # Donchian breakout: (close - high20_prev)/ATR
    high_20_prev = high.shift(1).rolling(20).max()
    df["feat_donchian_break"] = (close - high_20_prev) / atr.replace(0, np.nan)

    # Mean reversion strength: -ext_vs_ma_20 / realized_vol
    df["feat_mean_rev_strength"] = (-df["feat_ext_vs_ma_20"]) / df["feat_realized_vol_20"].replace(0, np.nan)

    # --- NEW: Gap & Intraday features for HIP-3 & native (Sep 17) ---
    open_series = df["open"] if "open" in df.columns else close
    close_prev = close.shift(1)
    # Gap: (open - close_prev)/ATR
    df["feat_gap"] = (open_series - close_prev) / atr.replace(0, np.nan)
    # Intraday momentum: (close - open)/(high - low)
    df["feat_intraday_mom"] = (close - open_series) / bar_range
    # High-low range: (high - low)/close
    df["feat_hl_range"] = (high - low) / close.replace(0, np.nan)
    # Overnight return: (open - close_prev)/close_prev
    df["feat_overnight_ret"] = (open_series - close_prev) / close_prev.replace(0, np.nan)
    # Vol of vol: std of realized_vol_20 over 20 bars
    df["feat_vol_of_vol"] = df["feat_realized_vol_20"].rolling(20).std()
    # Price acceleration: ret_1 - ret_1_prev
    df["feat_price_accel"] = ret_1 - ret_1.shift(1)
    # Volume breakout strength: vol_sma_ratio * abs(ret_1)
    df["feat_vol_breakout_strength"] = df["feat_vol_sma_ratio"].fillna(0) * ret_1.abs().fillna(0)

    # --- NEW: Additional neutral & intraday features (Sep 17) - 10 more ---
    # Z-score: (close - SMA20)/std20 - classic mean reversion
    df["feat_zscore_20"] = (close - sma_20) / std_20.replace(0, np.nan)

    # Stochastic %K: (close - low14)/(high14 - low14)
    high_14 = high.rolling(14).max()
    low_14 = low.rolling(14).min()
    range_14 = (high_14 - low_14).replace(0, np.nan)
    df["feat_stoch_k_14"] = (close - low_14) / range_14

    # Williams %R: (high14 - close)/(high14 - low14) = 1 - stoch_k
    df["feat_williams_r_14"] = (high_14 - close) / range_14

    # RSI 7: short-term momentum
    gain_7 = gain.ewm(span=7, adjust=False).mean()
    loss_7 = loss.ewm(span=7, adjust=False).mean()
    rs_7 = gain_7 / loss_7.replace(0, np.nan)
    df["feat_rsi_7"] = 100.0 - (100.0 / (1.0 + rs_7))

    # VWAP distance: (close - VWAP)/VWAP, VWAP approx = typical price weighted by volume
    typical = (high + low + close) / 3.0
    vwap = (typical * vol).rolling(20).sum() / vol.rolling(20).sum().replace(0, np.nan)
    df["feat_vwap_dist"] = (close - vwap) / vwap.replace(0, np.nan)

    # Range expansion: (high-low)/ATR14 - >1 expansion, <1 contraction
    df["feat_range_expansion"] = (high - low) / atr.replace(0, np.nan)

    # Gap fill ratio: (close - open)/(open - close_prev) - 1=fully filled, 0=not filled
    gap = (open_series - close_prev).replace(0, np.nan)
    df["feat_gap_fill_ratio"] = (close - open_series) / gap
    # Clip extreme values
    df["feat_gap_fill_ratio"] = df["feat_gap_fill_ratio"].clip(lower=-3, upper=3)

    # Keltner Channel position: (close - KC_lower)/(KC_upper - KC_lower)
    # KC = EMA20 ± 1.5*ATR14
    ema_20 = close.ewm(span=20, adjust=False).mean()
    kc_upper = ema_20 + 1.5 * atr
    kc_lower = ema_20 - 1.5 * atr
    kc_range = (kc_upper - kc_lower).replace(0, np.nan)
    df["feat_keltner_pos"] = (close - kc_lower) / kc_range

    # CCI 20: (typical - SMA20_typical)/(0.015*mean_dev)
    typical_sma_20 = typical.rolling(20).mean()
    mean_dev = (typical - typical_sma_20).abs().rolling(20).mean()
    df["feat_cci_20"] = (typical - typical_sma_20) / (0.015 * mean_dev.replace(0, np.nan))

    # ADX 14: trend strength, low = neutral regime (66% of time)
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    plus_dm = pd.Series(plus_dm, index=df.index)
    minus_dm = pd.Series(minus_dm, index=df.index)
    tr_smooth = true_range.rolling(14).mean()
    plus_di = 100.0 * (plus_dm.rolling(14).mean() / tr_smooth.replace(0, np.nan))
    minus_di = 100.0 * (minus_dm.rolling(14).mean() / tr_smooth.replace(0, np.nan))
    dx = 100.0 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    df["feat_adx_14"] = dx.rolling(14).mean()

    # --- NEW: 15 more for 70 total ---
    # ATR percent: ATR/close
    df["feat_atr_percent"] = atr / close.replace(0, np.nan)

    # Keltner width: (KC_upper - KC_lower)/EMA20
    df["feat_kc_width"] = (kc_upper - kc_lower) / ema_20.replace(0, np.nan)

    # BB squeeze: BB_width / KC_width, low = squeeze
    df["feat_bb_squeeze_20"] = df["feat_bb_width_20"] / df["feat_kc_width"].replace(0, np.nan)

    # Volume ROC: volume / volume_prev_20 -1
    vol_prev_20 = vol.shift(20)
    df["feat_vol_roc_20"] = vol / vol_prev_20.replace(0, np.nan) - 1.0

    # Price ROC 5: close / close_prev_5 -1
    df["feat_price_roc_5"] = close / close.shift(5).replace(0, np.nan) - 1.0

    # EMA cross 10-20: (EMA10 - EMA20)/close
    ema_10 = close.ewm(span=10, adjust=False).mean()
    df["feat_ema_cross_10_20"] = (ema_10 - ema_20) / close.replace(0, np.nan)

    # MACD 12-26: EMA12 - EMA26
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    df["feat_macd_12_26"] = ema_12 - ema_26

    # Donchian width 20: (high20 - low20)/ATR
    df["feat_donchian_width_20"] = (high_20 - low_20) / atr.replace(0, np.nan)

    # Asia range: hl_range when Asia else 0
    if "feat_hour_utc" in df.columns:
        is_asia = df["feat_hour_utc"].between(0, 7)
        df["feat_asia_range"] = df["feat_hl_range"].where(is_asia, 0.0)
    else:
        df["feat_asia_range"] = 0.0

    # Session momentum: intraday_mom * vol_regime
    df["feat_session_mom"] = df["feat_intraday_mom"].fillna(0) * df["feat_vol_regime"].fillna(0)

    # VWAP upper/lower dist
    df["feat_vwap_upper_dist"] = (high - vwap) / vwap.replace(0, np.nan)
    df["feat_vwap_lower_dist"] = (low - vwap) / vwap.replace(0, np.nan)

    # RSI 21: longer momentum
    gain_21 = gain.ewm(span=21, adjust=False).mean()
    loss_21 = loss.ewm(span=21, adjust=False).mean()
    rs_21 = gain_21 / loss_21.replace(0, np.nan)
    df["feat_rsi_21"] = 100.0 - (100.0 / (1.0 + rs_21))

    # Stochastic %D: SMA of %K
    df["feat_stoch_d_14"] = df["feat_stoch_k_14"].rolling(3).mean()

    # Range pos 50: longer range position
    high_50 = high.rolling(50).max()
    low_50 = low.rolling(50).min()
    range_50 = (high_50 - low_50).replace(0, np.nan)
    df["feat_range_pos_50"] = (close - low_50) / range_50

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
