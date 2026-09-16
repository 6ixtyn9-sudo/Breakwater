# Breakwater daily print — 2026-09-16 15:09 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **376.06 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **1966.48 ZAR** (seed 2000) | lifetime: **-33.52 ZAR** | closed: 71
- Today: 32 closed, **-21.92 ZAR**
- 7d: **-33.52 ZAR** | 30d: **-33.52 ZAR**

## 2b. Claimed vs realised

- Book: 26 slices (native 8 | hip3 18); validated pools: native 45 | hip3 160; book slices absent from pools: 16
  - absent: `feat_trend_slope_20:2:LONG:h12` (native)
  - absent: `feat_ext_vs_ma_20:2:LONG:h15` (native)
  - absent: `feat_ext_vs_ma_50:2:LONG:h15` (native)
  - absent: `feat_ret_20:2:LONG:h14` (native)
  - absent: `feat_realized_vol_20:2:LONG:h14` (native)
  - absent: `feat_ext_strength:2:LONG:h15` (native)
  - absent: `feat_ret_10:2:LONG:h19` (native)
  - absent: `feat_trend_slope_20:2:LONG:h11` (native)
  - absent: `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` (hip3)
  - absent: `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` (hip3)
  - ... and 6 more
- Claimed edge (median mean_ret_costadj over 10 book slices present in the validated pools): +0.064% | at 97.94 ZAR mean notional/trade: +0.06 ZAR/trade
- Realised (71 real closes per lane_gate._is_real_close, net of fees): -0.47 ZAR/trade | sd 1.94 | SE 0.23
- Gap: -0.54 ZAR/trade | t = -2.33 (one-sample t of realised mean vs the claimed constant) | verdict: FALLS SHORT
- native: claimed unknown (0/8 slices in pool 45) | realised 53 closes -0.79 ZAR | claimed unknown
- hip3: claimed median +0.064% over 10/18 slices (pool 160) ~ +0.06 ZAR | realised 18 closes +0.47 ZAR sd 0.80 | INSUFFICIENT SAMPLE (n<30)
- Ledger: 27045 decision rows; 71 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 26974 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 53 | wins: 11 | win%: 20.8 | P&L: **-42.05 ZAR** | today: -21.90 | 7d: -42.05 | 30d: -42.05
- By exit: target +9.9, horizon -2.9, regime_shift -12.5, stop -36.6
- By entry regime (n/pnl): bull 1/-3.8, neutral 11/-15.4, bear 41/-22.9
- Top slices: feat_ret_10:2:LONG:h19 8n/2w +4.70; feat_realized_vol_20:2:LONG:h20 8n/7w +1.47; engine_mean_reversion:rsi:2:BUY:h10:XRPUSDT 1n/0w -0.12; feat_realized_vol_20:2:LONG:h23 3n/1w -0.13; engine_momentum:breakout:2:SELL:h10:AVAXUSDT 1n/0w -0.23
- Worst slices: feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; engine_mean_reversion:rsi:2:SELL:h10:ARBUSDC 1n/0w -5.05; engine_mean_reversion:bollinger:2:SELL:h10:ZECUSDC 1n/0w -4.93; feat_atr_norm_ext:2:LONG:h13 7n/0w -4.88
- Top pairs: ARBUSDC 2n +4.86; LINKUSDC 2n +0.17; HYPEUSDC 5n +0.14; ENAUSDC 1n -0.10; XRPUSDT 1n -0.12
- Worst pairs: TRUMPUSDC 2n -6.38; ZECUSDC 2n -5.32; XRPUSDC 3n -5.21; NEARUSDC 2n -5.10; FILUSDC 1n -5.08

### HIP3

- Closed: 18 | wins: 16 | win%: 88.9 | P&L: **+8.53 ZAR** | today: -0.02 | 7d: +8.53 | 30d: +8.53
- By exit: target +6.3, horizon +2.1, regime_shift +1.8, trail_stop +1.0, stop -2.7
- By entry regime (n/pnl): bull 11/+5.1, bear 6/+5.1, neutral 1/-1.7
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 1n/1w +2.05; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01
- Worst slices: hip3_para_equity_c0:feat_ret_vol:2:SHORT:h24 1n/0w -1.66; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 1n/1w +2.05
- Top pairs: XYZ:STRC 8n +3.98; PARA:MELI 2n +3.06; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71; XYZ:NATGAS 2n +0.63
- Worst pairs: PARA:CIEN 1n -1.66; XYZ:PALLADIUM 2n -0.05; XYZ:BRENTOIL 1n +0.49; XYZ:NATGAS 2n +0.63; XYZ:SILVER 1n +0.71

## 4. Open positions & risk

- **NATIVE**: 9 open, stop-risk **29.11 ZAR**
  - ARBUSDC SELL ntl=84 risk=4.94 bars=2 stop=0.17935714285714285 peak=0.16938
  - ZECUSDC SELL ntl=99 risk=4.46 bars=1 stop=1307.1714285714286 peak=1250.6
  - UNIUSDC SELL ntl=98 risk=4.10 bars=0 stop=6.3065 peak=6.0545
  - FILUSDC SELL ntl=100 risk=3.73 bars=12 stop=0.8434728571428572 peak=0.81303
  - NEARUSDC SELL ntl=99 risk=3.56 bars=1 stop=2.555557142857143 peak=2.4664
  - LITUSDC SELL ntl=99 risk=3.47 bars=4 stop=4.453957142857143 peak=4.3036
  - PENDLEUSDC SELL ntl=98 risk=2.86 bars=0 stop=2.2190 peak=2.1563
  - MSTRXUSDT SELL ntl=100 risk=1.00 bars=9 stop=129.32039999999998 peak=128.04
  - SHIBUSDT SELL ntl=98 risk=0.98 bars=0 stop=0.0000048177000000000005 peak=0.00000477

