# Breakwater daily print — 2026-10-09 19:09 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **483.18 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2345.24 ZAR** (seed 2000) | lifetime: **+345.24 ZAR** | closed: 388
- Today: 2 closed, **-4.86 ZAR**
- 7d: **-70.90 ZAR** | 30d: **+345.24 ZAR**

## 2b. Claimed vs realised

- Book: 59 slices (native 34 | hip3 25); validated pools: native 11 | hip3 160; book slices absent from pools: 32
  - absent: `feat_time_since_low_20:2:LONG:h12` (native)
  - absent: `feat_atr_percent:2:LONG:h12` (native)
  - absent: `feat_kc_width:2:LONG:h15` (native)
  - absent: `feat_vwap_lower_dist:0:LONG:h24` (native)
  - absent: `feat_mean_rev_strength:0:LONG:h12` (native)
  - absent: `feat_ext_strength:2:LONG:h12` (native)
  - absent: `feat_ext_vs_ma_20:2:LONG:h12` (native)
  - absent: `feat_ret_10:2:LONG:h12` (native)
  - absent: `feat_range_pos_20:2:LONG:h12` (native)
  - absent: `feat_ret_20:2:LONG:h12` (native)
  - ... and 22 more
- Claimed edge (median mean_ret_costadj over 27 book slices present in the validated pools): +0.085% | at 161.81 ZAR mean notional/trade: +0.14 ZAR/trade
- Realised (388 real closes per lane_gate._is_real_close, net of fees): +0.89 ZAR/trade | sd 5.28 | SE 0.27
- Gap: +0.75 ZAR/trade | t = +2.81 (one-sample t of realised mean vs the claimed constant) | verdict: EXCEEDS
- native: claimed median +0.564% over 6/34 slices (pool 11) ~ +0.91 ZAR | realised 342 closes +1.14 ZAR sd 5.29 SE 0.29 | gap +0.23 t +0.81 | NOT ESTABLISHED
- hip3: claimed median +0.065% over 21/25 slices (pool 160) ~ +0.11 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.08 t -1.52 | NOT ESTABLISHED
- Ledger: 312591 decision rows; 388 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 312203 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 342 | wins: 177 | win%: 51.8 | P&L: **+389.75 ZAR** | today: -4.86 | 7d: -70.90 | 30d: +389.75
- By exit: target +516.3, horizon +78.3, trail_stop +47.3, regime_shift -11.9, stop -240.3
- By entry regime (n/pnl): neutral 130/+226.5, bull 112/+179.0, bear 100/-15.8
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_bb_squeeze_20:2:LONG:h20 3n/1w -9.38; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; feat_ext_vs_ma_50:0:LONG:h24 2n/0w -6.90
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPZAR 2n +18.07; ENAUSDC 2n +17.64; BTCUSDC 35n +13.32
- Worst pairs: UNIUSDC 6n -21.90; ZECUSDC 10n -15.50; ETHZAR 4n -14.36; ETHUSDC 40n -11.55; DOGEUSDC 14n -7.39

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: -44.50
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 5 open, stop-risk **27.30 ZAR**
  - HYPEUSDC BUY ntl=239 risk=9.51 bars=15 stop=81.95949999999999330 peak=86.5
  - SOLUSDC BUY ntl=119 risk=4.62 bars=13 stop=105.9999999999999930 peak=111.98
  - SUIUSDC BUY ntl=119 risk=4.56 bars=9 stop=1.0292250000000000615 peak=1.0796
  - ZECUSDC BUY ntl=119 risk=4.56 bars=9 stop=1186.2000000000000355 peak=1246.9
  - ETHUSDC BUY ntl=119 risk=4.04 bars=15 stop=2408.174999999999630 peak=2519.4

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **27.30 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **27.30 / 166.86 ZAR | 17.4% | ok**
- Remaining: 137.7762 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 91, "skipped": 91, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 3, "signals": 32, "skipped": 29, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **HYPEUSDC** 9.5130 ZAR
- positions without bars: 0 | replayed: 6 | invalid: 0

## 6. Monitored books

