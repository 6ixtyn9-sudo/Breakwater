# Breakwater daily print — 2026-09-20 22:44 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **437.06 ZAR** | high-water: **441.81 ZAR**
- Key perms: trade, view access | perps API: unavailable (ValrAuthenticationError: VALR authentication rejected request with HTTP 401)
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2265.45 ZAR** (seed 2000) | lifetime: **+265.45 ZAR** | closed: 184
- Today: 29 closed, **+145.12 ZAR**
- 7d: **+265.45 ZAR** | 30d: **+265.45 ZAR**

## 2b. Claimed vs realised

- Book: 301 slices (native 276 | hip3 25); validated pools: native 752 | hip3 160; book slices absent from pools: 7
  - absent: `feat_ret_20:2:LONG:h14` (native)
  - absent: `feat_ret_10:2:LONG:h19` (native)
  - absent: `feat_trend_slope_20:2:LONG:h11` (native)
  - absent: `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` (hip3)
  - absent: `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` (hip3)
  - absent: `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` (hip3)
  - absent: `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` (hip3)
- Claimed edge (median mean_ret_costadj over 294 book slices present in the validated pools): +0.464% | at 135.05 ZAR mean notional/trade: +0.63 ZAR/trade
- Realised (184 real closes per lane_gate._is_real_close, net of fees): +1.44 ZAR/trade | sd 4.33 | SE 0.32
- Gap: +0.82 ZAR/trade | t = +2.56 (one-sample t of realised mean vs the claimed constant) | verdict: EXCEEDS
- native: claimed median +0.473% over 273/276 slices (pool 752) ~ +0.67 ZAR | realised 154 closes +1.70 ZAR sd 4.59 SE 0.37 | gap +1.03 t +2.79 | EXCEEDS
- hip3: claimed median +0.065% over 21/25 slices (pool 160) ~ +0.06 ZAR | realised 30 closes +0.10 ZAR sd 2.26 SE 0.41 | gap +0.03 t +0.08 | NOT ESTABLISHED
- Ledger: 71414 decision rows; 184 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 71230 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 154 | wins: 86 | win%: 55.8 | P&L: **+262.55 ZAR** | today: +145.12 | 7d: +262.55 | 30d: +262.55
- By exit: target +280.6, horizon +78.1, regime_shift -11.9, stop -84.3
- By entry regime (n/pnl): neutral 52/+240.7, bull 36/+38.3, bear 66/-16.4
- Top slices: feat_close_pos_ma:1:LONG:h24 30n/25w +211.08; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77; feat_ret_10:2:LONG:h19 11n/5w +14.58; feat_ret_20:2:LONG:h14 5n/5w +13.42
- Worst slices: feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; engine_mean_reversion:rsi:2:SELL:h10:ZECUSDC 2n/0w -6.66; engine_mean_reversion:bollinger:2:SELL:h10:ZECUSDC 1n/0w -4.93; feat_atr_norm_ext:2:LONG:h13 7n/0w -4.88
- Top pairs: LINKZAR 25n +231.70; SUIUSDC 3n +14.91; LINKUSDC 7n +12.46; ARBUSDC 3n +7.76; AAVEUSDC 1n +7.32
- Worst pairs: ZECUSDC 4n -11.98; NEARUSDC 3n -8.75; ETHZAR 2n -8.51; SOLZAR 1n -5.95; UNIUSDC 1n -4.19

### HIP3

- Closed: 30 | wins: 19 | win%: 63.3 | P&L: **+2.90 ZAR** | today: +0.00 | 7d: +2.90 | 30d: +2.90
- By exit: target +19.0, horizon +2.3, regime_shift +1.8, trail_stop +1.0, stop -21.3
- By entry regime (n/pnl): bull 12/+5.0, bear 9/+3.1, neutral 9/-5.2
- Top slices: hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 2n/2w +7.29; hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01
- Worst slices: hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30; hip3_para_equity_c0:feat_ext_vs_ma_10:0:SHORT:h17 1n/0w -1.80; hip3_para_equity_c0:feat_trend_strength_20:2:SHORT:h20 1n/0w -1.80; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h24 1n/0w -1.66
- Top pairs: PARA:CIEN 4n +9.17; XYZ:STRC 8n +3.98; PARA:MELI 4n +1.64; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRDO 2n -6.24; PARA:COHR 1n -3.47; PARA:IREN 1n -2.84; PARA:TER 1n -1.80; PARA:AVGO 1n -0.60

## 4. Open positions & risk

