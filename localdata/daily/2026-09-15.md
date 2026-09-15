# Breakwater daily print — 2026-09-15 19:29 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **384.47 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2008.03 ZAR** (seed 2000) | lifetime: **+8.03 ZAR** | closed: 20
- Today: 20 closed, **+8.03 ZAR**
- 7d: **+8.03 ZAR** | 30d: **+8.03 ZAR**

## 2b. Claimed vs realised

- Book: 531 slices (native 66 | hip3 465); validated pools: native 0 | hip3 732; book slices absent from pools: 66
  - absent: `feat_trend_slope_20:2:LONG:h11` (native)
  - absent: `feat_trend_slope_20:2:LONG:h12` (native)
  - absent: `feat_trend_slope_20:2:LONG:h13` (native)
  - absent: `feat_trend_slope_20:2:LONG:h14` (native)
  - absent: `feat_ext_vs_ma_20:2:LONG:h14` (native)
  - absent: `feat_ext_vs_ma_50:2:LONG:h14` (native)
  - absent: `feat_ret_20:2:LONG:h14` (native)
  - absent: `feat_realized_vol_20:2:LONG:h14` (native)
  - absent: `feat_atr_norm_ext:2:LONG:h15` (native)
  - absent: `feat_trend_slope_20:2:LONG:h15` (native)
  - ... and 56 more
- Claimed edge (median mean_ret_costadj over 465 book slices present in the validated pools): +0.119% | at 99.71 ZAR mean notional/trade: +0.12 ZAR/trade
- Realised (20 real closes per lane_gate._is_real_close, net of fees): +0.40 ZAR/trade | INSUFFICIENT SAMPLE (n<30)
- Gap: not computed | verdict: INSUFFICIENT SAMPLE (n<30)
- native: claimed unknown (0/66 slices in pool 0) | realised 9 closes +0.23 ZAR sd 3.76 | INSUFFICIENT SAMPLE (n<30)
- hip3: claimed median +0.119% over 465/465 slices (pool 732) ~ +0.12 ZAR | realised 11 closes +0.54 ZAR sd 0.72 | INSUFFICIENT SAMPLE (n<30)
- Ledger: 17461 decision rows; 20 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 17441 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 9 | wins: 1 | win%: 11.1 | P&L: **+2.05 ZAR** | today: +2.05 | 7d: +2.05 | 30d: +2.05
- By exit: target +9.9, horizon -2.7, stop -5.2
- By entry regime (n/pnl): bear 3/+8.9, neutral 6/-6.9
- Top slices: feat_ret_10:2:LONG:h19 1n/1w +9.91; feat_realized_vol_20:2:LONG:h24 1n/0w -2.99; feat_atr_norm_ext:2:LONG:h13 7n/0w -4.88
- Worst slices: feat_atr_norm_ext:2:LONG:h13 7n/0w -4.88; feat_realized_vol_20:2:LONG:h24 1n/0w -2.99; feat_ret_10:2:LONG:h19 1n/1w +9.91
- Top pairs: ARBUSDC 1n +9.91; ENAUSDC 1n -0.10; SOLUSDC 2n -0.74; KPEPEUSDC 1n -0.81; JUPUSDC 2n -1.01
- Worst pairs: ETHUSDC 1n -2.99; BTCUSDC 1n -2.22; JUPUSDC 2n -1.01; KPEPEUSDC 1n -0.81; SOLUSDC 2n -0.74

### HIP3

- Closed: 11 | wins: 10 | win%: 90.9 | P&L: **+5.98 ZAR** | today: +5.98 | 7d: +5.98 | 30d: +5.98
- By exit: target +4.0, horizon +2.1, trail_stop +1.0, stop -1.1
- By entry regime (n/pnl): bull 8/+4.0, bear 3/+2.0
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 1n/1w +2.05; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 1n/0w -1.08
- Worst slices: hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 1n/0w -1.08; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 1n/1w +2.05; hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98
- Top pairs: XYZ:STRC 8n +3.98; PARA:MELI 1n +2.05; XYZ:PALLADIUM 2n -0.05
- Worst pairs: XYZ:PALLADIUM 2n -0.05; PARA:MELI 1n +2.05; XYZ:STRC 8n +3.98

## 4. Open positions & risk

- **NATIVE**: 8 open, stop-risk **33.36 ZAR**
  - NEARUSDC BUY ntl=87 risk=5.00 bars=8 stop=2.2467999999999997775 peak=2.3839
  - FILUSDC BUY ntl=91 risk=5.00 bars=9 stop=0.8385550000000000010 peak=0.88729
  - ZECUSDC BUY ntl=97 risk=5.00 bars=9 stop=1077.0250000000000175 peak=1135.3
  - TRUMPUSDC BUY ntl=100 risk=4.87 bars=0 stop=1.8895000000000000045 peak=1.9858
  - HYPEUSDC BUY ntl=100 risk=4.30 bars=1 stop=73.40625000000000455 peak=76.691
  - XRPUSDC BUY ntl=100 risk=3.70 bars=9 stop=1.3395500000000000160 peak=1.3911
  - ETHUSDC BUY ntl=100 risk=3.28 bars=1 stop=2342.225000000000085 peak=2421.2
  - BNBUSDC BUY ntl=100 risk=2.21 bars=0 stop=707.15500000000001725 peak=723.05

