# Breakwater daily print — 2026-11-01 13:30 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **429.07 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2260.53 ZAR** (seed 2000) | lifetime: **+260.53 ZAR** | closed: 518
- Today: 2 closed, **-6.49 ZAR**
- 7d: **-26.65 ZAR** | 30d: **-164.55 ZAR**

## 2b. Claimed vs realised

- Book: 108 slices (native 87 | hip3 21); validated pools: native 271 | hip3 160; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 108 book slices present in the validated pools): +0.306% | at 151.03 ZAR mean notional/trade: +0.46 ZAR/trade
- Realised (518 real closes per lane_gate._is_real_close, net of fees): +0.50 ZAR/trade | sd 4.80 | SE 0.21
- Gap: +0.04 ZAR/trade | t = +0.19 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.372% over 87/87 slices (pool 271) ~ +0.56 ZAR | realised 472 closes +0.65 ZAR sd 4.78 SE 0.22 | gap +0.09 t +0.41 | NOT ESTABLISHED
- hip3: claimed median +0.065% over 21/21 slices (pool 160) ~ +0.11 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.08 t -1.52 | NOT ESTABLISHED
- Ledger: 626 decision rows; 518 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 108 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 472 | wins: 227 | win%: 48.1 | P&L: **+305.03 ZAR** | today: -6.49 | 7d: -26.65 | 30d: -164.55
- By exit: target +516.3, trail_stop +106.9, horizon +66.2, max_bars +2.8, regime_shift -11.9, stop -375.1
- By entry regime (n/pnl): neutral 187/+228.4, bull 117/+178.4, bear 168/-101.8
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_ext_vs_ma_50:0:LONG:h20 4n/1w -11.21; feat_vol_of_vol:2:LONG:h15 3n/0w -10.82; feat_range_pos_50:2:SHORT:h24 3n/0w -10.55
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPZAR 2n +18.07; BTCUSDC 52n +11.55; AAVEUSDC 3n +9.47
- Worst pairs: UNIUSDC 10n -31.39; HYPEUSDC 35n -22.27; ZECUSDC 16n -20.91; ETHUSDC 61n -20.28; ETHZAR 4n -14.36

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 10 open, stop-risk **31.33 ZAR**
  - PUMPUSDC SELL ntl=115 risk=4.52 bars=21 stop=0.004350250000000000320 peak=0.004307
  - ZECUSDC BUY ntl=115 risk=4.37 bars=3 stop=1201.9749999999999670 peak=1249.5
  - UNIUSDC SELL ntl=115 risk=4.17 bars=2 stop=7.515724999999999825 peak=7.2768
  - HYPEUSDC SELL ntl=115 risk=4.10 bars=12 stop=91.06000000000000030 peak=88.658
  - NEARUSDC SELL ntl=115 risk=4.06 bars=1 stop=4.533674999999999675 peak=4.3878
  - XMRUSDC BUY ntl=115 risk=2.06 bars=2 stop=594.3325000000000605 peak=605.67
  - SOLUSDC SELL ntl=115 risk=2.02 bars=11 stop=97.0725525 peak=95.873
  - XRPUSDC SELL ntl=115 risk=2.01 bars=0 stop=1.27279075 peak=1.2509
  - BTCUSDC SELL ntl=115 risk=2.01 bars=3 stop=79467.76750 peak=78132.0
  - ETHUSDC SELL ntl=115 risk=2.01 bars=4 stop=2315.83000 peak=2276.5

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **31.33 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **31.33 / 160.88 ZAR | 21.3% | ok**
- Remaining: 126.6811 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 14, "skipped": 14, "slice_full": 0, "slot_full": 0}, "native": {"cluster_cap": 0, "lane_gate_blocked": 0, "opened": 1, "pair_held": 6, "signals": 177, "skipped": 112, "slice_full": 0, "slot_full": 58}}
- Highest-risk: **PUMPUSDC** 4.5248 ZAR
- positions without bars: 0 | replayed: 10 | invalid: 0

## 6. Monitored books

