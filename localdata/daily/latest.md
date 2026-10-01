# Breakwater daily print — 2026-10-01 03:45 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **505.41 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2421.04 ZAR** (seed 2000) | lifetime: **+421.04 ZAR** | closed: 309
- Today: 0 closed, **+0.00 ZAR**
- 7d: **-55.07 ZAR** | 30d: **+421.04 ZAR**

## 2b. Claimed vs realised

- Book: 307 slices (native 282 | hip3 25); validated pools: native 722 | hip3 160; book slices absent from pools: 11
  - absent: `feat_vol_regime:1:LONG:h24` (native)
  - absent: `feat_vol_contraction:1:LONG:h24` (native)
  - absent: `feat_bb_pos_20:2:LONG:h12` (native)
  - absent: `feat_zscore_20:2:LONG:h12` (native)
  - absent: `feat_trend_slope_20:2:LONG:h11` (native)
  - absent: `feat_atr_ratio:1:LONG:h20` (native)
  - absent: `feat_atr_norm_ext:2:LONG:h12` (native)
  - absent: `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` (hip3)
  - absent: `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` (hip3)
  - absent: `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` (hip3)
  - ... and 1 more
- Claimed edge (median mean_ret_costadj over 296 book slices present in the validated pools): +0.377% | at 167.72 ZAR mean notional/trade: +0.63 ZAR/trade
- Realised (309 real closes per lane_gate._is_real_close, net of fees): +1.36 ZAR/trade | sd 5.54 | SE 0.32
- Gap: +0.73 ZAR/trade | t = +2.31 (one-sample t of realised mean vs the claimed constant) | verdict: EXCEEDS
- native: claimed median +0.386% over 275/282 slices (pool 722) ~ +0.65 ZAR | realised 263 closes +1.77 ZAR sd 5.57 SE 0.34 | gap +1.12 t +3.27 | EXCEEDS
- hip3: claimed median +0.065% over 21/25 slices (pool 160) ~ +0.11 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.08 t -1.52 | NOT ESTABLISHED
- Ledger: 204443 decision rows; 309 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 204134 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 263 | wins: 149 | win%: 56.7 | P&L: **+465.54 ZAR** | today: +0.00 | 7d: -16.20 | 30d: +465.54
- By exit: target +516.3, horizon +92.4, trail_stop +6.5, regime_shift -11.9, stop -137.7
- By entry regime (n/pnl): neutral 95/+287.8, bull 96/+196.0, bear 72/-18.3
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; feat_ext_vs_ma_50:0:LONG:h24 2n/0w -6.90; engine_mean_reversion:rsi:2:SELL:h10:ZECUSDC 2n/0w -6.66; feat_buy_vol_ratio:2:LONG:h24 5n/0w -6.57
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPUSDC 18n +18.72; XRPZAR 2n +18.07; BTCUSDC 26n +15.89
- Worst pairs: ETHZAR 4n -14.36; ZECUSDC 7n -11.65; NEARUSDC 3n -8.75; LTCUSDC 2n -6.24; BNBZAR 5n -5.43

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: -38.87 | 30d: -44.50
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 4 open, stop-risk **16.14 ZAR**
  - XRPUSDC BUY ntl=123 risk=4.73 bars=12 stop=1.439975000000000055 peak=1.5148
  - SOLUSDC BUY ntl=123 risk=4.55 bars=0 stop=113.79499999999999960 peak=118.15
  - BTCUSDC BUY ntl=123 risk=3.56 bars=7 stop=81175.24999999999990 peak=83856.0
  - ETHUSDC BUY ntl=123 risk=3.30 bars=12 stop=2606.874999999999830 peak=2698.5

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **16.14 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **16.14 / 172.74 ZAR | 10.1% | ok**
- Remaining: 155.3628 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 49, "skipped": 49, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 0, "opened": 1, "pair_held": 20, "signals": 747, "skipped": 726, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **XRPUSDC** 4.7307 ZAR
- positions without bars: 0 | replayed: 3 | invalid: 0

## 6. Monitored books

- Native: 282 | HIP-3: 25
- Native top (by paper P&L):
  - `feat_bb_pos_20:2:LONG:h15` edge=0.0040 n=10327 p=0.0019 src=validated_walk_forward unproven=False paper=4n/+16.17
  - `feat_atr_norm_ext:2:LONG:h15` edge=0.0041 n=10348 p=0.0006 src=validated_walk_forward unproven=False paper=3n/+15.77
  - `feat_vol_regime:2:LONG:h12` edge=0.0044 n=11267 p=0.0001 src=validated_walk_forward unproven=False paper=5n/+7.60
  - `feat_vol_regime:2:LONG:h12` edge=0.0062 n=8545 p=0.0003 src=validated_walk_forward unproven=False paper=5n/+7.60
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0058 n=17004 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+5.56
  - `feat_zscore_20:2:LONG:h15` edge=0.0040 n=10327 p=0.0019 src=validated_walk_forward unproven=False paper=2n/+4.17
  - `feat_rsi_14:2:LONG:h15` edge=0.0036 n=10124 p=0.0021 src=validated_walk_forward unproven=False paper=1n/+3.63
  - `feat_ext_vs_ma_10:2:LONG:h15` edge=0.0037 n=10159 p=0.0042 src=validated_walk_forward unproven=False paper=1n/+2.49
