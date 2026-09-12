# Breakwater daily print — 2026-09-12 21:57 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **396.75 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **1766.62 ZAR** (seed 2000) | lifetime: **-233.38 ZAR** | closed: 130
- Today: 5 closed, **-0.10 ZAR**
- 7d: **-194.44 ZAR** | 30d: **-233.38 ZAR**

## 2b. Claimed vs realised

- Book: 49 slices (native 32 | hip3 17); validated pools: native 524 | hip3 464; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 49 book slices present in the validated pools): +0.428% | at 383.02 ZAR mean notional/trade: +1.64 ZAR/trade
- Realised (130 real closes per lane_gate._is_real_close, net of fees): -1.80 ZAR/trade | sd 8.48 | SE 0.74
- Gap: -3.43 ZAR/trade | t = -4.62 (one-sample t of realised mean vs the claimed constant) | verdict: FALLS SHORT
- native: claimed median +0.526% over 32/32 slices (pool 524) ~ +2.00 ZAR | realised 99 closes -2.15 ZAR sd 9.42 SE 0.95 | gap -4.15 t -4.39 | FALLS SHORT
- hip3: claimed median +0.085% over 17/17 slices (pool 464) ~ +0.33 ZAR | realised 31 closes -0.67 ZAR sd 4.17 SE 0.75 | gap -1.00 t -1.33 | NOT ESTABLISHED
- Ledger: 168456 decision rows; 130 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 168326 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 99 | wins: 40 | win%: 40.4 | P&L: **-212.68 ZAR** | today: -0.10 | 7d: -188.89 | 30d: -212.68
- By exit: target +101.5, trail_stop +45.1, lane_gate +7.6, rotated -47.9, horizon -97.3, stop -221.6
- By entry regime (n/pnl): bull 24/+10.8, bear 25/-12.1, neutral 50/-211.4
- Top slices: feat_ret_5:2:LONG:h19 5n/4w +22.27; feat_ext_vs_ma_20:0:LONG:h24 19n/10w +19.85; feat_ret_20:0:LONG:h24 1n/1w +11.91; feat_atr_norm_ext:2:LONG:h13 3n/2w +6.92; feat_ret_1:0:LONG:h18 1n/1w +5.20
- Worst slices: feat_ext_vs_ma_10:0:LONG:h24 6n/1w -40.73; feat_realized_vol_20:2:LONG:h13 4n/0w -38.28; feat_atr_norm_ext:2:LONG:h15 5n/2w -35.61; feat_trend_strength_20:1:LONG:h19 3n/0w -27.78; feat_ext_vs_ma_20:2:LONG:h13 3n/0w -26.78
- Top pairs: ZECUSDC 3n +39.15; KPEPEUSDC 1n +18.63; JUPUSDC 2n +17.06; LINKUSDC 7n +9.13; MONUSDC 3n +8.57
- Worst pairs: XMRUSDC 4n -32.97; DOGEUSDC 8n -31.31; SUIUSDC 4n -29.10; ASTERUSDC 2n -24.96; XRPUSDC 4n -23.78

### HIP3

- Closed: 31 | wins: 15 | win%: 48.4 | P&L: **-20.70 ZAR** | today: +0.00 | 7d: -5.55 | 30d: -20.70
- By exit: target +15.4, lane_gate +11.5, trail_stop +8.4, horizon -5.0, rotated -5.8, stop -45.2
- By entry regime (n/pnl): neutral 14/-0.9, bear 12/-8.8, bull 5/-11.1
- Top slices: hip3_xyz_equity_c0:feat_realized_vol_20:1:LONG:h24 1n/1w +6.16; hip3_xyz_equity_c0:feat_ext_vs_ma_20:0:LONG:h24 1n/1w +1.62; hip3_xyz_commodity_c0:feat_ext_vs_ma_50:2:LONG:h20 1n/1w +1.52; hip3_xyz_equity_c0:feat_realized_vol_20:2:LONG:h17 3n/1w +0.76; hip3_xyz_equity_c0:feat_vol_regime:0:LONG:h20 1n/1w +0.12
- Worst slices: hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 4n/1w -16.43; hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG:h24 3n/1w -6.37; hip3_xyz_equity_c0:feat_vol_regime:1:LONG:h24 3n/2w -6.04; hip3_xyz_equity_c0:feat_trend_strength_20:0:LONG:h22 1n/0w -0.74; hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24 11n/6w -0.74
- Top pairs: XYZ:EWT 1n +8.48; XYZ:DRAM 1n +6.59; XYZ:EWJ 2n +3.60; XYZ:AAPL 3n +2.71; XYZ:CRWD 1n +1.86
- Worst pairs: XYZ:ASML 2n -9.12; XYZ:CL 1n -8.93; XYZ:BRENTOIL 1n -7.77; XYZ:EBAY 1n -6.10; XYZ:AMAT 1n -3.98

## 4. Open positions & risk

- **NATIVE**: 11 open, stop-risk **85.79 ZAR**
  - ARBUSDC BUY ntl=342 risk=17.66 bars=13 stop=0.1367324999999999930 peak=0.14417
  - INJUSDC BUY ntl=353 risk=17.52 bars=13 stop=5.670149999999999605 peak=5.9661
  - HYPEUSDC BUY ntl=353 risk=10.99 bars=13 stop=76.49774999999999815 peak=78.955
  - KPEPEUSDC BUY ntl=353 risk=9.52 bars=13 stop=0.003256750000000000055 peak=0.003347
  - LTCUSDC BUY ntl=353 risk=7.61 bars=11 stop=52.93850000000000305 peak=54.106
  - SUIUSDC BUY ntl=353 risk=5.72 bars=2 stop=0.71029750000000001525 peak=0.72198
  - BNBUSDC BUY ntl=353 risk=4.98 bars=11 stop=725.1625000000000595 peak=735.54
  - ETHUSDC BUY ntl=353 risk=4.43 bars=11 stop=2498.8500000000000015 peak=2530.6
  - XRPUSDC BUY ntl=353 risk=3.86 bars=2 stop=1.3481250000000000840 peak=1.363
  - DOGEUSDC BUY ntl=353 risk=3.50 bars=2 stop=0.083883749999999989905 peak=0.084723
  - XMRUSDC BUY ntl=355 risk=0.00 bars=25 stop=526.16999999999998150 peak=545.65

