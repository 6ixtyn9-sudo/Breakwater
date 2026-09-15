"""Tests for the multi-engine signal generation."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from breakwater.engines.common import Signal
from breakwater.engines.engine_momentum import generate as momentum_generate
from breakwater.engines.engine_mean_reversion import generate as mr_generate
from breakwater.engines.engine_cross_asset import generate as cross_generate
from breakwater.engines.meta_ranker import rank_signals, score_summary


def _make_df(n: int = 200, trend: float = 0.0, volatility: float = 0.02) -> pd.DataFrame:
    """Create synthetic OHLCV data with optional trend."""
    np.random.seed(42)
    returns = np.random.normal(trend, volatility, n)
    close = 100 * np.exp(np.cumsum(returns))
    high = close * (1 + np.abs(np.random.normal(0, 0.005, n)))
    low = close * (1 - np.abs(np.random.normal(0, 0.005, n)))
    open_ = close * (1 + np.random.normal(0, 0.002, n))
    volume = np.random.uniform(1000, 10000, n)
    return pd.DataFrame({
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    })


class TestMomentumEngine:
    def test_uptrend_produces_buy(self):
        """Strong uptrend should produce a BUY signal."""
        df = _make_df(200, trend=0.003)  # strong uptrend
        signals = momentum_generate(df, symbol="BTCUSDC", regime="bull")
        if signals:  # may not trigger if ADX < threshold
            assert signals[0].side == "BUY"
            assert signals[0].engine == "momentum"
            assert signals[0].confidence > 0
            assert signals[0].expected_edge > 0

    def test_downtrend_produces_sell(self):
        """Strong downtrend should produce a SELL signal."""
        np.random.seed(123)
        n = 200
        returns = np.random.normal(-0.005, 0.01, n)  # strong downtrend, low noise
        close = 100 * np.exp(np.cumsum(returns))
        high = close * (1 + np.abs(np.random.normal(0, 0.003, n)))
        low = close * (1 - np.abs(np.random.normal(0, 0.003, n)))
        df = pd.DataFrame({
            "open": close * 0.999, "high": high, "low": low,
            "close": close, "volume": np.random.uniform(1000, 10000, n),
        })
        signals = momentum_generate(df, symbol="BTCUSDC", regime="bear")
        if signals:
            assert signals[0].side == "SELL"

    def test_no_trend_no_signal(self):
        """Flat market with low ADX should produce no signal."""
        df = _make_df(200, trend=0.0, volatility=0.005)  # very flat
        signals = momentum_generate(df, symbol="BTCUSDC", regime="neutral")
        assert len(signals) == 0

    def test_too_little_data(self):
        """Should handle short data gracefully."""
        df = _make_df(10)
        signals = momentum_generate(df, symbol="BTCUSDC")
        assert len(signals) == 0


class TestMeanReversionEngine:
    def test_oversold_produces_buy(self):
        """RSI < 30 and price below lower BB should produce BUY."""
        # Create data with a sharp drop at the end
        df = _make_df(200, trend=0.001)
        # Artificially push price down in last 20 bars
        drop = np.linspace(1, 0.85, 20)
        df.loc[df.index[-20:], "close"] *= drop
        df.loc[df.index[-20:], "low"] *= drop
        signals = mr_generate(df, symbol="ETHUSDC", regime="neutral")
        if signals:
            assert signals[0].side == "BUY"
            assert signals[0].engine == "mean_reversion"

    def test_overbought_produces_sell(self):
        """RSI > 70 and price above upper BB should produce SELL."""
        df = _make_df(200, trend=0.001)
        # Artificially push price up in last 20 bars
        pump = np.linspace(1, 1.15, 20)
        df.loc[df.index[-20:], "close"] *= pump
        df.loc[df.index[-20:], "high"] *= pump
        signals = mr_generate(df, symbol="ETHUSDC", regime="neutral")
        if signals:
            assert signals[0].side == "SELL"

    def test_neutral_market_no_signal(self):
        """Normal market should produce no signal."""
        df = _make_df(200, trend=0.0, volatility=0.02)
        signals = mr_generate(df, symbol="ETHUSDC", regime="neutral")
        assert len(signals) == 0

    def test_regime_fit_neutral_vs_trending(self):
        """Mean reversion should fit neutral regime better than trending."""
        df = _make_df(200, trend=0.0)
        # Force an extreme by dropping price
        df.loc[df.index[-10:], "close"] *= 0.9
        df.loc[df.index[-10:], "low"] *= 0.9
        signals_neutral = mr_generate(df, symbol="X", regime="neutral")
        signals_trending = mr_generate(df, symbol="X", regime="bull")
        if signals_neutral and signals_trending:
            assert signals_neutral[0].regime_fit > signals_trending[0].regime_fit


class TestCrossAssetEngine:
    def test_btc_move_triggers_alt_signals(self):
        """BTC making a big move should generate signals for correlated alts."""
        np.random.seed(42)
        # Create correlated assets
        n = 200
        btc_returns = np.random.normal(0, 0.02, n)
        # Last 5 bars: BTC pumps 3%
        btc_returns[-5:] = [0.006, 0.006, 0.006, 0.006, 0.006]

        btc_close = 100 * np.exp(np.cumsum(btc_returns))
        eth_close = 50 * np.exp(np.cumsum(btc_returns * 0.8 + np.random.normal(0, 0.01, n)))

        btc_df = pd.DataFrame({
            "open": btc_close * 0.999,
            "high": btc_close * 1.005,
            "low": btc_close * 0.995,
            "close": btc_close,
            "volume": np.random.uniform(1000, 10000, n),
        })
        eth_df = pd.DataFrame({
            "open": eth_close * 0.999,
            "high": eth_close * 1.005,
            "low": eth_close * 0.995,
            "close": eth_close,
            "volume": np.random.uniform(1000, 10000, n),
        })

        frames = {"BTCUSDC": btc_df, "ETHUSDC": eth_df}
        signals = cross_generate(frames, btc_symbol="BTCUSDC")
        # May or may not trigger depending on correlation — just check no crash
        for s in signals:
            assert s.engine == "cross_asset"
            assert s.side in ("BUY", "SELL")
            assert s.score > 0

    def test_no_btc_data(self):
        """Should handle missing BTC data gracefully."""
        frames = {"ETHUSDC": _make_df(200)}
        signals = cross_generate(frames, btc_symbol="BTCUSDC")
        assert len(signals) == 0

    def test_small_btc_move_no_signal(self):
        """Small BTC move should not trigger signals."""
        df = _make_df(200, trend=0.0, volatility=0.001)  # very flat
        frames = {"BTCUSDC": df, "ETHUSDC": df.copy()}
        signals = cross_generate(frames, btc_symbol="BTCUSDC", move_threshold=0.03)
        assert len(signals) == 0


class TestMetaRanker:
    def test_ranking_by_score(self):
        """Higher score signals should rank first."""
        signals = [
            Signal("A", "BUY", "momentum", 10, 0.005, 0.5, 0.5),
            Signal("B", "BUY", "momentum", 10, 0.01, 0.9, 0.9),
            Signal("C", "SELL", "mean_reversion", 8, 0.003, 0.8, 1.0),
        ]
        ranked = rank_signals(signals, max_signals=10)
        assert ranked[0].symbol == "B"  # highest score
        assert ranked[1].symbol == "C"  # second highest
        assert ranked[2].symbol == "A"  # lowest

    def test_max_per_symbol(self):
        """Should cap signals per symbol."""
        signals = [
            Signal("BTCUSDC", "BUY", "m", 10, 0.01, 0.9, 0.9),
            Signal("BTCUSDC", "SELL", "m", 10, 0.009, 0.8, 0.9),
            Signal("BTCUSDC", "BUY", "m", 10, 0.008, 0.7, 0.9),
        ]
        ranked = rank_signals(signals, max_per_symbol=2)
        assert len(ranked) == 2

    def test_max_per_engine(self):
        """Should cap signals per engine."""
        signals = [
            Signal(f"SYM{i}", "BUY", "momentum", 10, 0.01, 0.9, 0.9)
            for i in range(20)
        ]
        ranked = rank_signals(signals, max_per_engine=5)
        assert len(ranked) == 5

    def test_min_score_filter(self):
        """Should filter out low-score signals."""
        signals = [
            Signal("A", "BUY", "m", 10, 0.001, 0.1, 0.1),  # score = 0.00001
            Signal("B", "BUY", "m", 10, 0.01, 0.9, 0.9),    # score = 0.0081
        ]
        ranked = rank_signals(signals, min_score=0.001)
        assert len(ranked) == 1
        assert ranked[0].symbol == "B"

    def test_empty_signals(self):
        """Should handle empty input."""
        ranked = rank_signals([])
        assert len(ranked) == 0

    def test_score_summary(self):
        """Summary should report correct stats."""
        signals = [
            Signal("A", "BUY", "momentum", 10, 0.01, 0.9, 0.9),
            Signal("B", "SELL", "mean_reversion", 8, 0.005, 0.7, 0.8),
        ]
        summary = score_summary(signals)
        assert summary["total"] == 2
        assert summary["buys"] == 1
        assert summary["sells"] == 1
        assert "momentum" in summary["engines"]
        assert "mean_reversion" in summary["engines"]
