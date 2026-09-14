# Breakwater daily print — 2026-09-14 15:47 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **403.23 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2000.00 ZAR** (seed 2000) | lifetime: **+0.00 ZAR** | closed: 0
- Today: 0 closed, **+0.00 ZAR**
- 7d: **+0.00 ZAR** | 30d: **+0.00 ZAR**

## 2b. Claimed vs realised

- Book: 22 slices (native 5 | hip3 17); validated pools: native 0 | hip3 464; book slices absent from pools: 5
  - absent: `feat_atr_norm_ext:2:LONG:h15` (native)
  - absent: `feat_ret_10:2:LONG:h15` (native)
  - absent: `feat_ret_5:2:LONG:h19` (native)
  - absent: `feat_ret_3:2:LONG:h19` (native)
  - absent: `feat_atr_norm_ext:2:LONG:h13` (native)
- Claimed edge (median mean_ret_costadj over 17 book slices present in the validated pools): +0.085% | at 0.00 ZAR mean notional/trade: +0.00 ZAR/trade
- Realised (0 real closes per lane_gate._is_real_close, net of fees): no real closes | INSUFFICIENT SAMPLE (n<30)
- Gap: not computed | verdict: INSUFFICIENT SAMPLE (n<30)
- native: claimed unknown (0/5 slices in pool 0) | 0 real closes | INSUFFICIENT SAMPLE (n<30)
- hip3: claimed median +0.085% over 17/17 slices (pool 464) ~ +0.00 ZAR | 0 real closes | INSUFFICIENT SAMPLE (n<30)
- Ledger: 0 decision rows; 0 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 0 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 0 | wins: 0 | win%: 0.0 | P&L: **+0.00 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00

### HIP3

- Closed: 0 | wins: 0 | win%: 0.0 | P&L: **+0.00 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00

## 4. Open positions & risk

- **NATIVE**: 0 open, stop-risk **0.00 ZAR**

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **0.00 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 5 | HIP-3: 17
- Native top (by paper P&L):
  - `feat_ret_5:2:LONG:h19` edge=0.0079 n=17246 p=0.0000 src=validated_walk_forward unproven=False paper=7n/+14.88
  - `feat_atr_norm_ext:2:LONG:h13` edge=0.0077 n=15915 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+6.92
  - `feat_ret_10:2:LONG:h15` edge=0.0078 n=17576 p=0.0000 src=validated_walk_forward unproven=False paper=4n/+0.74
  - `feat_ret_3:2:LONG:h19` edge=0.0072 n=17204 p=0.0000 src=validated_walk_forward unproven=False paper=6n/-21.89
  - `feat_atr_norm_ext:2:LONG:h15` edge=0.0085 n=15663 p=0.0000 src=validated_walk_forward unproven=False paper=5n/-35.61
- HIP-3 top (by paper P&L):
  - `hip3_xyz_equity_c0:feat_vol_regime:1:LONG:h24` edge=0.0057 n=8724 p=0.0001 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_atr_norm_ext:1:LONG:h16` edge=0.0011 n=9676 p=0.1282 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_trend_strength_20:0:LONG:h22` edge=0.0015 n=9595 p=0.0308 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_20:1:LONG:h16` edge=0.0008 n=11431 p=0.1760 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_realized_vol_20:0:LONG:h18` edge=0.0008 n=12593 p=0.2498 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_realized_vol_20:1:LONG:h24` edge=0.0017 n=10604 p=0.1017 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ret_20:1:LONG:h19` edge=0.0012 n=11409 p=0.0525 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_10:1:LONG:h20` edge=0.0008 n=12127 p=0.1730 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **0/50** | ghost rows: **0/50** | PnL: **+0.00 ZAR**
- Gate verdict: **NOT READY**

## 8. Research / honesty checks

- Latest research: 2026-09-14T14:35:30+00:00 | discovered 3744 | validated 0 | reg-confounded 3041 | hostile-unproven 0
- floors: {"PERP": "86.2", "SPOT": "140.0"} | book: {"blocked_for_green_breadth": 0, "carried_cooldown": 0, "carried_decayed": 1, "carried_kinds": ["PERP"], "carried_monitored": 5, "carried_total": 6, "concentrated": 0, "cooldown": 0, "decayed": 0, "families_considered": 0, "families_promoted": 0, "green_assets_total": 0, "monitored": 0, "multi_horizon_min_passes": 2, "multi_horizon_select": "edge_per_bar", "net_edge_floor_enter_bps": {"PERP": "86.2", "SPOT": "140.0"}, "net_edge_floor_keep_bps": {"PERP": "71.2", "SPOT": "140.0"}, "paper_protected": 0, "per_asset_aware": true, "promotable": 0, "promoted_green_fraction_mean": null, "rows_total_after_sync": 6, "session_gate_blocked": 0, "validated": 0}
- Short audit: discovered=1872 validated=1872 passing=0 eligible=0 best=-7.2b best_fail=temporal_pass,direction_ok,breadth_ok,regime_confounded,mean_net<=0
- pair_errors: [{"error": "HTTPError: 500 Server Error: Internal Server Error for url: https://api.hyperliquid.xyz/info", "pair": "KBONKUSDC"}]
- Deep audit: candidates=37440 preliminary_passes=0 audit_passes=0 plateaus=0 fetch_errors=25

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

- Label: **unknown** | breadth bear=0 bull=0 neutral=0 | symbols=0
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: None | consecutive_bear: 0 / bull 0
- as_of: None
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 0 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=5616 validated=5616 passing=0 eligible=205 best=198.2b best_fail=breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=0 pnl=+0.00 | frozen=NO
- HIP-3 lane: **RED** | closed=0 pnl=+0.00 | frozen=NO
- Frozen lanes: none
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 0
- Tradable slices: native **5/5** | hip3 **17/17**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 0

## 13. Signal activity

- Latest scan 2026-09-14T14:09:46: errors=4 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=10
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 17, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 10, "pair_held": 26, "regime_blocked": 198, "skipped": 277, "slice_full": 0, "slot_full": 104})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=1 blocks=21
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:DKNG"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:EBAY"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:RDDT"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:ZM"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
