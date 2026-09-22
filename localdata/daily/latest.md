# Breakwater daily print — 2026-09-22 02:23 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **462.54 ZAR** | high-water: **474.55 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2531.47 ZAR** (seed 2000) | lifetime: **+531.47 ZAR** | closed: 219
- Today: 5 closed, **-14.04 ZAR**
- 7d: **+529.98 ZAR** | 30d: **+531.47 ZAR**

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
- Claimed edge (median mean_ret_costadj over 260 book slices present in the validated pools): +0.412% | at 157.76 ZAR mean notional/trade: +0.65 ZAR/trade
- Realised (219 real closes per lane_gate._is_real_close, net of fees): +2.43 ZAR/trade | sd 5.71 | SE 0.39
- Gap: +1.78 ZAR/trade | t = +4.60 (one-sample t of realised mean vs the claimed constant) | verdict: EXCEEDS
- native: claimed median +0.436% over 239/246 slices (pool 760) ~ +0.73 ZAR | realised 187 closes +2.88 ZAR sd 5.97 SE 0.44 | gap +2.16 t +4.94 | EXCEEDS
- hip3: claimed median +0.065% over 21/25 slices (pool 160) ~ +0.07 ZAR | realised 32 closes -0.25 ZAR sd 2.61 SE 0.46 | gap -0.32 t -0.69 | NOT ESTABLISHED
- Ledger: 87150 decision rows; 219 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 86931 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 187 | wins: 118 | win%: 63.1 | P&L: **+539.48 ZAR** | today: -3.13 | 7d: +539.48 | 30d: +539.48
- By exit: target +506.4, horizon +129.2, regime_shift -11.9, stop -84.3
- By entry regime (n/pnl): neutral 61/+292.2, bull 60/+263.7, bear 66/-16.4
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 20n/18w +166.60; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; engine_mean_reversion:rsi:2:SELL:h10:ZECUSDC 2n/0w -6.66; engine_mean_reversion:bollinger:2:SELL:h10:ZECUSDC 1n/0w -4.93; feat_atr_norm_ext:2:LONG:h13 7n/0w -4.88
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; BTCUSDC 13n +26.22; XRPUSDC 11n +21.98; XRPZAR 2n +18.07
- Worst pairs: ZECUSDC 4n -11.98; NEARUSDC 3n -8.75; ETHZAR 2n -8.51; UNIUSDC 1n -4.19; PUMPUSDC 1n -3.88

### HIP3

- Closed: 32 | wins: 19 | win%: 59.4 | P&L: **-8.00 ZAR** | today: -10.90 | 7d: -9.49 | 30d: -8.00
- By exit: target +19.0, horizon +2.3, regime_shift +1.8, trail_stop +1.0, stop -32.2
- By entry regime (n/pnl): bear 9/+3.1, bull 13/+1.2, neutral 10/-12.3
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 3n/2w +0.17
- Worst slices: hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 2n/1w -3.40; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30; hip3_para_equity_c0:feat_ext_vs_ma_10:0:SHORT:h17 1n/0w -1.80; hip3_para_equity_c0:feat_trend_strength_20:2:SHORT:h20 1n/0w -1.80
- Top pairs: PARA:CIEN 4n +9.17; XYZ:STRC 8n +3.98; PARA:MELI 4n +1.64; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73; PARA:COHR 1n -3.47; PARA:IREN 1n -2.84; PARA:TER 1n -1.80

## 4. Open positions & risk

- **NATIVE**: 9 open, stop-risk **85.72 ZAR**
  - BTCUSDC BUY ntl=509 risk=18.46 bars=4 stop=83480.24999999999985 peak=86621.0
  - BTCZAR BUY ntl=509 risk=16.49 bars=4 stop=1366578.2500000000010 peak=1412312.0
  - BNBZAR BUY ntl=503 risk=15.02 bars=11 stop=12643.499999999999985 peak=13033.0
  - ETHZAR BUY ntl=505 risk=14.47 bars=7 stop=43676.25 peak=44966.0
  - SOLUSDC BUY ntl=127 risk=4.86 bars=2 stop=114.44499999999999970 peak=118.98
  - ETHUSDC BUY ntl=121 risk=4.72 bars=14 stop=2620.5999999999998675 peak=2727.2
  - HYPEUSDC BUY ntl=124 risk=4.44 bars=12 stop=91.43674999999999890 peak=94.838
  - BNBUSDC BUY ntl=127 risk=3.91 bars=2 stop=775.7500000000000265 peak=800.28
  - BTCUSDC BUY ntl=127 risk=3.35 bars=1 stop=83664.25000000000005 peak=85933.0

