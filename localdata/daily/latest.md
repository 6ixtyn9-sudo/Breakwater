# Breakwater daily print — 2026-09-11 19:40 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **395.97 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **1785.78 ZAR** (seed 2000) | lifetime: **-214.22 ZAR** | closed: 121
- Today: 22 closed, **-43.29 ZAR**
- 7d: **-174.12 ZAR** | 30d: **-214.22 ZAR**

## 2b. Claimed vs realised

- Book: 45 slices (native 28 | hip3 17); validated pools: native 524 | hip3 464; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 45 book slices present in the validated pools): +0.413% | at 385.86 ZAR mean notional/trade: +1.59 ZAR/trade
- Realised (121 real closes per lane_gate._is_real_close, net of fees): -1.77 ZAR/trade | sd 8.55 | SE 0.78
- Gap: -3.36 ZAR/trade | t = -4.33 (one-sample t of realised mean vs the claimed constant) | verdict: FALLS SHORT
- native: claimed median +0.517% over 28/28 slices (pool 524) ~ +1.99 ZAR | realised 90 closes -2.15 ZAR sd 9.60 SE 1.01 | gap -4.14 t -4.09 | FALLS SHORT
- hip3: claimed median +0.085% over 17/17 slices (pool 464) ~ +0.33 ZAR | realised 31 closes -0.67 ZAR sd 4.17 SE 0.75 | gap -1.00 t -1.33 | NOT ESTABLISHED
- Ledger: 133066 decision rows; 121 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 132945 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 90 | wins: 35 | win%: 38.9 | P&L: **-193.52 ZAR** | today: -49.58 | 7d: -169.41 | 30d: -193.52
- By exit: target +101.5, trail_stop +36.6, lane_gate +7.6, rotated -36.0, horizon -97.2, stop -206.0
- By entry regime (n/pnl): bull 23/+24.7, bear 21/-7.9, neutral 46/-210.4
- Top slices: feat_ret_5:2:LONG:h19 4n/4w +37.91; feat_ext_vs_ma_20:0:LONG:h24 18n/9w +17.36; feat_ret_20:0:LONG:h24 1n/1w +11.91; feat_atr_norm_ext:2:LONG:h13 2n/2w +8.82; feat_ret_1:0:LONG:h18 1n/1w +5.20
- Worst slices: feat_ext_vs_ma_10:0:LONG:h24 6n/1w -40.73; feat_realized_vol_20:2:LONG:h13 4n/0w -38.28; feat_atr_norm_ext:2:LONG:h15 2n/0w -32.19; feat_trend_strength_20:1:LONG:h19 3n/0w -27.78; feat_ext_vs_ma_20:2:LONG:h13 2n/0w -24.03
- Top pairs: ZECUSDC 3n +39.15; KPEPEUSDC 1n +18.63; LINKUSDC 7n +9.13; MONUSDC 3n +8.57; JUPUSDC 1n +8.54
- Worst pairs: DOGEUSDC 7n -33.80; XMRUSDC 4n -32.97; SUIUSDC 4n -29.10; ASTERUSDC 2n -24.96; XRPUSDC 4n -23.78

### HIP3

- Closed: 31 | wins: 15 | win%: 48.4 | P&L: **-20.70 ZAR** | today: +6.28 | 7d: -4.71 | 30d: -20.70
- By exit: target +15.4, lane_gate +11.5, trail_stop +8.4, horizon -5.0, rotated -5.8, stop -45.2
- By entry regime (n/pnl): neutral 14/-0.9, bear 12/-8.8, bull 5/-11.1
- Top slices: hip3_xyz_equity_c0:feat_realized_vol_20:1:LONG:h24 1n/1w +6.16; hip3_xyz_equity_c0:feat_ext_vs_ma_20:0:LONG:h24 1n/1w +1.62; hip3_xyz_commodity_c0:feat_ext_vs_ma_50:2:LONG:h20 1n/1w +1.52; hip3_xyz_equity_c0:feat_realized_vol_20:2:LONG:h17 3n/1w +0.76; hip3_xyz_equity_c0:feat_vol_regime:0:LONG:h20 1n/1w +0.12
- Worst slices: hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 4n/1w -16.43; hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG:h24 3n/1w -6.37; hip3_xyz_equity_c0:feat_vol_regime:1:LONG:h24 3n/2w -6.04; hip3_xyz_equity_c0:feat_trend_strength_20:0:LONG:h22 1n/0w -0.74; hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24 11n/6w -0.74
- Top pairs: XYZ:EWT 1n +8.48; XYZ:DRAM 1n +6.59; XYZ:EWJ 2n +3.60; XYZ:AAPL 3n +2.71; XYZ:CRWD 1n +1.86
- Worst pairs: XYZ:ASML 2n -9.12; XYZ:CL 1n -8.93; XYZ:BRENTOIL 1n -7.77; XYZ:EBAY 1n -6.10; XYZ:AMAT 1n -3.98

## 4. Open positions & risk

