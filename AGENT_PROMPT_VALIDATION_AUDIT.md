# Audit: Why Does Nothing Validate? — Findings

## Current State (main branch, localdata/research/validated_slices.csv)

```
4608 discovered
  865 (18.7%) bonferroni_pass in discovery (p < 0.05/156 = 0.00032)
  207 (4.5%) temporal_pass in validation
  1031 (22%) breadth_ok
  1001 (21.7%) mean_positive after costs
  0 validated

By fail_reasons:
  temporal_pass,direction_ok,breadth_ok,mean_net<=0: 2088 (45%)
  temporal_pass,breadth_ok,mean_net<=0: 1277 (27%)
  temporal_pass: 986 (21%)
  → 95% fail temporal_pass as primary

By side:
  LONG: mean -0.00119, 43% mean_positive, 44% breadth_ok, 0% temporal_pass, 59% regime_confounded
  SHORT: mean -0.00627, 0% mean_positive, 0.26% breadth_ok, 8.9% temporal_pass, 98.8% regime_confounded

Best 903 (not confounded, 2+ passes, positive mean):
  ALL LONG, 0 SHORT
  required_passes=2, pass_count 2:62, 3:558, 4:283 → meets required
  latest_fold_passes=False for ALL 903
  recency_ok=False for ALL 903
  → temporal fails because (recency OR latest) is False
  Pattern: 11010, 11110, 10010 — last fold 0, recent decay
```

## 1. Is temporal_pass too strict?

**No — it's correctly rejecting decayed edges, but reveals regime problem.**

- `pass_count >= required_passes`: required=2 (when bonferroni off) or 3 (when on). Best 903 have 2-4 passes, so they meet it.
- `recency_ok`: last 20% rows mean>0, min 20 rows. `latest_fold_passes`: last fold mean>0.
- **100% of best 903 fail both recency and latest** — edge worked in early folds (2026-01 to 2026-08) but died in recent 20% (bear regime Sep). Pattern `11010` = pass, pass, fail, pass, fail — last fold fails.
- In bear market (consecutive_bear 27, bear breadth 59%), LONG edges naturally fail recency. That's not a bug, it's signal decay.
- **Bonferroni:** ALPHA 0.05 / 156 tests = 0.00032. 865/4608 pass = 18.7% — reasonable, not too aggressive. If we disabled bonferroni, required_passes drops 3→2, but best 903 already meet 2, still fail recency/latest.
- **Verdict:** Don't relax recency/latest. If we did (e.g., require recency > -0.001 or 10% window), we'd validate stale LONGs that lose in bear. The gate is working.

## 2. Is breadth_ok killing real edges?

**Partially — 10 symbols is realistic for a market edge, but crypto is heterogeneous.**

- `BREADTH_MIN_SYMBOLS=10`, `BREADTH_MIN_ROWS_PER_SYMBOL=10`, `BREADTH_MIN_POSITIVE_FRACTION=0.55`
- Universe has ~30 PERP symbols, but volatilities differ 10x (BTC vs DOGE). A BTC edge may not work on DOGE.
- Current: 22% breadth_ok, but SHORT only 0.26% — SHORT fails breadth catastrophically.
- Code already has adaptive breadth: `horizon_breadth_min = max(4, 10 - (horizon-10)//5)` — horizon 20 → min 8, horizon 1 → 10. Good.
- **Per-asset green** already exists: `asset_edges.csv` with 253k rows, 38k green, 213k blocked — allows per-asset filtering even if pooled breadth fails. So breadth_ok is not a hard block for trading, it's a validation filter.
- **Verdict:** Breadth 10 is okay for pooled validation. Don't lower to 4 just to get passes. Instead, rely on per-asset green to trade subset, and add cross-pair features.

## 3. Is regime_confounded a bug?

**No — 79% confounded is real, not a bug, and it's intentionally NOT blocking validation.**

