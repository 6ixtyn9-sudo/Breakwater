# Breakwater daily print — 2026-09-11 06:07 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

> ## COMA ALARM — HIP3

> No **proven** slice in this lane. Auditions can still open entries, so
> this is not a dead lane: it trades, but nothing in it trades on a record
> it earned, so it cannot unfreeze itself. The runner will keep reporting
> operational, which is why this block exists. Attention, not intervention.

## 1. Posture

- Mode: **readonly** | VALR equity: **393.23 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **1781.24 ZAR** (seed 2000) | lifetime: **-218.76 ZAR** | closed: 104
- Today: 5 closed, **-47.83 ZAR**
- 7d: **-192.76 ZAR** | 30d: **-218.76 ZAR**

## 2b. Claimed vs realised

- Book: 46 slices (native 29 | hip3 17); validated pools: native 524 | hip3 464; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 46 book slices present in the validated pools): +0.421% | at 389.77 ZAR mean notional/trade: +1.64 ZAR/trade
- Realised (104 real closes per lane_gate._is_real_close, net of fees): -2.10 ZAR/trade | sd 8.32 | SE 0.82
- Gap: -3.74 ZAR/trade | t = -4.59 (one-sample t of realised mean vs the claimed constant) | verdict: FALLS SHORT
- native: claimed median +0.525% over 29/29 slices (pool 524) ~ +2.04 ZAR | realised 75 closes -2.56 ZAR sd 9.45 SE 1.09 | gap -4.60 t -4.22 | FALLS SHORT
- hip3: claimed median +0.085% over 17/17 slices (pool 464) ~ +0.33 ZAR | realised 29 closes -0.93 ZAR sd 4.11 | INSUFFICIENT SAMPLE (n<30)
- Ledger: 117848 decision rows; 104 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 117744 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 75 | wins: 26 | win%: 34.7 | P&L: **-191.77 ZAR** | today: -47.83 | 7d: -167.66 | 30d: -191.77
- By exit: target +64.1, trail_stop +21.6, lane_gate +7.6, rotated -36.0, horizon -99.4, stop -149.7
- By entry regime (n/pnl): bull 23/+24.7, bear 14/-60.1, neutral 38/-156.4
- Top slices: feat_ext_vs_ma_20:0:LONG:h24 18n/9w +17.36; feat_ret_20:0:LONG:h24 1n/1w +11.91; feat_atr_norm_ext:2:LONG:h13 2n/2w +8.82; feat_ext_vs_ma_50:0:LONG:h21 2n/2w +2.35; feat_vol_regime:2:LONG:h11 1n/1w +0.26
- Worst slices: feat_realized_vol_20:2:LONG:h13 4n/0w -38.28; feat_ext_vs_ma_10:0:LONG:h24 3n/0w -37.74; feat_trend_strength_20:1:LONG:h19 3n/0w -27.78; feat_atr_norm_ext:0:LONG:h24 2n/0w -23.34; feat_ext_vs_ma_50:0:LONG:h24 4n/2w -22.58
- Top pairs: ZECUSDC 3n +39.15; MONUSDC 3n +8.57; JUPUSDC 1n +8.54; CRVUSDC 2n +7.07; LINKUSDC 6n +6.88
- Worst pairs: DOGEUSDC 7n -33.80; XMRUSDC 4n -32.97; SUIUSDC 3n -30.55; ASTERUSDC 2n -24.96; HYPEUSDC 6n -21.38

### HIP3

- Closed: 29 | wins: 13 | win%: 44.8 | P&L: **-26.98 ZAR** | today: +0.00 | 7d: -25.10 | 30d: -26.98
- By exit: lane_gate +11.5, target +9.2, trail_stop +8.4, horizon -5.1, rotated -5.8, stop -45.2
- By entry regime (n/pnl): neutral 12/-7.2, bear 12/-8.8, bull 5/-11.1
- Top slices: hip3_xyz_equity_c0:feat_ext_vs_ma_20:0:LONG:h24 1n/1w +1.62; hip3_xyz_commodity_c0:feat_ext_vs_ma_50:2:LONG:h20 1n/1w +1.52; hip3_xyz_equity_c0:feat_realized_vol_20:2:LONG:h17 3n/1w +0.76; hip3_xyz_commodity_c0:feat_trend_slope_20:0:LONG:h20 2n/0w -0.56; hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24 11n/6w -0.74
- Worst slices: hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 4n/1w -16.43; hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG:h24 3n/1w -6.37; hip3_xyz_equity_c0:feat_vol_regime:1:LONG:h24 3n/2w -6.04; hip3_xyz_equity_c0:feat_trend_strength_20:0:LONG:h22 1n/0w -0.74; hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24 11n/6w -0.74
- Top pairs: XYZ:EWT 1n +8.48; XYZ:DRAM 1n +6.59; XYZ:EWJ 2n +3.60; XYZ:CRWD 1n +1.86; XYZ:NFLX 1n +1.62
- Worst pairs: XYZ:ASML 2n -9.12; XYZ:CL 1n -8.93; XYZ:BRENTOIL 1n -7.77; XYZ:EBAY 1n -6.10; XYZ:AMAT 1n -3.98

## 4. Open positions & risk

- **NATIVE**: 5 open, stop-risk **59.43 ZAR**
  - ONDOUSDC BUY ntl=372 risk=17.25 bars=22 stop=0.3373299999999999995 peak=0.35372
  - LINKUSDC BUY ntl=366 risk=12.71 bars=10 stop=11.203750000000000085 peak=11.607
  - LTCUSDC BUY ntl=372 risk=12.08 bars=22 stop=50.712999999999995975 peak=52.414
  - BNBUSDC BUY ntl=372 risk=9.31 bars=22 stop=700.8499999999999830 peak=718.83
  - ETHUSDC BUY ntl=367 risk=8.08 bars=15 stop=2386.2499999999999110 peak=2439.9

