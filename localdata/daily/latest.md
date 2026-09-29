# Breakwater daily print — 2026-09-29 19:01 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **508.56 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2430.36 ZAR** (seed 2000) | lifetime: **+430.36 ZAR** | closed: 296
- Today: 4 closed, **-25.80 ZAR**
- 7d: **-68.27 ZAR** | 30d: **+430.36 ZAR**

## 2b. Claimed vs realised

- Book: 175 slices (native 150 | hip3 25); validated pools: native 122 | hip3 160; book slices absent from pools: 85
  - absent: `feat_gap_fill_ratio:0:LONG:h12` (native)
  - absent: `feat_bb_pos_20:2:LONG:h12` (native)
  - absent: `feat_zscore_20:2:LONG:h12` (native)
  - absent: `feat_mean_rev_strength:0:LONG:h12` (native)
  - absent: `feat_ret_10:2:LONG:h12` (native)
  - absent: `feat_vwap_upper_dist:2:LONG:h12` (native)
  - absent: `feat_stoch_d_14:2:LONG:h12` (native)
  - absent: `feat_vwap_dist:2:LONG:h12` (native)
  - absent: `feat_donchian_break:2:LONG:h15` (native)
  - absent: `feat_vwap_lower_dist:2:LONG:h12` (native)
  - ... and 75 more
- Claimed edge (median mean_ret_costadj over 90 book slices present in the validated pools): +0.446% | at 168.38 ZAR mean notional/trade: +0.75 ZAR/trade
- Realised (296 real closes per lane_gate._is_real_close, net of fees): +1.45 ZAR/trade | sd 5.61 | SE 0.33
- Gap: +0.70 ZAR/trade | t = +2.16 (one-sample t of realised mean vs the claimed constant) | verdict: EXCEEDS
- native: claimed median +0.481% over 69/150 slices (pool 122) ~ +0.82 ZAR | realised 251 closes +1.86 ZAR sd 5.67 SE 0.36 | gap +1.04 t +2.90 | EXCEEDS
- hip3: claimed median +0.065% over 21/25 slices (pool 160) ~ +0.10 ZAR | realised 45 closes -0.79 ZAR sd 4.70 SE 0.70 | gap -0.89 t -1.27 | NOT ESTABLISHED
- Ledger: 190183 decision rows; 296 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 189887 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 251 | wins: 143 | win%: 57.0 | P&L: **+465.75 ZAR** | today: +1.24 | 7d: -38.51 | 30d: +465.75
- By exit: target +516.3, horizon +99.1, regime_shift -11.9, stop -137.7
- By entry regime (n/pnl): neutral 86/+289.9, bull 96/+196.0, bear 69/-20.1
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; feat_ext_vs_ma_50:0:LONG:h24 2n/0w -6.90; engine_mean_reversion:rsi:2:SELL:h10:ZECUSDC 2n/0w -6.66; feat_buy_vol_ratio:2:LONG:h24 5n/0w -6.57
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPUSDC 16n +19.12; XRPZAR 2n +18.07; BTCUSDC 24n +15.83
- Worst pairs: ETHZAR 4n -14.36; ZECUSDC 7n -11.65; NEARUSDC 3n -8.75; LTCUSDC 2n -6.24; BNBZAR 5n -5.43

### HIP3

- Closed: 45 | wins: 23 | win%: 51.1 | P&L: **-35.39 ZAR** | today: -27.04 | 7d: -29.76 | 30d: -35.39
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -76.3
- By entry regime (n/pnl): neutral 14/-1.5, bear 11/-8.4, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 8n/2w -25.49; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:CIEN 5n +6.86; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 5 open, stop-risk **20.43 ZAR**
  - SOLUSDC BUY ntl=125 risk=4.98 bars=21 stop=114.05749999999998790 peak=118.79
  - XRPUSDC BUY ntl=125 risk=4.96 bars=10 stop=1.448099999999999985 peak=1.5079
  - HYPEUSDC BUY ntl=125 risk=4.80 bars=11 stop=84.59974999999999975 peak=87.977
  - ETHUSDC BUY ntl=125 risk=3.51 bars=23 stop=2624.500000000000270 peak=2700.3
  - BTCUSDC BUY ntl=125 risk=2.19 bars=7 stop=82516.24500 peak=83986.0

- **HIP3**: 2 open, stop-risk **17.33 ZAR**
  - PARA:AVGO SELL ntl=495 risk=8.66 bars=4 stop=366.320350 peak=360.02
  - PARA:CIEN SELL ntl=495 risk=8.66 bars=0 stop=352.624800 peak=346.56

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **37.76 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **37.76 / 173.14 ZAR | 24.1% | ok**
- Remaining: 131.3421 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 115, "skipped": 115, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 17, "signals": 398, "skipped": 381, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **PARA:AVGO** 8.6646 ZAR
- positions without bars: 1 | replayed: 6 | invalid: 0

## 6. Monitored books

