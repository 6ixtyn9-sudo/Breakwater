# Breakwater daily print — 2026-11-24 18:38 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **383.73 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2422.42 ZAR** (seed 2000) | lifetime: **+422.42 ZAR** | closed: 627
- Today: 0 closed, **+0.00 ZAR**
- 7d: **+34.19 ZAR** | 30d: **+135.24 ZAR**

## 2b. Claimed vs realised

- Book: 44 slices (native 24 | hip3 20); validated pools: native 259 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 44 book slices present in the validated pools): +0.335% | at 145.69 ZAR mean notional/trade: +0.49 ZAR/trade
- Realised (627 real closes per lane_gate._is_real_close, net of fees): +0.67 ZAR/trade | sd 4.78 | SE 0.19
- Gap: +0.19 ZAR/trade | t = +0.97 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.519% over 24/24 slices (pool 259) ~ +0.75 ZAR | realised 581 closes +0.80 ZAR sd 4.76 SE 0.20 | gap +0.06 t +0.28 | NOT ESTABLISHED
- hip3: claimed median +0.062% over 20/20 slices (pool 160) ~ +0.10 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.07 t -1.51 | NOT ESTABLISHED
- Ledger: 757 decision rows; 627 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 130 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 581 | wins: 295 | win%: 50.8 | P&L: **+466.92 ZAR** | today: +0.00 | 7d: +34.19 | 30d: +135.24
- By exit: target +516.3, trail_stop +336.5, horizon +72.9, max_bars +2.8, regime_shift -11.9, stop -449.5
- By entry regime (n/pnl): neutral 235/+250.6, bull 122/+199.3, bear 224/+17.1
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_adx_14:1:SHORT:h20 4n/4w +53.91; feat_overnight_ret:1:SHORT:h24 2n/2w +26.35; feat_trend_neutral:0:SHORT:h24 5n/5w +24.80
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_funding_cum_24:0:SHORT:h24 5n/1w -16.09; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_macd_12_26:2:SHORT:h15 3n/0w -11.55; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; BTCUSDC 70n +25.20; ENAUSDC 7n +23.48; SOLUSDC 70n +22.00
- Worst pairs: ZECUSDC 17n -21.96; UNIUSDC 15n -17.05; DOGEUSDC 20n -16.39; ETHZAR 4n -14.36; LTCUSDC 2n -6.24

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 5 open, stop-risk **18.69 ZAR**
  - XMRUSDC SELL ntl=123 risk=4.75 bars=3 stop=515.48500000000001725 peak=503.5
  - XRPUSDC SELL ntl=123 risk=4.75 bars=7 stop=0.964575000000000005 peak=0.93442
  - SOLUSDC SELL ntl=123 risk=4.69 bars=8 stop=73.4062500000000060 peak=70.942
  - ETHUSDC SELL ntl=123 risk=4.50 bars=9 stop=1753.4250000000000030 peak=1707.0
  - BTCUSDC SELL ntl=123 risk=0.00 bars=28 stop=61621.500000000000050 peak=64575.0

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **18.69 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **18.69 / 172.88 ZAR | 11.7% | ok**
- Remaining: 152.6446 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 84, "skipped": 84, "slice_full": 0, "slot_full": 0}, "native": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 37, "signals": 71, "skipped": 34, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **XMRUSDC** 4.7527 ZAR
- positions without bars: 0 | replayed: 5 | invalid: 0

## 6. Monitored books

- Native: 24 | HIP-3: 20
- Native top (by paper P&L):
  - `feat_vol_regime:2:SHORT:h24` edge=0.0045 n=9589 p=0.4583 src=validated_walk_forward unproven=False paper=2n/+3.02
  - `feat_close_position:0:SHORT:h24` edge=0.0069 n=9867 p=0.7850 src=validated_walk_forward unproven=False paper=1n/+2.70
  - `feat_oi_chg_24:2:SHORT:h20` edge=0.0167 n=4777 p=0.0422 src=validated_walk_forward unproven=False paper=1n/+2.26
  - `feat_oi_chg_24@oi_hi:2:SHORT:h24` edge=0.0100 n=1866 p=0.3653 src=validated_walk_forward unproven=False paper=1n/+1.58
  - `feat_bb_width_20:2:SHORT:h24` edge=0.0062 n=9945 p=0.0684 src=validated_walk_forward unproven=False paper=1n/+1.24
  - `feat_buy_vol_ratio:0:SHORT:h24` edge=0.0069 n=9867 p=0.7850 src=validated_walk_forward unproven=False paper=4n/+1.10
  - `feat_oi_chg_24@oi_mid:2:SHORT:h15` edge=0.0100 n=1843 p=0.1562 src=validated_walk_forward unproven=False paper=1n/+0.63
  - `feat_bb_squeeze_20:2:SHORT:h24` edge=0.0050 n=8725 p=0.0229 src=validated_walk_forward unproven=False paper=2n/+0.22
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

