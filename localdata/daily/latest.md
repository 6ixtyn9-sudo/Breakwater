# Breakwater daily print — 2026-09-15 04:02 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **393.23 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2002.84 ZAR** (seed 2000) | lifetime: **+2.84 ZAR** | closed: 9
- Today: 9 closed, **+2.84 ZAR**
- 7d: **+2.84 ZAR** | 30d: **+2.84 ZAR**

## 2b. Claimed vs realised

- Book: 14 slices (native 5 | hip3 9); validated pools: native 0 | hip3 11; book slices absent from pools: 5
  - absent: `feat_atr_norm_ext:2:LONG:h15` (native)
  - absent: `feat_ret_10:2:LONG:h15` (native)
  - absent: `feat_ret_5:2:LONG:h19` (native)
  - absent: `feat_ret_3:2:LONG:h19` (native)
  - absent: `feat_atr_norm_ext:2:LONG:h13` (native)
- Claimed edge (median mean_ret_costadj over 9 book slices present in the validated pools): +0.057% | at 100.00 ZAR mean notional/trade: +0.06 ZAR/trade
- Realised (9 real closes per lane_gate._is_real_close, net of fees): +0.32 ZAR/trade | INSUFFICIENT SAMPLE (n<30)
- Gap: not computed | verdict: INSUFFICIENT SAMPLE (n<30)
- native: claimed unknown (0/5 slices in pool 0) | realised 2 closes -0.32 ZAR sd 0.01 | INSUFFICIENT SAMPLE (n<30)
- hip3: claimed median +0.057% over 9/9 slices (pool 11) ~ +0.06 ZAR | realised 7 closes +0.50 ZAR sd 0.00 | INSUFFICIENT SAMPLE (n<30)
- Ledger: 1157 decision rows; 9 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 1148 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 2 | wins: 0 | win%: 0.0 | P&L: **-0.64 ZAR** | today: -0.64 | 7d: -0.64 | 30d: -0.64
- By exit: horizon -0.6
- By entry regime (n/pnl): neutral 1/-0.3, bear 1/-0.3
- Top slices: feat_atr_norm_ext:2:LONG:h13 2n/0w -0.64
- Worst slices: feat_atr_norm_ext:2:LONG:h13 2n/0w -0.64
- Top pairs: SOLUSDC 1n -0.32; JUPUSDC 1n -0.33
- Worst pairs: JUPUSDC 1n -0.33; SOLUSDC 1n -0.32

### HIP3

- Closed: 7 | wins: 7 | win%: 100.0 | P&L: **+3.48 ZAR** | today: +3.48 | 7d: +3.48 | 30d: +3.48
- By exit: target +3.5
- By entry regime (n/pnl): bull 7/+3.5
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 7n/7w +3.48
- Worst slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 7n/7w +3.48
- Top pairs: XYZ:STRC 7n +3.48
- Worst pairs: XYZ:STRC 7n +3.48

## 4. Open positions & risk

- **NATIVE**: 12 open, stop-risk **61.27 ZAR**
  - WLDUSDC BUY ntl=194 risk=10.15 bars=1 stop=0.3699825000000000015 peak=0.39041
  - INJUSDC BUY ntl=181 risk=10.15 bars=1 stop=5.990850000000000120 peak=6.3458
  - FARTCOINUSDC BUY ntl=185 risk=10.15 bars=1 stop=0.13784999999999999745 peak=0.14586
  - LINKUSDC BUY ntl=203 risk=7.54 bars=1 stop=11.275250000000000715 peak=11.71
  - ENAUSDC BUY ntl=100 risk=4.90 bars=6 stop=0.1347025000000000005 peak=0.14164
  - JUPUSDC BUY ntl=100 risk=4.47 bars=7 stop=0.2266600000000000090 peak=0.23726
  - ETHUSDC BUY ntl=102 risk=3.33 bars=1 stop=2474.224999999999770 peak=2558.1
  - KPEPEUSDC BUY ntl=100 risk=3.11 bars=6 stop=0.003371749999999999855 peak=0.00348
  - DOGEUSDC BUY ntl=102 risk=3.04 bars=1 stop=0.0822045000000000045 peak=0.084743
  - SOLUSDC BUY ntl=100 risk=2.31 bars=7 stop=99.4602499999999960 peak=101.81
  - BTCUSDC BUY ntl=102 risk=2.13 bars=1 stop=77262.75000000000005 peak=78919.0
  - UNIUSDC BUY ntl=197 risk=0.00 bars=6 stop=6.3999499999999999750 peak=6.7235

