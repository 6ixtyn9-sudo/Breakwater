# Breakwater daily print — 2026-09-16 07:06 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

> ## COMA ALARM — NATIVE

> No **proven** slice in this lane. Auditions can still open entries, so
> this is not a dead lane: it trades, but nothing in it trades on a record
> it earned, so it cannot unfreeze itself. The runner will keep reporting
> operational, which is why this block exists. Attention, not intervention.

## 1. Posture

- Mode: **readonly** | VALR equity: **385.70 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **1989.87 ZAR** (seed 2000) | lifetime: **-10.13 ZAR** | closed: 47
- Today: 8 closed, **+1.47 ZAR**
- 7d: **-10.13 ZAR** | 30d: **-10.13 ZAR**

## 2b. Claimed vs realised

- Book: 486 slices (native 21 | hip3 465); validated pools: native 157 | hip3 732; book slices absent from pools: 8
  - absent: `feat_trend_slope_20:2:LONG:h12` (native)
  - absent: `feat_ext_vs_ma_20:2:LONG:h15` (native)
  - absent: `feat_ext_vs_ma_50:2:LONG:h15` (native)
  - absent: `feat_ret_20:2:LONG:h14` (native)
  - absent: `feat_realized_vol_20:2:LONG:h14` (native)
  - absent: `feat_ext_strength:2:LONG:h15` (native)
  - absent: `feat_ret_10:2:LONG:h19` (native)
  - absent: `feat_trend_slope_20:2:LONG:h11` (native)
- Claimed edge (median mean_ret_costadj over 478 book slices present in the validated pools): +0.121% | at 97.97 ZAR mean notional/trade: +0.12 ZAR/trade
- Realised (47 real closes per lane_gate._is_real_close, net of fees): -0.22 ZAR/trade | sd 2.08 | SE 0.30
- Gap: -0.33 ZAR/trade | t = -1.10 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.183% over 13/21 slices (pool 157) ~ +0.18 ZAR | realised 32 closes -0.58 ZAR sd 2.41 SE 0.43 | gap -0.76 t -1.79 | NOT ESTABLISHED
- hip3: claimed median +0.119% over 465/465 slices (pool 732) ~ +0.12 ZAR | realised 15 closes +0.57 ZAR sd 0.62 | INSUFFICIENT SAMPLE (n<30)
- Ledger: 23772 decision rows; 47 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 23725 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 32 | wins: 9 | win%: 28.1 | P&L: **-18.68 ZAR** | today: +1.47 | 7d: -18.68 | 30d: -18.68
- By exit: target +9.9, horizon -2.7, regime_shift -4.6, stop -21.3
- By entry regime (n/pnl): bear 20/+0.5, bull 1/-3.8, neutral 11/-15.4
- Top slices: feat_ret_10:2:LONG:h19 1n/1w +9.91; feat_realized_vol_20:2:LONG:h20 8n/7w +1.47; feat_realized_vol_20:2:LONG:h23 3n/1w -0.13; feat_realized_vol_20:2:LONG:h22 4n/0w -1.39; feat_realized_vol_20:2:LONG:h21 3n/0w -2.71
- Worst slices: feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; feat_atr_norm_ext:2:LONG:h13 7n/0w -4.88; feat_realized_vol_20:2:LONG:h21 3n/0w -2.71; feat_realized_vol_20:2:LONG:h22 4n/0w -1.39
- Top pairs: ARBUSDC 1n +9.91; LINKUSDC 2n +0.17; HYPEUSDC 5n +0.14; ENAUSDC 1n -0.10; ZECUSDC 1n -0.39
- Worst pairs: FILUSDC 1n -5.08; TRUMPUSDC 1n -4.96; ETHUSDC 6n -4.44; XRPUSDC 1n -3.79; BNBUSDC 1n -2.30

### HIP3

- Closed: 15 | wins: 14 | win%: 93.3 | P&L: **+8.55 ZAR** | today: +0.00 | 7d: +8.55 | 30d: +8.55
- By exit: target +5.0, horizon +2.1, regime_shift +1.6, trail_stop +1.0, stop -1.1
- By entry regime (n/pnl): bull 10/+4.8, bear 5/+3.7
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 1n/1w +2.05; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 2n/2w +1.07; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01
- Worst slices: hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 2n/1w -0.58; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 2n/2w +1.07; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 1n/1w +2.05
- Top pairs: XYZ:STRC 8n +3.98; PARA:MELI 2n +3.06; XYZ:SILVER 1n +0.71; XYZ:BRENTOIL 1n +0.49; XYZ:NATGAS 1n +0.36
- Worst pairs: XYZ:PALLADIUM 2n -0.05; XYZ:NATGAS 1n +0.36; XYZ:BRENTOIL 1n +0.49; XYZ:SILVER 1n +0.71; PARA:MELI 2n +3.06

