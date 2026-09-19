# Breakwater daily print — 2026-09-19 10:19 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **427.61 ZAR** | high-water: **441.81 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2076.93 ZAR** (seed 2000) | lifetime: **+76.93 ZAR** | closed: 139
- Today: 7 closed, **+15.45 ZAR**
- 7d: **+76.93 ZAR** | 30d: **+76.93 ZAR**

## 2b. Claimed vs realised

- Book: 272 slices (native 247 | hip3 25); validated pools: native 705 | hip3 160; book slices absent from pools: 7
  - absent: `feat_ret_20:2:LONG:h14` (native)
  - absent: `feat_ret_10:2:LONG:h19` (native)
  - absent: `feat_trend_slope_20:2:LONG:h11` (native)
  - absent: `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` (hip3)
  - absent: `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` (hip3)
  - absent: `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` (hip3)
  - absent: `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` (hip3)
- Claimed edge (median mean_ret_costadj over 265 book slices present in the validated pools): +0.460% | at 100.36 ZAR mean notional/trade: +0.46 ZAR/trade
- Realised (139 real closes per lane_gate._is_real_close, net of fees): +0.55 ZAR/trade | sd 2.83 | SE 0.24
- Gap: +0.09 ZAR/trade | t = +0.38 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.476% over 244/247 slices (pool 705) ~ +0.48 ZAR | realised 109 closes +0.68 ZAR sd 2.97 SE 0.28 | gap +0.20 t +0.70 | NOT ESTABLISHED
- hip3: claimed median +0.065% over 21/25 slices (pool 160) ~ +0.06 ZAR | realised 30 closes +0.10 ZAR sd 2.26 SE 0.41 | gap +0.03 t +0.08 | NOT ESTABLISHED
- Ledger: 56639 decision rows; 139 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 56500 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 109 | wins: 55 | win%: 50.5 | P&L: **+74.03 ZAR** | today: +15.45 | 7d: +74.03 | 30d: +74.03
- By exit: horizon +91.9, target +57.6, regime_shift -11.9, stop -63.5
- By entry regime (n/pnl): neutral 35/+68.6, bull 8/+21.9, bear 66/-16.4
- Top slices: feat_ext_strength:2:LONG:h15 9n/6w +26.47; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77; feat_ret_10:2:LONG:h19 11n/5w +14.58; feat_ret_20:2:LONG:h14 5n/5w +13.42; feat_cci_20:2:LONG:h15 3n/3w +13.32
- Worst slices: feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; engine_mean_reversion:rsi:2:SELL:h10:ZECUSDC 2n/0w -6.66; engine_mean_reversion:bollinger:2:SELL:h10:ZECUSDC 1n/0w -4.93; feat_atr_norm_ext:2:LONG:h13 7n/0w -4.88
- Top pairs: LINKUSDC 5n +14.96; SUIUSDC 3n +14.91; SOLUSDC 13n +11.15; DOGEUSDC 5n +8.92; LINKZAR 3n +8.66
- Worst pairs: ZECUSDC 4n -11.98; NEARUSDC 3n -8.75; UNIUSDC 1n -4.19; PUMPUSDC 1n -3.88; LITUSDC 1n -3.56

### HIP3

- Closed: 30 | wins: 19 | win%: 63.3 | P&L: **+2.90 ZAR** | today: +0.00 | 7d: +2.90 | 30d: +2.90
- By exit: target +19.0, horizon +2.3, regime_shift +1.8, trail_stop +1.0, stop -21.3
- By entry regime (n/pnl): bull 12/+5.0, bear 9/+3.1, neutral 9/-5.2
- Top slices: hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 2n/2w +7.29; hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01
- Worst slices: hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30; hip3_para_equity_c0:feat_ext_vs_ma_10:0:SHORT:h17 1n/0w -1.80; hip3_para_equity_c0:feat_trend_strength_20:2:SHORT:h20 1n/0w -1.80; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h24 1n/0w -1.66
- Top pairs: PARA:CIEN 4n +9.17; XYZ:STRC 8n +3.98; PARA:MELI 4n +1.64; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRDO 2n -6.24; PARA:COHR 1n -3.47; PARA:IREN 1n -2.84; PARA:TER 1n -1.80; PARA:AVGO 1n -0.60

## 4. Open positions & risk

