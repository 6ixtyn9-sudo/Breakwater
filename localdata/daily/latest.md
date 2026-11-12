# Breakwater daily print — 2026-11-12 17:09 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **377.39 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2351.02 ZAR** (seed 2000) | lifetime: **+351.02 ZAR** | closed: 581
- Today: 3 closed, **+0.57 ZAR**
- 7d: **+72.49 ZAR** | 30d: **+16.74 ZAR**

## 2b. Claimed vs realised

- Book: 75 slices (native 55 | hip3 20); validated pools: native 174 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 75 book slices present in the validated pools): +0.328% | at 147.30 ZAR mean notional/trade: +0.48 ZAR/trade
- Realised (581 real closes per lane_gate._is_real_close, net of fees): +0.60 ZAR/trade | sd 4.69 | SE 0.19
- Gap: +0.12 ZAR/trade | t = +0.62 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.364% over 55/55 slices (pool 174) ~ +0.53 ZAR | realised 535 closes +0.74 ZAR sd 4.66 SE 0.20 | gap +0.21 t +1.04 | NOT ESTABLISHED
- hip3: claimed median +0.062% over 20/20 slices (pool 160) ~ +0.10 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.07 t -1.51 | NOT ESTABLISHED
- Ledger: 699 decision rows; 581 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 118 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 535 | wins: 271 | win%: 50.7 | P&L: **+395.53 ZAR** | today: +0.57 | 7d: +72.49 | 30d: +16.74
- By exit: target +516.3, trail_stop +212.4, horizon +79.6, max_bars +2.8, regime_shift -11.9, stop -403.6
- By entry regime (n/pnl): neutral 213/+234.4, bull 122/+199.3, bear 200/-38.1
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_trend_neutral:0:SHORT:h24 5n/5w +24.80; feat_premium@oi_hi:2:SHORT:h24 3n/3w +24.15; feat_ext_strength:2:LONG:h15 12n/8w +24.00
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_macd_12_26:2:SHORT:h15 3n/0w -11.55; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; ENAUSDC 7n +23.48; XRPZAR 2n +18.07; SOLUSDC 65n +17.29
- Worst pairs: UNIUSDC 13n -30.75; ZECUSDC 17n -21.96; ETHZAR 4n -14.36; DOGEUSDC 15n -11.90; HYPEUSDC 39n -9.14

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 4 open, stop-risk **14.75 ZAR**
  - HYPEUSDC SELL ntl=120 risk=4.45 bars=4 stop=73.85075000000000675 peak=71.813
  - XRPUSDC SELL ntl=120 risk=3.75 bars=0 stop=1.0692500000000000335 peak=1.0368
  - SOLUSDC SELL ntl=120 risk=3.74 bars=1 stop=85.03049999999999680 peak=82.731
  - ETHUSDC SELL ntl=120 risk=2.81 bars=2 stop=2092.0750000000000015 peak=2046.3

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **14.75 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **14.75 / 167.92 ZAR | 9.5% | ok**
- Remaining: 151.9709 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 55, "skipped": 55, "slice_full": 0, "slot_full": 0}, "native": {"cluster_cap": 22, "lane_gate_blocked": 0, "opened": 1, "pair_held": 35, "signals": 96, "skipped": 38, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **HYPEUSDC** 4.4501 ZAR
- positions without bars: 0 | replayed: 3 | invalid: 0

## 6. Monitored books

- Native: 55 | HIP-3: 20
- Native top (by paper P&L):
  - `feat_premium@oi_hi:2:SHORT:h24` edge=0.0054 n=2425 p=0.2278 src=validated_walk_forward unproven=False paper=3n/+24.15
  - `feat_ret_autocorr:2:SHORT:h24` edge=0.0073 n=8711 p=0.2478 src=validated_walk_forward unproven=False paper=5n/+8.20
  - `feat_vol_sma_ratio:1:SHORT:h24` edge=0.0034 n=8458 p=0.7064 src=validated_walk_forward unproven=False paper=1n/+3.25
  - `feat_overnight_ret:0:SHORT:h24` edge=0.0038 n=10957 p=0.6320 src=validated_walk_forward unproven=False paper=1n/+1.06
  - `feat_ext_strength:2:SHORT:h24` edge=0.0076 n=10243 p=0.2881 src=validated_walk_forward unproven=False paper=2n/+0.89
  - `feat_oi_chg_24@oi_mid:2:SHORT:h12` edge=0.0068 n=1054 p=0.1741 src=validated_walk_forward unproven=False paper=1n/+0.85
  - `feat_gap:0:SHORT:h24` edge=0.0040 n=11170 p=0.7587 src=validated_walk_forward unproven=False paper=1n/+0.78
  - `feat_vol_breakout:2:SHORT:h24` edge=0.0078 n=9698 p=0.2596 src=validated_walk_forward unproven=False paper=1n/+0.51
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

- Latest research: 2026-11-12T00:31:01.295767+00:00 | discovered 2240 | validated 174 | reg-confounded 983 | hostile-unproven 4
- floors: "" | book: {"rows": 62, "by_status": {"monitored": 55, "decayed": 6, "cooldown": 1}, "in_validated_pool": 62, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=1120 validated=1120 passing=172 eligible=248 best=335.8b best_fail=temporal_pass,breadth_ok
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=576 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_stoch_k_14:L2S0:h20: mean=-11.2b t_no=2.15 folds=11010 mkt_corr=-0.28 dd=136b legs=9.6/9.8 fail=n_nonoverlap,mean<=0,folds
  - feat_williams_r_14:L0S2:h20: mean=-11.3b t_no=2.15 folds=11010 mkt_corr=-0.28 dd=136b legs=9.6/9.8 fail=n_nonoverlap,mean<=0,folds
  - feat_vol_trend:L2S0:h12: mean=+6.7b t_no=1.98 folds=11011 mkt_corr=-0.21 dd=165b legs=14.2/12.7 fail=t_nonoverlap
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

- Label: **bear** | breadth bear=0.8667 bull=0.0 neutral=0.1333 | symbols=15
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 14 / bull 0
- as_of: 2026-11-12T15:39:52Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 1120 | eligible: 649 | observations: 2003 | armable: **1481**
- Armable slices: feat_adx_14:0:SHORT:h15, feat_adx_14:0:SHORT:h20, feat_adx_14:0:SHORT:h24, feat_adx_14:1:SHORT:h12, feat_adx_14:1:SHORT:h15, feat_adx_14:2:SHORT:h24, feat_asia_range:0:SHORT:h20, feat_asia_range:0:SHORT:h24, feat_asia_vol:0:SHORT:h20, feat_asia_vol:0:SHORT:h24, feat_atr_norm_ext:1:SHORT:h15, feat_atr_norm_ext:2:SHORT:h12, feat_atr_norm_ext:2:SHORT:h15, feat_atr_norm_ext:2:SHORT:h20, feat_atr_norm_ext:2:SHORT:h24, feat_atr_ratio:0:SHORT:h12, feat_atr_ratio:0:SHORT:h15, feat_atr_ratio:0:SHORT:h20, feat_atr_ratio:1:SHORT:h15, feat_atr_ratio:1:SHORT:h24, feat_bb_pos_20:2:SHORT:h12, feat_bb_pos_20:2:SHORT:h15, feat_bb_pos_20:2:SHORT:h20, feat_bb_pos_20:2:SHORT:h24, feat_bb_squeeze_20:0:SHORT:h12, feat_bb_squeeze_20:0:SHORT:h15, feat_bb_squeeze_20:1:SHORT:h24, feat_bb_squeeze_20:2:SHORT:h24, feat_bb_width_20:1:SHORT:h15, feat_bb_width_20:1:SHORT:h20, feat_bb_width_20:2:SHORT:h24, feat_book_imb_5:0:SHORT:h24, feat_book_imb_5:1:SHORT:h15, feat_book_imb_5:1:SHORT:h20, feat_book_imb_5:1:SHORT:h24, feat_book_imb_5:2:SHORT:h24, feat_book_imb_5@oi_hi:0:SHORT:h24, feat_book_imb_5@oi_hi:1:SHORT:h15, feat_book_imb_5@oi_hi:1:SHORT:h20, feat_book_imb_5@oi_hi:1:SHORT:h24, feat_book_imb_5@oi_lo:0:SHORT:h15, feat_book_imb_5@oi_lo:0:SHORT:h20, feat_book_imb_5@oi_lo:0:SHORT:h24, feat_book_imb_5@oi_lo:1:SHORT:h12, feat_book_imb_5@oi_lo:1:SHORT:h15, feat_book_imb_5@oi_lo:1:SHORT:h20, feat_book_imb_5@oi_lo:1:SHORT:h24, feat_book_imb_5@oi_mid:2:SHORT:h24, feat_buy_vol_ratio:0:SHORT:h24, feat_buy_vol_ratio:1:SHORT:h20, feat_buy_vol_ratio:1:SHORT:h24, feat_buy_vol_ratio:2:SHORT:h20, feat_buy_vol_ratio:2:SHORT:h24, feat_cci_20:2:SHORT:h12, feat_cci_20:2:SHORT:h15, feat_cci_20:2:SHORT:h20, feat_cci_20:2:SHORT:h24, feat_close_pos_ma:1:SHORT:h15, feat_close_pos_ma:1:SHORT:h20, feat_close_pos_ma:1:SHORT:h24, feat_close_pos_ma:2:SHORT:h12, feat_close_pos_ma:2:SHORT:h15, feat_close_pos_ma:2:SHORT:h20, feat_close_pos_ma:2:SHORT:h24, feat_close_position:0:SHORT:h24, feat_close_position:1:SHORT:h20, feat_close_position:1:SHORT:h24, feat_close_position:2:SHORT:h20, feat_close_position:2:SHORT:h24, feat_donchian_break:1:SHORT:h15, feat_donchian_break:1:SHORT:h20, feat_donchian_break:1:SHORT:h24, feat_donchian_break:2:SHORT:h12, feat_donchian_break:2:SHORT:h15, feat_donchian_break:2:SHORT:h20, feat_donchian_break:2:SHORT:h24, feat_donchian_width_20:0:SHORT:h12, feat_donchian_width_20:0:SHORT:h15, feat_donchian_width_20:1:SHORT:h20, feat_donchian_width_20:1:SHORT:h24, feat_donchian_width_20:2:SHORT:h24, feat_ema_cross_10_20:1:SHORT:h12, feat_ema_cross_10_20:1:SHORT:h15, feat_ema_cross_10_20:1:SHORT:h20, feat_ema_cross_10_20:1:SHORT:h24, feat_ema_cross_10_20:2:SHORT:h12, feat_ema_cross_10_20:2:SHORT:h15, feat_ema_cross_10_20:2:SHORT:h20, feat_ema_cross_10_20:2:SHORT:h24, feat_ext_strength:2:SHORT:h15, feat_ext_strength:2:SHORT:h20, feat_ext_strength:2:SHORT:h24, feat_ext_vs_ma_10:2:SHORT:h12, feat_ext_vs_ma_10:2:SHORT:h15, feat_ext_vs_ma_10:2:SHORT:h20, feat_ext_vs_ma_10:2:SHORT:h24, feat_ext_vs_ma_20:2:SHORT:h12, feat_ext_vs_ma_20:2:SHORT:h15, feat_ext_vs_ma_20:2:SHORT:h20, feat_ext_vs_ma_20:2:SHORT:h24, feat_ext_vs_ma_50:1:SHORT:h12, feat_ext_vs_ma_50:1:SHORT:h15, feat_ext_vs_ma_50:1:SHORT:h20, feat_ext_vs_ma_50:1:SHORT:h24, feat_ext_vs_ma_50:2:SHORT:h12, feat_ext_vs_ma_50:2:SHORT:h15, feat_ext_vs_ma_50:2:SHORT:h20, feat_ext_vs_ma_50:2:SHORT:h24, feat_funding_cum_24:1:SHORT:h24, feat_funding_cum_24:2:SHORT:h12, feat_funding_cum_24:2:SHORT:h15, feat_funding_cum_24:2:SHORT:h20, feat_funding_cum_24:2:SHORT:h24, feat_funding_cum_24@oi_hi:2:SHORT:h12, feat_funding_cum_24@oi_hi:2:SHORT:h15, feat_funding_cum_24@oi_hi:2:SHORT:h20, feat_funding_cum_24@oi_hi:2:SHORT:h24, feat_funding_cum_24@oi_lo:1:SHORT:h24, feat_funding_cum_24@oi_lo:2:SHORT:h12, feat_funding_cum_24@oi_lo:2:SHORT:h15, feat_funding_cum_24@oi_mid:0:SHORT:h20, feat_funding_cum_24@oi_mid:1:SHORT:h12, feat_funding_cum_24@oi_mid:1:SHORT:h15, feat_funding_cum_24@oi_mid:1:SHORT:h20, feat_funding_cum_24@oi_mid:1:SHORT:h24, feat_funding_rate:0:SHORT:h24, feat_funding_rate:2:SHORT:h12, feat_funding_rate:2:SHORT:h15, feat_funding_rate:2:SHORT:h20, feat_funding_rate:2:SHORT:h24, feat_funding_rate@oi_hi:1:SHORT:h15, feat_funding_rate@oi_hi:1:SHORT:h20, feat_funding_rate@oi_hi:1:SHORT:h24, feat_funding_rate@oi_hi:2:SHORT:h15, feat_funding_rate@oi_hi:2:SHORT:h20, feat_funding_rate@oi_hi:2:SHORT:h24, feat_funding_rate@oi_lo:0:SHORT:h20, feat_funding_rate@oi_mid:0:SHORT:h15, feat_funding_rate@oi_mid:0:SHORT:h20, feat_funding_rate@oi_mid:0:SHORT:h24, feat_funding_rate@oi_mid:2:SHORT:h15, feat_gap:0:SHORT:h15, feat_gap:0:SHORT:h20, feat_gap:0:SHORT:h24, feat_gap:1:SHORT:h20, feat_gap:1:SHORT:h24, feat_gap_fill_ratio:0:SHORT:h20, feat_gap_fill_ratio:0:SHORT:h24, feat_gap_fill_ratio:1:SHORT:h12, feat_gap_fill_ratio:1:SHORT:h15, feat_gap_fill_ratio:1:SHORT:h24, feat_hl_range:1:SHORT:h15, feat_hl_range:1:SHORT:h20, feat_hl_range:1:SHORT:h24, feat_intraday_mom:1:SHORT:h12, feat_intraday_mom:1:SHORT:h15, feat_intraday_mom:1:SHORT:h20, feat_intraday_mom:1:SHORT:h24, feat_intraday_mom:2:SHORT:h15, feat_intraday_mom:2:SHORT:h20, feat_intraday_mom:2:SHORT:h24, feat_keltner_pos:2:SHORT:h12, feat_keltner_pos:2:SHORT:h15, feat_keltner_pos:2:SHORT:h20, feat_keltner_pos:2:SHORT:h24, feat_macd_12_26:2:SHORT:h12, feat_macd_12_26:2:SHORT:h15, feat_macd_12_26:2:SHORT:h20, feat_macd_12_26:2:SHORT:h24, feat_mean_rev_strength:0:SHORT:h12, feat_mean_rev_strength:0:SHORT:h15, feat_mean_rev_strength:0:SHORT:h20, feat_mean_rev_strength:0:SHORT:h24, feat_oi_chg_24:1:SHORT:h12, feat_oi_chg_24:1:SHORT:h15, feat_oi_chg_24:1:SHORT:h20, feat_oi_chg_24:1:SHORT:h24, feat_oi_chg_24:2:SHORT:h12, feat_oi_chg_24:2:SHORT:h15, feat_oi_chg_24:2:SHORT:h20, feat_oi_chg_24@oi_hi:1:SHORT:h12, feat_oi_chg_24@oi_hi:1:SHORT:h15, feat_oi_chg_24@oi_hi:1:SHORT:h20, feat_oi_chg_24@oi_hi:1:SHORT:h24, feat_oi_chg_24@oi_hi:2:SHORT:h12, feat_oi_chg_24@oi_hi:2:SHORT:h15, feat_oi_chg_24@oi_hi:2:SHORT:h20, feat_oi_chg_24@oi_hi:2:SHORT:h24, feat_oi_chg_24@oi_lo:0:SHORT:h15, feat_oi_chg_24@oi_lo:0:SHORT:h20, feat_oi_chg_24@oi_lo:0:SHORT:h24, feat_oi_chg_24@oi_lo:1:SHORT:h12, feat_oi_chg_24@oi_lo:1:SHORT:h15, feat_oi_chg_24@oi_lo:1:SHORT:h20, feat_oi_chg_24@oi_lo:1:SHORT:h24, feat_oi_chg_24@oi_lo:2:SHORT:h15, feat_oi_chg_24@oi_lo:2:SHORT:h20, feat_oi_chg_24@oi_mid:2:SHORT:h12, feat_oi_chg_24@oi_mid:2:SHORT:h15, feat_oi_chg_24@oi_mid:2:SHORT:h24, feat_oi_ret_div:0:SHORT:h12, feat_oi_ret_div:0:SHORT:h15, feat_oi_ret_div:0:SHORT:h20, feat_oi_ret_div:0:SHORT:h24, feat_oi_ret_div:1:SHORT:h20, feat_oi_ret_div:1:SHORT:h24, feat_oi_ret_div:2:SHORT:h24, feat_oi_ret_div@oi_hi:0:SHORT:h12, feat_oi_ret_div@oi_hi:0:SHORT:h15, feat_oi_ret_div@oi_hi:0:SHORT:h20, feat_oi_ret_div@oi_hi:0:SHORT:h24, feat_oi_ret_div@oi_lo:0:SHORT:h12, feat_oi_ret_div@oi_lo:0:SHORT:h15, feat_oi_ret_div@oi_lo:0:SHORT:h20, feat_oi_ret_div@oi_lo:0:SHORT:h24, feat_oi_ret_div@oi_lo:1:SHORT:h12, feat_oi_ret_div@oi_lo:1:SHORT:h15, feat_oi_ret_div@oi_lo:1:SHORT:h20, feat_oi_ret_div@oi_lo:1:SHORT:h24, feat_oi_ret_div@oi_lo:2:SHORT:h20, feat_overnight_ret:0:SHORT:h15, feat_overnight_ret:0:SHORT:h20, feat_overnight_ret:0:SHORT:h24, feat_overnight_ret:1:SHORT:h15, feat_overnight_ret:1:SHORT:h20, feat_premium:1:SHORT:h20, feat_premium:1:SHORT:h24, feat_premium:2:SHORT:h12, feat_premium:2:SHORT:h15, feat_premium:2:SHORT:h20, feat_premium:2:SHORT:h24, feat_premium@oi_hi:2:SHORT:h12, feat_premium@oi_hi:2:SHORT:h15, feat_premium@oi_hi:2:SHORT:h20, feat_premium@oi_hi:2:SHORT:h24, feat_premium@oi_lo:0:SHORT:h24, feat_premium@oi_lo:1:SHORT:h20, feat_premium@oi_mid:1:SHORT:h15, feat_premium@oi_mid:1:SHORT:h20, feat_premium@oi_mid:1:SHORT:h24, feat_premium@oi_mid:2:SHORT:h12, feat_premium@oi_mid:2:SHORT:h15, feat_price_accel:0:SHORT:h24, feat_price_accel:1:SHORT:h20, feat_price_accel:2:SHORT:h20, feat_price_accel:2:SHORT:h24, feat_price_roc_5:2:SHORT:h12, feat_price_roc_5:2:SHORT:h15, feat_price_roc_5:2:SHORT:h20, feat_price_roc_5:2:SHORT:h24, feat_range_expansion:1:SHORT:h20, feat_range_expansion:1:SHORT:h24, feat_range_expansion:2:SHORT:h24, feat_range_pos_20:2:SHORT:h12, feat_range_pos_20:2:SHORT:h15, feat_range_pos_20:2:SHORT:h20, feat_range_pos_20:2:SHORT:h24, feat_range_pos_50:1:SHORT:h15, feat_range_pos_50:1:SHORT:h20, feat_range_pos_50:1:SHORT:h24, feat_range_pos_50:2:SHORT:h12, feat_range_pos_50:2:SHORT:h15, feat_range_pos_50:2:SHORT:h24, feat_realized_vol_20:1:SHORT:h20, feat_realized_vol_20:1:SHORT:h24, feat_ret_10:2:SHORT:h12, feat_ret_10:2:SHORT:h15, feat_ret_10:2:SHORT:h20, feat_ret_10:2:SHORT:h24, feat_ret_1:0:SHORT:h24, feat_ret_1:1:SHORT:h12, feat_ret_1:1:SHORT:h15, feat_ret_1:2:SHORT:h15, feat_ret_1:2:SHORT:h20, feat_ret_1:2:SHORT:h24, feat_ret_20:2:SHORT:h12, feat_ret_20:2:SHORT:h15, feat_ret_20:2:SHORT:h20, feat_ret_20:2:SHORT:h24, feat_ret_3:2:SHORT:h12, feat_ret_3:2:SHORT:h15, feat_ret_3:2:SHORT:h20, feat_ret_3:2:SHORT:h24, feat_ret_5:2:SHORT:h12, feat_ret_5:2:SHORT:h15, feat_ret_5:2:SHORT:h20, feat_ret_5:2:SHORT:h24, feat_ret_autocorr:1:SHORT:h20, feat_ret_autocorr:1:SHORT:h24, feat_ret_autocorr:2:SHORT:h12, feat_ret_autocorr:2:SHORT:h15, feat_ret_autocorr:2:SHORT:h20, feat_ret_autocorr:2:SHORT:h24, feat_ret_sign_streak:0:SHORT:h20, feat_ret_sign_streak:0:SHORT:h24, feat_ret_sign_streak:1:SHORT:h24, feat_ret_sign_streak:2:SHORT:h12, feat_ret_sign_streak:2:SHORT:h15, feat_ret_sign_streak:2:SHORT:h20, feat_ret_sign_streak:2:SHORT:h24, feat_ret_vol:1:SHORT:h12, feat_ret_vol:1:SHORT:h15, feat_ret_vol:2:SHORT:h12, feat_ret_vol:2:SHORT:h15, feat_ret_vol:2:SHORT:h20, feat_ret_vol:2:SHORT:h24, feat_rsi_14:2:SHORT:h12, feat_rsi_14:2:SHORT:h15, feat_rsi_14:2:SHORT:h20, feat_rsi_14:2:SHORT:h24, feat_rsi_21:2:SHORT:h12, feat_rsi_21:2:SHORT:h15, feat_rsi_21:2:SHORT:h20, feat_rsi_21:2:SHORT:h24, feat_rsi_7:2:SHORT:h12, feat_rsi_7:2:SHORT:h15, feat_rsi_7:2:SHORT:h20, feat_rsi_7:2:SHORT:h24, feat_rsi_divergence:0:SHORT:h15, feat_rsi_divergence:0:SHORT:h20, feat_rsi_divergence:0:SHORT:h24, feat_rsi_divergence:1:SHORT:h20, feat_rsi_divergence:1:SHORT:h24, feat_rsi_divergence:2:SHORT:h24, feat_session_mom:0:SHORT:h24, feat_session_mom:1:SHORT:h12, feat_session_mom:1:SHORT:h15, feat_session_mom:1:SHORT:h20, feat_session_mom:1:SHORT:h24, feat_session_mom:2:SHORT:h15, feat_session_mom:2:SHORT:h20, feat_session_mom:2:SHORT:h24, feat_squeeze:1:SHORT:h12, feat_squeeze:1:SHORT:h15, feat_squeeze:1:SHORT:h20, feat_squeeze:1:SHORT:h24, feat_squeeze:2:SHORT:h24, feat_stoch_d_14:2:SHORT:h12, feat_stoch_d_14:2:SHORT:h15, feat_stoch_d_14:2:SHORT:h20, feat_stoch_d_14:2:SHORT:h24, feat_stoch_k_14:2:SHORT:h12, feat_stoch_k_14:2:SHORT:h15, feat_stoch_k_14:2:SHORT:h20, feat_stoch_k_14:2:SHORT:h24, feat_time_since_high_20:0:SHORT:h20, feat_time_since_high_20:0:SHORT:h24, feat_time_since_high_20:1:SHORT:h20, feat_time_since_high_20:1:SHORT:h24, feat_time_since_low_20:1:SHORT:h12, feat_time_since_low_20:1:SHORT:h15, feat_time_since_low_20:1:SHORT:h20, feat_time_since_low_20:1:SHORT:h24, feat_trend_neutral:0:SHORT:h24, feat_trend_neutral:2:SHORT:h15, feat_trend_neutral:2:SHORT:h24, feat_trend_slope_20:1:SHORT:h12, feat_trend_slope_20:1:SHORT:h15, feat_trend_slope_20:1:SHORT:h24, feat_trend_slope_20:2:SHORT:h15, feat_trend_slope_20:2:SHORT:h20, feat_trend_slope_20:2:SHORT:h24, feat_trend_strength_20:0:SHORT:h24, feat_trend_strength_20:1:SHORT:h15, feat_trend_strength_20:1:SHORT:h20, feat_trend_strength_20:2:SHORT:h24, feat_vol_breakout:2:SHORT:h12, feat_vol_breakout:2:SHORT:h15, feat_vol_breakout:2:SHORT:h20, feat_vol_breakout:2:SHORT:h24, feat_vol_breakout_strength:0:SHORT:h12, feat_vol_breakout_strength:1:SHORT:h20, feat_vol_breakout_strength:1:SHORT:h24, feat_vol_contraction:0:SHORT:h12, feat_vol_contraction:0:SHORT:h15, feat_vol_contraction:0:SHORT:h20, feat_vol_contraction:0:SHORT:h24, feat_vol_of_vol:1:SHORT:h15, feat_vol_of_vol:1:SHORT:h20, feat_vol_of_vol:1:SHORT:h24, feat_vol_of_vol:2:SHORT:h24, feat_vol_regime:0:SHORT:h12, feat_vol_regime:0:SHORT:h15, feat_vol_regime:0:SHORT:h20, feat_vol_regime:0:SHORT:h24, feat_vol_roc_20:0:SHORT:h12, feat_vol_roc_20:0:SHORT:h15, feat_vol_roc_20:0:SHORT:h20, feat_vol_roc_20:0:SHORT:h24, feat_vol_roc_20:1:SHORT:h15, feat_vol_roc_20:1:SHORT:h20, feat_vol_roc_20:1:SHORT:h24, feat_vol_sma_ratio:1:SHORT:h20, feat_vol_sma_ratio:1:SHORT:h24, feat_vol_trend:1:SHORT:h15, feat_vol_trend:1:SHORT:h24, feat_vol_trend:2:SHORT:h15, feat_vol_trend:2:SHORT:h20, feat_vol_trend:2:SHORT:h24, feat_vwap_dist:2:SHORT:h12, feat_vwap_dist:2:SHORT:h15, feat_vwap_dist:2:SHORT:h20, feat_vwap_dist:2:SHORT:h24, feat_vwap_lower_dist:2:SHORT:h12, feat_vwap_lower_dist:2:SHORT:h15, feat_vwap_lower_dist:2:SHORT:h20, feat_vwap_lower_dist:2:SHORT:h24, feat_vwap_upper_dist:2:SHORT:h12, feat_vwap_upper_dist:2:SHORT:h20, feat_vwap_upper_dist:2:SHORT:h24, feat_williams_r_14:0:SHORT:h12, feat_williams_r_14:0:SHORT:h15, feat_williams_r_14:0:SHORT:h20, feat_williams_r_14:0:SHORT:h24, feat_zscore_20:2:SHORT:h12, feat_zscore_20:2:SHORT:h15, feat_zscore_20:2:SHORT:h20, feat_zscore_20:2:SHORT:h24
- Armable pairs: AVAXUSDC, BTCUSDC, ENAUSDC, ETHUSDC, GRAMUSDC, HYPEUSDC, KPEPEUSDC, LITUSDC, NEARUSDC, PUMPUSDC, SOLUSDC, UNIUSDC, XMRUSDC, XRPUSDC, ZECUSDC
  - `feat_funding_rate@oi_lo:2:SHORT:h24` edge=335.8b n=155 breadth=3 validated=False prov=False armable=False (too_few_rows)
  - `feat_funding_rate@oi_lo:2:SHORT:h20` edge=282.8b n=171 breadth=3 validated=False prov=False armable=False (too_few_rows)
  - `feat_funding_rate@oi_lo:2:SHORT:h15` edge=210.7b n=171 breadth=3 validated=False prov=False armable=False (too_few_rows)
  - `feat_oi_chg_24@oi_mid:2:SHORT:h24` edge=149.7b n=909 breadth=12 validated=True prov=False armable=True (ok)
  - `feat_funding_rate@oi_lo:2:SHORT:h12` edge=139.2b n=182 breadth=4 validated=False prov=False armable=False (too_few_rows)
  - `feat_funding_cum_24@oi_lo:2:SHORT:h24` edge=134.6b n=1255 breadth=11 validated=False prov=False armable=False (regime_confounded)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+35.09 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **55/55** | hip3 **19/20**
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

- Latest scan 2026-11-12T14:27:11: errors=2 signals=151 regime_blocked=144
- this cycle: closed=0 new_signals=151 skipped=93 slot_full=0 slice_full=0 pair_held=35
- Action funnel: regime_blocked=144 | lane_gate_blocked=1 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=35 | cluster_cap=22 | family_vetoed=1 | slot_full=0 | skipped=93
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "cluster_cap": 22, "family_vetoed": 1, "lane_gate_blocked": 1, "pair_held": 35, "regime_blocked": 144, "skipped": 93, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=48
- aggregate_risk: ok open=10.9998 cap=167.9242 used=0.0950 remaining=151.9709 replayed=3 no_new_bars=0
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:DKNG"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:RIVN"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
