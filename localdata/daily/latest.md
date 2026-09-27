# Breakwater daily print — 2026-09-27 19:08 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **532.67 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2487.57 ZAR** (seed 2000) | lifetime: **+487.57 ZAR** | closed: 281
- Today: 10 closed, **-3.14 ZAR**
- 7d: **+222.12 ZAR** | 30d: **+487.57 ZAR**

## 2b. Claimed vs realised

- Book: 273 slices (native 248 | hip3 25); validated pools: native 560 | hip3 160; book slices absent from pools: 24
  - absent: `feat_price_accel:1:LONG:h20` (native)
  - absent: `feat_ret_1:1:LONG:h20` (native)
  - absent: `feat_squeeze:1:LONG:h20` (native)
  - absent: `feat_rsi_14:2:LONG:h12` (native)
  - absent: `feat_ret_5:2:LONG:h20` (native)
  - absent: `feat_price_roc_5:2:LONG:h20` (native)
  - absent: `feat_trend_neutral:0:LONG:h15` (native)
  - absent: `feat_price_accel:1:LONG:h20` (native)
  - absent: `feat_intraday_mom:2:LONG:h24` (native)
  - absent: `feat_close_position:2:LONG:h24` (native)
  - ... and 14 more
- Claimed edge (median mean_ret_costadj over 249 book slices present in the validated pools): +0.484% | at 166.64 ZAR mean notional/trade: +0.81 ZAR/trade
- Realised (281 real closes per lane_gate._is_real_close, net of fees): +1.74 ZAR/trade | sd 5.55 | SE 0.33
- Gap: +0.93 ZAR/trade | t = +2.80 (one-sample t of realised mean vs the claimed constant) | verdict: EXCEEDS
- native: claimed median +0.488% over 228/248 slices (pool 560) ~ +0.84 ZAR | realised 239 closes +2.07 ZAR sd 5.71 SE 0.37 | gap +1.24 t +3.35 | EXCEEDS
- hip3: claimed median +0.065% over 21/25 slices (pool 160) ~ +0.09 ZAR | realised 42 closes -0.20 ZAR sd 4.08 SE 0.63 | gap -0.29 t -0.46 | NOT ESTABLISHED
- Ledger: 163930 decision rows; 281 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 163649 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 239 | wins: 142 | win%: 59.4 | P&L: **+495.92 ZAR** | today: -3.14 | 7d: +233.37 | 30d: +495.92
- By exit: target +516.3, horizon +102.6, regime_shift -11.9, stop -111.0
- By entry regime (n/pnl): neutral 81/+298.9, bull 91/+211.5, bear 67/-14.4
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; engine_mean_reversion:rsi:2:SELL:h10:ZECUSDC 2n/0w -6.66; feat_buy_vol_ratio:2:LONG:h24 5n/0w -6.57; feat_vol_breakout:2:LONG:h15 3n/0w -6.39
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPUSDC 15n +22.72; XRPZAR 2n +18.07; BTCUSDC 21n +17.94
- Worst pairs: ETHZAR 4n -14.36; NEARUSDC 3n -8.75; ZECUSDC 6n -6.51; BNBZAR 5n -5.43; UNIUSDC 1n -4.19

### HIP3

- Closed: 42 | wins: 23 | win%: 54.8 | P&L: **-8.35 ZAR** | today: +0.00 | 7d: -11.25 | 30d: -8.35
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -4.7, stop -51.5
- By entry regime (n/pnl): bull 18/-0.6, neutral 14/-1.5, bear 10/-6.2
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 5n/2w +1.55; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01
- Worst slices: hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30; hip3_para_equity_c0:feat_ext_vs_ma_10:0:SHORT:h17 1n/0w -1.80
- Top pairs: PARA:LRCX 1n +9.79; PARA:IREN 2n +9.17; PARA:CIEN 5n +6.86; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98
- Worst pairs: PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73; PARA:GLW 1n -3.99

## 4. Open positions & risk

- **NATIVE**: 7 open, stop-risk **25.15 ZAR**
  - ZECUSDC BUY ntl=126 risk=5.03 bars=2 stop=1543.6499999999999595 peak=1607.6
  - LTCUSDC BUY ntl=127 risk=4.95 bars=17 stop=69.84674999999999785 peak=72.688
  - SOLUSDC BUY ntl=126 risk=4.06 bars=0 stop=117.8800000000000040 peak=121.79
  - XRPUSDC BUY ntl=126 risk=3.49 bars=0 stop=1.4768499999999999045 peak=1.5188
  - HYPEUSDC BUY ntl=126 risk=3.18 bars=2 stop=89.00375000000000180 peak=91.304
  - BNBUSDC BUY ntl=127 risk=2.22 bars=6 stop=764.856600 peak=778.48
  - BTCUSDC BUY ntl=127 risk=2.22 bars=9 stop=83286.52500 peak=84770.0

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **25.15 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **25.15 / 177.01 ZAR | 15.5% | ok**
- Remaining: 149.6498 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 31, "skipped": 31, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 0, "opened": 2, "pair_held": 20, "signals": 765, "skipped": 743, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **ZECUSDC** 5.0289 ZAR
- positions without bars: 0 | replayed: 8 | invalid: 0

