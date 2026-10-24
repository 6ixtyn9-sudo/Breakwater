# Breakwater daily print — 2026-10-24 13:07 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

> ## COMA ALARM — NATIVE

> No **proven** slice in this lane. Auditions can still open entries, so
> this is not a dead lane: it trades, but nothing in it trades on a record
> it earned, so it cannot unfreeze itself. The runner will keep reporting
> operational, which is why this block exists. Attention, not intervention.

## 1. Posture

- Mode: **readonly** | VALR equity: **430.26 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2277.15 ZAR** (seed 2000) | lifetime: **+277.15 ZAR** | closed: 464
- Today: 2 closed, **+3.68 ZAR**
- 7d: **-21.62 ZAR** | 30d: **-197.49 ZAR**

## 2b. Claimed vs realised

- Book: 69 slices (native 49 | hip3 20); validated pools: native 143 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 69 book slices present in the validated pools): +0.144% | at 155.16 ZAR mean notional/trade: +0.22 ZAR/trade
- Realised (464 real closes per lane_gate._is_real_close, net of fees): +0.60 ZAR/trade | sd 4.99 | SE 0.23
- Gap: +0.37 ZAR/trade | t = +1.61 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.377% over 49/49 slices (pool 143) ~ +0.58 ZAR | realised 418 closes +0.77 ZAR sd 4.99 SE 0.24 | gap +0.19 t +0.78 | NOT ESTABLISHED
- hip3: claimed median +0.062% over 20/20 slices (pool 160) ~ +0.10 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.07 t -1.51 | NOT ESTABLISHED
- Ledger: 563 decision rows; 464 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 99 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 418 | wins: 203 | win%: 48.6 | P&L: **+321.65 ZAR** | today: +3.68 | 7d: -21.62 | 30d: -158.62
- By exit: target +516.3, trail_stop +74.8, horizon +72.8, max_bars +2.8, regime_shift -11.9, stop -333.1
- By entry regime (n/pnl): neutral 163/+222.1, bull 113/+176.5, bear 142/-77.0
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82; feat_range_pos_50:2:SHORT:h24 3n/0w -10.55
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPZAR 2n +18.07; XMRUSDC 5n +13.98; BTCUSDC 45n +9.55
- Worst pairs: UNIUSDC 7n -21.68; ETHUSDC 54n -21.35; ZECUSDC 14n -18.75; XRPUSDC 42n -17.44; ETHZAR 4n -14.36

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: -38.87
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 2 open, stop-risk **0.00 ZAR**
  - SOLUSDC SELL ntl=115 risk=0.00 bars=68 stop=103.852499999999997400 peak=109.19
  - XRPUSDC SELL ntl=116 risk=0.00 bars=31 stop=1.30810000000000002850 peak=1.3306

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **0.00 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 162.14 ZAR | 0.4% | ok**
- Remaining: 161.5602 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 29, "skipped": 29, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 5, "signals": 37, "skipped": 32, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **SOLUSDC** 0.0000 ZAR
- positions without bars: 0 | replayed: 2 | invalid: 0

## 6. Monitored books

- Native: 49 | HIP-3: 20
- Native top (by paper P&L):
  - `feat_donchian_break:2:SHORT:h24` edge=0.0058 n=8039 p=0.2408 src=validated_walk_forward unproven=False paper=2n/+3.68
  - `feat_vwap_dist:2:SHORT:h12` edge=0.0032 n=8260 p=0.1910 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vwap_upper_dist:2:SHORT:h15` edge=0.0038 n=7928 p=0.1125 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vwap_lower_dist:2:SHORT:h15` edge=0.0043 n=8560 p=0.1439 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_20:2:SHORT:h20` edge=0.0059 n=7499 p=0.0658 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_trend_slope_20:2:SHORT:h20` edge=0.0057 n=7614 p=0.0588 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_time_since_low_20:2:SHORT:h20` edge=0.0073 n=817 p=0.3580 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_macd_12_26:2:SHORT:h20` edge=0.0070 n=8398 p=0.0081 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Latest research: 2026-10-24T00:58:01.215903+00:00 | discovered 1664 | validated 143 | reg-confounded 394 | hostile-unproven 4
