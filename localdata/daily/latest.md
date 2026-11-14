# Breakwater daily print — 2026-11-14 00:25 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **383.73 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2366.59 ZAR** (seed 2000) | lifetime: **+366.59 ZAR** | closed: 587
- Today: 0 closed, **+0.00 ZAR**
- 7d: **+75.94 ZAR** | 30d: **+51.27 ZAR**

## 2b. Claimed vs realised

- Book: 64 slices (native 44 | hip3 20); validated pools: native 172 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 64 book slices present in the validated pools): +0.340% | at 147.22 ZAR mean notional/trade: +0.50 ZAR/trade
- Realised (587 real closes per lane_gate._is_real_close, net of fees): +0.62 ZAR/trade | sd 4.67 | SE 0.19
- Gap: +0.12 ZAR/trade | t = +0.64 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.514% over 44/44 slices (pool 172) ~ +0.75 ZAR | realised 541 closes +0.76 ZAR sd 4.64 SE 0.20 | gap +0.01 t +0.06 | NOT ESTABLISHED
- hip3: claimed median +0.062% over 20/20 slices (pool 160) ~ +0.10 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.07 t -1.51 | NOT ESTABLISHED
- Ledger: 705 decision rows; 587 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 118 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 541 | wins: 277 | win%: 51.2 | P&L: **+411.09 ZAR** | today: +0.00 | 7d: +75.94 | 30d: +51.27
- By exit: target +516.3, trail_stop +226.3, horizon +81.3, max_bars +2.8, regime_shift -11.9, stop -403.6
- By entry regime (n/pnl): neutral 213/+234.4, bull 122/+199.3, bear 206/-22.6
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_trend_neutral:0:SHORT:h24 5n/5w +24.80; feat_premium@oi_hi:2:SHORT:h24 3n/3w +24.15; feat_ext_strength:2:LONG:h15 12n/8w +24.00
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_macd_12_26:2:SHORT:h15 3n/0w -11.55; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; ENAUSDC 7n +23.48; SOLUSDC 66n +19.89; XRPZAR 2n +18.07
- Worst pairs: UNIUSDC 13n -30.75; ZECUSDC 17n -21.96; ETHZAR 4n -14.36; DOGEUSDC 16n -11.14; HYPEUSDC 40n -7.45

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 3 open, stop-risk **13.37 ZAR**
  - XRPUSDC SELL ntl=121 risk=4.62 bars=11 stop=1.0617250000000001870 peak=1.0431
  - BTCUSDC SELL ntl=121 risk=4.51 bars=12 stop=71660.99999999999990 peak=70214.0
  - ETHUSDC SELL ntl=121 risk=4.25 bars=0 stop=1995.800000000000065 peak=1928.0

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **13.37 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **13.37 / 169.01 ZAR | 8.5% | ok**
- Remaining: 154.7364 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 56, "skipped": 56, "slice_full": 0, "slot_full": 0}, "native": {"cluster_cap": 43, "lane_gate_blocked": 0, "opened": 1, "pair_held": 13, "signals": 60, "skipped": 3, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **XRPUSDC** 4.6175 ZAR
- positions without bars: 0 | replayed: 10 | invalid: 0

## 6. Monitored books

- Native: 44 | HIP-3: 20
- Native top (by paper P&L):
  - `feat_ret_autocorr:2:SHORT:h24` edge=0.0069 n=9456 p=0.1167 src=validated_walk_forward unproven=False paper=6n/+8.96
  - `feat_vol_sma_ratio:1:SHORT:h24` edge=0.0041 n=9161 p=0.4004 src=validated_walk_forward unproven=False paper=1n/+3.25
  - `feat_macd_12_26:2:SHORT:h24` edge=0.0130 n=8347 p=0.0831 src=validated_walk_forward unproven=False paper=4n/+1.90
  - `feat_vol_roc_20:0:SHORT:h20` edge=0.0055 n=9810 p=0.5352 src=validated_walk_forward unproven=False paper=1n/+1.69
  - `feat_ext_vs_ma_50:2:SHORT:h24` edge=0.0104 n=8638 p=0.1330 src=validated_walk_forward unproven=False paper=7n/+1.39
  - `feat_ret_20:2:SHORT:h24` edge=0.0096 n=8801 p=0.1282 src=validated_walk_forward unproven=False paper=3n/+0.87
  - `feat_oi_chg_24@oi_mid:2:SHORT:h12` edge=0.0099 n=986 p=0.1573 src=validated_walk_forward unproven=False paper=1n/+0.85
  - `feat_oi_ret_div:2:SHORT:h15` edge=0.0013 n=4508 p=0.4989 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Latest research: 2026-11-13T00:29:39.938955+00:00 | discovered 2240 | validated 151 | reg-confounded 1024 | hostile-unproven 8
- floors: "" | book: {"rows": 50, "by_status": {"decayed": 7, "monitored": 43}, "in_validated_pool": 50, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=1120 validated=1120 passing=151 eligible=439 best=508.4b best_fail=temporal_pass,breadth_ok
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=576 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_time_since_high_20:L0S2:h24: mean=+1.7b t_no=4.11 folds=00001 mkt_corr=-0.10 dd=0b legs=5.5/3.5 fail=n_nonoverlap,folds
  - feat_trend_strength_20:L0S2:h24: mean=+0.7b t_no=2.88 folds=11010 mkt_corr=-0.13 dd=156b legs=13.2/11.6 fail=n_nonoverlap,folds
  - feat_kc_width:L0S2:h24: mean=+8.3b t_no=2.10 folds=11010 mkt_corr=-0.43 dd=337b legs=13.5/9.1 fail=n_nonoverlap,folds,market_corr
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

- Label: **bear** | breadth bear=0.6667 bull=0.0 neutral=0.3333 | symbols=15
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 41 / bull 0
- as_of: 2026-11-13T22:48:58Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 1120 | eligible: 790 | observations: 3619 | armable: **2630**
- Armable slices: feat_adx_14:0:SHORT:h12, feat_adx_14:0:SHORT:h15, feat_adx_14:0:SHORT:h20, feat_adx_14:0:SHORT:h24, feat_adx_14:1:SHORT:h12, feat_adx_14:1:SHORT:h15, feat_adx_14:1:SHORT:h24, feat_asia_range:0:SHORT:h12, feat_asia_range:0:SHORT:h15, feat_asia_range:0:SHORT:h20, feat_asia_range:0:SHORT:h24, feat_asia_vol:0:SHORT:h12, feat_asia_vol:0:SHORT:h15, feat_asia_vol:0:SHORT:h20, feat_asia_vol:0:SHORT:h24, feat_atr_norm_ext:2:SHORT:h12, feat_atr_norm_ext:2:SHORT:h15, feat_atr_norm_ext:2:SHORT:h20, feat_atr_norm_ext:2:SHORT:h24, feat_atr_percent:2:SHORT:h24, feat_atr_ratio:0:SHORT:h12, feat_atr_ratio:0:SHORT:h15, feat_atr_ratio:0:SHORT:h20, feat_bb_pos_20:1:SHORT:h20, feat_bb_pos_20:1:SHORT:h24, feat_bb_pos_20:2:SHORT:h12, feat_bb_pos_20:2:SHORT:h15, feat_bb_pos_20:2:SHORT:h20, feat_bb_pos_20:2:SHORT:h24, feat_bb_squeeze_20:0:SHORT:h12, feat_bb_squeeze_20:0:SHORT:h15, feat_bb_squeeze_20:1:SHORT:h20, feat_bb_squeeze_20:1:SHORT:h24, feat_bb_squeeze_20:2:SHORT:h20, feat_bb_squeeze_20:2:SHORT:h24, feat_bb_width_20:1:SHORT:h12, feat_bb_width_20:1:SHORT:h15, feat_bb_width_20:2:SHORT:h24, feat_book_imb_5:0:SHORT:h15, feat_book_imb_5:0:SHORT:h20, feat_book_imb_5:0:SHORT:h24, feat_book_imb_5:1:SHORT:h15, feat_book_imb_5:1:SHORT:h20, feat_book_imb_5:1:SHORT:h24, feat_book_imb_5:2:SHORT:h20, feat_book_imb_5@oi_hi:0:SHORT:h15, feat_book_imb_5@oi_hi:0:SHORT:h20, feat_book_imb_5@oi_hi:0:SHORT:h24, feat_book_imb_5@oi_hi:1:SHORT:h12, feat_book_imb_5@oi_hi:1:SHORT:h15, feat_book_imb_5@oi_hi:1:SHORT:h20, feat_book_imb_5@oi_hi:1:SHORT:h24, feat_book_imb_5@oi_hi:2:SHORT:h20, feat_book_imb_5@oi_hi:2:SHORT:h24, feat_book_imb_5@oi_lo:0:SHORT:h15, feat_book_imb_5@oi_lo:0:SHORT:h20, feat_book_imb_5@oi_lo:0:SHORT:h24, feat_book_imb_5@oi_lo:1:SHORT:h15, feat_book_imb_5@oi_lo:1:SHORT:h20, feat_book_imb_5@oi_lo:1:SHORT:h24, feat_book_imb_5@oi_lo:2:SHORT:h24, feat_book_imb_5@oi_mid:1:SHORT:h15, feat_book_imb_5@oi_mid:1:SHORT:h20, feat_book_imb_5@oi_mid:2:SHORT:h20, feat_book_imb_5@oi_mid:2:SHORT:h24, feat_buy_vol_ratio:0:SHORT:h20, feat_buy_vol_ratio:0:SHORT:h24, feat_buy_vol_ratio:1:SHORT:h12, feat_buy_vol_ratio:1:SHORT:h15, feat_buy_vol_ratio:1:SHORT:h20, feat_buy_vol_ratio:1:SHORT:h24, feat_buy_vol_ratio:2:SHORT:h15, feat_buy_vol_ratio:2:SHORT:h20, feat_buy_vol_ratio:2:SHORT:h24, feat_cci_20:2:SHORT:h12, feat_cci_20:2:SHORT:h15, feat_cci_20:2:SHORT:h20, feat_cci_20:2:SHORT:h24, feat_close_pos_ma:1:SHORT:h12, feat_close_pos_ma:1:SHORT:h15, feat_close_pos_ma:1:SHORT:h20, feat_close_pos_ma:1:SHORT:h24, feat_close_pos_ma:2:SHORT:h12, feat_close_pos_ma:2:SHORT:h15, feat_close_pos_ma:2:SHORT:h20, feat_close_pos_ma:2:SHORT:h24, feat_close_position:0:SHORT:h20, feat_close_position:0:SHORT:h24, feat_close_position:1:SHORT:h12, feat_close_position:1:SHORT:h15, feat_close_position:1:SHORT:h20, feat_close_position:1:SHORT:h24, feat_close_position:2:SHORT:h15, feat_close_position:2:SHORT:h20, feat_close_position:2:SHORT:h24, feat_donchian_break:1:SHORT:h12, feat_donchian_break:1:SHORT:h15, feat_donchian_break:1:SHORT:h20, feat_donchian_break:1:SHORT:h24, feat_donchian_break:2:SHORT:h12, feat_donchian_break:2:SHORT:h15, feat_donchian_break:2:SHORT:h20, feat_donchian_break:2:SHORT:h24, feat_donchian_width_20:0:SHORT:h12, feat_donchian_width_20:0:SHORT:h15, feat_donchian_width_20:0:SHORT:h20, feat_donchian_width_20:1:SHORT:h15, feat_donchian_width_20:1:SHORT:h20, feat_donchian_width_20:1:SHORT:h24, feat_donchian_width_20:2:SHORT:h24, feat_ema_cross_10_20:1:SHORT:h12, feat_ema_cross_10_20:1:SHORT:h15, feat_ema_cross_10_20:1:SHORT:h20, feat_ema_cross_10_20:2:SHORT:h12, feat_ema_cross_10_20:2:SHORT:h15, feat_ema_cross_10_20:2:SHORT:h20, feat_ema_cross_10_20:2:SHORT:h24, feat_ext_strength:1:SHORT:h15, feat_ext_strength:1:SHORT:h20, feat_ext_strength:1:SHORT:h24, feat_ext_strength:2:SHORT:h12, feat_ext_strength:2:SHORT:h15, feat_ext_strength:2:SHORT:h20, feat_ext_strength:2:SHORT:h24, feat_ext_vs_ma_10:1:SHORT:h15, feat_ext_vs_ma_20:2:SHORT:h12, feat_ext_vs_ma_20:2:SHORT:h15, feat_ext_vs_ma_20:2:SHORT:h20, feat_ext_vs_ma_20:2:SHORT:h24, feat_ext_vs_ma_50:1:SHORT:h12, feat_ext_vs_ma_50:1:SHORT:h15, feat_ext_vs_ma_50:2:SHORT:h12, feat_ext_vs_ma_50:2:SHORT:h15, feat_ext_vs_ma_50:2:SHORT:h20, feat_ext_vs_ma_50:2:SHORT:h24, feat_funding_cum_24:1:SHORT:h12, feat_funding_cum_24:1:SHORT:h20, feat_funding_cum_24:2:SHORT:h12, feat_funding_cum_24:2:SHORT:h15, feat_funding_cum_24:2:SHORT:h20, feat_funding_cum_24:2:SHORT:h24, feat_funding_cum_24@oi_hi:0:SHORT:h12, feat_funding_cum_24@oi_hi:0:SHORT:h15, feat_funding_cum_24@oi_hi:0:SHORT:h20, feat_funding_cum_24@oi_hi:0:SHORT:h24, feat_funding_cum_24@oi_hi:2:SHORT:h12, feat_funding_cum_24@oi_hi:2:SHORT:h15, feat_funding_cum_24@oi_hi:2:SHORT:h20, feat_funding_cum_24@oi_hi:2:SHORT:h24, feat_funding_cum_24@oi_lo:1:SHORT:h12, feat_funding_cum_24@oi_lo:1:SHORT:h15, feat_funding_cum_24@oi_lo:1:SHORT:h20, feat_funding_cum_24@oi_lo:1:SHORT:h24, feat_funding_cum_24@oi_lo:2:SHORT:h12, feat_funding_cum_24@oi_lo:2:SHORT:h15, feat_funding_cum_24@oi_lo:2:SHORT:h20, feat_funding_cum_24@oi_lo:2:SHORT:h24, feat_funding_cum_24@oi_mid:1:SHORT:h12, feat_funding_cum_24@oi_mid:1:SHORT:h20, feat_funding_cum_24@oi_mid:1:SHORT:h24, feat_funding_cum_24@oi_mid:2:SHORT:h12, feat_funding_cum_24@oi_mid:2:SHORT:h15, feat_funding_cum_24@oi_mid:2:SHORT:h20, feat_funding_cum_24@oi_mid:2:SHORT:h24, feat_funding_rate:0:SHORT:h15, feat_funding_rate:0:SHORT:h20, feat_funding_rate:0:SHORT:h24, feat_funding_rate@oi_hi:0:SHORT:h20, feat_funding_rate@oi_hi:0:SHORT:h24, feat_funding_rate@oi_hi:1:SHORT:h12, feat_funding_rate@oi_hi:1:SHORT:h15, feat_funding_rate@oi_hi:1:SHORT:h20, feat_funding_rate@oi_hi:1:SHORT:h24, feat_funding_rate@oi_lo:0:SHORT:h12, feat_funding_rate@oi_lo:0:SHORT:h20, feat_funding_rate@oi_mid:0:SHORT:h15, feat_funding_rate@oi_mid:0:SHORT:h20, feat_funding_rate@oi_mid:0:SHORT:h24, feat_gap:0:SHORT:h12, feat_gap:0:SHORT:h15, feat_gap:0:SHORT:h20, feat_gap:0:SHORT:h24, feat_gap:1:SHORT:h15, feat_gap:1:SHORT:h20, feat_gap:1:SHORT:h24, feat_gap_fill_ratio:0:SHORT:h20, feat_gap_fill_ratio:0:SHORT:h24, feat_gap_fill_ratio:1:SHORT:h12, feat_gap_fill_ratio:1:SHORT:h15, feat_gap_fill_ratio:1:SHORT:h20, feat_hl_range:1:SHORT:h12, feat_hl_range:1:SHORT:h15, feat_hl_range:1:SHORT:h20, feat_hl_range:2:SHORT:h24, feat_hour_utc:2:SHORT:h12, feat_hour_utc:2:SHORT:h15, feat_hour_utc:2:SHORT:h20, feat_hour_utc:2:SHORT:h24, feat_intraday_mom:0:SHORT:h20, feat_intraday_mom:0:SHORT:h24, feat_intraday_mom:2:SHORT:h12, feat_intraday_mom:2:SHORT:h15, feat_intraday_mom:2:SHORT:h20, feat_intraday_mom:2:SHORT:h24, feat_kc_width:2:SHORT:h24, feat_keltner_pos:1:SHORT:h12, feat_keltner_pos:1:SHORT:h15, feat_keltner_pos:1:SHORT:h20, feat_keltner_pos:2:SHORT:h12, feat_keltner_pos:2:SHORT:h15, feat_keltner_pos:2:SHORT:h20, feat_keltner_pos:2:SHORT:h24, feat_macd_12_26:2:SHORT:h12, feat_macd_12_26:2:SHORT:h15, feat_macd_12_26:2:SHORT:h20, feat_macd_12_26:2:SHORT:h24, feat_mean_rev_strength:0:SHORT:h12, feat_mean_rev_strength:0:SHORT:h15, feat_mean_rev_strength:0:SHORT:h20, feat_mean_rev_strength:0:SHORT:h24, feat_oi_chg_24:0:SHORT:h24, feat_oi_chg_24:1:SHORT:h12, feat_oi_chg_24:1:SHORT:h15, feat_oi_chg_24:1:SHORT:h20, feat_oi_chg_24:1:SHORT:h24, feat_oi_chg_24:2:SHORT:h12, feat_oi_chg_24:2:SHORT:h15, feat_oi_chg_24:2:SHORT:h20, feat_oi_chg_24:2:SHORT:h24, feat_oi_chg_24@oi_hi:1:SHORT:h12, feat_oi_chg_24@oi_hi:1:SHORT:h15, feat_oi_chg_24@oi_hi:1:SHORT:h20, feat_oi_chg_24@oi_hi:1:SHORT:h24, feat_oi_chg_24@oi_hi:2:SHORT:h12, feat_oi_chg_24@oi_hi:2:SHORT:h15, feat_oi_chg_24@oi_hi:2:SHORT:h20, feat_oi_chg_24@oi_hi:2:SHORT:h24, feat_oi_chg_24@oi_lo:0:SHORT:h12, feat_oi_chg_24@oi_lo:0:SHORT:h15, feat_oi_chg_24@oi_lo:0:SHORT:h20, feat_oi_chg_24@oi_lo:0:SHORT:h24, feat_oi_chg_24@oi_lo:1:SHORT:h12, feat_oi_chg_24@oi_lo:1:SHORT:h15, feat_oi_chg_24@oi_lo:1:SHORT:h20, feat_oi_chg_24@oi_lo:1:SHORT:h24, feat_oi_chg_24@oi_lo:2:SHORT:h15, feat_oi_chg_24@oi_lo:2:SHORT:h20, feat_oi_chg_24@oi_lo:2:SHORT:h24, feat_oi_chg_24@oi_mid:2:SHORT:h12, feat_oi_chg_24@oi_mid:2:SHORT:h15, feat_oi_chg_24@oi_mid:2:SHORT:h20, feat_oi_chg_24@oi_mid:2:SHORT:h24, feat_oi_ret_div:0:SHORT:h12, feat_oi_ret_div:0:SHORT:h15, feat_oi_ret_div:0:SHORT:h20, feat_oi_ret_div:0:SHORT:h24, feat_oi_ret_div:1:SHORT:h12, feat_oi_ret_div:1:SHORT:h15, feat_oi_ret_div:1:SHORT:h20, feat_oi_ret_div:1:SHORT:h24, feat_oi_ret_div:2:SHORT:h20, feat_oi_ret_div:2:SHORT:h24, feat_oi_ret_div@oi_hi:0:SHORT:h12, feat_oi_ret_div@oi_hi:0:SHORT:h15, feat_oi_ret_div@oi_hi:0:SHORT:h20, feat_oi_ret_div@oi_hi:0:SHORT:h24, feat_oi_ret_div@oi_hi:1:SHORT:h20, feat_oi_ret_div@oi_hi:1:SHORT:h24, feat_oi_ret_div@oi_hi:2:SHORT:h24, feat_oi_ret_div@oi_lo:0:SHORT:h12, feat_oi_ret_div@oi_lo:0:SHORT:h15, feat_oi_ret_div@oi_lo:0:SHORT:h20, feat_oi_ret_div@oi_lo:0:SHORT:h24, feat_oi_ret_div@oi_lo:1:SHORT:h12, feat_oi_ret_div@oi_lo:1:SHORT:h15, feat_oi_ret_div@oi_lo:1:SHORT:h20, feat_oi_ret_div@oi_lo:1:SHORT:h24, feat_oi_ret_div@oi_lo:2:SHORT:h15, feat_oi_ret_div@oi_lo:2:SHORT:h24, feat_oi_ret_div@oi_mid:2:SHORT:h20, feat_oi_ret_div@oi_mid:2:SHORT:h24, feat_overnight_ret:0:SHORT:h12, feat_overnight_ret:0:SHORT:h15, feat_overnight_ret:0:SHORT:h20, feat_overnight_ret:0:SHORT:h24, feat_overnight_ret:1:SHORT:h15, feat_overnight_ret:1:SHORT:h20, feat_overnight_ret:1:SHORT:h24, feat_overnight_ret:2:SHORT:h20, feat_overnight_ret:2:SHORT:h24, feat_premium:1:SHORT:h12, feat_premium:1:SHORT:h15, feat_premium:1:SHORT:h20, feat_premium:1:SHORT:h24, feat_premium:2:SHORT:h12, feat_premium:2:SHORT:h15, feat_premium:2:SHORT:h20, feat_premium:2:SHORT:h24, feat_premium@oi_hi:1:SHORT:h24, feat_premium@oi_hi:2:SHORT:h12, feat_premium@oi_hi:2:SHORT:h15, feat_premium@oi_hi:2:SHORT:h20, feat_premium@oi_hi:2:SHORT:h24, feat_premium@oi_lo:0:SHORT:h20, feat_premium@oi_lo:0:SHORT:h24, feat_premium@oi_lo:1:SHORT:h12, feat_premium@oi_lo:1:SHORT:h20, feat_premium@oi_mid:1:SHORT:h12, feat_premium@oi_mid:1:SHORT:h15, feat_premium@oi_mid:1:SHORT:h20, feat_premium@oi_mid:1:SHORT:h24, feat_price_accel:0:SHORT:h20, feat_price_accel:0:SHORT:h24, feat_price_accel:1:SHORT:h12, feat_price_accel:1:SHORT:h15, feat_price_accel:1:SHORT:h20, feat_price_accel:1:SHORT:h24, feat_price_accel:2:SHORT:h15, feat_price_accel:2:SHORT:h20, feat_price_accel:2:SHORT:h24, feat_price_roc_5:1:SHORT:h12, feat_price_roc_5:1:SHORT:h15, feat_price_roc_5:1:SHORT:h20, feat_price_roc_5:1:SHORT:h24, feat_price_roc_5:2:SHORT:h12, feat_price_roc_5:2:SHORT:h15, feat_price_roc_5:2:SHORT:h20, feat_price_roc_5:2:SHORT:h24, feat_range_expansion:1:SHORT:h15, feat_range_expansion:1:SHORT:h20, feat_range_expansion:1:SHORT:h24, feat_range_expansion:2:SHORT:h20, feat_range_expansion:2:SHORT:h24, feat_range_pos_20:1:SHORT:h15, feat_range_pos_20:2:SHORT:h12, feat_range_pos_20:2:SHORT:h15, feat_range_pos_20:2:SHORT:h20, feat_range_pos_20:2:SHORT:h24, feat_range_pos_50:1:SHORT:h15, feat_range_pos_50:1:SHORT:h20, feat_range_pos_50:1:SHORT:h24, feat_range_pos_50:2:SHORT:h20, feat_range_pos_50:2:SHORT:h24, feat_realized_vol_20:1:SHORT:h12, feat_realized_vol_20:1:SHORT:h24, feat_realized_vol_20:2:SHORT:h24, feat_ret_1:0:SHORT:h20, feat_ret_1:0:SHORT:h24, feat_ret_1:2:SHORT:h15, feat_ret_1:2:SHORT:h20, feat_ret_1:2:SHORT:h24, feat_ret_20:1:SHORT:h12, feat_ret_20:1:SHORT:h15, feat_ret_3:0:SHORT:h20, feat_ret_3:0:SHORT:h24, feat_ret_3:1:SHORT:h12, feat_ret_5:1:SHORT:h12, feat_ret_5:1:SHORT:h15, feat_ret_5:1:SHORT:h20, feat_ret_5:1:SHORT:h24, feat_ret_5:2:SHORT:h12, feat_ret_5:2:SHORT:h15, feat_ret_5:2:SHORT:h20, feat_ret_5:2:SHORT:h24, feat_ret_autocorr:1:SHORT:h15, feat_ret_autocorr:1:SHORT:h20, feat_ret_autocorr:1:SHORT:h24, feat_ret_autocorr:2:SHORT:h12, feat_ret_autocorr:2:SHORT:h15, feat_ret_autocorr:2:SHORT:h20, feat_ret_autocorr:2:SHORT:h24, feat_ret_sign_streak:0:SHORT:h20, feat_ret_sign_streak:0:SHORT:h24, feat_ret_sign_streak:1:SHORT:h15, feat_ret_sign_streak:1:SHORT:h20, feat_ret_vol:1:SHORT:h12, feat_ret_vol:1:SHORT:h15, feat_ret_vol:1:SHORT:h20, feat_ret_vol:2:SHORT:h12, feat_ret_vol:2:SHORT:h15, feat_ret_vol:2:SHORT:h20, feat_ret_vol:2:SHORT:h24, feat_rsi_14:1:SHORT:h12, feat_rsi_14:1:SHORT:h15, feat_rsi_14:1:SHORT:h20, feat_rsi_14:1:SHORT:h24, feat_rsi_21:1:SHORT:h12, feat_rsi_21:1:SHORT:h15, feat_rsi_21:1:SHORT:h20, feat_rsi_21:1:SHORT:h24, feat_rsi_21:2:SHORT:h12, feat_rsi_21:2:SHORT:h15, feat_rsi_21:2:SHORT:h20, feat_rsi_21:2:SHORT:h24, feat_rsi_7:1:SHORT:h15, feat_rsi_7:1:SHORT:h20, feat_rsi_7:1:SHORT:h24, feat_rsi_divergence:0:SHORT:h15, feat_rsi_divergence:0:SHORT:h20, feat_rsi_divergence:0:SHORT:h24, feat_rsi_divergence:1:SHORT:h12, feat_rsi_divergence:1:SHORT:h15, feat_rsi_divergence:1:SHORT:h20, feat_rsi_divergence:2:SHORT:h12, feat_rsi_divergence:2:SHORT:h20, feat_rsi_divergence:2:SHORT:h24, feat_session_mom:0:SHORT:h20, feat_session_mom:0:SHORT:h24, feat_session_mom:2:SHORT:h15, feat_session_mom:2:SHORT:h20, feat_session_mom:2:SHORT:h24, feat_squeeze:1:SHORT:h12, feat_squeeze:1:SHORT:h15, feat_squeeze:1:SHORT:h24, feat_squeeze:2:SHORT:h24, feat_stoch_d_14:2:SHORT:h12, feat_stoch_d_14:2:SHORT:h15, feat_stoch_d_14:2:SHORT:h20, feat_stoch_d_14:2:SHORT:h24, feat_stoch_k_14:0:SHORT:h20, feat_stoch_k_14:2:SHORT:h12, feat_stoch_k_14:2:SHORT:h15, feat_stoch_k_14:2:SHORT:h20, feat_stoch_k_14:2:SHORT:h24, feat_time_since_high_20:1:SHORT:h15, feat_time_since_high_20:1:SHORT:h20, feat_time_since_high_20:1:SHORT:h24, feat_time_since_low_20:1:SHORT:h12, feat_time_since_low_20:1:SHORT:h15, feat_time_since_low_20:1:SHORT:h20, feat_time_since_low_20:1:SHORT:h24, feat_trend_neutral:0:SHORT:h20, feat_trend_neutral:0:SHORT:h24, feat_trend_neutral:2:SHORT:h12, feat_trend_neutral:2:SHORT:h15, feat_trend_neutral:2:SHORT:h20, feat_trend_neutral:2:SHORT:h24, feat_trend_slope_20:1:SHORT:h12, feat_trend_slope_20:1:SHORT:h15, feat_trend_slope_20:1:SHORT:h20, feat_trend_slope_20:1:SHORT:h24, feat_trend_slope_20:2:SHORT:h20, feat_trend_slope_20:2:SHORT:h24, feat_trend_strength_20:0:SHORT:h15, feat_trend_strength_20:0:SHORT:h20, feat_trend_strength_20:0:SHORT:h24, feat_trend_strength_20:1:SHORT:h12, feat_trend_strength_20:2:SHORT:h20, feat_trend_strength_20:2:SHORT:h24, feat_vol_breakout:2:SHORT:h12, feat_vol_breakout:2:SHORT:h15, feat_vol_breakout:2:SHORT:h20, feat_vol_breakout:2:SHORT:h24, feat_vol_breakout_strength:1:SHORT:h12, feat_vol_breakout_strength:1:SHORT:h15, feat_vol_breakout_strength:1:SHORT:h20, feat_vol_breakout_strength:1:SHORT:h24, feat_vol_breakout_strength:2:SHORT:h20, feat_vol_breakout_strength:2:SHORT:h24, feat_vol_of_vol:2:SHORT:h20, feat_vol_of_vol:2:SHORT:h24, feat_vol_roc_20:1:SHORT:h12, feat_vol_roc_20:1:SHORT:h15, feat_vol_roc_20:1:SHORT:h20, feat_vol_roc_20:1:SHORT:h24, feat_vol_sma_ratio:0:SHORT:h12, feat_vol_sma_ratio:0:SHORT:h15, feat_vol_sma_ratio:0:SHORT:h20, feat_vol_sma_ratio:0:SHORT:h24, feat_vol_sma_ratio:1:SHORT:h12, feat_vol_sma_ratio:1:SHORT:h15, feat_vol_sma_ratio:1:SHORT:h20, feat_vol_sma_ratio:1:SHORT:h24, feat_vol_sma_ratio:2:SHORT:h24, feat_vol_trend:1:SHORT:h12, feat_vol_trend:1:SHORT:h15, feat_vol_trend:1:SHORT:h20, feat_vol_trend:1:SHORT:h24, feat_vol_trend:2:SHORT:h15, feat_vol_trend:2:SHORT:h20, feat_vol_trend:2:SHORT:h24, feat_vwap_dist:2:SHORT:h12, feat_vwap_dist:2:SHORT:h15, feat_vwap_dist:2:SHORT:h20, feat_vwap_dist:2:SHORT:h24, feat_vwap_lower_dist:2:SHORT:h12, feat_vwap_lower_dist:2:SHORT:h15, feat_vwap_lower_dist:2:SHORT:h20, feat_vwap_lower_dist:2:SHORT:h24, feat_vwap_upper_dist:2:SHORT:h12, feat_vwap_upper_dist:2:SHORT:h15, feat_vwap_upper_dist:2:SHORT:h20, feat_vwap_upper_dist:2:SHORT:h24, feat_williams_r_14:0:SHORT:h12, feat_williams_r_14:0:SHORT:h15, feat_williams_r_14:0:SHORT:h20, feat_williams_r_14:0:SHORT:h24, feat_williams_r_14:2:SHORT:h20, feat_zscore_20:1:SHORT:h20, feat_zscore_20:1:SHORT:h24, feat_zscore_20:2:SHORT:h12, feat_zscore_20:2:SHORT:h15, feat_zscore_20:2:SHORT:h20, feat_zscore_20:2:SHORT:h24
- Armable pairs: AVAXUSDC, BTCUSDC, ENAUSDC, ETHUSDC, HYPEUSDC, KPEPEUSDC, LITUSDC, NEARUSDC, PUMPUSDC, SOLUSDC, SUIUSDC, UNIUSDC, XMRUSDC, XRPUSDC, ZECUSDC
  - `feat_funding_rate@oi_lo:2:SHORT:h24` edge=508.4b n=117 breadth=3 validated=False prov=False armable=False (too_few_rows)
  - `feat_funding_rate@oi_lo:2:SHORT:h20` edge=395.8b n=117 breadth=3 validated=False prov=False armable=False (too_few_rows)
  - `feat_funding_rate@oi_lo:2:SHORT:h15` edge=312.8b n=113 breadth=3 validated=False prov=False armable=False (too_few_rows)
  - `feat_funding_rate@oi_lo:2:SHORT:h12` edge=219.2b n=101 breadth=2 validated=False prov=False armable=False (too_few_rows)
  - `feat_oi_chg_24@oi_mid:2:SHORT:h24` edge=150.7b n=1130 breadth=13 validated=True prov=False armable=True (ok)
  - `feat_funding_rate@oi_mid:2:SHORT:h24` edge=147.0b n=247 breadth=6 validated=True prov=False armable=True (ok)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+20.38 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **44/44** | hip3 **19/20**
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

- Latest scan 2026-11-13T23:55:45: errors=0 signals=116 regime_blocked=111
- this cycle: closed=0 new_signals=116 skipped=59 slot_full=0 slice_full=0 pair_held=13
- Action funnel: regime_blocked=111 | lane_gate_blocked=1 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=13 | cluster_cap=43 | family_vetoed=0 | slot_full=0 | skipped=59
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "cluster_cap": 43, "family_vetoed": 0, "lane_gate_blocked": 1, "pair_held": 13, "regime_blocked": 111, "skipped": 59, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=48
- aggregate_risk: ok open=9.1266 cap=169.0137 used=0.0845 remaining=154.7364 replayed=10 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
