# Breakwater daily print — 2026-11-08 03:24 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **395.24 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2304.67 ZAR** (seed 2000) | lifetime: **+304.67 ZAR** | closed: 553
- Today: 0 closed, **+0.00 ZAR**
- 7d: **+37.66 ZAR** | 30d: **-45.43 ZAR**

## 2b. Claimed vs realised

- Book: 84 slices (native 64 | hip3 20); validated pools: native 199 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 84 book slices present in the validated pools): +0.262% | at 148.77 ZAR mean notional/trade: +0.39 ZAR/trade
- Realised (553 real closes per lane_gate._is_real_close, net of fees): +0.55 ZAR/trade | sd 4.74 | SE 0.20
- Gap: +0.16 ZAR/trade | t = +0.80 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.315% over 64/64 slices (pool 199) ~ +0.46 ZAR | realised 507 closes +0.69 ZAR sd 4.72 SE 0.21 | gap +0.23 t +1.08 | NOT ESTABLISHED
- hip3: claimed median +0.062% over 20/20 slices (pool 160) ~ +0.10 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.07 t -1.51 | NOT ESTABLISHED
- Ledger: 666 decision rows; 553 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 113 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 507 | wins: 249 | win%: 49.1 | P&L: **+349.18 ZAR** | today: +0.00 | 7d: +37.66 | 30d: -45.43
- By exit: target +516.3, trail_stop +163.6, horizon +71.9, max_bars +2.8, regime_shift -11.9, stop -393.5
- By entry regime (n/pnl): neutral 209/+241.0, bull 121/+199.5, bear 177/-91.3
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_premium@oi_hi:2:SHORT:h24 3n/3w +24.15; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_premium:2:SHORT:h24 5n/4w +20.06
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_macd_12_26:2:SHORT:h15 3n/0w -11.55; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPZAR 2n +18.07; ENAUSDC 6n +13.54; AAVEUSDC 4n +10.89
- Worst pairs: UNIUSDC 11n -29.94; ZECUSDC 17n -21.96; ETHUSDC 67n -16.84; ETHZAR 4n -14.36; HYPEUSDC 38n -12.40

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 10 open, stop-risk **24.33 ZAR**
  - WLDUSDC SELL ntl=117 risk=3.76 bars=13 stop=0.34756750000000001540 peak=0.34035
  - NEARUSDC SELL ntl=117 risk=3.55 bars=10 stop=3.807500000000000180 peak=3.7264
  - XRPUSDC SELL ntl=117 risk=3.04 bars=12 stop=1.200875000000000040 peak=1.1731
  - UNIUSDC SELL ntl=117 risk=2.97 bars=9 stop=7.221974999999999945 peak=7.2137
  - SUIUSDC SELL ntl=117 risk=2.46 bars=7 stop=0.8753500000000000180 peak=0.86247
  - HYPEUSDC SELL ntl=117 risk=2.40 bars=8 stop=79.35949999999999645 peak=77.818
  - SOLUSDC SELL ntl=117 risk=2.05 bars=6 stop=91.045900 peak=89.9
  - BTCUSDC SELL ntl=117 risk=2.05 bars=5 stop=77148.88500 peak=75883.0
  - ETHUSDC SELL ntl=117 risk=2.05 bars=11 stop=2283.98225 peak=2247.4
  - ENAUSDC SELL ntl=117 risk=0.00 bars=14 stop=0.161022499999999996650 peak=0.16397

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **24.33 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **24.33 / 164.09 ZAR | 16.6% | ok**
- Remaining: 136.8366 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 15, "skipped": 15, "slice_full": 0, "slot_full": 0}, "native": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 132, "skipped": 42, "slice_full": 0, "slot_full": 90}}
- Highest-risk: **WLDUSDC** 3.7564 ZAR
- positions without bars: 0 | replayed: 10 | invalid: 0

## 6. Monitored books

