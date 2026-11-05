# Breakwater daily print — 2026-11-05 00:31 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **427.84 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2272.30 ZAR** (seed 2000) | lifetime: **+272.30 ZAR** | closed: 545
- Today: 0 closed, **+0.00 ZAR**
- 7d: **+16.94 ZAR** | 30d: **-173.72 ZAR**

## 2b. Claimed vs realised

- Book: 84 slices (native 63 | hip3 21); validated pools: native 213 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 84 book slices present in the validated pools): +0.234% | at 149.25 ZAR mean notional/trade: +0.35 ZAR/trade
- Realised (545 real closes per lane_gate._is_real_close, net of fees): +0.50 ZAR/trade | sd 4.73 | SE 0.20
- Gap: +0.15 ZAR/trade | t = +0.74 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.264% over 63/63 slices (pool 213) ~ +0.39 ZAR | realised 499 closes +0.63 ZAR sd 4.71 SE 0.21 | gap +0.24 t +1.16 | NOT ESTABLISHED
- hip3: claimed median +0.065% over 21/21 slices (pool 160) ~ +0.11 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.08 t -1.52 | NOT ESTABLISHED
- Ledger: 653 decision rows; 545 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 108 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 499 | wins: 243 | win%: 48.7 | P&L: **+316.81 ZAR** | today: +0.00 | 7d: +16.94 | 30d: -173.72
- By exit: target +516.3, trail_stop +131.7, horizon +71.4, max_bars +2.8, regime_shift -11.9, stop -393.5
- By entry regime (n/pnl): neutral 206/+233.4, bull 119/+181.3, bear 174/-97.9
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_premium:2:SHORT:h24 5n/4w +20.06; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_macd_12_26:2:SHORT:h15 3n/0w -11.55; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPZAR 2n +18.07; ENAUSDC 6n +13.54; AAVEUSDC 4n +10.89
- Worst pairs: UNIUSDC 11n -29.94; ETHUSDC 65n -22.86; ZECUSDC 17n -21.96; HYPEUSDC 37n -18.30; XRPUSDC 54n -14.88

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 3 open, stop-risk **11.85 ZAR**
  - ETHUSDC SELL ntl=116 risk=4.51 bars=6 stop=2520.2250000000001095 peak=2444.0
  - XRPUSDC SELL ntl=116 risk=4.10 bars=8 stop=1.363699999999999875 peak=1.3422
  - BTCUSDC SELL ntl=116 risk=3.25 bars=5 stop=82641.25 peak=80923.0

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **11.85 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **11.85 / 161.71 ZAR | 7.9% | ok**
- Remaining: 148.9880 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 24, "skipped": 24, "slice_full": 0, "slot_full": 0}, "native": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 22, "signals": 204, "skipped": 182, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **ETHUSDC** 4.5059 ZAR
- positions without bars: 0 | replayed: 3 | invalid: 0

## 6. Monitored books

- Native: 63 | HIP-3: 21
- Native top (by paper P&L):
  - `feat_premium:2:SHORT:h24` edge=0.0076 n=4837 p=0.0149 src=validated_walk_forward unproven=False paper=5n/+20.06
  - `feat_macd_12_26:2:SHORT:h24` edge=0.0089 n=7971 p=0.0057 src=validated_walk_forward unproven=False paper=4n/+1.90
  - `feat_keltner_pos:2:SHORT:h12` edge=0.0029 n=9665 p=0.4312 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_3:2:SHORT:h12` edge=0.0022 n=9492 p=0.3272 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_10:2:SHORT:h20` edge=0.0042 n=9261 p=0.4099 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vol_trend:2:SHORT:h24` edge=0.0050 n=11144 p=0.3360 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_5:2:SHORT:h12` edge=0.0031 n=9593 p=0.1351 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_price_roc_5:2:SHORT:h12` edge=0.0031 n=9593 p=0.1351 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Latest research: 2026-11-04T00:55:52.431989+00:00 | discovered 2240 | validated 230 | reg-confounded 647 | hostile-unproven 2
- floors: "" | book: {"rows": 86, "by_status": {"monitored": 82, "decayed": 4}, "in_validated_pool": 86, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=1120 validated=1120 passing=230 eligible=150 best=273.7b best_fail=temporal_pass,regime_confounded
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=576 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_range_expansion:L0S2:h24: mean=-12.3b t_no=2.21 folds=01000 mkt_corr=-0.15 dd=202b legs=13.0/10.5 fail=n_nonoverlap,mean<=0,folds
  - feat_vwap_lower_dist:L0S2:h24: mean=+4.1b t_no=2.13 folds=01110 mkt_corr=-0.07 dd=99b legs=9.7/12.7 fail=n_nonoverlap,folds
  - feat_keltner_pos:L0S2:h15: mean=+1.5b t_no=1.97 folds=01000 mkt_corr=-0.24 dd=185b legs=12.0/10.9 fail=n_nonoverlap,t_nonoverlap,folds
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

- Label: **neutral** | breadth bear=0.1333 bull=0.3333 neutral=0.5333 | symbols=15
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 0 / bull 0
- as_of: 2026-11-04T23:01:18Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 1120 | eligible: 448 | observations: 2640 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
  - `feat_funding_rate@oi_mid:2:SHORT:h24` edge=273.7b n=501 breadth=9 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_funding_rate@oi_mid:2:SHORT:h20` edge=222.0b n=501 breadth=9 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_funding_cum_24@oi_mid:2:SHORT:h24` edge=171.7b n=1240 breadth=12 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_funding_rate:2:SHORT:h24` edge=153.4b n=1584 breadth=23 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_funding_rate@oi_lo:2:SHORT:h24` edge=148.4b n=537 breadth=7 validated=False prov=False armable=False (regime_confounded)
  - `feat_funding_rate@oi_mid:2:SHORT:h12` edge=146.3b n=501 breadth=9 validated=True prov=False armable=False (not_confirmed_bear)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+18.19 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **63/63** | hip3 **19/21**
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

- Latest scan 2026-11-05T00:07:42: errors=0 signals=228 regime_blocked=339
- this cycle: closed=0 new_signals=228 skipped=206 slot_full=0 slice_full=0 pair_held=22
- Action funnel: regime_blocked=339 | lane_gate_blocked=2 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=22 | cluster_cap=0 | family_vetoed=30 | slot_full=0 | skipped=206
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "cluster_cap": 0, "family_vetoed": 30, "lane_gate_blocked": 2, "pair_held": 22, "regime_blocked": 339, "skipped": 206, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=48
- aggregate_risk: ok open=11.8503 cap=161.7060 used=0.0786 remaining=148.9880 replayed=3 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