- Latest research: 2026-11-24T00:33:13.459671+00:00 | discovered 2240 | validated 259 | reg-confounded 1044 | hostile-unproven 20
- floors: "" | book: {"rows": 26, "by_status": {"decayed": 2, "monitored": 22, "cooldown": 2}, "in_validated_pool": 26, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=1120 validated=1120 passing=259 eligible=611 best=163.3b best_fail=regime_confounded
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=576 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_ema_cross_10_20:L0S2:h20: mean=+9.7b t_no=2.09 folds=11100 mkt_corr=-0.53 dd=161b legs=10.5/11.4 fail=n_nonoverlap,folds,market_corr
  - feat_rsi_7:L0S2:h24: mean=-15.5b t_no=1.88 folds=11100 mkt_corr=-0.54 dd=377b legs=10.3/11.4 fail=n_nonoverlap,mean<=0,t_nonoverlap,folds,market_corr
  - feat_ext_vs_ma_50:L0S2:h24: mean=+2.0b t_no=1.78 folds=00011 mkt_corr=-0.56 dd=220b legs=12.3/10.7 fail=n_nonoverlap,t_nonoverlap,folds,market_corr
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

- Label: **bear** | breadth bear=0.8667 bull=0.0667 neutral=0.0667 | symbols=15
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 11 / bull 0
- as_of: 2026-11-24T18:35:35Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 1120 | eligible: 931 | observations: 4353 | armable: **2693**
- Armable slices: feat_adx_14:1:SHORT:h12, feat_adx_14:2:SHORT:h20, feat_adx_14:2:SHORT:h24, feat_asia_range:0:SHORT:h12, feat_asia_range:0:SHORT:h15, feat_asia_range:0:SHORT:h20, feat_asia_range:0:SHORT:h24, feat_asia_vol:0:SHORT:h24, feat_atr_norm_ext:0:SHORT:h20, feat_atr_norm_ext:0:SHORT:h24, feat_atr_norm_ext:2:SHORT:h12, feat_atr_norm_ext:2:SHORT:h15, feat_atr_norm_ext:2:SHORT:h20, feat_atr_norm_ext:2:SHORT:h24, feat_atr_percent:2:SHORT:h20, feat_atr_percent:2:SHORT:h24, feat_atr_ratio:1:SHORT:h12, feat_atr_ratio:1:SHORT:h15, feat_bb_pos_20:0:SHORT:h15, feat_bb_pos_20:0:SHORT:h20, feat_bb_pos_20:2:SHORT:h12, feat_bb_pos_20:2:SHORT:h15, feat_bb_pos_20:2:SHORT:h24, feat_bb_squeeze_20:1:SHORT:h12, feat_bb_squeeze_20:1:SHORT:h15, feat_bb_squeeze_20:1:SHORT:h20, feat_bb_squeeze_20:1:SHORT:h24, feat_bb_squeeze_20:2:SHORT:h12, feat_bb_squeeze_20:2:SHORT:h15, feat_bb_squeeze_20:2:SHORT:h20, feat_bb_squeeze_20:2:SHORT:h24, feat_bb_width_20:1:SHORT:h15, feat_bb_width_20:2:SHORT:h15, feat_bb_width_20:2:SHORT:h20, feat_bb_width_20:2:SHORT:h24, feat_book_imb_5:0:SHORT:h12, feat_book_imb_5:0:SHORT:h15, feat_book_imb_5:0:SHORT:h20, feat_book_imb_5:1:SHORT:h15, feat_book_imb_5:2:SHORT:h20, feat_book_imb_5:2:SHORT:h24, feat_book_imb_5@oi_hi:0:SHORT:h15, feat_book_imb_5@oi_hi:0:SHORT:h20, feat_book_imb_5@oi_hi:0:SHORT:h24, feat_book_imb_5@oi_hi:1:SHORT:h12, feat_book_imb_5@oi_hi:1:SHORT:h15, feat_book_imb_5@oi_hi:1:SHORT:h20, feat_book_imb_5@oi_hi:1:SHORT:h24, feat_book_imb_5@oi_hi:2:SHORT:h20, feat_book_imb_5@oi_hi:2:SHORT:h24, feat_book_imb_5@oi_lo:0:SHORT:h12, feat_book_imb_5@oi_lo:0:SHORT:h15, feat_book_imb_5@oi_lo:0:SHORT:h20, feat_book_imb_5@oi_lo:0:SHORT:h24, feat_book_imb_5@oi_lo:2:SHORT:h20, feat_book_imb_5@oi_mid:0:SHORT:h15, feat_book_imb_5@oi_mid:1:SHORT:h12, feat_book_imb_5@oi_mid:1:SHORT:h15, feat_book_imb_5@oi_mid:1:SHORT:h20, feat_book_imb_5@oi_mid:1:SHORT:h24, feat_book_imb_5@oi_mid:2:SHORT:h15, feat_buy_vol_ratio:1:SHORT:h15, feat_buy_vol_ratio:1:SHORT:h24, feat_buy_vol_ratio:2:SHORT:h12, feat_buy_vol_ratio:2:SHORT:h15, feat_buy_vol_ratio:2:SHORT:h20, feat_buy_vol_ratio:2:SHORT:h24, feat_cci_20:0:SHORT:h15, feat_cci_20:0:SHORT:h20, feat_cci_20:2:SHORT:h12, feat_cci_20:2:SHORT:h24, feat_close_pos_ma:1:SHORT:h12, feat_close_pos_ma:1:SHORT:h15, feat_close_pos_ma:1:SHORT:h20, feat_close_pos_ma:1:SHORT:h24, feat_close_pos_ma:2:SHORT:h12, feat_close_pos_ma:2:SHORT:h15, feat_close_pos_ma:2:SHORT:h20, feat_close_pos_ma:2:SHORT:h24, feat_close_position:1:SHORT:h15, feat_close_position:1:SHORT:h24, feat_close_position:2:SHORT:h12, feat_close_position:2:SHORT:h15, feat_close_position:2:SHORT:h20, feat_close_position:2:SHORT:h24, feat_donchian_break:0:SHORT:h20, feat_donchian_break:0:SHORT:h24, feat_donchian_break:2:SHORT:h12, feat_donchian_break:2:SHORT:h15, feat_donchian_break:2:SHORT:h20, feat_donchian_break:2:SHORT:h24, feat_donchian_width_20:1:SHORT:h12, feat_donchian_width_20:1:SHORT:h15, feat_donchian_width_20:1:SHORT:h20, feat_donchian_width_20:1:SHORT:h24, feat_donchian_width_20:2:SHORT:h20, feat_donchian_width_20:2:SHORT:h24, feat_ema_cross_10_20:0:SHORT:h24, feat_ema_cross_10_20:1:SHORT:h12, feat_ext_strength:0:SHORT:h20, feat_ext_strength:0:SHORT:h24, feat_ext_strength:1:SHORT:h15, feat_ext_strength:2:SHORT:h12, feat_ext_strength:2:SHORT:h15, feat_ext_strength:2:SHORT:h20, feat_ext_strength:2:SHORT:h24, feat_ext_vs_ma_10:0:SHORT:h20, feat_ext_vs_ma_10:0:SHORT:h24, feat_ext_vs_ma_10:2:SHORT:h12, feat_ext_vs_ma_10:2:SHORT:h24, feat_ext_vs_ma_20:0:SHORT:h20, feat_ext_vs_ma_20:0:SHORT:h24, feat_ext_vs_ma_20:2:SHORT:h12, feat_ext_vs_ma_20:2:SHORT:h15, feat_ext_vs_ma_20:2:SHORT:h20, feat_ext_vs_ma_20:2:SHORT:h24, feat_ext_vs_ma_50:1:SHORT:h12, feat_ext_vs_ma_50:1:SHORT:h15, feat_funding_cum_24:0:SHORT:h24, feat_funding_cum_24:2:SHORT:h15, feat_funding_cum_24:2:SHORT:h20, feat_funding_cum_24:2:SHORT:h24, feat_funding_cum_24@oi_hi:0:SHORT:h24, feat_funding_cum_24@oi_hi:2:SHORT:h12, feat_funding_cum_24@oi_hi:2:SHORT:h15, feat_funding_cum_24@oi_hi:2:SHORT:h20, feat_funding_cum_24@oi_hi:2:SHORT:h24, feat_funding_cum_24@oi_lo:0:SHORT:h15, feat_funding_cum_24@oi_lo:0:SHORT:h20, feat_funding_cum_24@oi_lo:0:SHORT:h24, feat_funding_cum_24@oi_lo:1:SHORT:h15, feat_funding_cum_24@oi_lo:1:SHORT:h20, feat_funding_cum_24@oi_lo:1:SHORT:h24, feat_funding_cum_24@oi_mid:1:SHORT:h12, feat_funding_cum_24@oi_mid:1:SHORT:h15, feat_funding_cum_24@oi_mid:1:SHORT:h20, feat_funding_cum_24@oi_mid:1:SHORT:h24, feat_funding_cum_24@oi_mid:2:SHORT:h15, feat_funding_cum_24@oi_mid:2:SHORT:h24, feat_funding_rate:0:SHORT:h12, feat_funding_rate:0:SHORT:h15, feat_funding_rate:0:SHORT:h20, feat_funding_rate:0:SHORT:h24, feat_funding_rate@oi_hi:0:SHORT:h15, feat_funding_rate@oi_hi:0:SHORT:h20, feat_funding_rate@oi_hi:0:SHORT:h24, feat_funding_rate@oi_hi:1:SHORT:h12, feat_funding_rate@oi_hi:1:SHORT:h15, feat_funding_rate@oi_lo:1:SHORT:h12, feat_funding_rate@oi_lo:1:SHORT:h15, feat_funding_rate@oi_lo:1:SHORT:h20, feat_funding_rate@oi_lo:1:SHORT:h24, feat_funding_rate@oi_mid:0:SHORT:h12, feat_funding_rate@oi_mid:0:SHORT:h15, feat_funding_rate@oi_mid:0:SHORT:h24, feat_gap:0:SHORT:h15, feat_gap:0:SHORT:h20, feat_gap:0:SHORT:h24, feat_gap:1:SHORT:h15, feat_gap:1:SHORT:h20, feat_gap:1:SHORT:h24, feat_gap:2:SHORT:h24, feat_gap_fill_ratio:0:SHORT:h12, feat_gap_fill_ratio:0:SHORT:h15, feat_gap_fill_ratio:0:SHORT:h20, feat_gap_fill_ratio:0:SHORT:h24, feat_gap_fill_ratio:1:SHORT:h12, feat_gap_fill_ratio:1:SHORT:h15, feat_hl_range:1:SHORT:h15, feat_hl_range:1:SHORT:h20, feat_hl_range:1:SHORT:h24, feat_hl_range:2:SHORT:h20, feat_hl_range:2:SHORT:h24, feat_hour_utc:2:SHORT:h12, feat_hour_utc:2:SHORT:h15, feat_hour_utc:2:SHORT:h20, feat_hour_utc:2:SHORT:h24, feat_intraday_mom:1:SHORT:h12, feat_intraday_mom:2:SHORT:h12, feat_intraday_mom:2:SHORT:h15, feat_intraday_mom:2:SHORT:h20, feat_intraday_mom:2:SHORT:h24, feat_kc_width:1:SHORT:h12, feat_kc_width:2:SHORT:h20, feat_kc_width:2:SHORT:h24, feat_keltner_pos:0:SHORT:h20, feat_keltner_pos:0:SHORT:h24, feat_keltner_pos:2:SHORT:h12, feat_keltner_pos:2:SHORT:h15, feat_keltner_pos:2:SHORT:h20, feat_keltner_pos:2:SHORT:h24, feat_macd_12_26:1:SHORT:h12, feat_macd_12_26:1:SHORT:h15, feat_mean_rev_strength:0:SHORT:h12, feat_mean_rev_strength:0:SHORT:h15, feat_mean_rev_strength:0:SHORT:h20, feat_mean_rev_strength:0:SHORT:h24, feat_mean_rev_strength:2:SHORT:h12, feat_mean_rev_strength:2:SHORT:h15, feat_mean_rev_strength:2:SHORT:h20, feat_oi_chg_24:2:SHORT:h12, feat_oi_chg_24:2:SHORT:h15, feat_oi_chg_24:2:SHORT:h20, feat_oi_chg_24:2:SHORT:h24, feat_oi_chg_24@oi_hi:1:SHORT:h12, feat_oi_chg_24@oi_hi:1:SHORT:h15, feat_oi_chg_24@oi_hi:1:SHORT:h20, feat_oi_chg_24@oi_hi:1:SHORT:h24, feat_oi_chg_24@oi_hi:2:SHORT:h12, feat_oi_chg_24@oi_hi:2:SHORT:h15, feat_oi_chg_24@oi_hi:2:SHORT:h20, feat_oi_chg_24@oi_hi:2:SHORT:h24, feat_oi_chg_24@oi_lo:1:SHORT:h12, feat_oi_chg_24@oi_lo:1:SHORT:h15, feat_oi_chg_24@oi_lo:1:SHORT:h20, feat_oi_chg_24@oi_lo:2:SHORT:h15, feat_oi_chg_24@oi_mid:0:SHORT:h12, feat_oi_chg_24@oi_mid:0:SHORT:h15, feat_oi_chg_24@oi_mid:0:SHORT:h20, feat_oi_chg_24@oi_mid:0:SHORT:h24, feat_oi_chg_24@oi_mid:2:SHORT:h12, feat_oi_chg_24@oi_mid:2:SHORT:h15, feat_oi_ret_div:0:SHORT:h12, feat_oi_ret_div:0:SHORT:h15, feat_oi_ret_div:2:SHORT:h15, feat_oi_ret_div@oi_hi:0:SHORT:h12, feat_oi_ret_div@oi_hi:0:SHORT:h15, feat_oi_ret_div@oi_hi:0:SHORT:h20, feat_oi_ret_div@oi_hi:1:SHORT:h12, feat_oi_ret_div@oi_hi:1:SHORT:h15, feat_oi_ret_div@oi_hi:1:SHORT:h20, feat_oi_ret_div@oi_hi:1:SHORT:h24, feat_oi_ret_div@oi_hi:2:SHORT:h24, feat_oi_ret_div@oi_lo:0:SHORT:h20, feat_oi_ret_div@oi_lo:1:SHORT:h12, feat_oi_ret_div@oi_lo:1:SHORT:h15, feat_oi_ret_div@oi_lo:1:SHORT:h20, feat_oi_ret_div@oi_mid:0:SHORT:h15, feat_oi_ret_div@oi_mid:2:SHORT:h12, feat_oi_ret_div@oi_mid:2:SHORT:h15, feat_overnight_ret:0:SHORT:h12, feat_overnight_ret:0:SHORT:h15, feat_overnight_ret:0:SHORT:h20, feat_overnight_ret:0:SHORT:h24, feat_overnight_ret:1:SHORT:h12, feat_overnight_ret:1:SHORT:h15, feat_overnight_ret:1:SHORT:h20, feat_overnight_ret:1:SHORT:h24, feat_overnight_ret:2:SHORT:h20, feat_overnight_ret:2:SHORT:h24, feat_premium:0:SHORT:h24, feat_premium:1:SHORT:h15, feat_premium:2:SHORT:h12, feat_premium:2:SHORT:h15, feat_premium:2:SHORT:h20, feat_premium:2:SHORT:h24, feat_premium@oi_hi:0:SHORT:h15, feat_premium@oi_hi:0:SHORT:h20, feat_premium@oi_hi:0:SHORT:h24, feat_premium@oi_hi:1:SHORT:h12, feat_premium@oi_hi:1:SHORT:h15, feat_premium@oi_hi:1:SHORT:h20, feat_premium@oi_hi:1:SHORT:h24, feat_premium@oi_hi:2:SHORT:h24, feat_premium@oi_lo:0:SHORT:h15, feat_premium@oi_lo:0:SHORT:h20, feat_premium@oi_lo:0:SHORT:h24, feat_premium@oi_lo:2:SHORT:h12, feat_premium@oi_lo:2:SHORT:h15, feat_premium@oi_lo:2:SHORT:h20, feat_premium@oi_lo:2:SHORT:h24, feat_premium@oi_mid:1:SHORT:h12, feat_premium@oi_mid:1:SHORT:h15, feat_premium@oi_mid:1:SHORT:h20, feat_premium@oi_mid:1:SHORT:h24, feat_premium@oi_mid:2:SHORT:h15, feat_price_accel:1:SHORT:h12, feat_price_accel:1:SHORT:h15, feat_price_accel:1:SHORT:h20, feat_price_accel:1:SHORT:h24, feat_price_accel:2:SHORT:h15, feat_price_accel:2:SHORT:h20, feat_price_accel:2:SHORT:h24, feat_price_roc_5:0:SHORT:h20, feat_price_roc_5:0:SHORT:h24, feat_price_roc_5:1:SHORT:h15, feat_price_roc_5:2:SHORT:h12, feat_price_roc_5:2:SHORT:h24, feat_range_expansion:1:SHORT:h12, feat_range_expansion:1:SHORT:h15, feat_range_expansion:1:SHORT:h20, feat_range_expansion:1:SHORT:h24, feat_range_pos_20:0:SHORT:h12, feat_range_pos_20:0:SHORT:h15, feat_range_pos_20:0:SHORT:h20, feat_range_pos_20:0:SHORT:h24, feat_range_pos_20:2:SHORT:h12, feat_range_pos_20:2:SHORT:h15, feat_range_pos_20:2:SHORT:h20, feat_range_pos_20:2:SHORT:h24, feat_range_pos_50:0:SHORT:h20, feat_range_pos_50:0:SHORT:h24, feat_range_pos_50:1:SHORT:h12, feat_range_pos_50:1:SHORT:h15, feat_realized_vol_20:1:SHORT:h12, feat_realized_vol_20:1:SHORT:h15, feat_realized_vol_20:1:SHORT:h20, feat_realized_vol_20:1:SHORT:h24, feat_realized_vol_20:2:SHORT:h24, feat_ret_10:0:SHORT:h20, feat_ret_10:1:SHORT:h15, feat_ret_1:2:SHORT:h12, feat_ret_1:2:SHORT:h15, feat_ret_1:2:SHORT:h20, feat_ret_1:2:SHORT:h24, feat_ret_20:0:SHORT:h24, feat_ret_20:2:SHORT:h12, feat_ret_20:2:SHORT:h15, feat_ret_20:2:SHORT:h20, feat_ret_20:2:SHORT:h24, feat_ret_3:0:SHORT:h20, feat_ret_3:0:SHORT:h24, feat_ret_3:2:SHORT:h12, feat_ret_3:2:SHORT:h15, feat_ret_3:2:SHORT:h20, feat_ret_3:2:SHORT:h24, feat_ret_5:0:SHORT:h20, feat_ret_5:0:SHORT:h24, feat_ret_5:1:SHORT:h15, feat_ret_5:2:SHORT:h12, feat_ret_5:2:SHORT:h24, feat_ret_autocorr:0:SHORT:h15, feat_ret_autocorr:0:SHORT:h20, feat_ret_autocorr:0:SHORT:h24, feat_ret_autocorr:2:SHORT:h12, feat_ret_autocorr:2:SHORT:h15, feat_ret_autocorr:2:SHORT:h20, feat_ret_autocorr:2:SHORT:h24, feat_ret_sign_streak:2:SHORT:h12, feat_ret_sign_streak:2:SHORT:h15, feat_ret_sign_streak:2:SHORT:h20, feat_ret_sign_streak:2:SHORT:h24, feat_ret_vol:0:SHORT:h20, feat_ret_vol:0:SHORT:h24, feat_ret_vol:2:SHORT:h12, feat_ret_vol:2:SHORT:h15, feat_ret_vol:2:SHORT:h20, feat_ret_vol:2:SHORT:h24, feat_rsi_14:0:SHORT:h20, feat_rsi_14:0:SHORT:h24, feat_rsi_14:1:SHORT:h15, feat_rsi_14:1:SHORT:h20, feat_rsi_14:2:SHORT:h12, feat_rsi_14:2:SHORT:h15, feat_rsi_14:2:SHORT:h20, feat_rsi_14:2:SHORT:h24, feat_rsi_21:0:SHORT:h20, feat_rsi_21:0:SHORT:h24, feat_rsi_21:1:SHORT:h15, feat_rsi_21:2:SHORT:h12, feat_rsi_21:2:SHORT:h15, feat_rsi_21:2:SHORT:h20, feat_rsi_21:2:SHORT:h24, feat_rsi_7:0:SHORT:h20, feat_rsi_7:0:SHORT:h24, feat_rsi_7:1:SHORT:h12, feat_rsi_7:1:SHORT:h15, feat_rsi_7:1:SHORT:h20, feat_rsi_7:1:SHORT:h24, feat_rsi_7:2:SHORT:h12, feat_rsi_7:2:SHORT:h15, feat_rsi_7:2:SHORT:h24, feat_rsi_divergence:0:SHORT:h20, feat_rsi_divergence:1:SHORT:h15, feat_rsi_divergence:2:SHORT:h12, feat_rsi_divergence:2:SHORT:h15, feat_rsi_divergence:2:SHORT:h20, feat_rsi_divergence:2:SHORT:h24, feat_session_mom:1:SHORT:h12, feat_session_mom:2:SHORT:h12, feat_session_mom:2:SHORT:h15, feat_session_mom:2:SHORT:h20, feat_session_mom:2:SHORT:h24, feat_squeeze:1:SHORT:h12, feat_squeeze:1:SHORT:h15, feat_squeeze:1:SHORT:h20, feat_squeeze:1:SHORT:h24, feat_squeeze:2:SHORT:h20, feat_squeeze:2:SHORT:h24, feat_stoch_d_14:0:SHORT:h15, feat_stoch_d_14:2:SHORT:h12, feat_stoch_d_14:2:SHORT:h15, feat_stoch_d_14:2:SHORT:h20, feat_stoch_d_14:2:SHORT:h24, feat_stoch_k_14:1:SHORT:h12, feat_stoch_k_14:2:SHORT:h12, feat_stoch_k_14:2:SHORT:h15, feat_stoch_k_14:2:SHORT:h20, feat_stoch_k_14:2:SHORT:h24, feat_time_since_high_20:0:SHORT:h12, feat_time_since_high_20:0:SHORT:h15, feat_time_since_high_20:0:SHORT:h20, feat_time_since_high_20:0:SHORT:h24, feat_time_since_high_20:1:SHORT:h12, feat_time_since_high_20:1:SHORT:h15, feat_time_since_high_20:1:SHORT:h20, feat_time_since_low_20:1:SHORT:h12, feat_time_since_low_20:1:SHORT:h15, feat_time_since_low_20:1:SHORT:h20, feat_time_since_low_20:1:SHORT:h24, feat_trend_neutral:0:SHORT:h12, feat_trend_neutral:0:SHORT:h15, feat_trend_neutral:0:SHORT:h20, feat_trend_neutral:0:SHORT:h24, feat_trend_slope_20:1:SHORT:h12, feat_trend_slope_20:1:SHORT:h15, feat_trend_slope_20:2:SHORT:h20, feat_trend_slope_20:2:SHORT:h24, feat_trend_strength_20:0:SHORT:h12, feat_trend_strength_20:2:SHORT:h15, feat_trend_strength_20:2:SHORT:h20, feat_trend_strength_20:2:SHORT:h24, feat_vol_breakout:0:SHORT:h20, feat_vol_breakout:0:SHORT:h24, feat_vol_breakout:2:SHORT:h12, feat_vol_breakout:2:SHORT:h15, feat_vol_breakout:2:SHORT:h20, feat_vol_breakout:2:SHORT:h24, feat_vol_breakout_strength:1:SHORT:h12, feat_vol_breakout_strength:1:SHORT:h15, feat_vol_breakout_strength:1:SHORT:h20, feat_vol_breakout_strength:1:SHORT:h24, feat_vol_breakout_strength:2:SHORT:h15, feat_vol_breakout_strength:2:SHORT:h20, feat_vol_breakout_strength:2:SHORT:h24, feat_vol_contraction:0:SHORT:h24, feat_vol_contraction:2:SHORT:h20, feat_vol_contraction:2:SHORT:h24, feat_vol_of_vol:1:SHORT:h12, feat_vol_of_vol:1:SHORT:h15, feat_vol_of_vol:1:SHORT:h24, feat_vol_regime:0:SHORT:h24, feat_vol_regime:2:SHORT:h20, feat_vol_regime:2:SHORT:h24, feat_vol_roc_20:1:SHORT:h12, feat_vol_roc_20:1:SHORT:h15, feat_vol_roc_20:1:SHORT:h20, feat_vol_roc_20:1:SHORT:h24, feat_vol_roc_20:2:SHORT:h24, feat_vol_sma_ratio:0:SHORT:h12, feat_vol_sma_ratio:0:SHORT:h15, feat_vol_sma_ratio:0:SHORT:h24, feat_vol_sma_ratio:2:SHORT:h12, feat_vol_sma_ratio:2:SHORT:h15, feat_vol_trend:1:SHORT:h12, feat_vol_trend:1:SHORT:h15, feat_vol_trend:1:SHORT:h20, feat_vol_trend:1:SHORT:h24, feat_vol_trend:2:SHORT:h15, feat_vol_trend:2:SHORT:h20, feat_vol_trend:2:SHORT:h24, feat_vwap_dist:0:SHORT:h15, feat_vwap_dist:0:SHORT:h20, feat_vwap_dist:0:SHORT:h24, feat_vwap_dist:2:SHORT:h12, feat_vwap_dist:2:SHORT:h15, feat_vwap_dist:2:SHORT:h20, feat_vwap_dist:2:SHORT:h24, feat_vwap_lower_dist:0:SHORT:h15, feat_vwap_lower_dist:0:SHORT:h20, feat_vwap_lower_dist:0:SHORT:h24, feat_vwap_lower_dist:2:SHORT:h12, feat_vwap_lower_dist:2:SHORT:h15, feat_vwap_lower_dist:2:SHORT:h20, feat_vwap_lower_dist:2:SHORT:h24, feat_vwap_upper_dist:0:SHORT:h15, feat_vwap_upper_dist:0:SHORT:h20, feat_vwap_upper_dist:2:SHORT:h12, feat_vwap_upper_dist:2:SHORT:h15, feat_vwap_upper_dist:2:SHORT:h20, feat_vwap_upper_dist:2:SHORT:h24, feat_williams_r_14:0:SHORT:h12, feat_williams_r_14:0:SHORT:h15, feat_williams_r_14:0:SHORT:h20, feat_williams_r_14:0:SHORT:h24, feat_williams_r_14:1:SHORT:h12, feat_zscore_20:0:SHORT:h15, feat_zscore_20:0:SHORT:h20, feat_zscore_20:2:SHORT:h12, feat_zscore_20:2:SHORT:h15, feat_zscore_20:2:SHORT:h24
- Armable pairs: BTCUSDC, ETHUSDC, HYPEUSDC, LITUSDC, MONUSDC, NEARUSDC, PUMPUSDC, SOLUSDC, TRUMPUSDC, UNIUSDC, VVVUSDC, XMRUSDC, XRPUSDC, ZECUSDC, ZROUSDC
  - `feat_oi_chg_24@oi_mid:2:SHORT:h24` edge=163.3b n=1820 breadth=13 validated=False prov=False armable=False (regime_confounded)
  - `feat_oi_ret_div@oi_lo:0:SHORT:h24` edge=140.3b n=2427 breadth=13 validated=False prov=False armable=False (regime_confounded)
  - `feat_oi_chg_24@oi_lo:1:SHORT:h24` edge=136.0b n=2122 breadth=13 validated=False prov=False armable=False (regime_confounded)
  - `feat_oi_chg_24:2:SHORT:h24` edge=129.3b n=5941 breadth=39 validated=True prov=False armable=True (ok)
  - `feat_oi_chg_24@oi_lo:2:SHORT:h24` edge=126.4b n=2255 breadth=13 validated=False prov=False armable=False (regime_confounded)
  - `feat_oi_chg_24@oi_mid:2:SHORT:h20` edge=123.7b n=1891 breadth=13 validated=False prov=False armable=False (regime_confounded)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+26.00 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **24/24** | hip3 **19/20**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 52
  - `feat_adx_14:2:LONG:h12` slice_pnl=-1.83
  - `feat_adx_14:2:LONG:h15` slice_pnl=-3.92
  - `feat_atr_norm_ext:2:LONG:h13` slice_pnl=-4.88
  - `feat_atr_percent:2:LONG:h12` slice_pnl=-1.44
  - `feat_atr_ratio:0:LONG:h24` slice_pnl=-10.03
  - `feat_bb_squeeze_20:2:LONG:h20` slice_pnl=-10.15
  - `feat_bb_width_20:2:LONG:h15` slice_pnl=-6.62
  - `feat_book_imb_5@oi_hi:1:SHORT:h20` slice_pnl=-3.93
  - `feat_buy_vol_ratio:2:LONG:h24` slice_pnl=-6.57
  - `feat_cci_20:0:LONG:h24` slice_pnl=-17.74
  - `feat_cci_20:2:SHORT:h24` slice_pnl=-7.35
  - `feat_donchian_break:2:LONG:h15` slice_pnl=-2.57
  - `feat_ema_cross_10_20:2:LONG:h12` slice_pnl=-3.12
  - `feat_ema_cross_10_20:2:SHORT:h24` slice_pnl=-5.49
  - `feat_ext_vs_ma_50:0:LONG:h20` slice_pnl=-11.21
  - `feat_funding_cum_24:0:SHORT:h24` slice_pnl=-16.09
  - `feat_funding_cum_24:2:SHORT:h12` slice_pnl=-1.14
  - `feat_funding_rate:2:SHORT:h12` slice_pnl=-7.96
  - `feat_hour_utc:2:LONG:h15` slice_pnl=-1.61
  - `feat_kc_width:2:LONG:h12` slice_pnl=-6.60
  - `feat_kc_width:2:LONG:h15` slice_pnl=-0.19
  - `feat_macd_12_26:2:SHORT:h15` slice_pnl=-11.55
  - `feat_oi_ret_div@oi_hi:2:SHORT:h24` slice_pnl=-1.60
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
  - `feat_trend_strength_20:2:SHORT:h24` slice_pnl=-5.00
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

- Latest scan 2026-11-24T18:03:55: errors=0 signals=155 regime_blocked=95
- this cycle: closed=0 new_signals=155 skipped=118 slot_full=0 slice_full=0 pair_held=37
- Action funnel: regime_blocked=95 | lane_gate_blocked=1 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=37 | cluster_cap=0 | family_vetoed=3 | slot_full=0 | skipped=118
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "cluster_cap": 0, "family_vetoed": 3, "lane_gate_blocked": 1, "pair_held": 37, "regime_blocked": 95, "skipped": 118, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=52
- aggregate_risk: ok open=18.6881 cap=172.8762 used=0.1170 remaining=152.6446 replayed=5 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
