# Breakwater daily print — 2026-11-06 09:56 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **396.98 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2278.53 ZAR** (seed 2000) | lifetime: **+278.53 ZAR** | closed: 546
- Today: 0 closed, **+0.00 ZAR**
- 7d: **+9.38 ZAR** | 30d: **-108.76 ZAR**

## 2b. Claimed vs realised

- Book: 102 slices (native 81 | hip3 21); validated pools: native 239 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 102 book slices present in the validated pools): +0.266% | at 149.19 ZAR mean notional/trade: +0.40 ZAR/trade
- Realised (546 real closes per lane_gate._is_real_close, net of fees): +0.51 ZAR/trade | sd 4.73 | SE 0.20
- Gap: +0.11 ZAR/trade | t = +0.56 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.289% over 81/81 slices (pool 239) ~ +0.43 ZAR | realised 500 closes +0.65 ZAR sd 4.71 SE 0.21 | gap +0.22 t +1.04 | NOT ESTABLISHED
- hip3: claimed median +0.065% over 21/21 slices (pool 160) ~ +0.11 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.08 t -1.52 | NOT ESTABLISHED
- Ledger: 657 decision rows; 546 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 111 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 500 | wins: 244 | win%: 48.8 | P&L: **+323.04 ZAR** | today: +0.00 | 7d: +9.38 | 30d: -108.76
- By exit: target +516.3, trail_stop +137.9, horizon +71.4, max_bars +2.8, regime_shift -11.9, stop -393.5
- By entry regime (n/pnl): neutral 206/+233.4, bull 120/+187.5, bear 174/-97.9
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_premium:2:SHORT:h24 5n/4w +20.06; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_macd_12_26:2:SHORT:h15 3n/0w -11.55; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPZAR 2n +18.07; ENAUSDC 6n +13.54; AAVEUSDC 4n +10.89
- Worst pairs: UNIUSDC 11n -29.94; ZECUSDC 17n -21.96; HYPEUSDC 37n -18.30; ETHUSDC 66n -16.63; XRPUSDC 54n -14.88

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 5 open, stop-risk **7.93 ZAR**
  - ETHUSDC SELL ntl=116 risk=4.63 bars=14 stop=2355.6999999999997790 peak=2268.8
  - BTCUSDC SELL ntl=116 risk=3.30 bars=15 stop=78213.25000000000005 peak=77036.0
  - SOLUSDC SELL ntl=116 risk=0.00 bars=22 stop=91.35049999999999950 peak=96.941
  - HYPEUSDC SELL ntl=116 risk=0.00 bars=21 stop=79.093249999999998850 peak=83.556
  - XRPUSDC SELL ntl=116 risk=0.00 bars=19 stop=1.21862499999999996950 peak=1.3192

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **7.93 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **7.93 / 162.21 ZAR | 5.8% | ok**
- Remaining: 152.8373 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 32, "skipped": 32, "slice_full": 0, "slot_full": 0}, "native": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 1, "signals": 3, "skipped": 2, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **ETHUSDC** 4.6290 ZAR
- positions without bars: 0 | replayed: 5 | invalid: 0

## 6. Monitored books

- Native: 81 | HIP-3: 21
- Native top (by paper P&L):
  - `feat_premium@oi_hi:2:SHORT:h24` edge=0.0056 n=2224 p=0.0146 src=validated_walk_forward unproven=False paper=1n/+6.23
  - `feat_stoch_k_14:1:SHORT:h15` edge=0.0022 n=9426 p=0.2494 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_stoch_d_14:1:SHORT:h15` edge=0.0018 n=8816 p=0.3766 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_donchian_break:1:SHORT:h15` edge=0.0028 n=9165 p=0.2236 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_williams_r_14:1:SHORT:h15` edge=0.0022 n=9419 p=0.2577 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_range_pos_20:1:SHORT:h15` edge=0.0027 n=9272 p=0.3014 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_range_pos_50:2:SHORT:h12` edge=0.0032 n=10155 p=0.7783 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_1:2:SHORT:h15` edge=0.0024 n=9632 p=0.3744 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Latest research: 2026-11-06T00:30:14.504476+00:00 | discovered 2240 | validated 239 | reg-confounded 779 | hostile-unproven 10
- floors: "" | book: {"rows": 87, "by_status": {"decayed": 5, "monitored": 81, "cooldown": 1}, "in_validated_pool": 87, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=1120 validated=1120 passing=239 eligible=174 best=318.8b best_fail=temporal_pass
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=576 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_vwap_upper_dist:L2S0:h24: mean=-0.2b t_no=2.66 folds=00011 mkt_corr=-0.33 dd=120b legs=10.5/10.5 fail=n_nonoverlap,mean<=0,folds,market_corr
  - feat_ret_autocorr:L2S0:h24: mean=-9.0b t_no=2.25 folds=01100 mkt_corr=-0.01 dd=116b legs=12.7/11.8 fail=n_nonoverlap,mean<=0,folds
  - feat_keltner_pos:L2S0:h15: mean=-3.6b t_no=2.24 folds=01101 mkt_corr=-0.29 dd=262b legs=11.4/11.9 fail=n_nonoverlap,mean<=0,folds
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
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bull | consecutive_bear: 0 / bull 0
- as_of: 2026-11-06T08:27:09Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 1120 | eligible: 604 | observations: 2733 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
  - `feat_funding_rate@oi_mid:2:SHORT:h24` edge=318.8b n=389 breadth=7 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_funding_rate@oi_mid:2:SHORT:h20` edge=269.2b n=394 breadth=7 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_funding_rate@oi_lo:2:SHORT:h24` edge=262.3b n=242 breadth=5 validated=False prov=False armable=False (not_confirmed_bear)
  - `feat_funding_rate@oi_lo:2:SHORT:h20` edge=196.1b n=231 breadth=4 validated=False prov=False armable=False (not_confirmed_bear)
  - `feat_funding_rate@oi_mid:2:SHORT:h15` edge=196.0b n=411 breadth=8 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_funding_cum_24@oi_mid:2:SHORT:h24` edge=180.3b n=1323 breadth=10 validated=True prov=False armable=False (not_confirmed_bear)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+24.67 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **80/81** | hip3 **19/21**
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

- Latest scan 2026-11-06T08:25:29: errors=0 signals=35 regime_blocked=87
- this cycle: closed=0 new_signals=35 skipped=34 slot_full=0 slice_full=0 pair_held=1
- Action funnel: regime_blocked=87 | lane_gate_blocked=3 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=1 | cluster_cap=0 | family_vetoed=0 | slot_full=0 | skipped=34
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "cluster_cap": 0, "family_vetoed": 0, "lane_gate_blocked": 3, "pair_held": 1, "regime_blocked": 87, "skipped": 34, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=48
- aggregate_risk: ok open=7.9252 cap=162.2076 used=0.0578 remaining=152.8373 replayed=5 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
