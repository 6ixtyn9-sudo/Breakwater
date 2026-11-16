# Breakwater daily print — 2026-11-16 20:04 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **376.43 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2391.63 ZAR** (seed 2000) | lifetime: **+391.63 ZAR** | closed: 592
- Today: 1 closed, **-1.20 ZAR**
- 7d: **+42.66 ZAR** | 30d: **+106.49 ZAR**

## 2b. Claimed vs realised

- Book: 75 slices (native 55 | hip3 20); validated pools: native 262 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 75 book slices present in the validated pools): +0.446% | at 147.00 ZAR mean notional/trade: +0.66 ZAR/trade
- Realised (592 real closes per lane_gate._is_real_close, net of fees): +0.66 ZAR/trade | sd 4.68 | SE 0.19
- Gap: +0.01 ZAR/trade | t = +0.03 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.678% over 55/55 slices (pool 262) ~ +0.98 ZAR | realised 546 closes +0.80 ZAR sd 4.65 SE 0.20 | gap -0.19 t -0.94 | NOT ESTABLISHED
- hip3: claimed median +0.062% over 20/20 slices (pool 160) ~ +0.10 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.07 t -1.51 | NOT ESTABLISHED
- Ledger: 713 decision rows; 592 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 121 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 546 | wins: 281 | win%: 51.5 | P&L: **+436.14 ZAR** | today: -1.20 | 7d: +42.66 | 30d: +106.49
- By exit: target +516.3, trail_stop +249.2, horizon +83.4, max_bars +2.8, regime_shift -11.9, stop -403.6
- By entry regime (n/pnl): neutral 213/+234.4, bull 122/+199.3, bear 211/+2.5
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_trend_neutral:0:SHORT:h24 5n/5w +24.80; feat_premium@oi_hi:2:SHORT:h24 3n/3w +24.15; feat_ext_strength:2:LONG:h15 12n/8w +24.00
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_macd_12_26:2:SHORT:h15 3n/0w -11.55; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; ENAUSDC 7n +23.48; SOLUSDC 66n +19.89; BTCUSDC 64n +18.16
- Worst pairs: UNIUSDC 13n -30.75; ZECUSDC 17n -21.96; ETHZAR 4n -14.36; DOGEUSDC 17n -12.34; HYPEUSDC 40n -7.45

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 3 open, stop-risk **12.43 ZAR**
  - XRPUSDC SELL ntl=122 risk=4.82 bars=10 stop=0.9804950000000000080 peak=0.97627
  - ETHUSDC SELL ntl=122 risk=4.17 bars=8 stop=1866.550000000000045 peak=1866.2
  - BTCUSDC SELL ntl=122 risk=3.44 bars=9 stop=66354.00000000000015 peak=65679.0

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **12.43 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **12.43 / 171.24 ZAR | 7.8% | ok**
- Remaining: 157.8927 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 127, "skipped": 127, "slice_full": 0, "slot_full": 0}, "native": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 16, "signals": 54, "skipped": 38, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **XRPUSDC** 4.8220 ZAR
- positions without bars: 0 | replayed: 3 | invalid: 0

## 6. Monitored books

- Native: 55 | HIP-3: 20
- Native top (by paper P&L):
  - `feat_premium@oi_hi:2:SHORT:h24` edge=0.0045 n=2854 p=0.2962 src=validated_walk_forward unproven=False paper=3n/+24.15
  - `feat_vol_sma_ratio:1:SHORT:h24` edge=0.0041 n=9161 p=0.4004 src=validated_walk_forward unproven=False paper=1n/+3.25
  - `feat_vol_regime:2:SHORT:h24` edge=0.0053 n=8796 p=0.0918 src=validated_walk_forward unproven=False paper=2n/+3.02
  - `feat_close_position:0:SHORT:h24` edge=0.0056 n=9723 p=0.6490 src=validated_walk_forward unproven=False paper=1n/+2.70
  - `feat_oi_chg_24@oi_mid:2:SHORT:h12` edge=0.0117 n=1202 p=0.1799 src=validated_walk_forward unproven=False paper=1n/+0.85
  - `feat_oi_chg_24:0:SHORT:h20` edge=0.0086 n=5987 p=0.9514 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vol_roc_20:0:SHORT:h15` edge=0.0063 n=8988 p=0.4922 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_premium:0:SHORT:h15` edge=0.0043 n=11095 p=0.7964 src=validated_walk_forward unproven=False paper=0n/+0.00
