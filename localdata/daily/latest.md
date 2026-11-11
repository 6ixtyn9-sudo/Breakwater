# Breakwater daily print — 2026-11-11 17:09 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **390.31 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2350.45 ZAR** (seed 2000) | lifetime: **+350.45 ZAR** | closed: 578
- Today: 2 closed, **-4.44 ZAR**
- 7d: **+66.60 ZAR** | 30d: **+1.17 ZAR**

## 2b. Claimed vs realised

- Book: 93 slices (native 73 | hip3 20); validated pools: native 195 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 93 book slices present in the validated pools): +0.318% | at 147.44 ZAR mean notional/trade: +0.47 ZAR/trade
- Realised (578 real closes per lane_gate._is_real_close, net of fees): +0.61 ZAR/trade | sd 4.70 | SE 0.20
- Gap: +0.14 ZAR/trade | t = +0.70 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.359% over 73/73 slices (pool 195) ~ +0.52 ZAR | realised 532 closes +0.74 ZAR sd 4.67 SE 0.20 | gap +0.22 t +1.08 | NOT ESTABLISHED
- hip3: claimed median +0.062% over 20/20 slices (pool 160) ~ +0.10 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.07 t -1.51 | NOT ESTABLISHED
- Ledger: 694 decision rows; 578 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 116 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 532 | wins: 269 | win%: 50.6 | P&L: **+394.96 ZAR** | today: -4.44 | 7d: +66.60 | 30d: +1.17
- By exit: target +516.3, trail_stop +212.4, horizon +79.0, max_bars +2.8, regime_shift -11.9, stop -403.6
- By entry regime (n/pnl): neutral 213/+234.4, bull 121/+199.5, bear 198/-38.9
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_trend_neutral:0:SHORT:h24 5n/5w +24.80; feat_premium@oi_hi:2:SHORT:h24 3n/3w +24.15; feat_ext_strength:2:LONG:h15 12n/8w +24.00
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_macd_12_26:2:SHORT:h15 3n/0w -11.55; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; ENAUSDC 7n +23.48; XRPZAR 2n +18.07; SOLUSDC 65n +17.29
- Worst pairs: UNIUSDC 13n -30.75; ZECUSDC 17n -21.96; ETHZAR 4n -14.36; DOGEUSDC 15n -11.90; HYPEUSDC 39n -9.14

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 5 open, stop-risk **18.62 ZAR**
  - AVAXUSDC SELL ntl=120 risk=4.34 bars=7 stop=8.901874999999999530 peak=8.7225
  - SOLUSDC SELL ntl=120 risk=4.00 bars=1 stop=86.84325000000000470 peak=85.383
  - XRPUSDC SELL ntl=120 risk=3.68 bars=6 stop=1.0916000000000000325 peak=1.0791
  - BTCUSDC SELL ntl=120 risk=3.67 bars=14 stop=76024.49999999999985 peak=74478.0
  - ETHUSDC SELL ntl=120 risk=2.94 bars=5 stop=2109.9999999999997145 peak=2090.0

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **18.62 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **18.62 / 167.68 ZAR | 12.0% | ok**
- Remaining: 147.5593 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 140, "skipped": 140, "slice_full": 0, "slot_full": 0}, "native": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 42, "signals": 157, "skipped": 115, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **AVAXUSDC** 4.3411 ZAR
- positions without bars: 0 | replayed: 5 | invalid: 0

## 6. Monitored books

