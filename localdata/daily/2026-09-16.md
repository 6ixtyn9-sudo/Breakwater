# Breakwater daily print — 2026-09-16 08:09 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

> ## COMA ALARM — NATIVE

> No **proven** slice in this lane. Auditions can still open entries, so
> this is not a dead lane: it trades, but nothing in it trades on a record
> it earned, so it cannot unfreeze itself. The runner will keep reporting
> operational, which is why this block exists. Attention, not intervention.

## 1. Posture

- Mode: **readonly** | VALR equity: **380.49 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **1988.75 ZAR** (seed 2000) | lifetime: **-11.25 ZAR** | closed: 56
- Today: 17 closed, **+0.34 ZAR**
- 7d: **-11.25 ZAR** | 30d: **-11.25 ZAR**

## 2b. Claimed vs realised

- Book: 26 slices (native 8 | hip3 18); validated pools: native 157 | hip3 160; book slices absent from pools: 16
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
- Claimed edge (median mean_ret_costadj over 10 book slices present in the validated pools): +0.064% | at 98.01 ZAR mean notional/trade: +0.06 ZAR/trade
- Realised (56 real closes per lane_gate._is_real_close, net of fees): -0.20 ZAR/trade | sd 1.92 | SE 0.26
- Gap: -0.26 ZAR/trade | t = -1.03 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed unknown (0/8 slices in pool 157) | realised 40 closes -0.53 ZAR | claimed unknown
- hip3: claimed median +0.064% over 10/18 slices (pool 160) ~ +0.06 ZAR | realised 16 closes +0.62 ZAR sd 0.63 | INSUFFICIENT SAMPLE (n<30)
- Ledger: 25990 decision rows; 56 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 25934 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 40 | wins: 10 | win%: 25.0 | P&L: **-21.16 ZAR** | today: -1.02 | 7d: -21.16 | 30d: -21.16
- By exit: target +9.9, horizon -2.7, regime_shift -7.1, stop -21.3
- By entry regime (n/pnl): bear 28/-2.0, bull 1/-3.8, neutral 11/-15.4
- Top slices: feat_ret_10:2:LONG:h19 2n/1w +8.86; feat_realized_vol_20:2:LONG:h20 8n/7w +1.47; engine_mean_reversion:rsi:2:BUY:h10:XRPUSDT 1n/0w -0.12; feat_realized_vol_20:2:LONG:h23 3n/1w -0.13; feat_realized_vol_20:2:LONG:h14 4n/1w -0.40
- Worst slices: feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; feat_atr_norm_ext:2:LONG:h13 7n/0w -4.88; feat_realized_vol_20:2:LONG:h21 3n/0w -2.71; feat_realized_vol_20:2:LONG:h22 4n/0w -1.39
- Top pairs: ARBUSDC 1n +9.91; LINKUSDC 2n +0.17; HYPEUSDC 5n +0.14; ENAUSDC 1n -0.10; XRPUSDT 1n -0.12
- Worst pairs: FILUSDC 1n -5.08; TRUMPUSDC 1n -4.96; ETHUSDC 8n -4.40; XRPUSDC 1n -3.79; BNBUSDC 1n -2.30

### HIP3

- Closed: 16 | wins: 15 | win%: 93.8 | P&L: **+9.91 ZAR** | today: +1.36 | 7d: +9.91 | 30d: +9.91
- By exit: target +6.3, horizon +2.1, regime_shift +1.6, trail_stop +1.0, stop -1.1
- By entry regime (n/pnl): bear 6/+5.1, bull 10/+4.8
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 1n/1w +2.05; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01
- Worst slices: hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 2n/1w -0.58; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 1n/1w +2.05; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42
- Top pairs: XYZ:STRC 8n +3.98; PARA:MELI 2n +3.06; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71; XYZ:BRENTOIL 1n +0.49
- Worst pairs: XYZ:PALLADIUM 2n -0.05; XYZ:NATGAS 1n +0.36; XYZ:BRENTOIL 1n +0.49; XYZ:SILVER 1n +0.71; XYZ:COPPER 1n +1.36

## 4. Open positions & risk

- **NATIVE**: 6 open, stop-risk **20.52 ZAR**
  - UNIUSDC SELL ntl=89 risk=4.98 bars=5 stop=6.647857142857142 peak=6.2943
  - KPEPEUSDC BUY ntl=89 risk=4.98 bars=0 stop=0.0031672500000000001360 peak=0.003355
  - ZECUSDC SELL ntl=100 risk=4.84 bars=1 stop=1246.0714285714284 peak=1188.3
  - FILUSDC SELL ntl=100 risk=3.73 bars=5 stop=0.8434728571428572 peak=0.81303
  - AVAXUSDT SELL ntl=100 risk=1.00 bars=3 stop=7.37906 peak=7.306
  - MSTRXUSDT SELL ntl=100 risk=1.00 bars=2 stop=129.32039999999998 peak=128.04

