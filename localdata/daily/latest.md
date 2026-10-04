# Breakwater daily print — 2026-10-04 02:24 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **528.10 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2411.87 ZAR** (seed 2000) | lifetime: **+411.87 ZAR** | closed: 324
- Today: 1 closed, **-1.17 ZAR**
- 7d: **-80.89 ZAR** | 30d: **+411.87 ZAR**

## 2b. Claimed vs realised

- Book: 306 slices (native 281 | hip3 25); validated pools: native 186 | hip3 160; book slices absent from pools: 195
  - absent: `feat_gap_fill_ratio:0:LONG:h12` (native)
  - absent: `feat_rsi_divergence:2:LONG:h15` (native)
  - absent: `feat_cci_20:2:LONG:h12` (native)
  - absent: `feat_mean_rev_strength:0:LONG:h12` (native)
  - absent: `feat_ext_strength:2:LONG:h12` (native)
  - absent: `feat_ext_vs_ma_20:2:LONG:h12` (native)
  - absent: `feat_donchian_break:2:LONG:h12` (native)
  - absent: `feat_ret_10:2:LONG:h12` (native)
  - absent: `feat_range_pos_20:2:LONG:h12` (native)
  - absent: `feat_vol_roc_20:0:LONG:h12` (native)
  - ... and 185 more
- Claimed edge (median mean_ret_costadj over 111 book slices present in the validated pools): +0.531% | at 166.05 ZAR mean notional/trade: +0.88 ZAR/trade
- Realised (324 real closes per lane_gate._is_real_close, net of fees): +1.27 ZAR/trade | sd 5.45 | SE 0.30
- Gap: +0.39 ZAR/trade | t = +1.28 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.566% over 90/281 slices (pool 186) ~ +0.94 ZAR | realised 278 closes +1.64 ZAR sd 5.47 SE 0.33 | gap +0.70 t +2.14 | EXCEEDS
- hip3: claimed median +0.065% over 21/25 slices (pool 160) ~ +0.11 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.08 t -1.52 | NOT ESTABLISHED
- Ledger: 243935 decision rows; 324 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 243611 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 278 | wins: 156 | win%: 56.1 | P&L: **+456.37 ZAR** | today: -1.17 | 7d: -44.73 | 30d: +456.37
- By exit: target +516.3, horizon +92.1, trail_stop +11.8, regime_shift -11.9, stop -151.9
- By entry regime (n/pnl): neutral 100/+280.7, bull 99/+190.6, bear 79/-15.0
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; feat_ext_vs_ma_50:0:LONG:h24 2n/0w -6.90; engine_mean_reversion:rsi:2:SELL:h10:ZECUSDC 2n/0w -6.66; feat_bb_width_20:2:LONG:h15 3n/0w -6.62
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; BTCUSDC 28n +19.20; XRPZAR 2n +18.07; SUIUSDC 3n +14.91
- Worst pairs: ETHZAR 4n -14.36; ZECUSDC 8n -12.81; NEARUSDC 3n -8.75; LTCUSDC 2n -6.24; BNBZAR 5n -5.43

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: -36.16 | 30d: -44.50
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 11 open, stop-risk **46.04 ZAR**
  - ENAUSDC BUY ntl=246 risk=9.31 bars=11 stop=0.223654999999999985 peak=0.24
  - UNIUSDC BUY ntl=123 risk=4.91 bars=6 stop=8.663325000000000385 peak=9.08
  - NEARUSDC BUY ntl=123 risk=4.77 bars=13 stop=4.513225000000000030 peak=4.8734
  - HYPEUSDC BUY ntl=123 risk=4.49 bars=15 stop=84.55450000000000775 peak=89.732
  - AAVEUSDC BUY ntl=123 risk=4.31 bars=4 stop=173.54500000000000710 peak=181.61
  - ONDOUSDC BUY ntl=123 risk=4.09 bars=10 stop=0.4724750000000000220 peak=0.50344
  - SUIUSDC BUY ntl=123 risk=3.87 bars=0 stop=1.1476749999999998890 peak=1.185
  - SOLUSDC BUY ntl=123 risk=3.84 bars=21 stop=115.1249999999999880 peak=120.01
  - BTCUSDC BUY ntl=123 risk=2.15 bars=17 stop=83059.56750 peak=85003.0
  - ETHUSDC BUY ntl=123 risk=2.15 bars=13 stop=2636.14575 peak=2689.1
  - XRPUSDC BUY ntl=123 risk=2.15 bars=11 stop=1.45930725 peak=1.4959

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **46.04 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **46.04 / 171.97 ZAR | 28.9% | ok**
- Remaining: 122.2501 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 17, "skipped": 17, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 0, "opened": 1, "pair_held": 22, "signals": 894, "skipped": 847, "slice_full": 2, "slot_full": 22}}
- Highest-risk: **ENAUSDC** 9.3100 ZAR
- positions without bars: 0 | replayed: 22 | invalid: 0

