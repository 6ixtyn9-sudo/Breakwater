# Breakwater daily print — 2026-09-16 16:57 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **379.17 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **1965.54 ZAR** (seed 2000) | lifetime: **-34.46 ZAR** | closed: 73
- Today: 34 closed, **-22.87 ZAR**
- 7d: **-34.46 ZAR** | 30d: **-34.46 ZAR**

## 2b. Claimed vs realised

- Book: 31 slices (native 13 | hip3 18); validated pools: native 14 | hip3 160; book slices absent from pools: 16
  - absent: `feat_trend_slope_20:2:LONG:h12` (native)
  - absent: `feat_ext_vs_ma_20:2:LONG:h15` (native)
  - absent: `feat_ext_vs_ma_50:2:LONG:h15` (native)
  - absent: `feat_ret_20:2:LONG:h14` (native)
  - absent: `feat_realized_vol_20:2:LONG:h14` (native)
  - absent: `feat_ext_strength:2:LONG:h15` (native)
  - absent: `feat_ret_10:2:LONG:h19` (native)
  - absent: `feat_trend_slope_20:2:LONG:h11` (native)
  - absent: `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` (hip3)
  - absent: `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` (hip3)
  - ... and 6 more
- Claimed edge (median mean_ret_costadj over 15 book slices present in the validated pools): +0.130% | at 97.97 ZAR mean notional/trade: +0.13 ZAR/trade
- Realised (73 real closes per lane_gate._is_real_close, net of fees): -0.47 ZAR/trade | sd 1.91 | SE 0.22
- Gap: -0.60 ZAR/trade | t = -2.68 (one-sample t of realised mean vs the claimed constant) | verdict: FALLS SHORT
- native: claimed median +0.188% over 5/13 slices (pool 14) ~ +0.18 ZAR | realised 54 closes -0.79 ZAR sd 2.08 SE 0.28 | gap -0.98 t -3.45 | FALLS SHORT
- hip3: claimed median +0.064% over 10/18 slices (pool 160) ~ +0.06 ZAR | realised 19 closes +0.44 ZAR sd 0.79 | INSUFFICIENT SAMPLE (n<30)
- Ledger: 27119 decision rows; 73 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 27046 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 54 | wins: 11 | win%: 20.4 | P&L: **-42.90 ZAR** | today: -22.76 | 7d: -42.90 | 30d: -42.90
- By exit: target +9.9, horizon -3.7, regime_shift -12.5, stop -36.6
- By entry regime (n/pnl): bull 1/-3.8, neutral 11/-15.4, bear 42/-23.7
- Top slices: feat_ret_10:2:LONG:h19 8n/2w +4.70; feat_realized_vol_20:2:LONG:h20 8n/7w +1.47; engine_mean_reversion:rsi:2:BUY:h10:XRPUSDT 1n/0w -0.12; feat_realized_vol_20:2:LONG:h23 3n/1w -0.13; engine_momentum:breakout:2:SELL:h10:AVAXUSDT 1n/0w -0.23
- Worst slices: feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; engine_mean_reversion:rsi:2:SELL:h10:ARBUSDC 1n/0w -5.05; engine_mean_reversion:bollinger:2:SELL:h10:ZECUSDC 1n/0w -4.93; feat_atr_norm_ext:2:LONG:h13 7n/0w -4.88
- Top pairs: ARBUSDC 2n +4.86; LINKUSDC 2n +0.17; HYPEUSDC 5n +0.14; ENAUSDC 1n -0.10; XRPUSDT 1n -0.12
- Worst pairs: TRUMPUSDC 2n -6.38; ZECUSDC 2n -5.32; XRPUSDC 3n -5.21; NEARUSDC 2n -5.10; FILUSDC 1n -5.08

### HIP3

- Closed: 19 | wins: 16 | win%: 84.2 | P&L: **+8.44 ZAR** | today: -0.11 | 7d: +8.44 | 30d: +8.44
- By exit: target +6.3, horizon +2.0, regime_shift +1.8, trail_stop +1.0, stop -2.7
- By entry regime (n/pnl): bear 6/+5.1, bull 12/+5.0, neutral 1/-1.7
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 1n/1w +2.05; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01
- Worst slices: hip3_para_equity_c0:feat_ret_vol:2:SHORT:h24 1n/0w -1.66; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 1n/0w -0.09; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02
- Top pairs: XYZ:STRC 8n +3.98; PARA:MELI 2n +3.06; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71; XYZ:NATGAS 2n +0.63
- Worst pairs: PARA:CIEN 1n -1.66; PARA:IGV 1n -0.09; XYZ:PALLADIUM 2n -0.05; XYZ:BRENTOIL 1n +0.49; XYZ:NATGAS 2n +0.63

## 4. Open positions & risk

- **NATIVE**: 8 open, stop-risk **28.11 ZAR**
  - ARBUSDC SELL ntl=84 risk=4.94 bars=3 stop=0.17935714285714285 peak=0.16938
  - ZECUSDC SELL ntl=99 risk=4.46 bars=2 stop=1307.1714285714286 peak=1250.6
  - UNIUSDC SELL ntl=98 risk=4.10 bars=1 stop=6.3065 peak=6.0545
  - FILUSDC SELL ntl=100 risk=3.73 bars=13 stop=0.8434728571428572 peak=0.81303
  - NEARUSDC SELL ntl=99 risk=3.56 bars=2 stop=2.555557142857143 peak=2.4664
  - LITUSDC SELL ntl=99 risk=3.47 bars=5 stop=4.453957142857143 peak=4.3036
  - PENDLEUSDC SELL ntl=98 risk=2.86 bars=1 stop=2.2190 peak=2.1563
  - SHIBUSDT SELL ntl=98 risk=0.98 bars=1 stop=0.0000048177000000000005 peak=0.00000477