- Native: 73 | HIP-3: 20
- Native top (by paper P&L):
  - `feat_ret_autocorr:2:SHORT:h24` edge=0.0070 n=9815 p=0.2044 src=validated_walk_forward unproven=False paper=5n/+8.20
  - `feat_funding_cum_24:2:SHORT:h20` edge=0.0068 n=4722 p=0.2175 src=validated_walk_forward unproven=False paper=5n/+5.47
  - `feat_donchian_break:2:SHORT:h24` edge=0.0073 n=9628 p=0.5217 src=validated_walk_forward unproven=False paper=2n/+3.68
  - `feat_vol_sma_ratio:1:SHORT:h24` edge=0.0033 n=9540 p=0.6952 src=validated_walk_forward unproven=False paper=1n/+3.25
  - `feat_rsi_21:2:SHORT:h24` edge=0.0080 n=9069 p=0.3432 src=validated_walk_forward unproven=False paper=2n/+1.17
  - `feat_book_imb_5:1:SHORT:h24` edge=0.0056 n=3922 p=0.8251 src=validated_walk_forward unproven=False paper=2n/+1.10
  - `feat_overnight_ret:0:SHORT:h24` edge=0.0036 n=11529 p=0.4924 src=validated_walk_forward unproven=False paper=1n/+1.06
  - `feat_ext_strength:2:SHORT:h24` edge=0.0076 n=10243 p=0.2881 src=validated_walk_forward unproven=False paper=2n/+0.89
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

- Latest research: 2026-11-11T01:10:48.911917+00:00 | discovered 2240 | validated 195 | reg-confounded 966 | hostile-unproven 4
- floors: "" | book: {"rows": 80, "by_status": {"decayed": 6, "monitored": 74}, "in_validated_pool": 80, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=1120 validated=1120 passing=195 eligible=229 best=375.1b best_fail=breadth_ok
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=576 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_atr_norm_ext:L2S0:h15: mean=-3.7b t_no=1.84 folds=01011 mkt_corr=-0.21 dd=429b legs=11.4/10.7 fail=n_nonoverlap,mean<=0,t_nonoverlap,folds
  - feat_ret_3:L0S2:h24: mean=-7.5b t_no=1.68 folds=01001 mkt_corr=-0.06 dd=218b legs=10.8/11.8 fail=n_nonoverlap,mean<=0,t_nonoverlap,folds
  - feat_intraday_mom:L0S2:h12: mean=-6.0b t_no=1.58 folds=01100 mkt_corr=-0.14 dd=204b legs=11.9/12.2 fail=mean<=0,t_nonoverlap,folds
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

- Label: **neutral** | breadth bear=0.4 bull=0.0667 neutral=0.5333 | symbols=15
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 0 / bull 0
- as_of: 2026-11-11T16:01:20Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 1120 | eligible: 625 | observations: 3206 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
  - `feat_funding_rate@oi_lo:2:SHORT:h24` edge=375.1b n=184 breadth=4 validated=True prov=False armable=False (too_few_rows)
  - `feat_funding_rate@oi_lo:2:SHORT:h20` edge=276.8b n=189 breadth=4 validated=True prov=False armable=False (too_few_rows)
  - `feat_funding_rate@oi_lo:2:SHORT:h15` edge=204.0b n=189 breadth=4 validated=False prov=False armable=False (too_few_rows)
  - `feat_funding_cum_24@oi_lo:2:SHORT:h24` edge=141.9b n=1663 breadth=10 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_funding_rate@oi_lo:2:SHORT:h12` edge=140.0b n=189 breadth=4 validated=False prov=False armable=False (too_few_rows)
  - `feat_oi_ret_div@oi_lo:0:SHORT:h24` edge=129.8b n=1166 breadth=13 validated=False prov=False armable=False (not_confirmed_bear)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+45.00 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **73/73** | hip3 **19/20**
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

- Latest scan 2026-11-11T17:09:54: errors=0 signals=297 regime_blocked=200
- this cycle: closed=0 new_signals=297 skipped=255 slot_full=0 slice_full=0 pair_held=42
- Action funnel: regime_blocked=200 | lane_gate_blocked=1 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=42 | cluster_cap=0 | family_vetoed=10 | slot_full=0 | skipped=255
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "cluster_cap": 0, "family_vetoed": 10, "lane_gate_blocked": 1, "pair_held": 42, "regime_blocked": 200, "skipped": 255, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=48
- aggregate_risk: ok open=18.6226 cap=167.6796 used=0.1200 remaining=147.5593 replayed=5 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
