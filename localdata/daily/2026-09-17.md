# Breakwater daily print — 2026-09-17 13:09 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **394.78 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **1951.87 ZAR** (seed 2000) | lifetime: **-48.13 ZAR** | closed: 100
- Today: 14 closed, **-2.18 ZAR**
- 7d: **-48.13 ZAR** | 30d: **-48.13 ZAR**

## 2b. Claimed vs realised

- Book: 26 slices (native 8 | hip3 18); validated pools: native 0 | hip3 160; book slices absent from pools: 16
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
- Claimed edge (median mean_ret_costadj over 10 book slices present in the validated pools): +0.064% | at 98.89 ZAR mean notional/trade: +0.06 ZAR/trade
- Realised (100 real closes per lane_gate._is_real_close, net of fees): -0.48 ZAR/trade | sd 2.35 | SE 0.24
- Gap: -0.54 ZAR/trade | t = -2.32 (one-sample t of realised mean vs the claimed constant) | verdict: FALLS SHORT
- native: claimed unknown (0/8 slices in pool 0) | realised 73 closes -0.65 ZAR | claimed unknown
- hip3: claimed median +0.064% over 10/18 slices (pool 160) ~ +0.06 ZAR | realised 27 closes -0.03 ZAR sd 2.12 | INSUFFICIENT SAMPLE (n<30)
- Ledger: 32698 decision rows; 100 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 32598 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 73 | wins: 20 | win%: 27.4 | P&L: **-47.20 ZAR** | today: +10.34 | 7d: -47.20 | 30d: -47.20
- By exit: horizon +18.3, target +9.9, regime_shift -11.9, stop -63.5
- By entry regime (n/pnl): bull 1/-3.8, neutral 11/-15.4, bear 61/-28.0
- Top slices: feat_ext_vs_ma_20:2:LONG:h15 4n/4w +9.07; feat_ext_strength:2:LONG:h15 4n/2w +6.73; feat_ret_10:2:LONG:h19 9n/3w +5.29; engine_momentum:trend_align:2:SELL:h15:FILUSDC 2n/1w +2.45; feat_realized_vol_20:2:LONG:h20 8n/7w +1.47
- Worst slices: feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; engine_mean_reversion:rsi:2:SELL:h10:ZECUSDC 2n/0w -6.66; engine_mean_reversion:bollinger:2:SELL:h10:ZECUSDC 1n/0w -4.93; feat_atr_norm_ext:2:LONG:h13 7n/0w -4.88
- Top pairs: ARBUSDC 3n +7.76; SUIUSDC 1n +3.81; TAOUSDC 2n +3.43; WLDUSDC 1n +1.64; LINKUSDC 2n +0.17
- Worst pairs: ZECUSDC 4n -11.98; NEARUSDC 3n -8.75; XRPUSDC 3n -5.21; ETHUSDC 8n -4.40; UNIUSDC 1n -4.19

### HIP3

- Closed: 27 | wins: 17 | win%: 63.0 | P&L: **-0.92 ZAR** | today: -12.51 | 7d: -0.92 | 30d: -0.92
- By exit: target +13.7, horizon +2.0, regime_shift +1.8, trail_stop +1.0, stop -19.5
- By entry regime (n/pnl): bull 12/+5.0, bear 8/+2.7, neutral 7/-8.6
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 1n/1w +2.05; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01
- Worst slices: hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30; hip3_para_equity_c0:feat_ext_vs_ma_10:0:SHORT:h17 1n/0w -1.80; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h24 1n/0w -1.66; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Top pairs: XYZ:STRC 8n +3.98; PARA:CIEN 3n +3.93; XYZ:COPPER 1n +1.36; PARA:MELI 3n +1.26; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRDO 2n -6.24; PARA:COHR 1n -3.47; PARA:IREN 1n -2.84; PARA:AVGO 1n -0.60; PARA:IGV 1n -0.09

## 4. Open positions & risk

