# Breakwater daily print — 2026-09-22 22:00 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **464.37 ZAR** | high-water: **474.55 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2498.63 ZAR** (seed 2000) | lifetime: **+498.63 ZAR** | closed: 234
- Today: 20 closed, **-46.88 ZAR**
- 7d: **+507.51 ZAR** | 30d: **+498.63 ZAR**

## 2b. Claimed vs realised

- Book: 271 slices (native 246 | hip3 25); validated pools: native 760 | hip3 160; book slices absent from pools: 11
  - absent: `feat_range_pos_50:2:LONG:h15` (native)
  - absent: `feat_ext_vs_ma_50:1:SHORT:h24` (native)
  - absent: `feat_vol_regime:0:LONG:h24` (native)
  - absent: `feat_vol_contraction:0:LONG:h24` (native)
  - absent: `feat_ret_20:2:LONG:h14` (native)
  - absent: `feat_ret_10:2:LONG:h19` (native)
  - absent: `feat_trend_slope_20:2:LONG:h11` (native)
  - absent: `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` (hip3)
  - absent: `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` (hip3)
  - absent: `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` (hip3)
  - ... and 1 more
- Claimed edge (median mean_ret_costadj over 260 book slices present in the validated pools): +0.412% | at 163.78 ZAR mean notional/trade: +0.67 ZAR/trade
- Realised (234 real closes per lane_gate._is_real_close, net of fees): +2.13 ZAR/trade | sd 5.78 | SE 0.38
- Gap: +1.46 ZAR/trade | t = +3.85 (one-sample t of realised mean vs the claimed constant) | verdict: EXCEEDS
- native: claimed median +0.436% over 239/246 slices (pool 760) ~ +0.75 ZAR | realised 196 closes +2.57 ZAR sd 6.05 SE 0.43 | gap +1.82 t +4.22 | EXCEEDS
- hip3: claimed median +0.065% over 21/25 slices (pool 160) ~ +0.08 ZAR | realised 38 closes -0.15 ZAR sd 3.43 SE 0.56 | gap -0.22 t -0.40 | NOT ESTABLISHED
- Ledger: 97135 decision rows; 234 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 96901 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 196 | wins: 119 | win%: 60.7 | P&L: **+504.26 ZAR** | today: -38.35 | 7d: +521.69 | 30d: +504.26
- By exit: target +506.4, horizon +94.0, regime_shift -11.9, stop -84.3
- By entry regime (n/pnl): neutral 61/+292.2, bull 69/+228.5, bear 66/-16.4
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 24n/18w +137.02; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; engine_mean_reversion:rsi:2:SELL:h10:ZECUSDC 2n/0w -6.66; feat_vol_breakout:2:LONG:h15 3n/0w -6.39; engine_mean_reversion:bollinger:2:SELL:h10:ZECUSDC 1n/0w -4.93
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPUSDC 11n +21.98; BTCUSDC 15n +19.57; XRPZAR 2n +18.07
- Worst pairs: ETHZAR 3n -16.60; ZECUSDC 4n -11.98; NEARUSDC 3n -8.75; UNIUSDC 1n -4.19; PUMPUSDC 1n -3.88

### HIP3

- Closed: 38 | wins: 22 | win%: 57.9 | P&L: **-5.63 ZAR** | today: -8.53 | 7d: -14.18 | 30d: -5.63
- By exit: target +33.0, regime_shift +1.8, trail_stop +1.0, horizon +0.8, stop -42.3
- By entry regime (n/pnl): bear 9/+3.1, bull 18/-0.6, neutral 11/-8.0
- Top slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 1n/1w +4.26; hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01
- Worst slices: hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30; hip3_para_equity_c0:feat_ext_vs_ma_10:0:SHORT:h17 1n/0w -1.80
- Top pairs: PARA:LRCX 1n +9.79; PARA:CIEN 5n +6.86; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; PARA:MELI 4n +1.64
- Worst pairs: PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73; PARA:IREN 1n -2.84; PARA:COHR 2n -2.39

## 4. Open positions & risk

- **NATIVE**: 8 open, stop-risk **47.83 ZAR**
  - BNBZAR BUY ntl=498 risk=10.49 bars=9 stop=12591.999999999999995 peak=12863.0
  - BTCZAR BUY ntl=498 risk=9.85 bars=9 stop=1372452.0000000000005 peak=1400141.0
  - ETHZAR BUY ntl=499 risk=8.90 bars=3 stop=43931.250000000000030 peak=44729.0
  - HYPEUSDC BUY ntl=126 risk=4.80 bars=15 stop=89.96399999999999715 peak=93.542
  - SOLUSDC BUY ntl=125 risk=4.60 bars=5 stop=112.66499999999999845 peak=116.98
  - ETHUSDC BUY ntl=125 risk=3.30 bars=12 stop=2656.3000000000001325 peak=2728.2
  - BNBUSDC BUY ntl=125 risk=3.06 bars=5 stop=768.0850000000000135 peak=787.38
  - BTCUSDC BUY ntl=125 risk=2.83 bars=4 stop=84492.50000000000015 peak=86453.0

