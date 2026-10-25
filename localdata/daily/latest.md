# Breakwater daily print — 2026-10-25 06:57 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **433.18 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2286.94 ZAR** (seed 2000) | lifetime: **+286.94 ZAR** | closed: 466
- Today: 0 closed, **+0.00 ZAR**
- 7d: **-3.96 ZAR** | 30d: **-192.64 ZAR**

## 2b. Claimed vs realised

- Book: 74 slices (native 54 | hip3 20); validated pools: native 148 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 74 book slices present in the validated pools): +0.250% | at 154.99 ZAR mean notional/trade: +0.39 ZAR/trade
- Realised (466 real closes per lane_gate._is_real_close, net of fees): +0.62 ZAR/trade | sd 4.99 | SE 0.23
- Gap: +0.23 ZAR/trade | t = +0.99 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.300% over 54/54 slices (pool 148) ~ +0.46 ZAR | realised 420 closes +0.79 ZAR sd 4.99 SE 0.24 | gap +0.33 t +1.35 | NOT ESTABLISHED
- hip3: claimed median +0.062% over 20/20 slices (pool 160) ~ +0.10 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.07 t -1.51 | NOT ESTABLISHED
- Ledger: 565 decision rows; 466 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 99 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 420 | wins: 205 | win%: 48.8 | P&L: **+331.45 ZAR** | today: +0.00 | 7d: -3.96 | 30d: -153.77
- By exit: target +516.3, trail_stop +84.6, horizon +72.8, max_bars +2.8, regime_shift -11.9, stop -333.1
- By entry regime (n/pnl): neutral 164/+224.5, bull 114/+183.9, bear 142/-77.0
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82; feat_range_pos_50:2:SHORT:h24 3n/0w -10.55
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPZAR 2n +18.07; XMRUSDC 5n +13.98; BTCUSDC 45n +9.55
- Worst pairs: UNIUSDC 7n -21.68; ETHUSDC 54n -21.35; ZECUSDC 14n -18.75; XRPUSDC 43n -15.06; ETHZAR 4n -14.36

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: -38.87
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 7 open, stop-risk **23.18 ZAR**
  - SUIUSDC SELL ntl=116 risk=4.53 bars=5 stop=0.9768899999999999975 peak=0.94051
  - UNIUSDC SELL ntl=116 risk=3.73 bars=0 stop=6.9991499999999999190 peak=6.7816
  - HYPEUSDC SELL ntl=116 risk=3.71 bars=11 stop=78.49824999999999960 peak=76.802
  - SOLUSDC SELL ntl=116 risk=3.12 bars=9 stop=104.27499999999999765 peak=102.7
  - XRPUSDC SELL ntl=116 risk=3.04 bars=10 stop=1.3217500000000000655 peak=1.3153
  - ETHUSDC SELL ntl=116 risk=3.02 bars=9 stop=2406.624999999999730 peak=2370.5
  - BTCUSDC SELL ntl=116 risk=2.03 bars=11 stop=81927.06500 peak=81014.0

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **23.18 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **23.18 / 162.82 ZAR | 15.5% | ok**
- Remaining: 137.6086 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 20, "skipped": 20, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 0, "opened": 1, "pair_held": 81, "signals": 174, "skipped": 92, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **SUIUSDC** 4.5308 ZAR
- positions without bars: 0 | replayed: 6 | invalid: 0

## 6. Monitored books

