# Breakwater daily print — 2026-09-15 10:00 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **393.46 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **1998.03 ZAR** (seed 2000) | lifetime: **-1.97 ZAR** | closed: 16
- Today: 16 closed, **-1.97 ZAR**
- 7d: **-1.97 ZAR** | 30d: **-1.97 ZAR**

## 2b. Claimed vs realised

- Book: 610 slices (native 145 | hip3 465); validated pools: native 524 | hip3 732; book slices absent from pools: 48
  - absent: `feat_ext_vs_ma_50:1:LONG:h13` (native)
  - absent: `feat_ext_vs_ma_50:2:LONG:h14` (native)
  - absent: `feat_vol_trend:1:LONG:h14` (native)
  - absent: `feat_ext_strength:2:LONG:h15` (native)
  - absent: `feat_ext_vs_ma_50:2:LONG:h15` (native)
  - absent: `feat_vol_trend:1:LONG:h15` (native)
  - absent: `feat_realized_vol_20:1:LONG:h15` (native)
  - absent: `feat_ext_vs_ma_50:1:LONG:h15` (native)
  - absent: `feat_ext_strength:2:LONG:h16` (native)
  - absent: `feat_ext_vs_ma_50:2:LONG:h16` (native)
  - ... and 38 more
- Claimed edge (median mean_ret_costadj over 562 book slices present in the validated pools): +0.147% | at 100.10 ZAR mean notional/trade: +0.15 ZAR/trade
- Realised (16 real closes per lane_gate._is_real_close, net of fees): -0.12 ZAR/trade | INSUFFICIENT SAMPLE (n<30)
- Gap: not computed | verdict: INSUFFICIENT SAMPLE (n<30)
- native: claimed median +0.705% over 97/145 slices (pool 524) ~ +0.71 ZAR | realised 7 closes -0.70 ZAR sd 0.71 | INSUFFICIENT SAMPLE (n<30)
- hip3: claimed median +0.119% over 465/465 slices (pool 732) ~ +0.12 ZAR | realised 9 closes +0.32 ZAR sd 0.52 | INSUFFICIENT SAMPLE (n<30)
- Ledger: 6377 decision rows; 16 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 6361 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 7 | wins: 0 | win%: 0.0 | P&L: **-4.88 ZAR** | today: -4.88 | 7d: -4.88 | 30d: -4.88
- By exit: stop -2.2, horizon -2.7
- By entry regime (n/pnl): bear 2/-1.0, neutral 5/-3.9
- Top slices: feat_atr_norm_ext:2:LONG:h13 7n/0w -4.88
- Worst slices: feat_atr_norm_ext:2:LONG:h13 7n/0w -4.88
- Top pairs: ENAUSDC 1n -0.10; SOLUSDC 2n -0.74; KPEPEUSDC 1n -0.81; JUPUSDC 2n -1.01; BTCUSDC 1n -2.22
- Worst pairs: BTCUSDC 1n -2.22; JUPUSDC 2n -1.01; KPEPEUSDC 1n -0.81; SOLUSDC 2n -0.74; ENAUSDC 1n -0.10

### HIP3

- Closed: 9 | wins: 8 | win%: 88.9 | P&L: **+2.91 ZAR** | today: +2.91 | 7d: +2.91 | 30d: +2.91
- By exit: target +4.0, stop -1.1
- By entry regime (n/pnl): bull 8/+4.0, bear 1/-1.1
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 1n/0w -1.08
- Worst slices: hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 1n/0w -1.08; hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98
- Top pairs: XYZ:STRC 8n +3.98; XYZ:PALLADIUM 1n -1.08
- Worst pairs: XYZ:PALLADIUM 1n -1.08; XYZ:STRC 8n +3.98

## 4. Open positions & risk

- **NATIVE**: 5 open, stop-risk **21.60 ZAR**
  - NEARUSDC BUY ntl=87 risk=5.00 bars=0 stop=2.2467999999999997775 peak=2.3839
  - FILUSDC BUY ntl=91 risk=5.00 bars=1 stop=0.8385550000000000010 peak=0.88729
  - ZECUSDC BUY ntl=97 risk=5.00 bars=1 stop=1077.0250000000000175 peak=1135.3
  - XRPUSDC BUY ntl=100 risk=3.70 bars=1 stop=1.3395500000000000160 peak=1.3911
  - ETHUSDC BUY ntl=100 risk=2.90 bars=1 stop=2398.1249999999998425 peak=2469.7

