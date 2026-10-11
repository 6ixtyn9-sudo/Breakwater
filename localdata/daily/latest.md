# Breakwater daily print — 2026-10-11 23:07 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **489.80 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2352.57 ZAR** (seed 2000) | lifetime: **+352.57 ZAR** | closed: 407
- Today: 11 closed, **+8.86 ZAR**
- 7d: **-67.55 ZAR** | 30d: **+352.57 ZAR**

## 2b. Claimed vs realised

- Book: 49 slices (native 24 | hip3 25); validated pools: native 31 | hip3 160; book slices absent from pools: 16
  - absent: `feat_time_since_low_20:2:LONG:h12` (native)
  - absent: `feat_vwap_lower_dist:0:LONG:h24` (native)
  - absent: `feat_ext_vs_ma_20:2:LONG:h12` (native)
  - absent: `feat_ret_20:2:LONG:h12` (native)
  - absent: `feat_bb_squeeze_20:2:LONG:h20` (native)
  - absent: `feat_ext_vs_ma_50:2:LONG:h12` (native)
  - absent: `feat_vwap_dist:0:LONG:h24` (native)
  - absent: `feat_close_pos_ma:2:LONG:h15` (native)
  - absent: `feat_rsi_14:2:LONG:h15` (native)
  - absent: `feat_keltner_pos:2:LONG:h15` (native)
  - ... and 6 more
- Claimed edge (median mean_ret_costadj over 33 book slices present in the validated pools): +0.117% | at 160.11 ZAR mean notional/trade: +0.19 ZAR/trade
- Realised (407 real closes per lane_gate._is_real_close, net of fees): +0.87 ZAR/trade | sd 5.18 | SE 0.26
- Gap: +0.68 ZAR/trade | t = +2.64 (one-sample t of realised mean vs the claimed constant) | verdict: EXCEEDS
- native: claimed median +0.491% over 12/24 slices (pool 31) ~ +0.78 ZAR | realised 361 closes +1.10 ZAR sd 5.18 SE 0.27 | gap +0.32 t +1.17 | NOT ESTABLISHED
- hip3: claimed median +0.065% over 21/25 slices (pool 160) ~ +0.11 ZAR | realised 46 closes -0.97 ZAR sd 4.81 SE 0.71 | gap -1.08 t -1.52 | NOT ESTABLISHED
- Ledger: 320337 decision rows; 407 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 9 exit reasons); the other 319930 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 361 | wins: 185 | win%: 51.2 | P&L: **+397.08 ZAR** | today: +8.86 | 7d: -67.55 | 30d: +397.08
- By exit: target +516.3, horizon +75.0, trail_stop +58.0, regime_shift -11.9, stop -240.3
- By entry regime (n/pnl): neutral 141/+233.6, bull 112/+179.0, bear 108/-15.5
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_cci_20:0:LONG:h24 5n/0w -17.74; feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_bb_squeeze_20:2:LONG:h20 4n/1w -10.15; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; feat_ext_vs_ma_50:0:LONG:h24 2n/0w -6.90
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPZAR 2n +18.07; ENAUSDC 3n +17.56; BTCUSDC 36n +13.47
- Worst pairs: UNIUSDC 7n -21.68; ZECUSDC 12n -16.52; ETHZAR 4n -14.36; ETHUSDC 43n -11.92; HYPEUSDC 26n -9.37

### HIP3

- Closed: 46 | wins: 23 | win%: 50.0 | P&L: **-44.50 ZAR** | today: +0.00 | 7d: +0.00 | 30d: -44.50
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -7.0, stop -85.5
- By entry regime (n/pnl): neutral 14/-1.5, bear 12/-17.5, bull 20/-25.4
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23 3n/2w -0.30
- Worst slices: hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 9n/2w -34.61; hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30
- Top pairs: PARA:IREN 2n +9.17; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98; XYZ:COPPER 1n +1.36; XYZ:SILVER 1n +0.71
- Worst pairs: PARA:CRWD 2n -13.94; PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73

