# Breakwater daily print — 2026-10-12 01:11 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **489.80 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2352.57 ZAR** (seed 2000) | lifetime: **+352.57 ZAR** | closed: 407
- Today: 0 closed, **+0.00 ZAR**
- 7d: **-68.77 ZAR** | 30d: **+352.57 ZAR**

## 2b. Claimed vs realised

- Book: 73 slices (native 48 | hip3 25); validated pools: native 119 | hip3 160; book slices absent from pools: 12
  - absent: `feat_time_since_low_20:2:LONG:h12` (native)
  - absent: `feat_ext_vs_ma_20:2:LONG:h12` (native)
  - absent: `feat_vwap_dist:0:LONG:h24` (native)
  - absent: `feat_close_pos_ma:2:LONG:h15` (native)
  - absent: `feat_rsi_14:2:LONG:h15` (native)
  - absent: `feat_keltner_pos:2:LONG:h15` (native)
  - absent: `feat_donchian_width_20:2:LONG:h20` (native)
  - absent: `feat_atr_norm_ext:2:LONG:h15` (native)
  - absent: `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` (hip3)
  - absent: `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` (hip3)
  - ... and 2 more
- Claimed edge (median mean_ret_costadj over 61 book slices present in the validated pools): +0.301% | at 160.11 ZAR mean notional/trade: +0.48 ZAR/trade
- Realised (407 real closes per lane_gate._is_real_close, net of fees): +0.87 ZAR/trade | sd 5.18 | SE 0.26
- Gap: +0.39 ZAR/trade | t = +1.50 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.441% over 40/48 slices (pool 119) ~ +0.70 ZAR | realised 361 closes +1.10 ZAR sd 5.18 SE 0.27 | gap +0.40 t +1.46 | NOT ESTABLISHED
- hip3: claimed median +0.065% over 21/25 slices (pool 160) ~ +0.11 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.08 t -1.52 | NOT ESTABLISHED
- Ledger: 321220 decision rows; 407 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 320813 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 361 | wins: 185 | win%: 51.2 | P&L: **+397.08 ZAR** | today: +0.00 | 7d: -68.77 | 30d: +397.08
- By exit: target +516.3, horizon +75.0, trail_stop +58.0, regime_shift -11.9, stop -240.3
- By entry regime (n/pnl): neutral 141/+233.6, bull 112/+179.0, bear 108/-15.5
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_bb_squeeze_20:2:LONG:h20 4n/1w -10.15; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; feat_ext_vs_ma_50:0:LONG:h24 2n/0w -6.90
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPZAR 2n +18.07; ENAUSDC 3n +17.56; BTCUSDC 36n +13.47
- Worst pairs: UNIUSDC 7n -21.68; ZECUSDC 12n -16.52; ETHZAR 4n -14.36; ETHUSDC 43n -11.92; HYPEUSDC 26n -9.37

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: -44.50
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 5 open, stop-risk **19.25 ZAR**
  - ZECUSDC BUY ntl=238 risk=9.51 bars=7 stop=1233.6500000000000330 peak=1289.8
  - SOLUSDC BUY ntl=120 risk=3.04 bars=0 stop=108.76500000000000980 peak=111.6
  - XRPUSDC BUY ntl=120 risk=2.52 bars=3 stop=1.3749500000000000380 peak=1.4134
  - BTCUSDC BUY ntl=120 risk=2.09 bars=0 stop=82463.19000 peak=83932.0
  - ETHUSDC BUY ntl=119 risk=2.08 bars=8 stop=2504.39250 peak=2552.0

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **19.25 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **19.25 / 167.55 ZAR | 12.6% | ok**
- Remaining: 146.5142 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 33, "skipped": 33, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 0, "opened": 2, "pair_held": 5, "signals": 91, "skipped": 84, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **ZECUSDC** 9.5125 ZAR
- positions without bars: 0 | replayed: 3 | invalid: 0

## 6. Monitored books

