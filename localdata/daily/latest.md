# Breakwater daily print — 2026-09-26 17:18 UTC

> Observation mode. Read-only digest of committed state. Nothing here trades or promotes.

## 1. Posture

- Mode: **readonly** | VALR equity: **544.04 ZAR** | high-water: **560.11 ZAR**
- Key perms: trade, view access | VALR perps: **retired** (venue choke, not used; Hyperliquid is the perp venue)
  - last perps probe: ValrAuthenticationError: VALR authentication rejected request with HTTP 401
- risk_allowed: **True** reasons=[]

## 2. Paper account

- Equity: **2484.38 ZAR** (seed 2000) | lifetime: **+484.38 ZAR** | closed: 269
- Today: 4 closed, **-2.22 ZAR**
- 7d: **+361.58 ZAR** | 30d: **+484.38 ZAR**

## 2b. Claimed vs realised

- Book: 274 slices (native 249 | hip3 25); validated pools: native 400 | hip3 160; book slices absent from pools: 38
  - absent: `feat_ext_vs_ma_20:2:LONG:h12` (native)
  - absent: `feat_atr_norm_ext:2:LONG:h12` (native)
  - absent: `feat_vol_breakout:2:LONG:h12` (native)
  - absent: `feat_rsi_14:2:LONG:h12` (native)
  - absent: `feat_hl_range:2:LONG:h15` (native)
  - absent: `feat_adx_14:2:LONG:h12` (native)
  - absent: `feat_trend_neutral:0:LONG:h15` (native)
  - absent: `feat_donchian_width_20:1:LONG:h24` (native)
  - absent: `feat_vol_roc_20:0:LONG:h20` (native)
  - absent: `feat_asia_vol:2:LONG:h24` (native)
  - ... and 28 more
- Claimed edge (median mean_ret_costadj over 236 book slices present in the validated pools): +0.386% | at 168.46 ZAR mean notional/trade: +0.65 ZAR/trade
- Realised (269 real closes per lane_gate._is_real_close, net of fees): +1.80 ZAR/trade | sd 5.62 | SE 0.34
- Gap: +1.15 ZAR/trade | t = +3.36 (one-sample t of realised mean vs the claimed constant) | verdict: EXCEEDS
- native: claimed median +0.407% over 215/249 slices (pool 400) ~ +0.71 ZAR | realised 227 closes +2.17 ZAR sd 5.79 SE 0.38 | gap +1.46 t +3.80 | EXCEEDS
- hip3: claimed median +0.065% over 21/25 slices (pool 160) ~ +0.09 ZAR | realised 42 closes -0.20 ZAR sd 4.08 SE 0.63 | gap -0.29 t -0.46 | NOT ESTABLISHED
- Ledger: 152535 decision rows; 269 real closes (outcome win/loss and exit_reason in lane_gate.ACTUAL_EXITS, 8 exit reasons); the other 152266 rows are skipped/guard decisions and never count

_Read-only and advisory: this section feeds no gate, admission decision or promotion path._

## 3. Lanes

### NATIVE

- Closed: 227 | wins: 134 | win%: 59.0 | P&L: **+492.73 ZAR** | today: -2.22 | 7d: +372.83 | 30d: +492.73
- By exit: target +506.4, horizon +98.5, regime_shift -11.9, stop -100.4
- By entry regime (n/pnl): neutral 76/+289.8, bull 85/+219.4, bear 66/-16.4
- Top slices: feat_close_pos_ma:1:LONG:h24 37n/32w +283.35; feat_close_pos_ma:2:LONG:h12 29n/19w +121.93; feat_ext_strength:2:LONG:h15 12n/8w +24.00; feat_bb_pos_20:2:LONG:h15 4n/4w +16.17; feat_atr_norm_ext:2:LONG:h15 3n/3w +15.77
- Worst slices: feat_realized_vol_20:2:LONG:h24 4n/0w -13.68; feat_atr_norm_ext:2:LONG:h19 2n/0w -7.26; engine_mean_reversion:rsi:2:SELL:h10:ZECUSDC 2n/0w -6.66; feat_buy_vol_ratio:2:LONG:h24 5n/0w -6.57; feat_vol_breakout:2:LONG:h15 3n/0w -6.39
- Top pairs: LINKZAR 28n +269.82; LTCZAR 8n +106.00; XRPUSDC 13n +25.68; XRPZAR 2n +18.07; BTCUSDC 20n +17.02
- Worst pairs: ETHZAR 4n -14.36; ZECUSDC 4n -11.98; NEARUSDC 3n -8.75; BNBZAR 5n -5.43; UNIUSDC 1n -4.19

### HIP3

