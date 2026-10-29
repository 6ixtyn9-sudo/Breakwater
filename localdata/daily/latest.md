# Breakwater daily print — 2026-10-29 04:05 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

> ## COMA ALARM — NATIVE

> No **proven** slice in this lane. Auditions can still open entries, so
> this is not a dead lane: it trades, but nothing in it trades on a record
> it earned, so it cannot unfreeze itself. The runner will keep reporting
> operational, which is why this block exists. Attention, not intervention.

## 1. Posture

- Mode: **readonly** | VALR equity: **439.57 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2259.34 ZAR** (seed 2000) | lifetime: **+259.34 ZAR** | closed: 497
- Today: 2 closed, **+3.98 ZAR**
- 7d: **-11.49 ZAR** | 30d: **-196.83 ZAR**

## 2b. Claimed vs realised

- Book: 94 slices (native 73 | hip3 21); validated pools: native 208 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 94 book slices present in the validated pools): +0.218% | at 152.55 ZAR mean notional/trade: +0.33 ZAR/trade
- Realised (497 real closes per lane_gate._is_real_close, net of fees): +0.52 ZAR/trade | sd 4.87 | SE 0.22
- Gap: +0.19 ZAR/trade | t = +0.86 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.293% over 73/73 slices (pool 208) ~ +0.44 ZAR | realised 451 closes +0.67 ZAR sd 4.85 SE 0.23 | gap +0.23 t +1.01 | NOT ESTABLISHED
- hip3: claimed median +0.065% over 21/21 slices (pool 160) ~ +0.11 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.08 t -1.52 | NOT ESTABLISHED
- Ledger: 600 decision rows; 497 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 103 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 451 | wins: 216 | win%: 47.9 | P&L: **+303.84 ZAR** | today: +3.98 | 7d: -11.49 | 30d: -160.67
- By exit: target +516.3, trail_stop +85.0, horizon +70.5, max_bars +2.8, regime_shift -11.9, stop -358.7
- By entry regime (n/pnl): neutral 176/+217.8, bull 115/+179.3, bear 160/-93.3
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82; feat_range_pos_50:2:SHORT:h24 3n/0w -10.55
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPZAR 2n +18.07; XMRUSDC 9n +11.84; AAVEUSDC 3n +9.47
- Worst pairs: UNIUSDC 9n -26.80; ETHUSDC 58n -24.41; ZECUSDC 15n -23.41; HYPEUSDC 34n -18.89; XRPUSDC 47n -16.05

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: -36.16
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 7 open, stop-risk **23.31 ZAR**
  - SUIUSDC SELL ntl=115 risk=4.55 bars=5 stop=0.9863650000000000810 peak=0.95438
  - ZECUSDC SELL ntl=115 risk=4.52 bars=18 stop=1362.9750000000001620 peak=1326.5
  - XRPUSDC SELL ntl=115 risk=3.46 bars=0 stop=1.3369250000000001870 peak=1.2978
  - HYPEUSDC SELL ntl=115 risk=3.28 bars=9 stop=82.55025000000000735 peak=81.997
  - ETHUSDC SELL ntl=115 risk=3.21 bars=4 stop=2429.8750000000001780 peak=2366.2
  - SOLUSDC SELL ntl=115 risk=2.28 bars=22 stop=103.99999999999999985 peak=103.85
  - BTCUSDC SELL ntl=115 risk=2.01 bars=17 stop=82895.72500 peak=81780.0

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **23.31 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **23.31 / 160.85 ZAR | 15.7% | ok**
- Remaining: 135.5214 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 39, "skipped": 39, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 0, "opened": 1, "pair_held": 10, "signals": 47, "skipped": 36, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **SUIUSDC** 4.5512 ZAR
- positions without bars: 0 | replayed: 7 | invalid: 0

## 6. Monitored books

