# Breakwater daily print — 2026-09-14 15:01 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **391.31 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2000.00 ZAR** (seed 2000) | lifetime: **+0.00 ZAR** | closed: 0
- Today: 0 closed, **+0.00 ZAR**
- 7d: **+0.00 ZAR** | 30d: **+0.00 ZAR**

## 2b. Claimed vs realised

- Book: 38 slices (native 31 | hip3 7); validated pools: native 524 | hip3 349; book slices absent from pools: 0
- Claimed edge (median mean_ret_costadj over 38 book slices present in the validated pools): +0.490% | at 0.00 ZAR mean notional/trade: +0.00 ZAR/trade
- Realised (0 real closes per lane_gate._is_real_close, net of fees): no real closes | INSUFFICIENT SAMPLE (n<30)
- Gap: not computed | verdict: INSUFFICIENT SAMPLE (n<30)
- native: claimed median +0.525% over 31/31 slices (pool 524) ~ +0.00 ZAR | 0 real closes | INSUFFICIENT SAMPLE (n<30)
- hip3: claimed median +0.148% over 7/7 slices (pool 349) ~ +0.00 ZAR | 0 real closes | INSUFFICIENT SAMPLE (n<30)
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

- Native: 31 | HIP-3: 7
- Native top (by paper P&L):
  - `feat_ext_vs_ma_10:2:LONG:h15` edge=0.0067 n=17389 p=0.0000 src=validated_walk_forward unproven=False paper=4n/+21.09
  - `feat_ret_5:2:LONG:h19` edge=0.0079 n=17246 p=0.0000 src=validated_walk_forward unproven=False paper=7n/+14.88
  - `feat_atr_norm_ext:2:LONG:h13` edge=0.0077 n=15915 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+6.92
  - `feat_ret_3:1:LONG:h24` edge=0.0044 n=12367 p=0.0000 src=validated_walk_forward unproven=False paper=1n/+5.54
  - `feat_ret_1:0:LONG:h18` edge=0.0067 n=16176 p=0.0000 src=validated_walk_forward unproven=False paper=1n/+5.20
  - `feat_ret_5:0:LONG:h16` edge=0.0049 n=15411 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+3.41
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0065 n=17661 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+2.06
  - `feat_ret_3:0:LONG:h14` edge=0.0049 n=15653 p=0.0000 src=validated_walk_forward unproven=False paper=1n/+1.65
- HIP-3 top (by paper P&L):
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h11` edge=0.0015 n=1337 p=0.2087 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` edge=0.0047 n=1222 p=0.0019 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ret_20:2:SHORT:h21` edge=0.0013 n=9563 p=0.1102 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` edge=0.0015 n=9627 p=0.0640 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_vol_regime:2:SHORT:h19` edge=0.0031 n=10325 p=0.0003 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_50:2:SHORT:h21` edge=0.0005 n=9330 p=0.3050 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_20:2:SHORT:h24` edge=0.0004 n=9612 p=0.3907 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **0/50** | ghost rows: **0/50** | PnL: **+0.00 ZAR**
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

- Label: **neutral** | breadth bear=0.3333 bull=0.0333 neutral=0.6333 | symbols=30
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from:  | consecutive_bear: 0 / bull 0
- as_of: 2026-09-14T14:30:33Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 1872 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6528 validated=6528 passing=104 eligible=366 best=543.2b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=0 pnl=+0.00 | frozen=NO
- HIP-3 lane: **RED** | closed=0 pnl=+0.00 | frozen=NO
- Frozen lanes: none
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 0
- Tradable slices: native **31/31** | hip3 **7/7**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 0

## 13. Signal activity

- Latest scan 2026-09-11T03:39:51: errors=0 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=2
- green_gate: native_green=False hip3_green=False frozen=hip3,native islands=2 blocks=13
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
