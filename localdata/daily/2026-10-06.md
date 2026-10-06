# Breakwater daily print — 2026-10-06 06:18 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **532.21 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2441.64 ZAR** (seed 2000) | lifetime: **+441.64 ZAR** | closed: 359
- Today: 3 closed, **-4.38 ZAR**
- 7d: **-14.53 ZAR** | 30d: **+441.64 ZAR**

## 2b. Claimed vs realised

- Book: 307 slices (native 282 | hip3 25); validated pools: native 573 | hip3 160; book slices absent from pools: 71
  - absent: `feat_rsi_divergence:2:LONG:h15` (native)
  - absent: `feat_cci_20:2:LONG:h12` (native)
  - absent: `feat_mean_rev_strength:0:LONG:h12` (native)
  - absent: `feat_ext_strength:2:LONG:h12` (native)
  - absent: `feat_ext_vs_ma_20:2:LONG:h12` (native)
  - absent: `feat_donchian_break:2:LONG:h12` (native)
  - absent: `feat_ret_10:2:LONG:h12` (native)
  - absent: `feat_range_pos_20:2:LONG:h12` (native)
  - absent: `feat_williams_r_14:0:LONG:h15` (native)
  - absent: `feat_vwap_upper_dist:2:LONG:h12` (native)
  - ... and 61 more
- Claimed edge (median mean_ret_costadj over 236 book slices present in the validated pools): +0.397% | at 162.91 ZAR mean notional/trade: +0.65 ZAR/trade
- Realised (359 real closes per lane_gate._is_real_close, net of fees): +1.23 ZAR/trade | sd 5.29 | SE 0.28
- Gap: +0.58 ZAR/trade | t = +2.09 (one-sample t of realised mean vs the claimed constant) | verdict: EXCEEDS
- native: claimed median +0.416% over 215/282 slices (pool 573) ~ +0.67 ZAR | realised 313 closes +1.55 ZAR sd 5.29 SE 0.30 | gap +0.88 t +2.94 | EXCEEDS
- hip3: claimed median +0.065% over 21/25 slices (pool 160) ~ +0.11 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.08 t -1.52 | NOT ESTABLISHED
- Ledger: 272595 decision rows; 359 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 272236 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 313 | wins: 175 | win%: 55.9 | P&L: **+486.15 ZAR** | today: -4.38 | 7d: +21.63 | 30d: +486.15
- By exit: target +516.3, horizon +86.4, trail_stop +47.3, regime_shift -11.9, stop -151.9
- By entry regime (n/pnl): neutral 116/+285.0, bull 107/+187.5, bear 90/+13.7
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_range_pos_50:0:LONG:h24 7n/5w +17.73; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17
- Worst slices: feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; feat_ext_vs_ma_50:0:LONG:h24 2n/0w -6.90; engine_mean_reversion:rsi:2:SELL:h10:ZECUSDC 2n/0w -6.66; feat_bb_width_20:2:LONG:h15 3n/0w -6.62
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; BTCUSDC 31n +20.52; SUIUSDC 5n +19.60; XRPZAR 2n +18.07
- Worst pairs: ETHZAR 4n -14.36; ZECUSDC 9n -13.34; UNIUSDC 4n -7.73; LTCUSDC 2n -6.24; BNBZAR 5n -5.43

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: -36.16 | 30d: -44.50
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 7 open, stop-risk **33.27 ZAR**
  - SUIUSDC BUY ntl=249 risk=9.73 bars=0 stop=1.1475749999999999860 peak=1.1943
  - UNIUSDC BUY ntl=249 risk=9.24 bars=0 stop=8.541499999999999445 peak=8.8711
  - DOGEUSDC BUY ntl=125 risk=3.70 bars=8 stop=0.09285225000000000585 peak=0.096115
  - XRPUSDC BUY ntl=125 risk=3.44 bars=12 stop=1.4506249999999999870 peak=1.5159
  - SOLUSDC BUY ntl=125 risk=2.74 bars=17 stop=118.12750000000000215 peak=121.59
  - BTCUSDC BUY ntl=125 risk=2.24 bars=8 stop=84225.750000000000040 peak=86129.0
  - ETHUSDC BUY ntl=125 risk=2.18 bars=4 stop=2670.33675 peak=2722.8

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **33.27 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **33.27 / 174.06 ZAR | 20.7% | ok**
- Remaining: 137.9892 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 46, "skipped": 46, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 0, "opened": 2, "pair_held": 22, "signals": 635, "skipped": 606, "slice_full": 5, "slot_full": 0}}
- Highest-risk: **SUIUSDC** 9.7282 ZAR
- positions without bars: 0 | replayed: 7 | invalid: 0