- Native: 73 | HIP-3: 21
- Native top (by paper P&L):
  - `feat_donchian_break:2:SHORT:h24` edge=0.0061 n=8313 p=0.2200 src=validated_walk_forward unproven=False paper=2n/+3.68
  - `feat_rsi_21:2:SHORT:h24` edge=0.0070 n=6576 p=0.0932 src=validated_walk_forward unproven=False paper=2n/+1.17
  - `feat_funding_rate:2:SHORT:h12` edge=0.0052 n=1887 p=0.4153 src=validated_walk_forward unproven=False paper=1n/+0.48
  - `feat_premium:1:SHORT:h24` edge=0.0053 n=7833 p=0.6893 src=validated_walk_forward unproven=False paper=1n/+0.05
  - `feat_premium:2:SHORT:h15` edge=0.0080 n=2968 p=0.1232 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_macd_12_26:2:SHORT:h12` edge=0.0049 n=6633 p=0.0241 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vwap_dist:2:SHORT:h12` edge=0.0038 n=8106 p=0.1017 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vwap_lower_dist:2:SHORT:h12` edge=0.0038 n=8576 p=0.0958 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Latest research: 2026-10-29T00:52:25.439956+00:00 | discovered 2080 | validated 208 | reg-confounded 1060 | hostile-unproven 111
- floors: "" | book: {"rows": 78, "by_status": {"monitored": 72, "decayed": 2, "cooldown": 4}, "in_validated_pool": 78, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=1040 validated=1040 passing=208 eligible=160 best=286.8b best_fail=temporal_pass
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=568 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_book_imb_5:L0S2:h20: mean=-16.6b t_no=7.37 folds=00000 mkt_corr=+0.59 dd=0b legs=12.3/13.9 fail=n_nonoverlap,mean<=0,folds,market_corr
  - feat_vwap_lower_dist:L0S2:h15: mean=+9.3b t_no=2.64 folds=01100 mkt_corr=-0.04 dd=232b legs=11.1/10.7 fail=folds
  - feat_ret_1:L0S2:h24: mean=-6.0b t_no=2.37 folds=00101 mkt_corr=-0.01 dd=249b legs=10.3/11.4 fail=n_nonoverlap,mean<=0,folds
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

- Label: **bear** | breadth bear=0.625 bull=0.125 neutral=0.25 | symbols=16
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 2 / bull 0
- as_of: 2026-10-29T03:35:31Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 1040 | eligible: 309 | observations: 703 | armable: **481**
- Armable slices: feat_asia_vol:2:SHORT:h24, feat_atr_ratio:1:SHORT:h20, feat_bb_squeeze_20:2:SHORT:h20, feat_bb_squeeze_20:2:SHORT:h24, feat_bb_width_20:1:SHORT:h20, feat_bb_width_20:1:SHORT:h24, feat_close_pos_ma:1:SHORT:h24, feat_close_pos_ma:2:SHORT:h12, feat_donchian_width_20:1:SHORT:h20, feat_donchian_width_20:1:SHORT:h24, feat_donchian_width_20:2:SHORT:h24, feat_ema_cross_10_20:2:SHORT:h12, feat_ema_cross_10_20:2:SHORT:h20, feat_ema_cross_10_20:2:SHORT:h24, feat_ext_vs_ma_50:2:SHORT:h12, feat_ext_vs_ma_50:2:SHORT:h15, feat_ext_vs_ma_50:2:SHORT:h20, feat_ext_vs_ma_50:2:SHORT:h24, feat_funding_cum_24:1:SHORT:h12, feat_funding_cum_24:1:SHORT:h15, feat_funding_cum_24:1:SHORT:h20, feat_funding_cum_24:1:SHORT:h24, feat_funding_cum_24:2:SHORT:h12, feat_funding_cum_24:2:SHORT:h15, feat_funding_cum_24:2:SHORT:h20, feat_funding_cum_24:2:SHORT:h24, feat_funding_cum_24@oi_hi:1:SHORT:h12, feat_funding_cum_24@oi_hi:1:SHORT:h15, feat_funding_cum_24@oi_hi:1:SHORT:h20, feat_funding_cum_24@oi_hi:1:SHORT:h24, feat_funding_cum_24@oi_hi:2:SHORT:h12, feat_funding_cum_24@oi_hi:2:SHORT:h15, feat_funding_cum_24@oi_lo:1:SHORT:h12, feat_funding_cum_24@oi_lo:1:SHORT:h15, feat_funding_cum_24@oi_lo:1:SHORT:h20, feat_funding_cum_24@oi_lo:1:SHORT:h24, feat_funding_cum_24@oi_lo:2:SHORT:h12, feat_funding_cum_24@oi_lo:2:SHORT:h15, feat_funding_cum_24@oi_lo:2:SHORT:h20, feat_funding_cum_24@oi_lo:2:SHORT:h24, feat_funding_cum_24@oi_mid:2:SHORT:h12, feat_funding_cum_24@oi_mid:2:SHORT:h15, feat_funding_cum_24@oi_mid:2:SHORT:h20, feat_funding_cum_24@oi_mid:2:SHORT:h24, feat_gap:0:SHORT:h15, feat_gap:0:SHORT:h20, feat_gap:0:SHORT:h24, feat_gap_fill_ratio:1:SHORT:h15, feat_gap_fill_ratio:1:SHORT:h20, feat_hl_range:1:SHORT:h20, feat_hl_range:1:SHORT:h24, feat_intraday_mom:1:SHORT:h20, feat_kc_width:0:SHORT:h12, feat_kc_width:0:SHORT:h15, feat_kc_width:0:SHORT:h20, feat_macd_12_26:2:SHORT:h12, feat_macd_12_26:2:SHORT:h15, feat_macd_12_26:2:SHORT:h20, feat_macd_12_26:2:SHORT:h24, feat_overnight_ret:0:SHORT:h20, feat_overnight_ret:0:SHORT:h24, feat_premium:1:SHORT:h12, feat_premium:1:SHORT:h15, feat_premium:1:SHORT:h20, feat_premium:1:SHORT:h24, feat_premium:2:SHORT:h12, feat_premium:2:SHORT:h15, feat_premium:2:SHORT:h20, feat_premium:2:SHORT:h24, feat_premium@oi_hi:1:SHORT:h12, feat_premium@oi_hi:1:SHORT:h15, feat_premium@oi_hi:1:SHORT:h20, feat_premium@oi_hi:1:SHORT:h24, feat_premium@oi_hi:2:SHORT:h12, feat_premium@oi_hi:2:SHORT:h15, feat_premium@oi_hi:2:SHORT:h20, feat_premium@oi_hi:2:SHORT:h24, feat_premium@oi_lo:1:SHORT:h12, feat_premium@oi_lo:1:SHORT:h15, feat_premium@oi_lo:1:SHORT:h20, feat_premium@oi_lo:1:SHORT:h24, feat_premium@oi_lo:2:SHORT:h12, feat_premium@oi_lo:2:SHORT:h15, feat_premium@oi_lo:2:SHORT:h20, feat_premium@oi_lo:2:SHORT:h24, feat_premium@oi_mid:1:SHORT:h12, feat_premium@oi_mid:2:SHORT:h12, feat_premium@oi_mid:2:SHORT:h15, feat_premium@oi_mid:2:SHORT:h20, feat_premium@oi_mid:2:SHORT:h24, feat_price_accel:1:SHORT:h20, feat_price_accel:1:SHORT:h24, feat_range_expansion:1:SHORT:h24, feat_range_pos_50:2:SHORT:h12, feat_range_pos_50:2:SHORT:h15, feat_range_pos_50:2:SHORT:h20, feat_range_pos_50:2:SHORT:h24, feat_ret_10:2:SHORT:h12, feat_ret_10:2:SHORT:h15, feat_ret_10:2:SHORT:h20, feat_ret_10:2:SHORT:h24, feat_ret_20:2:SHORT:h12, feat_ret_20:2:SHORT:h24, feat_ret_vol:2:SHORT:h12, feat_ret_vol:2:SHORT:h24, feat_rsi_21:2:SHORT:h12, feat_rsi_21:2:SHORT:h15, feat_rsi_21:2:SHORT:h20, feat_rsi_21:2:SHORT:h24, feat_session_mom:1:SHORT:h20, feat_session_mom:1:SHORT:h24, feat_squeeze:1:SHORT:h15, feat_squeeze:1:SHORT:h20, feat_squeeze:1:SHORT:h24, feat_time_since_high_20:0:SHORT:h12, feat_time_since_high_20:0:SHORT:h15, feat_time_since_low_20:1:SHORT:h12, feat_time_since_low_20:1:SHORT:h15, feat_time_since_low_20:1:SHORT:h20, feat_time_since_low_20:1:SHORT:h24, feat_trend_neutral:0:SHORT:h24, feat_trend_slope_20:2:SHORT:h12, feat_trend_slope_20:2:SHORT:h15, feat_trend_slope_20:2:SHORT:h20, feat_trend_slope_20:2:SHORT:h24, feat_trend_strength_20:2:SHORT:h15, feat_trend_strength_20:2:SHORT:h20, feat_trend_strength_20:2:SHORT:h24, feat_vol_breakout:2:SHORT:h12, feat_vol_breakout:2:SHORT:h15, feat_vol_breakout:2:SHORT:h20, feat_vol_breakout:2:SHORT:h24, feat_vol_of_vol:2:SHORT:h24, feat_vol_trend:2:SHORT:h12, feat_vol_trend:2:SHORT:h15, feat_vol_trend:2:SHORT:h20, feat_vol_trend:2:SHORT:h24
- Armable pairs: BTCUSDC, ENAUSDC, ETHUSDC, HYPEUSDC, KPEPEUSDC, LITUSDC, NEARUSDC, PONSUSDC, PUMPUSDC, SOLUSDC, SUIUSDC, VVVUSDC, WLDUSDC, XMRUSDC, XRPUSDC, ZECUSDC
  - `feat_funding_rate@oi_mid:2:SHORT:h24` edge=286.8b n=540 breadth=9 validated=True prov=False armable=True (ok)
  - `feat_funding_cum_24@oi_mid:2:SHORT:h24` edge=282.6b n=611 breadth=8 validated=True prov=False armable=True (ok)
  - `feat_funding_rate@oi_lo:2:SHORT:h24` edge=274.3b n=368 breadth=7 validated=False prov=False armable=True (ok)
  - `feat_funding_rate@oi_lo:1:SHORT:h24` edge=235.0b n=159 breadth=4 validated=True prov=False armable=False (too_few_rows)
  - `feat_funding_rate@oi_lo:2:SHORT:h20` edge=234.8b n=318 breadth=7 validated=False prov=False armable=True (ok)
  - `feat_funding_rate@oi_mid:2:SHORT:h20` edge=231.9b n=414 breadth=8 validated=True prov=False armable=True (ok)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-20.66 | frozen=YES
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3, native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 20
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
  - `feat_intraday_mom:2:LONG:h24` pnl=+7.09
  - `feat_price_roc_5:1:LONG:h24` pnl=+0.70
  - `feat_realized_vol_20:2:LONG:h12` pnl=+0.61
  - `feat_ret_10:2:LONG:h19` pnl=+14.58
  - `feat_ret_20:2:LONG:h14` pnl=+13.42
  - `feat_rsi_divergence:2:LONG:h20` pnl=+8.36
  - `feat_trend_slope_20:2:LONG:h12` pnl=+11.12
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **73/73** | hip3 **19/21**
- **COMA LANES: native** — frozen with no tradable slice on an earned green record; auditions may still open.
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 45
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
  - `feat_ext_vs_ma_50:2:SHORT:h24` lane_not_green
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

- Latest scan 2026-10-29T02:30:09: errors=0 signals=86 regime_blocked=164
- this cycle: closed=1 new_signals=86 skipped=75 slot_full=0 slice_full=0 pair_held=10
- Action funnel: regime_blocked=164 | lane_gate_blocked=2 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=10 | slot_full=0 | skipped=75
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 2, "pair_held": 10, "regime_blocked": 164, "skipped": 75, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=False hip3_green=False frozen=hip3,native islands=20 blocks=44
- aggregate_risk: ok open=19.8502 cap=160.8457 used=0.1574 remaining=135.5214 replayed=7 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