- **HIP3**: 1 open, stop-risk **0.76 ZAR**
  - XYZ:STRC BUY ntl=368 risk=0.76 bars=15 stop=97.66200000000000180 peak=97.864

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **60.19 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 29 | HIP-3: 17
- Native top (by paper P&L):
  - `feat_ext_vs_ma_20:0:LONG:h24` edge=0.0070 n=15301 p=0.0000 src=validated_walk_forward unproven=False paper=18n/+17.36
  - `feat_atr_norm_ext:2:LONG:h13` edge=0.0077 n=15915 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+8.82
  - `feat_atr_norm_ext:2:LONG:h15` edge=0.0085 n=15663 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_20:2:LONG:h13` edge=0.0070 n=17286 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0065 n=17661 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_20:2:LONG:h10` edge=0.0051 n=17687 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vol_regime:2:LONG:h12` edge=0.0053 n=14691 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_10:2:LONG:h15` edge=0.0067 n=17389 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
- HIP-3 top (by paper P&L):
  - `hip3_xyz_equity_c0:feat_atr_norm_ext:1:LONG:h16` edge=0.0011 n=9676 p=0.1282 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_20:1:LONG:h16` edge=0.0008 n=11431 p=0.1760 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_realized_vol_20:0:LONG:h18` edge=0.0008 n=12593 p=0.2498 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_realized_vol_20:1:LONG:h24` edge=0.0017 n=10604 p=0.1017 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ret_20:1:LONG:h19` edge=0.0012 n=11409 p=0.0525 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_10:1:LONG:h20` edge=0.0008 n=12127 p=0.1730 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ret_5:1:LONG:h24` edge=0.0009 n=12246 p=0.1747 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ret_3:0:LONG:h22` edge=0.0007 n=9677 p=0.2191 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **29/50** | ghost rows: **143/50** | PnL: **-26.98 ZAR**
- Gate verdict: **NOT READY**

## 8. Research / honesty checks

- Latest research: 2026-09-10T00:34:58+00:00 | discovered 3744 | validated 524 | reg-confounded 3006 | hostile-unproven 0
- floors: {"PERP": "72.8", "SPOT": "140.0"} | book: {"blocked_for_green_breadth": 0, "carried_cooldown": 0, "carried_decayed": 0, "carried_kinds": [], "carried_monitored": 0, "carried_total": 0, "concentrated": 0, "cooldown": 3, "decayed": 4, "families_considered": 35, "families_promoted": 35, "green_assets_total": 1277, "monitored": 28, "multi_horizon_min_passes": 2, "multi_horizon_select": "edge_per_bar", "net_edge_floor_enter_bps": {"PERP": "72.8", "SPOT": "140.0"}, "net_edge_floor_keep_bps": {"PERP": "52.7", "SPOT": "140.0"}, "paper_protected": 1, "per_asset_aware": true, "promotable": 319, "promoted_green_fraction_mean": 0.3141, "rows_total_after_sync": 36, "session_gate_blocked": 0, "validated": 524}
- Short audit: discovered=1872 validated=1872 passing=0 eligible=0 best=-8.0b best_fail=temporal_pass,breadth_ok,regime_confounded,mean_net<=0
- pair_errors: [{"error": "HTTPError: 500 Server Error: Internal Server Error for url: https://api.hyperliquid.xyz/info", "pair": "KBONKUSDC"}]
- Deep audit: candidates=18720 preliminary_passes=0 audit_passes=0 plateaus=0 fetch_errors=32

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

- Label: **bear** | breadth bear=0.7667 bull=0.0 neutral=0.2333 | symbols=30
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 21 / bull 0
- as_of: 2026-09-11T06:00:23Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 0 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=5616 validated=5616 passing=0 eligible=205 best=198.2b best_fail=breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-161.12 | frozen=YES
- HIP-3 lane: **RED** | closed=20 pnl=-11.00 | frozen=YES
- Frozen lanes: hip3, native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `feat_ext_vs_ma_20:0:LONG:h24` pnl=+17.36
  - `hip3_xyz_equity_c0:feat_realized_vol_20:2:LONG:h17` pnl=+0.76
- Tradable slices: native **28/29** | hip3 **16/17**
- **COMA LANES: hip3** — frozen with no tradable slice on an earned green record; auditions may still open.
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 13
  - `feat_ext_vs_ma_10:0:LONG:h24` lane_not_green
  - `feat_ext_vs_ma_50:0:LONG:h24` lane_not_green
  - `feat_realized_vol_20:2:LONG:h13` lane_not_green
  - `feat_ret_10:0:LONG:h24` lane_not_green
  - `feat_ret_10:2:LONG:h13` lane_not_green
  - `feat_ret_5:0:LONG:h24` lane_not_green
  - `feat_trend_slope_20:0:LONG:h24` lane_not_green
  - `feat_trend_slope_20:2:LONG:h10` lane_not_green
  - `feat_trend_strength_20:1:LONG:h19` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24` lane_not_green
  - `hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG:h24` lane_not_green
  - `hip3_xyz_equity_c0:feat_vol_regime:1:LONG:h24` lane_not_green

## 13. Signal activity

- Latest scan 2026-09-11T06:07:34: errors=0 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=2
- green_gate: native_green=False hip3_green=False frozen=hip3,native islands=2 blocks=13
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
