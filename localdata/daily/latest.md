# Breakwater daily print — 2026-09-13 09:38 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

> ## COMA ALARM — HIP3

> No **proven** slice in this lane. Auditions can still open entries, so
> this is not a dead lane: it trades, but nothing in it trades on a record
> it earned, so it cannot unfreeze itself. The runner will keep reporting
> operational, which is why this block exists. Attention, not intervention.

## 1. Posture

- Mode: **readonly** | VALR equity: **398.16 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **1732.11 ZAR** (seed 2000) | lifetime: **-267.89 ZAR** | closed: 143
- Today: 12 closed, **-33.05 ZAR**
- 7d: **-263.74 ZAR** | 30d: **-267.89 ZAR**

## 2b. Claimed vs realised

- Book: 49 slices (native 32 | hip3 17); validated pools: native 524 | hip3 464; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 49 book slices present in the validated pools): +0.428% | at 380.42 ZAR mean notional/trade: +1.63 ZAR/trade
- Realised (143 real closes per lane_gate._is_real_close, net of fees): -1.87 ZAR/trade | sd 8.15 | SE 0.68
- Gap: -3.50 ZAR/trade | t = -5.14 (one-sample t of realised mean vs the claimed constant) | verdict: FALLS SHORT
- native: claimed median +0.526% over 32/32 slices (pool 524) ~ +1.99 ZAR | realised 109 closes -2.17 ZAR sd 9.04 SE 0.87 | gap -4.16 t -4.81 | FALLS SHORT
- hip3: claimed median +0.085% over 17/17 slices (pool 464) ~ +0.33 ZAR | realised 34 closes -0.91 ZAR sd 4.11 SE 0.70 | gap -1.24 t -1.76 | NOT ESTABLISHED
- Ledger: 183248 decision rows; 143 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 183105 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 109 | wins: 42 | win%: 38.5 | P&L: **-236.97 ZAR** | today: -22.83 | 7d: -247.97 | 30d: -236.97
- By exit: target +101.5, trail_stop +49.6, lane_gate +7.6, rotated -47.9, horizon -120.1, stop -227.6
- By entry regime (n/pnl): bull 26/+6.3, bear 28/-27.2, neutral 55/-216.1
- Top slices: feat_ret_5:2:LONG:h19 5n/4w +22.27; feat_ext_vs_ma_20:0:LONG:h24 20n/10w +13.82; feat_ret_20:0:LONG:h24 1n/1w +11.91; feat_atr_norm_ext:2:LONG:h13 3n/2w +6.92; feat_ret_1:0:LONG:h18 1n/1w +5.20
- Worst slices: feat_ext_vs_ma_10:0:LONG:h24 6n/1w -40.73; feat_realized_vol_20:2:LONG:h13 4n/0w -38.28; feat_atr_norm_ext:2:LONG:h15 5n/2w -35.61; feat_trend_strength_20:1:LONG:h19 3n/0w -27.78; feat_ext_vs_ma_20:2:LONG:h13 3n/0w -26.78
- Top pairs: ZECUSDC 3n +39.15; KPEPEUSDC 2n +23.14; JUPUSDC 2n +17.06; LINKUSDC 7n +9.13; MONUSDC 3n +8.57
- Worst pairs: SUIUSDC 5n -35.13; XMRUSDC 4n -32.97; DOGEUSDC 9n -32.80; ASTERUSDC 2n -24.96; XRPUSDC 5n -23.99

### HIP3