- **HIP3**: 5 open, stop-risk **6.85 ZAR**
  - XYZ:AVGO SELL ntl=100 risk=2.13 bars=6 stop=354.34500000000002395 peak=346.95
  - XYZ:AMZN SELL ntl=100 risk=1.83 bars=6 stop=258.29249999999999080 peak=253.65
  - XYZ:BABA SELL ntl=100 risk=1.65 bars=6 stop=111.54500000000000465 peak=109.73
  - XYZ:COST SELL ntl=100 risk=0.94 bars=6 stop=926.8850000000000470 peak=918.28
  - XYZ:STRC SELL ntl=100 risk=0.29 bars=6 stop=98.98699999999999560 peak=98.697

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **68.12 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 5 | HIP-3: 9
- Native top (by paper P&L):
  - `feat_ret_5:2:LONG:h19` edge=0.0079 n=17246 p=0.0000 src=validated_walk_forward unproven=False paper=7n/+14.88
  - `feat_atr_norm_ext:2:LONG:h13` edge=0.0077 n=15915 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+6.27
  - `feat_ret_10:2:LONG:h15` edge=0.0078 n=17576 p=0.0000 src=validated_walk_forward unproven=False paper=4n/+0.74
  - `feat_ret_3:2:LONG:h19` edge=0.0072 n=17204 p=0.0000 src=validated_walk_forward unproven=False paper=6n/-21.89
  - `feat_atr_norm_ext:2:LONG:h15` edge=0.0085 n=15663 p=0.0000 src=validated_walk_forward unproven=False paper=5n/-35.61
- HIP-3 top (by paper P&L):
  - `hip3_xyz_commodity_c0:feat_atr_norm_ext:2:LONG:h17` edge=0.0002 n=1176 p=0.8999 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_atr_norm_ext:2:LONG:h19` edge=0.0005 n=1170 p=0.7217 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_atr_norm_ext:2:LONG:h20` edge=0.0006 n=1167 p=0.6600 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_atr_norm_ext:2:LONG:h21` edge=0.0007 n=1166 p=0.6123 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_atr_norm_ext:2:LONG:h22` edge=0.0007 n=1163 p=0.5836 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_atr_norm_ext:2:LONG:h23` edge=0.0009 n=1160 p=0.5480 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ext_vs_ma_20:2:LONG:h23` edge=0.0003 n=1126 p=0.9632 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_atr_norm_ext:2:LONG:h24` edge=0.0010 n=1157 p=0.5055 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **7/50** | ghost rows: **0/50** | PnL: **+3.48 ZAR**
- Gate verdict: **NOT READY**

## 8. Research / honesty checks

- Latest research: 2026-09-15T00:10:28+00:00 | discovered 4608 | validated 0 | reg-confounded 3614 | hostile-unproven 0
- floors: {"PERP": "82.8", "SPOT": "140.0"} | book: {"blocked_for_green_breadth": 0, "carried_cooldown": 0, "carried_decayed": 1, "carried_kinds": ["PERP"], "carried_monitored": 5, "carried_total": 6, "concentrated": 0, "cooldown": 0, "decayed": 0, "families_considered": 0, "families_promoted": 0, "green_assets_total": 0, "monitored": 0, "multi_horizon_min_passes": 2, "multi_horizon_select": "edge_per_bar", "net_edge_floor_enter_bps": {"PERP": "82.8", "SPOT": "140.0"}, "net_edge_floor_keep_bps": {"PERP": "63.8", "SPOT": "140.0"}, "paper_protected": 0, "per_asset_aware": true, "promotable": 0, "promoted_green_fraction_mean": null, "rows_total_after_sync": 6, "session_gate_blocked": 0, "validated": 0}
- Short audit: discovered=2304 validated=2304 passing=0 eligible=0 best=nanb best_fail=temporal_pass,breadth_ok,mean_net<=0
- pair_errors: [{"error": "HTTPError: 500 Server Error: Internal Server Error for url: https://api.hyperliquid.xyz/info", "pair": "KBONKUSDC"}]
- Deep audit: candidates=46080 preliminary_passes=0 audit_passes=0 plateaus=0 fetch_errors=27

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

- Label: **neutral** | breadth bear=0.303 bull=0.0606 neutral=0.6061 | symbols=32
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from:  | consecutive_bear: 0 / bull 0
- as_of: 2026-09-15T04:00:29Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 2304 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=0 eligible=0 best=30.3b best_fail=breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=2 pnl=-0.64 | frozen=NO
- HIP-3 lane: **RED** | closed=7 pnl=+3.48 | frozen=NO
- Frozen lanes: none
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 0
- Tradable slices: native **5/5** | hip3 **9/9**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 0

## 13. Signal activity

- Latest scan 2026-09-11T23:39:32: errors=1 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=5
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 5, "pair_held": 34, "regime_blocked": 573, "skipped": 108, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=False hip3_green=True frozen=native islands=3 blocks=15
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:XBI"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