## 4. Open positions & risk

- **NATIVE**: 4 open, stop-risk **18.01 ZAR**
  - ZECUSDC BUY ntl=238 risk=9.51 bars=4 stop=1233.6500000000000330 peak=1289.2
  - SUIUSDC BUY ntl=119 risk=3.90 bars=21 stop=1.0703999999999999925 peak=1.142
  - XRPUSDC BUY ntl=120 risk=2.52 bars=0 stop=1.3749500000000000380 peak=1.4045
  - ETHUSDC BUY ntl=119 risk=2.08 bars=5 stop=2504.39250 peak=2552.0

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **18.01 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **18.01 / 167.38 ZAR | 11.7% | ok**
- Remaining: 147.8812 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 27, "skipped": 27, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 3, "opened": 1, "pair_held": 8, "signals": 66, "skipped": 54, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **ZECUSDC** 9.5125 ZAR
- positions without bars: 0 | replayed: 5 | invalid: 0

## 6. Monitored books

- Native: 24 | HIP-3: 25
- Native top (by paper P&L):
  - `feat_atr_norm_ext:2:LONG:h15` edge=0.0041 n=10348 p=0.0006 src=validated_walk_forward unproven=False paper=3n/+15.77
  - `feat_vwap_dist:0:LONG:h24` edge=0.0069 n=9169 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+10.59
  - `feat_bb_squeeze_20:2:LONG:h15` edge=0.0033 n=10668 p=0.0092 src=validated_walk_forward unproven=False paper=2n/+7.41
  - `feat_rsi_14:2:LONG:h15` edge=0.0036 n=10124 p=0.0021 src=validated_walk_forward unproven=False paper=2n/+3.70
  - `feat_squeeze:2:LONG:h15` edge=0.0052 n=12111 p=0.0033 src=validated_walk_forward unproven=False paper=1n/+2.25
  - `feat_close_pos_ma:2:LONG:h15` edge=0.0054 n=9374 p=0.0000 src=validated_walk_forward unproven=False paper=6n/+1.75
  - `feat_keltner_pos:2:LONG:h15` edge=0.0033 n=10530 p=0.0112 src=validated_walk_forward unproven=False paper=1n/+1.46
  - `feat_kc_width:2:LONG:h12` edge=0.0054 n=10935 p=0.0027 src=validated_walk_forward unproven=False paper=1n/+0.70
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

- Closed paper trades: **46/50** | ghost rows: **550/50** | PnL: **-44.50 ZAR**
- Gate verdict: **NOT READY**

## 8. Research / honesty checks

- Deep audit: candidates=74880 preliminary_passes=0 audit_passes=0 plateaus=0 fetch_errors=25

## 9. Live readiness checks

- Promotion registry strategies: **0** | live_capped: 0
- 1 live HL executor: NOT PRESENT - hyperliquid.py is read-only; no mainnet signer
- 2 mechanism canary: NOT RUN - no testnet agent key / no signed action
- 3 live loss limits: WIRED, UNEXERCISED - reconciliation is in the guardian but no live position has closed yet, so the daily/7d limits have never had a non-zero input
- 4 promotion registry valr_native: NOT APPLICABLE TO HL - gate requires valr_native=True
- 5 big-wave-only live path: NOT YOUR BOOK - engine executes slice_id=='big-wave' only
- 6 deep audit passes: 0 preliminary / 0 audit
- 7 book regime durability: NOT PROVEN - hostile_unproven can be True and still promoted

## 10. Regime shift

