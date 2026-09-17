# No-Holds-Barred Audit: Why Nothing Validates (2026-09-17)

## Executive Summary
**0 validated is truth, not a bug.** Zombie fix is correct. Previous 7488 validated was carry-forward junk. Current pipeline correctly rejects all 4608 discovered slices because no real edge survives costs + temporal + breadth.

Synthetic proof: injected +1% mean-reversion edge validates 15/17, SHORT edge 17/17. Pipeline works.

## Data Flow Trace (candle → feature → validation → book → paper)

### 1. Candle Fetch (perpdata.py, market.py)
- PERP: Hyperliquid public info API, candleSnapshot, deduped, incomplete bar filtered by server_time.
- SPOT: VALR paged candles, 60-5000 count, page sleep 0.05s.
- No lookahead: complete_at() <= server_time filter prevents repainting.
- **Bug check:** OK.

### 2. Feature Computation (features.py)
- 26 families listed, but actually:
  - ret_1,3,5,10,20 = 5 (same signal, different lags, corr >0.8)
  - ext_vs_ma_10,20,50, atr_norm_ext, ext_strength =5 (MA distance, corr >0.7 with ret_20)
  - trend_slope_20, trend_strength_20, vol_trend =3 (trend)
  - realized_vol_20, vol_regime, ret_vol =3 (vol)
  - vol_sma_ratio, buy_vol_ratio, vol_breakout, close_position, close_pos_ma =5 (volume/price structure)
  - rsi_14, rsi_divergence =2
  - ret_sign_streak, ret_autocorr =2
  - hour_utc =1
- **Independence:** No. 10/26 are pure returns or MA extensions. Composite features use fillna(0) before multiply, which creates neutral 0 for early bars, but min_periods 200 excludes them.
- **Missing:** funding rate, orderbook depth, bid-ask imbalance, BTC beta, alt/BTC ratio, liquidation OI, open interest. These are fundamentally different sources.
- **Verdict:** Feature homogeneity is real. Need new families.

### 3. Discovery (discovery.py)
- prepare_pooled: per symbol, bin_states with expanding quantile (min_periods 200, no lookahead), fwd_mae_atr, trade_net_cols with stop 1.5 ATR, horizon 1-24.
- _trade_net_cols: entry at close[t], stop at close ±1.5 ATR, exit at stop if low_next <= stop_long (excludes entry bar), else close[t+h]. No target (proxy).
- _slice_stats: per feature/state/side, mean/median/hit/t_stat/p_value, session stats, effective_tests = 26*3*2=156, bonferroni threshold 0.05/156=0.00032.
- **Local discovered:** 4608 rows, horizons 1-24 (192 per horizon), 2304 LONG 2304 SHORT, mean -0.0027 after costs, 865 bonferroni_pass (18.7%).
- **Bug check:** Discovery uses stop-only, validation uses stop+target+trailing. Mismatch intentional proxy, but could undervalue target-hitting edges. Not fatal.