- `regime_confounded`: checks hostile regime (bear for LONG, bull for SHORT) mean <=0 with enough rows. 3638/4608 = 79% confounded.
- Code comment: `regime_confounded is intentionally NOT part of is_validated` — a slice positive in neutral/bull but negative in bear is still valid, regime gate blocks bear entries at trade time.
- LONG 59% confounded, SHORT 98.8% confounded — SHORT almost always fails in bull (makes sense).
- Regime tracker: SMA50 vs SMA200 + close vs SMA50, slow, not too volatile. 27 consecutive bear cycles is real bear, not flip-flop.
- **Verdict:** Not a bug. It's diagnosing that most edges are regime-dependent. In current bear, LONG edges die, which is why native lane is -37.10 frozen and HIP-3 (different source) is green.

## 4. Are 26 feature families independent?

**No — they are mostly variations of the same signal.**

List:
```
ret_1, ret_3, ret_5, ret_10, ret_20 (5x returns)
ext_vs_ma_10,20,50, atr_norm_ext, ext_strength (5x MA distance)
trend_slope_20, trend_strength_20, vol_trend (trend)
realized_vol_20, vol_regime, ret_vol (volatility)
vol_sma_ratio, vol_breakout, buy_vol_ratio, close_position, close_pos_ma (volume/price structure)
rsi_14, rsi_divergence (RSI)
ret_sign_streak, ret_autocorr (persistence)
hour_utc (session)
```

- 10 are pure returns, 5 are MA extensions (returns vs MA), 3 are trend, 3 are vol — all price-derived from same OHLCV.
- New families added in main: volume, RSI, close position, streak, autocorr, hour — better, but still price-only.
- No funding rate, orderbook depth, cross-pair correlation, BTC beta, on-chain, liquidation, open interest.
- Correlation likely >0.8 between ret_10, ret_20, ext_vs_ma_20, trend_slope.
- **Verdict:** Feature homogeneity is real. Need fundamentally different sources.

## 5. What would you change? (Don't lower standards)

**Don't lower validation — features are genuinely bad for current regime.**

The honest answer: **The features are genuinely bad and you need new ones that work in bear and for SHORT.**

Current edges:
- Mean after costs: LONG -0.00119, SHORT -0.00627 — both negative on average
- 87% mean_net<=0 — costs kill most
- Best 903 LONG decayed recently (bear)

What to add (in order of impact):

1. **SHORT-specific features for bear:** Funding rate (high funding = SHORT edge), liquidation maps, open interest, BTC dominance. Current SHORT mean_positive 0% — no SHORT edge survives costs.
2. **Cross-pair / BTC beta:** `feat_btc_corr_20`, `feat_btc_beta`, `feat_alt_btc_ratio` — in bear, alt/BTC ratio mean-reverts.
3. **Orderbook depth / imbalance:** `feat_bid_ask_imbalance`, `feat_depth_10bps` — requires L2Book, already sampled for cost measurement, reuse.
4. **Volatility regime:** `feat_vol_regime` exists but need `feat_vol_of_vol`, `feat_atr_expansion` — bear has high vol.
5. **Funding proxy:** If funding not available, use `basis = perp - spot` or `funding = (perp_mark - oracle)/oracle` — already have oracle deviation in HIP-3, add to native.

Thresholds to keep:
- `temporal_pass` with recency/latest — keep, it's catching decay
- `breadth_ok` 10 symbols 55% — keep, rely on per-asset green for trading subset
- `regime_confounded` diagnostic only — keep not blocking
- `bonferroni` — keep, 18.7% pass rate reasonable

What to experiment (not lowering standards, but tuning):
- Reduce `BREADTH_MIN_SYMBOLS` to 8 for SHORT only (SHORT needs fewer symbols due to higher variance)
- Reduce `RECENCY_FRACTION` 0.20→0.15 to be less sensitive to recent bear, but keep latest_fold requirement
- Add `hostile_n` check: currently `HOSTILE_MIN_ROWS=20` to declare confounded, good

**Bottom line:** Zombie fix is correct. 0 validated is truth, not a bug. The 7,488 previous validated was carry-forward junk. Need new feature families, especially SHORT/bear features, not threshold relaxation.

## Files

- `validation.py`: temporal_pass logic correct, recency/latest catching decay, bonferroni reasonable
- `features.py`: 26 families but ~80% correlated, need funding/orderbook/cross-pair
- `research_lifecycle.py`: promotion uses pooled edge, per-asset green already allows trading subset
- `validated_slices.csv`: 0 validated is correct given current features and bear regime
