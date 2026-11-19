# Breakwater daily print — 2026-11-19 11:38 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **376.43 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2385.25 ZAR** (seed 2000) | lifetime: **+385.25 ZAR** | closed: 604
- Today: 2 closed, **+1.15 ZAR**
- 7d: **+34.23 ZAR** | 30d: **+98.29 ZAR**

## 2b. Claimed vs realised

- Book: 55 slices (native 35 | hip3 20); validated pools: native 201 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 55 book slices present in the validated pools): +0.414% | at 146.50 ZAR mean notional/trade: +0.61 ZAR/trade
- Realised (604 real closes per lane_gate._is_real_close, net of fees): +0.64 ZAR/trade | sd 4.64 | SE 0.19
- Gap: +0.03 ZAR/trade | t = +0.16 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.493% over 35/35 slices (pool 201) ~ +0.71 ZAR | realised 558 closes +0.77 ZAR sd 4.61 SE 0.20 | gap +0.06 t +0.29 | NOT ESTABLISHED
- hip3: claimed median +0.062% over 20/20 slices (pool 160) ~ +0.10 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.07 t -1.51 | NOT ESTABLISHED
- Ledger: 730 decision rows; 604 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 126 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 558 | wins: 286 | win%: 51.3 | P&L: **+429.76 ZAR** | today: +1.15 | 7d: +34.23 | 30d: +98.29
- By exit: target +516.3, trail_stop +254.0, horizon +80.0, max_bars +2.8, regime_shift -11.9, stop -411.3
- By entry regime (n/pnl): neutral 217/+231.4, bull 122/+199.3, bear 219/-0.9
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_trend_neutral:0:SHORT:h24 5n/5w +24.80; feat_premium@oi_hi:2:SHORT:h24 3n/3w +24.15; feat_ext_strength:2:LONG:h15 12n/8w +24.00
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_macd_12_26:2:SHORT:h15 3n/0w -11.55; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; ENAUSDC 7n +23.48; BTCUSDC 67n +18.74; XRPZAR 2n +18.07
- Worst pairs: UNIUSDC 13n -30.75; ZECUSDC 17n -21.96; ETHZAR 4n -14.36; DOGEUSDC 18n -12.37; LTCUSDC 2n -6.24

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 4 open, stop-risk **17.30 ZAR**
  - UNIUSDC SELL ntl=122 risk=4.84 bars=1 stop=5.425850000000000165 peak=5.2255
  - ETHUSDC SELL ntl=122 risk=4.54 bars=17 stop=1833.4749999999999425 peak=1812.4
  - SOLUSDC SELL ntl=122 risk=4.04 bars=2 stop=76.99074999999999535 peak=74.777
  - XRPUSDC SELL ntl=122 risk=3.88 bars=0 stop=1.0129824999999999715 peak=0.98172

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **17.30 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **17.30 / 170.57 ZAR | 10.8% | ok**
- Remaining: 152.0568 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 18, "skipped": 18, "slice_full": 0, "slot_full": 0}, "native": {"cluster_cap": 34, "lane_gate_blocked": 0, "opened": 1, "pair_held": 18, "signals": 61, "skipped": 8, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **UNIUSDC** 4.8410 ZAR
- positions without bars: 0 | replayed: 3 | invalid: 0

## 6. Monitored books

- Native: 35 | HIP-3: 20
- Native top (by paper P&L):
  - `feat_ret_autocorr:2:SHORT:h20` edge=0.0085 n=9253 p=0.1117 src=validated_walk_forward unproven=False paper=4n/+15.53
  - `feat_vol_regime:2:SHORT:h24` edge=0.0042 n=8920 p=0.1918 src=validated_walk_forward unproven=False paper=2n/+3.02
  - `feat_oi_chg_24@oi_hi:2:SHORT:h12` edge=0.0078 n=1465 p=0.3817 src=validated_walk_forward unproven=False paper=1n/+1.67
  - `feat_oi_chg_24@oi_hi:2:SHORT:h24` edge=0.0158 n=1069 p=0.3938 src=validated_walk_forward unproven=False paper=1n/+1.58
  - `feat_bb_width_20:2:SHORT:h24` edge=0.0054 n=9574 p=0.1461 src=validated_walk_forward unproven=False paper=1n/+1.24
  - `feat_oi_chg_24:2:SHORT:h24` edge=0.0165 n=4090 p=0.2619 src=validated_walk_forward unproven=False paper=2n/+1.03
  - `feat_oi_chg_24@oi_mid:2:SHORT:h12` edge=0.0102 n=1491 p=0.2480 src=validated_walk_forward unproven=False paper=1n/+0.85
  - `feat_close_pos_ma:1:SHORT:h24` edge=0.0069 n=10359 p=0.4317 src=validated_walk_forward unproven=False paper=1n/+0.54
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

- Latest research: 2026-11-19T00:31:53.257836+00:00 | discovered 2240 | validated 201 | reg-confounded 1042 | hostile-unproven 8
- floors: "" | book: {"rows": 39, "by_status": {"decayed": 4, "monitored": 35}, "in_validated_pool": 39, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=1120 validated=1120 passing=201 eligible=525 best=176.3b best_fail=direction_ok,regime_confounded
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=576 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_vol_regime:L0S2:h15: mean=+30.2b t_no=2.06 folds=10011 mkt_corr=-0.64 dd=84b legs=9.9/8.6 fail=n_nonoverlap,folds,market_corr
  - feat_vol_contraction:L0S2:h15: mean=+30.2b t_no=2.06 folds=10011 mkt_corr=-0.64 dd=84b legs=9.9/8.6 fail=n_nonoverlap,folds,market_corr
  - feat_vol_regime:L0S2:h12: mean=+27.8b t_no=2.02 folds=10011 mkt_corr=-0.63 dd=93b legs=9.8/8.5 fail=n_nonoverlap,folds,market_corr
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

- Label: **neutral** | breadth bear=0.3333 bull=0.1333 neutral=0.5333 | symbols=15
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 0 / bull 0
- as_of: 2026-11-19T11:35:25Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 1120 | eligible: 885 | observations: 5205 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
  - `feat_oi_chg_24@oi_mid:2:SHORT:h24` edge=176.3b n=1404 breadth=13 validated=False prov=False armable=False (regime_confounded)
  - `feat_oi_chg_24:2:SHORT:h24` edge=151.3b n=4747 breadth=40 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_oi_chg_24@oi_mid:2:SHORT:h20` edge=147.7b n=1428 breadth=13 validated=False prov=False armable=False (regime_confounded)
  - `feat_oi_chg_24@oi_lo:2:SHORT:h24` edge=143.1b n=1923 breadth=14 validated=False prov=False armable=False (regime_confounded)
  - `feat_oi_chg_24@oi_hi:2:SHORT:h24` edge=137.8b n=1420 breadth=13 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_oi_chg_24:2:SHORT:h20` edge=131.0b n=4635 breadth=39 validated=True prov=False armable=False (not_confirmed_bear)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+24.26 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **35/35** | hip3 **19/20**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 49
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

- Latest scan 2026-11-19T11:03:52: errors=0 signals=79 regime_blocked=226
- this cycle: closed=0 new_signals=79 skipped=26 slot_full=0 slice_full=0 pair_held=18
- Action funnel: regime_blocked=226 | lane_gate_blocked=1 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=18 | cluster_cap=34 | family_vetoed=0 | slot_full=0 | skipped=26
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "cluster_cap": 34, "family_vetoed": 0, "lane_gate_blocked": 1, "pair_held": 18, "regime_blocked": 226, "skipped": 26, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=49
- aggregate_risk: ok open=13.4169 cap=170.5717 used=0.1085 remaining=152.0568 replayed=3 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