- **HIP3**: 5 open, stop-risk **29.15 ZAR**
  - PARA:CIFR SELL ntl=248 risk=9.88 bars=9 stop=19.379999999999999455 peak=18.637
  - PARA:CIEN SELL ntl=248 risk=6.81 bars=12 stop=374.53749999999999845 peak=364.52
  - PARA:LRCX SELL ntl=254 risk=5.00 bars=6 stop=309.01249999999999675 peak=303.04
  - PARA:COHR SELL ntl=124 risk=4.27 bars=12 stop=337.78750000000002090 peak=326.53
  - PARA:CRWD SELL ntl=124 risk=3.18 bars=12 stop=252.9599999999999910 peak=246.63

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **114.87 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 246 | HIP-3: 25
- Native top (by paper P&L):
  - `feat_close_pos_ma:1:LONG:h24` edge=0.0036 n=10058 p=0.0066 src=validated_walk_forward unproven=False paper=37n/+283.35
  - `feat_close_pos_ma:2:LONG:h12` edge=0.0092 n=1092 p=0.3222 src=validated_walk_forward unproven=False paper=20n/+166.60
  - `feat_ext_strength:2:LONG:h15` edge=0.0072 n=16038 p=0.0016 src=validated_walk_forward unproven=False paper=12n/+24.00
  - `feat_bb_pos_20:2:LONG:h15` edge=0.0073 n=9943 p=0.0322 src=validated_walk_forward unproven=False paper=4n/+16.17
  - `feat_bb_pos_20:2:LONG:h15` edge=0.0090 n=10497 p=0.0043 src=validated_walk_forward unproven=False paper=4n/+16.17
  - `feat_ret_10:2:LONG:h19` edge=0.0077 n=16875 p=0.0000 src=validated_walk_forward unproven=False paper=11n/+14.58
  - `feat_ret_20:2:LONG:h14` edge=0.0060 n=17052 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+13.42
  - `feat_cci_20:2:LONG:h15` edge=0.0088 n=9677 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+13.32
- HIP-3 top (by paper P&L):
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` edge=0.0003 n=9570 p=0.3356 src=validated_walk_forward unproven=False paper=15n/+4.27
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` edge=0.0175 n=268 p=0.0651 src=validated_walk_forward unproven=False paper=9n/+0.66
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h11` edge=0.0015 n=1260 p=0.0162 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h9` edge=0.0006 n=1272 p=0.4321 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ext_vs_ma_50:1:LONG:h22` edge=0.0006 n=1354 p=0.8646 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ext_strength:1:LONG:h18` edge=0.0001 n=1420 p=0.9829 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ret_20:1:LONG:h18` edge=0.0001 n=1563 p=0.9678 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_trend_slope_20:0:LONG:h20` edge=0.0008 n=1576 p=0.1320 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **32/50** | ghost rows: **315/50** | PnL: **-8.00 ZAR**
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

- Label: **bull** | breadth bear=0.0 bull=0.8 neutral=0.2 | symbols=15
- confirmed_bear: **False** | confirmed_bull: **True** | flip: **True** | flipped_from: bull | consecutive_bear: 0 / bull 30
- as_of: 2026-09-22T02:00:26Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 832 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+191.84 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-14.48 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 3
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` pnl=+0.17
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **191/246** | hip3 **21/25**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 9
  - `feat_atr_norm_ext:2:LONG:h13` slice_pnl=-4.88
  - `feat_realized_vol_20:2:LONG:h14` slice_pnl=-0.40
  - `feat_realized_vol_20:2:LONG:h21` slice_pnl=-2.71
  - `feat_realized_vol_20:2:LONG:h22` slice_pnl=-1.39
  - `feat_realized_vol_20:2:LONG:h23` slice_pnl=-0.13
  - `feat_realized_vol_20:2:LONG:h24` slice_pnl=-13.68
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-09-22T02:23:02: errors=0 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=3
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 3, "pair_held": 8, "regime_blocked": 525, "skipped": 726, "slice_full": 1, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=3 blocks=9
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
