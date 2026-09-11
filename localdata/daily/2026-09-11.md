# Breakwater daily print — 2026-09-11 15:40 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **398.16 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **1827.06 ZAR** (seed 2000) | lifetime: **-172.94 ZAR** | closed: 113
- Today: 14 closed, **-2.01 ZAR**
- 7d: **-132.84 ZAR** | 30d: **-172.94 ZAR**

## 2b. Claimed vs realised

- Book: 47 slices (native 30 | hip3 17); validated pools: native 524 | hip3 464; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 47 book slices present in the validated pools): +0.428% | at 387.73 ZAR mean notional/trade: +1.66 ZAR/trade
- Realised (113 real closes per lane_gate._is_real_close, net of fees): -1.53 ZAR/trade | sd 8.44 | SE 0.79
- Gap: -3.19 ZAR/trade | t = -4.02 (one-sample t of realised mean vs the claimed constant) | verdict: FALLS SHORT
- native: claimed median +0.526% over 30/30 slices (pool 524) ~ +2.04 ZAR | realised 82 closes -1.86 ZAR sd 9.57 SE 1.06 | gap -3.89 t -3.68 | FALLS SHORT
- hip3: claimed median +0.085% over 17/17 slices (pool 464) ~ +0.33 ZAR | realised 31 closes -0.67 ZAR sd 4.17 SE 0.75 | gap -1.00 t -1.33 | NOT ESTABLISHED
- Ledger: 128224 decision rows; 113 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 128111 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 82 | wins: 31 | win%: 37.8 | P&L: **-152.24 ZAR** | today: -8.30 | 7d: -128.13 | 30d: -152.24
- By exit: target +101.5, trail_stop +21.6, lane_gate +7.6, rotated -36.0, horizon -97.2, stop -149.7
- By entry regime (n/pnl): bull 23/+24.7, bear 17/-22.8, neutral 42/-154.2
- Top slices: feat_ret_5:2:LONG:h19 2n/2w +26.67; feat_ext_vs_ma_20:0:LONG:h24 18n/9w +17.36; feat_ret_20:0:LONG:h24 1n/1w +11.91; feat_atr_norm_ext:2:LONG:h13 2n/2w +8.82; feat_ret_1:0:LONG:h18 1n/1w +5.20
- Worst slices: feat_ext_vs_ma_10:0:LONG:h24 6n/1w -40.73; feat_realized_vol_20:2:LONG:h13 4n/0w -38.28; feat_trend_strength_20:1:LONG:h19 3n/0w -27.78; feat_atr_norm_ext:0:LONG:h24 2n/0w -23.34; feat_ext_vs_ma_50:0:LONG:h24 4n/2w -22.58
- Top pairs: ZECUSDC 3n +39.15; KPEPEUSDC 1n +18.63; MONUSDC 3n +8.57; JUPUSDC 1n +8.54; CRVUSDC 2n +7.07
- Worst pairs: DOGEUSDC 7n -33.80; XMRUSDC 4n -32.97; SUIUSDC 3n -30.55; ASTERUSDC 2n -24.96; HYPEUSDC 6n -21.38

### HIP3

- Closed: 31 | wins: 15 | win%: 48.4 | P&L: **-20.70 ZAR** | today: +6.28 | 7d: -4.71 | 30d: -20.70
- By exit: target +15.4, lane_gate +11.5, trail_stop +8.4, horizon -5.0, rotated -5.8, stop -45.2
- By entry regime (n/pnl): neutral 14/-0.9, bear 12/-8.8, bull 5/-11.1
- Top slices: hip3_xyz_equity_c0:feat_realized_vol_20:1:LONG:h24 1n/1w +6.16; hip3_xyz_equity_c0:feat_ext_vs_ma_20:0:LONG:h24 1n/1w +1.62; hip3_xyz_commodity_c0:feat_ext_vs_ma_50:2:LONG:h20 1n/1w +1.52; hip3_xyz_equity_c0:feat_realized_vol_20:2:LONG:h17 3n/1w +0.76; hip3_xyz_equity_c0:feat_vol_regime:0:LONG:h20 1n/1w +0.12
- Worst slices: hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 4n/1w -16.43; hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG:h24 3n/1w -6.37; hip3_xyz_equity_c0:feat_vol_regime:1:LONG:h24 3n/2w -6.04; hip3_xyz_equity_c0:feat_trend_strength_20:0:LONG:h22 1n/0w -0.74; hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24 11n/6w -0.74
- Top pairs: XYZ:EWT 1n +8.48; XYZ:DRAM 1n +6.59; XYZ:EWJ 2n +3.60; XYZ:AAPL 3n +2.71; XYZ:CRWD 1n +1.86
- Worst pairs: XYZ:ASML 2n -9.12; XYZ:CL 1n -8.93; XYZ:BRENTOIL 1n -7.77; XYZ:EBAY 1n -6.10; XYZ:AMAT 1n -3.98

## 4. Open positions & risk

