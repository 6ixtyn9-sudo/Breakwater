# Breakwater daily print — 2026-09-23 07:14 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **476.56 ZAR** | high-water: **477.38 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2497.66 ZAR** (seed 2000) | lifetime: **+497.66 ZAR** | closed: 238
- Today: 4 closed, **-0.97 ZAR**
- 7d: **+507.86 ZAR** | 30d: **+497.66 ZAR**

## 2b. Claimed vs realised

- Book: 281 slices (native 256 | hip3 25); validated pools: native 652 | hip3 160; book slices absent from pools: 13
  - absent: `feat_time_since_low_20:2:LONG:h12` (native)
  - absent: `feat_hour_utc:0:LONG:h12` (native)
  - absent: `feat_asia_range:2:LONG:h12` (native)
  - absent: `feat_vol_regime:1:LONG:h24` (native)
  - absent: `feat_vol_contraction:1:LONG:h24` (native)
  - absent: `feat_atr_ratio:2:LONG:h12` (native)
  - absent: `feat_ret_5:2:LONG:h20` (native)
  - absent: `feat_price_roc_5:2:LONG:h20` (native)
  - absent: `feat_trend_slope_20:2:LONG:h11` (native)
  - absent: `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` (hip3)
  - ... and 3 more
- Claimed edge (median mean_ret_costadj over 268 book slices present in the validated pools): +0.272% | at 167.83 ZAR mean notional/trade: +0.46 ZAR/trade
- Realised (238 real closes per lane_gate._is_real_close, net of fees): +2.09 ZAR/trade | sd 5.77 | SE 0.37
- Gap: +1.63 ZAR/trade | t = +4.37 (one-sample t of realised mean vs the claimed constant) | verdict: EXCEEDS
- native: claimed median +0.281% over 247/256 slices (pool 652) ~ +0.50 ZAR | realised 200 closes +2.52 ZAR sd 6.03 SE 0.43 | gap +2.02 t +4.73 | EXCEEDS
- hip3: claimed median +0.065% over 21/25 slices (pool 160) ~ +0.08 ZAR | realised 38 closes -0.15 ZAR sd 3.43 SE 0.56 | gap -0.22 t -0.40 | NOT ESTABLISHED
- Ledger: 103692 decision rows; 238 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 103454 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 200 | wins: 121 | win%: 60.5 | P&L: **+503.29 ZAR** | today: -0.97 | 7d: +523.40 | 30d: +503.29
- By exit: target +506.4, horizon +93.0, regime_shift -11.9, stop -84.3
- By entry regime (n/pnl): neutral 61/+292.2, bull 73/+227.6, bear 66/-16.4
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 27n/19w +130.78; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; engine_mean_reversion:rsi:2:SELL:h10:ZECUSDC 2n/0w -6.66; feat_vol_breakout:2:LONG:h15 3n/0w -6.39; engine_mean_reversion:bollinger:2:SELL:h10:ZECUSDC 1n/0w -4.93
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPUSDC 11n +21.98; BTCUSDC 15n +19.57; XRPZAR 2n +18.07
- Worst pairs: ETHZAR 4n -14.36; ZECUSDC 4n -11.98; NEARUSDC 3n -8.75; UNIUSDC 1n -4.19; PUMPUSDC 1n -3.88

### HIP3

- Closed: 38 | wins: 22 | win%: 57.9 | P&L: **-5.63 ZAR** | today: +0.00 | 7d: -15.54 | 30d: -5.63
- By exit: target +33.0, regime_shift +1.8, trail_stop +1.0, horizon +0.8, stop -42.3
- By entry regime (n/pnl): bear 9/+3.1, bull 18/-0.6, neutral 11/-8.0
- Top slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 1n/1w +4.26; hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01
- Worst slices: hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30; hip3_para_equity_c0:feat_ext_vs_ma_10:0:SHORT:h17 1n/0w -1.80
- Top pairs: PARA:LRCX 1n +9.79; PARA:CIEN 5n +6.86; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; PARA:MELI 4n +1.64
- Worst pairs: PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73; PARA:IREN 1n -2.84; PARA:COHR 2n -2.39

## 4. Open positions & risk