- Closed: 42 | wins: 23 | win%: 54.8 | P&L: **-8.35 ZAR** | today: +0.00 | 7d: -11.25 | 30d: -8.35
- By exit: target +45.0, regime_shift +1.8, trail_stop +1.0, horizon -4.7, stop -51.5
- By entry regime (n/pnl): bull 18/-0.6, neutral 14/-1.5, bear 10/-6.2
- Top slices: hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23 8n/8w +3.98; hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21 3n/3w +2.42; hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20 5n/2w +1.55; hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h24 1n/1w +1.02; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h24 1n/1w +1.01
- Worst slices: hip3_para_equity_c0:feat_ret_20:2:SHORT:h21 3n/0w -5.36; hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11 4n/2w -2.66; hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20 6n/3w -2.46; hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20 5n/1w -2.30; hip3_para_equity_c0:feat_ext_vs_ma_10:0:SHORT:h17 1n/0w -1.80
- Top pairs: PARA:LRCX 1n +9.79; PARA:IREN 2n +9.17; PARA:CIEN 5n +6.86; PARA:RDDT 1n +4.26; XYZ:STRC 8n +3.98
- Worst pairs: PARA:COHR 3n -11.63; PARA:CIFR 1n -10.11; PARA:CRDO 3n -10.02; PARA:AVGO 2n -7.73; PARA:GLW 1n -3.99

## 4. Open positions & risk

- **NATIVE**: 7 open, stop-risk **23.13 ZAR**
  - ZECUSDC BUY ntl=125 risk=4.97 bars=9 stop=1474.9749999999999340 peak=1535.9
  - SOLUSDC BUY ntl=125 risk=4.63 bars=10 stop=116.19749999999999280 peak=120.65
  - HYPEUSDC BUY ntl=125 risk=3.56 bars=9 stop=89.15125000000001140 peak=91.753
  - XRPUSDC BUY ntl=125 risk=3.39 bars=7 stop=1.5106750000000000740 peak=1.5527
  - ETHUSDC BUY ntl=125 risk=2.19 bars=10 stop=2642.43375 peak=2689.5
  - BTCUSDC BUY ntl=125 risk=2.19 bars=7 stop=82604.67000 peak=84076.0
  - BNBUSDC BUY ntl=125 risk=2.19 bars=3 stop=760.337100 peak=773.88

- **HIP3**: 0 open, stop-risk **0.00 ZAR**

## 5. Aggregate risk leash

- Aggregate: **NOT WIRED FOR LIVE TRADING** - no cap is applied to any live position (there is no live executor); the computed open stop-risk is informational only.
- Computed open stop-risk (section 4): **23.13 ZAR** (informational only, no cap applied)
- Paper shadow ledger (gates paper entries only, nothing live): **23.13 / 176.79 ZAR | 14.3% | ok**
- Remaining: 151.4635 | cap skips: 0 | unknown skips: 0
- booked stats: {"hip3": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 0, "signals": 20, "skipped": 20, "slice_full": 0, "slot_full": 0}, "native": {"lane_gate_blocked": 0, "opened": 0, "pair_held": 12, "signals": 646, "skipped": 634, "slice_full": 0, "slot_full": 0}}
- Highest-risk: **ZECUSDC** 4.9738 ZAR
- positions without bars: 0 | replayed: 6 | invalid: 0

## 6. Monitored books

- Native: 249 | HIP-3: 25
- Native top (by paper P&L):
  - `feat_close_pos_ma:2:LONG:h12` edge=0.0052 n=8788 p=0.0000 src=validated_walk_forward unproven=False paper=29n/+121.93
  - `feat_trend_slope_20:2:LONG:h12` edge=0.0056 n=9427 p=0.0002 src=validated_walk_forward unproven=False paper=5n/+11.12
  - `feat_vol_regime:2:LONG:h12` edge=0.0058 n=9031 p=0.0004 src=validated_walk_forward unproven=False paper=5n/+7.60
  - `feat_vol_regime:2:LONG:h12` edge=0.0062 n=8545 p=0.0003 src=validated_walk_forward unproven=False paper=5n/+7.60
  - `feat_bb_squeeze_20:2:LONG:h15` edge=0.0074 n=9829 p=0.0515 src=validated_walk_forward unproven=False paper=2n/+7.41
  - `feat_trend_slope_20:2:LONG:h11` edge=0.0058 n=17004 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+5.56
  - `feat_close_pos_ma:2:LONG:h20` edge=0.0097 n=10051 p=0.0000 src=validated_walk_forward unproven=False paper=3n/+5.01
  - `feat_close_position:2:LONG:h24` edge=0.0071 n=9742 p=0.0000 src=validated_walk_forward unproven=False paper=2n/+3.97
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

- Closed paper trades: **42/50** | ghost rows: **489/50** | PnL: **-8.35 ZAR**
- Gate verdict: **NOT READY**

## 8. Research / honesty checks

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

- Label: **bull** | breadth bear=0.0 bull=0.8125 neutral=0.1875 | symbols=16
- confirmed_bear: **False** | confirmed_bull: **True** | flip: **True** | flipped_from: bull | consecutive_bear: 0 / bull 34
- as_of: 2026-09-26T16:35:33Z
- Defensive gate: ON (wrong-direction entries blocked & opposite exits armed)