- Native: 64 | HIP-3: 20
- Native top (by paper P&L):
  - `feat_ret_20:2:SHORT:h24` edge=0.0075 n=9257 p=0.3928 src=validated_walk_forward unproven=False paper=3n/+0.87
  - `feat_ret_5:2:SHORT:h12` edge=0.0039 n=10009 p=0.2470 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_price_roc_5:2:SHORT:h12` edge=0.0039 n=10009 p=0.2470 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_1:2:SHORT:h15` edge=0.0028 n=9697 p=0.2383 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_rsi_14:1:SHORT:h15` edge=0.0024 n=9881 p=0.7208 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_trend_neutral:0:SHORT:h24` edge=0.0039 n=17036 p=0.0650 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_rsi_7:1:SHORT:h15` edge=0.0028 n=9806 p=0.4239 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_squeeze:2:SHORT:h24` edge=0.0033 n=11331 p=0.0578 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Latest research: 2026-11-08T00:31:39.438217+00:00 | discovered 2240 | validated 199 | reg-confounded 862 | hostile-unproven 5
- floors: "" | book: {"rows": 71, "by_status": {"decayed": 6, "monitored": 64, "cooldown": 1}, "in_validated_pool": 71, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=1120 validated=1120 passing=199 eligible=194 best=333.2b best_fail=breadth_ok
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=576 qualifying=1 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_trend_slope_20:L2S0:h12: mean=+16.2b t_no=2.24 folds=11101 mkt_corr=-0.17 dd=260b legs=10.2/10.8 QUALIFIES
  - feat_time_since_low_20:L2S0:h15: mean=+15.6b t_no=3.04 folds=10101 mkt_corr=-0.31 dd=146b legs=12.3/12.3 fail=n_nonoverlap,folds,market_corr
  - feat_stoch_d_14:L2S0:h15: mean=-3.6b t_no=2.24 folds=10101 mkt_corr=-0.43 dd=195b legs=12.3/11.8 fail=mean<=0,folds,market_corr
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

- Label: **bear** | breadth bear=0.6875 bull=0.0 neutral=0.3125 | symbols=16
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 28 / bull 0
- as_of: 2026-11-07T23:14:52Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 1120 | eligible: 575 | observations: 2426 | armable: **1844**
- Armable slices: feat_adx_14:0:SHORT:h20, feat_adx_14:0:SHORT:h24, feat_adx_14:2:SHORT:h24, feat_asia_range:0:SHORT:h20, feat_asia_range:0:SHORT:h24, feat_asia_vol:0:SHORT:h20, feat_asia_vol:0:SHORT:h24, feat_atr_norm_ext:1:SHORT:h15, feat_atr_norm_ext:1:SHORT:h20, feat_atr_norm_ext:1:SHORT:h24, feat_atr_norm_ext:2:SHORT:h12, feat_atr_norm_ext:2:SHORT:h15, feat_atr_norm_ext:2:SHORT:h20, feat_atr_norm_ext:2:SHORT:h24, feat_atr_percent:1:SHORT:h12, feat_atr_percent:1:SHORT:h15, feat_atr_percent:1:SHORT:h20, feat_atr_percent:1:SHORT:h24, feat_atr_ratio:0:SHORT:h20, feat_atr_ratio:0:SHORT:h24, feat_bb_pos_20:1:SHORT:h15, feat_bb_pos_20:1:SHORT:h20, feat_bb_pos_20:1:SHORT:h24, feat_bb_pos_20:2:SHORT:h12, feat_bb_pos_20:2:SHORT:h15, feat_bb_pos_20:2:SHORT:h20, feat_bb_pos_20:2:SHORT:h24, feat_bb_squeeze_20:1:SHORT:h20, feat_bb_squeeze_20:1:SHORT:h24, feat_bb_squeeze_20:2:SHORT:h24, feat_bb_width_20:1:SHORT:h12, feat_bb_width_20:1:SHORT:h15, feat_bb_width_20:1:SHORT:h20, feat_bb_width_20:1:SHORT:h24, feat_bb_width_20:2:SHORT:h24, feat_book_imb_5:1:SHORT:h24, feat_book_imb_5@oi_lo:0:SHORT:h20, feat_book_imb_5@oi_lo:0:SHORT:h24, feat_book_imb_5@oi_lo:1:SHORT:h20, feat_book_imb_5@oi_lo:1:SHORT:h24, feat_book_imb_5@oi_mid:1:SHORT:h24, feat_buy_vol_ratio:0:SHORT:h20, feat_buy_vol_ratio:0:SHORT:h24, feat_buy_vol_ratio:1:SHORT:h24, feat_buy_vol_ratio:2:SHORT:h20, feat_buy_vol_ratio:2:SHORT:h24, feat_cci_20:1:SHORT:h15, feat_cci_20:1:SHORT:h20, feat_cci_20:1:SHORT:h24, feat_cci_20:2:SHORT:h12, feat_cci_20:2:SHORT:h15, feat_cci_20:2:SHORT:h20, feat_cci_20:2:SHORT:h24, feat_close_pos_ma:1:SHORT:h20, feat_close_pos_ma:1:SHORT:h24, feat_close_pos_ma:2:SHORT:h20, feat_close_pos_ma:2:SHORT:h24, feat_close_position:0:SHORT:h20, feat_close_position:0:SHORT:h24, feat_close_position:1:SHORT:h24, feat_close_position:2:SHORT:h20, feat_close_position:2:SHORT:h24, feat_donchian_break:1:SHORT:h15, feat_donchian_break:1:SHORT:h24, feat_donchian_break:2:SHORT:h12, feat_donchian_break:2:SHORT:h15, feat_donchian_break:2:SHORT:h20, feat_donchian_break:2:SHORT:h24, feat_donchian_width_20:0:SHORT:h15, feat_donchian_width_20:0:SHORT:h20, feat_donchian_width_20:1:SHORT:h15, feat_donchian_width_20:1:SHORT:h20, feat_donchian_width_20:1:SHORT:h24, feat_ema_cross_10_20:2:SHORT:h12, feat_ema_cross_10_20:2:SHORT:h15, feat_ema_cross_10_20:2:SHORT:h20, feat_ema_cross_10_20:2:SHORT:h24, feat_ext_strength:1:SHORT:h24, feat_ext_strength:2:SHORT:h12, feat_ext_strength:2:SHORT:h15, feat_ext_strength:2:SHORT:h20, feat_ext_strength:2:SHORT:h24, feat_ext_vs_ma_10:1:SHORT:h12, feat_ext_vs_ma_10:1:SHORT:h15, feat_ext_vs_ma_10:1:SHORT:h20, feat_ext_vs_ma_10:1:SHORT:h24, feat_ext_vs_ma_10:2:SHORT:h12, feat_ext_vs_ma_10:2:SHORT:h24, feat_ext_vs_ma_20:1:SHORT:h12, feat_ext_vs_ma_20:1:SHORT:h15, feat_ext_vs_ma_20:1:SHORT:h20, feat_ext_vs_ma_20:1:SHORT:h24, feat_ext_vs_ma_20:2:SHORT:h12, feat_ext_vs_ma_20:2:SHORT:h20, feat_ext_vs_ma_20:2:SHORT:h24, feat_ext_vs_ma_50:2:SHORT:h12, feat_ext_vs_ma_50:2:SHORT:h15, feat_ext_vs_ma_50:2:SHORT:h20, feat_ext_vs_ma_50:2:SHORT:h24, feat_funding_cum_24:1:SHORT:h12, feat_funding_cum_24:2:SHORT:h12, feat_funding_cum_24:2:SHORT:h15, feat_funding_cum_24:2:SHORT:h20, feat_funding_cum_24:2:SHORT:h24, feat_funding_cum_24@oi_hi:2:SHORT:h12, feat_funding_cum_24@oi_hi:2:SHORT:h15, feat_funding_cum_24@oi_hi:2:SHORT:h20, feat_funding_cum_24@oi_hi:2:SHORT:h24, feat_funding_cum_24@oi_lo:1:SHORT:h12, feat_funding_cum_24@oi_lo:1:SHORT:h15, feat_funding_cum_24@oi_lo:2:SHORT:h12, feat_funding_cum_24@oi_lo:2:SHORT:h15, feat_funding_cum_24@oi_lo:2:SHORT:h20, feat_funding_cum_24@oi_lo:2:SHORT:h24, feat_funding_cum_24@oi_mid:1:SHORT:h12, feat_funding_cum_24@oi_mid:1:SHORT:h15, feat_funding_cum_24@oi_mid:1:SHORT:h20, feat_funding_cum_24@oi_mid:1:SHORT:h24, feat_funding_rate:0:SHORT:h24, feat_funding_rate:1:SHORT:h12, feat_funding_rate:1:SHORT:h15, feat_funding_rate@oi_lo:1:SHORT:h12, feat_funding_rate@oi_lo:1:SHORT:h15, feat_funding_rate@oi_lo:1:SHORT:h20, feat_funding_rate@oi_lo:1:SHORT:h24, feat_gap:0:SHORT:h12, feat_gap:0:SHORT:h15, feat_gap:0:SHORT:h20, feat_gap:0:SHORT:h24, feat_gap:2:SHORT:h24, feat_gap_fill_ratio:0:SHORT:h24, feat_gap_fill_ratio:1:SHORT:h12, feat_gap_fill_ratio:1:SHORT:h15, feat_gap_fill_ratio:1:SHORT:h20, feat_gap_fill_ratio:1:SHORT:h24, feat_hl_range:0:SHORT:h12, feat_hl_range:0:SHORT:h15, feat_hl_range:0:SHORT:h20, feat_hl_range:0:SHORT:h24, feat_hour_utc:2:SHORT:h20, feat_intraday_mom:1:SHORT:h12, feat_intraday_mom:1:SHORT:h15, feat_intraday_mom:1:SHORT:h20, feat_intraday_mom:1:SHORT:h24, feat_intraday_mom:2:SHORT:h15, feat_intraday_mom:2:SHORT:h20, feat_intraday_mom:2:SHORT:h24, feat_kc_width:1:SHORT:h12, feat_kc_width:1:SHORT:h24, feat_keltner_pos:1:SHORT:h12, feat_keltner_pos:1:SHORT:h15, feat_keltner_pos:1:SHORT:h20, feat_keltner_pos:1:SHORT:h24, feat_keltner_pos:2:SHORT:h12, feat_keltner_pos:2:SHORT:h20, feat_keltner_pos:2:SHORT:h24, feat_macd_12_26:2:SHORT:h12, feat_macd_12_26:2:SHORT:h15, feat_macd_12_26:2:SHORT:h20, feat_macd_12_26:2:SHORT:h24, feat_mean_rev_strength:0:SHORT:h12, feat_mean_rev_strength:0:SHORT:h15, feat_mean_rev_strength:0:SHORT:h20, feat_mean_rev_strength:0:SHORT:h24, feat_mean_rev_strength:1:SHORT:h15, feat_mean_rev_strength:1:SHORT:h20, feat_mean_rev_strength:1:SHORT:h24, feat_oi_chg_24:2:SHORT:h12, feat_oi_chg_24:2:SHORT:h24, feat_oi_chg_24@oi_hi:2:SHORT:h15, feat_oi_chg_24@oi_hi:2:SHORT:h20, feat_oi_chg_24@oi_hi:2:SHORT:h24, feat_oi_chg_24@oi_lo:1:SHORT:h24, feat_oi_chg_24@oi_lo:2:SHORT:h12, feat_oi_chg_24@oi_lo:2:SHORT:h24, feat_oi_chg_24@oi_mid:2:SHORT:h12, feat_oi_chg_24@oi_mid:2:SHORT:h15, feat_oi_ret_div:0:SHORT:h20, feat_oi_ret_div@oi_lo:0:SHORT:h24, feat_oi_ret_div@oi_lo:1:SHORT:h12, feat_oi_ret_div@oi_lo:2:SHORT:h24, feat_oi_ret_div@oi_mid:1:SHORT:h15, feat_oi_ret_div@oi_mid:1:SHORT:h20, feat_oi_ret_div@oi_mid:1:SHORT:h24, feat_overnight_ret:0:SHORT:h12, feat_overnight_ret:0:SHORT:h15, feat_overnight_ret:0:SHORT:h20, feat_overnight_ret:0:SHORT:h24, feat_overnight_ret:2:SHORT:h24, feat_premium:1:SHORT:h12, feat_premium:1:SHORT:h15, feat_premium:1:SHORT:h20, feat_premium:1:SHORT:h24, feat_premium@oi_hi:1:SHORT:h24, feat_premium@oi_lo:1:SHORT:h12, feat_premium@oi_lo:1:SHORT:h15, feat_premium@oi_lo:1:SHORT:h20, feat_premium@oi_lo:1:SHORT:h24, feat_price_accel:0:SHORT:h24, feat_price_accel:1:SHORT:h12, feat_price_accel:1:SHORT:h15, feat_price_accel:1:SHORT:h20, feat_price_accel:1:SHORT:h24, feat_price_accel:2:SHORT:h20, feat_price_accel:2:SHORT:h24, feat_price_roc_5:1:SHORT:h15, feat_price_roc_5:1:SHORT:h20, feat_price_roc_5:1:SHORT:h24, feat_price_roc_5:2:SHORT:h12, feat_price_roc_5:2:SHORT:h15, feat_price_roc_5:2:SHORT:h20, feat_price_roc_5:2:SHORT:h24, feat_range_expansion:0:SHORT:h15, feat_range_expansion:0:SHORT:h20, feat_range_expansion:0:SHORT:h24, feat_range_expansion:1:SHORT:h20, feat_range_expansion:1:SHORT:h24, feat_range_pos_20:2:SHORT:h12, feat_range_pos_20:2:SHORT:h15, feat_range_pos_20:2:SHORT:h20, feat_range_pos_20:2:SHORT:h24, feat_range_pos_50:2:SHORT:h12, feat_range_pos_50:2:SHORT:h15, feat_range_pos_50:2:SHORT:h20, feat_range_pos_50:2:SHORT:h24, feat_realized_vol_20:0:SHORT:h12, feat_realized_vol_20:1:SHORT:h12, feat_realized_vol_20:1:SHORT:h15, feat_realized_vol_20:1:SHORT:h20, feat_realized_vol_20:1:SHORT:h24, feat_ret_10:1:SHORT:h12, feat_ret_10:1:SHORT:h15, feat_ret_10:1:SHORT:h20, feat_ret_10:1:SHORT:h24, feat_ret_10:2:SHORT:h12, feat_ret_10:2:SHORT:h20, feat_ret_10:2:SHORT:h24, feat_ret_1:1:SHORT:h12, feat_ret_1:1:SHORT:h20, feat_ret_1:1:SHORT:h24, feat_ret_1:2:SHORT:h15, feat_ret_1:2:SHORT:h20, feat_ret_1:2:SHORT:h24, feat_ret_20:1:SHORT:h12, feat_ret_20:1:SHORT:h15, feat_ret_20:1:SHORT:h20, feat_ret_20:1:SHORT:h24, feat_ret_20:2:SHORT:h20, feat_ret_20:2:SHORT:h24, feat_ret_3:1:SHORT:h15, feat_ret_3:1:SHORT:h20, feat_ret_3:1:SHORT:h24, feat_ret_3:2:SHORT:h12, feat_ret_3:2:SHORT:h24, feat_ret_5:1:SHORT:h15, feat_ret_5:1:SHORT:h20, feat_ret_5:1:SHORT:h24, feat_ret_5:2:SHORT:h12, feat_ret_5:2:SHORT:h15, feat_ret_5:2:SHORT:h20, feat_ret_5:2:SHORT:h24, feat_ret_autocorr:1:SHORT:h15, feat_ret_autocorr:1:SHORT:h20, feat_ret_autocorr:1:SHORT:h24, feat_ret_sign_streak:0:SHORT:h24, feat_ret_sign_streak:1:SHORT:h15, feat_ret_sign_streak:1:SHORT:h20, feat_ret_sign_streak:1:SHORT:h24, feat_ret_sign_streak:2:SHORT:h12, feat_ret_sign_streak:2:SHORT:h15, feat_ret_sign_streak:2:SHORT:h20, feat_ret_sign_streak:2:SHORT:h24, feat_ret_vol:2:SHORT:h12, feat_ret_vol:2:SHORT:h15, feat_ret_vol:2:SHORT:h20, feat_ret_vol:2:SHORT:h24, feat_rsi_14:1:SHORT:h15, feat_rsi_14:1:SHORT:h20, feat_rsi_14:1:SHORT:h24, feat_rsi_14:2:SHORT:h12, feat_rsi_14:2:SHORT:h24, feat_rsi_21:1:SHORT:h12, feat_rsi_21:1:SHORT:h15, feat_rsi_21:1:SHORT:h20, feat_rsi_21:1:SHORT:h24, feat_rsi_21:2:SHORT:h12, feat_rsi_21:2:SHORT:h20, feat_rsi_21:2:SHORT:h24, feat_rsi_7:1:SHORT:h15, feat_rsi_7:1:SHORT:h20, feat_rsi_7:1:SHORT:h24, feat_rsi_7:2:SHORT:h12, feat_rsi_divergence:0:SHORT:h20, feat_rsi_divergence:0:SHORT:h24, feat_rsi_divergence:1:SHORT:h20, feat_rsi_divergence:1:SHORT:h24, feat_rsi_divergence:2:SHORT:h24, feat_session_mom:1:SHORT:h20, feat_session_mom:1:SHORT:h24, feat_session_mom:2:SHORT:h15, feat_session_mom:2:SHORT:h20, feat_session_mom:2:SHORT:h24, feat_squeeze:1:SHORT:h12, feat_squeeze:1:SHORT:h15, feat_squeeze:1:SHORT:h20, feat_squeeze:1:SHORT:h24, feat_squeeze:2:SHORT:h24, feat_stoch_d_14:1:SHORT:h20, feat_stoch_d_14:1:SHORT:h24, feat_stoch_k_14:1:SHORT:h15, feat_stoch_k_14:1:SHORT:h20, feat_stoch_k_14:1:SHORT:h24, feat_stoch_k_14:2:SHORT:h12, feat_stoch_k_14:2:SHORT:h15, feat_stoch_k_14:2:SHORT:h20, feat_stoch_k_14:2:SHORT:h24, feat_time_since_high_20:0:SHORT:h12, feat_time_since_high_20:0:SHORT:h20, feat_time_since_high_20:0:SHORT:h24, feat_time_since_low_20:1:SHORT:h12, feat_time_since_low_20:1:SHORT:h15, feat_time_since_low_20:1:SHORT:h20, feat_time_since_low_20:1:SHORT:h24, feat_trend_neutral:0:SHORT:h20, feat_trend_neutral:0:SHORT:h24, feat_trend_slope_20:1:SHORT:h24, feat_trend_slope_20:2:SHORT:h12, feat_trend_slope_20:2:SHORT:h15, feat_trend_slope_20:2:SHORT:h20, feat_trend_slope_20:2:SHORT:h24, feat_trend_strength_20:0:SHORT:h24, feat_trend_strength_20:1:SHORT:h15, feat_trend_strength_20:1:SHORT:h20, feat_trend_strength_20:2:SHORT:h20, feat_trend_strength_20:2:SHORT:h24, feat_vol_breakout:1:SHORT:h15, feat_vol_breakout:1:SHORT:h20, feat_vol_breakout:1:SHORT:h24, feat_vol_breakout:2:SHORT:h12, feat_vol_breakout:2:SHORT:h15, feat_vol_breakout:2:SHORT:h20, feat_vol_breakout:2:SHORT:h24, feat_vol_breakout_strength:0:SHORT:h12, feat_vol_breakout_strength:0:SHORT:h15, feat_vol_breakout_strength:0:SHORT:h20, feat_vol_breakout_strength:0:SHORT:h24, feat_vol_breakout_strength:1:SHORT:h20, feat_vol_breakout_strength:1:SHORT:h24, feat_vol_breakout_strength:2:SHORT:h24, feat_vol_contraction:0:SHORT:h24, feat_vol_of_vol:1:SHORT:h20, feat_vol_of_vol:1:SHORT:h24, feat_vol_of_vol:2:SHORT:h24, feat_vol_regime:0:SHORT:h24, feat_vol_roc_20:0:SHORT:h15, feat_vol_roc_20:0:SHORT:h20, feat_vol_roc_20:0:SHORT:h24, feat_vol_roc_20:1:SHORT:h12, feat_vol_roc_20:1:SHORT:h15, feat_vol_roc_20:1:SHORT:h20, feat_vol_roc_20:1:SHORT:h24, feat_vol_sma_ratio:0:SHORT:h15, feat_vol_sma_ratio:0:SHORT:h20, feat_vol_sma_ratio:0:SHORT:h24, feat_vol_sma_ratio:1:SHORT:h20, feat_vol_sma_ratio:1:SHORT:h24, feat_vol_sma_ratio:2:SHORT:h24, feat_vol_trend:2:SHORT:h12, feat_vol_trend:2:SHORT:h15, feat_vol_trend:2:SHORT:h20, feat_vol_trend:2:SHORT:h24, feat_vwap_dist:1:SHORT:h12, feat_vwap_dist:1:SHORT:h15, feat_vwap_dist:2:SHORT:h12, feat_vwap_dist:2:SHORT:h15, feat_vwap_dist:2:SHORT:h20, feat_vwap_dist:2:SHORT:h24, feat_vwap_lower_dist:2:SHORT:h12, feat_vwap_lower_dist:2:SHORT:h15, feat_vwap_lower_dist:2:SHORT:h20, feat_vwap_lower_dist:2:SHORT:h24, feat_vwap_upper_dist:1:SHORT:h15, feat_williams_r_14:0:SHORT:h12, feat_williams_r_14:0:SHORT:h15, feat_williams_r_14:0:SHORT:h20, feat_williams_r_14:0:SHORT:h24, feat_williams_r_14:1:SHORT:h20, feat_williams_r_14:1:SHORT:h24, feat_zscore_20:1:SHORT:h15, feat_zscore_20:1:SHORT:h20, feat_zscore_20:1:SHORT:h24, feat_zscore_20:2:SHORT:h12, feat_zscore_20:2:SHORT:h15, feat_zscore_20:2:SHORT:h20, feat_zscore_20:2:SHORT:h24
- Armable pairs: BTCUSDC, ENAUSDC, ETHUSDC, HYPEUSDC, KPEPEUSDC, LITUSDC, NEARUSDC, PUMPUSDC, SOLUSDC, SUIUSDC, TRUMPUSDC, UNIUSDC, WLDUSDC, XMRUSDC, XRPUSDC, ZECUSDC
  - `feat_funding_rate@oi_mid:2:SHORT:h24` edge=331.6b n=342 breadth=6 validated=True prov=False armable=True (ok)
  - `feat_funding_rate@oi_lo:2:SHORT:h24` edge=318.7b n=211 breadth=5 validated=True prov=False armable=True (ok)
  - `feat_funding_rate@oi_mid:2:SHORT:h20` edge=247.0b n=352 breadth=7 validated=True prov=False armable=True (ok)
  - `feat_funding_rate@oi_lo:2:SHORT:h20` edge=223.1b n=239 breadth=6 validated=True prov=False armable=True (ok)
  - `feat_funding_rate:2:SHORT:h24` edge=188.5b n=1076 breadth=18 validated=True prov=False armable=True (ok)
  - `feat_funding_rate@oi_mid:2:SHORT:h15` edge=181.5b n=275 breadth=7 validated=True prov=False armable=True (ok)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+29.37 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **64/64** | hip3 **19/20**
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

- Latest scan 2026-11-08T00:27:50: errors=2 signals=147 regime_blocked=132
- this cycle: closed=0 new_signals=147 skipped=57 slot_full=90 slice_full=0 pair_held=0
- Action funnel: regime_blocked=132 | lane_gate_blocked=2 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=0 | cluster_cap=0 | family_vetoed=0 | slot_full=90 | skipped=57
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "cluster_cap": 0, "family_vetoed": 0, "lane_gate_blocked": 2, "pair_held": 0, "regime_blocked": 132, "skipped": 57, "slice_full": 0, "slot_full": 90})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=48
- aggregate_risk: ok open=24.3275 cap=164.0934 used=0.1661 remaining=136.8366 replayed=10 no_new_bars=0
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:BOT"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:LYTE"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