- **HIP3**: 6 open, stop-risk **13.80 ZAR**
  - PARA:RDDT SELL ntl=100 risk=4.65 bars=12 stop=166.79999999999999210 peak=159.37
  - PARA:CRWD SELL ntl=100 risk=3.87 bars=12 stop=252.03749999999998405 peak=242.63
  - PARA:IGV SELL ntl=100 risk=1.79 bars=0 stop=108.7800000000000015 peak=106.86
  - PARA:CIEN SELL ntl=100 risk=1.56 bars=12 stop=339.73 peak=334.48
  - PARA:MELI SELL ntl=100 risk=0.99 bars=0 stop=1849.22499999999996625 peak=1831.0
  - PARA:AVGO SELL ntl=100 risk=0.94 bars=11 stop=345.24999999999999390 peak=342.04

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **34.32 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 8 | HIP-3: 18
- Native top (by paper P&L):
  - `feat_ret_10:2:LONG:h19` edge=0.0077 n=16875 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+8.86
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0058 n=17004 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+5.56
  - `feat_trend_slope_20:2:LONG:h12` edge=0.0063 n=16968 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_20:2:LONG:h15` edge=0.0072 n=16809 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_50:2:LONG:h15` edge=0.0069 n=16411 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_20:2:LONG:h14` edge=0.0060 n=17052 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_strength:2:LONG:h15` edge=0.0072 n=16038 p=0.0016 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_realized_vol_20:2:LONG:h14` edge=0.0058 n=22975 p=0.0000 src=validated_walk_forward unproven=False paper=4n/-0.40
- HIP-3 top (by paper P&L):
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` edge=0.0003 n=9570 p=0.3356 src=validated_walk_forward unproven=False paper=15n/+4.27
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` edge=0.0175 n=268 p=0.0651 src=validated_walk_forward unproven=False paper=1n/+2.05
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h11` edge=0.0015 n=1260 p=0.0162 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h13` edge=0.0007 n=1256 p=0.4781 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ext_vs_ma_50:1:LONG:h22` edge=0.0006 n=1354 p=0.8646 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ret_20:1:LONG:h18` edge=0.0001 n=1563 p=0.9678 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_trend_strength_20:0:LONG:h23` edge=0.0001 n=1455 p=0.9492 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_vol_regime:2:SHORT:h21` edge=0.0016 n=11089 p=0.0125 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **16/50** | ghost rows: **47/50** | PnL: **+9.91 ZAR**
- Gate verdict: **NOT READY**

## 8. Research / honesty checks

- Latest research: 2026-09-16T03:18:43+00:00 | discovered 7488 | validated 157 | reg-confounded 6148 | hostile-unproven 0
- floors: {"PERP": "69.0", "SPOT": "140.0"} | book: {"blocked_for_green_breadth": 0, "carried_cooldown": 0, "carried_decayed": 0, "carried_kinds": ["PERP"], "carried_monitored": 7, "carried_total": 7, "concentrated": 0, "cooldown": 0, "decayed": 0, "families_considered": 14, "families_promoted": 13, "green_assets_total": 461, "monitored": 13, "multi_horizon_min_passes": 2, "multi_horizon_select": "edge_per_bar", "net_edge_floor_enter_bps": {"PERP": "69.0", "SPOT": "140.0"}, "net_edge_floor_keep_bps": {"PERP": "52.9", "SPOT": "140.0"}, "paper_protected": 1, "per_asset_aware": true, "promotable": 52, "promoted_green_fraction_mean": 0.3064, "rows_total_after_sync": 21, "session_gate_blocked": 0, "validated": 157}
- Short audit: discovered=3744 validated=3744 passing=0 eligible=0 best=-6.1b best_fail=direction_ok,breadth_ok,mean_net<=0
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

- Label: **bear** | breadth bear=0.7667 bull=0.0 neutral=0.2 | symbols=29
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 13 / bull 0
- as_of: 2026-09-16T08:00:31Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 3744 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-4.24 | frozen=YES
- HIP-3 lane: **GREEN** | closed=16 pnl=+9.91 | frozen=NO
- Frozen lanes: native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 1
  - `feat_realized_vol_20:2:LONG:h20` pnl=+1.47
- Tradable slices: native **7/8** | hip3 **18/18**
- **COMA LANES: native** — frozen with no tradable slice on an earned green record; auditions may still open.
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 6
  - `feat_atr_norm_ext:2:LONG:h13` lane_not_green
  - `feat_realized_vol_20:2:LONG:h14` lane_not_green
  - `feat_realized_vol_20:2:LONG:h21` lane_not_green
  - `feat_realized_vol_20:2:LONG:h22` lane_not_green
  - `feat_realized_vol_20:2:LONG:h23` lane_not_green
  - `feat_realized_vol_20:2:LONG:h24` lane_not_green

## 13. Signal activity

- Latest scan 2026-09-16T08:09:21: errors=5 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=1
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 1, "pair_held": 8, "regime_blocked": 130, "skipped": 11, "slice_full": 0, "slot_full": 20})
- green_gate: native_green=False hip3_green=True frozen=native islands=1 blocks=6
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:BOT"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:EWJ"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:NOW"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:SHAZ"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:SMH"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