- **HIP3**: 6 open, stop-risk **5.86 ZAR**
  - XYZ:BRENTOIL BUY ntl=100 risk=1.78 bars=10 stop=100.81750000000000215 peak=102.64
  - XYZ:SILVER BUY ntl=100 risk=1.42 bars=10 stop=62.312499999999996790 peak=63.209
  - XYZ:NATGAS BUY ntl=100 risk=1.18 bars=10 stop=3.0126500000000001925 peak=3.0487
  - PARA:AVGO SELL ntl=100 risk=0.94 bars=1 stop=345.24999999999999390 peak=342.04
  - PARA:MELI SELL ntl=100 risk=0.55 bars=4 stop=1870.17500000000001210 peak=1860.0
  - XYZ:COPPER BUY ntl=100 risk=0.00 bars=10 stop=6.4019500000000000900 peak=6.4481

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **39.23 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **39.23 / 140.67 ZAR | 30.3% | ok**
- Remaining: 97.9996 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 1672, "skipped": 0, "slice_full": 0, "slot_full": 1672}, "native": {"lane_gate_blocked": 0, "opened": 2, "pair_held": 27, "signals": 198, "skipped": 169, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **ZECUSDC** 4.9990 ZAR
- positions without bars: 1 | replayed: 14 | invalid: 0

## 6. Monitored books

- Native: 66 | HIP-3: 465
- Native top (by paper P&L):
  - `feat_ret_10:2:LONG:h19` edge=0.0077 n=16875 p=0.0000 src=validated_walk_forward unproven=False paper=1n/+9.91
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0058 n=17004 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+5.56
  - `feat_trend_slope_20:2:LONG:h12` edge=0.0063 n=16968 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_trend_slope_20:2:LONG:h13` edge=0.0068 n=16931 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_trend_slope_20:2:LONG:h14` edge=0.0071 n=16890 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_20:2:LONG:h14` edge=0.0067 n=16847 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ext_vs_ma_50:2:LONG:h14` edge=0.0064 n=16441 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `feat_ret_20:2:LONG:h14` edge=0.0060 n=17052 p=0.0000 src=validated_walk_forward unproven=False paper=0n/+0.00
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

- Closed paper trades: **11/50** | ghost rows: **33/50** | PnL: **+5.98 ZAR**
- Gate verdict: **NOT READY**

## 8. Research / honesty checks

- Latest research: 2026-09-15T10:13:03+00:00 | discovered 4608 | validated 0 | reg-confounded 3638 | hostile-unproven 0
- floors: {"PERP": "75.7", "SPOT": "140.0"} | book: {"blocked_for_green_breadth": 0, "carried_cooldown": 0, "carried_decayed": 0, "carried_kinds": ["PERP"], "carried_monitored": 67, "carried_total": 67, "concentrated": 0, "cooldown": 0, "decayed": 0, "families_considered": 0, "families_promoted": 0, "green_assets_total": 0, "monitored": 0, "multi_horizon_min_passes": 2, "multi_horizon_select": "edge_per_bar", "net_edge_floor_enter_bps": {"PERP": "75.7", "SPOT": "140.0"}, "net_edge_floor_keep_bps": {"PERP": "57.8", "SPOT": "140.0"}, "paper_protected": 0, "per_asset_aware": true, "promotable": 0, "promoted_green_fraction_mean": null, "rows_total_after_sync": 67, "session_gate_blocked": 0, "validated": 0}
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

- Label: **bear** | breadth bear=0.5 bull=0.0 neutral=0.5 | symbols=14
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 1 / bull 0
- as_of: 2026-09-15T19:25:39Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 2304 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=365 eligible=530 best=208.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=9 pnl=+2.05 | frozen=NO
- HIP-3 lane: **GREEN** | closed=11 pnl=+5.98 | frozen=NO
- Frozen lanes: none
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 0
- Tradable slices: native **66/66** | hip3 **465/465**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 1
  - `feat_atr_norm_ext:2:LONG:h13` slice_pnl=-4.88

## 13. Signal activity

- Latest scan 2026-09-15T18:39:07: errors=2 signals=None regime_blocked=None
- this cycle: closed=0 new_signals=1870 skipped=169 slot_full=1672 slice_full=0 pair_held=27
- Action funnel: lane_gate_blocked=0 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=27 | slot_full=1672 | skipped=169
- **NO ACTION:** dominant blocker = `slot_full` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 0, "pair_held": 27, "regime_blocked": 616, "skipped": 169, "slice_full": 0, "slot_full": 1672})
- green_gate: native_green=False hip3_green=True frozen=none islands=0 blocks=1
- aggregate_risk: ok open=32.1466 cap=140.6713 used=0.3033 remaining=97.9996 replayed=14 no_new_bars=1
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:EWT"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:NFLX"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