- **NATIVE**: 13 open, stop-risk **105.72 ZAR**
  - INJUSDC BUY ntl=356 risk=18.21 bars=1 stop=5.806575000000000320 peak=6.1192
  - CRVUSDC BUY ntl=350 risk=18.21 bars=1 stop=0.33908499999999995275 peak=0.35767
  - XPLUSDC BUY ntl=356 risk=15.33 bars=7 stop=0.08227924999999999890 peak=0.085985
  - XRPUSDC BUY ntl=364 risk=14.52 bars=1 stop=1.3615750000000000070 peak=1.4181
  - SOLUSDC BUY ntl=364 risk=13.34 bars=1 stop=101.20174999999999265 peak=105.05
  - BNBUSDC BUY ntl=364 risk=9.10 bars=1 stop=718.34250000000003075 peak=736.75
  - BTCUSDC BUY ntl=364 risk=8.86 bars=1 stop=77411.25000000000015 peak=79342.0
  - LTCUSDC BUY ntl=356 risk=8.15 bars=7 stop=51.91174999999999710 peak=53.13
  - LINKUSDC BUY ntl=366 risk=0.00 bars=19 stop=11.6887500000000000850 peak=12.092
  - JUPUSDC BUY ntl=302 risk=0.00 bars=7 stop=0.24041750000000000700 peak=0.25419
  - HYPEUSDC BUY ntl=356 risk=0.00 bars=7 stop=80.806750000000003600 peak=83.463
  - UNIUSDC BUY ntl=356 risk=0.00 bars=7 stop=6.2142749999999992900 peak=6.4936
  - SUIUSDC BUY ntl=356 risk=0.00 bars=7 stop=0.74065499999999997150 peak=0.76072

- **HIP3**: 3 open, stop-risk **7.30 ZAR**
  - XYZ:AVGO BUY ntl=364 risk=4.92 bars=1 stop=359.37499999999998860 peak=364.3
  - XYZ:COST BUY ntl=364 risk=1.61 bars=1 stop=899.50250000000005440 peak=903.5
  - XYZ:STRC BUY ntl=365 risk=0.76 bars=0 stop=97.963000000000001685 peak=98.168

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **113.02 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 30 | HIP-3: 17
- Native top (by paper P&L):
  - `feat_ret_5:2:LONG:h19` edge=0.0079 n=17246 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+26.67
  - `feat_ext_vs_ma_20:0:LONG:h24` edge=0.0070 n=15301 p=0.0000 src=validated_walk_forward unproven=False paper=18n/+17.36
  - `feat_atr_norm_ext:2:LONG:h13` edge=0.0077 n=15915 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+8.82
  - `feat_ret_1:0:LONG:h18` edge=0.0067 n=16176 p=0.0000 src=validated_walk_forward unproven=False paper=1n/+5.20
  - `feat_atr_norm_ext:2:LONG:h15` edge=0.0085 n=15663 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_20:2:LONG:h13` edge=0.0070 n=17286 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0065 n=17661 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_20:2:LONG:h10` edge=0.0051 n=17687 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Label: **neutral** | breadth bear=0.1333 bull=0.1 neutral=0.7667 | symbols=30
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **False** | flipped_from: neutral | consecutive_bear: 35 / bull 0
- as_of: 2026-09-11T15:30:23Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 0 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=5616 validated=5616 passing=0 eligible=205 best=198.2b best_fail=breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-71.03 | frozen=YES
- HIP-3 lane: **GREEN** | closed=20 pnl=+1.12 | frozen=NO
- Frozen lanes: native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 1
  - `feat_ext_vs_ma_20:0:LONG:h24` pnl=+17.36
- Tradable slices: native **27/30** | hip3 **16/17**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 14
  - `feat_ext_vs_ma_10:0:LONG:h24` lane_not_green
  - `feat_ext_vs_ma_50:0:LONG:h24` lane_not_green
  - `feat_realized_vol_20:2:LONG:h13` lane_not_green
  - `feat_ret_10:0:LONG:h24` lane_not_green
  - `feat_ret_10:2:LONG:h13` lane_not_green
  - `feat_ret_10:2:LONG:h15` lane_not_green
  - `feat_ret_5:0:LONG:h24` lane_not_green
  - `feat_trend_slope_20:0:LONG:h24` lane_not_green
  - `feat_trend_slope_20:2:LONG:h10` lane_not_green
  - `feat_trend_strength_20:1:LONG:h19` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` slice_pnl=-16.43
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24` slice_pnl=-0.74
  - `hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG:h24` slice_pnl=-6.37
  - `hip3_xyz_equity_c0:feat_vol_regime:1:LONG:h24` slice_pnl=-6.04

## 13. Signal activity

- Latest scan 2026-09-11T15:40:29: errors=0 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=4
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 12, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 4, "pair_held": 38, "regime_blocked": 222, "skipped": 322, "slice_full": 0, "slot_full": 139})
- green_gate: native_green=False hip3_green=True frozen=native islands=1 blocks=14
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