- Closed: 34 | wins: 15 | win%: 44.1 | P&L: **-30.92 ZAR** | today: -10.22 | 7d: -15.77 | 30d: -30.92
- By exit: target +15.4, lane_gate +11.5, trail_stop +8.1, horizon -5.0, rotated -5.8, stop -55.1
- By entry regime (n/pnl): neutral 15/-5.6, bear 12/-8.8, bull 7/-16.6
- Top slices: hip3_xyz_equity_c0:feat_ext_vs_ma_20:0:LONG:h24 1n/1w +1.62; hip3_xyz_commodity_c0:feat_ext_vs_ma_50:2:LONG:h20 1n/1w +1.52; hip3_xyz_equity_c0:feat_realized_vol_20:2:LONG:h17 3n/1w +0.76; hip3_xyz_equity_c0:feat_vol_regime:0:LONG:h20 1n/1w +0.12; hip3_xyz_equity_c0:feat_ret_1:1:LONG:h24 1n/0w -0.28
- Worst slices: hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 4n/1w -16.43; hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG:h24 3n/1w -6.37; hip3_xyz_equity_c0:feat_vol_regime:1:LONG:h24 3n/2w -6.04; hip3_xyz_equity_c0:feat_realized_vol_20:1:LONG:h24 3n/1w -3.77; hip3_xyz_equity_c0:feat_trend_strength_20:0:LONG:h22 1n/0w -0.74
- Top pairs: XYZ:EWT 1n +8.48; XYZ:DRAM 1n +6.59; XYZ:EWJ 2n +3.60; XYZ:AAPL 3n +2.71; XYZ:CRWD 1n +1.86
- Worst pairs: XYZ:ASML 2n -9.12; XYZ:CL 1n -8.93; XYZ:BRENTOIL 1n -7.77; XYZ:EBAY 1n -6.10; XYZ:AVGO 1n -5.25

## 4. Open positions & risk

- **NATIVE**: 13 open, stop-risk **92.40 ZAR**
  - ARBUSDC BUY ntl=347 risk=14.70 bars=1 stop=0.13294499999999999205 peak=0.13883
  - LITUSDC BUY ntl=347 risk=13.72 bars=1 stop=3.947674999999999980 peak=4.1103
  - NEARUSDC BUY ntl=347 risk=11.05 bars=1 stop=2.2261500000000000720 peak=2.2994
  - TAOUSDC BUY ntl=347 risk=8.45 bars=1 stop=230.16499999999999520 peak=235.91
  - FARTCOINUSDC BUY ntl=347 risk=8.38 bars=1 stop=0.13803999999999998685 peak=0.14146
  - ASTERUSDC BUY ntl=353 risk=7.49 bars=11 stop=0.6719625000000000010 peak=0.68652
  - HYPEUSDC BUY ntl=347 risk=6.66 bars=1 stop=76.92624999999999375 peak=78.432
  - LTCUSDC BUY ntl=347 risk=6.02 bars=1 stop=53.15024999999999935 peak=54.089
  - LINKUSDC BUY ntl=347 risk=5.20 bars=1 stop=11.254749999999999435 peak=11.426
  - DOGEUSDC BUY ntl=347 risk=4.13 bars=1 stop=0.08315825000000000075 peak=0.08416
  - ETHUSDC BUY ntl=346 risk=3.58 bars=0 stop=2468.62499999999990825 peak=2494.4
  - BNBUSDC BUY ntl=347 risk=3.04 bars=1 stop=715.4824999999999855 peak=721.81
  - XMRUSDC BUY ntl=355 risk=0.00 bars=37 stop=526.16999999999998150 peak=545.65