- **HIP3**: 6 open, stop-risk **11.88 ZAR**
  - PARA:COHR SELL ntl=99 risk=3.38 bars=2 stop=294.5500000000000190 peak=284.79
  - PARA:IREN SELL ntl=98 risk=2.75 bars=0 stop=44.663250000000000375 peak=43.45
  - PARA:CRDO SELL ntl=99 risk=2.34 bars=2 stop=164.02500000000001420 peak=160.22
  - PARA:CIEN SELL ntl=99 risk=1.73 bars=2 stop=347.15249999999997345 peak=341.17
  - PARA:GLW SELL ntl=99 risk=1.18 bars=0 stop=148.99000000000001205 peak=147.23
  - PARA:AVGO SELL ntl=99 risk=0.51 bars=2 stop=344.77249999999998465 peak=342.99

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **39.99 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 13 | HIP-3: 18
- Native top (by paper P&L):
  - `feat_ret_10:2:LONG:h19` edge=0.0077 n=16875 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+8.86
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0058 n=17004 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+5.56
  - `feat_close_pos_ma:0:LONG:h5` edge=0.0013 n=13893 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_1:0:LONG:h6` edge=0.0013 n=16749 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_hour_utc:0:LONG:h10` edge=0.0019 n=14963 p=0.0004 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_buy_vol_ratio:0:LONG:h11` edge=0.0019 n=14671 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_close_position:0:LONG:h11` edge=0.0019 n=14671 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_trend_slope_20:2:LONG:h12` edge=0.0063 n=16968 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
- HIP-3 top (by paper P&L):
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h11` edge=0.0015 n=1260 p=0.0162 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h13` edge=0.0007 n=1256 p=0.4781 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ext_vs_ma_50:1:LONG:h22` edge=0.0006 n=1354 p=0.8646 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ret_20:1:LONG:h18` edge=0.0001 n=1563 p=0.9678 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_trend_strength_20:0:LONG:h23` edge=0.0001 n=1455 p=0.9492 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_vol_regime:2:SHORT:h21` edge=0.0016 n=11089 p=0.0125 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ret_20:2:SHORT:h21` edge=0.0001 n=9425 p=0.4234 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` edge=0.0003 n=9570 p=0.3356 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **19/50** | ghost rows: **69/50** | PnL: **+8.44 ZAR**
- Gate verdict: **NOT READY**

## 8. Research / honesty checks

- Latest research: 2026-09-16T11:09:41+00:00 | discovered 7488 | validated 14 | reg-confounded 6236 | hostile-unproven 0
- floors: {"PERP": "20.0", "SPOT": "140.0"} | book: {"blocked_for_green_breadth": 0, "carried_cooldown": 0, "carried_decayed": 0, "carried_kinds": ["PERP"], "carried_monitored": 7, "carried_total": 7, "concentrated": 0, "cooldown": 0, "decayed": 0, "families_considered": 6, "families_promoted": 5, "green_assets_total": 216, "monitored": 5, "multi_horizon_min_passes": 2, "multi_horizon_select": "edge_per_bar", "net_edge_floor_enter_bps": {"PERP": "20.0", "SPOT": "140.0"}, "net_edge_floor_keep_bps": {"PERP": "20.0", "SPOT": "140.0"}, "paper_protected": 1, "per_asset_aware": true, "promotable": 14, "promoted_green_fraction_mean": 0.4047, "rows_total_after_sync": 13, "session_gate_blocked": 0, "validated": 14}
- Short audit: discovered=3744 validated=3744 passing=0 eligible=0 best=-5.5b best_fail=direction_ok,breadth_ok,mean_net<=0
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

- Label: **bear** | breadth bear=0.5333 bull=0.0667 neutral=0.4 | symbols=15
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 22 / bull 0
- as_of: 2026-09-16T16:55:37Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 3744 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-23.89 | frozen=YES
- HIP-3 lane: **GREEN** | closed=19 pnl=+8.44 | frozen=NO
- Frozen lanes: native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `feat_realized_vol_20:2:LONG:h20` pnl=+1.47
  - `feat_ret_10:2:LONG:h19` pnl=+4.70
- Tradable slices: native **12/13** | hip3 **17/18**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 7
  - `feat_atr_norm_ext:2:LONG:h13` lane_not_green
  - `feat_realized_vol_20:2:LONG:h14` lane_not_green
  - `feat_realized_vol_20:2:LONG:h21` lane_not_green
  - `feat_realized_vol_20:2:LONG:h22` lane_not_green
  - `feat_realized_vol_20:2:LONG:h23` lane_not_green
  - `feat_realized_vol_20:2:LONG:h24` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` slice_pnl=-0.30

## 13. Signal activity

- Latest scan 2026-09-14T14:09:46: errors=4 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=10
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 17, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 10, "pair_held": 26, "regime_blocked": 198, "skipped": 277, "slice_full": 0, "slot_full": 104})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=1 blocks=21
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:DKNG"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:EBAY"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:RDDT"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:ZM"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
