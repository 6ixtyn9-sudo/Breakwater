# Breakwater daily print — 2026-11-03 09:11 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

> ## WARNING — only 3 proven slice(s) trading (native 2, hip3 1); 112 slices are auditioning in frozen lanes. One bad proven trade from coma.

## 1. Posture

- Mode: **readonly** | VALR equity: **411.13 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2259.78 ZAR** (seed 2000) | lifetime: **+259.78 ZAR** | closed: 531
- Today: 1 closed, **+0.14 ZAR**
- 7d: **-15.31 ZAR** | 30d: **-160.19 ZAR**

## 2b. Claimed vs realised

- Book: 114 slices (native 93 | hip3 21); validated pools: native 284 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 114 book slices present in the validated pools): +0.246% | at 150.15 ZAR mean notional/trade: +0.37 ZAR/trade
- Realised (531 real closes per lane_gate._is_real_close, net of fees): +0.49 ZAR/trade | sd 4.75 | SE 0.21
- Gap: +0.12 ZAR/trade | t = +0.58 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.302% over 93/93 slices (pool 284) ~ +0.45 ZAR | realised 485 closes +0.63 ZAR sd 4.72 SE 0.21 | gap +0.18 t +0.83 | NOT ESTABLISHED
- hip3: claimed median +0.065% over 21/21 slices (pool 160) ~ +0.11 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.08 t -1.52 | NOT ESTABLISHED
- Ledger: 639 decision rows; 531 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 108 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 485 | wins: 233 | win%: 48.0 | P&L: **+304.28 ZAR** | today: +0.14 | 7d: -15.31 | 30d: -160.19
- By exit: target +516.3, trail_stop +107.4, horizon +69.3, max_bars +2.8, regime_shift -11.9, stop -379.6
- By entry regime (n/pnl): neutral 194/+226.6, bull 119/+181.3, bear 172/-103.6
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82; feat_range_pos_50:2:SHORT:h24 3n/0w -10.55
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPZAR 2n +18.07; BTCUSDC 53n +11.53; AAVEUSDC 4n +10.89
- Worst pairs: UNIUSDC 11n -29.94; ZECUSDC 17n -21.96; ETHUSDC 62n -21.44; HYPEUSDC 36n -21.43; ETHZAR 4n -14.36

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 6 open, stop-risk **0.00 ZAR**
  - NEARUSDC SELL ntl=115 risk=0.00 bars=43 stop=3.9102749999999996750 peak=4.41
  - HYPEUSDC SELL ntl=115 risk=0.00 bars=34 stop=84.726749999999999250 peak=89.024
  - ENAUSDC SELL ntl=115 risk=0.00 bars=33 stop=0.17479999999999999400 peak=0.187
  - ETHUSDC SELL ntl=115 risk=0.00 bars=22 stop=2286.5499999999997050 peak=2300.9
  - BTCUSDC SELL ntl=115 risk=0.00 bars=21 stop=77707.805000 peak=78220.0
  - SOLUSDC SELL ntl=115 risk=0.00 bars=20 stop=93.582750000000002600 peak=94.91

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **0.00 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 160.83 ZAR | 1.1% | ok**
- Remaining: 159.1089 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 48, "skipped": 48, "slice_full": 0, "slot_full": 0}, "native": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 0, "skipped": 0, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **NEARUSDC** 0.0000 ZAR
- positions without bars: 0 | replayed: 12 | invalid: 0

## 6. Monitored books

