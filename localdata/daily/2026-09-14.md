# Breakwater daily print — 2026-09-14 06:39 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

> ## COMA ALARM — HIP3

> No **proven** slice in this lane. Auditions can still open entries, so
> this is not a dead lane: it trades, but nothing in it trades on a record
> it earned, so it cannot unfreeze itself. The runner will keep reporting
> operational, which is why this block exists. Attention, not intervention.

## 1. Posture

- Mode: **readonly** | VALR equity: **401.18 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **1732.06 ZAR** (seed 2000) | lifetime: **-267.94 ZAR** | closed: 163
- Today: 14 closed, **-3.10 ZAR**
- 7d: **-282.20 ZAR** | 30d: **-267.94 ZAR**

## 2b. Claimed vs realised

- Book: 48 slices (native 31 | hip3 17); validated pools: native 524 | hip3 464; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 48 book slices present in the validated pools): +0.421% | at 376.48 ZAR mean notional/trade: +1.58 ZAR/trade
- Realised (163 real closes per lane_gate._is_real_close, net of fees): -1.64 ZAR/trade | sd 8.32 | SE 0.65
- Gap: -3.23 ZAR/trade | t = -4.95 (one-sample t of realised mean vs the claimed constant) | verdict: FALLS SHORT
- native: claimed median +0.525% over 31/31 slices (pool 524) ~ +1.96 ZAR | realised 127 closes -1.79 ZAR sd 9.18 SE 0.81 | gap -3.76 t -4.61 | FALLS SHORT
- hip3: claimed median +0.085% over 17/17 slices (pool 464) ~ +0.33 ZAR | realised 36 closes -1.12 ZAR sd 4.08 SE 0.68 | gap -1.44 t -2.12 | FALLS SHORT
- Ledger: 204842 decision rows; 163 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 204679 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 127 | wins: 50 | win%: 39.4 | P&L: **-227.74 ZAR** | today: +6.18 | 7d: -257.16 | 30d: -227.74
- By exit: target +134.8, trail_stop +53.3, lane_gate +7.6, rotated -47.9, horizon -103.2, stop -272.3
- By entry regime (n/pnl): bull 26/+6.3, bear 41/-20.8, neutral 60/-213.2
- Top slices: feat_ext_vs_ma_10:2:LONG:h15 4n/1w +21.09; feat_ret_5:2:LONG:h19 7n/4w +14.88; feat_ret_20:0:LONG:h24 1n/1w +11.91; feat_atr_norm_ext:2:LONG:h13 3n/2w +6.92; feat_ret_1:0:LONG:h18 1n/1w +5.20
- Worst slices: feat_ext_vs_ma_10:0:LONG:h24 6n/1w -40.73; feat_realized_vol_20:2:LONG:h13 4n/0w -38.28; feat_atr_norm_ext:2:LONG:h15 5n/2w -35.61; feat_trend_strength_20:1:LONG:h19 3n/0w -27.78; feat_ext_vs_ma_20:2:LONG:h13 3n/0w -26.78
- Top pairs: LITUSDC 2n +41.67; ZECUSDC 3n +39.15; KPEPEUSDC 2n +23.14; JUPUSDC 2n +17.06; MONUSDC 3n +8.57
- Worst pairs: SUIUSDC 6n -44.55; DOGEUSDC 10n -37.24; XMRUSDC 5n -29.08; ARBUSDC 2n -24.87; SOLUSDC 9n -24.69

### HIP3

- Closed: 36 | wins: 15 | win%: 41.7 | P&L: **-40.19 ZAR** | today: -9.28 | 7d: -25.04 | 30d: -40.19
- By exit: target +15.4, lane_gate +11.5, trail_stop +8.1, horizon -5.0, rotated -5.8, stop -64.4
- By entry regime (n/pnl): bear 12/-8.8, neutral 16/-10.3, bull 8/-21.1
- Top slices: hip3_xyz_equity_c0:feat_ext_vs_ma_20:0:LONG:h24 1n/1w +1.62; hip3_xyz_commodity_c0:feat_ext_vs_ma_50:2:LONG:h20 1n/1w +1.52; hip3_xyz_equity_c0:feat_realized_vol_20:2:LONG:h17 3n/1w +0.76; hip3_xyz_equity_c0:feat_ret_1:1:LONG:h24 1n/0w -0.28; hip3_xyz_commodity_c0:feat_trend_slope_20:0:LONG:h20 2n/0w -0.56
- Worst slices: hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 4n/1w -16.43; hip3_xyz_equity_c0:feat_realized_vol_20:1:LONG:h24 4n/1w -8.55; hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG:h24 3n/1w -6.37; hip3_xyz_equity_c0:feat_vol_regime:1:LONG:h24 3n/2w -6.04; hip3_xyz_equity_c0:feat_vol_regime:0:LONG:h20 2n/1w -4.38
- Top pairs: XYZ:DRAM 1n +6.59; XYZ:EWT 2n +3.70; XYZ:EWJ 2n +3.60; XYZ:AAPL 3n +2.71; XYZ:CRWD 1n +1.86
- Worst pairs: XYZ:EBAY 2n -10.60; XYZ:ASML 2n -9.12; XYZ:CL 1n -8.93; XYZ:BRENTOIL 1n -7.77; XYZ:AVGO 1n -5.25

