# Breakwater daily print — 2026-10-05 10:38 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **537.92 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2446.87 ZAR** (seed 2000) | lifetime: **+446.87 ZAR** | closed: 346
- Today: 8 closed, **+26.75 ZAR**
- 7d: **-12.69 ZAR** | 30d: **+446.87 ZAR**

## 2b. Claimed vs realised

- Book: 305 slices (native 280 | hip3 25); validated pools: native 546 | hip3 160; book slices absent from pools: 74
  - absent: `feat_cci_20:2:LONG:h12` (native)
  - absent: `feat_mean_rev_strength:0:LONG:h12` (native)
  - absent: `feat_ext_strength:2:LONG:h12` (native)
  - absent: `feat_ext_vs_ma_20:2:LONG:h12` (native)
  - absent: `feat_donchian_break:2:LONG:h12` (native)
  - absent: `feat_ret_10:2:LONG:h12` (native)
  - absent: `feat_range_pos_20:2:LONG:h12` (native)
  - absent: `feat_williams_r_14:0:LONG:h15` (native)
  - absent: `feat_vwap_upper_dist:2:LONG:h12` (native)
  - absent: `feat_ret_20:2:LONG:h12` (native)
  - ... and 64 more
- Claimed edge (median mean_ret_costadj over 231 book slices present in the validated pools): +0.408% | at 163.67 ZAR mean notional/trade: +0.67 ZAR/trade
- Realised (346 real closes per lane_gate._is_real_close, net of fees): +1.29 ZAR/trade | sd 5.37 | SE 0.29
- Gap: +0.62 ZAR/trade | t = +2.16 (one-sample t of realised mean vs the claimed constant) | verdict: EXCEEDS
- native: claimed median +0.420% over 210/280 slices (pool 546) ~ +0.69 ZAR | realised 300 closes +1.64 ZAR sd 5.37 SE 0.31 | gap +0.95 t +3.07 | EXCEEDS
- hip3: claimed median +0.065% over 21/25 slices (pool 160) ~ +0.11 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.08 t -1.52 | NOT ESTABLISHED
- Ledger: 261943 decision rows; 346 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 261597 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 300 | wins: 170 | win%: 56.7 | P&L: **+491.37 ZAR** | today: +26.75 | 7d: +23.46 | 30d: +491.37
- By exit: target +516.3, horizon +96.3, trail_stop +42.6, regime_shift -11.9, stop -151.9
- By entry regime (n/pnl): neutral 108/+285.1, bull 103/+188.9, bear 89/+17.4
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_range_pos_50:0:LONG:h24 6n/5w +21.46; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17
- Worst slices: feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; feat_ext_vs_ma_50:0:LONG:h24 2n/0w -6.90; engine_mean_reversion:rsi:2:SELL:h10:ZECUSDC 2n/0w -6.66; feat_bb_width_20:2:LONG:h15 3n/0w -6.62
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; BTCUSDC 30n +20.38; SUIUSDC 5n +19.60; XRPZAR 2n +18.07
- Worst pairs: ETHZAR 4n -14.36; ZECUSDC 8n -12.81; LTCUSDC 2n -6.24; BNBZAR 5n -5.43; NEARUSDC 4n -4.25

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: -36.16 | 30d: -44.50
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 11 open, stop-risk **37.69 ZAR**
  - UNIUSDC BUY ntl=247 risk=7.52 bars=5 stop=8.724850000000000690 peak=9.1442
  - ONDOUSDC BUY ntl=124 risk=4.86 bars=5 stop=0.475570000000000015 peak=0.51015
  - ZECUSDC BUY ntl=123 risk=4.68 bars=21 stop=1278.7500000000000115 peak=1368.8
  - TAOUSDC BUY ntl=124 risk=4.53 bars=2 stop=295.94000000000000960 peak=308.58
  - DOGEUSDC BUY ntl=124 risk=4.10 bars=5 stop=0.09205075000000000380 peak=0.097151
  - AAVEUSDC BUY ntl=123 risk=2.94 bars=14 stop=175.69000000000000970 peak=182.38
  - XRPUSDC BUY ntl=124 risk=2.57 bars=5 stop=1.4735750000000000070 peak=1.5275
  - BTCUSDC BUY ntl=124 risk=2.16 bars=5 stop=84026.34750 peak=86491.0
  - ETHUSDC BUY ntl=123 risk=2.16 bars=10 stop=2679.08100 peak=2737.5
  - SOLUSDC BUY ntl=123 risk=2.16 bars=10 stop=119.422875 peak=122.07
  - HYPEUSDC BUY ntl=123 risk=0.00 bars=14 stop=92.24083750 peak=93.821

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **37.69 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **37.69 / 174.42 ZAR | 23.7% | ok**
- Remaining: 133.0263 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 18, "skipped": 18, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 24, "signals": 875, "skipped": 851, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **UNIUSDC** 7.5210 ZAR
- positions without bars: 0 | replayed: 12 | invalid: 0