- **NATIVE**: 13 open, stop-risk **46.86 ZAR**
  - SOLUSDC BUY ntl=207 risk=8.17 bars=4 stop=108.78750000000000565 peak=113.27
  - ETHUSDC BUY ntl=207 risk=5.79 bars=3 stop=2547.924999999999975 peak=2621.4
  - LINKUSDC BUY ntl=103 risk=3.95 bars=11 stop=11.87724999999999980 peak=12.352
  - DOGEUSDC BUY ntl=103 risk=3.87 bars=7 stop=0.08463350000000000245 peak=0.087927
  - BTCUSDC BUY ntl=207 risk=3.86 bars=3 stop=79553.750000000000095 peak=81067.0
  - XRPZAR BUY ntl=103 risk=3.75 bars=3 stop=22.262500000000001420 peak=23.1
  - ETHZAR BUY ntl=103 risk=2.84 bars=5 stop=41496.500000000000095 peak=42672.0
  - BTCUSDC BUY ntl=103 risk=2.83 bars=5 stop=79105.74999999999985 peak=81333.0
  - BNBUSDC BUY ntl=103 risk=2.55 bars=7 stop=745.6200000000000145 peak=764.51
  - BTCZAR BUY ntl=103 risk=2.54 bars=5 stop=1294261.0000000000005 peak=1326934.0
  - LTCZAR BUY ntl=103 risk=2.48 bars=5 stop=908.9749999999999845 peak=931.3
  - BNBZAR BUY ntl=103 risk=2.41 bars=5 stop=12153.999999999999990 peak=12444.0
  - LINKZAR BUY ntl=104 risk=1.82 bars=0 stop=157.583175 peak=160.39

- **HIP3**: 4 open, stop-risk **17.94 ZAR**
  - PARA:COHR SELL ntl=203 risk=7.42 bars=18 stop=320.19000000000001555 peak=308.91
  - PARA:CRDO SELL ntl=203 risk=5.19 bars=18 stop=177.76000000000000660 peak=173.33
  - PARA:AVGO SELL ntl=203 risk=3.55 bars=18 stop=365.313025 peak=359.03
  - PARA:CIEN SELL ntl=102 risk=1.78 bars=11 stop=354.059475 peak=347.97

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **64.80 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 247 | HIP-3: 25
- Native top (by paper P&L):
  - `feat_ext_strength:2:LONG:h15` edge=0.0072 n=16038 p=0.0016 src=validated_walk_forward unproven=False paper=9n/+26.47
  - `feat_atr_norm_ext:2:LONG:h15` edge=0.0091 n=9846 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+15.77
  - `feat_atr_norm_ext:2:LONG:h15` edge=0.0063 n=9365 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+15.77
  - `feat_ret_10:2:LONG:h19` edge=0.0077 n=16875 p=0.0000 src=validated_walk_forward unproven=False paper=11n/+14.58
  - `feat_ret_20:2:LONG:h14` edge=0.0060 n=17052 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+13.42
  - `feat_cci_20:2:LONG:h15` edge=0.0057 n=9147 p=0.0001 src=validated_walk_forward unproven=False paper=3n/+13.32
  - `feat_mean_rev_strength:0:LONG:h15` edge=0.0093 n=9931 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+11.65
  - `feat_mean_rev_strength:0:LONG:h15` edge=0.0066 n=9478 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+11.65
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

- Closed paper trades: **30/50** | ghost rows: **241/50** | PnL: **+2.90 ZAR**
- Gate verdict: **NOT READY**

## 8. Research / honesty checks

- Latest research: 2026-09-15T10:13:03+00:00 | discovered 4608 | validated 0 | reg-confounded 3638 | hostile-unproven 0
- floors: {"PERP": "75.7", "SPOT": "140.0"} | book: {"blocked_for_green_breadth": 0, "carried_cooldown": 0, "carried_decayed": 0, "carried_kinds": ["PERP"], "carried_monitored": 67, "carried_total": 67, "concentrated": 0, "cooldown": 0, "decayed": 0, "families_considered": 0, "families_promoted": 0, "green_assets_total": 0, "monitored": 0, "multi_horizon_min_passes": 2, "multi_horizon_select": "edge_per_bar", "net_edge_floor_enter_bps": {"PERP": "75.7", "SPOT": "140.0"}, "net_edge_floor_keep_bps": {"PERP": "57.8", "SPOT": "140.0"}, "paper_protected": 0, "per_asset_aware": true, "promotable": 0, "promoted_green_fraction_mean": null, "rows_total_after_sync": 67, "session_gate_blocked": 0, "validated": 0}
- Short audit: discovered=2304 validated=2304 passing=0 eligible=0 best=-6.6b best_fail=temporal_pass,direction_ok,breadth_ok,mean_net<=0
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

- Label: **bull** | breadth bear=0.0 bull=0.8235 neutral=0.1765 | symbols=17
- confirmed_bear: **False** | confirmed_bull: **True** | flip: **True** | flipped_from: bull | consecutive_bear: 0 / bull 29
- as_of: 2026-09-19T09:35:28Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 832 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+73.56 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-2.06 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **194/247** | hip3 **21/25**
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

- Latest scan 2026-09-19T08:25:47: errors=0 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=3
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 3, "pair_held": 59, "regime_blocked": 434, "skipped": 891, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=9
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