- **HIP3**: 6 open, stop-risk **19.53 ZAR**
  - XYZ:AVGO BUY ntl=364 risk=4.92 bars=31 stop=359.37499999999998860 peak=364.3
  - XYZ:EWT BUY ntl=357 risk=4.46 bars=24 stop=109.37749999999999265 peak=110.76
  - XYZ:HYUNDAI BUY ntl=357 risk=4.36 bars=26 stop=283.88000000000002330 peak=287.39
  - XYZ:EBAY BUY ntl=357 risk=4.18 bars=27 stop=105.88750000000000230 peak=107.14
  - XYZ:COST BUY ntl=364 risk=1.61 bars=31 stop=899.50250000000005440 peak=903.5
  - XYZ:STRC BUY ntl=365 risk=0.00 bars=28 stop=98.1800000000000016850 peak=98.385

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **105.32 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 32 | HIP-3: 17
- Native top (by paper P&L):
  - `feat_ret_5:2:LONG:h19` edge=0.0079 n=17246 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+22.27
  - `feat_ext_vs_ma_20:0:LONG:h24` edge=0.0070 n=15301 p=0.0000 src=validated_walk_forward unproven=False paper=19n/+19.85
  - `feat_atr_norm_ext:2:LONG:h13` edge=0.0077 n=15915 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+6.92
  - `feat_ret_1:0:LONG:h18` edge=0.0067 n=16176 p=0.0000 src=validated_walk_forward unproven=False paper=1n/+5.20
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0065 n=17661 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+2.06
  - `feat_ret_10:2:LONG:h15` edge=0.0078 n=17576 p=0.0000 src=validated_walk_forward unproven=False paper=4n/+0.74
  - `feat_ret_20:2:LONG:h10` edge=0.0051 n=17687 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vol_regime:2:LONG:h12` edge=0.0053 n=14691 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
- HIP-3 top (by paper P&L):
  - `hip3_xyz_equity_c0:feat_vol_regime:1:LONG:h24` edge=0.0057 n=8724 p=0.0001 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_atr_norm_ext:1:LONG:h16` edge=0.0011 n=9676 p=0.1282 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_trend_strength_20:0:LONG:h22` edge=0.0015 n=9595 p=0.0308 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_20:1:LONG:h16` edge=0.0008 n=11431 p=0.1760 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_realized_vol_20:0:LONG:h18` edge=0.0008 n=12593 p=0.2498 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_realized_vol_20:1:LONG:h24` edge=0.0017 n=10604 p=0.1017 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ret_20:1:LONG:h19` edge=0.0012 n=11409 p=0.0525 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_10:1:LONG:h20` edge=0.0008 n=12127 p=0.1730 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **31/50** | ghost rows: **288/50** | PnL: **-20.70 ZAR**
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

- Label: **neutral** | breadth bear=0.4211 bull=0.1053 neutral=0.4737 | symbols=19
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 65 / bull 0
- as_of: 2026-09-12T21:55:30Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 0 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=5616 validated=5616 passing=0 eligible=205 best=198.2b best_fail=breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-23.11 | frozen=YES
- HIP-3 lane: **GREEN** | closed=20 pnl=+1.12 | frozen=NO
- Frozen lanes: native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 4
  - `feat_atr_norm_ext:2:LONG:h13` pnl=+6.92
  - `feat_ext_vs_ma_20:0:LONG:h24` pnl=+19.85
  - `feat_ret_10:2:LONG:h15` pnl=+0.74
  - `feat_ret_5:2:LONG:h19` pnl=+22.27
- Tradable slices: native **27/32** | hip3 **16/17**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 16
  - `feat_atr_norm_ext:0:LONG:h24` lane_not_green
  - `feat_atr_norm_ext:2:LONG:h15` lane_not_green
  - `feat_ext_vs_ma_10:0:LONG:h24` lane_not_green
  - `feat_ext_vs_ma_20:2:LONG:h13` lane_not_green
  - `feat_ext_vs_ma_50:0:LONG:h24` lane_not_green
  - `feat_realized_vol_20:2:LONG:h13` lane_not_green
  - `feat_ret_10:0:LONG:h24` lane_not_green
  - `feat_ret_10:2:LONG:h13` lane_not_green
  - `feat_ret_5:0:LONG:h24` lane_not_green
  - `feat_trend_slope_20:0:LONG:h24` lane_not_green
  - `feat_trend_slope_20:2:LONG:h10` lane_not_green
  - `feat_trend_strength_20:1:LONG:h19` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` slice_pnl=-16.43
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24` slice_pnl=-0.74
  - `hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG:h24` slice_pnl=-6.37
  - `hip3_xyz_equity_c0:feat_vol_regime:1:LONG:h24` slice_pnl=-6.04

## 13. Signal activity

- Latest scan 2026-09-12T21:40:37: errors=4 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=6
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 6, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 6, "pair_held": 8, "regime_blocked": 720, "skipped": 9, "slice_full": 0, "slot_full": 134})
- green_gate: native_green=False hip3_green=True frozen=native islands=4 blocks=16
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:BIRD"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:GEV"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:LYTE"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:XBI"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
