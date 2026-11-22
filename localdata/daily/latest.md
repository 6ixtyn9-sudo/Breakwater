# Breakwater daily print — 2026-11-22 12:04 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **383.73 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2464.54 ZAR** (seed 2000) | lifetime: **+464.54 ZAR** | closed: 612
- Today: 0 closed, **+0.00 ZAR**
- 7d: **+71.71 ZAR** | 30d: **+192.59 ZAR**

## 2b. Claimed vs realised

- Book: 33 slices (native 13 | hip3 20); validated pools: native 259 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 33 book slices present in the validated pools): +0.117% | at 146.18 ZAR mean notional/trade: +0.17 ZAR/trade
- Realised (612 real closes per lane_gate._is_real_close, net of fees): +0.76 ZAR/trade | sd 4.80 | SE 0.19
- Gap: +0.59 ZAR/trade | t = +3.03 (one-sample t of realised mean vs the claimed constant) | verdict: EXCEEDS
- native: claimed median +0.956% over 13/13 slices (pool 259) ~ +1.38 ZAR | realised 566 closes +0.90 ZAR sd 4.78 SE 0.20 | gap -0.48 t -2.40 | FALLS SHORT
- hip3: claimed median +0.062% over 20/20 slices (pool 160) ~ +0.10 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.07 t -1.51 | NOT ESTABLISHED
- Ledger: 739 decision rows; 612 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 127 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 566 | wins: 293 | win%: 51.8 | P&L: **+509.05 ZAR** | today: +0.00 | 7d: +71.71 | 30d: +192.59
- By exit: target +516.3, trail_stop +336.5, horizon +76.7, max_bars +2.8, regime_shift -11.9, stop -411.3
- By entry regime (n/pnl): neutral 222/+293.3, bull 122/+199.3, bear 222/+16.5
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_adx_14:1:SHORT:h20 4n/4w +53.91; feat_overnight_ret:1:SHORT:h24 2n/2w +26.35; feat_trend_neutral:0:SHORT:h24 5n/5w +24.80
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_macd_12_26:2:SHORT:h15 3n/0w -11.55; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; BTCUSDC 68n +31.01; SOLUSDC 68n +26.88; ENAUSDC 7n +23.48
- Worst pairs: ZECUSDC 17n -21.96; ETHZAR 4n -14.36; UNIUSDC 14n -12.43; DOGEUSDC 18n -12.37; LTCUSDC 2n -6.24

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 8 open, stop-risk **37.15 ZAR**
  - BTCUSDC SELL ntl=126 risk=5.03 bars=15 stop=62841.74999999999985 peak=61346.0
  - KPEPEUSDC SELL ntl=126 risk=4.89 bars=2 stop=0.003529999999999999845 peak=0.003426
  - AAVEUSDC SELL ntl=126 risk=4.86 bars=0 stop=102.38425000000000725 peak=98.58
  - ETHUSDC SELL ntl=126 risk=4.71 bars=13 stop=1742.575000000000055 peak=1722.5
  - DOGEUSDC SELL ntl=126 risk=4.62 bars=14 stop=0.05728024999999999785 peak=0.055772
  - HYPEUSDC SELL ntl=126 risk=4.42 bars=3 stop=63.23499999999999705 peak=62.63
  - SOLUSDC SELL ntl=126 risk=4.36 bars=12 stop=72.70575000000000920 peak=70.91
  - XMRUSDC SELL ntl=126 risk=4.27 bars=1 stop=505.577500000000010 peak=489.48

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **37.15 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **37.15 / 176.21 ZAR | 22.5% | ok**
- Remaining: 136.5372 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 17, "skipped": 17, "slice_full": 0, "slot_full": 0}, "native": {"cluster_cap": 16, "lane_gate_blocked": 0, "opened": 1, "pair_held": 14, "signals": 34, "skipped": 3, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **BTCUSDC** 5.0275 ZAR
- positions without bars: 0 | replayed: 7 | invalid: 0

## 6. Monitored books

- Native: 13 | HIP-3: 20
- Native top (by paper P&L):
  - `feat_buy_vol_ratio:0:SHORT:h24` edge=0.0086 n=9741 p=0.7351 src=validated_walk_forward unproven=False paper=2n/+5.00
  - `feat_close_position:0:SHORT:h24` edge=0.0086 n=9741 p=0.7351 src=validated_walk_forward unproven=False paper=1n/+2.70
  - `feat_oi_chg_24:2:SHORT:h20` edge=0.0167 n=4777 p=0.0422 src=validated_walk_forward unproven=False paper=1n/+2.26
  - `feat_oi_chg_24@oi_hi:2:SHORT:h24` edge=0.0158 n=1069 p=0.3938 src=validated_walk_forward unproven=False paper=1n/+1.58
  - `feat_bb_width_20:2:SHORT:h24` edge=0.0102 n=9273 p=0.1399 src=validated_walk_forward unproven=False paper=1n/+1.24
  - `feat_oi_chg_24@oi_mid:2:SHORT:h12` edge=0.0102 n=1491 p=0.2480 src=validated_walk_forward unproven=False paper=1n/+0.85
  - `feat_funding_cum_24:0:SHORT:h24` edge=0.0093 n=10907 p=0.5047 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_oi_chg_24:2:SHORT:h15` edge=0.0116 n=4422 p=0.1345 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Latest research: 2026-11-22T00:32:17.879030+00:00 | discovered 2240 | validated 259 | reg-confounded 816 | hostile-unproven 10
- floors: "" | book: {"rows": 14, "by_status": {"monitored": 13, "decayed": 1}, "in_validated_pool": 14, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=1120 validated=1120 passing=259 eligible=828 best=217.2b best_fail=regime_confounded
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=576 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_ext_vs_ma_50:L0S2:h12: mean=+1.7b t_no=2.20 folds=10101 mkt_corr=-0.15 dd=248b legs=12.0/10.7 fail=folds
  - feat_atr_ratio:L0S2:h20: mean=+30.7b t_no=2.04 folds=10101 mkt_corr=-0.75 dd=128b legs=10.5/10.9 fail=n_nonoverlap,folds,market_corr
  - feat_vol_regime:L0S2:h12: mean=+22.7b t_no=1.74 folds=10011 mkt_corr=-0.68 dd=204b legs=10.1/9.7 fail=n_nonoverlap,t_nonoverlap,folds,market_corr
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

- Label: **neutral** | breadth bear=0.0625 bull=0.0625 neutral=0.875 | symbols=16
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 0 / bull 0
- as_of: 2026-11-22T12:01:22Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 1120 | eligible: 1055 | observations: 5901 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
  - `feat_oi_chg_24@oi_mid:2:SHORT:h24` edge=217.2b n=1604 breadth=13 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_oi_chg_24:2:SHORT:h24` edge=178.5b n=4811 breadth=38 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_oi_ret_div@oi_lo:0:SHORT:h24` edge=174.5b n=2249 breadth=13 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_oi_chg_24@oi_lo:2:SHORT:h24` edge=168.7b n=1739 breadth=13 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_oi_chg_24@oi_mid:2:SHORT:h20` edge=166.3b n=1471 breadth=12 validated=False prov=False armable=False (regime_confounded)
  - `feat_oi_ret_div@oi_lo:0:SHORT:h20` edge=156.0b n=2157 breadth=13 validated=False prov=False armable=False (regime_confounded)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+72.91 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **13/13** | hip3 **19/20**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 50
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

- Latest scan 2026-11-22T12:04:58: errors=0 signals=51 regime_blocked=157
- this cycle: closed=0 new_signals=51 skipped=20 slot_full=0 slice_full=0 pair_held=14
- Action funnel: regime_blocked=157 | lane_gate_blocked=1 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=14 | cluster_cap=16 | family_vetoed=0 | slot_full=0 | skipped=20
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "cluster_cap": 16, "family_vetoed": 0, "lane_gate_blocked": 1, "pair_held": 14, "regime_blocked": 157, "skipped": 20, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=50
- aggregate_risk: ok open=32.2970 cap=176.2086 used=0.2251 remaining=136.5372 replayed=7 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
