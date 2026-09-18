# Breakwater daily print — 2026-09-18 05:45 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **409.17 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **1994.00 ZAR** (seed 2000) | lifetime: **-6.00 ZAR** | closed: 115
- Today: 7 closed, **+28.59 ZAR**
- 7d: **-6.00 ZAR** | 30d: **-6.00 ZAR**

## 2b. Claimed vs realised

- Book: 219 slices (native 194 | hip3 25); validated pools: native 520 | hip3 160; book slices absent from pools: 8
  - absent: `feat_ret_20:2:LONG:h14` (native)
  - absent: `feat_realized_vol_20:2:LONG:h14` (native)
  - absent: `feat_ret_10:2:LONG:h19` (native)
  - absent: `feat_trend_slope_20:2:LONG:h11` (native)
  - absent: `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` (hip3)
  - absent: `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` (hip3)
  - absent: `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` (hip3)
  - absent: `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` (hip3)
- Claimed edge (median mean_ret_costadj over 211 book slices present in the validated pools): +0.309% | at 100.42 ZAR mean notional/trade: +0.31 ZAR/trade
- Realised (115 real closes per lane_gate._is_real_close, net of fees): -0.05 ZAR/trade | sd 2.63 | SE 0.25
- Gap: -0.36 ZAR/trade | t = -1.48 (one-sample t of realised mean vs the claimed constant) | verdict: NOT ESTABLISHED
- native: claimed median +0.341% over 190/194 slices (pool 520) ~ +0.34 ZAR | realised 86 closes -0.10 ZAR sd 2.75 SE 0.30 | gap -0.44 t -1.49 | NOT ESTABLISHED
- hip3: claimed median +0.065% over 21/25 slices (pool 160) ~ +0.06 ZAR | realised 29 closes +0.09 ZAR sd 2.30 | INSUFFICIENT SAMPLE (n<30)
- Ledger: 38920 decision rows; 115 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 38805 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 86 | wins: 32 | win%: 37.2 | P&L: **-8.53 ZAR** | today: +23.35 | 7d: -8.53 | 30d: -8.53
- By exit: horizon +49.6, target +17.2, regime_shift -11.9, stop -63.5
- By entry regime (n/pnl): neutral 19/+11.7, bull 1/-3.8, bear 66/-16.4
- Top slices: feat_ext_strength:2:LONG:h15 8n/5w +21.75; feat_ret_10:2:LONG:h19 11n/5w +14.58; feat_trend_slope_20:2:LONG:h12 5n/5w +11.12; feat_ext_vs_ma_20:2:LONG:h15 5n/5w +9.35; feat_ret_20:2:LONG:h14 1n/1w +2.97
- Worst slices: feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; engine_mean_reversion:rsi:2:SELL:h10:ZECUSDC 2n/0w -6.66; engine_mean_reversion:bollinger:2:SELL:h10:ZECUSDC 1n/0w -4.93; feat_atr_norm_ext:2:LONG:h13 7n/0w -4.88
- Top pairs: ARBUSDC 3n +7.76; SUIUSDC 2n +7.67; AAVEUSDC 1n +7.32; WLDUSDC 2n +7.00; LINKUSDC 3n +6.68
- Worst pairs: ZECUSDC 4n -11.98; NEARUSDC 3n -8.75; XRPUSDC 4n -5.90; UNIUSDC 1n -4.19; PUMPUSDC 1n -3.88

### HIP3

- Closed: 29 | wins: 18 | win%: 62.1 | P&L: **+2.52 ZAR** | today: +5.24 | 7d: +2.52 | 30d: +2.52
- By exit: target +19.0, horizon +2.0, regime_shift +1.8, trail_stop +1.0, stop -21.3
- By entry regime (n/pnl): bull 12/+5.0, bear 8/+2.7, neutral 9/-5.2
- Top slices: hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 2n/2w +7.29; hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01
- Worst slices: hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30; hip3_para_equity_c0:feat_ext_vs_ma_10:0:SHORT:h17 1n/0w -1.80; hip3_para_equity_c0:feat_trend_strength_20:2:SHORT:h20 1n/0w -1.80; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h24 1n/0w -1.66
- Top pairs: PARA:CIEN 4n +9.17; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; PARA:MELI 3n +1.26; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRDO 2n -6.24; PARA:COHR 1n -3.47; PARA:IREN 1n -2.84; PARA:TER 1n -1.80; PARA:AVGO 1n -0.60

