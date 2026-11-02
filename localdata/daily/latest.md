# Breakwater daily print — 2026-11-02 00:31 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

> ## COMA ALARM — NATIVE

> No **proven** slice in this lane. Auditions can still open entries, so
> this is not a dead lane: it trades, but nothing in it trades on a record
> it earned, so it cannot unfreeze itself. The runner will keep reporting
> operational, which is why this block exists. Attention, not intervention.

## 1. Posture

- Mode: **readonly** | VALR equity: **423.32 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2256.97 ZAR** (seed 2000) | lifetime: **+256.97 ZAR** | closed: 522
- Today: 0 closed, **+0.00 ZAR**
- 7d: **-25.14 ZAR** | 30d: **-159.17 ZAR**

## 2b. Claimed vs realised

- Book: 78 slices (native 57 | hip3 21); validated pools: native 199 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 78 book slices present in the validated pools): +0.151% | at 150.76 ZAR mean notional/trade: +0.23 ZAR/trade
- Realised (522 real closes per lane_gate._is_real_close, net of fees): +0.49 ZAR/trade | sd 4.78 | SE 0.21
- Gap: +0.26 ZAR/trade | t = +1.26 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.174% over 57/57 slices (pool 199) ~ +0.26 ZAR | realised 476 closes +0.63 ZAR sd 4.76 SE 0.22 | gap +0.37 t +1.71 | NOT ESTABLISHED
- hip3: claimed median +0.065% over 21/21 slices (pool 160) ~ +0.11 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.08 t -1.52 | NOT ESTABLISHED
- Ledger: 630 decision rows; 522 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 108 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 476 | wins: 228 | win%: 47.9 | P&L: **+301.47 ZAR** | today: +0.00 | 7d: -25.14 | 30d: -159.17
- By exit: target +516.3, trail_stop +106.9, horizon +64.8, max_bars +2.8, regime_shift -11.9, stop -377.3
- By entry regime (n/pnl): neutral 191/+224.8, bull 117/+178.4, bear 168/-101.8
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82; feat_range_pos_50:2:SHORT:h24 3n/0w -10.55
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPZAR 2n +18.07; BTCUSDC 52n +11.55; AAVEUSDC 3n +9.47
- Worst pairs: UNIUSDC 10n -31.39; ZECUSDC 17n -21.96; HYPEUSDC 36n -21.43; ETHUSDC 61n -20.28; ETHZAR 4n -14.36

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 11 open, stop-risk **32.59 ZAR**
  - ENAUSDC SELL ntl=115 risk=4.59 bars=1 stop=0.1898299999999999940 peak=0.18271
  - PUMPUSDC SELL ntl=115 risk=4.53 bars=7 stop=0.004370999999999999480 peak=0.004266
  - AAVEUSDC SELL ntl=115 risk=4.27 bars=4 stop=138.5450000000000160 peak=134.58
  - UNIUSDC SELL ntl=115 risk=4.17 bars=12 stop=7.515724999999999825 peak=7.4097
  - NEARUSDC SELL ntl=115 risk=4.06 bars=11 stop=4.533674999999999675 peak=4.41
  - HYPEUSDC SELL ntl=115 risk=2.93 bars=2 stop=89.44474999999999925 peak=88.091
  - XRPUSDC SELL ntl=115 risk=2.01 bars=10 stop=1.27279075 peak=1.2548
  - BTCUSDC SELL ntl=115 risk=2.01 bars=13 stop=79467.76750 peak=78158.0
  - ETHUSDC SELL ntl=115 risk=2.01 bars=14 stop=2315.83000 peak=2276.5
  - XMRUSDC SELL ntl=115 risk=2.01 bars=0 stop=609.88950 peak=599.4
  - SOLUSDC SELL ntl=115 risk=0.00 bars=21 stop=94.80755250 peak=95.873

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **32.59 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **32.59 / 160.63 ZAR | 22.3% | ok**
- Remaining: 124.8820 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 21, "skipped": 21, "slice_full": 0, "slot_full": 0}, "native": {"cluster_cap": 7, "lane_gate_blocked": 0, "opened": 1, "pair_held": 49, "signals": 123, "skipped": 66, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **ENAUSDC** 4.5887 ZAR
- positions without bars: 0 | replayed: 10 | invalid: 0

## 6. Monitored books

- Native: 57 | HIP-3: 21
- Native top (by paper P&L):
  - `feat_funding_cum_24:2:SHORT:h20` edge=0.0120 n=2073 p=0.0772 src=validated_walk_forward unproven=False paper=1n/+0.83
  - `feat_premium:2:SHORT:h24` edge=0.0093 n=4113 p=0.0714 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_macd_12_26:2:SHORT:h12` edge=0.0045 n=9272 p=0.0609 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_range_pos_50:2:SHORT:h12` edge=0.0032 n=10067 p=0.1435 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vol_roc_20:0:SHORT:h20` edge=0.0008 n=9537 p=0.4165 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_sign_streak:2:SHORT:h15` edge=0.0017 n=6858 p=0.5761 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_1:2:SHORT:h24` edge=0.0023 n=9342 p=0.2475 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_strength:2:SHORT:h15` edge=0.0038 n=10407 p=0.3835 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Latest research: 2026-11-01T01:18:49.794493+00:00 | discovered 2240 | validated 271 | reg-confounded 343 | hostile-unproven 34
- floors: "" | book: {"rows": 91, "by_status": {"monitored": 88, "decayed": 2, "cooldown": 1}, "in_validated_pool": 91, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=1120 validated=1120 passing=266 eligible=197 best=235.6b best_fail=temporal_pass
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=576 qualifying=0 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_stoch_d_14:L0S2:h20: mean=+4.2b t_no=2.15 folds=01100 mkt_corr=+0.01 dd=345b legs=11.2/12.7 fail=n_nonoverlap,folds
  - feat_rsi_7:L0S2:h20: mean=+2.9b t_no=2.00 folds=01100 mkt_corr=+0.04 dd=228b legs=11.6/12.1 fail=n_nonoverlap,t_nonoverlap,folds
  - feat_rsi_14:L0S2:h20: mean=-4.1b t_no=1.95 folds=11010 mkt_corr=-0.08 dd=194b legs=12.0/11.4 fail=n_nonoverlap,mean<=0,t_nonoverlap,folds
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

- Label: **neutral** | breadth bear=0.375 bull=0.0625 neutral=0.5625 | symbols=16
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 0 / bull 0
- as_of: 2026-11-01T23:01:10Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 1120 | eligible: 337 | observations: 918 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
  - `feat_oi_chg_24@oi_lo:2:SHORT:h24` edge=235.6b n=135 breadth=4 validated=False prov=False armable=False (too_few_rows)
  - `feat_funding_rate@oi_lo:2:SHORT:h24` edge=221.1b n=362 breadth=7 validated=False prov=False armable=False (not_confirmed_bear)
  - `feat_oi_chg_24@oi_lo:1:SHORT:h12` edge=207.4b n=210 breadth=10 validated=False prov=False armable=False (regime_confounded)
  - `feat_oi_chg_24@oi_lo:1:SHORT:h15` edge=203.9b n=200 breadth=10 validated=False prov=False armable=False (regime_confounded)
  - `feat_oi_chg_24@oi_lo:1:SHORT:h24` edge=202.5b n=181 breadth=10 validated=False prov=False armable=False (regime_confounded)
  - `feat_oi_chg_24@oi_lo:1:SHORT:h20` edge=197.2b n=189 breadth=10 validated=False prov=False armable=False (regime_confounded)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-4.19 | frozen=YES
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3, native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 22
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
- Tradable slices: native **57/57** | hip3 **19/21**
- **COMA LANES: native** — frozen with no tradable slice on an earned green record; auditions may still open.
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

- Latest scan 2026-11-01T23:34:03: errors=0 signals=144 regime_blocked=179
- this cycle: closed=0 new_signals=144 skipped=87 slot_full=0 slice_full=0 pair_held=49
- Action funnel: regime_blocked=179 | lane_gate_blocked=2 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=49 | cluster_cap=7 | family_vetoed=3 | slot_full=0 | skipped=87
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "cluster_cap": 7, "family_vetoed": 3, "lane_gate_blocked": 2, "pair_held": 49, "regime_blocked": 179, "skipped": 87, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=False hip3_green=False frozen=hip3,native islands=22 blocks=46
- aggregate_risk: ok open=30.5839 cap=160.6326 used=0.2226 remaining=124.8820 replayed=10 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