## 6. Monitored books

- Native: 280 | HIP-3: 25
- Native top (by paper P&L):
  - `feat_range_pos_50:0:LONG:h24` edge=0.0057 n=9303 p=0.0002 src=validated_walk_forward unproven=False paper=6n/+21.45
  - `feat_range_pos_50:0:LONG:h24` edge=0.0081 n=11086 p=0.0000 src=validated_walk_forward unproven=False paper=6n/+21.45
  - `feat_bb_pos_20:2:LONG:h15` edge=0.0040 n=10327 p=0.0019 src=validated_walk_forward unproven=False paper=4n/+16.17
  - `feat_atr_norm_ext:2:LONG:h15` edge=0.0041 n=10348 p=0.0006 src=validated_walk_forward unproven=False paper=3n/+15.77
  - `feat_ret_vol:0:LONG:h24` edge=0.0085 n=10329 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+10.84
  - `feat_ret_vol:0:LONG:h24` edge=0.0073 n=10551 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+10.84
  - `feat_vol_regime:2:LONG:h12` edge=0.0044 n=11267 p=0.0001 src=validated_walk_forward unproven=False paper=5n/+7.60
  - `feat_vol_regime:2:LONG:h12` edge=0.0062 n=8545 p=0.0003 src=validated_walk_forward unproven=False paper=5n/+7.60
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

- Label: **neutral** | breadth bear=0.1111 bull=0.2778 neutral=0.6111 | symbols=18
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 0 / bull 0
- as_of: 2026-10-05T10:00:30Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 832 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+32.53 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **210/280** | hip3 **18/25**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 21
  - `feat_atr_norm_ext:2:LONG:h13` slice_pnl=-4.88
  - `feat_bb_width_20:2:LONG:h15` slice_pnl=-6.62
  - `feat_buy_vol_ratio:2:LONG:h24` slice_pnl=-6.57
  - `feat_donchian_break:2:LONG:h15` slice_pnl=-2.57
  - `feat_price_roc_5:2:LONG:h20` slice_pnl=-5.02
  - `feat_range_pos_20:2:LONG:h15` slice_pnl=-3.77
  - `feat_realized_vol_20:2:LONG:h14` slice_pnl=-0.40
  - `feat_realized_vol_20:2:LONG:h21` slice_pnl=-2.71
  - `feat_realized_vol_20:2:LONG:h22` slice_pnl=-1.39
  - `feat_realized_vol_20:2:LONG:h23` slice_pnl=-0.13
  - `feat_realized_vol_20:2:LONG:h24` slice_pnl=-13.68
  - `feat_ret_1:2:LONG:h24` slice_pnl=-1.95
  - `feat_time_since_high_20:0:LONG:h12` slice_pnl=-4.14
  - `feat_vol_breakout:2:LONG:h15` slice_pnl=-6.39
  - `feat_vol_of_vol:1:LONG:h24` slice_pnl=-3.36
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` lane_not_green
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-10-05T10:38:13: errors=0 signals=893 regime_blocked=524
- this cycle: closed=1 new_signals=893 skipped=869 slot_full=0 slice_full=0 pair_held=24
- Action funnel: regime_blocked=524 | lane_gate_blocked=11 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=24 | slot_full=0 | skipped=869
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 11, "pair_held": 24, "regime_blocked": 524, "skipped": 869, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=21
- aggregate_risk: ok open=37.6922 cap=174.4242 used=0.2373 remaining=133.0263 replayed=12 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
