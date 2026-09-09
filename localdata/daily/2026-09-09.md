# Breakwater daily print — 2026-09-09 02:56 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

> ## WARNING — only 2 proven slice(s) trading (native 1, hip3 1); 49 slices are auditioning in frozen lanes. One bad proven trade from coma.

## 1. Posture

- Mode: **readonly** | VALR equity: **399.76 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **1956.97 ZAR** (seed 2000) | lifetime: **-43.03 ZAR** | closed: 73
- Today: 0 closed, **+0.00 ZAR**
- 7d: **-43.03 ZAR** | 30d: **-43.03 ZAR**

## 3. Lanes

### NATIVE

- Closed: 52 | wins: 22 | win%: 42.3 | P&L: **-22.20 ZAR** | today: +0.00 | 7d: -22.20 | 30d: -22.20
- By exit: target +64.1, trail_stop +19.5, lane_gate +7.6, rotated -0.4, horizon -47.2, stop -65.8
- By entry regime (n/pnl): bull 22/+35.3, neutral 20/-24.8, bear 10/-32.8
- Top slices: feat_ext_vs_ma_20:0:LONG:h24 13n/7w +42.62; feat_ret_20:0:LONG:h24 1n/1w +11.91; feat_atr_norm_ext:2:LONG:h13 2n/2w +8.82; feat_vol_regime:2:LONG:h11 1n/1w +0.26; feat_trend_slope_20:2:LONG:h10 3n/1w -0.21
- Worst slices: feat_ext_vs_ma_50:0:LONG:h24 4n/2w -22.58; feat_ret_5:0:LONG:h24 5n/2w -20.67; feat_ret_10:0:LONG:h24 3n/2w -9.44; feat_realized_vol_20:2:LONG:h13 1n/0w -9.32; feat_trend_slope_20:0:LONG:h24 3n/1w -7.33
- Top pairs: ZECUSDC 3n +39.15; LINKUSDC 4n +31.81; CRVUSDC 1n +13.20; MONUSDC 3n +8.57; NEARUSDC 1n +6.52
- Worst pairs: XMRUSDC 4n -32.97; FARTCOINUSDC 1n -20.07; PUMPUSDC 1n -17.84; DOGEUSDC 5n -13.72; ENAUSDC 2n -10.83

### HIP3

- Closed: 21 | wins: 8 | win%: 38.1 | P&L: **-20.83 ZAR** | today: +0.00 | 7d: -20.83 | 30d: -20.83
- By exit: lane_gate +11.5, target +9.2, trail_stop +3.7, horizon -1.5, rotated -5.8, stop -37.9
- By entry regime (n/pnl): neutral 10/-0.6, bear 7/-9.9, bull 4/-10.3
- Top slices: hip3_xyz_commodity_c0:feat_ext_vs_ma_50:2:LON 1n/1w +1.52; hip3_xyz_equity_c0:feat_realized_vol_20:2:LON 3n/1w +0.76; hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h 8n/4w +0.24; hip3_xyz_commodity_c0:feat_trend_slope_20:0:L 2n/0w -0.56; hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG 3n/1w -6.37
- Worst slices: hip3_xyz_commodity_c0:feat_vol_regime:1:LONG: 4n/1w -16.43; hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG 3n/1w -6.37; hip3_xyz_commodity_c0:feat_trend_slope_20:0:L 2n/0w -0.56; hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h 8n/4w +0.24; hip3_xyz_equity_c0:feat_realized_vol_20:2:LON 3n/1w +0.76
- Top pairs: XYZ:EWT 1n +8.48; XYZ:DRAM 1n +6.59; XYZ:EWJ 1n +2.87; XYZ:PLATINUM 1n +1.52; XYZ:STRC 1n +0.72
- Worst pairs: XYZ:CL 1n -8.93; XYZ:BRENTOIL 1n -7.77; XYZ:EBAY 1n -6.10; XYZ:AMAT 1n -3.98; XYZ:AAPL 2n -3.46

## 4. Open positions & risk

- **NATIVE**: 8 open, stop-risk **116.43 ZAR**
  - UNIUSDC BUY ntl=334 risk=19.57 bars=10 stop=6.516825000000000045 peak=6.9228
  - JUPUSDC BUY ntl=373 risk=19.57 bars=10 stop=0.22997250000000001170 peak=0.24272
  - ASTERUSDC BUY ntl=391 risk=17.46 bars=10 stop=0.7296099999999999945 peak=0.76367
  - LINKUSDC BUY ntl=391 risk=16.08 bars=6 stop=12.02299999999999945 peak=12.538
  - LTCUSDC BUY ntl=391 risk=13.31 bars=10 stop=53.12149999999999945 peak=54.991
  - HYPEUSDC BUY ntl=391 risk=12.58 bars=10 stop=81.10949999999999880 peak=83.804

