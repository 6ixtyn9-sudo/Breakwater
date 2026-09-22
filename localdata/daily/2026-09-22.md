# Breakwater daily print — 2026-09-22 09:54 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **451.99 ZAR** | high-water: **474.55 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2503.01 ZAR** (seed 2000) | lifetime: **+503.01 ZAR** | closed: 224
- Today: 10 closed, **-42.50 ZAR**
- 7d: **+504.98 ZAR** | 30d: **+503.01 ZAR**

## 2b. Claimed vs realised

- Book: 271 slices (native 246 | hip3 25); validated pools: native 760 | hip3 160; book slices absent from pools: 11
  - absent: `feat_range_pos_50:2:LONG:h15` (native)
  - absent: `feat_ext_vs_ma_50:1:SHORT:h24` (native)
  - absent: `feat_vol_regime:0:LONG:h24` (native)
  - absent: `feat_vol_contraction:0:LONG:h24` (native)
  - absent: `feat_ret_20:2:LONG:h14` (native)
  - absent: `feat_ret_10:2:LONG:h19` (native)
  - absent: `feat_trend_slope_20:2:LONG:h11` (native)
  - absent: `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` (hip3)
  - absent: `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` (hip3)
  - absent: `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` (hip3)
  - ... and 1 more
- Claimed edge (median mean_ret_costadj over 260 book slices present in the validated pools): +0.412% | at 160.93 ZAR mean notional/trade: +0.66 ZAR/trade
- Realised (224 real closes per lane_gate._is_real_close, net of fees): +2.25 ZAR/trade | sd 5.80 | SE 0.39
- Gap: +1.58 ZAR/trade | t = +4.08 (one-sample t of realised mean vs the claimed constant) | verdict: EXCEEDS
- native: claimed median +0.436% over 239/246 slices (pool 760) ~ +0.74 ZAR | realised 191 closes +2.73 ZAR sd 6.03 SE 0.44 | gap +1.99 t +4.56 | EXCEEDS
- hip3: claimed median +0.065% over 21/25 slices (pool 160) ~ +0.07 ZAR | realised 33 closes -0.55 ZAR sd 3.09 SE 0.54 | gap -0.62 t -1.15 | NOT ESTABLISHED
- Ledger: 91261 decision rows; 224 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 91037 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 191 | wins: 118 | win%: 61.8 | P&L: **+521.11 ZAR** | today: -21.49 | 7d: +525.99 | 30d: +521.11
- By exit: target +506.4, horizon +110.8, regime_shift -11.9, stop -84.3
- By entry regime (n/pnl): neutral 61/+292.2, bull 64/+245.4, bear 66/-16.4
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 22n/18w +150.10; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; engine_mean_reversion:rsi:2:SELL:h10:ZECUSDC 2n/0w -6.66; feat_vol_breakout:2:LONG:h15 3n/0w -6.39; engine_mean_reversion:bollinger:2:SELL:h10:ZECUSDC 1n/0w -4.93
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; BTCUSDC 13n +26.22; XRPUSDC 11n +21.98; XRPZAR 2n +18.07
- Worst pairs: ETHZAR 3n -16.60; ZECUSDC 4n -11.98; NEARUSDC 3n -8.75; UNIUSDC 1n -4.19; PUMPUSDC 1n -3.88

### HIP3

- Closed: 33 | wins: 19 | win%: 57.6 | P&L: **-18.11 ZAR** | today: -21.01 | 7d: -21.02 | 30d: -18.11
- By exit: target +19.0, horizon +2.3, regime_shift +1.8, trail_stop +1.0, stop -42.3
- By entry regime (n/pnl): bear 9/+3.1, bull 14/-8.9, neutral 10/-12.3
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 4n/2w -9.94; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 2n/1w -3.40; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30; hip3_para_equity_c0:feat_ext_vs_ma_10:0:SHORT:h17 1n/0w -1.80
- Top pairs: PARA:CIEN 4n +9.17; XYZ:STRC 8n +3.98; PARA:MELI 4n +1.64; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73; PARA:COHR 1n -3.47; PARA:IREN 1n -2.84

## 4. Open positions & risk

- **NATIVE**: 7 open, stop-risk **55.17 ZAR**
  - BTCUSDC BUY ntl=509 risk=18.46 bars=11 stop=83480.24999999999985 peak=86621.0
  - BTCZAR BUY ntl=509 risk=16.49 bars=11 stop=1366578.2500000000010 peak=1412312.0
  - SOLUSDC BUY ntl=127 risk=4.86 bars=9 stop=114.44499999999999970 peak=118.98
  - HYPEUSDC BUY ntl=126 risk=4.80 bars=4 stop=89.96399999999999715 peak=93.542
  - BNBUSDC BUY ntl=127 risk=3.91 bars=9 stop=775.7500000000000265 peak=800.28
  - BTCUSDC BUY ntl=127 risk=3.35 bars=8 stop=83664.25000000000005 peak=85933.0
  - ETHUSDC BUY ntl=125 risk=3.30 bars=1 stop=2656.3000000000001325 peak=2728.2