- **NATIVE**: 7 open, stop-risk **81.25 ZAR**
  - INJUSDC BUY ntl=356 risk=18.21 bars=5 stop=5.806575000000000320 peak=6.1192
  - DOGEUSDC BUY ntl=339 risk=17.86 bars=0 stop=0.07961000000000000190 peak=0.084031
  - XPLUSDC BUY ntl=356 risk=15.33 bars=11 stop=0.08227924999999999890 peak=0.085985
  - BTCUSDC BUY ntl=357 risk=12.60 bars=0 stop=74299.99999999999990 peak=77018.0
  - BNBUSDC BUY ntl=364 risk=9.10 bars=5 stop=718.34250000000003075 peak=736.75
  - LTCUSDC BUY ntl=356 risk=8.15 bars=11 stop=51.91174999999999710 peak=53.13
  - JUPUSDC BUY ntl=302 risk=0.00 bars=11 stop=0.24041750000000000700 peak=0.25419

- **HIP3**: 6 open, stop-risk **20.29 ZAR**
  - XYZ:AVGO BUY ntl=364 risk=4.92 bars=5 stop=359.37499999999998860 peak=364.3
  - XYZ:EWT BUY ntl=357 risk=4.46 bars=1 stop=109.37749999999999265 peak=110.76
  - XYZ:HYUNDAI BUY ntl=357 risk=4.36 bars=0 stop=283.88000000000002330 peak=287.39
  - XYZ:EBAY BUY ntl=357 risk=4.18 bars=1 stop=105.88750000000000230 peak=107.14
  - XYZ:COST BUY ntl=364 risk=1.61 bars=5 stop=899.50250000000005440 peak=903.5
  - XYZ:STRC BUY ntl=365 risk=0.76 bars=4 stop=97.963000000000001685 peak=98.168

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **101.55 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 28 | HIP-3: 17
- Native top (by paper P&L):
  - `feat_ret_5:2:LONG:h19` edge=0.0079 n=17246 p=0.0000 src=validated_walk_forward unproven=False paper=4n/+37.91
  - `feat_ext_vs_ma_20:0:LONG:h24` edge=0.0070 n=15301 p=0.0000 src=validated_walk_forward unproven=False paper=18n/+17.36
  - `feat_atr_norm_ext:2:LONG:h13` edge=0.0077 n=15915 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+8.82
  - `feat_ret_1:0:LONG:h18` edge=0.0067 n=16176 p=0.0000 src=validated_walk_forward unproven=False paper=1n/+5.20
  - `feat_ret_10:2:LONG:h15` edge=0.0078 n=17576 p=0.0000 src=validated_walk_forward unproven=False paper=4n/+0.74
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0065 n=17661 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_20:2:LONG:h10` edge=0.0051 n=17687 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vol_regime:2:LONG:h12` edge=0.0053 n=14691 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
- HIP-3 top (by paper P&L):
  - `hip3_xyz_equity_c0:feat_realized_vol_20:1:LONG:h24` edge=0.0017 n=10604 p=0.1017 src=validated_walk_forward unproven=False paper=1n/+6.16
  - `hip3_xyz_equity_c0:feat_vol_regime:0:LONG:h20` edge=0.0015 n=8720 p=0.0082 src=validated_walk_forward unproven=False paper=1n/+0.12
  - `hip3_xyz_equity_c0:feat_atr_norm_ext:1:LONG:h16` edge=0.0011 n=9676 p=0.1282 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_20:1:LONG:h16` edge=0.0008 n=11431 p=0.1760 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_realized_vol_20:0:LONG:h18` edge=0.0008 n=12593 p=0.2498 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ret_20:1:LONG:h19` edge=0.0012 n=11409 p=0.0525 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_10:1:LONG:h20` edge=0.0008 n=12127 p=0.1730 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ret_5:1:LONG:h24` edge=0.0009 n=12246 p=0.1747 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **31/50** | ghost rows: **165/50** | PnL: **-20.70 ZAR**
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

- Label: **bear** | breadth bear=0.6333 bull=0.0333 neutral=0.3333 | symbols=30
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 38 / bull 0
- as_of: 2026-09-11T19:30:41Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 0 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=5616 validated=5616 passing=0 eligible=205 best=198.2b best_fail=breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-49.58 | frozen=YES
- HIP-3 lane: **GREEN** | closed=20 pnl=+1.12 | frozen=NO
- Frozen lanes: native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 3
  - `feat_ext_vs_ma_20:0:LONG:h24` pnl=+17.36
  - `feat_ret_10:2:LONG:h15` pnl=+0.74
  - `feat_ret_5:2:LONG:h19` pnl=+37.91
- Tradable slices: native **25/28** | hip3 **16/17**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 14
  - `feat_atr_norm_ext:0:LONG:h24` lane_not_green
  - `feat_ext_vs_ma_10:0:LONG:h24` lane_not_green
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

- Latest scan 2026-09-11T19:40:21: errors=3 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=4
- **NO ACTION:** dominant blocker = `slot_full` (funnel={"aggregate_risk_cap_skips": 2, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 4, "pair_held": 34, "regime_blocked": 236, "skipped": 126, "slice_full": 0, "slot_full": 314})
- green_gate: native_green=False hip3_green=True frozen=native islands=3 blocks=14
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:ASML"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:NCLD"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:RIVN"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