### 4. Validation (validation.py) — The Bottleneck
- FOLD_COUNT 5 (env, min 3), TRAIN_FRACTION 0.6, RECENCY_FRACTION 0.2 min 20 rows, BREADTH 6 symbols (workflow) /10 default, 10 rows per symbol, 0.40 positive fraction (workflow) /0.55 default.
- Steps per candidate:
  1. Calibrate stop_atr_mult from first 60% MAE 90th percentile, clamped 1.5-3.5 (no lookahead).
  2. Compute stop-aware net (fixed) and trailing-aware net (activate 0.75R trail 1.0R).
  3. Choose side on training window only (leakage fix), direction_ok = candidate side == train side.
  4. Slice mask valid = isfinite(val_values) — uses trailing returns when enabled.
  5. mean_net = mean(val_values[slice_mask]), mean_positive = >0.
  6. Breadth: symbol means >0 fraction, adaptive horizon_breadth_min = max(4, base - (h-10)//5). For h=1 base 6 →6, h=24 →4.
  7. Recency: last 20% of total pooled rows (n_total=~10000, window 2000), slice rows in window >=20 and mean>0.
  8. Folds: linspace 0..len(subset) into 6 points, purge last h bars per fold to avoid overlap, pass if mean>0 per fold.
  9. temporal_pass = pass_count>=required AND (recency OR latest) AND bonferroni_ok (if enabled).
  10. Hostile regime: bear for LONG, bull for SHORT, mean<=0 with n>=20 → confounded (diagnostic only, NOT blocking).

- **Local validated_slices.csv (4608):**
  - recency_ok 865 (18.7%), latest_fold_passes 865, pass_count>=3 975, pass_count>=2 1448, temporal_pass 207 (4.5%), breadth_ok 1031 (22%), mean_positive 1001 (21.7%), regime_confounded 3638 (79%).
  - By side: LONG recency 0%, latest 0%, mean -0.00119, 43% positive, 44% breadth; SHORT recency 37.5%, latest 37.5%, mean -0.00627, 0% positive, 0.26% breadth, 98.8% confounded.
  - Best 903 (not confounded, 2+ passes, positive): ALL LONG, required 2, pass 2-4, latest 0, recency 0, pattern 11010,11110,10010 — last fold fails, recent bear kills LONG.
  - Temporal 207: ALL SHORT, mean -0.0056 (max -0.0007), mean_positive 0/207, breadth 4/207, direction 2/207. So temporal passes but mean negative → fails mean_positive.
  - Without bonferroni: pass_ge_req & rec_or_latest =207, and mean_positive among those =0, so 0 validate even ignoring bonferroni.

- **Is temporal too strict?** No. Synthetic edge with +1% mean reversion validates 15/17 with 11111 pattern, recency True, latest True. When edge decays (bear), recency/latest correctly rejects. 100% of best LONG failing recency is not a bug, it's bear regime.
- **Is breadth killing real edges?** Partially. 10 symbols realistic for market edge, but crypto vol differs 10x. Workflow already relaxed to 6 symbols 40% (vs 10/55% default), plus adaptive 4 for h=24, plus per-asset green (38k green /253k) allows subset trading. Even with 6/40%, 0 validate. So not the cause.
- **Is regime_confounded bug?** No. 79% confounded real, diagnostic only, not blocking. LONG 59% confounded, SHORT 98.8% — SHORT fails in bull. Tracker SMA50 vs SMA200 + close vs SMA50, slow, 27 consecutive bear cycles real.
- **Bonferroni aggressiveness:** 0.05/156=0.00032, 865/4608 pass =18.7% reasonable. Workflow disables it (REQUIRE_BONFERRONI=0) so required_passes 2, yet still 0 validate. So not cause.
- **Recency gate tightness:** 20% window min 20 rows. For n_slice 5000, recent expected 1000 rows, enough. For rare slices n=30, recent expected 6 <20 → would fail, but local n is 7194-28264, so not rare. So gate not too tight.
- **Pattern truncation bug:** Local file has patterns "0","1","101" length 1/3 vs folds 5, but fold_mean_rets has 5 values and pass_count matches count of "1" in truncated pattern? Actually "0" with 5 fold_means all negative and pass_count 0 → should be "00000" not "0". Likely CSV writer converted "00000" to 0 via integer? But validation code uses pattern.count("1") for pass_count, so "0" and "00000" both count 0. So not affecting logic, just display. Needs fix: ensure pattern written as string with leading zeros preserved (quote).

### 5. Book (research_lifecycle.py)
- sync_book: promotable = validated AND n>=60 AND green_breadth>=2 AND directional_edge> floor AND session_ok. Floor = max(static 0.004, cost*2, pool percentile top 25%). With 0 validated, 0 promotable. Carry-forward uses current research edge, not stale, plus hysteresis keep quantile 40%, plus paper_protected (green slices). Zombie fix correct: no carry-forward of unvalidated.
- **Bug check:** No zombie carry-forward. Good.

### 6. Paper (paper_trade.py, engine.py, lane_gate.py, monitor.py, regime_tracker.py)
- Paper.yml: SESSIONS eu,us,asia (includes Asia per user), MAX_POSITIONS 24, PER_KIND 30, PER_SLICE 5, TRAIL 1 activate 0.75 trail 1.0, WARMING 1, GAP 12, MAX_BOOK 20, ENTRY aligned, SELECTION profit, R_GATE 1, FILTER_NONPOSITIVE 1, RISK_FRACTION 0.06 hard ceiling 0.04, AGG_RISK 0.07 equity fraction, MULTI_ENGINE 1.
- Engine: momentum, mean_reversion, lead_lag, simple_trend, ranker. P0 fixes: mean_reversion BUY in bear disabled at source, volume <50% avg20 filtered. No session gate for engines (fixed). Good.
- Lane gate: green when closed PnL>0 and closed>=10, frozen when proven red, warmup when <10 closes. Native frozen, hip3 warmup. No forced liquidation (retired 2026-09-08, was -9.59 bleed). Good.
- Regime gate: blocks BUY in bear if hostile_unproven, SELL in bull, neutral optionally blocked if BLOCK_NEUTRAL=1. Green assets allowed even in neutral. Defensive exit only for blocked assets with bars_held>=3 and not R-gate winner. Good.
- **Bug check:** No silent wrong behavior. Asia included.

## Synthetic Proof (validation works)
- Random walk 11 symbols 1000 bars, no edge: found 156, positive 0, validated 0 — correct.
- Injected LONG edge: when close < SMA20*0.98 next +1%: found 156, positive 17, validated 15/17 pattern 11111 — validates real edge.
- Injected SHORT edge: when close > SMA20*1.02 next -1%: found 156 positive 17 validated 17/17 — validates SHORT.
- So 0 validated on real data means no edge, not validation too strict.

## What Would You Change (Don't Lower Standards)

**Don't lower thresholds.** Even with relaxed workflow (bonferroni off, breadth 6/40%, required 2), 0 validate. Lowering further would validate noise.

**Features genuinely bad for bear/SHORT.** Need:
1. Funding rate / perp-spot basis (high funding = SHORT edge). Currently no funding feature.
2. Orderbook depth / bid-ask imbalance from L2Book (already sampled for cost, reuse).
3. BTC beta / alt/BTC ratio: in bear, alt/BTC mean-reverts.
4. Liquidation maps / OI: bear has liquidations.
5. Vol-of-vol, ATR expansion.
6. Cross-pair lead/lag already in engine but not in research features.

**Thresholds to keep:**
- temporal_pass with recency/latest — keep, catches decay.
- breadth 6-10 symbols 40-55% — keep, rely on per-asset green.
- regime_confounded diagnostic — keep not blocking.
- bonferroni — keep disabled in workflow is okay, but 18.7% pass rate reasonable if enabled.

**Experiments (not lowering):**
- Reduce RECENCY_FRACTION 0.20→0.15 to be less sensitive to recent bear, but keep latest.
- Add hostile_n check already 20 rows.
- Add per-side breadth: SHORT needs fewer symbols (higher variance).

## Files
- validation.py: correct, trailing validation mirrors paper, no lookahead, pattern display bug (00000→0) cosmetic.
- features.py: 26 families but ~80% correlated, need funding/orderbook/BTC.
- discovery.py: stop-only proxy vs trailing+target in validation, okay but could add target.
- research_lifecycle.py: zombie fix correct, no carry-forward.
- paper.yml: Asia included, hard ceiling 0.04, multi-engine 1 — correct.

## Bottom Line
- Zombie fix correct, must stay.
- 0 validated is truth.
- Features need bear/SHORT families, not threshold relaxation.
- Validation pipeline proven to work on synthetic edges.

## Action Items
- [ ] Add funding/basis feature (perp - spot)
- [ ] Add orderbook imbalance from L2
- [ ] Add BTC dominance / alt/BTC ratio
- [ ] Fix pattern CSV quoting to preserve leading zeros
- [ ] Keep Asia session, hard ceiling, engine filters