- Native: 34 | HIP-3: 25
- Native top (by paper P&L):
  - `feat_bb_pos_20:2:LONG:h15` edge=0.0040 n=10327 p=0.0019 src=validated_walk_forward unproven=False paper=4n/+16.17
  - `feat_atr_norm_ext:2:LONG:h15` edge=0.0041 n=10348 p=0.0006 src=validated_walk_forward unproven=False paper=3n/+15.77
  - `feat_zscore_20:2:LONG:h15` edge=0.0040 n=10327 p=0.0019 src=validated_walk_forward unproven=False paper=2n/+4.17
  - `feat_rsi_14:2:LONG:h15` edge=0.0036 n=10124 p=0.0021 src=validated_walk_forward unproven=False paper=1n/+3.63
  - `feat_ext_vs_ma_10:2:LONG:h15` edge=0.0045 n=9740 p=0.0005 src=validated_walk_forward unproven=False paper=1n/+2.49
  - `feat_close_pos_ma:2:LONG:h15` edge=0.0054 n=9374 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+1.94
  - `feat_realized_vol_20:2:LONG:h20` edge=0.0061 n=11077 p=0.0075 src=validated_walk_forward unproven=False paper=8n/+1.47
  - `feat_keltner_pos:2:LONG:h15` edge=0.0033 n=10530 p=0.0112 src=validated_walk_forward unproven=False paper=1n/+1.46
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

- Label: **bear** | breadth bear=0.8125 bull=0.0625 neutral=0.125 | symbols=16
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 50 / bull 0
- as_of: 2026-10-09T19:00:28Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 832 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-64.49 | frozen=YES
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3, native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 20
  - `feat_atr_norm_ext:2:LONG:h15` pnl=+15.77
  - `feat_bb_pos_20:2:LONG:h15` pnl=+16.17
  - `feat_cci_20:2:LONG:h15` pnl=+10.70
  - `feat_close_pos_ma:1:LONG:h24` pnl=+283.35
  - `feat_close_pos_ma:2:LONG:h12` pnl=+121.93
  - `feat_close_pos_ma:2:LONG:h15` pnl=+1.94
  - `feat_close_pos_ma:2:LONG:h20` pnl=+5.01
  - `feat_close_position:2:LONG:h24` pnl=+1.16
  - `feat_ext_strength:2:LONG:h15` pnl=+24.00
  - `feat_ext_vs_ma_20:2:LONG:h15` pnl=+9.35
  - `feat_intraday_mom:2:LONG:h24` pnl=+7.09
  - `feat_price_roc_5:1:LONG:h24` pnl=+0.70
  - `feat_realized_vol_20:2:LONG:h20` pnl=+1.47
  - `feat_ret_10:2:LONG:h19` pnl=+14.58
  - `feat_ret_20:2:LONG:h14` pnl=+13.42
  - `feat_rsi_divergence:2:LONG:h20` pnl=+8.36
  - `feat_trend_slope_20:2:LONG:h12` pnl=+11.12
  - `feat_vol_sma_ratio:0:LONG:h24` pnl=+1.00
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **32/34** | hip3 **18/25**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 29
  - `feat_adx_14:2:LONG:h12` lane_not_green
  - `feat_adx_14:2:LONG:h15` lane_not_green
  - `feat_atr_norm_ext:2:LONG:h13` lane_not_green
  - `feat_bb_squeeze_20:2:LONG:h20` lane_not_green
  - `feat_bb_width_20:2:LONG:h15` lane_not_green
  - `feat_buy_vol_ratio:2:LONG:h24` lane_not_green
  - `feat_cci_20:0:LONG:h24` lane_not_green
  - `feat_donchian_break:2:LONG:h15` lane_not_green
  - `feat_ema_cross_10_20:2:LONG:h12` lane_not_green
  - `feat_price_roc_5:2:LONG:h20` lane_not_green
  - `feat_range_pos_20:2:LONG:h15` lane_not_green
  - `feat_range_pos_50:0:LONG:h24` lane_not_green
  - `feat_realized_vol_20:2:LONG:h14` lane_not_green
  - `feat_realized_vol_20:2:LONG:h21` lane_not_green
  - `feat_realized_vol_20:2:LONG:h22` lane_not_green
  - `feat_realized_vol_20:2:LONG:h23` lane_not_green
  - `feat_realized_vol_20:2:LONG:h24` lane_not_green
  - `feat_ret_1:2:LONG:h24` lane_not_green
  - `feat_ret_vol:0:LONG:h24` lane_not_green
  - `feat_time_since_high_20:0:LONG:h12` lane_not_green
  - `feat_vol_breakout:2:LONG:h15` lane_not_green
  - `feat_vol_of_vol:1:LONG:h24` lane_not_green
  - `feat_vol_trend:0:LONG:h24` lane_not_green
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` lane_not_green
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-10-09T19:09:49: errors=0 signals=123 regime_blocked=43
- this cycle: closed=1 new_signals=123 skipped=120 slot_full=0 slice_full=0 pair_held=3
- Action funnel: regime_blocked=43 | lane_gate_blocked=9 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=3 | slot_full=0 | skipped=120
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 9, "pair_held": 3, "regime_blocked": 43, "skipped": 120, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=False hip3_green=False frozen=hip3,native islands=19 blocks=29
- aggregate_risk: ok open=27.2968 cap=166.8645 used=0.1743 remaining=137.7762 replayed=6 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