- Native: 93 | HIP-3: 21
- Native top (by paper P&L):
  - `feat_funding_cum_24:2:SHORT:h20` edge=0.0120 n=2073 p=0.0772 src=validated_walk_forward unproven=False paper=5n/+5.47
  - `feat_donchian_break:2:SHORT:h24` edge=0.0058 n=9958 p=0.2858 src=validated_walk_forward unproven=False paper=2n/+3.68
  - `feat_macd_12_26:2:SHORT:h24` edge=0.0097 n=6543 p=0.0694 src=validated_walk_forward unproven=False paper=2n/+1.43
  - `feat_ext_vs_ma_50:2:SHORT:h24` edge=0.0073 n=8605 p=0.0026 src=validated_walk_forward unproven=False paper=7n/+1.39
  - `feat_ret_20:2:SHORT:h20` edge=0.0050 n=9191 p=0.2248 src=validated_walk_forward unproven=False paper=2n/+0.52
  - `feat_atr_percent:1:SHORT:h15` edge=0.0039 n=8756 p=0.3261 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_20:2:SHORT:h12` edge=0.0035 n=9558 p=0.8798 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_mean_rev_strength:0:SHORT:h12` edge=0.0036 n=9896 p=0.6399 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Latest research: 2026-11-03T00:31:05.131428+00:00 | discovered 2240 | validated 284 | reg-confounded 811 | hostile-unproven 5
