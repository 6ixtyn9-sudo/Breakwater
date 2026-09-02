# Breakwater daily print — 2026-09-02 23:51 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **367.21 ZAR** | high-water: **406.15 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **1969.86 ZAR** (seed 2000) | lifetime: **-30.14 ZAR** | closed: 3
- Today: 3 closed, **-30.14 ZAR**
- 7d: **-30.14 ZAR** | 30d: **-30.14 ZAR**

## 3. Lanes

### NATIVE

- Closed: 3 | wins: 0 | win%: 0.0 | P&L: **-30.14 ZAR** | today: -30.14 | 7d: -30.14 | 30d: -30.14
- By exit: horizon -10.1, stop -20.1
- By entry regime (n/pnl): neutral 1/-0.8, bull 1/-9.3, bear 1/-20.1
- Top slices: feat_ret_10:2:LONG:h15 1n/0w -0.76; feat_realized_vol_20:2:LONG:h13 1n/0w -9.32; feat_ret_5:0:LONG:h24 1n/0w -20.07
- Worst slices: feat_ret_5:0:LONG:h24 1n/0w -20.07; feat_realized_vol_20:2:LONG:h13 1n/0w -9.32; feat_ret_10:2:LONG:h15 1n/0w -0.76
- Top pairs: BNBUSDC 1n -0.76; XMRUSDC 1n -9.32; FARTCOINUSDC 1n -20.07
- Worst pairs: FARTCOINUSDC 1n -20.07; XMRUSDC 1n -9.32; BNBUSDC 1n -0.76

### HIP3

- Closed: 0 | wins: 0 | win%: 0.0 | P&L: **+0.00 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00

## 4. Open positions & risk

- **NATIVE**: 9 open, stop-risk **124.47 ZAR**
  - NEARUSDC BUY ntl=400 risk=18.46 bars=15 stop=1.77437499999999990 peak=1.8602
  - MONUSDC BUY ntl=400 risk=17.67 bars=15 stop=0.024780999999999998960 peak=0.025926
  - SUIUSDC BUY ntl=394 risk=16.90 bars=2 stop=0.7088275 peak=0.74059
  - HYPEUSDC BUY ntl=400 risk=13.61 bars=15 stop=79.54500000000000375 peak=82.347
  - XRPUSDC BUY ntl=396 risk=13.47 bars=3 stop=1.2975249999999998145 peak=1.3432
  - LINKUSDC BUY ntl=400 risk=12.05 bars=15 stop=10.877250000000000245 peak=11.215

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **124.47 / 137.89 ZAR | 96.8% | warning**
- Remaining: 4.4611 | cap skips: 14 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 0, "skipped": 0, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 0, "opened": 1, "pair_held": 46, "signals": 134, "skipped": 87, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **NEARUSDC** 18.4550 ZAR
- positions without bars: 0 | replayed: 9 | invalid: 0

## 6. Monitored books

- Native: 22 | HIP-3: 5
- Native top (by paper P&L):
  - `feat_trend_slope_20:2:LONG:h10` edge=0.0054 n=18264 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_50:2:LONG:h12` edge=0.0060 n=18027 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_vol_regime:2:LONG:h24` edge=0.0098 n=14910 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_10:2:LONG:h15` edge=0.0052 n=17891 p=0.0001 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_5:2:LONG:h18` edge=0.0059 n=17694 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_50:0:LONG:h19` edge=0.0053 n=12222 p=0.0001 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_1:0:LONG:h17` edge=0.0052 n=15893 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_3:0:LONG:h17` edge=0.0049 n=15326 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
- HIP-3 top (by paper P&L):
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24` edge=0.0019 n=7879 p=0.1394 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ret_20:0:LONG:h24` edge=0.0017 n=8311 p=0.2077 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_trend_slope_20:0:LONG:h24` edge=0.0019 n=8433 p=0.1035 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_atr_norm_ext:0:LONG:h24` edge=0.0012 n=9425 p=0.1928 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_equity_c0:feat_ext_vs_ma_20:0:LONG:h24` edge=0.0007 n=8450 p=0.5510 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **0/50** | ghost rows: **0/50** | PnL: **+0.00 ZAR**
- Gate verdict: **NOT READY**
- gate.json: paper_ready=True live_ready=False book_frozen=False book_rows=5
- live unresolved: market_classification_not_fully_authoritative, market_calendars_not_enforced, historical_oracle_quality_not_available, no_hip3_paper_evidence

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

- Label: **bear** | breadth bear=0.5333 bull=0.1333 neutral=0.3333 | symbols=30
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 61 / bull 0
- as_of: 2026-09-02T23:46:24Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 0 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6528 validated=6528 passing=0 eligible=344 best=223.0b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=3 pnl=-30.14 | frozen=NO
- HIP-3 lane: **RED** | closed=0 pnl=+0.00 | frozen=NO
- Frozen lanes: none
- Green islands kept alive inside red lanes: 0
- Slice blocks: 0

## 13. Signal activity

- Latest scan 2026-09-02T23:51:30: errors=0 signals=134 regime_blocked=137
- this cycle: closed=1 new_signals=134 skipped=87 slot_full=0 slice_full=0 pair_held=46
- Action funnel: regime_blocked=137 | lane_gate_blocked=0 | aggregate_risk_cap_skips=14 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=46 | slot_full=0 | skipped=87
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 14, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 0, "pair_held": 46, "regime_blocked": 137, "skipped": 87, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=False hip3_green=False frozen=none islands=0 blocks=0
- aggregate_risk: warning open=114.6445 cap=137.8899 used=0.9676 remaining=4.4611 replayed=9 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