- **NATIVE**: 14 open, stop-risk **65.77 ZAR**
  - XRPZAR BUY ntl=442 risk=10.31 bars=7 stop=21.98499999999999965 peak=22.51
  - BNBZAR BUY ntl=418 risk=8.23 bars=19 stop=12022.749999999999995 peak=12264.0
  - LINKZAR BUY ntl=453 risk=7.93 bars=0 stop=157.583175 peak=160.39
  - BTCUSDC BUY ntl=421 risk=7.36 bars=18 stop=79102.05750 peak=80511.0
  - BTCZAR BUY ntl=421 risk=7.36 bars=17 stop=1289481.14250 peak=1312449.0
  - HYPEUSDC BUY ntl=110 risk=3.70 bars=8 stop=87.90974999999999825 peak=90.96
  - SOLUSDC BUY ntl=113 risk=3.34 bars=2 stop=107.21000000000000570 peak=110.47
  - XRPUSDC BUY ntl=111 risk=3.27 bars=6 stop=1.3499000000000000060 peak=1.3908
  - XRPUSDC BUY ntl=112 risk=3.04 bars=4 stop=1.3651500000000000695 peak=1.4031
  - ETHUSDC BUY ntl=113 risk=2.61 bars=2 stop=2572.9500000000001090 peak=2633.7
  - SOLZAR BUY ntl=110 risk=2.47 bars=9 stop=1728.2499999999999970 peak=1768.0
  - BNBUSDC BUY ntl=112 risk=2.12 bars=4 stop=750.087499999999995 peak=764.52
  - LTCZAR BUY ntl=109 risk=2.08 bars=10 stop=920.99999999999993625 peak=938.9
  - BTCUSDC BUY ntl=111 risk=1.94 bars=6 stop=79512.74250 peak=80929.0

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **65.77 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **0.00 / 0.00 ZAR | 0.0% | None**
- Remaining: None | cap skips: None | unknown skips: None
- booked stats: null
- positions without bars: None | replayed: None | invalid: None

## 6. Monitored books

- Native: 276 | HIP-3: 25
- Native top (by paper P&L):
  - `feat_close_pos_ma:1:LONG:h24` edge=0.0091 n=1147 p=0.3217 src=validated_walk_forward unproven=False paper=30n/+211.08
  - `feat_ext_strength:2:LONG:h15` edge=0.0072 n=16038 p=0.0016 src=validated_walk_forward unproven=False paper=12n/+24.00
  - `feat_atr_norm_ext:2:LONG:h15` edge=0.0096 n=10364 p=0.0113 src=validated_walk_forward unproven=False paper=3n/+15.77
  - `feat_atr_norm_ext:2:LONG:h15` edge=0.0091 n=9846 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+15.77
  - `feat_ret_10:2:LONG:h19` edge=0.0077 n=16875 p=0.0000 src=validated_walk_forward unproven=False paper=11n/+14.58
  - `feat_ret_20:2:LONG:h14` edge=0.0060 n=17052 p=0.0000 src=validated_walk_forward unproven=False paper=5n/+13.42
  - `feat_cci_20:2:LONG:h15` edge=0.0088 n=9677 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+13.32
  - `feat_mean_rev_strength:0:LONG:h15` edge=0.0098 n=10438 p=0.0098 src=validated_walk_forward unproven=False paper=2n/+11.65
- HIP-3 top (by paper P&L):
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` edge=0.0175 n=268 p=0.0651 src=validated_walk_forward unproven=False paper=8n/+7.78
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` edge=0.0003 n=9570 p=0.3356 src=validated_walk_forward unproven=False paper=15n/+4.27
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` edge=0.0054 n=242 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+1.57
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` edge=0.0108 n=499 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+1.57
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h11` edge=0.0015 n=1260 p=0.0162 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h9` edge=0.0006 n=1272 p=0.4321 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ext_vs_ma_50:1:LONG:h22` edge=0.0006 n=1354 p=0.8646 src=validated_walk_forward unproven=False paper=0n/+0.00
  - `hip3_xyz_commodity_c0:feat_ext_strength:1:LONG:h18` edge=0.0001 n=1420 p=0.9829 src=validated_walk_forward unproven=False paper=0n/+0.00

## 7. HIP-3 live gate

- Closed paper trades: **30/50** | ghost rows: **282/50** | PnL: **+2.90 ZAR**
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

- Label: **bull** | breadth bear=0.0667 bull=0.5333 neutral=0.4 | symbols=15
- confirmed_bear: **False** | confirmed_bull: **True** | flip: **True** | flipped_from: bull | consecutive_bear: 0 / bull 3
- as_of: 2026-09-20T22:00:28Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 832 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+169.06 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-2.06 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **215/276** | hip3 **21/25**
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

- Latest scan 2026-09-20T22:44:02: errors=1 signals=None regime_blocked=None
- this cycle: closed=None new_signals=None skipped=None slot_full=None slice_full=None pair_held=None
- Action funnel: lane_gate_blocked=3
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 3, "pair_held": 74, "regime_blocked": 384, "skipped": 837, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=True hip3_green=False frozen=hip3 islands=2 blocks=9
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:EWZ"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
