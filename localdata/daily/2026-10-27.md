# Breakwater daily print — 2026-10-27 12:25 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **432.36 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2275.09 ZAR** (seed 2000) | lifetime: **+275.09 ZAR** | closed: 480
- Today: 1 closed, **-2.18 ZAR**
- 7d: **-11.88 ZAR** | 30d: **-219.25 ZAR**

## 2b. Claimed vs realised

- Book: 68 slices (native 48 | hip3 20); validated pools: native 123 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 68 book slices present in the validated pools): +0.249% | at 153.86 ZAR mean notional/trade: +0.38 ZAR/trade
- Realised (480 real closes per lane_gate._is_real_close, net of fees): +0.57 ZAR/trade | sd 4.93 | SE 0.23
- Gap: +0.19 ZAR/trade | t = +0.84 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.364% over 48/48 slices (pool 123) ~ +0.56 ZAR | realised 434 closes +0.74 ZAR sd 4.92 SE 0.24 | gap +0.18 t +0.77 | NOT ESTABLISHED
- hip3: claimed median +0.062% over 20/20 slices (pool 160) ~ +0.10 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.07 t -1.51 | NOT ESTABLISHED
- Ledger: 581 decision rows; 480 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 101 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 434 | wins: 208 | win%: 47.9 | P&L: **+319.59 ZAR** | today: -2.18 | 7d: -11.88 | 30d: -183.09
- By exit: target +516.3, trail_stop +84.5, horizon +67.5, max_bars +2.8, regime_shift -11.9, stop -339.5
- By entry regime (n/pnl): neutral 166/+222.7, bull 114/+183.9, bear 154/-87.1
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82; feat_range_pos_50:2:SHORT:h24 3n/0w -10.55
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPZAR 2n +18.07; XMRUSDC 7n +10.76; AAVEUSDC 3n +9.47
- Worst pairs: UNIUSDC 9n -26.80; ETHUSDC 56n -21.15; ZECUSDC 14n -18.75; XRPUSDC 45n -16.32; HYPEUSDC 32n -15.86

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: -36.16
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 7 open, stop-risk **22.18 ZAR**
  - HYPEUSDC SELL ntl=116 risk=4.60 bars=17 stop=81.46774999999999810 peak=80.564
  - ZECUSDC SELL ntl=116 risk=4.55 bars=0 stop=1296.87500000000010 peak=1247.8
  - SOLUSDC SELL ntl=116 risk=3.70 bars=22 stop=104.9207500000000020 peak=102.7
  - XRPUSDC SELL ntl=116 risk=3.63 bars=21 stop=1.3382000000000000805 peak=1.3132
  - ETHUSDC SELL ntl=116 risk=3.36 bars=18 stop=2394.5250000000000690 peak=2335.7
  - BTCUSDC SELL ntl=116 risk=2.34 bars=22 stop=82010.250000000000040 peak=80835.0
  - SUIUSDC SELL ntl=116 risk=0.00 bars=57 stop=0.93609999999999999750 peak=0.94051

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **22.18 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **22.18 / 161.95 ZAR | 14.9% | ok**
- Remaining: 137.7385 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 38, "skipped": 38, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 0, "opened": 1, "pair_held": 37, "signals": 77, "skipped": 39, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **HYPEUSDC** 4.5960 ZAR
- positions without bars: 0 | replayed: 12 | invalid: 0

## 6. Monitored books

- Native: 48 | HIP-3: 20
- Native top (by paper P&L):
  - `feat_vwap_dist:2:SHORT:h15` edge=0.0049 n=7451 p=0.2098 src=validated_walk_forward unproven=False paper=1n/+1.83
  - `feat_vwap_lower_dist:2:SHORT:h12` edge=0.0043 n=8030 p=0.1386 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_10:2:SHORT:h12` edge=0.0039 n=7574 p=0.2318 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vol_roc_20:0:SHORT:h20` edge=0.0017 n=10080 p=0.8721 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_funding_rate:1:SHORT:h12` edge=0.0057 n=898 p=0.0673 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_range_pos_20:1:SHORT:h20` edge=0.0023 n=9714 p=0.7718 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_stoch_d_14:1:SHORT:h20` edge=0.0018 n=9776 p=0.6345 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vol_sma_ratio:1:SHORT:h15` edge=0.0016 n=9504 p=0.5443 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Latest research: 2026-10-27T09:48:26.554004+00:00 | discovered 1960 | validated 123 | reg-confounded 817 | hostile-unproven 10
