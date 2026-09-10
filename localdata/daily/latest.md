# Breakwater daily print — 2026-09-10 01:56 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

> ## COMA ALARM — HIP3

> No **proven** slice in this lane. Auditions can still open entries, so
> this is not a dead lane: it trades, but nothing in it trades on a record
> it earned, so it cannot unfreeze itself. The runner will keep reporting
> operational, which is why this block exists. Attention, not intervention.

## 1. Posture

- Mode: **readonly** | VALR equity: **389.17 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **1859.52 ZAR** (seed 2000) | lifetime: **-140.48 ZAR** | closed: 90
- Today: 5 closed, **-35.59 ZAR**
- 7d: **-109.98 ZAR** | 30d: **-140.48 ZAR**

## 3. Lanes

### NATIVE

- Closed: 67 | wins: 26 | win%: 38.8 | P&L: **-116.81 ZAR** | today: -35.59 | 7d: -86.30 | 30d: -116.81
- By exit: target +64.1, trail_stop +21.6, lane_gate +7.6, rotated -36.0, horizon -72.2, stop -102.0
- By entry regime (n/pnl): bull 23/+24.7, bear 11/-38.9, neutral 33/-102.6
- Top slices: feat_ext_vs_ma_20:0:LONG:h24 18n/9w +17.36; feat_ret_20:0:LONG:h24 1n/1w +11.91; feat_atr_norm_ext:2:LONG:h13 2n/2w +8.82; feat_ext_vs_ma_50:0:LONG:h21 2n/2w +2.35; feat_vol_regime:2:LONG:h11 1n/1w +0.26
- Worst slices: feat_realized_vol_20:2:LONG:h13 4n/0w -38.28; feat_atr_norm_ext:0:LONG:h24 2n/0w -23.34; feat_ext_vs_ma_50:0:LONG:h24 4n/2w -22.58; feat_ret_5:0:LONG:h24 5n/2w -20.67; feat_ret_10:2:LONG:h15 2n/0w -11.37
- Top pairs: ZECUSDC 3n +39.15; MONUSDC 3n +8.57; JUPUSDC 1n +8.54; CRVUSDC 2n +7.07; LINKUSDC 6n +6.88
- Worst pairs: XMRUSDC 4n -32.97; DOGEUSDC 6n -24.34; FARTCOINUSDC 1n -20.07; BNBUSDC 7n -19.48; UNIUSDC 1n -18.95

### HIP3

- Closed: 23 | wins: 9 | win%: 39.1 | P&L: **-23.67 ZAR** | today: +0.00 | 7d: -23.67 | 30d: -23.67
- By exit: lane_gate +11.5, target +9.2, trail_stop +3.7, horizon -4.3, rotated -5.8, stop -37.9
- By entry regime (n/pnl): neutral 10/-0.6, bull 4/-10.3, bear 9/-12.7
- Top slices: hip3_xyz_commodity_c0:feat_ext_vs_ma_50:2:LONG:h20 1n/1w +1.52; hip3_xyz_equity_c0:feat_realized_vol_20:2:LONG:h17 3n/1w +0.76; hip3_xyz_commodity_c0:feat_trend_slope_20:0:LONG:h20 2n/0w -0.56; hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24 10n/5w -2.60; hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG:h24 3n/1w -6.37
- Worst slices: hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 4n/1w -16.43; hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG:h24 3n/1w -6.37; hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24 10n/5w -2.60; hip3_xyz_commodity_c0:feat_trend_slope_20:0:LONG:h20 2n/0w -0.56; hip3_xyz_equity_c0:feat_realized_vol_20:2:LONG:h17 3n/1w +0.76
- Top pairs: XYZ:EWT 1n +8.48; XYZ:DRAM 1n +6.59; XYZ:EWJ 1n +2.87; XYZ:PLATINUM 1n +1.52; XYZ:STRC 1n +0.72
- Worst pairs: XYZ:CL 1n -8.93; XYZ:BRENTOIL 1n -7.77; XYZ:EBAY 1n -6.10; XYZ:COST 3n -4.24; XYZ:AMAT 1n -3.98

## 4. Open positions & risk