- floors: "" | book: {"rows": 51, "by_status": {"monitored": 49, "decayed": 2}, "in_validated_pool": 51, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=832 validated=832 passing=143 eligible=67 best=92.2b best_fail=regime_confounded
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=528 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_time_since_low_20:L2S0:h20: mean=+44.9b t_no=3.20 folds=00001 mkt_corr=+0.30 dd=0b legs=4.0/8.0 fail=n_nonoverlap,folds,market_corr
  - feat_ret_1:L0S2:h20: mean=-11.6b t_no=2.57 folds=10000 mkt_corr=+0.04 dd=185b legs=11.8/11.3 fail=n_nonoverlap,mean<=0,folds
  - feat_time_since_low_20:L2S0:h12: mean=+13.2b t_no=2.56 folds=11010 mkt_corr=+0.38 dd=39b legs=4.0/8.0 fail=n_nonoverlap,folds,market_corr
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

- Label: **bear** | breadth bear=0.6 bull=0.0 neutral=0.4 | symbols=15
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 5 / bull 0
- as_of: 2026-10-24T12:35:33Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 832 | eligible: 146 | observations: 197 | armable: **75**
- Armable slices: feat_atr_norm_ext:2:SHORT:h20, feat_atr_norm_ext:2:SHORT:h24, feat_atr_percent:1:SHORT:h20, feat_atr_percent:1:SHORT:h24, feat_ext_strength:2:SHORT:h12, feat_ext_strength:2:SHORT:h15, feat_ext_strength:2:SHORT:h20, feat_ext_strength:2:SHORT:h24, feat_ext_vs_ma_10:2:SHORT:h24, feat_ext_vs_ma_20:2:SHORT:h12, feat_ext_vs_ma_20:2:SHORT:h15, feat_ext_vs_ma_20:2:SHORT:h20, feat_ext_vs_ma_20:2:SHORT:h24, feat_keltner_pos:2:SHORT:h20, feat_keltner_pos:2:SHORT:h24, feat_mean_rev_strength:0:SHORT:h20, feat_mean_rev_strength:0:SHORT:h24, feat_range_pos_20:2:SHORT:h12, feat_range_pos_20:2:SHORT:h15, feat_range_pos_20:2:SHORT:h20, feat_range_pos_20:2:SHORT:h24, feat_ret_10:2:SHORT:h15, feat_ret_10:2:SHORT:h20, feat_ret_10:2:SHORT:h24, feat_rsi_21:2:SHORT:h20, feat_rsi_21:2:SHORT:h24, feat_stoch_d_14:2:SHORT:h12, feat_stoch_d_14:2:SHORT:h15, feat_stoch_d_14:2:SHORT:h20, feat_stoch_d_14:2:SHORT:h24, feat_stoch_k_14:2:SHORT:h12, feat_stoch_k_14:2:SHORT:h15, feat_stoch_k_14:2:SHORT:h20, feat_stoch_k_14:2:SHORT:h24, feat_time_since_low_20:1:SHORT:h20, feat_time_since_low_20:1:SHORT:h24, feat_trend_neutral:1:SHORT:h15, feat_vol_breakout:2:SHORT:h15, feat_vol_breakout:2:SHORT:h20, feat_vol_breakout:2:SHORT:h24, feat_vol_of_vol:2:SHORT:h24, feat_vwap_dist:2:SHORT:h12, feat_vwap_dist:2:SHORT:h15, feat_vwap_dist:2:SHORT:h20, feat_vwap_dist:2:SHORT:h24, feat_vwap_lower_dist:2:SHORT:h12, feat_vwap_lower_dist:2:SHORT:h15, feat_vwap_lower_dist:2:SHORT:h20, feat_vwap_lower_dist:2:SHORT:h24, feat_vwap_upper_dist:2:SHORT:h12, feat_vwap_upper_dist:2:SHORT:h15, feat_vwap_upper_dist:2:SHORT:h20, feat_vwap_upper_dist:2:SHORT:h24, feat_williams_r_14:0:SHORT:h12, feat_williams_r_14:0:SHORT:h15, feat_williams_r_14:0:SHORT:h20, feat_williams_r_14:0:SHORT:h24
- Armable pairs: BTCUSDC, ENAUSDC, ETHUSDC, KPEPEUSDC, NEARUSDC, WLDUSDC, XMRUSDC, ZECUSDC, ZROUSDC
  - `feat_ext_vs_ma_50:2:SHORT:h24` edge=92.2b n=6208 breadth=40 validated=True prov=False armable=True (ok)
  - `feat_time_since_low_20:2:SHORT:h24` edge=83.4b n=817 breadth=9 validated=True prov=False armable=True (ok)
  - `feat_macd_12_26:2:SHORT:h24` edge=78.9b n=8390 breadth=40 validated=True prov=False armable=True (ok)
  - `feat_ext_vs_ma_50:2:SHORT:h20` edge=74.7b n=6215 breadth=40 validated=True prov=False armable=True (ok)
  - `feat_time_since_low_20:2:SHORT:h20` edge=72.6b n=817 breadth=9 validated=True prov=False armable=True (ok)
  - `feat_ema_cross_10_20:2:SHORT:h24` edge=71.2b n=8161 breadth=40 validated=True prov=False armable=True (ok)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-17.23 | frozen=YES
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3, native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 20
  - `feat_atr_norm_ext:2:LONG:h15` pnl=+15.77
  - `feat_bb_pos_20:2:LONG:h15` pnl=+16.17
  - `feat_bb_width_20:2:LONG:h20` pnl=+1.39
  - `feat_cci_20:2:LONG:h15` pnl=+10.70
  - `feat_close_pos_ma:1:LONG:h24` pnl=+283.35
  - `feat_close_pos_ma:2:LONG:h12` pnl=+121.93
  - `feat_close_pos_ma:2:LONG:h15` pnl=+4.06
  - `feat_close_pos_ma:2:LONG:h20` pnl=+5.01
  - `feat_close_position:2:LONG:h24` pnl=+1.16
  - `feat_ext_strength:2:LONG:h15` pnl=+24.00
  - `feat_ext_vs_ma_20:2:LONG:h15` pnl=+9.35
  - `feat_intraday_mom:2:LONG:h24` pnl=+7.09
  - `feat_price_roc_5:1:LONG:h24` pnl=+0.70
  - `feat_realized_vol_20:2:LONG:h12` pnl=+0.61
  - `feat_ret_10:2:LONG:h19` pnl=+14.58
  - `feat_ret_20:2:LONG:h14` pnl=+13.42
  - `feat_rsi_divergence:2:LONG:h20` pnl=+8.36
  - `feat_trend_slope_20:2:LONG:h12` pnl=+11.12
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **48/49** | hip3 **18/20**
- **COMA LANES: native** — frozen with no tradable slice on an earned green record; auditions may still open.
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 42
  - `feat_adx_14:2:LONG:h12` lane_not_green
  - `feat_adx_14:2:LONG:h15` lane_not_green
  - `feat_atr_norm_ext:2:LONG:h13` lane_not_green
  - `feat_atr_percent:2:LONG:h12` lane_not_green
  - `feat_atr_ratio:0:LONG:h24` lane_not_green
  - `feat_bb_squeeze_20:2:LONG:h20` lane_not_green
  - `feat_bb_width_20:2:LONG:h15` lane_not_green
  - `feat_buy_vol_ratio:2:LONG:h24` lane_not_green
  - `feat_cci_20:0:LONG:h24` lane_not_green
  - `feat_cci_20:2:SHORT:h24` lane_not_green
  - `feat_donchian_break:2:LONG:h15` lane_not_green
  - `feat_ema_cross_10_20:2:LONG:h12` lane_not_green
  - `feat_ext_vs_ma_50:0:LONG:h20` lane_not_green
  - `feat_hour_utc:2:LONG:h15` lane_not_green
  - `feat_kc_width:2:LONG:h12` lane_not_green
  - `feat_kc_width:2:LONG:h15` lane_not_green
  - `feat_price_roc_5:2:LONG:h20` lane_not_green
  - `feat_range_pos_20:2:LONG:h15` lane_not_green
  - `feat_range_pos_50:0:LONG:h24` lane_not_green
  - `feat_range_pos_50:2:SHORT:h24` lane_not_green
  - `feat_realized_vol_20:2:LONG:h14` lane_not_green
  - `feat_realized_vol_20:2:LONG:h20` lane_not_green
  - `feat_realized_vol_20:2:LONG:h21` lane_not_green
  - `feat_realized_vol_20:2:LONG:h22` lane_not_green
  - `feat_realized_vol_20:2:LONG:h23` lane_not_green
  - `feat_realized_vol_20:2:LONG:h24` lane_not_green
  - `feat_ret_1:2:LONG:h24` lane_not_green
  - `feat_ret_20:0:LONG:h24` lane_not_green
  - `feat_ret_vol:0:LONG:h24` lane_not_green
  - `feat_time_since_high_20:0:LONG:h12` lane_not_green
  - `feat_vol_breakout:2:LONG:h15` lane_not_green
  - `feat_vol_of_vol:1:LONG:h24` lane_not_green
  - `feat_vol_of_vol:2:LONG:h12` lane_not_green
  - `feat_vol_of_vol:2:LONG:h15` lane_not_green
  - `feat_vol_sma_ratio:0:LONG:h24` lane_not_green
  - `feat_vol_trend:0:LONG:h24` lane_not_green
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` lane_not_green
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-10-24T12:12:22: errors=0 signals=66 regime_blocked=104
- this cycle: closed=0 new_signals=66 skipped=61 slot_full=0 slice_full=0 pair_held=5
- Action funnel: regime_blocked=104 | lane_gate_blocked=3 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=5 | slot_full=0 | skipped=61
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 3, "pair_held": 5, "regime_blocked": 104, "skipped": 61, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=False hip3_green=False frozen=hip3,native islands=20 blocks=42
- aggregate_risk: ok open=0.0000 cap=162.1379 used=0.0036 remaining=161.5602 replayed=2 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