## 6. Monitored books

- Native: 248 | HIP-3: 25
- Native top (by paper P&L):
  - `feat_close_pos_ma:2:LONG:h12` edge=0.0052 n=8788 p=0.0000 src=validated_walk_forward unproven=False paper=29n/+121.93
  - `feat_trend_slope_20:2:LONG:h12` edge=0.0056 n=9427 p=0.0002 src=validated_walk_forward unproven=False paper=5n/+11.12
  - `feat_rsi_divergence:2:LONG:h20` edge=0.0068 n=9718 p=0.2152 src=validated_walk_forward unproven=False paper=5n/+8.36
  - `feat_vol_regime:2:LONG:h12` edge=0.0058 n=9031 p=0.0004 src=validated_walk_forward unproven=False paper=5n/+7.60
  - `feat_vol_regime:2:LONG:h12` edge=0.0062 n=8545 p=0.0003 src=validated_walk_forward unproven=False paper=5n/+7.60
  - `feat_bb_squeeze_20:2:LONG:h15` edge=0.0074 n=9829 p=0.0515 src=validated_walk_forward unproven=False paper=2n/+7.41
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0058 n=17004 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+5.56
  - `feat_close_pos_ma:2:LONG:h20` edge=0.0097 n=10051 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+5.01
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

- Closed paper trades: **42/50** | ghost rows: **495/50** | PnL: **-8.35 ZAR**
- Gate verdict: **NOT READY**

## 8. Research / honesty checks

- Deep audit: candidates=74880 preliminary_passes=0 audit_passes=0 plateaus=0 fetch_errors=25

## 9. Live readiness checks

- Promotion registry strategies: **0** | live_capped: 0
- 1 live HL executor: NOT PRESENT - hyperliquid.py is read-only; no mainnet signer
- 2 mechanism canary: NOT RUN - no testnet agent key / no signed action
- 3 live aggregate risk in guardian: NOT WIRED - guardian passes aggregate_open_risk_zar=0, loss-limit events never appended
- 4 promotion registry valr_native: NOT APPLICABLE TO HL - gate requires valr_native=True
- 5 big-wave-only live path: NOT YOUR BOOK - engine executes slice_id=='big-wave' only
- 6 deep audit passes: 0 preliminary / 0 audit
- 7 book regime durability: NOT PROVEN - hostile_unproven can be True and still promoted

## 10. Regime shift

- Label: **bull** | breadth bear=0.0588 bull=0.5882 neutral=0.3529 | symbols=17
- confirmed_bear: **False** | confirmed_bull: **True** | flip: **True** | flipped_from: bull | consecutive_bear: 0 / bull 19
- as_of: 2026-09-27T18:35:32Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 832 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+11.38 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-19.94 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 3
  - `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` pnl=+1.55
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **184/248** | hip3 **19/25**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 17
  - `feat_atr_norm_ext:2:LONG:h13` slice_pnl=-4.88
  - `feat_buy_vol_ratio:2:LONG:h24` slice_pnl=-6.57
  - `feat_donchian_break:2:LONG:h15` slice_pnl=-1.54
  - `feat_range_pos_20:2:LONG:h15` slice_pnl=-3.77
  - `feat_realized_vol_20:2:LONG:h14` slice_pnl=-0.40
  - `feat_realized_vol_20:2:LONG:h21` slice_pnl=-2.71
  - `feat_realized_vol_20:2:LONG:h22` slice_pnl=-1.39
  - `feat_realized_vol_20:2:LONG:h23` slice_pnl=-0.13
  - `feat_realized_vol_20:2:LONG:h24` slice_pnl=-13.68
  - `feat_ret_1:2:LONG:h24` slice_pnl=-1.95
  - `feat_time_since_high_20:0:LONG:h12` slice_pnl=-4.14
  - `feat_vol_breakout:2:LONG:h15` slice_pnl=-6.39
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` lane_not_green
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-09-27T17:33:13: errors=0 signals=796 regime_blocked=435
- this cycle: closed=3 new_signals=796 skipped=774 slot_full=0 slice_full=0 pair_held=20
- Action funnel: regime_blocked=435 | lane_gate_blocked=8 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=20 | slot_full=0 | skipped=774
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 8, "pair_held": 20, "regime_blocked": 435, "skipped": 774, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=3 blocks=15
- aggregate_risk: ok open=17.5988 cap=177.0148 used=0.1546 remaining=149.6498 replayed=8 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
