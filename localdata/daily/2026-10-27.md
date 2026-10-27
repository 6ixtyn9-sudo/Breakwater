# Breakwater daily print — 2026-10-27 22:43 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

> ## COMA ALARM — NATIVE

> No **proven** slice in this lane. Auditions can still open entries, so
> this is not a dead lane: it trades, but nothing in it trades on a record
> it earned, so it cannot unfreeze itself. The runner will keep reporting
> operational, which is why this block exists. Attention, not intervention.

## 1. Posture

- Mode: **readonly** | VALR equity: **433.23 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2267.76 ZAR** (seed 2000) | lifetime: **+267.76 ZAR** | closed: 486
- Today: 7 closed, **-9.51 ZAR**
- 7d: **-15.27 ZAR** | 30d: **-216.96 ZAR**

## 2b. Claimed vs realised

- Book: 66 slices (native 46 | hip3 20); validated pools: native 123 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 66 book slices present in the validated pools): +0.241% | at 153.39 ZAR mean notional/trade: +0.37 ZAR/trade
- Realised (486 real closes per lane_gate._is_real_close, net of fees): +0.55 ZAR/trade | sd 4.91 | SE 0.22
- Gap: +0.18 ZAR/trade | t = +0.82 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.364% over 46/46 slices (pool 123) ~ +0.55 ZAR | realised 440 closes +0.71 ZAR sd 4.90 SE 0.23 | gap +0.16 t +0.67 | NOT ESTABLISHED
- hip3: claimed median +0.062% over 20/20 slices (pool 160) ~ +0.10 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.07 t -1.51 | NOT ESTABLISHED
- Ledger: 589 decision rows; 486 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 103 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 440 | wins: 211 | win%: 48.0 | P&L: **+312.27 ZAR** | today: -9.51 | 7d: -15.27 | 30d: -180.81
- By exit: target +516.3, trail_stop +84.9, horizon +66.9, max_bars +2.8, regime_shift -11.9, stop -346.7
- By entry regime (n/pnl): neutral 168/+221.5, bull 115/+179.3, bear 157/-88.5
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82; feat_range_pos_50:2:SHORT:h24 3n/0w -10.55
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPZAR 2n +18.07; XMRUSDC 7n +10.76; BTCUSDC 47n +9.90
- Worst pairs: UNIUSDC 9n -26.80; ETHUSDC 57n -23.64; ZECUSDC 15n -23.41; HYPEUSDC 33n -18.76; XRPUSDC 45n -16.32

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: -36.16
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 6 open, stop-risk **18.01 ZAR**
  - SUIUSDC SELL ntl=115 risk=4.02 bars=0 stop=0.9608849999999999070 peak=0.92848
  - HYPEUSDC SELL ntl=115 risk=3.60 bars=5 stop=82.7517499999999930 peak=81.809
  - XRPUSDC SELL ntl=116 risk=3.00 bars=10 stop=1.3361499999999998885 peak=1.3305
  - ETHUSDC SELL ntl=115 risk=2.77 bars=0 stop=2406.7250000000000945 peak=2350.2
  - SOLUSDC SELL ntl=116 risk=2.58 bars=10 stop=102.33424999999999945 peak=101.88
  - BTCUSDC SELL ntl=116 risk=2.03 bars=10 stop=81292.14500 peak=81281.0

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **18.01 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **18.01 / 161.44 ZAR | 12.2% | ok**
- Remaining: 141.6961 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 30, "skipped": 30, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 0, "opened": 2, "pair_held": 77, "signals": 166, "skipped": 87, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **SUIUSDC** 4.0245 ZAR
- positions without bars: 0 | replayed: 6 | invalid: 0

## 6. Monitored books

- Native: 46 | HIP-3: 20
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

- Label: **neutral** | breadth bear=0.0667 bull=0.1333 neutral=0.8 | symbols=15
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 0 / bull 0
- as_of: 2026-10-27T22:01:23Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 980 | eligible: 375 | observations: 2714 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
  - `feat_funding_rate@oi_lo:1:SHORT:h24` edge=231.4b n=221 breadth=6 validated=False prov=False armable=False (not_confirmed_bear)
  - `feat_funding_rate@oi_lo:1:SHORT:h20` edge=192.4b n=204 breadth=5 validated=False prov=False armable=False (not_confirmed_bear)
  - `feat_funding_rate@oi_lo:1:SHORT:h15` edge=185.6b n=211 breadth=5 validated=False prov=False armable=False (not_confirmed_bear)
  - `feat_funding_cum_24@oi_mid:2:SHORT:h20` edge=146.4b n=925 breadth=10 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_funding_rate@oi_mid:2:SHORT:h20` edge=146.1b n=763 breadth=10 validated=True prov=False armable=False (not_confirmed_bear)
  - `feat_funding_cum_24@oi_mid:2:SHORT:h24` edge=145.7b n=739 breadth=9 validated=False prov=False armable=False (regime_confounded)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-19.18 | frozen=YES
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
- Tradable slices: native **46/46** | hip3 **18/20**
- **COMA LANES: native** — frozen with no tradable slice on an earned green record; auditions may still open.
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 43
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
  - `feat_ext_vs_ma_50:0:LONG:h20` lane_not_green
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

- Latest scan 2026-10-27T22:43:57: errors=0 signals=196 regime_blocked=239
- this cycle: closed=2 new_signals=196 skipped=117 slot_full=0 slice_full=0 pair_held=77
- Action funnel: regime_blocked=239 | lane_gate_blocked=2 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=77 | slot_full=0 | skipped=117
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 2, "pair_held": 77, "regime_blocked": 239, "skipped": 117, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=False hip3_green=False frozen=hip3,native islands=20 blocks=43
- aggregate_risk: ok open=11.2080 cap=161.4355 used=0.1223 remaining=141.6961 replayed=6 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