- **HIP3**: 6 open, stop-risk **10.90 ZAR**
  - PARA:COHR SELL ntl=99 risk=3.38 bars=1 stop=294.5500000000000190 peak=284.79
  - PARA:CRDO SELL ntl=99 risk=2.34 bars=1 stop=164.02500000000001420 peak=160.22
  - PARA:IGV SELL ntl=99 risk=1.77 bars=0 stop=108.7800000000000015 peak=106.86
  - PARA:CIEN SELL ntl=99 risk=1.73 bars=0 stop=347.15249999999997345 peak=341.17
  - PARA:GLW SELL ntl=99 risk=1.18 bars=0 stop=148.99000000000001205 peak=147.23
  - PARA:AVGO SELL ntl=99 risk=0.51 bars=1 stop=344.77249999999998465 peak=342.99

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **40.01 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 8 | HIP-3: 18
- Native top (by paper P&L):
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0058 n=17004 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+5.56
  - `feat_ret_10:2:LONG:h19` edge=0.0077 n=16875 p=0.0000 src=validated_walk_forward unproven=False paper=8n/+4.70
  - `feat_trend_slope_20:2:LONG:h12` edge=0.0063 n=16968 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_20:2:LONG:h15` edge=0.0072 n=16809 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_50:2:LONG:h15` edge=0.0069 n=16411 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_20:2:LONG:h14` edge=0.0060 n=17052 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_realized_vol_20:2:LONG:h14` edge=0.0058 n=22975 p=0.0000 src=validated_walk_forward unproven=False paper=4n/-0.40
  - `feat_ext_strength:2:LONG:h15` edge=0.0072 n=16038 p=0.0016 src=validated_walk_forward unproven=False paper=2n/-1.22
- HIP-3 top (by paper P&L):
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` edge=0.0003 n=9570 p=0.3356 src=validated_walk_forward unproven=False paper=15n/+4.27
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` edge=0.0175 n=268 p=0.0651 src=validated_walk_forward unproven=False paper=1n/+2.05
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h11` edge=0.0015 n=1260 p=0.0162 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h13` edge=0.0007 n=1256 p=0.4781 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ext_vs_ma_50:1:LONG:h22` edge=0.0006 n=1354 p=0.8646 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ret_20:1:LONG:h18` edge=0.0001 n=1563 p=0.9678 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_trend_strength_20:0:LONG:h23` edge=0.0001 n=1455 p=0.9492 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_vol_regime:2:SHORT:h21` edge=0.0016 n=11089 p=0.0125 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **18/50** | ghost rows: **64/50** | PnL: **+8.53 ZAR**
- Gate verdict: **NOT READY**

## 8. Research / honesty checks

- Latest research: 2026-09-16T08:33:18+00:00 | discovered 7488 | validated 45 | reg-confounded 6210 | hostile-unproven 0
- floors: {"PERP": "68.9", "SPOT": "140.0"} | book: {"blocked_for_green_breadth": 0, "carried_cooldown": 0, "carried_decayed": 0, "carried_kinds": ["PERP"], "carried_monitored": 7, "carried_total": 7, "concentrated": 0, "cooldown": 0, "decayed": 0, "families_considered": 0, "families_promoted": 0, "green_assets_total": 0, "monitored": 0, "multi_horizon_min_passes": 2, "multi_horizon_select": "edge_per_bar", "net_edge_floor_enter_bps": {"PERP": "68.9", "SPOT": "140.0"}, "net_edge_floor_keep_bps": {"PERP": "52.7", "SPOT": "140.0"}, "paper_protected": 1, "per_asset_aware": true, "promotable": 0, "promoted_green_fraction_mean": null, "rows_total_after_sync": 8, "session_gate_blocked": 0, "validated": 45}
- Short audit: discovered=3744 validated=3744 passing=0 eligible=0 best=-6.2b best_fail=direction_ok,breadth_ok,mean_net<=0
- pair_errors: []
- Deep audit: candidates=74880 preliminary_passes=0 audit_passes=0 plateaus=0 fetch_errors=27

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

- Label: **bear** | breadth bear=0.7333 bull=0.0 neutral=0.2333 | symbols=29
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 20 / bull 0
- as_of: 2026-09-16T15:00:40Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 3744 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-23.16 | frozen=YES
- HIP-3 lane: **GREEN** | closed=18 pnl=+8.53 | frozen=NO
- Frozen lanes: native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `feat_realized_vol_20:2:LONG:h20` pnl=+1.47
  - `feat_ret_10:2:LONG:h19` pnl=+4.70
- Tradable slices: native **7/8** | hip3 **17/18**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 7
  - `feat_atr_norm_ext:2:LONG:h13` lane_not_green
  - `feat_realized_vol_20:2:LONG:h14` lane_not_green
  - `feat_realized_vol_20:2:LONG:h21` lane_not_green
  - `feat_realized_vol_20:2:LONG:h22` lane_not_green
  - `feat_realized_vol_20:2:LONG:h23` lane_not_green
  - `feat_realized_vol_20:2:LONG:h24` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` slice_pnl=-0.30

## 13. Signal activity

- Latest scan 2026-09-16T15:09:58: errors=0 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=2
- **NO ACTION:** dominant blocker = `slot_full` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 2, "pair_held": 14, "regime_blocked": 60, "skipped": 3, "slice_full": 0, "slot_full": 175})
- green_gate: native_green=False hip3_green=True frozen=native islands=2 blocks=7
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