## 6. Monitored books

- Native: 281 | HIP-3: 25
- Native top (by paper P&L):
  - `feat_bb_pos_20:2:LONG:h15` edge=0.0040 n=10327 p=0.0019 src=validated_walk_forward unproven=False paper=4n/+16.17
  - `feat_atr_norm_ext:2:LONG:h15` edge=0.0041 n=10348 p=0.0006 src=validated_walk_forward unproven=False paper=3n/+15.77
  - `feat_vol_regime:2:LONG:h12` edge=0.0044 n=11267 p=0.0001 src=validated_walk_forward unproven=False paper=5n/+7.60
  - `feat_vol_regime:2:LONG:h12` edge=0.0062 n=8545 p=0.0003 src=validated_walk_forward unproven=False paper=5n/+7.60
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0058 n=17004 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+5.56
  - `feat_zscore_20:2:LONG:h15` edge=0.0040 n=10327 p=0.0019 src=validated_walk_forward unproven=False paper=2n/+4.17
  - `feat_range_pos_50:0:LONG:h24` edge=0.0057 n=9303 p=0.0002 src=validated_walk_forward unproven=False paper=5n/+3.71
  - `feat_range_pos_50:0:LONG:h24` edge=0.0081 n=11086 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+3.71
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

- Label: **neutral** | breadth bear=0.1765 bull=0.3529 neutral=0.4706 | symbols=17
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 0 / bull 0
- as_of: 2026-10-04T01:35:27Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 832 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-3.85 | frozen=YES
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
  - `feat_close_position:2:LONG:h24` pnl=+3.31
  - `feat_ext_strength:2:LONG:h15` pnl=+24.00
  - `feat_ext_vs_ma_20:2:LONG:h15` pnl=+9.35
  - `feat_range_pos_50:0:LONG:h24` pnl=+3.71
  - `feat_realized_vol_20:2:LONG:h20` pnl=+1.47
  - `feat_ret_10:2:LONG:h19` pnl=+14.58
  - `feat_ret_20:2:LONG:h14` pnl=+13.42
  - `feat_rsi_divergence:2:LONG:h20` pnl=+8.36
  - `feat_trend_slope_20:2:LONG:h12` pnl=+11.12
  - `feat_vol_sma_ratio:0:LONG:h24` pnl=+1.00
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **210/281** | hip3 **18/25**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 21
  - `feat_atr_norm_ext:2:LONG:h13` lane_not_green
  - `feat_bb_width_20:2:LONG:h15` lane_not_green
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
  - `feat_vol_of_vol:1:LONG:h24` lane_not_green
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` lane_not_green
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-10-04T00:51:49: errors=0 signals=911 regime_blocked=387
- this cycle: closed=1 new_signals=911 skipped=864 slot_full=22 slice_full=2 pair_held=22
- Action funnel: regime_blocked=387 | lane_gate_blocked=10 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=2 | pair_held=22 | slot_full=22 | skipped=864
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 10, "pair_held": 22, "regime_blocked": 387, "skipped": 864, "slice_full": 2, "slot_full": 22})
- green_gate: native_green=False hip3_green=False frozen=hip3,native islands=18 blocks=20
- aggregate_risk: ok open=42.1671 cap=171.9740 used=0.2891 remaining=122.2501 replayed=22 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