- HIP-3 top (by paper P&L):
  - `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` edge=0.0081 n=494 p=0.1655 src=validated_walk_forward unproven=False paper=20n/+9.43
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` edge=0.0003 n=9570 p=0.3356 src=validated_walk_forward unproven=False paper=15n/+4.27
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h11` edge=0.0015 n=1260 p=0.0162 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h9` edge=0.0006 n=1272 p=0.4321 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ext_vs_ma_50:1:LONG:h22` edge=0.0006 n=1354 p=0.8646 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ext_strength:1:LONG:h18` edge=0.0001 n=1420 p=0.9829 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ret_20:1:LONG:h18` edge=0.0001 n=1563 p=0.9678 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_trend_slope_20:0:LONG:h20` edge=0.0008 n=1576 p=0.1320 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **46/50** | ghost rows: **550/50** | PnL: **-44.50 ZAR**
- Gate verdict: **NOT READY**

## 8. Research / honesty checks

- Deep audit: candidates=74880 preliminary_passes=0 audit_passes=0 plateaus=0 fetch_errors=25

## 9. Live readiness checks

- Promotion registry strategies: **0** | live_capped: 0
- 1 live HL executor: NOT PRESENT - hyperliquid.py is read-only; no mainnet signer
- 2 mechanism canary: NOT RUN - no testnet agent key / no signed action
- 3 live loss limits: WIRED, UNEXERCISED - reconciliation is in the guardian but no live position has closed yet, so the daily/7d limits have never had a non-zero input
- 4 promotion registry valr_native: NOT APPLICABLE TO HL - gate requires valr_native=True
- 5 big-wave-only live path: NOT YOUR BOOK - engine executes slice_id=='big-wave' only
- 6 deep audit passes: 0 preliminary / 0 audit
- 7 book regime durability: NOT PROVEN - hostile_unproven can be True and still promoted

## 10. Regime shift

- Label: **bear** | breadth bear=0.5333 bull=0.4 neutral=0.0667 | symbols=15
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bull | consecutive_bear: 1 / bull 0
- as_of: 2026-10-01T03:00:31Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 832 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-23.31 | frozen=YES
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3, native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 18
  - `feat_atr_norm_ext:2:LONG:h15` pnl=+15.77
  - `feat_bb_pos_20:2:LONG:h15` pnl=+16.17
  - `feat_cci_20:2:LONG:h15` pnl=+10.70
  - `feat_close_pos_ma:1:LONG:h24` pnl=+283.35
  - `feat_close_pos_ma:2:LONG:h12` pnl=+121.93
  - `feat_close_pos_ma:2:LONG:h20` pnl=+5.01
  - `feat_close_position:2:LONG:h24` pnl=+1.42
  - `feat_ext_strength:2:LONG:h15` pnl=+24.00
  - `feat_ext_vs_ma_20:2:LONG:h15` pnl=+9.35
  - `feat_range_pos_50:0:LONG:h24` pnl=+1.86
  - `feat_realized_vol_20:2:LONG:h20` pnl=+1.47
  - `feat_ret_10:2:LONG:h19` pnl=+14.58
  - `feat_ret_20:2:LONG:h14` pnl=+13.42
  - `feat_rsi_divergence:2:LONG:h20` pnl=+8.36
  - `feat_trend_slope_20:2:LONG:h12` pnl=+11.12
  - `feat_vol_sma_ratio:0:LONG:h24` pnl=+1.00
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **213/282** | hip3 **18/25**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 19
  - `feat_atr_norm_ext:2:LONG:h13` lane_not_green
  - `feat_buy_vol_ratio:2:LONG:h24` lane_not_green
  - `feat_donchian_break:2:LONG:h15` lane_not_green
  - `feat_price_roc_5:2:LONG:h20` lane_not_green
  - `feat_range_pos_20:2:LONG:h15` lane_not_green
  - `feat_realized_vol_20:2:LONG:h14` lane_not_green
  - `feat_realized_vol_20:2:LONG:h21` lane_not_green
  - `feat_realized_vol_20:2:LONG:h22` lane_not_green
  - `feat_realized_vol_20:2:LONG:h23` lane_not_green
  - `feat_realized_vol_20:2:LONG:h24` lane_not_green
  - `feat_ret_1:2:LONG:h24` lane_not_green
  - `feat_time_since_high_20:0:LONG:h12` lane_not_green
  - `feat_vol_breakout:2:LONG:h15` lane_not_green
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` lane_not_green
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-10-01T03:45:19: errors=0 signals=796 regime_blocked=521
- this cycle: closed=0 new_signals=796 skipped=775 slot_full=0 slice_full=0 pair_held=20
- Action funnel: regime_blocked=521 | lane_gate_blocked=9 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=20 | slot_full=0 | skipped=775
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 9, "pair_held": 20, "regime_blocked": 521, "skipped": 775, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=False hip3_green=False frozen=hip3,native islands=18 blocks=19
- aggregate_risk: ok open=11.5944 cap=172.7380 used=0.1006 remaining=155.3628 replayed=3 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
