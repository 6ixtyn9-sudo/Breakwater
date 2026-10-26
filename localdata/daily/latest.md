# Breakwater daily print — 2026-10-26 15:34 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **431.58 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2284.25 ZAR** (seed 2000) | lifetime: **+284.25 ZAR** | closed: 475
- Today: 4 closed, **+2.14 ZAR**
- 7d: **-2.72 ZAR** | 30d: **-200.13 ZAR**

## 2b. Claimed vs realised

- Book: 80 slices (native 60 | hip3 20); validated pools: native 180 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 80 book slices present in the validated pools): +0.207% | at 154.26 ZAR mean notional/trade: +0.32 ZAR/trade
- Realised (475 real closes per lane_gate._is_real_close, net of fees): +0.60 ZAR/trade | sd 4.95 | SE 0.23
- Gap: +0.28 ZAR/trade | t = +1.23 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.295% over 60/60 slices (pool 180) ~ +0.45 ZAR | realised 429 closes +0.77 ZAR sd 4.94 SE 0.24 | gap +0.32 t +1.33 | NOT ESTABLISHED
- hip3: claimed median +0.062% over 20/20 slices (pool 160) ~ +0.10 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.07 t -1.51 | NOT ESTABLISHED
- Ledger: 576 decision rows; 475 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 101 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 429 | wins: 208 | win%: 48.5 | P&L: **+328.75 ZAR** | today: +2.14 | 7d: -2.72 | 30d: -163.98
- By exit: target +516.3, trail_stop +84.5, horizon +70.2, max_bars +2.8, regime_shift -11.9, stop -333.1
- By entry regime (n/pnl): neutral 165/+224.4, bull 114/+183.9, bear 150/-79.6
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82; feat_range_pos_50:2:SHORT:h24 3n/0w -10.55
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPZAR 2n +18.07; XMRUSDC 5n +13.98; AAVEUSDC 3n +9.47
- Worst pairs: UNIUSDC 8n -25.10; ETHUSDC 55n -21.12; ZECUSDC 14n -18.75; XRPUSDC 45n -16.32; ETHZAR 4n -14.36

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: -36.16
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 8 open, stop-risk **22.26 ZAR**
  - UNIUSDC SELL ntl=116 risk=4.47 bars=18 stop=7.243525000000000135 peak=7.1195
  - HYPEUSDC SELL ntl=116 risk=4.11 bars=10 stop=78.46925000000000570 peak=78.156
  - XMRUSDC SELL ntl=116 risk=4.01 bars=5 stop=610.3999999999999920 peak=594.39
  - SOLUSDC SELL ntl=116 risk=3.70 bars=3 stop=104.9207500000000020 peak=102.12
  - XRPUSDC SELL ntl=116 risk=3.63 bars=2 stop=1.3382000000000000805 peak=1.3034
  - BTCUSDC SELL ntl=116 risk=2.34 bars=3 stop=82010.250000000000040 peak=80544.0
  - SUIUSDC SELL ntl=116 risk=0.00 bars=38 stop=0.93609999999999999750 peak=0.94051
  - ETHUSDC SELL ntl=116 risk=0.00 bars=27 stop=2337.45000000000013900 peak=2364.3

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **22.26 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **22.26 / 162.59 ZAR | 15.1% | ok**
- Remaining: 138.0110 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 95, "skipped": 95, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 85, "signals": 199, "skipped": 114, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **UNIUSDC** 4.4667 ZAR
- positions without bars: 0 | replayed: 8 | invalid: 0

## 6. Monitored books

