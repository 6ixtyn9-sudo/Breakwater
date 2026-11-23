# Breakwater daily print — 2026-11-23 14:38 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **383.73 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2422.42 ZAR** (seed 2000) | lifetime: **+422.42 ZAR** | closed: 627
- Today: 11 closed, **-33.46 ZAR**
- 7d: **+29.59 ZAR** | 30d: **+145.27 ZAR**

## 2b. Claimed vs realised

- Book: 28 slices (native 8 | hip3 20); validated pools: native 265 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 28 book slices present in the validated pools): +0.090% | at 145.69 ZAR mean notional/trade: +0.13 ZAR/trade
- Realised (627 real closes per lane_gate._is_real_close, net of fees): +0.67 ZAR/trade | sd 4.78 | SE 0.19
- Gap: +0.54 ZAR/trade | t = +2.84 (one-sample t of realised mean vs the claimed constant) | verdict: EXCEEDS
- native: claimed median +1.298% over 8/8 slices (pool 265) ~ +1.87 ZAR | realised 581 closes +0.80 ZAR sd 4.76 SE 0.20 | gap -1.06 t -5.39 | FALLS SHORT
- hip3: claimed median +0.062% over 20/20 slices (pool 160) ~ +0.10 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.07 t -1.51 | NOT ESTABLISHED
- Ledger: 757 decision rows; 627 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 130 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 581 | wins: 295 | win%: 50.8 | P&L: **+466.92 ZAR** | today: -33.46 | 7d: +29.59 | 30d: +145.27
- By exit: target +516.3, trail_stop +336.5, horizon +72.9, max_bars +2.8, regime_shift -11.9, stop -449.5
- By entry regime (n/pnl): neutral 235/+250.6, bull 122/+199.3, bear 224/+17.1
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_adx_14:1:SHORT:h20 4n/4w +53.91; feat_overnight_ret:1:SHORT:h24 2n/2w +26.35; feat_trend_neutral:0:SHORT:h24 5n/5w +24.80
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_funding_cum_24:0:SHORT:h24 5n/1w -16.09; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_macd_12_26:2:SHORT:h15 3n/0w -11.55; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; BTCUSDC 70n +25.20; ENAUSDC 7n +23.48; SOLUSDC 70n +22.00
- Worst pairs: ZECUSDC 17n -21.96; UNIUSDC 15n -17.05; DOGEUSDC 20n -16.39; ETHZAR 4n -14.36; LTCUSDC 2n -6.24

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 1 open, stop-risk **4.63 ZAR**
  - BTCUSDC SELL ntl=123 risk=4.63 bars=0 stop=66223.50000000000005 peak=63832.0

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **4.63 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **4.63 / 172.88 ZAR | 2.9% | ok**
- Remaining: 167.9412 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 30, "skipped": 30, "slice_full": 0, "slot_full": 0}, "native": {"cluster_cap": 9, "lane_gate_blocked": 0, "opened": 1, "pair_held": 1, "signals": 32, "skipped": 21, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **BTCUSDC** 4.6264 ZAR
- positions without bars: 0 | replayed: 8 | invalid: 0

## 6. Monitored books

- Native: 8 | HIP-3: 20
- Native top (by paper P&L):
  - `feat_oi_chg_24:2:SHORT:h20` edge=0.0167 n=4777 p=0.0422 src=validated_walk_forward unproven=False paper=1n/+2.26
  - `feat_bb_width_20:2:SHORT:h24` edge=0.0079 n=9806 p=0.1312 src=validated_walk_forward unproven=False paper=1n/+1.24
  - `feat_oi_chg_24:2:SHORT:h24` edge=0.0172 n=5180 p=0.0716 src=validated_walk_forward unproven=False paper=2n/+1.03
  - `feat_oi_chg_24@oi_mid:2:SHORT:h15` edge=0.0148 n=1453 p=0.1343 src=validated_walk_forward unproven=False paper=1n/+0.63
  - `feat_oi_chg_24@oi_mid:2:SHORT:h20` edge=0.0173 n=1529 p=0.0690 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_oi_ret_div@oi_lo:0:SHORT:h24` edge=0.0187 n=2299 p=0.6069 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vol_contraction:2:SHORT:h24` edge=0.0046 n=8494 p=0.3456 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_trend_strength_20:2:SHORT:h24` edge=0.0055 n=8970 p=0.4026 src=validated_walk_forward unproven=False paper=4n/-5.00
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

- Latest research: 2026-11-23T00:30:46.911464+00:00 | discovered 2240 | validated 265 | reg-confounded 874 | hostile-unproven 20
- floors: "" | book: {"rows": 12, "by_status": {"monitored": 12}, "in_validated_pool": 12, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=1120 validated=1120 passing=264 eligible=817 best=205.8b best_fail=direction_ok,regime_confounded
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=576 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_vol_regime:L0S2:h24: mean=+16.5b t_no=2.26 folds=10011 mkt_corr=-0.68 dd=59b legs=9.2/9.7 fail=n_nonoverlap,folds,market_corr
  - feat_vol_contraction:L0S2:h24: mean=+16.5b t_no=2.26 folds=10011 mkt_corr=-0.68 dd=59b legs=9.2/9.7 fail=n_nonoverlap,folds,market_corr
  - feat_bb_width_20:L0S2:h15: mean=+11.1b t_no=1.96 folds=10011 mkt_corr=-0.54 dd=217b legs=14.2/9.3 fail=t_nonoverlap,folds,market_corr
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

- Label: **neutral** | breadth bear=0.0667 bull=0.1333 neutral=0.8 | symbols=15
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 0 / bull 0
- as_of: 2026-11-23T14:35:29Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 1120 | eligible: 1056 | observations: 5435 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
  - `feat_oi_chg_24@oi_mid:2:SHORT:h24` edge=205.8b n=1668 breadth=13 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_oi_ret_div@oi_lo:0:SHORT:h24` edge=186.9b n=2299 breadth=13 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_oi_chg_24@oi_lo:2:SHORT:h24` edge=175.5b n=2002 breadth=13 validated=False prov=False armable=False (regime_confounded)
  - `feat_oi_chg_24@oi_mid:2:SHORT:h20` edge=172.6b n=1529 breadth=12 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_oi_chg_24:2:SHORT:h24` edge=172.2b n=5180 breadth=38 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_oi_chg_24@oi_lo:1:SHORT:h24` edge=170.1b n=2136 breadth=13 validated=False prov=False armable=False (not_confirmed_bear)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+26.00 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **7/8** | hip3 **19/20**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 52
  - `feat_adx_14:2:LONG:h12` slice_pnl=-1.83
  - `feat_adx_14:2:LONG:h15` slice_pnl=-3.92
  - `feat_atr_norm_ext:2:LONG:h13` slice_pnl=-4.88
  - `feat_atr_percent:2:LONG:h12` slice_pnl=-1.44
  - `feat_atr_ratio:0:LONG:h24` slice_pnl=-10.03
  - `feat_bb_squeeze_20:2:LONG:h20` slice_pnl=-10.15
  - `feat_bb_width_20:2:LONG:h15` slice_pnl=-6.62
  - `feat_book_imb_5@oi_hi:1:SHORT:h20` slice_pnl=-3.93
  - `feat_buy_vol_ratio:2:LONG:h24` slice_pnl=-6.57
  - `feat_cci_20:0:LONG:h24` slice_pnl=-17.74
  - `feat_cci_20:2:SHORT:h24` slice_pnl=-7.35
  - `feat_donchian_break:2:LONG:h15` slice_pnl=-2.57
  - `feat_ema_cross_10_20:2:LONG:h12` slice_pnl=-3.12
  - `feat_ema_cross_10_20:2:SHORT:h24` slice_pnl=-5.49
  - `feat_ext_vs_ma_50:0:LONG:h20` slice_pnl=-11.21
  - `feat_funding_cum_24:0:SHORT:h24` slice_pnl=-16.09
  - `feat_funding_cum_24:2:SHORT:h12` slice_pnl=-1.14
  - `feat_funding_rate:2:SHORT:h12` slice_pnl=-7.96
  - `feat_hour_utc:2:LONG:h15` slice_pnl=-1.61
  - `feat_kc_width:2:LONG:h12` slice_pnl=-6.60
  - `feat_kc_width:2:LONG:h15` slice_pnl=-0.19
  - `feat_macd_12_26:2:SHORT:h15` slice_pnl=-11.55
  - `feat_oi_ret_div@oi_hi:2:SHORT:h24` slice_pnl=-1.60
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
  - `feat_trend_strength_20:2:SHORT:h24` slice_pnl=-5.00
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

- Latest scan 2026-11-23T14:07:12: errors=0 signals=62 regime_blocked=256
- this cycle: closed=8 new_signals=62 skipped=51 slot_full=0 slice_full=0 pair_held=1
- Action funnel: regime_blocked=256 | lane_gate_blocked=2 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=1 | cluster_cap=9 | family_vetoed=13 | slot_full=0 | skipped=51
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "cluster_cap": 9, "family_vetoed": 13, "lane_gate_blocked": 2, "pair_held": 1, "regime_blocked": 256, "skipped": 51, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=51
- aggregate_risk: ok open=0.0000 cap=172.8762 used=0.0285 remaining=167.9412 replayed=8 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
