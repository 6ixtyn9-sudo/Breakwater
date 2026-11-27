# Breakwater daily print — 2026-11-27 12:38 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

> ## COMA ALARM — NATIVE

> No **proven** slice in this lane. Auditions can still open entries, so
> this is not a dead lane: it trades, but nothing in it trades on a record
> it earned, so it cannot unfreeze itself. The runner will keep reporting
> operational, which is why this block exists. Attention, not intervention.

## 1. Posture

- No guardian_ok row found.

## 2. Paper account

- Equity: **2387.58 ZAR** (seed 2000) | lifetime: **+387.58 ZAR** | closed: 643
- Today: 6 closed, **-23.17 ZAR**
- 7d: **+3.30 ZAR** | 30d: **+127.75 ZAR**

## 2b. Claimed vs realised

- Book: 61 slices (native 41 | hip3 20); validated pools: native 217 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 61 book slices present in the validated pools): +0.460% | at 145.13 ZAR mean notional/trade: +0.67 ZAR/trade
- Realised (643 real closes per lane_gate._is_real_close, net of fees): +0.60 ZAR/trade | sd 4.78 | SE 0.19
- Gap: -0.06 ZAR/trade | t = -0.34 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.554% over 41/41 slices (pool 217) ~ +0.79 ZAR | realised 597 closes +0.72 ZAR sd 4.76 SE 0.19 | gap -0.07 t -0.36 | NOT ESTABLISHED
- hip3: claimed median +0.062% over 20/20 slices (pool 160) ~ +0.10 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.07 t -1.51 | NOT ESTABLISHED
- Ledger: 773 decision rows; 643 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 130 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 597 | wins: 299 | win%: 50.1 | P&L: **+432.09 ZAR** | today: -23.17 | 7d: +3.30 | 30d: +127.75
- By exit: target +516.3, trail_stop +344.3, horizon +77.9, max_bars +2.8, regime_shift -11.9, stop -497.2
- By entry regime (n/pnl): neutral 244/+225.3, bull 122/+199.3, bear 231/+7.5
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_adx_14:1:SHORT:h20 4n/4w +53.91; feat_overnight_ret:1:SHORT:h24 2n/2w +26.35; feat_trend_neutral:0:SHORT:h24 5n/5w +24.80
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_gap_fill_ratio:0:SHORT:h24 4n/0w -16.28; feat_funding_cum_24:0:SHORT:h24 5n/1w -16.09; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_vwap_dist:0:SHORT:h24 3n/0w -13.04
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; BTCUSDC 72n +29.41; ENAUSDC 8n +18.35; XRPZAR 2n +18.07
- Worst pairs: ZECUSDC 17n -21.96; UNIUSDC 15n -17.05; DOGEUSDC 20n -16.39; ETHZAR 4n -14.36; XMRUSDC 19n -7.37

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 4 open, stop-risk **13.47 ZAR**
  - ETHUSDC SELL ntl=122 risk=3.76 bars=2 stop=1781.4500000000000775 peak=1731.2
  - XRPUSDC SELL ntl=122 risk=3.50 bars=0 stop=1.0036425000000000335 peak=0.97562
  - SOLUSDC SELL ntl=122 risk=3.47 bars=1 stop=75.46674999999999980 peak=73.399
  - BTCUSDC SELL ntl=122 risk=2.74 bars=3 stop=63098.999999999999905 peak=61835.0

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **13.47 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **13.47 / 170.44 ZAR | 8.6% | ok**
- Remaining: 155.7525 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 15, "skipped": 15, "slice_full": 0, "slot_full": 0}, "native": {"cluster_cap": 25, "lane_gate_blocked": 0, "opened": 1, "pair_held": 14, "signals": 68, "skipped": 28, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **ETHUSDC** 3.7584 ZAR
- positions without bars: 0 | replayed: 3 | invalid: 0

## 6. Monitored books

- Native: 41 | HIP-3: 20
- Native top (by paper P&L):
  - `feat_bb_width_20:2:SHORT:h24` edge=0.0079 n=11118 p=0.1358 src=validated_walk_forward unproven=False paper=1n/+1.24
  - `feat_trend_slope_20:0:SHORT:h24` edge=0.0052 n=10112 p=0.6617 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_strength:0:SHORT:h24` edge=0.0050 n=10861 p=0.4636 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_20:0:SHORT:h24` edge=0.0052 n=10176 p=0.5595 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_20:0:SHORT:h20` edge=0.0026 n=9557 p=0.8322 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_oi_chg_24@oi_mid:2:SHORT:h20` edge=0.0159 n=1885 p=0.0361 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_funding_rate@oi_lo:0:SHORT:h12` edge=0.0035 n=7195 p=0.1332 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_premium@oi_lo:0:SHORT:h15` edge=0.0030 n=4413 p=0.1374 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Latest research: 2026-11-26T00:32:30.405673+00:00 | discovered 2240 | validated 217 | reg-confounded 1360 | hostile-unproven 11
- floors: "" | book: {"rows": 47, "by_status": {"monitored": 42, "decayed": 3, "cooldown": 2}, "in_validated_pool": 47, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=1120 validated=1120 passing=217 eligible=579 best=159.1b best_fail=direction_ok,regime_confounded,alpha<=0
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=576 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_macd_12_26:L0S2:h24: mean=+21.6b t_no=2.42 folds=01110 mkt_corr=-0.46 dd=68b legs=9.8/8.9 fail=n_nonoverlap,folds,market_corr
  - feat_ext_vs_ma_10:L2S0:h24: mean=+3.7b t_no=2.27 folds=01011 mkt_corr=-0.35 dd=128b legs=9.4/9.8 fail=n_nonoverlap,folds,market_corr
  - feat_range_pos_50:L0S2:h15: mean=-19.0b t_no=2.26 folds=00000 mkt_corr=-0.34 dd=135b legs=11.4/9.9 fail=mean<=0,folds,market_corr
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

- Label: **neutral** | breadth bear=0.0667 bull=0.3333 neutral=0.6 | symbols=15
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 0 / bull 0
- as_of: 2026-11-27T12:35:30Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 1120 | eligible: 946 | observations: 5028 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
  - `feat_oi_chg_24@oi_mid:2:SHORT:h20` edge=159.1b n=1885 breadth=12 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_oi_chg_24@oi_mid:2:SHORT:h24` edge=157.9b n=1749 breadth=11 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_vol_regime:1:SHORT:h24` edge=133.6b n=6915 breadth=34 validated=False prov=False armable=False (regime_confounded)
  - `feat_vol_contraction:1:SHORT:h24` edge=133.6b n=6915 breadth=34 validated=False prov=False armable=False (regime_confounded)
  - `feat_oi_ret_div@oi_mid:1:SHORT:h24` edge=133.4b n=1969 breadth=11 validated=False prov=False armable=False (not_confirmed_bear)
  - `feat_oi_chg_24@oi_mid:1:SHORT:h24` edge=128.5b n=1990 breadth=11 validated=False prov=False armable=False (not_confirmed_bear)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-51.25 | frozen=YES
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3, native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 31
  - `feat_adx_14:1:SHORT:h20` pnl=+53.91
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
  - `feat_ext_vs_ma_50:2:SHORT:h24` pnl=+1.39
  - `feat_funding_cum_24:2:SHORT:h20` pnl=+5.47
  - `feat_intraday_mom:2:LONG:h24` pnl=+7.09
  - `feat_macd_12_26:2:SHORT:h24` pnl=+1.90
  - `feat_premium:2:SHORT:h24` pnl=+20.06
  - `feat_premium@oi_hi:2:SHORT:h24` pnl=+24.15
  - `feat_price_roc_5:1:LONG:h24` pnl=+0.70
  - `feat_realized_vol_20:2:LONG:h12` pnl=+0.61
  - `feat_ret_10:2:LONG:h19` pnl=+14.58
  - `feat_ret_20:2:LONG:h14` pnl=+13.42
  - `feat_ret_autocorr:2:SHORT:h20` pnl=+15.53
  - `feat_ret_autocorr:2:SHORT:h24` pnl=+8.16
  - `feat_rsi_divergence:2:LONG:h20` pnl=+8.36
  - `feat_trend_neutral:0:SHORT:h24` pnl=+24.80
  - `feat_trend_slope_20:2:LONG:h12` pnl=+11.12
  - `feat_vol_regime:0:SHORT:h24` pnl=+8.78
  - `feat_vwap_upper_dist:2:SHORT:h24` pnl=+12.06
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **39/41** | hip3 **19/20**
- **COMA LANES: native** — frozen with no tradable slice on an earned green record; auditions may still open.
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 55
  - `feat_adx_14:2:LONG:h12` lane_not_green
  - `feat_adx_14:2:LONG:h15` lane_not_green
  - `feat_atr_norm_ext:2:LONG:h13` lane_not_green
  - `feat_atr_percent:2:LONG:h12` lane_not_green
  - `feat_atr_ratio:0:LONG:h24` lane_not_green
  - `feat_bb_squeeze_20:2:LONG:h20` lane_not_green
  - `feat_bb_width_20:2:LONG:h15` lane_not_green
  - `feat_book_imb_5@oi_hi:1:SHORT:h20` lane_not_green
  - `feat_buy_vol_ratio:2:LONG:h24` lane_not_green
  - `feat_cci_20:0:LONG:h24` lane_not_green
  - `feat_cci_20:2:SHORT:h24` lane_not_green
  - `feat_donchian_break:2:LONG:h15` lane_not_green
  - `feat_ema_cross_10_20:2:LONG:h12` lane_not_green
  - `feat_ema_cross_10_20:2:SHORT:h24` lane_not_green
  - `feat_ext_vs_ma_50:0:LONG:h20` lane_not_green
  - `feat_funding_cum_24:0:SHORT:h24` lane_not_green
  - `feat_funding_cum_24:2:SHORT:h12` lane_not_green
  - `feat_funding_rate:2:SHORT:h12` lane_not_green
  - `feat_gap_fill_ratio:0:SHORT:h24` lane_not_green
  - `feat_hour_utc:2:LONG:h15` lane_not_green
  - `feat_kc_width:2:LONG:h12` lane_not_green
  - `feat_kc_width:2:LONG:h15` lane_not_green
  - `feat_macd_12_26:2:SHORT:h15` lane_not_green
  - `feat_oi_ret_div@oi_hi:2:SHORT:h24` lane_not_green
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
  - `feat_rsi_divergence:0:SHORT:h20` lane_not_green
  - `feat_time_since_high_20:0:LONG:h12` lane_not_green
  - `feat_trend_slope_20:2:SHORT:h24` lane_not_green
  - `feat_trend_strength_20:2:SHORT:h24` lane_not_green
  - `feat_vol_breakout:2:LONG:h15` lane_not_green
  - `feat_vol_of_vol:1:LONG:h24` lane_not_green
  - `feat_vol_of_vol:2:LONG:h12` lane_not_green
  - `feat_vol_of_vol:2:LONG:h15` lane_not_green
  - `feat_vol_sma_ratio:0:LONG:h24` lane_not_green
  - `feat_vol_trend:0:LONG:h24` lane_not_green
  - `feat_vwap_dist:0:SHORT:h24` lane_not_green
  - `feat_williams_r_14:0:SHORT:h24` lane_not_green
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` lane_not_green
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-11-27T12:04:21: errors=0 signals=83 regime_blocked=237
- this cycle: closed=0 new_signals=83 skipped=43 slot_full=0 slice_full=0 pair_held=14
- Action funnel: regime_blocked=237 | lane_gate_blocked=3 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=14 | cluster_cap=25 | family_vetoed=2 | slot_full=0 | skipped=43
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "cluster_cap": 25, "family_vetoed": 2, "lane_gate_blocked": 3, "pair_held": 14, "regime_blocked": 237, "skipped": 43, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=False hip3_green=False frozen=hip3,native islands=31 blocks=55
- aggregate_risk: ok open=9.9710 cap=170.4381 used=0.0862 remaining=155.7525 replayed=3 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