- Native: 60 | HIP-3: 20
- Native top (by paper P&L):
  - `feat_premium:2:SHORT:h24` edge=0.0072 n=4456 p=0.2947 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_macd_12_26:2:SHORT:h20` edge=0.0081 n=7084 p=0.0285 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_funding_cum_24:2:SHORT:h12` edge=0.0054 n=2758 p=0.1354 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ema_cross_10_20:2:SHORT:h24` edge=0.0083 n=7019 p=0.0679 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vwap_dist:2:SHORT:h12` edge=0.0030 n=8059 p=0.2708 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vwap_upper_dist:2:SHORT:h24` edge=0.0055 n=7128 p=0.1666 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_time_since_low_20:2:SHORT:h15` edge=0.0054 n=989 p=0.8983 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_20:2:SHORT:h24` edge=0.0067 n=7100 p=0.2284 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Latest research: 2026-10-26T09:37:46.138526+00:00 | discovered 1744 | validated 180 | reg-confounded 700 | hostile-unproven 8
- floors: "" | book: {"rows": 62, "by_status": {"monitored": 60, "decayed": 2}, "in_validated_pool": 62, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=872 validated=872 passing=180 eligible=78 best=98.4b best_fail=regime_confounded
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=552 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_stoch_d_14:L0S2:h20: mean=+13.2b t_no=2.87 folds=10010 mkt_corr=+0.07 dd=207b legs=12.6/11.0 fail=n_nonoverlap,folds
  - feat_stoch_k_14:L0S2:h24: mean=+7.3b t_no=1.95 folds=10011 mkt_corr=+0.10 dd=172b legs=11.9/10.5 fail=n_nonoverlap,t_nonoverlap,folds
  - feat_stoch_d_14:L0S2:h24: mean=+14.5b t_no=1.94 folds=10010 mkt_corr=+0.10 dd=409b legs=12.5/11.0 fail=n_nonoverlap,t_nonoverlap,folds
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

- Label: **neutral** | breadth bear=0.2667 bull=0.1333 neutral=0.6 | symbols=15
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 0 / bull 0
- as_of: 2026-10-26T15:01:20Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 872 | eligible: 214 | observations: 1349 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
  - `feat_ext_vs_ma_50:2:SHORT:h24` edge=98.4b n=5726 breadth=40 validated=False prov=False armable=False (regime_confounded)
  - `feat_funding_cum_24:2:SHORT:h24` edge=93.4b n=2705 breadth=36 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_macd_12_26:2:SHORT:h24` edge=91.9b n=7064 breadth=40 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_funding_rate:2:SHORT:h24` edge=83.7b n=2057 breadth=28 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_funding_cum_24:2:SHORT:h20` edge=82.8b n=2778 breadth=37 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_ema_cross_10_20:2:SHORT:h24` edge=82.6b n=7019 breadth=40 validated=True prov=False armable=False (not_confirmed_bear)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+1.22 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **60/60** | hip3 **18/20**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 43
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
  - `feat_ext_vs_ma_50:0:LONG:h20` slice_pnl=-11.21
  - `feat_hour_utc:2:LONG:h15` slice_pnl=-1.61
  - `feat_kc_width:2:LONG:h12` slice_pnl=-6.60
  - `feat_kc_width:2:LONG:h15` slice_pnl=-0.19
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
  - `feat_vol_breakout:2:LONG:h15` slice_pnl=-6.39
  - `feat_vol_of_vol:1:LONG:h24` slice_pnl=-3.36
  - `feat_vol_of_vol:2:LONG:h12` slice_pnl=-1.49
  - `feat_vol_of_vol:2:LONG:h15` slice_pnl=-10.82
  - `feat_vol_sma_ratio:0:LONG:h24` slice_pnl=-2.20
  - `feat_vol_trend:0:LONG:h24` slice_pnl=-4.17
  - `feat_williams_r_14:0:SHORT:h24` slice_pnl=-1.65
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` lane_not_green
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-10-26T15:34:27: errors=0 signals=294 regime_blocked=149
- this cycle: closed=0 new_signals=294 skipped=209 slot_full=0 slice_full=0 pair_held=85
- Action funnel: regime_blocked=149 | lane_gate_blocked=2 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=85 | slot_full=0 | skipped=209
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 2, "pair_held": 85, "regime_blocked": 149, "skipped": 209, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=43
- aggregate_risk: ok open=22.2565 cap=162.5908 used=0.1512 remaining=138.0110 replayed=8 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