- floors: "" | book: {"rows": 97, "by_status": {"monitored": 93, "decayed": 3, "cooldown": 1}, "in_validated_pool": 97, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=1120 validated=1120 passing=284 eligible=182 best=239.7b best_fail=temporal_pass,breadth_ok
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=576 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_atr_percent:L0S2:h20: mean=+1.6b t_no=2.61 folds=01010 mkt_corr=-0.40 dd=318b legs=19.0/6.0 fail=n_nonoverlap,folds,market_corr
  - feat_stoch_k_14:L0S2:h20: mean=+4.5b t_no=2.54 folds=01100 mkt_corr=+0.06 dd=128b legs=11.7/12.6 fail=n_nonoverlap,folds
  - feat_rsi_14:L0S2:h20: mean=-0.9b t_no=2.37 folds=11000 mkt_corr=-0.03 dd=123b legs=11.9/11.7 fail=n_nonoverlap,mean<=0,folds
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

- Label: **bear** | breadth bear=0.6 bull=0.0667 neutral=0.3333 | symbols=15
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 15 / bull 0
- as_of: 2026-11-03T08:35:30Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 1120 | eligible: 407 | observations: 1548 | armable: **1242**
- Armable slices: feat_adx_14:1:SHORT:h15, feat_adx_14:2:SHORT:h24, feat_atr_norm_ext:2:SHORT:h12, feat_atr_norm_ext:2:SHORT:h15, feat_atr_norm_ext:2:SHORT:h20, feat_atr_norm_ext:2:SHORT:h24, feat_atr_percent:1:SHORT:h12, feat_atr_percent:1:SHORT:h15, feat_atr_percent:1:SHORT:h20, feat_atr_percent:1:SHORT:h24, feat_atr_ratio:1:SHORT:h12, feat_atr_ratio:1:SHORT:h15, feat_atr_ratio:1:SHORT:h20, feat_atr_ratio:1:SHORT:h24, feat_atr_ratio:2:SHORT:h24, feat_bb_pos_20:1:SHORT:h24, feat_bb_pos_20:2:SHORT:h12, feat_bb_pos_20:2:SHORT:h15, feat_bb_pos_20:2:SHORT:h20, feat_bb_pos_20:2:SHORT:h24, feat_bb_squeeze_20:1:SHORT:h24, feat_bb_width_20:1:SHORT:h15, feat_bb_width_20:1:SHORT:h20, feat_bb_width_20:1:SHORT:h24, feat_book_imb_5:0:SHORT:h24, feat_book_imb_5@oi_lo:0:SHORT:h12, feat_book_imb_5@oi_lo:0:SHORT:h15, feat_book_imb_5@oi_lo:0:SHORT:h20, feat_book_imb_5@oi_lo:0:SHORT:h24, feat_book_imb_5@oi_lo:1:SHORT:h20, feat_book_imb_5@oi_lo:1:SHORT:h24, feat_book_imb_5@oi_lo:2:SHORT:h24, feat_buy_vol_ratio:2:SHORT:h20, feat_buy_vol_ratio:2:SHORT:h24, feat_cci_20:1:SHORT:h24, feat_cci_20:2:SHORT:h12, feat_cci_20:2:SHORT:h15, feat_cci_20:2:SHORT:h20, feat_cci_20:2:SHORT:h24, feat_close_position:2:SHORT:h20, feat_close_position:2:SHORT:h24, feat_donchian_break:1:SHORT:h15, feat_donchian_break:2:SHORT:h12, feat_donchian_break:2:SHORT:h15, feat_donchian_break:2:SHORT:h20, feat_donchian_break:2:SHORT:h24, feat_donchian_width_20:0:SHORT:h24, feat_donchian_width_20:1:SHORT:h12, feat_donchian_width_20:1:SHORT:h15, feat_donchian_width_20:1:SHORT:h20, feat_donchian_width_20:1:SHORT:h24, feat_ema_cross_10_20:2:SHORT:h12, feat_ema_cross_10_20:2:SHORT:h15, feat_ema_cross_10_20:2:SHORT:h20, feat_ema_cross_10_20:2:SHORT:h24, feat_ext_strength:2:SHORT:h12, feat_ext_strength:2:SHORT:h15, feat_ext_strength:2:SHORT:h20, feat_ext_strength:2:SHORT:h24, feat_ext_vs_ma_10:2:SHORT:h15, feat_ext_vs_ma_10:2:SHORT:h20, feat_ext_vs_ma_20:2:SHORT:h12, feat_ext_vs_ma_20:2:SHORT:h15, feat_ext_vs_ma_20:2:SHORT:h20, feat_ext_vs_ma_20:2:SHORT:h24, feat_ext_vs_ma_50:2:SHORT:h12, feat_ext_vs_ma_50:2:SHORT:h15, feat_ext_vs_ma_50:2:SHORT:h20, feat_ext_vs_ma_50:2:SHORT:h24, feat_funding_cum_24:1:SHORT:h12, feat_funding_cum_24:1:SHORT:h15, feat_funding_cum_24:1:SHORT:h20, feat_funding_cum_24:1:SHORT:h24, feat_funding_cum_24:2:SHORT:h12, feat_funding_cum_24:2:SHORT:h15, feat_funding_cum_24:2:SHORT:h20, feat_funding_cum_24:2:SHORT:h24, feat_funding_cum_24@oi_hi:2:SHORT:h12, feat_funding_cum_24@oi_hi:2:SHORT:h15, feat_funding_cum_24@oi_hi:2:SHORT:h20, feat_funding_cum_24@oi_hi:2:SHORT:h24, feat_funding_cum_24@oi_lo:1:SHORT:h12, feat_funding_cum_24@oi_lo:1:SHORT:h15, feat_funding_cum_24@oi_lo:1:SHORT:h20, feat_funding_cum_24@oi_lo:1:SHORT:h24, feat_funding_cum_24@oi_lo:2:SHORT:h12, feat_funding_cum_24@oi_lo:2:SHORT:h15, feat_funding_cum_24@oi_lo:2:SHORT:h20, feat_funding_cum_24@oi_lo:2:SHORT:h24, feat_funding_cum_24@oi_mid:2:SHORT:h12, feat_funding_cum_24@oi_mid:2:SHORT:h24, feat_funding_rate:1:SHORT:h12, feat_funding_rate:1:SHORT:h15, feat_funding_rate:1:SHORT:h24, feat_funding_rate:2:SHORT:h12, feat_funding_rate:2:SHORT:h15, feat_funding_rate:2:SHORT:h20, feat_funding_rate:2:SHORT:h24, feat_funding_rate@oi_hi:2:SHORT:h15, feat_funding_rate@oi_hi:2:SHORT:h20, feat_funding_rate@oi_hi:2:SHORT:h24, feat_funding_rate@oi_lo:1:SHORT:h12, feat_funding_rate@oi_lo:1:SHORT:h15, feat_funding_rate@oi_lo:1:SHORT:h20, feat_funding_rate@oi_lo:1:SHORT:h24, feat_funding_rate@oi_lo:2:SHORT:h12, feat_funding_rate@oi_lo:2:SHORT:h20, feat_funding_rate@oi_lo:2:SHORT:h24, feat_funding_rate@oi_mid:2:SHORT:h12, feat_funding_rate@oi_mid:2:SHORT:h15, feat_funding_rate@oi_mid:2:SHORT:h20, feat_funding_rate@oi_mid:2:SHORT:h24, feat_gap:0:SHORT:h20, feat_gap:0:SHORT:h24, feat_gap:1:SHORT:h24, feat_gap_fill_ratio:1:SHORT:h15, feat_gap_fill_ratio:1:SHORT:h20, feat_gap_fill_ratio:1:SHORT:h24, feat_hl_range:1:SHORT:h15, feat_hl_range:1:SHORT:h20, feat_hl_range:1:SHORT:h24, feat_intraday_mom:1:SHORT:h24, feat_intraday_mom:2:SHORT:h20, feat_intraday_mom:2:SHORT:h24, feat_kc_width:1:SHORT:h12, feat_kc_width:1:SHORT:h15, feat_kc_width:1:SHORT:h20, feat_kc_width:1:SHORT:h24, feat_keltner_pos:2:SHORT:h12, feat_keltner_pos:2:SHORT:h15, feat_keltner_pos:2:SHORT:h20, feat_keltner_pos:2:SHORT:h24, feat_macd_12_26:2:SHORT:h12, feat_macd_12_26:2:SHORT:h15, feat_macd_12_26:2:SHORT:h20, feat_macd_12_26:2:SHORT:h24, feat_mean_rev_strength:0:SHORT:h12, feat_mean_rev_strength:0:SHORT:h15, feat_mean_rev_strength:0:SHORT:h20, feat_mean_rev_strength:0:SHORT:h24, feat_oi_chg_24:1:SHORT:h12, feat_oi_chg_24:1:SHORT:h15, feat_oi_chg_24:1:SHORT:h20, feat_oi_chg_24:1:SHORT:h24, feat_oi_chg_24:2:SHORT:h12, feat_oi_chg_24:2:SHORT:h15, feat_oi_chg_24:2:SHORT:h20, feat_oi_chg_24:2:SHORT:h24, feat_oi_chg_24@oi_hi:2:SHORT:h12, feat_oi_chg_24@oi_hi:2:SHORT:h15, feat_oi_chg_24@oi_hi:2:SHORT:h20, feat_oi_chg_24@oi_hi:2:SHORT:h24, feat_oi_chg_24@oi_lo:0:SHORT:h12, feat_oi_chg_24@oi_lo:0:SHORT:h15, feat_oi_chg_24@oi_lo:0:SHORT:h20, feat_oi_chg_24@oi_lo:0:SHORT:h24, feat_oi_chg_24@oi_lo:1:SHORT:h12, feat_oi_chg_24@oi_lo:1:SHORT:h15, feat_oi_chg_24@oi_lo:1:SHORT:h20, feat_oi_chg_24@oi_lo:1:SHORT:h24, feat_oi_chg_24@oi_lo:2:SHORT:h12, feat_oi_chg_24@oi_lo:2:SHORT:h15, feat_oi_chg_24@oi_lo:2:SHORT:h20, feat_oi_chg_24@oi_lo:2:SHORT:h24, feat_oi_chg_24@oi_mid:2:SHORT:h12, feat_oi_chg_24@oi_mid:2:SHORT:h15, feat_oi_ret_div:0:SHORT:h12, feat_oi_ret_div:0:SHORT:h15, feat_oi_ret_div:0:SHORT:h20, feat_oi_ret_div:0:SHORT:h24, feat_oi_ret_div:1:SHORT:h12, feat_oi_ret_div:1:SHORT:h15, feat_oi_ret_div:1:SHORT:h20, feat_oi_ret_div:1:SHORT:h24, feat_oi_ret_div@oi_lo:0:SHORT:h12, feat_oi_ret_div@oi_lo:0:SHORT:h15, feat_oi_ret_div@oi_lo:0:SHORT:h20, feat_oi_ret_div@oi_lo:0:SHORT:h24, feat_oi_ret_div@oi_lo:1:SHORT:h12, feat_oi_ret_div@oi_lo:1:SHORT:h15, feat_oi_ret_div@oi_lo:1:SHORT:h20, feat_oi_ret_div@oi_lo:1:SHORT:h24, feat_oi_ret_div@oi_lo:2:SHORT:h12, feat_oi_ret_div@oi_lo:2:SHORT:h15, feat_oi_ret_div@oi_lo:2:SHORT:h20, feat_oi_ret_div@oi_lo:2:SHORT:h24, feat_overnight_ret:0:SHORT:h24, feat_premium:1:SHORT:h12, feat_premium:1:SHORT:h15, feat_premium:1:SHORT:h20, feat_premium:2:SHORT:h12, feat_premium:2:SHORT:h15, feat_premium:2:SHORT:h20, feat_premium:2:SHORT:h24, feat_premium@oi_hi:2:SHORT:h12, feat_premium@oi_hi:2:SHORT:h15, feat_premium@oi_hi:2:SHORT:h20, feat_premium@oi_hi:2:SHORT:h24, feat_premium@oi_lo:1:SHORT:h20, feat_premium@oi_lo:1:SHORT:h24, feat_premium@oi_lo:2:SHORT:h12, feat_premium@oi_lo:2:SHORT:h15, feat_premium@oi_lo:2:SHORT:h20, feat_premium@oi_lo:2:SHORT:h24, feat_price_accel:1:SHORT:h24, feat_range_expansion:1:SHORT:h24, feat_range_pos_20:2:SHORT:h12, feat_range_pos_20:2:SHORT:h15, feat_range_pos_20:2:SHORT:h20, feat_range_pos_20:2:SHORT:h24, feat_range_pos_50:2:SHORT:h12, feat_range_pos_50:2:SHORT:h15, feat_range_pos_50:2:SHORT:h20, feat_range_pos_50:2:SHORT:h24, feat_realized_vol_20:0:SHORT:h12, feat_realized_vol_20:0:SHORT:h15, feat_realized_vol_20:0:SHORT:h20, feat_realized_vol_20:0:SHORT:h24, feat_realized_vol_20:1:SHORT:h12, feat_realized_vol_20:1:SHORT:h15, feat_realized_vol_20:1:SHORT:h20, feat_realized_vol_20:1:SHORT:h24, feat_ret_10:2:SHORT:h12, feat_ret_10:2:SHORT:h15, feat_ret_10:2:SHORT:h20, feat_ret_10:2:SHORT:h24, feat_ret_1:2:SHORT:h20, feat_ret_1:2:SHORT:h24, feat_ret_20:1:SHORT:h24, feat_ret_20:2:SHORT:h12, feat_ret_20:2:SHORT:h15, feat_ret_20:2:SHORT:h20, feat_ret_20:2:SHORT:h24, feat_ret_3:2:SHORT:h15, feat_ret_3:2:SHORT:h20, feat_ret_autocorr:1:SHORT:h15, feat_ret_autocorr:1:SHORT:h20, feat_ret_autocorr:1:SHORT:h24, feat_ret_autocorr:2:SHORT:h12, feat_ret_autocorr:2:SHORT:h15, feat_ret_autocorr:2:SHORT:h20, feat_ret_sign_streak:1:SHORT:h20, feat_ret_sign_streak:1:SHORT:h24, feat_ret_sign_streak:2:SHORT:h12, feat_ret_sign_streak:2:SHORT:h15, feat_ret_sign_streak:2:SHORT:h20, feat_ret_sign_streak:2:SHORT:h24, feat_ret_vol:2:SHORT:h12, feat_ret_vol:2:SHORT:h15, feat_ret_vol:2:SHORT:h20, feat_ret_vol:2:SHORT:h24, feat_rsi_14:2:SHORT:h12, feat_rsi_14:2:SHORT:h15, feat_rsi_14:2:SHORT:h20, feat_rsi_14:2:SHORT:h24, feat_rsi_21:2:SHORT:h12, feat_rsi_21:2:SHORT:h15, feat_rsi_21:2:SHORT:h20, feat_rsi_21:2:SHORT:h24, feat_rsi_7:1:SHORT:h24, feat_rsi_7:2:SHORT:h15, feat_rsi_divergence:1:SHORT:h24, feat_session_mom:1:SHORT:h24, feat_session_mom:2:SHORT:h20, feat_session_mom:2:SHORT:h24, feat_squeeze:1:SHORT:h12, feat_squeeze:1:SHORT:h15, feat_squeeze:1:SHORT:h20, feat_squeeze:1:SHORT:h24, feat_stoch_d_14:2:SHORT:h12, feat_stoch_d_14:2:SHORT:h15, feat_stoch_d_14:2:SHORT:h20, feat_stoch_d_14:2:SHORT:h24, feat_stoch_k_14:2:SHORT:h12, feat_stoch_k_14:2:SHORT:h15, feat_stoch_k_14:2:SHORT:h20, feat_stoch_k_14:2:SHORT:h24, feat_time_since_high_20:0:SHORT:h12, feat_time_since_high_20:0:SHORT:h15, feat_time_since_high_20:0:SHORT:h20, feat_time_since_high_20:0:SHORT:h24, feat_time_since_low_20:1:SHORT:h12, feat_time_since_low_20:1:SHORT:h15, feat_time_since_low_20:1:SHORT:h20, feat_time_since_low_20:1:SHORT:h24, feat_trend_neutral:0:SHORT:h24, feat_trend_slope_20:2:SHORT:h12, feat_trend_slope_20:2:SHORT:h15, feat_trend_slope_20:2:SHORT:h20, feat_trend_slope_20:2:SHORT:h24, feat_trend_strength_20:1:SHORT:h24, feat_trend_strength_20:2:SHORT:h20, feat_trend_strength_20:2:SHORT:h24, feat_vol_breakout:2:SHORT:h12, feat_vol_breakout:2:SHORT:h15, feat_vol_breakout:2:SHORT:h20, feat_vol_breakout:2:SHORT:h24, feat_vol_breakout_strength:1:SHORT:h24, feat_vol_contraction:2:SHORT:h20, feat_vol_contraction:2:SHORT:h24, feat_vol_of_vol:0:SHORT:h20, feat_vol_of_vol:0:SHORT:h24, feat_vol_of_vol:1:SHORT:h24, feat_vol_regime:2:SHORT:h20, feat_vol_regime:2:SHORT:h24, feat_vol_roc_20:1:SHORT:h20, feat_vol_roc_20:1:SHORT:h24, feat_vol_sma_ratio:1:SHORT:h20, feat_vol_sma_ratio:1:SHORT:h24, feat_vol_trend:2:SHORT:h12, feat_vol_trend:2:SHORT:h15, feat_vol_trend:2:SHORT:h20, feat_vol_trend:2:SHORT:h24, feat_vwap_dist:2:SHORT:h12, feat_vwap_dist:2:SHORT:h15, feat_vwap_dist:2:SHORT:h20, feat_vwap_dist:2:SHORT:h24, feat_vwap_lower_dist:1:SHORT:h15, feat_vwap_lower_dist:1:SHORT:h20, feat_vwap_upper_dist:2:SHORT:h12, feat_vwap_upper_dist:2:SHORT:h15, feat_vwap_upper_dist:2:SHORT:h20, feat_vwap_upper_dist:2:SHORT:h24, feat_williams_r_14:0:SHORT:h12, feat_williams_r_14:0:SHORT:h15, feat_williams_r_14:0:SHORT:h20, feat_williams_r_14:0:SHORT:h24, feat_zscore_20:1:SHORT:h24, feat_zscore_20:2:SHORT:h12, feat_zscore_20:2:SHORT:h15, feat_zscore_20:2:SHORT:h20, feat_zscore_20:2:SHORT:h24
- Armable pairs: AAVEUSDC, BTCUSDC, ENAUSDC, ETHUSDC, HYPEUSDC, KPEPEUSDC, LITUSDC, NEARUSDC, PUMPUSDC, SOLUSDC, WLDUSDC, XMRUSDC, XPLUSDC, XRPUSDC, ZECUSDC
  - `feat_funding_rate@oi_lo:2:SHORT:h15` edge=239.7b n=184 breadth=4 validated=False prov=False armable=False (too_few_rows)
  - `feat_funding_rate@oi_mid:2:SHORT:h24` edge=215.6b n=522 breadth=8 validated=True prov=False armable=True (ok)
  - `feat_oi_chg_24@oi_lo:1:SHORT:h24` edge=195.4b n=417 breadth=13 validated=True prov=False armable=True (ok)
  - `feat_funding_rate@oi_mid:2:SHORT:h20` edge=190.3b n=476 breadth=8 validated=True prov=False armable=True (ok)
  - `feat_oi_ret_div@oi_lo:0:SHORT:h24` edge=188.0b n=464 breadth=13 validated=False prov=False armable=True (ok)
  - `feat_funding_rate@oi_lo:2:SHORT:h24` edge=164.9b n=357 breadth=6 validated=False prov=False armable=True (ok)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-9.15 | frozen=YES
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3, native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 23
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
  - `feat_price_roc_5:1:LONG:h24` pnl=+0.70
  - `feat_realized_vol_20:2:LONG:h12` pnl=+0.61
  - `feat_ret_10:2:LONG:h19` pnl=+14.58
  - `feat_ret_20:2:LONG:h14` pnl=+13.42
  - `feat_rsi_divergence:2:LONG:h20` pnl=+8.36
  - `feat_trend_slope_20:2:LONG:h12` pnl=+11.12
  - `feat_vwap_upper_dist:2:SHORT:h24` pnl=+12.06
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **93/93** | hip3 **19/21**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 46
  - `feat_adx_14:2:LONG:h12` lane_not_green
  - `feat_adx_14:2:LONG:h15` lane_not_green
  - `feat_atr_norm_ext:2:LONG:h13` lane_not_green
  - `feat_atr_percent:2:LONG:h12` lane_not_green
  - `feat_atr_ratio:0:LONG:h24` lane_not_green
  - `feat_bb_squeeze_20:2:LONG:h20` lane_not_green
  - `feat_bb_width_20:2:LONG:h15` lane_not_green
  - `feat_buy_vol_ratio:2:LONG:h24` lane_not_green
  - `feat_cci_20:0:LONG:h24` lane_not_green
  - `feat_cci_20:2:SHORT:h24` lane_not_green
  - `feat_donchian_break:2:LONG:h15` lane_not_green
  - `feat_ema_cross_10_20:2:LONG:h12` lane_not_green
  - `feat_ema_cross_10_20:2:SHORT:h24` lane_not_green
  - `feat_ext_vs_ma_50:0:LONG:h20` lane_not_green
  - `feat_funding_rate:2:SHORT:h12` lane_not_green
  - `feat_hour_utc:2:LONG:h15` lane_not_green
  - `feat_kc_width:2:LONG:h12` lane_not_green
  - `feat_kc_width:2:LONG:h15` lane_not_green
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
  - `feat_time_since_high_20:0:LONG:h12` lane_not_green
  - `feat_trend_slope_20:2:SHORT:h24` lane_not_green
  - `feat_vol_breakout:2:LONG:h15` lane_not_green
  - `feat_vol_of_vol:1:LONG:h24` lane_not_green
  - `feat_vol_of_vol:2:LONG:h12` lane_not_green
  - `feat_vol_of_vol:2:LONG:h15` lane_not_green
  - `feat_vol_sma_ratio:0:LONG:h24` lane_not_green
  - `feat_vol_trend:0:LONG:h24` lane_not_green
  - `feat_williams_r_14:0:SHORT:h24` lane_not_green
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` lane_not_green
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-11-03T08:13:06: errors=3 signals=48 regime_blocked=100
- this cycle: closed=0 new_signals=48 skipped=48 slot_full=0 slice_full=0 pair_held=0
- Action funnel: regime_blocked=100 | lane_gate_blocked=2 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=0 | cluster_cap=0 | family_vetoed=0 | slot_full=0 | skipped=48
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "cluster_cap": 0, "family_vetoed": 0, "lane_gate_blocked": 2, "pair_held": 0, "regime_blocked": 100, "skipped": 48, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=False hip3_green=False frozen=hip3,native islands=23 blocks=46
- aggregate_risk: ok open=0.0000 cap=160.8295 used=0.0107 remaining=159.1089 replayed=12 no_new_bars=0
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:BOT"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:GME"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:USAR"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