## 4. Open positions & risk

- **NATIVE**: 10 open, stop-risk **29.34 ZAR**
  - XMRUSDC BUY ntl=98 risk=3.91 bars=7 stop=494.3899999999999790 peak=514.9
  - SUIUSDC BUY ntl=99 risk=3.67 bars=3 stop=0.7232825000000000470 peak=0.75106
  - TRUMPUSDC BUY ntl=98 risk=3.50 bars=14 stop=1.878824999999999980 peak=1.9487
  - LINKUSDC BUY ntl=98 risk=3.42 bars=12 stop=10.969999999999999660 peak=11.366
  - XRPUSDC BUY ntl=99 risk=2.93 bars=2 stop=1.2665499999999999605 peak=1.305
  - SOLUSDC BUY ntl=98 risk=2.86 bars=6 stop=98.16725000000000310 peak=101.11
  - ETHUSDC BUY ntl=98 risk=2.67 bars=9 stop=2384.5500000000000205 peak=2451.2
  - DOGEUSDC BUY ntl=98 risk=2.64 bars=9 stop=0.07923699999999999735 peak=0.081432
  - BNBUSDC BUY ntl=98 risk=1.88 bars=6 stop=720.04750000000004875 peak=734.07
  - BTCUSDC BUY ntl=98 risk=1.86 bars=13 stop=75013.500000000000040 peak=76468.0

- **HIP3**: 6 open, stop-risk **15.83 ZAR**
  - PARA:RDDT SELL ntl=98 risk=3.44 bars=12 stop=156.8850000000000120 peak=151.57
  - PARA:COHR SELL ntl=98 risk=3.07 bars=14 stop=314.50749999999999095 peak=304.92
  - PARA:NET SELL ntl=99 risk=3.05 bars=8 stop=344.7099999999999605 peak=334.37
  - PARA:CRDO SELL ntl=98 risk=2.55 bars=14 stop=171.35750000000002975 peak=167.0
  - PARA:GLW SELL ntl=98 risk=2.02 bars=14 stop=155.95250000000000345 peak=152.8
  - PARA:AVGO SELL ntl=98 risk=1.71 bars=14 stop=355.982550 peak=349.86

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **45.18 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 194 | HIP-3: 25
- Native top (by paper P&L):
  - `feat_ret_10:2:LONG:h19` edge=0.0077 n=16875 p=0.0000 src=validated_walk_forward unproven=False paper=11n/+14.58
  - `feat_ext_strength:2:LONG:h15` edge=0.0072 n=16038 p=0.0016 src=validated_walk_forward unproven=False paper=7n/+14.44
  - `feat_trend_slope_20:2:LONG:h12` edge=0.0060 n=10596 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+11.12
  - `feat_trend_slope_20:2:LONG:h12` edge=0.0063 n=16968 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+11.12
  - `feat_ext_vs_ma_20:2:LONG:h15` edge=0.0060 n=10542 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+9.35
  - `feat_ext_vs_ma_20:2:LONG:h15` edge=0.0072 n=16809 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+9.35
  - `feat_vol_regime:2:LONG:h12` edge=0.0051 n=8773 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+7.60
  - `feat_vol_regime:2:LONG:h12` edge=0.0048 n=8815 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+7.60
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

- Closed paper trades: **29/50** | ghost rows: **178/50** | PnL: **+2.52 ZAR**
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

- Label: **neutral** | breadth bear=0.0 bull=0.4706 neutral=0.5294 | symbols=17
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bull | consecutive_bear: 0 / bull 0
- as_of: 2026-09-18T05:25:27Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 832 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+53.58 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-0.38 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **151/194** | hip3 **21/25**
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

- Latest scan 2026-09-18T04:23:01: errors=1 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=4
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 4, "pair_held": 122, "regime_blocked": 442, "skipped": 529, "slice_full": 0, "slot_full": 39})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=9
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:RDDT"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