- Label: **neutral** | breadth bear=0.0667 bull=0.2667 neutral=0.6667 | symbols=15
- confirmed_bear: **False** | confirmed_bull: **False** | flip: **False** | flipped_from: bear | consecutive_bear: 0 / bull 0
- as_of: 2026-10-11T22:59:09Z
- Defensive gate: off (no confirmed flip)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 832 | eligible: 4 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
  - `feat_gap_fill_ratio:2:SHORT:h20` edge=140.3b n=43 breadth=3 validated=False prov=False armable=False (too_few_rows)
  - `feat_gap_fill_ratio:2:SHORT:h24` edge=116.7b n=43 breadth=3 validated=False prov=False armable=False (too_few_rows)
  - `feat_gap_fill_ratio:2:SHORT:h12` edge=88.2b n=43 breadth=3 validated=False prov=False armable=False (too_few_rows)
  - `feat_gap_fill_ratio:2:SHORT:h15` edge=84.9b n=43 breadth=3 validated=False prov=False armable=False (too_few_rows)
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **GREEN** | closed=20 pnl=+7.26 | frozen=NO
- HIP-3 lane: **RED** | closed=20 pnl=-47.39 | frozen=YES
- Frozen lanes: hip3
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 2
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **20/24** | hip3 **18/25**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 31
  - `feat_adx_14:2:LONG:h12` slice_pnl=-1.83
  - `feat_adx_14:2:LONG:h15` slice_pnl=-3.92
  - `feat_atr_norm_ext:2:LONG:h13` slice_pnl=-4.88
  - `feat_bb_squeeze_20:2:LONG:h20` slice_pnl=-10.15
  - `feat_bb_width_20:2:LONG:h15` slice_pnl=-6.62
  - `feat_buy_vol_ratio:2:LONG:h24` slice_pnl=-6.57
  - `feat_cci_20:0:LONG:h24` slice_pnl=-17.74
  - `feat_donchian_break:2:LONG:h15` slice_pnl=-2.57
  - `feat_ema_cross_10_20:2:LONG:h12` slice_pnl=-3.12
  - `feat_hour_utc:2:LONG:h15` slice_pnl=-1.61
  - `feat_price_roc_5:2:LONG:h20` slice_pnl=-5.02
  - `feat_range_pos_20:2:LONG:h15` slice_pnl=-3.77
  - `feat_range_pos_50:0:LONG:h24` slice_pnl=-6.24
  - `feat_realized_vol_20:2:LONG:h14` slice_pnl=-0.40
  - `feat_realized_vol_20:2:LONG:h20` slice_pnl=-2.15
  - `feat_realized_vol_20:2:LONG:h21` slice_pnl=-2.71
  - `feat_realized_vol_20:2:LONG:h22` slice_pnl=-1.39
  - `feat_realized_vol_20:2:LONG:h23` slice_pnl=-0.13
  - `feat_realized_vol_20:2:LONG:h24` slice_pnl=-13.68
  - `feat_ret_1:2:LONG:h24` slice_pnl=-1.95
  - `feat_ret_vol:0:LONG:h24` slice_pnl=-4.69
  - `feat_time_since_high_20:0:LONG:h12` slice_pnl=-4.14
  - `feat_vol_breakout:2:LONG:h15` slice_pnl=-6.39
  - `feat_vol_of_vol:1:LONG:h24` slice_pnl=-3.36
  - `feat_vol_trend:0:LONG:h24` slice_pnl=-4.17
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` lane_not_green
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-10-11T22:08:43: errors=0 signals=93 regime_blocked=136
- this cycle: closed=2 new_signals=93 skipped=84 slot_full=0 slice_full=0 pair_held=8
- Action funnel: regime_blocked=136 | lane_gate_blocked=9 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=8 | slot_full=0 | skipped=84
- **NO ACTION:** dominant blocker = `regime_blocked` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 9, "pair_held": 8, "regime_blocked": 136, "skipped": 84, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=False hip3_green=False frozen=hip3,native islands=21 blocks=31
- aggregate_risk: ok open=15.4919 cap=167.3778 used=0.1165 remaining=147.8812 replayed=5 no_new_bars=0
- pair_errors: []

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
