Breakwater Handover / Runbook (2026-08-20)
Date: Thursday, 2026-08-20 (Africa/Johannesburg). Trust this over older stamps.

This is the canonical handover for operators and future agents.
Copy-paste safe: ASCII markdown, no smart quotes.

Spine: Price is the parent research lab for equities. Breakwater is VALR-native crypto (spot + mapped crypto perps). Do not port Hermes/YouTube agents here. Do not mix HIP-3 equity perps (xyz:) into this book.

0) Executive summary (read this first)
Breakwater is hands-off paper on one hunt slice:

PERP feat_ext_vs_ma_50:2:LONG:h21

Source: validated_concentrated (19 Aug). Mean +0.005465, n=2282, 17 names, fail only breadth_ok, hostile_n=0 at promote time.
Paper (score this only): n=5 closes, all target, 0 stops, +34.80 ZAR on R200 notionals (SOL +5.20, BTC +3.41, BTC +5.86, ETH +9.61, SOL +10.72). Last close 2026-08-19T21:15Z.
All-time paper fills (every slice, 16-19 Aug): n=31, +30.57 ZAR. Hunt is the profit; other slices ~ -4.2.
Live: locked. VALR authenticated /simple-futures/* still HTTP 401 code -93. Guardian equity ~R345-352 ZAR, 0 live positions. Paper marks public Hyperliquid candles, not VALR perps API.
Operator posture: hawk, not pig. Do not click research. Cron research is daily 02:25 UTC. Do not raise 2R, MIN_NET_EDGE, or PER_SLICE.
If you only remember one rule: score only h21 closes (target / trail_stop / horizon / stop). First honest stop has not printed.

1) Current operating mode
BREAKWATER_MODE: paper workflow = shadow; guardian often readonly; research = readonly.
No live orders. Mandate env is present; writes not armed for perps.
Cron (cron-job.org) dispatches filenames (do not rename workflows):
guardian.yml ~ :05 and :35
paper.yml ~ :15
research.yml daily 02:25 UTC
Concurrency groups (internal; cron URLs unchanged):
breakwater-guardian
breakwater-paper
breakwater-research
Shared lock used to queue guardian behind 60x1000 candle paper jobs. Split on purpose. commit_state.sh rebase-retries and merges status.csv.
2) System map
2.1 Pipeline
text

VALR spot + VALR perp symbol dump
        |
        v
universe.csv (ranked by venue volume; 7-day cache)
        |
        v
Rank window: top max_pairs by rank, DROP xyz: (no tail fill)
        |
        v
OHLCV: spot VALR public/auth candles; perps Hyperliquid public info
        |
        v
Features -> discovery -> walk-forward validation
        |
        v
sync_book: promote (net edge + 2-horizon) OR concentrated OR carry OR paper-green veto
        |
        v
monitor (EU/US sessions for paper) -> paper (R-gate, 2R cap, fees)
        |
        v
live path still big-wave + perps execute locked (401)
Nothing is a hand-authored strategy. Features are price states.

2.2 Files of record
Book: 
monitored_slices.csv

Paper: 
paper_positions.json
, paper_trade_log.csv, cooldown_journal.json
Research: discovered_slices.csv, validated_slices.csv, universe.csv
Ops: 
status.csv
, risk_state.json
Code: src/breakwater/{universe,perpdata,engine,paper_trade,research_lifecycle,monitor,validation,discovery}.py
Persist: 
commit_state.sh
 roles research | paper | guardian

paper now also persists monitored_slices.csv (was the hole that left paper_trades=0 in git)
2.3 Identity / git
Public: https://github.com/6ixtyn9-sudo/Breakwater.git
Operator: 6ixtyn9. Mac died; Actions + cron are the computer.
Never git add -A on Edge Factory; here bot owns localdata/ via commit_state. Humans: source files only, then git checkout -- localdata/ before pull if dirty.
3) Hunt doctrine (frozen)
Do not retune these because the tape is green.

MIN_NET_EDGE=0.002
RESEARCH_MAX_PAIRS=60 (rank window, not 60 crypto from the tail)
Paper --max-pairs 30
Candles 1000 spot/perp
Horizons 1-24; Bonferroni off
Concentrated promote: fail subset {breadth_ok} only; temporal+direction+mean_positive; not confounded; n>=2000; symbols>=10; mean>=0.004; selector edge_per_bar -> h21
Paper: MAX_POSITIONS=10, PER_KIND=8, PER_SLICE=5
Sessions: eu,us (skip Asia 00-07 UTC)
FILTER_NONPOSITIVE_BOOK=1
R-gate ON. Trail ENABLE=0 but R-gate arms trail at +1R, TRAIL_DISTANCE_R=1.0
Validation/paper: stop else 2R else horizon. Do not drop 2R mid-sample.
Same-bar: stop checked before target/trail (full -1R possible)
TIME_STOP_BARS=12 only if horizon_bars==0
Cousins (ret_20, trend_slope_20, atr_norm_ext, ext_vs_ma_20) failed temporal and/or confounded. Leave them.
Falsified earlier: PERP feat_realized_vol_20:0:LONG:h24 (fat on 6 names, died at 60x1000+2R)
Exit menu: no +1R -> original stop / horizon; after clean +1R bar -> trail giveback 1R from peak; max banked +2R.

4) Universe, xyz:, rank window (2026-08-19/20)
4.1 What xyz: is
VALR lists HIP-3 builder perps as XYZ:NVDAUSDC etc. (trade.xyz: equities, gold, SP500). Hyperliquid coin id is xyz:NVDA. This crypto lab must not pool them with BTC. Different oracle, session, fees, weekend.

4.2 What we did wrong, then fixed
xyz: in the top-30/60 counted as pair errors (24/35). Designed skip, noisy telemetry.
First fix filled max_pairs with the next mappable crypto (walked into rank 80 dust: CASHCAT, ACE, ...).
Research #78 (2026-08-20 02:25 UTC, 10m55s): 109 frames, 2 frame errors. Same hunt id on the wide pool: mean -0.00237, n=7962, 58 names, posf 0.26, fail temporal+direction+breadth+mean<=0, hostile_n=2. validated=False. 25 "validated" rows were SPOT shorts ~3-16 bp (under 0.002, not promoted). concentrated this pass: 0.
Book carried the 19 Aug hunt (PERP promoted nothing). Paper kept trading it.
Rank window (landed): take top limit by liquidity_rank, then drop unmappable. No tail fill. Research 60 ~= the sample that found the hunt (~36 crypto). Paper 30 ~= ~6 mappable in that window (BTC, ETH, HYPE, SOL, PUMP, ZEC on the 14 Aug file).
Do not undo xyz skip. Do not fill the tail again to "make 60 crypto". Do not shrink to 17 names to p-hack the mean green.

4.3 7-day universe cache
universe.csv as_of 2026-08-14T13:58Z. _universe() re-ingests if age >= 7 days (~21 Aug 13:58 UTC; 21 Aug 02:25 research may still be inside the window; 22 Aug 02:25 is the safe first photo).

Ingest = new volume ranking photo, not a bigger brain. Rank window still top N minus xyz:. Hunt does not auto-re-promote on ingest.

4.4 KPEPE flake
Hyperliquid coin is kPEPE, not KPEPE. Alias in perpdata.py HL_COIN_ALIASES. Was paper errors: 1 / research frame_errors class. Status now stores up to 8 {pair, error} strings (pair_errors).

5) Paper lifecycle vs research (2026-08-20)
5.1 Carry
If a kind promotes 0 rows, existing eligible book rows carry. That is why h21 survived #78.

5.2 Paper-green veto
If a monitored/cooldown row has paper_trades >= 1 and paper_pnl_zar > 0, it stays even if the same kind promotes a different family. New family can be added. Losers still decay (stale 96 bars; or trades>=3 and pnl<0; stopout cooldown).

This is Edge Factory's money judge, not a lower edge floor.

5.3 Book vs log hole (fixed)
Paper apply_signal_feedback wrote the book in the runner; commit_state.sh paper did not persist monitored_slices.csv. Git showed paper_trades=0 while the log was +34.80.

Fixed: paper persists the book. reconcile_paper_stats_from_log on each paper cycle recomputes paper_* from real fills (win/loss, not skips). Next paper job after that land should stamp hunt 5/5 +34.80 on the book. Confirm in monitored_slices.csv.

5.4 Open seats outside the rank window
Fill-quota paper opened AAVE/BNB/DOGE/PAXG. Rank window then stopped fetching them -> missing_bars climbing toward 24 -> stale_data close at entry+fees.

Fixed: shadow_scan unions open position pairs into _frames targets. Rank window still governs new names.

5.5 Open book snapshot (morning 20 Aug, then rest)
After rest: BTC 15/21 trail ON (peak 71362 vs 68630, stop ~69330). AAVE/BNB/DOGE trail on, missing_bars had been 4 before open-seat fetch fix. PAXG trail off. EU 08:15: 6 signals, slice_full 6, cap 5. errors 0.

Score only h21. BTC is the seat most likely to print the first trail_stop.

6) Paper execution rules (must remain true)
In paper_trade.py:

Horizon = loser timer. If never +1R, exit at horizon bar close. Stop still wins intrabar.
After +1R (R-gate): do not horizon-cut; 2R target may fire; trail ratchets 1R under peak.
Do not drop 2R mid-sample (validation = stop else 2R else horizon).
pnl_outcome after fees is truth; cooldown is stop/trail_stop/stale_data only.
Immortal guard: missing_bars >= 24 -> close at entry with fees (stale_data).
Sessions eu,us. FILTER_NONPOSITIVE_BOOK=1.
Expected hunt signature: mix of target / trail_stop / horizon / stop. All-target n=5 is a bull-tape print, not a proven edge.

7) Research / promotion (must remain true)
Net LONG = r - cost; SHORT = -r - cost. Perp cost 26 bps, spot 20.
Promote walk-forward validated rows with n>=60 and mean >= MIN_NET_EDGE, and 2 distinct horizons per family (edge_per_bar pick).
Concentrated path (env on): fail only breadth_ok, plus temporal/direction/mean_positive, not confounded, n>=2000, symbols>=10, mean>=0.004.
25 WF-validated SPOT shorts under 0.002 stay off the book. Do not loosen posf / MIN_NET_EDGE / max_pairs to revive dust.
#78 wider pool failing the hunt is sample change (tail alts), not automatic "regime flipped". hostile_n 0->2 is a note, not a kill switch.
If a better family passes floors, it promotes. Green hunt also stays (paper veto). Empty promote -> carry.
Do not click research to soothe. Cron 02:25 UTC is the sample.

8) Live / VALR
Public symbol-info OK. Authenticated simple-futures: 401 -93. Snow escalated. Tickets auto-close 3 days.
Live path still big-wave + perp execute code-locked.
Paper outgrew live. No cash, no leverage, no options, no forex on this lab.
Funding not in net returns.
Go-live: not because n=5 is green. Need VALR auth, 15-20 hunt closes including stops, stable ops. Then micro-live spot only if ever. Perps after API is real.

9) Cron / workflows
Filenames (cron-job.org POSTs these; do not rename):


guardian.yml

paper.yml

research.yml
YAML under .github/ may be hidden in some agent UIs; use COPY_INTO_* if needed.

Paper command: PYTHONPATH=src python scripts/breakwater.py shadow-scan --max-pairs 30
Guardian: operate --max-pairs 12
Research: research

10) Daily hawk routine
Do not fondle YAML. Do not one-knob-a-day.
Score only feat_ext_vs_ma_50:2:LONG:h21.
Wait for first stop / trail_stop / horizon. Target-only tape is incomplete.
Empty book in bear is valid (hostile_unproven=True blocks new longs).
Tomorrow research: rank window. Do not panic if hunt fails in-sample again; carry + paper-green hold it if the tape is green.
21-22 Aug: universe re-ingest. Ranking photo only.
Job search > retune. Cloud is the computer.
11) Related labs (do not merge)
Edge Factory: soccer; auto-tickets ROI gates; empty ticket valid; Wilson floor 0.50; noon freeze SAST.
Price: Alpaca paper, no leverage/options/forex/cash; TF cull floors 1d=5, 1h=15, 15m=20; ~month paper; Mac dead -> checkout localdata + pull.
Tempest / Halcyon / STST / Slipstream: not this hunt. Slipstream: accept no-edge.
XYZ HIP-3: second lab, isolated book/paper/fees/sessions, later. Not tonight.
12) What not to break
Horizon on positions; 2R cap; R-gate as loser-timer vs winner-cap.
Rank window (no tail fill). xyz: skip (no equity in this pool).
Paper persist of monitored book + log reconcile.
Fetch frames for open seats even off-window.
Paper-green veto; decay still evicts.
Concurrency group names can change; workflow filenames cannot (cron).
MIN_NET_EDGE 0.002; PER_SLICE 5; do not lift 2R.
Do not port self-improving agents into Breakwater.
13) Tape cheat-sheet (as of 2026-08-20)
Hunt closes: 5 target, +34.80 ZAR, 0 stops.
All-time fills: 31, +30.57 ZAR.
Open: 5/5 hunt (BTC trailed; others from fill-quota era still marking).
Live: 401. Research #78 did not rotate the book.
Operator: hawk.

End.