- Native: 87 | HIP-3: 21
- Native top (by paper P&L):
  - `feat_rsi_21:2:SHORT:h24` edge=0.0070 n=6576 p=0.0932 src=validated_walk_forward unproven=False paper=2n/+1.17
  - `feat_vwap_dist:2:SHORT:h24` edge=0.0072 n=9402 p=0.2148 src=validated_walk_forward unproven=False paper=1n/+0.61
  - `feat_ret_20:2:SHORT:h20` edge=0.0082 n=8310 p=0.0181 src=validated_walk_forward unproven=False paper=2n/+0.52
  - `feat_gap_fill_ratio:0:SHORT:h24` edge=0.0018 n=10763 p=0.6128 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_premium:2:SHORT:h24` edge=0.0108 n=3143 p=0.2336 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_time_since_low_20:2:SHORT:h20` edge=0.0035 n=3103 p=0.7645 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_macd_12_26:2:SHORT:h12` edge=0.0065 n=7820 p=0.0006 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ema_cross_10_20:2:SHORT:h12` edge=0.0062 n=8162 p=0.0038 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Latest research: 2026-11-01T01:18:49.794493+00:00 | discovered 2240 | validated 271 | reg-confounded 343 | hostile-unproven 34
- floors: "" | book: {"rows": 91, "by_status": {"monitored": 88, "decayed": 2, "cooldown": 1}, "in_validated_pool": 91, "absent_from_pool": 0, "net_edge_floor_enter_bps": ""}
- Short audit: discovered=1120 validated=1120 passing=266 eligible=197 best=235.6b best_fail=temporal_pass
- pair_errors: "not propagated from shards"
- Spread research (long/short, PERP): rows=576 qualifying=2 (go/no-go gate: >=1 qualifying spread on 3 consecutive runs)
  - feat_ext_vs_ma_50:L0S2:h12: mean=+25.4b t_no=2.13 folds=11111 mkt_corr=-0.09 dd=193b legs=13.2/9.0 QUALIFIES
  - feat_macd_12_26:L0S2:h15: mean=+24.1b t_no=2.08 folds=11110 mkt_corr=-0.06 dd=480b legs=14.4/9.0 QUALIFIES
  - feat_range_pos_20:L0S2:h12: mean=-3.4b t_no=2.51 folds=10100 mkt_corr=-0.20 dd=287b legs=12.1/12.2 fail=mean<=0,folds
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

- Label: **neutral** | breadth bear=0.2 bull=0.0667 neutral=0.7333 | symbols=15
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 0 / bull 0
- as_of: 2026-11-01T13:01:09Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 1120 | eligible: 337 | observations: 1438 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
  - `feat_oi_chg_24@oi_lo:2:SHORT:h24` edge=235.6b n=135 breadth=4 validated=False prov=False armable=False (too_few_rows)
  - `feat_funding_rate@oi_lo:2:SHORT:h24` edge=221.1b n=362 breadth=7 validated=False prov=False armable=False (not_confirmed_bear)
  - `feat_oi_chg_24@oi_lo:1:SHORT:h12` edge=207.4b n=210 breadth=10 validated=False prov=False armable=False (regime_confounded)
  - `feat_oi_chg_24@oi_lo:1:SHORT:h15` edge=203.9b n=200 breadth=10 validated=False prov=False armable=False (regime_confounded)
  - `feat_oi_chg_24@oi_lo:1:SHORT:h24` edge=202.5b n=181 breadth=10 validated=False prov=False armable=False (regime_confounded)
  - `feat_oi_chg_24@oi_lo:1:SHORT:h20` edge=197.2b n=189 breadth=10 validated=False prov=False armable=False (regime_confounded)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+4.57 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **87/87** | hip3 **19/21**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 46
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
  - `feat_funding_rate:2:SHORT:h12` slice_pnl=-7.96
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

- Latest scan 2026-11-01T13:30:38: errors=1 signals=191 regime_blocked=279
- this cycle: closed=1 new_signals=191 skipped=126 slot_full=58 slice_full=0 pair_held=6
- Action funnel: regime_blocked=279 | lane_gate_blocked=2 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=6 | cluster_cap=0 | family_vetoed=2 | slot_full=58 | skipped=126
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "cluster_cap": 0, "family_vetoed": 2, "lane_gate_blocked": 2, "pair_held": 6, "regime_blocked": 279, "skipped": 126, "slice_full": 0, "slot_full": 58})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=46
- aggregate_risk: ok open=29.3147 cap=160.8818 used=0.2126 remaining=126.6811 replayed=10 no_new_bars=0
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:PLTR"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