- floors: "" | book: {"rows": 50, "by_status": {"monitored": 48, "decayed": 1, "cooldown": 1}, "in_validated_pool": 50, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=980 validated=980 passing=123 eligible=142 best=231.4b best_fail=temporal_pass
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=552 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_buy_vol_ratio:L2S0:h24: mean=-10.5b t_no=2.51 folds=00100 mkt_corr=-0.18 dd=276b legs=11.3/11.6 fail=n_nonoverlap,mean<=0,folds
  - feat_close_position:L2S0:h24: mean=-10.5b t_no=2.51 folds=00100 mkt_corr=-0.18 dd=276b legs=11.3/11.6 fail=n_nonoverlap,mean<=0,folds
  - feat_rsi_7:L0S2:h12: mean=+2.3b t_no=2.03 folds=01100 mkt_corr=+0.03 dd=411b legs=12.2/11.0 fail=folds
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
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 16 / bull 0
- as_of: 2026-10-27T11:35:28Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 980 | eligible: 375 | observations: 1103 | armable: **752**
- Armable slices: feat_adx_14:0:SHORT:h20, feat_adx_14:0:SHORT:h24, feat_adx_14:1:SHORT:h20, feat_adx_14:1:SHORT:h24, feat_atr_norm_ext:1:SHORT:h20, feat_atr_norm_ext:1:SHORT:h24, feat_atr_percent:1:SHORT:h20, feat_atr_percent:1:SHORT:h24, feat_atr_ratio:1:SHORT:h12, feat_atr_ratio:1:SHORT:h15, feat_atr_ratio:1:SHORT:h20, feat_atr_ratio:1:SHORT:h24, feat_bb_pos_20:1:SHORT:h20, feat_bb_pos_20:1:SHORT:h24, feat_bb_squeeze_20:1:SHORT:h15, feat_bb_squeeze_20:1:SHORT:h20, feat_bb_squeeze_20:1:SHORT:h24, feat_bb_width_20:1:SHORT:h20, feat_bb_width_20:1:SHORT:h24, feat_cci_20:1:SHORT:h20, feat_cci_20:1:SHORT:h24, feat_cci_20:2:SHORT:h24, feat_close_pos_ma:1:SHORT:h20, feat_close_pos_ma:1:SHORT:h24, feat_donchian_width_20:1:SHORT:h12, feat_donchian_width_20:1:SHORT:h15, feat_donchian_width_20:1:SHORT:h20, feat_donchian_width_20:1:SHORT:h24, feat_ema_cross_10_20:2:SHORT:h24, feat_ext_vs_ma_10:1:SHORT:h20, feat_ext_vs_ma_10:1:SHORT:h24, feat_ext_vs_ma_10:2:SHORT:h24, feat_ext_vs_ma_20:2:SHORT:h24, feat_ext_vs_ma_50:1:SHORT:h20, feat_ext_vs_ma_50:1:SHORT:h24, feat_ext_vs_ma_50:2:SHORT:h24, feat_funding_rate:1:SHORT:h12, feat_funding_rate:1:SHORT:h15, feat_funding_rate:1:SHORT:h20, feat_funding_rate:1:SHORT:h24, feat_funding_rate:2:SHORT:h12, feat_funding_rate@oi_hi:1:SHORT:h12, feat_funding_rate@oi_hi:1:SHORT:h15, feat_funding_rate@oi_hi:1:SHORT:h20, feat_funding_rate@oi_hi:1:SHORT:h24, feat_funding_rate@oi_lo:1:SHORT:h12, feat_funding_rate@oi_lo:1:SHORT:h15, feat_funding_rate@oi_lo:1:SHORT:h20, feat_funding_rate@oi_lo:1:SHORT:h24, feat_funding_rate@oi_lo:2:SHORT:h12, feat_funding_rate@oi_mid:2:SHORT:h12, feat_funding_rate@oi_mid:2:SHORT:h15, feat_funding_rate@oi_mid:2:SHORT:h20, feat_funding_rate@oi_mid:2:SHORT:h24, feat_gap:0:SHORT:h20, feat_gap:0:SHORT:h24, feat_gap_fill_ratio:0:SHORT:h20, feat_gap_fill_ratio:0:SHORT:h24, feat_gap_fill_ratio:1:SHORT:h20, feat_gap_fill_ratio:1:SHORT:h24, feat_hl_range:1:SHORT:h20, feat_hl_range:1:SHORT:h24, feat_intraday_mom:1:SHORT:h24, feat_kc_width:1:SHORT:h20, feat_kc_width:1:SHORT:h24, feat_keltner_pos:2:SHORT:h24, feat_macd_12_26:2:SHORT:h20, feat_macd_12_26:2:SHORT:h24, feat_mean_rev_strength:1:SHORT:h20, feat_mean_rev_strength:1:SHORT:h24, feat_overnight_ret:0:SHORT:h20, feat_overnight_ret:0:SHORT:h24, feat_premium:1:SHORT:h12, feat_premium:1:SHORT:h15, feat_premium:1:SHORT:h20, feat_premium:1:SHORT:h24, feat_premium:2:SHORT:h24, feat_premium@oi_hi:1:SHORT:h12, feat_premium@oi_hi:1:SHORT:h15, feat_premium@oi_hi:1:SHORT:h20, feat_premium@oi_hi:1:SHORT:h24, feat_premium@oi_hi:2:SHORT:h20, feat_premium@oi_hi:2:SHORT:h24, feat_premium@oi_lo:1:SHORT:h15, feat_premium@oi_lo:1:SHORT:h20, feat_premium@oi_lo:1:SHORT:h24, feat_premium@oi_mid:1:SHORT:h20, feat_premium@oi_mid:1:SHORT:h24, feat_premium@oi_mid:2:SHORT:h12, feat_premium@oi_mid:2:SHORT:h24, feat_price_accel:1:SHORT:h24, feat_price_roc_5:2:SHORT:h24, feat_range_expansion:1:SHORT:h24, feat_range_pos_20:1:SHORT:h20, feat_range_pos_20:1:SHORT:h24, feat_range_pos_50:1:SHORT:h20, feat_range_pos_50:1:SHORT:h24, feat_range_pos_50:2:SHORT:h12, feat_range_pos_50:2:SHORT:h15, feat_range_pos_50:2:SHORT:h20, feat_range_pos_50:2:SHORT:h24, feat_realized_vol_20:0:SHORT:h12, feat_realized_vol_20:1:SHORT:h20, feat_realized_vol_20:1:SHORT:h24, feat_ret_1:2:SHORT:h24, feat_ret_20:1:SHORT:h24, feat_ret_5:2:SHORT:h24, feat_ret_autocorr:1:SHORT:h15, feat_ret_autocorr:1:SHORT:h20, feat_ret_autocorr:1:SHORT:h24, feat_ret_autocorr:2:SHORT:h24, feat_ret_sign_streak:0:SHORT:h24, feat_ret_sign_streak:2:SHORT:h24, feat_ret_vol:2:SHORT:h24, feat_rsi_divergence:0:SHORT:h20, feat_rsi_divergence:1:SHORT:h24, feat_rsi_divergence:2:SHORT:h24, feat_session_mom:1:SHORT:h15, feat_session_mom:1:SHORT:h20, feat_session_mom:1:SHORT:h24, feat_squeeze:1:SHORT:h15, feat_squeeze:1:SHORT:h20, feat_squeeze:1:SHORT:h24, feat_stoch_d_14:2:SHORT:h12, feat_stoch_d_14:2:SHORT:h24, feat_stoch_k_14:1:SHORT:h20, feat_stoch_k_14:1:SHORT:h24, feat_time_since_low_20:1:SHORT:h20, feat_time_since_low_20:1:SHORT:h24, feat_time_since_low_20:2:SHORT:h15, feat_time_since_low_20:2:SHORT:h20, feat_time_since_low_20:2:SHORT:h24, feat_trend_slope_20:1:SHORT:h24, feat_trend_strength_20:0:SHORT:h24, feat_trend_strength_20:2:SHORT:h24, feat_vol_breakout:2:SHORT:h20, feat_vol_breakout:2:SHORT:h24, feat_vol_breakout_strength:1:SHORT:h24, feat_vol_contraction:1:SHORT:h12, feat_vol_contraction:1:SHORT:h15, feat_vol_contraction:1:SHORT:h20, feat_vol_contraction:1:SHORT:h24, feat_vol_contraction:2:SHORT:h24, feat_vol_regime:1:SHORT:h12, feat_vol_regime:1:SHORT:h15, feat_vol_regime:1:SHORT:h20, feat_vol_regime:1:SHORT:h24, feat_vol_regime:2:SHORT:h24, feat_vol_roc_20:1:SHORT:h20, feat_vol_roc_20:1:SHORT:h24, feat_vol_sma_ratio:0:SHORT:h24, feat_vol_sma_ratio:1:SHORT:h20, feat_vol_sma_ratio:1:SHORT:h24, feat_vol_sma_ratio:2:SHORT:h24, feat_vwap_dist:1:SHORT:h20, feat_vwap_dist:1:SHORT:h24, feat_vwap_lower_dist:1:SHORT:h20, feat_vwap_lower_dist:1:SHORT:h24, feat_vwap_upper_dist:1:SHORT:h24, feat_williams_r_14:1:SHORT:h20, feat_williams_r_14:1:SHORT:h24, feat_zscore_20:1:SHORT:h20, feat_zscore_20:1:SHORT:h24
- Armable pairs: BTCUSDC, CHIPUSDC, ENAUSDC, ETHUSDC, HYPEUSDC, LITUSDC, NEARUSDC, PUMPUSDC, SOLUSDC, SUIUSDC, WLDUSDC, XMRUSDC, XRPUSDC, ZECUSDC, ZROUSDC
  - `feat_funding_rate@oi_lo:1:SHORT:h24` edge=231.4b n=221 breadth=6 validated=False prov=False armable=True (ok)
  - `feat_funding_rate@oi_lo:1:SHORT:h20` edge=192.4b n=204 breadth=5 validated=False prov=False armable=True (ok)
  - `feat_funding_rate@oi_lo:1:SHORT:h15` edge=185.6b n=211 breadth=5 validated=False prov=False armable=True (ok)
  - `feat_funding_cum_24@oi_mid:2:SHORT:h20` edge=146.4b n=925 breadth=10 validated=True prov=False armable=True (ok)
  - `feat_funding_rate@oi_mid:2:SHORT:h20` edge=146.1b n=763 breadth=10 validated=True prov=False armable=True (ok)
  - `feat_funding_cum_24@oi_mid:2:SHORT:h24` edge=145.7b n=739 breadth=9 validated=False prov=False armable=False (regime_confounded)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+4.26 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **48/48** | hip3 **18/20**
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

- Latest scan 2026-10-27T11:01:45: errors=2 signals=115 regime_blocked=173
- this cycle: closed=0 new_signals=115 skipped=77 slot_full=0 slice_full=0 pair_held=37
- Action funnel: regime_blocked=173 | lane_gate_blocked=2 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=37 | slot_full=0 | skipped=77
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 2, "pair_held": 37, "regime_blocked": 173, "skipped": 77, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=43
- aggregate_risk: ok open=17.6309 cap=161.9496 used=0.1495 remaining=137.7385 replayed=12 no_new_bars=0
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:DKNG"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:QCOM"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