- HIP-3 top (by paper P&L):
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` edge=0.0003 n=9570 p=0.3356 src=validated_walk_forward unproven=False paper=15n/+4.27
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

- Latest research: 2026-11-16T00:29:04.852446+00:00 | discovered 2240 | validated 262 | reg-confounded 788 | hostile-unproven 11
- floors: "" | book: {"rows": 57, "by_status": {"monitored": 55, "decayed": 2}, "in_validated_pool": 57, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=1120 validated=1120 passing=262 eligible=657 best=222.5b best_fail=breadth_ok
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=576 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_range_pos_20:L2S0:h20: mean=+7.8b t_no=2.73 folds=00101 mkt_corr=-0.39 dd=299b legs=11.7/10.9 fail=n_nonoverlap,folds,market_corr
  - feat_vwap_lower_dist:L2S0:h15: mean=+21.4b t_no=2.50 folds=10101 mkt_corr=-0.25 dd=192b legs=11.8/8.9 fail=n_nonoverlap,folds
  - feat_donchian_break:L2S0:h15: mean=+12.2b t_no=2.43 folds=10101 mkt_corr=-0.15 dd=138b legs=11.0/10.4 fail=n_nonoverlap,folds
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

- Label: **neutral** | breadth bear=0.2 bull=0.0 neutral=0.8 | symbols=15
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 0 / bull 0
- as_of: 2026-11-16T20:01:24Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 1120 | eligible: 967 | observations: 5218 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
  - `feat_funding_rate@oi_lo:2:SHORT:h24` edge=222.5b n=339 breadth=5 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_oi_chg_24@oi_hi:2:SHORT:h24` edge=202.9b n=973 breadth=13 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_oi_ret_div@oi_lo:0:SHORT:h20` edge=196.9b n=1529 breadth=13 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_oi_ret_div@oi_lo:0:SHORT:h24` edge=196.3b n=1541 breadth=13 validated=False prov=False armable=False (not_confirmed_bear)
  - `feat_oi_chg_24@oi_mid:2:SHORT:h24` edge=188.2b n=1298 breadth=13 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_oi_chg_24@oi_lo:1:SHORT:h24` edge=183.8b n=1378 breadth=13 validated=True prov=False armable=False (not_confirmed_bear)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+40.07 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **55/55** | hip3 **19/20**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 48
  - `feat_adx_14:2:LONG:h12` slice_pnl=-1.83
  - `feat_adx_14:2:LONG:h15` slice_pnl=-3.92
  - `feat_atr_norm_ext:2:LONG:h13` slice_pnl=-4.88
  - `feat_atr_percent:2:LONG:h12` slice_pnl=-1.44
  - `feat_atr_ratio:0:LONG:h24` slice_pnl=-10.03
  - `feat_bb_squeeze_20:2:LONG:h20` slice_pnl=-10.15
  - `feat_bb_width_20:2:LONG:h15` slice_pnl=-6.62
  - `feat_buy_vol_ratio:2:LONG:h24` slice_pnl=-6.57
  - `feat_cci_20:0:LONG:h24` slice_pnl=-17.74
  - `feat_cci_20:2:SHORT:h24` slice_pnl=-7.35
  - `feat_donchian_break:2:LONG:h15` slice_pnl=-2.57
  - `feat_ema_cross_10_20:2:LONG:h12` slice_pnl=-3.12
  - `feat_ema_cross_10_20:2:SHORT:h24` slice_pnl=-5.49
  - `feat_ext_vs_ma_50:0:LONG:h20` slice_pnl=-11.21
  - `feat_funding_cum_24:2:SHORT:h12` slice_pnl=-1.14
  - `feat_funding_rate:2:SHORT:h12` slice_pnl=-7.96
  - `feat_hour_utc:2:LONG:h15` slice_pnl=-1.61
  - `feat_kc_width:2:LONG:h12` slice_pnl=-6.60
  - `feat_kc_width:2:LONG:h15` slice_pnl=-0.19
  - `feat_macd_12_26:2:SHORT:h15` slice_pnl=-11.55
  - `feat_price_roc_5:2:LONG:h20` slice_pnl=-5.02
  - `feat_range_pos_20:2:LONG:h15` slice_pnl=-3.77
  - `feat_range_pos_50:0:LONG:h24` slice_pnl=-6.24
  - `feat_range_pos_50:2:SHORT:h24` slice_pnl=-10.55
  - `feat_realized_vol_20:2:LONG:h14` slice_pnl=-0.40
  - `feat_realized_vol_20:2:LONG:h20` slice_pnl=-2.15
  - `feat_realized_vol_20:2:LONG:h21` slice_pnl=-2.71
  - `feat_realized_vol_20:2:LONG:h22` slice_pnl=-1.39
  - `feat_realized_vol_20:2:LONG:h23` slice_pnl=-0.13
  - `feat_realized_vol_20:2:LONG:h24` slice_pnl=-13.68
  - `feat_ret_1:2:LONG:h24` slice_pnl=-1.95
  - `feat_ret_20:0:LONG:h24` slice_pnl=-3.42
  - `feat_ret_vol:0:LONG:h24` slice_pnl=-4.69
  - `feat_time_since_high_20:0:LONG:h12` slice_pnl=-4.14
  - `feat_trend_slope_20:2:SHORT:h24` slice_pnl=-2.57
  - `feat_vol_breakout:2:LONG:h15` slice_pnl=-6.39
  - `feat_vol_of_vol:1:LONG:h24` slice_pnl=-3.36
  - `feat_vol_of_vol:2:LONG:h12` slice_pnl=-1.49
  - `feat_vol_of_vol:2:LONG:h15` slice_pnl=-10.82
  - `feat_vol_sma_ratio:0:LONG:h24` slice_pnl=-2.20
  - `feat_vol_trend:0:LONG:h24` slice_pnl=-4.17
  - `feat_williams_r_14:0:SHORT:h24` slice_pnl=-1.23
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` lane_not_green
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-11-16T20:04:02: errors=0 signals=181 regime_blocked=104
- this cycle: closed=0 new_signals=181 skipped=165 slot_full=0 slice_full=0 pair_held=16
- Action funnel: regime_blocked=104 | lane_gate_blocked=1 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=16 | cluster_cap=0 | family_vetoed=0 | slot_full=0 | skipped=165
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "cluster_cap": 0, "family_vetoed": 0, "lane_gate_blocked": 1, "pair_held": 16, "regime_blocked": 104, "skipped": 165, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=48
- aggregate_risk: ok open=12.4259 cap=171.2355 used=0.0779 remaining=157.8927 replayed=3 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
