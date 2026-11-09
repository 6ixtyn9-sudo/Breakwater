# Breakwater daily print — 2026-11-09 18:51 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **391.13 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2348.97 ZAR** (seed 2000) | lifetime: **+348.97 ZAR** | closed: 570
- Today: 10 closed, **+42.98 ZAR**
- 7d: **+89.34 ZAR** | 30d: **+5.15 ZAR**

## 2b. Claimed vs realised

- Book: 91 slices (native 71 | hip3 20); validated pools: native 217 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 91 book slices present in the validated pools): +0.282% | at 147.83 ZAR mean notional/trade: +0.42 ZAR/trade
- Realised (570 real closes per lane_gate._is_real_close, net of fees): +0.61 ZAR/trade | sd 4.72 | SE 0.20
- Gap: +0.20 ZAR/trade | t = +0.99 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.322% over 71/71 slices (pool 217) ~ +0.47 ZAR | realised 524 closes +0.75 ZAR sd 4.70 SE 0.21 | gap +0.28 t +1.37 | NOT ESTABLISHED
- hip3: claimed median +0.062% over 20/20 slices (pool 160) ~ +0.10 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.07 t -1.51 | NOT ESTABLISHED
- Ledger: 685 decision rows; 570 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 115 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 524 | wins: 263 | win%: 50.2 | P&L: **+393.48 ZAR** | today: +42.98 | 7d: +89.34 | 30d: +5.15
- By exit: target +516.3, trail_stop +209.0, horizon +76.4, max_bars +2.8, regime_shift -11.9, stop -399.0
- By entry regime (n/pnl): neutral 211/+238.6, bull 121/+199.5, bear 192/-44.7
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_trend_neutral:0:SHORT:h24 5n/5w +24.80; feat_premium@oi_hi:2:SHORT:h24 3n/3w +24.15; feat_ext_strength:2:LONG:h15 12n/8w +24.00
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_macd_12_26:2:SHORT:h15 3n/0w -11.55; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; ENAUSDC 7n +23.48; XRPZAR 2n +18.07; SOLUSDC 63n +13.67
- Worst pairs: UNIUSDC 13n -30.75; ZECUSDC 17n -21.96; ETHZAR 4n -14.36; DOGEUSDC 15n -11.90; ETHUSDC 69n -9.72

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 3 open, stop-risk **11.50 ZAR**
  - SOLUSDC SELL ntl=120 risk=4.71 bars=2 stop=90.1402499999999945 peak=87.987
  - ETHUSDC SELL ntl=120 risk=4.26 bars=0 stop=2223.475000000000040 peak=2146.9
  - BTCUSDC SELL ntl=120 risk=2.53 bars=16 stop=76405.49999999999995 peak=75585.0

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **11.50 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **11.50 / 167.36 ZAR | 7.4% | ok**
- Remaining: 154.9596 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 213, "skipped": 213, "slice_full": 0, "slot_full": 0}, "native": {"cluster_cap": 86, "lane_gate_blocked": 0, "opened": 1, "pair_held": 28, "signals": 242, "skipped": 127, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **SOLUSDC** 4.7091 ZAR
- positions without bars: 0 | replayed: 2 | invalid: 0

## 6. Monitored books

- Native: 71 | HIP-3: 20
- Native top (by paper P&L):
  - `feat_trend_neutral:0:SHORT:h24` edge=0.0041 n=16524 p=0.1142 src=validated_walk_forward unproven=False paper=5n/+24.80
  - `feat_premium@oi_hi:2:SHORT:h24` edge=0.0066 n=2350 p=0.2950 src=validated_walk_forward unproven=False paper=3n/+24.15
  - `feat_ret_autocorr:2:SHORT:h24` edge=0.0059 n=9596 p=0.4942 src=validated_walk_forward unproven=False paper=4n/+4.68
  - `feat_vol_trend:2:SHORT:h20` edge=0.0067 n=10628 p=0.4735 src=validated_walk_forward unproven=False paper=2n/+1.61
  - `feat_rsi_21:2:SHORT:h24` edge=0.0090 n=8253 p=0.3607 src=validated_walk_forward unproven=False paper=2n/+1.17
  - `feat_bb_squeeze_20:2:SHORT:h24` edge=0.0053 n=10339 p=0.3363 src=validated_walk_forward unproven=False paper=1n/+1.16
  - `feat_oi_ret_div:2:SHORT:h24` edge=0.0024 n=2881 p=0.2230 src=validated_walk_forward unproven=False paper=2n/+0.30
  - `feat_ret_1:2:SHORT:h24` edge=0.0040 n=9013 p=0.3535 src=validated_walk_forward unproven=False paper=1n/+0.03
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

- Latest research: 2026-11-09T00:31:53.253035+00:00 | discovered 2240 | validated 217 | reg-confounded 649 | hostile-unproven 6
- floors: "" | book: {"rows": 77, "by_status": {"monitored": 71, "decayed": 5, "cooldown": 1}, "in_validated_pool": 77, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=1120 validated=1120 passing=217 eligible=219 best=371.5b best_fail=direction_ok,alpha<=0
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=576 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_macd_12_26:L0S2:h12: mean=+18.9b t_no=2.86 folds=11001 mkt_corr=-0.32 dd=144b legs=11.9/8.7 fail=folds,market_corr
  - feat_bb_width_20:L0S2:h20: mean=+17.3b t_no=2.26 folds=10101 mkt_corr=-0.34 dd=174b legs=15.6/8.5 fail=n_nonoverlap,folds,market_corr
  - feat_rsi_14:L2S0:h20: mean=-11.3b t_no=2.11 folds=00100 mkt_corr=-0.25 dd=155b legs=9.8/11.1 fail=n_nonoverlap,mean<=0,folds
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

- Label: **bear** | breadth bear=0.7333 bull=0.0667 neutral=0.2 | symbols=15
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 1 / bull 0
- as_of: 2026-11-09T17:35:30Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 1120 | eligible: 634 | observations: 3105 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
  - `feat_funding_rate@oi_lo:2:SHORT:h24` edge=371.5b n=206 breadth=5 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_funding_rate@oi_lo:2:SHORT:h20` edge=223.8b n=231 breadth=6 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_funding_rate@oi_lo:2:SHORT:h15` edge=209.3b n=206 breadth=5 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_oi_chg_24@oi_lo:2:SHORT:h20` edge=148.0b n=894 breadth=13 validated=False prov=False armable=False (not_confirmed_bear)
  - `feat_funding_rate:2:SHORT:h24` edge=140.9b n=946 breadth=18 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_funding_cum_24@oi_lo:2:SHORT:h24` edge=139.9b n=1213 breadth=12 validated=True prov=False armable=False (not_confirmed_bear)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+44.72 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **71/71** | hip3 **19/20**
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

- Latest scan 2026-11-09T16:54:45: errors=0 signals=455 regime_blocked=263
- this cycle: closed=0 new_signals=455 skipped=340 slot_full=0 slice_full=0 pair_held=28
- Action funnel: regime_blocked=263 | lane_gate_blocked=1 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=28 | cluster_cap=86 | family_vetoed=5 | slot_full=0 | skipped=340
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "cluster_cap": 86, "family_vetoed": 5, "lane_gate_blocked": 1, "pair_held": 28, "regime_blocked": 263, "skipped": 340, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=48
- aggregate_risk: ok open=7.2407 cap=167.3606 used=0.0741 remaining=154.9596 replayed=2 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