## 4. Open positions & risk

- **NATIVE**: 0 open, stop-risk **0.00 ZAR**

- **HIP3**: 6 open, stop-risk **12.01 ZAR**
  - PARA:RDDT SELL ntl=100 risk=4.65 bars=5 stop=166.79999999999999210 peak=159.37
  - PARA:CRWD SELL ntl=100 risk=3.87 bars=5 stop=252.03749999999998405 peak=242.63
  - PARA:CIEN SELL ntl=100 risk=1.56 bars=5 stop=339.73 peak=334.48
  - PARA:MELI SELL ntl=100 risk=0.99 bars=0 stop=1849.22499999999996625 peak=1831.0
  - PARA:AVGO SELL ntl=100 risk=0.94 bars=10 stop=345.24999999999999390 peak=342.04
  - XYZ:COPPER BUY ntl=100 risk=0.00 bars=17 stop=6.4221500000000000900 peak=6.4683

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **12.01 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 21 | HIP-3: 465
- Native top (by paper P&L):
  - `feat_ret_10:2:LONG:h19` edge=0.0077 n=16875 p=0.0000 src=validated_walk_forward unproven=False paper=1n/+9.91
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0058 n=17004 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+5.56
  - `feat_ret_autocorr:2:LONG:h15` edge=0.0027 n=13718 p=0.0449 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_5:0:LONG:h16` edge=0.0011 n=16118 p=0.1532 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_rsi_divergence:2:LONG:h19` edge=0.0017 n=14280 p=0.0118 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_3:0:LONG:h18` edge=0.0020 n=16073 p=0.0163 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vol_breakout:0:LONG:h20` edge=0.0007 n=16229 p=0.5675 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_rsi_14:0:LONG:h24` edge=0.0015 n=14391 p=0.1765 src=validated_walk_forward unproven=False paper=0n/+0.00
- HIP-3 top (by paper P&L):
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h6` edge=0.0049 n=505 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h8` edge=0.0070 n=503 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h8` edge=0.0047 n=295 p=0.0022 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h9` edge=0.0082 n=502 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h9` edge=0.0054 n=295 p=0.0151 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h10` edge=0.0094 n=501 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` edge=0.0108 n=499 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h12` edge=0.0117 n=497 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **15/50** | ghost rows: **36/50** | PnL: **+8.55 ZAR**
- Gate verdict: **NOT READY**

## 8. Research / honesty checks

- Latest research: 2026-09-16T03:18:43+00:00 | discovered 7488 | validated 157 | reg-confounded 6148 | hostile-unproven 0
- floors: {"PERP": "69.0", "SPOT": "140.0"} | book: {"blocked_for_green_breadth": 0, "carried_cooldown": 0, "carried_decayed": 0, "carried_kinds": ["PERP"], "carried_monitored": 7, "carried_total": 7, "concentrated": 0, "cooldown": 0, "decayed": 0, "families_considered": 14, "families_promoted": 13, "green_assets_total": 461, "monitored": 13, "multi_horizon_min_passes": 2, "multi_horizon_select": "edge_per_bar", "net_edge_floor_enter_bps": {"PERP": "69.0", "SPOT": "140.0"}, "net_edge_floor_keep_bps": {"PERP": "52.9", "SPOT": "140.0"}, "paper_protected": 1, "per_asset_aware": true, "promotable": 52, "promoted_green_fraction_mean": 0.3064, "rows_total_after_sync": 21, "session_gate_blocked": 0, "validated": 157}
- Short audit: discovered=3744 validated=3744 passing=0 eligible=0 best=-6.1b best_fail=direction_ok,breadth_ok,mean_net<=0
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

- Label: **bear** | breadth bear=0.7667 bull=0.0 neutral=0.2 | symbols=29
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 7 / bull 0
- as_of: 2026-09-16T02:00:30Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 2304 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=365 eligible=530 best=208.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-9.56 | frozen=YES
- HIP-3 lane: **GREEN** | closed=15 pnl=+8.55 | frozen=NO
- Frozen lanes: native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 1
  - `feat_realized_vol_20:2:LONG:h20` pnl=+1.47
- Tradable slices: native **21/21** | hip3 **465/465**
- **COMA LANES: native** — frozen with no tradable slice on an earned green record; auditions may still open.
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 5
  - `feat_atr_norm_ext:2:LONG:h13` lane_not_green
  - `feat_realized_vol_20:2:LONG:h21` lane_not_green
  - `feat_realized_vol_20:2:LONG:h22` lane_not_green
  - `feat_realized_vol_20:2:LONG:h23` lane_not_green
  - `feat_realized_vol_20:2:LONG:h24` lane_not_green

## 13. Signal activity

- Latest scan 2026-09-13T04:40:20: errors=0 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=7
- green_gate: native_green=False hip3_green=True frozen=native islands=4 blocks=17
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
