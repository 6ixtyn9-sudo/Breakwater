# Audit: Why Does Nothing Validate?

## The Problem

Research runs every few hours. It discovers 7,488 slices. **Zero validate.** This has been consistent since the zombie fix landed — the previous "7,488 validated" was carry-forward junk. Now that the zombie fix is in, nothing real passes.

```
7,488 discovered
6,124 (82%) regime_confounded — edge only works in one regime
7,123 (95%) fail temporal_pass — can't pass walk-forward validation
6,525 (87%) mean_net<=0 — negative after costs
6,404 (86%) fail breadth_ok — not enough symbols positive
0 validated
```

Even the best790 slices (NOT regime-confounded, 2+ walk-forward passes, positive mean) ALL fail temporal_pass.

## What I Need You to Audit

### 1. Is temporal_pass too strict?

Look at `validation.py`. The temporal_pass gate requires:
- `pass_count >= required_passes` (currently 2 out of 5 folds)
- `recency_ok OR latest_fold_passes`
- `bonferroni_ok` (multiple testing correction)

Are these thresholds correct? Is the Bonferroni correction too aggressive? Is the recency gate too tight?

### 2. Is breadth_ok killing real edges?

breadth_ok requires the edge to hold across multiple symbols, not just one. But crypto pairs have different volatilities and behaviors — a feature that works on BTCUSDC might not work on DOGEUSDC. Is the breadth requirement realistic for crypto?

### 3. Is regime_confounded a real problem or a bug?

82% of slices are marked regime_confounded. Is this because the regime tracker is too volatile (flipping between bear/neutral/bull too quickly)? Or is it a genuine problem with the features?

### 4. Are the 26 feature families actually independent?

The features are: ret_1, ret_3, ret_5, ret_10, ret_20, rsi_14, rsi_divergence, atr_norm_ext, ext_vs_ma_10, ext_vs_ma_20, ext_vs_ma_50, ext_strength, trend_slope_20, trend_strength_20, vol_sma_ratio, vol_breakout, vol_regime, vol_trend, buy_vol_ratio, close_position, close_pos_ma, ret_sign_streak, ret_autocorr, ret_vol, hour_utc, realized_vol_20.

Most are derivatives of returns and moving averages. Are they actually capturing different information or are they all variations of the same signal?

### 5. What would you change?

The system needs edges that:
- Pass temporal validation (out-of-sample)
- Hold across multiple symbols
- Work in more than one regime
- Survive after costs

What features, thresholds, or validation logic would you change to find real edges?

## Files to Review

- `src/breakwater/validation.py` — temporal_pass, breadth_ok, regime_confounded logic
- `src/breakwater/features.py` — 26 feature families
- `src/breakwater/research_lifecycle.py` — discovery and promotion pipeline
- `localdata/research/validated_slices.csv` — 7,488 slices, 0 validated

## Constraints

- All fixes go to `main` branch
- Don't lower validation standards just to get slices passing — the point is to find REAL edges
- The zombie fix is correct and must stay — no carry-forward of unvalidated slices
- If the answer is "the features are genuinely bad and you need new ones," say that