- **HIP3**: 3 open, stop-risk **9.53 ZAR**
  - XYZ:DKNG BUY ntl=393 risk=5.87 bars=13 stop=23.333999999999998155 peak=23.688
  - XYZ:COST BUY ntl=391 risk=3.66 bars=10 stop=899.17999999999999060 peak=907.67
  - XYZ:CRWD BUY ntl=393 risk=0.00 bars=13 stop=206.840000000000005950 peak=210.62

## 5. Aggregate risk leash

- Aggregate: **125.96 / 136.99 ZAR | 99.7% | warning**
- Remaining: 0.4519 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 0, "skipped": 0, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 0, "skipped": 0, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **JUPUSDC** 19.5697 ZAR
- positions without bars: 10 | replayed: 1 | invalid: 0

## 6. Monitored books

- Native: 34 | HIP-3: 20
- Native top (by paper P&L):
  - `feat_ext_vs_ma_20:0:LONG:h24` edge=0.0086 n=15222 p=0.0000 src=validated_walk_forward unproven=False paper=13n/+42.62
  - `feat_ret_20:0:LONG:h24` edge=0.0083 n=15176 p=0.0000 src=validated_walk_forward unproven=False paper=1n/+11.91
  - `feat_atr_norm_ext:2:LONG:h13` edge=0.0077 n=15915 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+8.82
  - `feat_ret_20:2:LONG:h8` edge=0.0045 n=17527 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vol_regime:2:LONG:h12` edge=0.0059 n=15279 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_atr_norm_ext:2:LONG:h12` edge=0.0072 n=15575 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_20:2:LONG:h13` edge=0.0075 n=17066 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_trend_strength_20:2:LONG:h13` edge=0.0063 n=15517 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Closed paper trades: **21/50** | ghost rows: **104/50** | PnL: **-20.83 ZAR**
- Gate verdict: **NOT READY**

## 8. Research / honesty checks

- Latest research: 2026-09-09T00:10:31+00:00 | discovered 3744 | validated 766 | reg-confounded 2961 | hostile-unproven 0
- floors: {"PERP": "70.0", "SPOT": "140.0"} | book: {"blocked_for_green_breadth": 0, "carried_cooldown": 0, "carried_decayed": 0, "carried_kinds": [], "carried_monitored": 0, "carried_total": 0, "concentrated": 0, "cooldown": 0, "decayed": 4, "families_considered": 38, "families_promoted": 37, "green_assets_total": 1567, "monitored": 33, "multi_horizon_min_passes": 2, "multi_horizon_select": "edge_per_bar", "net_edge_floor_enter_bps": {"PERP": "70.0", "SPOT": "140.0"}, "net_edge_floor_keep_bps": {"PERP": "49.6", "SPOT": "140.0"}, "paper_protected": 1, "per_asset_aware": true, "promotable": 358, "promoted_green_fraction_mean": 0.3633, "rows_total_after_sync": 38, "session_gate_blocked": 0, "validated": 766}
- Short audit: discovered=1872 validated=1872 passing=0 eligible=0 best=-9.5b best_fail=temporal_pass,direction_ok,breadth_ok,regime_confounded,mean_net<=0
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

- Label: **neutral** | breadth bear=0.0625 bull=0.3125 neutral=0.625 | symbols=16
- confirmed_bear: **False** | confirmed_bull: **True** | flip: **False** | flipped_from: neutral | consecutive_bear: 0 / bull 107
- as_of: 2026-09-09T02:55:38Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 0 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=5592 validated=5592 passing=0 eligible=86 best=74.1b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-9.65 | frozen=YES
- HIP-3 lane: **RED** | closed=20 pnl=-18.95 | frozen=YES
- Frozen lanes: hip3, native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 3
  - `feat_ext_vs_ma_20:0:LONG:h24` pnl=+42.62
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24` pnl=+0.24
  - `hip3_xyz_equity_c0:feat_realized_vol_20:2:LONG:h17` pnl=+0.76
- Tradable slices: native **30/34** | hip3 **19/20**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 8
  - `feat_ext_vs_ma_50:0:LONG:h24` lane_not_green
  - `feat_ret_10:0:LONG:h24` lane_not_green
  - `feat_ret_10:2:LONG:h13` lane_not_green
  - `feat_ret_5:0:LONG:h24` lane_not_green
  - `feat_trend_slope_20:0:LONG:h24` lane_not_green
  - `feat_trend_slope_20:2:LONG:h10` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green
  - `hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG:h24` lane_not_green

## 13. Signal activity

- Latest scan 2026-09-09T02:42:04: errors=0 signals=None regime_blocked=None
- this cycle: closed=0 new_signals=0 skipped=0 slot_full=0 slice_full=0 pair_held=0
- Action funnel: lane_gate_blocked=5 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=0 | slot_full=0 | skipped=0
- green_gate: native_green=False hip3_green=False frozen=hip3,native islands=3 blocks=8
- aggregate_risk: warning open=125.9578 cap=136.9879 used=0.9967 remaining=0.4519 replayed=1 no_new_bars=10
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