- **NATIVE**: 2 open, stop-risk **25.30 ZAR**
  - ASTERUSDC BUY ntl=383 risk=15.45 bars=8 stop=0.7107175000000000190 peak=0.74063
  - ETHUSDC BUY ntl=380 risk=9.85 bars=5 stop=2400.949999999999975 peak=2464.8

- **HIP3**: 6 open, stop-risk **17.62 ZAR**
  - XYZ:ASML BUY ntl=391 risk=6.90 bars=12 stop=1711.2750000000000930 peak=1742.0
  - XYZ:EWJ BUY ntl=382 risk=3.96 bars=10 stop=96.215500000000005610 peak=97.224
  - XYZ:NFLX BUY ntl=382 risk=3.15 bars=10 stop=75.858250000000015135 peak=76.489
  - XYZ:COST BUY ntl=391 risk=2.63 bars=10 stop=895.06499999999997360 peak=901.13
  - XYZ:STRC BUY ntl=383 risk=0.97 bars=9 stop=97.718250000000000090 peak=97.966
  - XYZ:CRWD BUY ntl=393 risk=0.00 bars=36 stop=206.840000000000005950 peak=210.62

## 5. Aggregate risk leash

- Aggregate: **42.92 / 130.17 ZAR | 38.9% | ok**
- Remaining: 79.5350 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 0, "skipped": 0, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 0, "skipped": 0, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **ASTERUSDC** 15.4496 ZAR
- positions without bars: 4 | replayed: 4 | invalid: 0

## 6. Monitored books

- Native: 29 | HIP-3: 20
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
  - `hip3_xyz_equity_c0:feat_vol_regime:1:LONG:h24` edge=0.0062 n=9082 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24` edge=0.0019 n=10716 p=0.0440 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ret_20:1:LONG:h15` edge=0.0014 n=12601 p=0.0067 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_atr_norm_ext:1:LONG:h16` edge=0.0015 n=10490 p=0.0320 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_trend_strength_20:0:LONG:h22` edge=0.0019 n=10177 p=0.0075 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_realized_vol_20:0:LONG:h16` edge=0.0012 n=13937 p=0.0550 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ret_20:0:LONG:h24` edge=0.0019 n=10488 p=0.0513 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG:h24` edge=0.0021 n=10544 p=0.0310 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **23/50** | ghost rows: **114/50** | PnL: **-23.67 ZAR**
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

- Label: **neutral** | breadth bear=0.1538 bull=0.0769 neutral=0.7692 | symbols=13
- confirmed_bear: **False** | confirmed_bull: **True** | flip: **False** | flipped_from: bull | consecutive_bear: 0 / bull 122
- as_of: 2026-09-10T01:55:30Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 0 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=5592 validated=5592 passing=0 eligible=86 best=74.1b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-85.54 | frozen=YES
- HIP-3 lane: **RED** | closed=20 pnl=-18.03 | frozen=YES
- Frozen lanes: hip3, native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `feat_ext_vs_ma_20:0:LONG:h24` pnl=+17.36
  - `hip3_xyz_equity_c0:feat_realized_vol_20:2:LONG:h17` pnl=+0.76
- Tradable slices: native **29/29** | hip3 **18/20**
- **COMA LANES: hip3** — frozen with no tradable slice on an earned green record; auditions may still open.
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 10
  - `feat_ext_vs_ma_50:0:LONG:h24` lane_not_green
  - `feat_realized_vol_20:2:LONG:h13` lane_not_green
  - `feat_ret_10:0:LONG:h24` lane_not_green
  - `feat_ret_10:2:LONG:h13` lane_not_green
  - `feat_ret_5:0:LONG:h24` lane_not_green
  - `feat_trend_slope_20:0:LONG:h24` lane_not_green
  - `feat_trend_slope_20:2:LONG:h10` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24` lane_not_green
  - `hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG:h24` lane_not_green

## 13. Signal activity

- Latest scan 2026-09-10T01:38:38: errors=0 signals=None regime_blocked=None
- this cycle: closed=0 new_signals=0 skipped=0 slot_full=0 slice_full=0 pair_held=0
- Action funnel: lane_gate_blocked=2 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=0 | slot_full=0 | skipped=0
- green_gate: native_green=False hip3_green=False frozen=hip3,native islands=2 blocks=10
- aggregate_risk: ok open=42.9199 cap=130.1661 used=0.3890 remaining=79.5350 replayed=4 no_new_bars=4
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