## 11. Short inventory

- confirmed_bear: **False** | promote_env: ON
- candidates: 832 | eligible: 0 | observations: 0 | armable: **0**
- No armable short today (no validated SHORT slice clears the floor).
- HIP-3 short evidence: discovered=6912 validated=6912 passing=42 eligible=177 best=321.4b best_fail=temporal_pass,breadth_ok

## 12. Green gate

- Native lane: **RED** | closed=20 pnl=-0.67 | frozen=YES
- HIP-3 lane: **RED** | closed=20 pnl=-19.94 | frozen=YES
- Frozen lanes: hip3, native
- Lane verdict judged on the last 20 closes per lane; section 3 is the lifetime ledger. They differ by design, not by staleness.
- Green islands kept alive inside red lanes: 16
  - `feat_atr_norm_ext:2:LONG:h15` pnl=+15.77
  - `feat_bb_pos_20:2:LONG:h15` pnl=+16.17
  - `feat_cci_20:2:LONG:h15` pnl=+10.70
  - `feat_close_pos_ma:1:LONG:h24` pnl=+283.35
  - `feat_close_pos_ma:2:LONG:h12` pnl=+121.93
  - `feat_close_pos_ma:2:LONG:h20` pnl=+5.01
  - `feat_ext_strength:2:LONG:h15` pnl=+24.00
  - `feat_ext_vs_ma_20:2:LONG:h15` pnl=+9.35
  - `feat_realized_vol_20:2:LONG:h20` pnl=+1.47
  - `feat_ret_10:2:LONG:h19` pnl=+14.58
  - `feat_ret_20:2:LONG:h14` pnl=+13.42
  - `feat_trend_slope_20:2:LONG:h12` pnl=+11.12
  - `feat_vol_sma_ratio:0:LONG:h24` pnl=+1.00
  - `hip3_para_equity_c0:feat_trend_strength_20:1:SHORT:h20` pnl=+1.55
  - `hip3_xyz_commodity_c0:feat_realized_vol_20:1:LONG:h21` pnl=+2.42
  - `hip3_xyz_equity_c0:feat_trend_slope_20:2:SHORT:h23` pnl=+3.98
- Tradable slices: native **188/249** | hip3 **19/25**
- Forced liquidation on freeze: **RETIRED 2026-09-08**. A frozen lane blocks new entries only; open positions run to their own stop/target/horizon.
- Slice blocks: 14
  - `feat_atr_norm_ext:2:LONG:h13` lane_not_green
  - `feat_buy_vol_ratio:2:LONG:h24` lane_not_green
  - `feat_range_pos_20:2:LONG:h15` lane_not_green
  - `feat_realized_vol_20:2:LONG:h14` lane_not_green
  - `feat_realized_vol_20:2:LONG:h21` lane_not_green
  - `feat_realized_vol_20:2:LONG:h22` lane_not_green
  - `feat_realized_vol_20:2:LONG:h23` lane_not_green
  - `feat_realized_vol_20:2:LONG:h24` lane_not_green
  - `feat_vol_breakout:2:LONG:h15` lane_not_green
  - `hip3_para_equity_c0:feat_ret_20:2:SHORT:h21` lane_not_green
  - `hip3_para_equity_c0:feat_ret_vol:2:SHORT:h20` lane_not_green
  - `hip3_para_equity_c0:feat_vol_regime:2:SHORT:h11` lane_not_green
  - `hip3_para_equity_c0:feat_vol_trend:2:SHORT:h20` lane_not_green
  - `hip3_xyz_commodity_c0:feat_vol_regime:1:LONG:h23` lane_not_green

## 13. Signal activity

- Latest scan 2026-09-26T15:30:23: errors=6 signals=666 regime_blocked=301
- this cycle: closed=0 new_signals=666 skipped=654 slot_full=0 slice_full=0 pair_held=12
- Action funnel: regime_blocked=301 | lane_gate_blocked=7 | aggregate_risk_cap_skips=0 | aggregate_risk_unknown_skips=0 | slice_full=0 | pair_held=12 | slot_full=0 | skipped=654
- **NO ACTION:** dominant blocker = `skipped` (funnel={"aggregate_risk_cap_skips": 0, "aggregate_risk_unknown_skips": 0, "lane_gate_blocked": 7, "pair_held": 12, "regime_blocked": 301, "skipped": 654, "slice_full": 0, "slot_full": 0})
- green_gate: native_green=False hip3_green=False frozen=hip3,native islands=16 blocks=14
- aggregate_risk: ok open=23.1337 cap=176.7915 used=0.1433 remaining=151.4635 replayed=6 no_new_bars=0
- pair_errors: [{"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "BNBUSDC"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:BIRD"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:EBAY"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:NCLD"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:NET"}, {"error": "HTTPError: 429 Client Error: Too Many Requests for url: https://api.hyperliquid.xyz/info", "pair": "XYZ:XBI"}]

---
_Generated by scripts/daily_print.py. Read-only. Trades are paper observation only._