- **HIP3**: 3 open, stop-risk **10.24 ZAR**
  - XYZ:EWT BUY ntl=357 risk=4.46 bars=39 stop=109.37749999999999265 peak=110.76
  - XYZ:EBAY BUY ntl=357 risk=4.18 bars=39 stop=105.88750000000000230 peak=107.14
  - XYZ:COST BUY ntl=364 risk=1.61 bars=43 stop=899.50250000000005440 peak=903.5

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **102.65 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 32 | HIP-3: 17
- Native top (by paper P&L):
  - `feat_ret_5:2:LONG:h19` edge=0.0079 n=17246 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+22.27
  - `feat_ext_vs_ma_20:0:LONG:h24` edge=0.0070 n=15301 p=0.0000 src=validated_walk_forward unproven=False paper=20n/+13.82
  - `feat_atr_norm_ext:2:LONG:h13` edge=0.0077 n=15915 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+6.92
  - `feat_ret_1:0:LONG:h18` edge=0.0067 n=16176 p=0.0000 src=validated_walk_forward unproven=False paper=1n/+5.20
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0065 n=17661 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+2.06
  - `feat_ret_10:2:LONG:h15` edge=0.0078 n=17576 p=0.0000 src=validated_walk_forward unproven=False paper=4n/+0.74
  - `feat_vol_regime:2:LONG:h12` edge=0.0053 n=14691 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_realized_vol_20:0:LONG:h14` edge=0.0018 n=8058 p=0.2259 src=validated_walk_forward unproven=False paper=0n/+0.00
- HIP-3 top (by paper P&L):
  - `hip3_xyz_equity_c0:feat_vol_regime:0:LONG:h20` edge=0.0015 n=8720 p=0.0082 src=validated_walk_forward unproven=False paper=1n/+0.12
  - `hip3_xyz_equity_c0:feat_atr_norm_ext:1:LONG:h16` edge=0.0011 n=9676 p=0.1282 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_20:1:LONG:h16` edge=0.0008 n=11431 p=0.1760 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_realized_vol_20:0:LONG:h18` edge=0.0008 n=12593 p=0.2498 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ret_20:1:LONG:h19` edge=0.0012 n=11409 p=0.0525 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_10:1:LONG:h20` edge=0.0008 n=12127 p=0.1730 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ret_5:1:LONG:h24` edge=0.0009 n=12246 p=0.1747 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ret_3:0:LONG:h22` edge=0.0007 n=9677 p=0.2191 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **34/50** | ghost rows: **517/50** | PnL: **-30.92 ZAR**
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

- Label: **bear** | breadth bear=0.7667 bull=0.0333 neutral=0.2 | symbols=30
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 84 / bull 0
- as_of: 2026-09-13T09:30:24Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 0 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=5616 validated=5616 passing=0 eligible=205 best=198.2b best_fail=breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-58.30 | frozen=YES
- HIP-3 lane: **RED** | closed=20 pnl=-19.24 | frozen=YES
- Frozen lanes: hip3, native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 5
  - `feat_atr_norm_ext:2:LONG:h13` pnl=+6.92
  - `feat_ext_vs_ma_20:0:LONG:h24` pnl=+13.82
  - `feat_ret_10:2:LONG:h15` pnl=+0.74
  - `feat_ret_5:2:LONG:h19` pnl=+22.27
  - `hip3_xyz_equity_c0:feat_realized_vol_20:2:LONG:h17` pnl=+0.76
- Tradable slices: native **26/32** | hip3 **15/17**
- **COMA LANES: hip3** — frozen with no tradable slice on an earned green record; auditions may still open.
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 18
  - `feat_atr_norm_ext:0:LONG:h24` lane_not_green
  - `feat_atr_norm_ext:2:LONG:h15` lane_not_green
  - `feat_ext_vs_ma_10:0:LONG:h24` lane_not_green
  - `feat_ext_vs_ma_20:2:LONG:h13` lane_not_green
  - `feat_ext_vs_ma_50:0:LONG:h24` lane_not_green
  - `feat_realized_vol_20:2:LONG:h13` lane_not_green
  - `feat_ret_10:0:LONG:h24` lane_not_green
  - `feat_ret_10:2:LONG:h13` lane_not_green
  - `feat_ret_3:2:LONG:h19` lane_not_green
  - `feat_ret_5:0:LONG:h24` lane_not_green
  - `feat_trend_slope_20:0:LONG:h24` lane_not_green
  - `feat_trend_slope_20:2:LONG:h10` lane_not_green
  - `feat_trend_strength_20:1:LONG:h19` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24` lane_not_green
  - `hip3_xyz_equity_c0:feat_realized_vol_20:1:LONG:h24` lane_not_green
  - `hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG:h24` lane_not_green
  - `hip3_xyz_equity_c0:feat_vol_regime:1:LONG:h24` lane_not_green

## 13. Signal activity

- Latest scan 2026-09-13T09:38:12: errors=2 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=8
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 12, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 8, "pair_held": 19, "regime_blocked": 589, "skipped": 16, "slice_full": 0, "slot_full": 101})
- green_gate: native_green=False hip3_green=False frozen=hip3,native islands=5 blocks=18
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:RDDT"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:ZM"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