## 4. Open positions & risk

- **NATIVE**: 2 open, stop-risk **6.92 ZAR**
  - XRPUSDC BUY ntl=347 risk=6.92 bars=10 stop=1.3274000000000000290 peak=1.3544
  - BTCUSDC BUY ntl=346 risk=0.00 bars=16 stop=77006.7500000000000200 peak=77657.0

- **HIP3**: 1 open, stop-risk **0.00 ZAR**
  - XYZ:COST BUY ntl=364 risk=0.00 bars=63 stop=904.932500000000054400 peak=908.93

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **6.92 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 31 | HIP-3: 17
- Native top (by paper P&L):
  - `feat_ext_vs_ma_10:2:LONG:h15` edge=0.0067 n=17389 p=0.0000 src=validated_walk_forward unproven=False paper=4n/+21.09
  - `feat_ret_5:2:LONG:h19` edge=0.0079 n=17246 p=0.0000 src=validated_walk_forward unproven=False paper=7n/+14.88
  - `feat_atr_norm_ext:2:LONG:h13` edge=0.0077 n=15915 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+6.92
  - `feat_ret_1:0:LONG:h18` edge=0.0067 n=16176 p=0.0000 src=validated_walk_forward unproven=False paper=1n/+5.20
  - `feat_ret_5:0:LONG:h16` edge=0.0049 n=15411 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+3.41
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0065 n=17661 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+2.06
  - `feat_ret_3:0:LONG:h14` edge=0.0049 n=15653 p=0.0000 src=validated_walk_forward unproven=False paper=1n/+1.65
  - `feat_ret_10:2:LONG:h15` edge=0.0078 n=17576 p=0.0000 src=validated_walk_forward unproven=False paper=4n/+0.74
- HIP-3 top (by paper P&L):
  - `hip3_xyz_equity_c0:feat_atr_norm_ext:1:LONG:h16` edge=0.0011 n=9676 p=0.1282 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_20:1:LONG:h16` edge=0.0008 n=11431 p=0.1760 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_realized_vol_20:0:LONG:h18` edge=0.0008 n=12593 p=0.2498 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ret_20:1:LONG:h19` edge=0.0012 n=11409 p=0.0525 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_10:1:LONG:h20` edge=0.0008 n=12127 p=0.1730 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ret_5:1:LONG:h24` edge=0.0009 n=12246 p=0.1747 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ret_3:0:LONG:h22` edge=0.0007 n=9677 p=0.2191 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ret_5:0:LONG:h23` edge=0.0008 n=9717 p=0.1758 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **36/50** | ghost rows: **694/50** | PnL: **-40.19 ZAR**
- Gate verdict: **NOT READY**

## 8. Research / honesty checks

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

- Label: **neutral** | breadth bear=0.4333 bull=0.0667 neutral=0.5 | symbols=30
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **False** | flipped_from: neutral | consecutive_bear: 116 / bull 0
- as_of: 2026-09-14T06:30:27Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 0 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=5616 validated=5616 passing=0 eligible=205 best=198.2b best_fail=breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+7.71 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-25.26 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 1
  - `hip3_xyz_equity_c0:feat_realized_vol_20:2:LONG:h17` pnl=+0.76
- Tradable slices: native **24/31** | hip3 **15/17**
- **COMA LANES: hip3** — frozen with no tradable slice on an earned green record; auditions may still open.
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 20
  - `feat_atr_norm_ext:0:LONG:h24` slice_pnl=-21.09
  - `feat_atr_norm_ext:2:LONG:h15` slice_pnl=-35.61
  - `feat_ext_vs_ma_10:0:LONG:h24` slice_pnl=-40.73
  - `feat_ext_vs_ma_20:0:LONG:h24` slice_pnl=-5.64
  - `feat_ext_vs_ma_20:2:LONG:h13` slice_pnl=-26.78
  - `feat_ext_vs_ma_50:0:LONG:h24` slice_pnl=-22.58
  - `feat_realized_vol_20:2:LONG:h13` slice_pnl=-38.28
  - `feat_ret_10:0:LONG:h24` slice_pnl=-9.44
  - `feat_ret_10:2:LONG:h13` slice_pnl=-1.97
  - `feat_ret_3:2:LONG:h19` slice_pnl=-21.89
  - `feat_ret_5:0:LONG:h24` slice_pnl=-20.67
  - `feat_trend_slope_20:0:LONG:h24` slice_pnl=-7.33
  - `feat_trend_slope_20:2:LONG:h10` slice_pnl=-0.21
  - `feat_trend_strength_20:1:LONG:h19` slice_pnl=-27.78
  - `feat_trend_strength_20:2:LONG:h12` slice_pnl=-2.65
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24` lane_not_green
  - `hip3_xyz_equity_c0:feat_realized_vol_20:1:LONG:h24` lane_not_green
  - `hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG:h24` lane_not_green
  - `hip3_xyz_equity_c0:feat_vol_regime:1:LONG:h24` lane_not_green

## 13. Signal activity

- Latest scan 2026-09-14T06:39:26: errors=3 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=9
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=1 blocks=20
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:COST"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:EBAY"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:GEV"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