- Native: 54 | HIP-3: 20
- Native top (by paper P&L):
  - `feat_donchian_break:2:SHORT:h24` edge=0.0080 n=7892 p=0.1453 src=validated_walk_forward unproven=False paper=2n/+3.68
  - `feat_vwap_lower_dist:2:SHORT:h20` edge=0.0038 n=9108 p=0.1178 src=validated_walk_forward unproven=False paper=1n/+2.38
  - `feat_trend_slope_20:2:SHORT:h12` edge=0.0043 n=7292 p=0.2256 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_macd_12_26:2:SHORT:h20` edge=0.0098 n=7293 p=0.0083 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_gap_fill_ratio:0:SHORT:h20` edge=0.0019 n=10841 p=0.6548 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vwap_lower_dist:2:SHORT:h12` edge=0.0046 n=8213 p=0.1646 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_time_since_high_20:0:SHORT:h12` edge=0.0043 n=7826 p=0.3609 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_atr_percent:1:SHORT:h15` edge=0.0027 n=9736 p=0.5166 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Latest research: 2026-10-25T01:03:22.791098+00:00 | discovered 1664 | validated 148 | reg-confounded 573 | hostile-unproven 4
- floors: "" | book: {"rows": 55, "by_status": {"monitored": 54, "decayed": 1}, "in_validated_pool": 55, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=832 validated=832 passing=148 eligible=113 best=114.2b best_fail=temporal_pass
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=528 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_range_pos_50:L0S2:h24: mean=+11.2b t_no=3.32 folds=00111 mkt_corr=-0.00 dd=106b legs=13.3/9.5 fail=n_nonoverlap,folds
  - feat_ext_vs_ma_50:L0S2:h20: mean=+9.3b t_no=2.81 folds=01111 mkt_corr=-0.02 dd=161b legs=14.5/7.7 fail=n_nonoverlap
  - feat_williams_r_14:L2S0:h24: mean=+4.0b t_no=2.34 folds=00010 mkt_corr=+0.07 dd=151b legs=12.6/11.0 fail=n_nonoverlap,folds
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

- Label: **bear** | breadth bear=0.6667 bull=0.1333 neutral=0.2 | symbols=15
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 22 / bull 0
- as_of: 2026-10-25T06:00:31Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 832 | eligible: 299 | observations: 1688 | armable: **1340**
- Armable slices: feat_adx_14:0:SHORT:h24, feat_adx_14:1:SHORT:h15, feat_adx_14:1:SHORT:h20, feat_adx_14:1:SHORT:h24, feat_asia_range:2:SHORT:h15, feat_asia_range:2:SHORT:h20, feat_asia_range:2:SHORT:h24, feat_asia_vol:2:SHORT:h15, feat_asia_vol:2:SHORT:h20, feat_asia_vol:2:SHORT:h24, feat_atr_norm_ext:1:SHORT:h20, feat_atr_norm_ext:1:SHORT:h24, feat_atr_norm_ext:2:SHORT:h24, feat_atr_percent:1:SHORT:h12, feat_atr_percent:1:SHORT:h15, feat_atr_percent:1:SHORT:h20, feat_atr_percent:1:SHORT:h24, feat_atr_ratio:1:SHORT:h15, feat_atr_ratio:1:SHORT:h20, feat_atr_ratio:1:SHORT:h24, feat_bb_pos_20:1:SHORT:h20, feat_bb_pos_20:1:SHORT:h24, feat_bb_width_20:0:SHORT:h12, feat_bb_width_20:0:SHORT:h15, feat_bb_width_20:0:SHORT:h20, feat_bb_width_20:0:SHORT:h24, feat_bb_width_20:1:SHORT:h20, feat_bb_width_20:1:SHORT:h24, feat_buy_vol_ratio:1:SHORT:h24, feat_cci_20:2:SHORT:h12, feat_cci_20:2:SHORT:h15, feat_cci_20:2:SHORT:h20, feat_cci_20:2:SHORT:h24, feat_close_pos_ma:1:SHORT:h20, feat_close_pos_ma:1:SHORT:h24, feat_close_position:1:SHORT:h24, feat_donchian_break:2:SHORT:h12, feat_donchian_break:2:SHORT:h15, feat_donchian_break:2:SHORT:h20, feat_donchian_break:2:SHORT:h24, feat_donchian_width_20:0:SHORT:h24, feat_donchian_width_20:1:SHORT:h20, feat_donchian_width_20:1:SHORT:h24, feat_ema_cross_10_20:2:SHORT:h20, feat_ema_cross_10_20:2:SHORT:h24, feat_ext_strength:2:SHORT:h12, feat_ext_strength:2:SHORT:h15, feat_ext_strength:2:SHORT:h20, feat_ext_strength:2:SHORT:h24, feat_ext_vs_ma_10:1:SHORT:h20, feat_ext_vs_ma_10:1:SHORT:h24, feat_ext_vs_ma_20:1:SHORT:h20, feat_ext_vs_ma_20:1:SHORT:h24, feat_ext_vs_ma_20:2:SHORT:h15, feat_ext_vs_ma_20:2:SHORT:h20, feat_ext_vs_ma_20:2:SHORT:h24, feat_ext_vs_ma_50:2:SHORT:h24, feat_gap:0:SHORT:h15, feat_gap:0:SHORT:h20, feat_gap:0:SHORT:h24, feat_gap_fill_ratio:0:SHORT:h24, feat_gap_fill_ratio:1:SHORT:h20, feat_gap_fill_ratio:1:SHORT:h24, feat_hl_range:0:SHORT:h20, feat_hl_range:0:SHORT:h24, feat_hl_range:1:SHORT:h20, feat_hl_range:1:SHORT:h24, feat_hour_utc:0:SHORT:h15, feat_hour_utc:0:SHORT:h20, feat_hour_utc:0:SHORT:h24, feat_intraday_mom:1:SHORT:h24, feat_kc_width:1:SHORT:h15, feat_kc_width:1:SHORT:h20, feat_kc_width:1:SHORT:h24, feat_keltner_pos:1:SHORT:h20, feat_keltner_pos:1:SHORT:h24, feat_macd_12_26:2:SHORT:h12, feat_macd_12_26:2:SHORT:h15, feat_macd_12_26:2:SHORT:h20, feat_macd_12_26:2:SHORT:h24, feat_mean_rev_strength:0:SHORT:h24, feat_mean_rev_strength:1:SHORT:h24, feat_overnight_ret:0:SHORT:h20, feat_overnight_ret:0:SHORT:h24, feat_price_accel:1:SHORT:h20, feat_price_accel:1:SHORT:h24, feat_price_roc_5:1:SHORT:h20, feat_price_roc_5:1:SHORT:h24, feat_range_expansion:1:SHORT:h20, feat_range_expansion:1:SHORT:h24, feat_range_pos_20:2:SHORT:h12, feat_range_pos_20:2:SHORT:h15, feat_range_pos_20:2:SHORT:h20, feat_range_pos_20:2:SHORT:h24, feat_range_pos_50:2:SHORT:h12, feat_range_pos_50:2:SHORT:h15, feat_range_pos_50:2:SHORT:h20, feat_range_pos_50:2:SHORT:h24, feat_realized_vol_20:0:SHORT:h12, feat_realized_vol_20:0:SHORT:h15, feat_realized_vol_20:0:SHORT:h20, feat_realized_vol_20:0:SHORT:h24, feat_ret_10:1:SHORT:h20, feat_ret_10:1:SHORT:h24, feat_ret_10:2:SHORT:h20, feat_ret_10:2:SHORT:h24, feat_ret_1:1:SHORT:h24, feat_ret_20:1:SHORT:h15, feat_ret_20:1:SHORT:h20, feat_ret_20:1:SHORT:h24, feat_ret_20:2:SHORT:h20, feat_ret_20:2:SHORT:h24, feat_ret_3:1:SHORT:h20, feat_ret_3:1:SHORT:h24, feat_ret_5:1:SHORT:h20, feat_ret_5:1:SHORT:h24, feat_ret_autocorr:1:SHORT:h12, feat_ret_autocorr:1:SHORT:h15, feat_ret_autocorr:1:SHORT:h20, feat_ret_autocorr:1:SHORT:h24, feat_ret_sign_streak:2:SHORT:h24, feat_ret_vol:1:SHORT:h20, feat_ret_vol:1:SHORT:h24, feat_ret_vol:2:SHORT:h24, feat_rsi_divergence:0:SHORT:h20, feat_rsi_divergence:1:SHORT:h24, feat_session_mom:1:SHORT:h20, feat_session_mom:1:SHORT:h24, feat_squeeze:0:SHORT:h20, feat_squeeze:1:SHORT:h20, feat_squeeze:1:SHORT:h24, feat_stoch_d_14:2:SHORT:h12, feat_stoch_d_14:2:SHORT:h15, feat_stoch_d_14:2:SHORT:h20, feat_stoch_d_14:2:SHORT:h24, feat_stoch_k_14:2:SHORT:h12, feat_stoch_k_14:2:SHORT:h15, feat_stoch_k_14:2:SHORT:h20, feat_stoch_k_14:2:SHORT:h24, feat_time_since_high_20:0:SHORT:h12, feat_time_since_high_20:0:SHORT:h15, feat_time_since_high_20:0:SHORT:h20, feat_time_since_high_20:0:SHORT:h24, feat_time_since_low_20:1:SHORT:h12, feat_time_since_low_20:1:SHORT:h15, feat_time_since_low_20:1:SHORT:h20, feat_time_since_low_20:1:SHORT:h24, feat_trend_neutral:1:SHORT:h12, feat_trend_neutral:1:SHORT:h15, feat_trend_slope_20:1:SHORT:h15, feat_trend_slope_20:1:SHORT:h20, feat_trend_slope_20:1:SHORT:h24, feat_trend_slope_20:2:SHORT:h12, feat_trend_slope_20:2:SHORT:h15, feat_trend_slope_20:2:SHORT:h20, feat_trend_slope_20:2:SHORT:h24, feat_trend_strength_20:2:SHORT:h24, feat_vol_breakout:1:SHORT:h24, feat_vol_breakout:2:SHORT:h15, feat_vol_breakout:2:SHORT:h20, feat_vol_breakout:2:SHORT:h24, feat_vol_breakout_strength:1:SHORT:h20, feat_vol_breakout_strength:1:SHORT:h24, feat_vol_contraction:0:SHORT:h24, feat_vol_contraction:1:SHORT:h12, feat_vol_contraction:1:SHORT:h15, feat_vol_contraction:2:SHORT:h24, feat_vol_regime:0:SHORT:h24, feat_vol_regime:1:SHORT:h12, feat_vol_regime:1:SHORT:h15, feat_vol_regime:2:SHORT:h24, feat_vol_roc_20:1:SHORT:h20, feat_vol_roc_20:1:SHORT:h24, feat_vol_roc_20:2:SHORT:h20, feat_vol_roc_20:2:SHORT:h24, feat_vol_sma_ratio:1:SHORT:h20, feat_vol_sma_ratio:1:SHORT:h24, feat_vol_sma_ratio:2:SHORT:h24, feat_vol_trend:1:SHORT:h20, feat_vol_trend:1:SHORT:h24, feat_vol_trend:2:SHORT:h20, feat_vol_trend:2:SHORT:h24, feat_vwap_dist:1:SHORT:h20, feat_vwap_dist:1:SHORT:h24, feat_vwap_dist:2:SHORT:h12, feat_vwap_dist:2:SHORT:h15, feat_vwap_dist:2:SHORT:h20, feat_vwap_dist:2:SHORT:h24, feat_vwap_lower_dist:1:SHORT:h20, feat_vwap_lower_dist:1:SHORT:h24, feat_vwap_lower_dist:2:SHORT:h12, feat_vwap_lower_dist:2:SHORT:h15, feat_vwap_lower_dist:2:SHORT:h20, feat_vwap_lower_dist:2:SHORT:h24, feat_vwap_upper_dist:1:SHORT:h24, feat_vwap_upper_dist:2:SHORT:h12, feat_vwap_upper_dist:2:SHORT:h15, feat_vwap_upper_dist:2:SHORT:h20, feat_vwap_upper_dist:2:SHORT:h24, feat_williams_r_14:0:SHORT:h12, feat_williams_r_14:0:SHORT:h15, feat_williams_r_14:0:SHORT:h20, feat_williams_r_14:0:SHORT:h24, feat_zscore_20:1:SHORT:h20, feat_zscore_20:1:SHORT:h24
- Armable pairs: BTCUSDC, ENAUSDC, ETHUSDC, FARTCOINUSDC, HYPEUSDC, KPEPEUSDC, NEARUSDC, PUMPUSDC, SOLUSDC, SUIUSDC, UNIUSDC, WLDUSDC, XMRUSDC, XRPUSDC, ZECUSDC
  - `feat_macd_12_26:2:SHORT:h24` edge=114.2b n=7284 breadth=40 validated=True prov=False armable=True (ok)
  - `feat_ema_cross_10_20:2:SHORT:h24` edge=102.9b n=7120 breadth=40 validated=True prov=False armable=True (ok)
  - `feat_ext_vs_ma_50:2:SHORT:h24` edge=100.0b n=5991 breadth=40 validated=True prov=False armable=True (ok)
  - `feat_macd_12_26:2:SHORT:h20` edge=97.7b n=7293 breadth=40 validated=True prov=False armable=True (ok)
  - `feat_trend_slope_20:2:SHORT:h24` edge=86.1b n=7272 breadth=40 validated=True prov=False armable=True (ok)
  - `feat_stoch_d_14:2:SHORT:h24` edge=85.7b n=8246 breadth=40 validated=True prov=False armable=True (ok)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+1.80 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **53/54** | hip3 **18/20**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 42
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
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` lane_not_green
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-10-25T06:56:26: errors=0 signals=194 regime_blocked=233
- this cycle: closed=0 new_signals=194 skipped=112 slot_full=0 slice_full=0 pair_held=81
- Action funnel: regime_blocked=233 | lane_gate_blocked=3 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=81 | slot_full=0 | skipped=112
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 3, "pair_held": 81, "regime_blocked": 233, "skipped": 112, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=42
- aggregate_risk: ok open=19.4495 cap=162.8237 used=0.1549 remaining=137.6086 replayed=6 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
