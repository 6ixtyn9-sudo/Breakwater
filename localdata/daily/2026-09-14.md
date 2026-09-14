# Breakwater daily print — 2026-09-14 16:56 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **403.32 ZAR** | high-water: **435.05 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2000.00 ZAR** (seed 2000) | lifetime: **+0.00 ZAR** | closed: 0
- Today: 0 closed, **+0.00 ZAR**
- 7d: **+0.00 ZAR** | 30d: **+0.00 ZAR**

## 2b. Claimed vs realised

- Book: 12 slices (native 5 | hip3 7); validated pools: native 0 | hip3 349; book slices absent from pools: 5
  - absent: `feat_atr_norm_ext:2:LONG:h15` (native)
  - absent: `feat_ret_10:2:LONG:h15` (native)
  - absent: `feat_ret_5:2:LONG:h19` (native)
  - absent: `feat_ret_3:2:LONG:h19` (native)
  - absent: `feat_atr_norm_ext:2:LONG:h13` (native)
- Claimed edge (median mean_ret_costadj over 7 book slices present in the validated pools): +0.148% | at 0.00 ZAR mean notional/trade: +0.00 ZAR/trade
- Realised (0 real closes per lane_gate._is_real_close, net of fees): no real closes | INSUFFICIENT SAMPLE (n<30)
- Gap: not computed | verdict: INSUFFICIENT SAMPLE (n<30)
- native: claimed unknown (0/5 slices in pool 0) | 0 real closes | INSUFFICIENT SAMPLE (n<30)
- hip3: claimed median +0.148% over 7/7 slices (pool 349) ~ +0.00 ZAR | 0 real closes | INSUFFICIENT SAMPLE (n<30)
- Ledger: 441 decision rows; 0 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 441 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 0 | wins: 0 | win%: 0.0 | P&L: **+0.00 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00

### HIP3

- Closed: 0 | wins: 0 | win%: 0.0 | P&L: **+0.00 ZAR** | today: +0.00 | 7d: +0.00 | 30d: +0.00

## 4. Open positions & risk

- **NATIVE**: 19 open, stop-risk **77.84 ZAR**
  - UNIUSDC BUY ntl=197 risk=10.00 bars=0 stop=6.045149999999999975 peak=6.3687
  - TAOUSDC BUY ntl=200 risk=7.22 bars=1 stop=224.20000000000000175 peak=232.6
  - INJUSDC BUY ntl=95 risk=5.00 bars=1 stop=5.855224999999999825 peak=6.1788
  - ASTERUSDC BUY ntl=200 risk=4.99 bars=1 stop=0.6782624999999999730 peak=0.69562
  - ENAUSDC BUY ntl=100 risk=4.90 bars=0 stop=0.1347025000000000005 peak=0.14164
  - XPLUSDC BUY ntl=100 risk=4.63 bars=1 stop=0.07751075000000000995 peak=0.081272
  - ETHUSDC BUY ntl=200 risk=4.56 bars=1 stop=2444.52499999999975 peak=2501.5
  - JUPUSDC BUY ntl=100 risk=4.47 bars=1 stop=0.2266600000000000090 peak=0.23726
  - HYPEUSDC BUY ntl=100 risk=4.19 bars=1 stop=76.1829999999999980 peak=79.513
  - FARTCOINUSDC BUY ntl=100 risk=4.18 bars=1 stop=0.13483499999999999205 peak=0.14072
  - SUIUSDC BUY ntl=100 risk=3.53 bars=1 stop=0.6972224999999999185 peak=0.72274
  - XRPUSDC BUY ntl=100 risk=3.33 bars=1 stop=1.3540999999999999225 peak=1.4008
  - KPEPEUSDC BUY ntl=100 risk=3.11 bars=0 stop=0.003371749999999999855 peak=0.00348
  - LINKUSDC BUY ntl=100 risk=2.87 bars=1 stop=11.101750000000000755 peak=11.43
  - DOGEUSDC BUY ntl=100 risk=2.51 bars=1 stop=0.0818242499999999985 peak=0.083935
  - SOLUSDC BUY ntl=100 risk=2.31 bars=1 stop=99.4602499999999960 peak=101.81
  - LTCUSDC BUY ntl=100 risk=2.25 bars=1 stop=52.57149999999999735 peak=53.783
  - BTCUSDC BUY ntl=100 risk=2.01 bars=1 stop=76838.50 peak=78417.0
  - BNBUSDC BUY ntl=100 risk=1.77 bars=1 stop=708.82750000000002130 peak=721.6

- **HIP3**: 5 open, stop-risk **6.85 ZAR**
  - XYZ:AVGO SELL ntl=100 risk=2.13 bars=0 stop=354.34500000000002395 peak=346.95
  - XYZ:AMZN SELL ntl=100 risk=1.83 bars=0 stop=258.29249999999999080 peak=253.65
  - XYZ:BABA SELL ntl=100 risk=1.65 bars=0 stop=111.54500000000000465 peak=109.73
  - XYZ:COST SELL ntl=100 risk=0.94 bars=1 stop=926.8850000000000470 peak=918.28
  - XYZ:STRC SELL ntl=100 risk=0.29 bars=0 stop=98.98699999999999560 peak=98.697

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **84.68 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **84.68 / 140.00 ZAR | 65.5% | ok**
- Remaining: 48.3352 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 190, "skipped": 0, "slice_full": 0, "slot_full": 190}, "native": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 34, "skipped": 0, "slice_full": 0, "slot_full": 34}}
- Highest-risk: **UNIUSDC** 10.0000 ZAR
- positions without bars: 23 | replayed: 1 | invalid: 0

## 6. Monitored books

- Native: 5 | HIP-3: 7
- Native top (by paper P&L):
  - `feat_ret_5:2:LONG:h19` edge=0.0079 n=17246 p=0.0000 src=validated_walk_forward unproven=False paper=7n/+14.88
  - `feat_atr_norm_ext:2:LONG:h13` edge=0.0077 n=15915 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+6.92
  - `feat_ret_10:2:LONG:h15` edge=0.0078 n=17576 p=0.0000 src=validated_walk_forward unproven=False paper=4n/+0.74
  - `feat_ret_3:2:LONG:h19` edge=0.0072 n=17204 p=0.0000 src=validated_walk_forward unproven=False paper=6n/-21.89
  - `feat_atr_norm_ext:2:LONG:h15` edge=0.0085 n=15663 p=0.0000 src=validated_walk_forward unproven=False paper=5n/-35.61
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

- Label: **neutral** | breadth bear=0.0833 bull=0.0833 neutral=0.8333 | symbols=24
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from:  | consecutive_bear: 0 / bull 0
- as_of: 2026-09-14T16:55:34Z
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
- Tradable slices: native **5/5** | hip3 **7/7**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 0

## 13. Signal activity

- Latest scan 2026-09-14T16:35:11: errors=0 signals=224 regime_blocked=93
- this cycle: closed=0 new_signals=224 skipped=0 slot_full=224 slice_full=0 pair_held=0
- Action funnel: regime_blocked=93 | lane_gate_blocked=0 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=0 | slot_full=224 | skipped=0
- **NO ACTION:** dominant blocker = `slot_full` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 0, "pair_held": 0, "regime_blocked": 93, "skipped": 0, "slice_full": 0, "slot_full": 224})
- green_gate: native_green=False hip3_green=False frozen=none islands=0 blocks=0
- aggregate_risk: ok open=84.6840 cap=140.0000 used=0.6547 remaining=48.3352 replayed=1 no_new_bars=23
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