- **HIP3**: 6 open, stop-risk **9.22 ZAR**
  - PARA:MELI SELL ntl=100 risk=2.89 bars=0 stop=1955.6999999999999990 peak=1900.7
  - XYZ:BRENTOIL BUY ntl=100 risk=1.78 bars=2 stop=100.81750000000000215 peak=102.64
  - XYZ:SILVER BUY ntl=100 risk=1.42 bars=2 stop=62.312499999999996790 peak=63.209
  - XYZ:PALLADIUM BUY ntl=100 risk=1.23 bars=0 stop=1259.8249999999999880 peak=1275.5
  - XYZ:NATGAS BUY ntl=100 risk=1.18 bars=2 stop=3.0126500000000001925 peak=3.0487
  - XYZ:COPPER BUY ntl=100 risk=0.72 bars=2 stop=6.333150000000000090 peak=6.3793

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **30.82 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **30.82 / 139.97 ZAR | 23.9% | ok**
- Remaining: 106.4583 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 779, "skipped": 0, "slice_full": 0, "slot_full": 779}, "native": {"lane_gate_blocked": 0, "opened": 1, "pair_held": 22, "signals": 573, "skipped": 550, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **ZECUSDC** 4.9990 ZAR
- positions without bars: 2 | replayed: 8 | invalid: 0

## 6. Monitored books

- Native: 145 | HIP-3: 465
- Native top (by paper P&L):
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0058 n=17004 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+5.56
  - `feat_trend_slope_20:2:LONG:h12` edge=0.0063 n=16968 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_20:2:LONG:h12` edge=0.0053 n=17135 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_trend_slope_20:2:LONG:h13` edge=0.0068 n=16931 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_20:2:LONG:h13` edge=0.0057 n=17086 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_50:1:LONG:h13` edge=0.0014 n=11294 p=0.2307 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_trend_slope_20:2:LONG:h14` edge=0.0071 n=16890 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_20:2:LONG:h14` edge=0.0067 n=16847 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
- HIP-3 top (by paper P&L):
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h6` edge=0.0049 n=505 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h8` edge=0.0070 n=503 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h8` edge=0.0047 n=295 p=0.0022 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h9` edge=0.0082 n=502 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h9` edge=0.0054 n=295 p=0.0151 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h10` edge=0.0094 n=501 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` edge=0.0108 n=499 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h12` edge=0.0117 n=497 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **9/50** | ghost rows: **9/50** | PnL: **+2.91 ZAR**
- Gate verdict: **NOT READY**

## 8. Research / honesty checks

- Latest research: 2026-09-15T06:24:56+00:00 | discovered 4608 | validated 309 | reg-confounded 3633 | hostile-unproven 0
- floors: {"PERP": "75.9", "SPOT": "140.0"} | book: {"blocked_for_green_breadth": 0, "carried_cooldown": 0, "carried_decayed": 0, "carried_kinds": [], "carried_monitored": 0, "carried_total": 0, "concentrated": 0, "cooldown": 0, "decayed": 1, "families_considered": 22, "families_promoted": 19, "green_assets_total": 622, "monitored": 18, "multi_horizon_min_passes": 2, "multi_horizon_select": "edge_per_bar", "net_edge_floor_enter_bps": {"PERP": "75.9", "SPOT": "140.0"}, "net_edge_floor_keep_bps": {"PERP": "57.9", "SPOT": "140.0"}, "paper_protected": 2, "per_asset_aware": true, "promotable": 145, "promoted_green_fraction_mean": 0.2761, "rows_total_after_sync": 21, "session_gate_blocked": 0, "validated": 309}
- Short audit: discovered=2304 validated=2304 passing=0 eligible=0 best=-6.6b best_fail=temporal_pass,direction_ok,breadth_ok,mean_net<=0
- pair_errors: []
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

- Label: **bear** | breadth bear=0.5333 bull=0.0667 neutral=0.3667 | symbols=29
- confirmed_bear: **True** | confirmed_bull: **False** | flip: **True** | flipped_from: bear | consecutive_bear: 6 / bull 0
- as_of: 2026-09-15T09:30:31Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **True** | promote_env: ON
- candidates: 2088 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=365 eligible=530 best=208.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=7 pnl=-4.88 | frozen=NO
- HIP-3 lane: **RED** | closed=9 pnl=+2.91 | frozen=NO
- Frozen lanes: none
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 0
- Tradable slices: native **145/145** | hip3 **465/465**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 1
  - `feat_atr_norm_ext:2:LONG:h13` slice_pnl=-4.88

## 13. Signal activity

- Latest scan 2026-09-15T09:23:01: errors=0 signals=None regime_blocked=2271
- this cycle: closed=0 new_signals=1352 skipped=550 slot_full=779 slice_full=0 pair_held=22
- Action funnel: regime_blocked=2271 | lane_gate_blocked=0 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=22 | slot_full=779 | skipped=550
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 0, "pair_held": 22, "regime_blocked": 2271, "skipped": 550, "slice_full": 0, "slot_full": 779})
- green_gate: native_green=False hip3_green=False frozen=none islands=0 blocks=1
- aggregate_risk: ok open=25.8252 cap=139.9711 used=0.2394 remaining=106.4583 replayed=8 no_new_bars=2
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
