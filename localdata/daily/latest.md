# Breakwater daily print — 2026-10-31 18:32 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **426.74 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2268.95 ZAR** (seed 2000) | lifetime: **+268.95 ZAR** | closed: 512
- Today: 2 closed, **-0.20 ZAR**
- 7d: **-8.19 ZAR** | 30d: **-151.16 ZAR**

## 2b. Claimed vs realised

- Book: 121 slices (native 100 | hip3 21); validated pools: native 284 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 121 book slices present in the validated pools): +0.253% | at 151.45 ZAR mean notional/trade: +0.38 ZAR/trade
- Realised (512 real closes per lane_gate._is_real_close, net of fees): +0.53 ZAR/trade | sd 4.82 | SE 0.21
- Gap: +0.14 ZAR/trade | t = +0.67 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.359% over 100/100 slices (pool 284) ~ +0.54 ZAR | realised 466 closes +0.67 ZAR sd 4.80 SE 0.22 | gap +0.14 t +0.61 | NOT ESTABLISHED
- hip3: claimed median +0.065% over 21/21 slices (pool 160) ~ +0.11 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.08 t -1.52 | NOT ESTABLISHED
- Ledger: 616 decision rows; 512 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 104 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 466 | wins: 226 | win%: 48.5 | P&L: **+313.46 ZAR** | today: -0.20 | 7d: -8.19 | 30d: -151.16
- By exit: target +516.3, trail_stop +106.9, horizon +70.0, max_bars +2.8, regime_shift -11.9, stop -370.6
- By entry regime (n/pnl): neutral 186/+233.0, bull 117/+178.4, bear 163/-97.9
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82; feat_range_pos_50:2:SHORT:h24 3n/0w -10.55
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPZAR 2n +18.07; BTCUSDC 51n +12.29; AAVEUSDC 3n +9.47
- Worst pairs: UNIUSDC 9n -26.80; HYPEUSDC 35n -22.27; ZECUSDC 16n -20.91; ETHUSDC 61n -20.28; ETHZAR 4n -14.36

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 8 open, stop-risk **31.22 ZAR**
  - ZECUSDC SELL ntl=115 risk=4.54 bars=1 stop=1328.9499999999999625 peak=1290.5
  - XMRUSDC SELL ntl=115 risk=4.53 bars=9 stop=621.95000000000001725 peak=601.63
  - PUMPUSDC SELL ntl=115 risk=4.52 bars=0 stop=0.004350250000000000320 peak=0.004186
  - XRPUSDC SELL ntl=115 risk=4.49 bars=22 stop=1.2933999999999998895 peak=1.2614
  - SOLUSDC SELL ntl=115 risk=4.41 bars=18 stop=98.96124999999999480 peak=96.946
  - UNIUSDC SELL ntl=115 risk=4.30 bars=2 stop=7.231950000000000105 peak=7.058
  - BTCUSDC SELL ntl=115 risk=2.41 bars=11 stop=78764.99999999999995 peak=77699.0
  - ETHUSDC SELL ntl=115 risk=2.02 bars=7 stop=2278.99650 peak=2254.3

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **31.22 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **31.22 / 161.44 ZAR | 20.8% | ok**
- Remaining: 127.9193 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 22, "skipped": 22, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 0, "opened": 1, "pair_held": 62, "signals": 330, "skipped": 267, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **ZECUSDC** 4.5411 ZAR
- positions without bars: 0 | replayed: 7 | invalid: 0

## 6. Monitored books

- Native: 100 | HIP-3: 21
- Native top (by paper P&L):
  - `feat_premium:2:SHORT:h15` edge=0.0109 n=2720 p=0.0180 src=validated_walk_forward unproven=False paper=2n/+4.23
  - `feat_vwap_dist:2:SHORT:h15` edge=0.0046 n=8333 p=0.3609 src=validated_walk_forward unproven=False paper=2n/+1.85
  - `feat_rsi_21:2:SHORT:h24` edge=0.0070 n=6576 p=0.0932 src=validated_walk_forward unproven=False paper=2n/+1.17
  - `feat_premium:2:SHORT:h20` edge=0.0099 n=3128 p=0.0307 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_50:2:SHORT:h12` edge=0.0060 n=8250 p=0.0045 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_macd_12_26:2:SHORT:h12` edge=0.0060 n=8473 p=0.0025 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ema_cross_10_20:2:SHORT:h12` edge=0.0058 n=8562 p=0.0127 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vwap_upper_dist:2:SHORT:h12` edge=0.0050 n=8973 p=0.0964 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Latest research: 2026-10-31T01:15:43.321862+00:00 | discovered 2240 | validated 284 | reg-confounded 684 | hostile-unproven 72
- floors: "" | book: {"rows": 103, "by_status": {"monitored": 100, "decayed": 1, "cooldown": 2}, "in_validated_pool": 103, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=1120 validated=1120 passing=284 eligible=237 best=289.4b best_fail=temporal_pass,breadth_ok
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=576 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_range_pos_50:L0S2:h12: mean=+18.0b t_no=2.22 folds=10110 mkt_corr=-0.04 dd=286b legs=12.5/11.3 fail=folds
  - feat_hl_range:L0S2:h24: mean=-18.7b t_no=2.07 folds=00100 mkt_corr=-0.28 dd=265b legs=16.3/7.1 fail=n_nonoverlap,mean<=0,folds
  - feat_ext_vs_ma_50:L0S2:h12: mean=+22.1b t_no=2.07 folds=10110 mkt_corr=-0.07 dd=274b legs=13.4/9.6 fail=folds
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

- Label: **neutral** | breadth bear=0.2 bull=0.0667 neutral=0.7333 | symbols=15
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 0 / bull 0
- as_of: 2026-10-31T17:35:38Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 1120 | eligible: 370 | observations: 2232 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
  - `feat_oi_chg_24@oi_lo:2:SHORT:h12` edge=289.4b n=99 breadth=3 validated=False prov=False armable=False (too_few_rows)
  - `feat_oi_chg_24@oi_lo:2:SHORT:h24` edge=266.2b n=90 breadth=3 validated=False prov=False armable=False (too_few_rows)
  - `feat_funding_rate@oi_lo:2:SHORT:h24` edge=265.6b n=310 breadth=9 validated=False prov=False armable=False (not_confirmed_bear)
  - `feat_funding_rate@oi_mid:2:SHORT:h24` edge=263.8b n=397 breadth=7 validated=False prov=False armable=False (not_confirmed_bear)
  - `feat_oi_chg_24@oi_lo:2:SHORT:h15` edge=261.5b n=87 breadth=3 validated=False prov=False armable=False (too_few_rows)
  - `feat_funding_rate@oi_lo:2:SHORT:h20` edge=254.9b n=359 breadth=9 validated=False prov=False armable=False (not_confirmed_bear)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+8.75 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **100/100** | hip3 **19/21**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 45
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
  - `feat_funding_rate:2:SHORT:h12` slice_pnl=-7.96
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
  - `feat_williams_r_14:0:SHORT:h24` slice_pnl=-1.23
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` lane_not_green
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-10-31T16:57:03: errors=0 signals=352 regime_blocked=347
- this cycle: closed=0 new_signals=352 skipped=289 slot_full=0 slice_full=0 pair_held=62
- Action funnel: regime_blocked=347 | lane_gate_blocked=2 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=62 | slot_full=0 | skipped=289
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 2, "pair_held": 62, "regime_blocked": 347, "skipped": 289, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=45
- aggregate_risk: ok open=26.6929 cap=161.4441 used=0.2077 remaining=127.9193 replayed=7 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