- Native: 150 | HIP-3: 25
- Native top (by paper P&L):
  - `feat_close_pos_ma:2:LONG:h12` edge=0.0052 n=8788 p=0.0000 src=validated_walk_forward unproven=False paper=29n/+121.93
  - `feat_trend_slope_20:2:LONG:h12` edge=0.0056 n=9427 p=0.0002 src=validated_walk_forward unproven=False paper=5n/+11.12
  - `feat_rsi_divergence:2:LONG:h20` edge=0.0068 n=9718 p=0.2152 src=validated_walk_forward unproven=False paper=5n/+8.36
  - `feat_vol_regime:2:LONG:h12` edge=0.0062 n=8545 p=0.0003 src=validated_walk_forward unproven=False paper=5n/+7.60
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0058 n=17004 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+5.56
  - `feat_ext_vs_ma_10:2:LONG:h15` edge=0.0045 n=9740 p=0.0005 src=validated_walk_forward unproven=False paper=1n/+2.49
  - `feat_vol_trend:2:LONG:h12` edge=0.0078 n=12345 p=0.0000 src=validated_walk_forward unproven=False paper=1n/+2.37
  - `feat_squeeze:2:LONG:h15` edge=0.0071 n=13876 p=0.0043 src=validated_walk_forward unproven=False paper=1n/+2.25
- HIP-3 top (by paper P&L):
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` edge=0.0054 n=242 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h11` edge=0.0015 n=1260 p=0.0162 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h9` edge=0.0006 n=1272 p=0.4321 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ext_vs_ma_50:1:LONG:h22` edge=0.0006 n=1354 p=0.8646 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ext_strength:1:LONG:h18` edge=0.0001 n=1420 p=0.9829 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ret_20:1:LONG:h18` edge=0.0001 n=1563 p=0.9678 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_trend_slope_20:0:LONG:h20` edge=0.0008 n=1576 p=0.1320 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_atr_norm_ext:0:LONG:h23` edge=0.0009 n=1577 p=0.0441 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **45/50** | ghost rows: **540/50** | PnL: **-35.39 ZAR**
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

- Label: **neutral** | breadth bear=0.4 bull=0.1333 neutral=0.4667 | symbols=15
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bull | consecutive_bear: 0 / bull 0
- as_of: 2026-09-29T18:35:33Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 832 | eligible: 4 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
  - `feat_time_since_low_20:2:SHORT:h15` edge=44.1b n=170 breadth=2 validated=False prov=False armable=False (too_few_rows)
  - `feat_time_since_low_20:2:SHORT:h12` edge=36.6b n=170 breadth=2 validated=False prov=False armable=False (too_few_rows)
  - `feat_time_since_low_20:2:SHORT:h20` edge=34.4b n=170 breadth=2 validated=False prov=False armable=False (too_few_rows)
  - `feat_time_since_low_20:2:SHORT:h24` edge=31.5b n=170 breadth=2 validated=False prov=False armable=False (regime_confounded)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-35.35 | frozen=YES
- HIP-3 lane: **RED** | closed=20 pnl=-41.12 | frozen=YES
- Frozen lanes: hip3, native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 17
  - `feat_atr_norm_ext:2:LONG:h15` pnl=+15.77
  - `feat_bb_pos_20:2:LONG:h15` pnl=+16.17
  - `feat_cci_20:2:LONG:h15` pnl=+10.70
  - `feat_close_pos_ma:1:LONG:h24` pnl=+283.35
  - `feat_close_pos_ma:2:LONG:h12` pnl=+121.93
  - `feat_close_pos_ma:2:LONG:h20` pnl=+5.01
  - `feat_close_position:2:LONG:h24` pnl=+1.68
  - `feat_ext_strength:2:LONG:h15` pnl=+24.00
  - `feat_ext_vs_ma_20:2:LONG:h15` pnl=+9.35
  - `feat_realized_vol_20:2:LONG:h20` pnl=+1.47
  - `feat_ret_10:2:LONG:h19` pnl=+14.58
  - `feat_ret_20:2:LONG:h14` pnl=+13.42
  - `feat_rsi_divergence:2:LONG:h20` pnl=+8.36
  - `feat_trend_slope_20:2:LONG:h12` pnl=+11.12
  - `feat_vol_sma_ratio:0:LONG:h24` pnl=+1.00
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **131/150** | hip3 **18/25**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 18
  - `feat_atr_norm_ext:2:LONG:h13` lane_not_green
  - `feat_buy_vol_ratio:2:LONG:h24` lane_not_green
  - `feat_donchian_break:2:LONG:h15` lane_not_green
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

- Latest scan 2026-09-29T18:26:46: errors=0 signals=513 regime_blocked=373
- this cycle: closed=0 new_signals=513 skipped=496 slot_full=0 slice_full=0 pair_held=17
- Action funnel: regime_blocked=373 | lane_gate_blocked=10 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=17 | slot_full=0 | skipped=496
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 10, "pair_held": 17, "regime_blocked": 373, "skipped": 496, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=False hip3_green=False frozen=hip3,native islands=17 blocks=18
- aggregate_risk: ok open=37.7553 cap=173.1351 used=0.2414 remaining=131.3421 replayed=6 no_new_bars=1
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