- Native: 48 | HIP-3: 25
- Native top (by paper P&L):
  - `feat_atr_norm_ext:2:LONG:h15` edge=0.0041 n=10348 p=0.0006 src=validated_walk_forward unproven=False paper=3n/+15.77
  - `feat_vwap_dist:0:LONG:h24` edge=0.0069 n=9169 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+13.05
  - `feat_bb_squeeze_20:2:LONG:h15` edge=0.0033 n=10668 p=0.0092 src=validated_walk_forward unproven=False paper=2n/+7.41
  - `feat_vol_regime:2:LONG:h12` edge=0.0070 n=9423 p=0.0000 src=validated_walk_forward unproven=False paper=6n/+6.68
  - `feat_rsi_14:2:LONG:h15` edge=0.0036 n=10124 p=0.0021 src=validated_walk_forward unproven=False paper=2n/+3.70
  - `feat_squeeze:2:LONG:h15` edge=0.0053 n=11985 p=0.0048 src=validated_walk_forward unproven=False paper=1n/+2.25
  - `feat_squeeze:2:LONG:h15` edge=0.0052 n=12111 p=0.0033 src=validated_walk_forward unproven=False paper=1n/+2.25
  - `feat_close_pos_ma:2:LONG:h15` edge=0.0054 n=9374 p=0.0000 src=validated_walk_forward unproven=False paper=6n/+1.75
- HIP-3 top (by paper P&L):
  - `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` edge=0.0081 n=494 p=0.1655 src=validated_walk_forward unproven=False paper=20n/+9.43
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` edge=0.0003 n=9570 p=0.3356 src=validated_walk_forward unproven=False paper=15n/+4.27
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h11` edge=0.0015 n=1260 p=0.0162 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h9` edge=0.0006 n=1272 p=0.4321 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ext_vs_ma_50:1:LONG:h22` edge=0.0006 n=1354 p=0.8646 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ext_strength:1:LONG:h18` edge=0.0001 n=1420 p=0.9829 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ret_20:1:LONG:h18` edge=0.0001 n=1563 p=0.9678 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_trend_slope_20:0:LONG:h20` edge=0.0008 n=1576 p=0.1320 src=validated_walk_forward unproven=False paper=0n/+0.00

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

- Label: **neutral** | breadth bear=0.0 bull=0.2667 neutral=0.7333 | symbols=15
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 0 / bull 0
- as_of: 2026-10-12T01:00:31Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 832 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+7.26 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **39/48** | hip3 **18/25**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 31
  - `feat_adx_14:2:LONG:h12` slice_pnl=-1.83
  - `feat_adx_14:2:LONG:h15` slice_pnl=-3.92
  - `feat_atr_norm_ext:2:LONG:h13` slice_pnl=-4.88
  - `feat_bb_squeeze_20:2:LONG:h20` slice_pnl=-10.15
  - `feat_bb_width_20:2:LONG:h15` slice_pnl=-6.62
  - `feat_buy_vol_ratio:2:LONG:h24` slice_pnl=-6.57
  - `feat_cci_20:0:LONG:h24` slice_pnl=-17.74
  - `feat_donchian_break:2:LONG:h15` slice_pnl=-2.57
  - `feat_ema_cross_10_20:2:LONG:h12` slice_pnl=-3.12
  - `feat_hour_utc:2:LONG:h15` slice_pnl=-1.61
  - `feat_price_roc_5:2:LONG:h20` slice_pnl=-5.02
  - `feat_range_pos_20:2:LONG:h15` slice_pnl=-3.77
  - `feat_range_pos_50:0:LONG:h24` slice_pnl=-6.24
  - `feat_realized_vol_20:2:LONG:h14` slice_pnl=-0.40
  - `feat_realized_vol_20:2:LONG:h20` slice_pnl=-2.15
  - `feat_realized_vol_20:2:LONG:h21` slice_pnl=-2.71
  - `feat_realized_vol_20:2:LONG:h22` slice_pnl=-1.39
  - `feat_realized_vol_20:2:LONG:h23` slice_pnl=-0.13
  - `feat_realized_vol_20:2:LONG:h24` slice_pnl=-13.68
  - `feat_ret_1:2:LONG:h24` slice_pnl=-1.95
  - `feat_ret_vol:0:LONG:h24` slice_pnl=-4.69
  - `feat_time_since_high_20:0:LONG:h12` slice_pnl=-4.14
  - `feat_vol_breakout:2:LONG:h15` slice_pnl=-6.39
  - `feat_vol_of_vol:1:LONG:h24` slice_pnl=-3.36
  - `feat_vol_trend:0:LONG:h24` slice_pnl=-4.17
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` lane_not_green
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-10-12T01:11:35: errors=0 signals=124 regime_blocked=268
- this cycle: closed=0 new_signals=124 skipped=117 slot_full=0 slice_full=0 pair_held=5
- Action funnel: regime_blocked=268 | lane_gate_blocked=10 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=5 | slot_full=0 | skipped=117
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 10, "pair_held": 5, "regime_blocked": 268, "skipped": 117, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=31
- aggregate_risk: ok open=14.1108 cap=167.5496 used=0.1255 remaining=146.5142 replayed=3 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