- **NATIVE**: 6 open, stop-risk **35.83 ZAR**
  - SOLZAR BUY ntl=500 risk=12.74 bars=7 stop=1874.00 peak=1923.0
  - BNBZAR BUY ntl=498 risk=9.31 bars=5 stop=12582.25 peak=12822.0
  - SOLUSDC BUY ntl=125 risk=4.60 bars=14 stop=112.66499999999999845 peak=116.98
  - ETHUSDC BUY ntl=125 risk=3.30 bars=21 stop=2656.3000000000001325 peak=2728.2
  - BNBUSDC BUY ntl=125 risk=3.06 bars=14 stop=768.0850000000000135 peak=787.38
  - BTCUSDC BUY ntl=125 risk=2.83 bars=13 stop=84492.50000000000015 peak=86453.0

- **HIP3**: 3 open, stop-risk **11.17 ZAR**
  - PARA:COHR SELL ntl=125 risk=4.68 bars=15 stop=335.5075000000000165 peak=323.4
  - PARA:AVGO SELL ntl=125 risk=4.31 bars=11 stop=376.0024999999999655 peak=363.48
  - PARA:IGV SELL ntl=125 risk=2.19 bars=15 stop=108.587600 peak=106.72

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **47.00 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 256 | HIP-3: 25
- Native top (by paper P&L):
  - `feat_close_pos_ma:1:LONG:h24` edge=0.0021 n=9970 p=0.0755 src=validated_walk_forward unproven=False paper=37n/+283.35
  - `feat_close_pos_ma:2:LONG:h12` edge=0.0027 n=9186 p=0.0450 src=validated_walk_forward unproven=False paper=27n/+130.78
  - `feat_ext_strength:2:LONG:h15` edge=0.0072 n=16038 p=0.0016 src=validated_walk_forward unproven=False paper=12n/+24.00
  - `feat_bb_pos_20:2:LONG:h15` edge=0.0032 n=9073 p=0.0052 src=validated_walk_forward unproven=False paper=4n/+16.17
  - `feat_bb_pos_20:2:LONG:h15` edge=0.0090 n=10497 p=0.0043 src=validated_walk_forward unproven=False paper=4n/+16.17
  - `feat_atr_norm_ext:2:LONG:h15` edge=0.0031 n=8891 p=0.0217 src=validated_walk_forward unproven=False paper=3n/+15.77
  - `feat_cci_20:2:LONG:h15` edge=0.0088 n=9677 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+13.32
  - `feat_mean_rev_strength:0:LONG:h15` edge=0.0034 n=8951 p=0.0110 src=validated_walk_forward unproven=False paper=2n/+11.65
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

- Label: **bull** | breadth bear=0.0 bull=1.0 neutral=0.0 | symbols=15
- confirmed_bear: **False** | confirmed_bull: **True** | flip: **True** | flipped_from: bull | consecutive_bear: 0 / bull 58
- as_of: 2026-09-23T06:35:30Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 832 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-6.08 | frozen=YES
- HIP-3 lane: **RED** | closed=20 pnl=-14.16 | frozen=YES
- Frozen lanes: hip3, native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 14
  - `feat_atr_norm_ext:2:LONG:h15` pnl=+15.77
  - `feat_bb_pos_20:2:LONG:h15` pnl=+16.17
  - `feat_cci_20:2:LONG:h15` pnl=+13.32
  - `feat_close_pos_ma:1:LONG:h24` pnl=+283.35
  - `feat_close_pos_ma:2:LONG:h12` pnl=+130.78
  - `feat_close_pos_ma:2:LONG:h20` pnl=+5.01
  - `feat_ext_strength:2:LONG:h15` pnl=+24.00
  - `feat_ext_vs_ma_20:2:LONG:h15` pnl=+9.35
  - `feat_realized_vol_20:2:LONG:h20` pnl=+1.47
  - `feat_ret_10:2:LONG:h19` pnl=+14.58
  - `feat_ret_20:2:LONG:h14` pnl=+13.42
  - `feat_trend_slope_20:2:LONG:h12` pnl=+11.12
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **203/256** | hip3 **19/25**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 13
  - `feat_atr_norm_ext:2:LONG:h13` lane_not_green
  - `feat_range_pos_20:2:LONG:h15` lane_not_green
  - `feat_realized_vol_20:2:LONG:h14` lane_not_green
  - `feat_realized_vol_20:2:LONG:h21` lane_not_green
  - `feat_realized_vol_20:2:LONG:h22` lane_not_green
  - `feat_realized_vol_20:2:LONG:h23` lane_not_green
  - `feat_realized_vol_20:2:LONG:h24` lane_not_green
  - `feat_vol_breakout:2:LONG:h15` lane_not_green
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` lane_not_green
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-09-23T05:25:03: errors=0 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=8
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 8, "pair_held": 30, "regime_blocked": 745, "skipped": 607, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=13
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