- **HIP3**: 3 open, stop-risk **11.17 ZAR**
  - PARA:COHR SELL ntl=125 risk=4.68 bars=6 stop=335.5075000000000165 peak=323.4
  - PARA:AVGO SELL ntl=125 risk=4.31 bars=2 stop=376.0024999999999655 peak=363.48
  - PARA:IGV SELL ntl=125 risk=2.19 bars=6 stop=108.587600 peak=106.72

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **59.00 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 246 | HIP-3: 25
- Native top (by paper P&L):
  - `feat_close_pos_ma:1:LONG:h24` edge=0.0036 n=10058 p=0.0066 src=validated_walk_forward unproven=False paper=37n/+283.35
  - `feat_close_pos_ma:2:LONG:h12` edge=0.0092 n=1092 p=0.3222 src=validated_walk_forward unproven=False paper=24n/+137.02
  - `feat_ext_strength:2:LONG:h15` edge=0.0072 n=16038 p=0.0016 src=validated_walk_forward unproven=False paper=12n/+24.00
  - `feat_bb_pos_20:2:LONG:h15` edge=0.0073 n=9943 p=0.0322 src=validated_walk_forward unproven=False paper=4n/+16.17
  - `feat_bb_pos_20:2:LONG:h15` edge=0.0090 n=10497 p=0.0043 src=validated_walk_forward unproven=False paper=4n/+16.17
  - `feat_ret_10:2:LONG:h19` edge=0.0077 n=16875 p=0.0000 src=validated_walk_forward unproven=False paper=11n/+14.58
  - `feat_ret_20:2:LONG:h14` edge=0.0060 n=17052 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+13.42
  - `feat_cci_20:2:LONG:h15` edge=0.0088 n=9677 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+13.32
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

- Closed paper trades: **38/50** | ghost rows: **408/50** | PnL: **-5.63 ZAR**
- Gate verdict: **NOT READY**

## 8. Research / honesty checks

- Latest research: 2026-09-16T11:09:41+00:00 | discovered 7488 | validated 14 | reg-confounded 6236 | hostile-unproven 0
- floors: {"PERP": "20.0", "SPOT": "140.0"} | book: {"blocked_for_green_breadth": 0, "carried_cooldown": 0, "carried_decayed": 0, "carried_kinds": ["PERP"], "carried_monitored": 7, "carried_total": 7, "concentrated": 0, "cooldown": 0, "decayed": 0, "families_considered": 6, "families_promoted": 5, "green_assets_total": 216, "monitored": 5, "multi_horizon_min_passes": 2, "multi_horizon_select": "edge_per_bar", "net_edge_floor_enter_bps": {"PERP": "20.0", "SPOT": "140.0"}, "net_edge_floor_keep_bps": {"PERP": "20.0", "SPOT": "140.0"}, "paper_protected": 1, "per_asset_aware": true, "promotable": 14, "promoted_green_fraction_mean": 0.4047, "rows_total_after_sync": 13, "session_gate_blocked": 0, "validated": 14}
- Short audit: discovered=3744 validated=3744 passing=0 eligible=0 best=-5.5b best_fail=direction_ok,breadth_ok,mean_net<=0
- pair_errors: []
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

- Label: **bull** | breadth bear=0.0 bull=0.875 neutral=0.125 | symbols=16
- confirmed_bear: **False** | confirmed_bull: **True** | flip: **True** | flipped_from: bull | consecutive_bear: 0 / bull 49
- as_of: 2026-09-22T21:35:36Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 832 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+76.73 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-14.16 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **189/246** | hip3 **19/25**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 13
  - `feat_atr_norm_ext:2:LONG:h13` slice_pnl=-4.88
  - `feat_range_pos_20:2:LONG:h15` slice_pnl=-3.77
  - `feat_realized_vol_20:2:LONG:h14` slice_pnl=-0.40
  - `feat_realized_vol_20:2:LONG:h21` slice_pnl=-2.71
  - `feat_realized_vol_20:2:LONG:h22` slice_pnl=-1.39
  - `feat_realized_vol_20:2:LONG:h23` slice_pnl=-0.13
  - `feat_realized_vol_20:2:LONG:h24` slice_pnl=-13.68
  - `feat_vol_breakout:2:LONG:h15` slice_pnl=-6.39
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` lane_not_green
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-09-22T20:42:45: errors=0 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=9
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 9, "pair_held": 32, "regime_blocked": 332, "skipped": 849, "slice_full": 8, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=13
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
