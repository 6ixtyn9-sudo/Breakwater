# Breakwater daily print — 2026-09-10 21:36 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

> ## COMA ALARM — HIP3

> No **proven** slice in this lane. Auditions can still open entries, so
> this is not a dead lane: it trades, but nothing in it trades on a record
> it earned, so it cannot unfreeze itself. The runner will keep reporting
> operational, which is why this block exists. Attention, not intervention.

## 1. Posture

- Mode: **readonly** | VALR equity: **391.13 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **1829.07 ZAR** (seed 2000) | lifetime: **-170.93 ZAR** | closed: 99
- Today: 14 closed, **-66.04 ZAR**
- 7d: **-144.94 ZAR** | 30d: **-170.93 ZAR**

## 2b. Claimed vs realised

- Book: 48 slices (native 31 | hip3 17); validated pools: native 524 | hip3 464; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 48 book slices present in the validated pools): +0.421% | at 390.76 ZAR mean notional/trade: +1.64 ZAR/trade
- Realised (99 real closes per lane_gate._is_real_close, net of fees): -1.73 ZAR/trade | sd 8.23 | SE 0.83
- Gap: -3.37 ZAR/trade | t = -4.07 (one-sample t of realised mean vs the claimed constant) | verdict: FALLS SHORT
- native: claimed median +0.525% over 31/31 slices (pool 524) ~ +2.05 ZAR | realised 70 closes -2.06 ZAR sd 9.44 SE 1.13 | gap -4.11 t -3.64 | FALLS SHORT
- hip3: claimed median +0.085% over 17/17 slices (pool 464) ~ +0.33 ZAR | realised 29 closes -0.93 ZAR sd 4.11 | INSUFFICIENT SAMPLE (n<30)
- Ledger: 111113 decision rows; 99 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 111014 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 70 | wins: 26 | win%: 37.1 | P&L: **-143.95 ZAR** | today: -62.73 | 7d: -119.83 | 30d: -143.95
- By exit: target +64.1, trail_stop +21.6, lane_gate +7.6, rotated -36.0, horizon -99.4, stop -102.0
- By entry regime (n/pnl): bull 23/+24.7, bear 11/-38.9, neutral 36/-129.8
- Top slices: feat_ext_vs_ma_20:0:LONG:h24 18n/9w +17.36; feat_ret_20:0:LONG:h24 1n/1w +11.91; feat_atr_norm_ext:2:LONG:h13 2n/2w +8.82; feat_ext_vs_ma_50:0:LONG:h21 2n/2w +2.35; feat_vol_regime:2:LONG:h11 1n/1w +0.26
- Worst slices: feat_realized_vol_20:2:LONG:h13 4n/0w -38.28; feat_trend_strength_20:1:LONG:h19 3n/0w -27.78; feat_atr_norm_ext:0:LONG:h24 2n/0w -23.34; feat_ext_vs_ma_50:0:LONG:h24 4n/2w -22.58; feat_ret_5:0:LONG:h24 5n/2w -20.67
- Top pairs: ZECUSDC 3n +39.15; MONUSDC 3n +8.57; JUPUSDC 1n +8.54; CRVUSDC 2n +7.07; LINKUSDC 6n +6.88
- Worst pairs: XMRUSDC 4n -32.97; ASTERUSDC 2n -24.96; DOGEUSDC 6n -24.34; FARTCOINUSDC 1n -20.07; BNBUSDC 7n -19.48

### HIP3

- Closed: 29 | wins: 13 | win%: 44.8 | P&L: **-26.98 ZAR** | today: -3.31 | 7d: -25.10 | 30d: -26.98
- By exit: lane_gate +11.5, target +9.2, trail_stop +8.4, horizon -5.1, rotated -5.8, stop -45.2
- By entry regime (n/pnl): neutral 12/-7.2, bear 12/-8.8, bull 5/-11.1
- Top slices: hip3_xyz_equity_c0:feat_ext_vs_ma_20:0:LONG:h24 1n/1w +1.62; hip3_xyz_commodity_c0:feat_ext_vs_ma_50:2:LONG:h20 1n/1w +1.52; hip3_xyz_equity_c0:feat_realized_vol_20:2:LONG:h17 3n/1w +0.76; hip3_xyz_commodity_c0:feat_trend_slope_20:0:LONG:h20 2n/0w -0.56; hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24 11n/6w -0.74
- Worst slices: hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 4n/1w -16.43; hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG:h24 3n/1w -6.37; hip3_xyz_equity_c0:feat_vol_regime:1:LONG:h24 3n/2w -6.04; hip3_xyz_equity_c0:feat_trend_strength_20:0:LONG:h22 1n/0w -0.74; hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24 11n/6w -0.74
- Top pairs: XYZ:EWT 1n +8.48; XYZ:DRAM 1n +6.59; XYZ:EWJ 2n +3.60; XYZ:CRWD 1n +1.86; XYZ:NFLX 1n +1.62
- Worst pairs: XYZ:ASML 2n -9.12; XYZ:CL 1n -8.93; XYZ:BRENTOIL 1n -7.77; XYZ:EBAY 1n -6.10; XYZ:AMAT 1n -3.98