- **HIP3**: 4 open, stop-risk **19.27 ZAR**
  - PARA:CIEN SELL ntl=248 risk=6.81 bars=19 stop=374.53749999999999845 peak=364.52
  - PARA:LRCX SELL ntl=254 risk=5.00 bars=13 stop=309.01249999999999675 peak=303.04
  - PARA:COHR SELL ntl=124 risk=4.27 bars=19 stop=337.78750000000002090 peak=326.53
  - PARA:CRWD SELL ntl=124 risk=3.18 bars=19 stop=252.9599999999999910 peak=246.63

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **74.44 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 246 | HIP-3: 25
- Native top (by paper P&L):
  - `feat_close_pos_ma:1:LONG:h24` edge=0.0036 n=10058 p=0.0066 src=validated_walk_forward unproven=False paper=37n/+283.35
  - `feat_close_pos_ma:2:LONG:h12` edge=0.0092 n=1092 p=0.3222 src=validated_walk_forward unproven=False paper=22n/+150.10
  - `feat_ext_strength:2:LONG:h15` edge=0.0072 n=16038 p=0.0016 src=validated_walk_forward unproven=False paper=12n/+24.00
  - `feat_bb_pos_20:2:LONG:h15` edge=0.0073 n=9943 p=0.0322 src=validated_walk_forward unproven=False paper=4n/+16.17
  - `feat_bb_pos_20:2:LONG:h15` edge=0.0090 n=10497 p=0.0043 src=validated_walk_forward unproven=False paper=4n/+16.17
  - `feat_ret_10:2:LONG:h19` edge=0.0077 n=16875 p=0.0000 src=validated_walk_forward unproven=False paper=11n/+14.58
  - `feat_ret_20:2:LONG:h14` edge=0.0060 n=17052 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+13.42
  - `feat_cci_20:2:LONG:h15` edge=0.0088 n=9677 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+13.32
- HIP-3 top (by paper P&L):
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` edge=0.0054 n=242 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h11` edge=0.0015 n=1260 p=0.0162 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h9` edge=0.0006 n=1272 p=0.4321 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ext_vs_ma_50:1:LONG:h22` edge=0.0006 n=1354 p=0.8646 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ext_strength:1:LONG:h18` edge=0.0001 n=1420 p=0.9829 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ret_20:1:LONG:h18` edge=0.0001 n=1563 p=0.9678 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_trend_slope_20:0:LONG:h20` edge=0.0008 n=1576 p=0.1320 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_atr_norm_ext:0:LONG:h23` edge=0.0009 n=1577 p=0.0441 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **33/50** | ghost rows: **365/50** | PnL: **-18.11 ZAR**
- Gate verdict: **NOT READY**

## 8. Research / honesty checks

- Latest research: 2026-09-16T11:09:41+00:00 | discovered 7488 | validated 14 | reg-confounded 6236 | hostile-unproven 0
- floors: {"PERP": "20.0", "SPOT": "140.0"} | book: {"blocked_for_green_breadth": 0, "carried_cooldown": 0, "carried_decayed": 0, "carried_kinds": ["PERP"], "carried_monitored": 7, "carried_total": 7, "concentrated": 0, "cooldown": 0, "decayed": 0, "families_considered": 6, "families_promoted": 5, "green_assets_total": 216, "monitored": 5, "multi_horizon_min_passes": 2, "multi_horizon_select": "edge_per_bar", "net_edge_floor_enter_bps": {"PERP": "20.0", "SPOT": "140.0"}, "net_edge_floor_keep_bps": {"PERP": "20.0", "SPOT": "140.0"}, "paper_protected": 1, "per_asset_aware": true, "promotable": 14, "promoted_green_fraction_mean": 0.4047, "rows_total_after_sync": 13, "session_gate_blocked": 0, "validated": 14}
- Short audit: discovered=3744 validated=3744 passing=0 eligible=0 best=-5.5b best_fail=direction_ok,breadth_ok,mean_net<=0
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

- Label: **bull** | breadth bear=0.0 bull=0.9375 neutral=0.0625 | symbols=16
- confirmed_bear: **False** | confirmed_bull: **True** | flip: **True** | flipped_from: bull | consecutive_bear: 0 / bull 38
- as_of: 2026-09-22T09:35:25Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 832 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+145.16 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-24.94 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **190/246** | hip3 **20/25**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 11
  - `feat_atr_norm_ext:2:LONG:h13` slice_pnl=-4.88
  - `feat_realized_vol_20:2:LONG:h14` slice_pnl=-0.40
  - `feat_realized_vol_20:2:LONG:h21` slice_pnl=-2.71
  - `feat_realized_vol_20:2:LONG:h22` slice_pnl=-1.39
  - `feat_realized_vol_20:2:LONG:h23` slice_pnl=-0.13
  - `feat_realized_vol_20:2:LONG:h24` slice_pnl=-13.68
  - `feat_vol_breakout:2:LONG:h15` slice_pnl=-6.39
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-09-22T09:26:40: errors=1 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=5
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 5, "pair_held": 12, "regime_blocked": 455, "skipped": 861, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=11
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:EBAY"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