## 6. Monitored books

- Native: 282 | HIP-3: 25
- Native top (by paper P&L):
  - `feat_range_pos_50:0:LONG:h24` edge=0.0057 n=9303 p=0.0002 src=validated_walk_forward unproven=False paper=7n/+17.73
  - `feat_range_pos_50:0:LONG:h24` edge=0.0081 n=11086 p=0.0000 src=validated_walk_forward unproven=False paper=7n/+17.73
  - `feat_bb_pos_20:2:LONG:h15` edge=0.0040 n=10327 p=0.0019 src=validated_walk_forward unproven=False paper=4n/+16.17
  - `feat_atr_norm_ext:2:LONG:h15` edge=0.0041 n=10348 p=0.0006 src=validated_walk_forward unproven=False paper=3n/+15.77
  - `feat_ret_vol:0:LONG:h24` edge=0.0085 n=10329 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+10.84
  - `feat_ret_vol:0:LONG:h24` edge=0.0073 n=10551 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+10.84
  - `feat_intraday_mom:2:LONG:h24` edge=0.0062 n=9611 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+7.09
  - `feat_vol_regime:2:LONG:h12` edge=0.0044 n=11267 p=0.0001 src=validated_walk_forward unproven=False paper=6n/+6.68
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

- Label: **neutral** | breadth bear=0.0 bull=0.2 neutral=0.8 | symbols=15
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bull | consecutive_bear: 0 / bull 0
- as_of: 2026-10-06T05:35:36Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 832 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+20.29 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **208/282** | hip3 **18/25**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 24
  - `feat_adx_14:2:LONG:h12` slice_pnl=-1.83
  - `feat_adx_14:2:LONG:h15` slice_pnl=-3.92
  - `feat_atr_norm_ext:2:LONG:h13` slice_pnl=-4.88
  - `feat_bb_width_20:2:LONG:h15` slice_pnl=-6.62
  - `feat_buy_vol_ratio:2:LONG:h24` slice_pnl=-6.57
  - `feat_donchian_break:2:LONG:h15` slice_pnl=-2.57
  - `feat_ema_cross_10_20:2:LONG:h12` slice_pnl=-3.12
  - `feat_price_roc_5:2:LONG:h20` slice_pnl=-5.02
  - `feat_range_pos_20:2:LONG:h15` slice_pnl=-3.77
  - `feat_realized_vol_20:2:LONG:h14` slice_pnl=-0.40
  - `feat_realized_vol_20:2:LONG:h21` slice_pnl=-2.71
  - `feat_realized_vol_20:2:LONG:h22` slice_pnl=-1.39
  - `feat_realized_vol_20:2:LONG:h23` slice_pnl=-0.13
  - `feat_realized_vol_20:2:LONG:h24` slice_pnl=-13.68
  - `feat_ret_1:2:LONG:h24` slice_pnl=-1.95
  - `feat_time_since_high_20:0:LONG:h12` slice_pnl=-4.14
  - `feat_vol_breakout:2:LONG:h15` slice_pnl=-6.39
  - `feat_vol_of_vol:1:LONG:h24` slice_pnl=-3.36
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` lane_not_green
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-10-06T05:17:19: errors=1 signals=681 regime_blocked=561
- this cycle: closed=2 new_signals=681 skipped=652 slot_full=0 slice_full=5 pair_held=22
- Action funnel: regime_blocked=561 | lane_gate_blocked=14 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=5 | pair_held=22 | slot_full=0 | skipped=652
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 14, "pair_held": 22, "regime_blocked": 561, "skipped": 652, "slice_full": 5, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=23
- aggregate_risk: ok open=14.3024 cap=174.0584 used=0.2072 remaining=137.9892 replayed=7 no_new_bars=0
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:SNXX"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