## 4. Open positions & risk

- **NATIVE**: 10 open, stop-risk **116.48 ZAR**
  - ONDOUSDC BUY ntl=372 risk=17.25 bars=13 stop=0.3373299999999999995 peak=0.35372
  - SUIUSDC BUY ntl=372 risk=16.80 bars=13 stop=0.729662499999999995 peak=0.76415
  - HYPEUSDC BUY ntl=372 risk=15.34 bars=13 stop=79.77874999999999920 peak=83.209
  - LINKUSDC BUY ntl=366 risk=12.71 bars=1 stop=11.203750000000000085 peak=11.607
  - LTCUSDC BUY ntl=372 risk=12.08 bars=13 stop=50.712999999999995975 peak=52.414
  - SOLUSDC BUY ntl=368 risk=10.60 bars=8 stop=96.19624999999999860 peak=99.047
  - BNBUSDC BUY ntl=372 risk=9.31 bars=13 stop=700.8499999999999830 peak=718.83
  - DOGEUSDC BUY ntl=369 risk=9.13 bars=9 stop=0.08314199999999999435 peak=0.08525
  - ETHUSDC BUY ntl=367 risk=8.08 bars=6 stop=2386.2499999999999110 peak=2439.9
  - BTCUSDC BUY ntl=369 risk=5.17 bars=9 stop=76750.75 peak=77841.0

- **HIP3**: 1 open, stop-risk **0.76 ZAR**
  - XYZ:STRC BUY ntl=368 risk=0.76 bars=7 stop=97.66200000000000180 peak=97.864

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **117.24 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 31 | HIP-3: 17
- Native top (by paper P&L):
  - `feat_ext_vs_ma_20:0:LONG:h24` edge=0.0070 n=15301 p=0.0000 src=validated_walk_forward unproven=False paper=18n/+17.36
  - `feat_atr_norm_ext:2:LONG:h13` edge=0.0077 n=15915 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+8.82
  - `feat_atr_norm_ext:2:LONG:h15` edge=0.0085 n=15663 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_20:2:LONG:h13` edge=0.0070 n=17286 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0065 n=17661 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_20:2:LONG:h10` edge=0.0051 n=17687 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vol_regime:2:LONG:h12` edge=0.0053 n=14691 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_realized_vol_20:2:LONG:h12` edge=0.0053 n=24468 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Label: **bear** | breadth bear=0.5667 bull=0.0333 neutral=0.4 | symbols=30
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 6 / bull 0
- as_of: 2026-09-10T21:30:20Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 0 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=5616 validated=5616 passing=0 eligible=205 best=198.2b best_fail=breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-113.97 | frozen=YES
- HIP-3 lane: **RED** | closed=20 pnl=-11.00 | frozen=YES
- Frozen lanes: hip3, native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `feat_ext_vs_ma_20:0:LONG:h24` pnl=+17.36
  - `hip3_xyz_equity_c0:feat_realized_vol_20:2:LONG:h17` pnl=+0.76
- Tradable slices: native **31/31** | hip3 **16/17**
- **COMA LANES: hip3** — frozen with no tradable slice on an earned green record; auditions may still open.
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 12
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

- Latest scan 2026-09-10T21:36:40: errors=0 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=1
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 3, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 1, "pair_held": 6, "regime_blocked": 546, "skipped": 10, "slice_full": 0, "slot_full": 164})
- green_gate: native_green=False hip3_green=False frozen=hip3,native islands=2 blocks=12
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