- **NATIVE**: 11 open, stop-risk **42.56 ZAR**
  - LINKUSDC BUY ntl=195 risk=7.50 bars=16 stop=10.568250000000000175 peak=10.99
  - DOGEUSDC BUY ntl=195 risk=6.51 bars=17 stop=0.07773975000000000430 peak=0.080417
  - SUIUSDC BUY ntl=98 risk=3.81 bars=3 stop=0.6937050000000000245 peak=0.72188
  - TAOUSDC BUY ntl=98 risk=3.77 bars=2 stop=218.55249999999998005 peak=227.32
  - KPEPEUSDC BUY ntl=98 risk=3.76 bars=3 stop=0.0033364999999999999610 peak=0.00347
  - FILUSDC BUY ntl=98 risk=3.70 bars=3 stop=0.7672624999999999540 peak=0.79746
  - XRPUSDC BUY ntl=97 risk=3.42 bars=4 stop=1.2580499999999999655 peak=1.3041
  - ETHUSDC BUY ntl=97 risk=3.37 bars=10 stop=2344.3999999999998880 peak=2428.4
  - SOLUSDC BUY ntl=98 risk=2.69 bars=3 stop=97.43574999999999960 peak=100.2
  - BTCUSDC BUY ntl=98 risk=2.32 bars=13 stop=74370.75000000000010 peak=76180.0
  - BNBUSDC BUY ntl=98 risk=1.71 bars=3 stop=712.734975 peak=725.43

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **42.56 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 8 | HIP-3: 18
- Native top (by paper P&L):
  - `feat_ext_vs_ma_20:2:LONG:h15` edge=0.0072 n=16809 p=0.0000 src=validated_walk_forward unproven=False paper=4n/+9.07
  - `feat_ext_strength:2:LONG:h15` edge=0.0072 n=16038 p=0.0016 src=validated_walk_forward unproven=False paper=4n/+6.73
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0058 n=17004 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+5.56
  - `feat_ret_10:2:LONG:h19` edge=0.0077 n=16875 p=0.0000 src=validated_walk_forward unproven=False paper=9n/+5.29
  - `feat_trend_slope_20:2:LONG:h12` edge=0.0063 n=16968 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_50:2:LONG:h15` edge=0.0069 n=16411 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_20:2:LONG:h14` edge=0.0060 n=17052 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Closed paper trades: **27/50** | ghost rows: **166/50** | PnL: **-0.92 ZAR**
- Gate verdict: **NOT READY**

## 8. Research / honesty checks

- Latest research: 2026-09-17T00:10:32+00:00 | discovered 7488 | validated 0 | reg-confounded 6124 | hostile-unproven 0
- floors: {"PERP": "20.0", "SPOT": "140.0"} | book: {"blocked_for_green_breadth": 0, "carried_cooldown": 0, "carried_decayed": 0, "carried_kinds": ["PERP"], "carried_monitored": 7, "carried_total": 7, "concentrated": 0, "cooldown": 0, "decayed": 0, "families_considered": 0, "families_promoted": 0, "green_assets_total": 0, "monitored": 0, "multi_horizon_min_passes": 2, "multi_horizon_select": "edge_per_bar", "net_edge_floor_enter_bps": {"PERP": "20.0", "SPOT": "140.0"}, "net_edge_floor_keep_bps": {"PERP": "20.0", "SPOT": "140.0"}, "paper_protected": 1, "per_asset_aware": true, "promotable": 0, "promoted_green_fraction_mean": null, "rows_total_after_sync": 8, "session_gate_blocked": 0, "validated": 0}
- Short audit: discovered=3744 validated=3744 passing=0 eligible=0 best=-7.0b best_fail=direction_ok,breadth_ok,mean_net<=0
- pair_errors: []
- Deep audit: candidates=74880 preliminary_passes=0 audit_passes=0 plateaus=0 fetch_errors=25

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

- Label: **neutral** | breadth bear=0.0333 bull=0.2667 neutral=0.7 | symbols=30
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 0 / bull 0
- as_of: 2026-09-17T13:00:26Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 3744 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-5.16 | frozen=YES
- HIP-3 lane: **RED** | closed=20 pnl=-4.40 | frozen=YES
- Frozen lanes: hip3, native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 6
  - `feat_ext_strength:2:LONG:h15` pnl=+6.73
  - `feat_ext_vs_ma_20:2:LONG:h15` pnl=+9.07
  - `feat_realized_vol_20:2:LONG:h20` pnl=+1.47
  - `feat_ret_10:2:LONG:h19` pnl=+5.29
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **7/8** | hip3 **15/18**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 9
  - `feat_atr_norm_ext:2:LONG:h13` lane_not_green
  - `feat_realized_vol_20:2:LONG:h14` lane_not_green
  - `feat_realized_vol_20:2:LONG:h21` lane_not_green
  - `feat_realized_vol_20:2:LONG:h22` lane_not_green
  - `feat_realized_vol_20:2:LONG:h23` lane_not_green
  - `feat_realized_vol_20:2:LONG:h24` lane_not_green
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-09-17T13:09:23: errors=2 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=4
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 4, "pair_held": 33, "regime_blocked": 327, "skipped": 55, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=False hip3_green=False frozen=hip3,native islands=6 blocks=9
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:EWZ"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:URNM"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
