BREAKWATER HANDOVER / RUNBOOK
Date: 2026-08-20 (Africa/Johannesburg); updated 2026-08-27.

This is the canonical handover. Plain text. Copy this whole file.
Sections are dated. Where sections conflict, the newest one wins.

Breakwater = Hyperliquid-authoritative perps (native crypto, plus HIP-3
builder perps as a SEPARATE lane) + VALR ZAR spot.
Do not port Hermes/YouTube agents here.
Do not pool HIP-3 (xyz:) evidence with the native crypto book: separate
universe, candles, books, paper state and fees. The HIP-3 paper lane has
been ARMED since 25 Aug (section 23) - isolation, not absence.


0) EXECUTIVE SUMMARY (updated 25 Aug; supersedes the 20 Aug h21-only summary)

Hands-off paper, multi-slice book + armed HIP-3 sub-pool.

Book: 15 PERP slices, ALL LONG, net edge 40.0-198.3 bps, zero spot.
  Auto-tuned floor over fact-based costs (sections 24-25). h21 (the original
  hunt) is one of the 15: 13 closes 12W/1L +114.00 ZAR, still trading.

Paper: equity 2121.09 ZAR (seed 2000 + 121.09). 79 closes, 47W/32L (60%).
  native PERP +134.90 (68), native SPOT -7.93 (9, all pre-floor era),
  HIP-3 -5.88 (2). 16 open positions, ~136 ZAR stop-risk vs ~148 cap (91%).
Sizing: COMPOUNDING (section 26) - R = 1% of equity, notional cap = 20% of
  equity. First 424 ZAR tickets printed 25 Aug; the old 200 fence is gone.
HIP-3 paper lane ARMED 25 Aug (section 23): 6 seats, per-slice cap 3,
  group-scoped matching, collateral set check. 6 open; first stop (CRCL,
  -1.09R) cut clean. Live gate still needs 25 closes + 25 positive ghost rows.
Ghosts (section 27): 2R control stays. Max MFE 2.25R, zero 3R trades; the
  3R ghost's +2.72 ZAR is ONE trade - a whisper, not a voice.
Live: locked. Perps = Hyperliquid (testnet funding paused, section 15).
  Spot is walled by the 140 bps cost floor - arithmetic, not policy.
Cron (SAST): paper every 30 min; guardian :05/:35; research daily 02:25;
  hip3-research daily 03:40. Section 27.

One rule (current): no knob changes without a number in status.csv.
The 40 bps bar (BREAKWATER_MIN_NET_EDGE=0.004) is a guarantee under the
auto-tune, not a dial. Do not lift 2R.


1) OPERATING MODE

BREAKWATER_MODE: paper workflow = shadow; guardian often readonly; research = readonly.
No live orders.

Cron (cron-job.org) hits FILENAMES. Do not rename workflows. Times SAST.
  guardian.yml     about :05 and :35
  paper.yml        every 30 min (:00 and :30), since 25 Aug
  research.yml     daily 02:25  (00:25 UTC)
  hip3-research.yml daily 03:40 (01:40 UTC; discovery runs first inside it)

Concurrency groups (internal; cron URLs unchanged):
  breakwater-guardian
  breakwater-paper
  breakwater-research

These used to share one lock so guardian queued behind fat paper candle jobs.
Split on purpose. commit_state.sh rebase-retries and merges status.csv.


2) SYSTEM MAP

Pipeline:
  VALR spot + VALR perp symbol dump
  -> universe.csv ranked by venue volume (7-day cache)
  -> Rank window: top max_pairs by rank, DROP xyz: (no tail fill)
  -> OHLCV: spot VALR candles; perps Hyperliquid public info
  -> Features -> discovery -> walk-forward validation
  -> sync_book: promote (net edge + 2-horizon) OR concentrated OR carry OR paper-green veto
  -> monitor (EU/US for paper) -> paper (R-gate, 2R cap, fees)
  -> live path still big-wave + perps execute locked (401)

Nothing is a hand-authored strategy. Features are price states.

Files:
  Book: localdata/research/monitored_slices.csv
  Paper: localdata/research/paper_positions.json
         localdata/research/paper_trade_log.csv
         localdata/research/cooldown_journal.json
  Research: discovered_slices.csv, validated_slices.csv, universe.csv
  Ops: localdata/status.csv, risk_state.json
  Code: src/breakwater/universe.py perpdata.py engine.py paper_trade.py
        research_lifecycle.py monitor.py validation.py discovery.py
  Persist: scripts/commit_state.sh roles research | paper | guardian
  Paper now also persists monitored_slices.csv
  (that hole left paper_trades=0 in git while the log was green)

Git: https://github.com/6ixtyn9-sudo/Breakwater.git
Operator: 6ixtyn9. Mac died. Actions + cron are the computer.
Humans commit source only. If localdata dirty: git checkout -- localdata/ then pull.


3) HUNT DOCTRINE (FROZEN 19 Aug)

[Partially superseded 25 Aug: MIN_NET_EDGE is now 0.004 as a guarantee under
the auto-tune (section 25); paper caps are now MAX_POSITIONS=24, PER_KIND=30,
PER_SLICE=5, OLD_SEATS=12, FAT_SEATS=10, HIP-3 sub-pool 6 seats / 3 per slice
(sections 23, 26). The frozen exit doctrine - stop / 2R / horizon, R-gate,
same-bar stop-first - is unchanged and still binding.]

Do not retune because the tape is green.

  MIN_NET_EDGE=0.002
  RESEARCH_MAX_PAIRS=60  (rank window, not 60 crypto from the tail)
  Paper --max-pairs 30
  Candles 1000 spot/perp
  Horizons 1-24; Bonferroni off
  Concentrated promote: fail subset {breadth_ok} only;
    temporal + direction + mean_positive; not confounded;
    n>=2000; symbols>=10; mean>=0.004;
    selector edge_per_bar -> h21
  Paper: MAX_POSITIONS=10, PER_KIND=8, PER_SLICE=5
  Sessions: eu,us (skip Asia 00-07 UTC)
  FILTER_NONPOSITIVE_BOOK=1
  R-gate ON. Trail ENABLE=0 but R-gate arms trail at +1R, TRAIL_DISTANCE_R=1.0
  Validation/paper: stop else 2R else horizon. Do not drop 2R mid-sample.
  Same-bar: stop checked before target/trail (full -1R possible)
  TIME_STOP_BARS=12 only if horizon_bars==0
  Cousins ret_20, trend_slope_20, atr_norm_ext, ext_vs_ma_20 failed. Leave them.
  Falsified: PERP feat_realized_vol_20:0:LONG:h24 (fat on 6 names, died at 60x1000+2R)

Exit menu:
  no +1R -> original stop / horizon
  after clean +1R bar -> trail giveback 1R from peak
  max banked +2R


4) UNIVERSE, xyz:, RANK WINDOW (19-20 Aug)

xyz: is HIP-3 builder perps VALR lists as XYZ:NVDAUSDC etc (trade.xyz equities, gold, SP500).
Hyperliquid coin id is xyz:NVDA.
This crypto lab must not pool them with BTC. Different oracle, session, fees, weekend.

What we did wrong, then fixed:

1) xyz: in the top-30/60 counted as pair errors (24/35). Designed skip, noisy telemetry.

2) First fix FILLED max_pairs with the next mappable crypto (walked into rank 80 dust:
   CASHCAT, ACE, ...).

3) Research #78 (2026-08-20 02:25 UTC, 10m55s): 109 frames, 2 frame errors.
   Same hunt id on the WIDE pool: mean -0.00237, n=7962, 58 names, posf 0.26,
   fail temporal+direction+breadth+mean<=0, hostile_n=2, validated=False.
   25 validated rows were SPOT shorts about 3-16 bp (under 0.002, not promoted).
   concentrated this pass: 0.

4) Book CARRIED the 19 Aug hunt (PERP promoted nothing). Paper kept trading it.

5) Rank window (landed): take top limit by liquidity_rank, THEN drop unmappable.
   No tail fill. Research 60 ~= the sample that found the hunt (~36 crypto).
   Paper 30 ~= ~6 mappable in that window (BTC, ETH, HYPE, SOL, PUMP, ZEC on the 14 Aug file).

Do not undo xyz skip.
Do not fill the tail again to make 60 crypto.
Do not shrink to 17 names to p-hack the mean green.

7-day universe cache:
  universe.csv as_of 2026-08-14T13:58Z
  Re-ingest if age >= 7 days (about 21 Aug 13:58 UTC).
  21 Aug 02:25 research may still be inside the window.
  22 Aug 02:25 is the safe first new photo.
  Ingest = new volume ranking photo, not a bigger brain.
  Hunt does not auto-re-promote on ingest.

KPEPE flake:
  Hyperliquid coin is kPEPE, not KPEPE.
  Alias in perpdata.py HL_COIN_ALIASES.
  Status now stores up to 8 pair+error strings (pair_errors).


5) PAPER LIFECYCLE VS RESEARCH

Carry: if a kind promotes 0 rows, existing eligible book rows carry. Why h21 survived #78.

Paper-green veto: if monitored/cooldown has paper_trades >= 1 AND paper_pnl_zar > 0,
it STAYS even if the same kind promotes a different family. New family can be ADDED.
Losers still decay (stale 96 bars; or trades>=3 and pnl<0; stopout cooldown).
Paper PnL is the eviction judge, not a lower edge floor.

Book vs log hole (fixed):
  Paper wrote the book in the runner; commit_state.sh paper did not persist
  monitored_slices.csv. Git showed paper_trades=0 while the log was +34.80.
  Fixed: paper persists the book.
  reconcile_paper_stats_from_log on each paper cycle recomputes paper_* from real fills.
  Next paper job after that land should stamp hunt 5/5 +34.80 on the book.
  Confirm in monitored_slices.csv.

Open seats outside rank window:
  Fill-quota paper opened AAVE/BNB/DOGE/PAXG. Rank window then stopped fetching them.
  missing_bars climbed toward 24 = stale_data close at entry+fees.
  Fixed: shadow_scan unions open position pairs into _frames targets.
  Rank window still governs NEW names.

Open snapshot after rest 20 Aug:
  BTC 15/21 trail ON (peak 71362 vs 68630, stop about 69330).
  AAVE/BNB/DOGE trail on. PAXG trail off.
  EU 08:15: 6 signals, slice_full 6, cap 5, errors 0.
  BTC is the seat most likely to print the first trail_stop.


6) PAPER EXECUTION (MUST REMAIN TRUE)

Horizon = loser timer. If never +1R, exit at horizon bar close. Stop still wins intrabar.
After +1R (R-gate): do not horizon-cut; 2R target may fire; trail ratchets 1R under peak.
Do not drop 2R mid-sample.
pnl_outcome after fees is truth.
Cooldown is stop / trail_stop / stale_data only.
Immortal guard: missing_bars >= 24 -> close at entry with fees (stale_data).
Sessions eu,us. FILTER_NONPOSITIVE_BOOK=1.

All-target n=5 is a bull-tape print, not a proven edge.


7) RESEARCH / PROMOTION (MUST REMAIN TRUE)

Net LONG = r - cost; SHORT = -r - cost. Perp 26 bps, spot 20.
  [SUPERSEDED 25 Aug: spot 70 bps, perp 9 bps - published venue schedules,
  env-driven, shared by research and paper. Section 24.]
Promote WF validated rows with n>=60 and mean >= MIN_NET_EDGE,
AND 2 distinct horizons per family (edge_per_bar pick).
Concentrated path (env on): fail ONLY breadth_ok, plus temporal/direction/mean_positive,
not confounded, n>=2000, symbols>=10, mean>=0.004.
25 WF-validated SPOT shorts under 0.002 stay off the book.
Do not loosen posf / MIN_NET_EDGE / max_pairs to revive dust.
#78 wider pool failing the hunt is SAMPLE CHANGE (tail alts), not automatic regime flip.
hostile_n 0->2 is a note, not a kill switch.
If a better family passes floors, it promotes. Green hunt also stays (paper veto).
Empty promote -> carry.

Do not click research to soothe. Cron 02:25 UTC is the sample.


8) LIVE / VALR

Public symbol-info OK. Authenticated simple-futures: 401 -93.
Live path still big-wave + perp execute code-locked.
Paper outgrew live. No cash, no leverage, no options, no forex on this lab.
Funding not in net returns.

Go-live: not because n=5 is green.
Need VALR auth, 15-20 hunt closes including stops, stable ops.
Then micro-live spot only if ever. Perps after API is real.


9) CRON / WORKFLOWS

Do not rename these files (cron POSTs them):
  .github/workflows/guardian.yml
  .github/workflows/paper.yml
  .github/workflows/research.yml

Paper:    PYTHONPATH=src python scripts/breakwater.py shadow-scan --max-pairs 30
Guardian: PYTHONPATH=src python scripts/breakwater.py operate --max-pairs 12
Research: PYTHONPATH=src python scripts/breakwater.py research


10) DAILY HAWK ROUTINE

[SUPERSEDED 25 Aug by section 27: the book is 15 slices, not just h21 -
score the book, watch the auto-tuned floors in status.csv.]

Do not fondle YAML. Do not one-knob-a-day.
Score only feat_ext_vs_ma_50:2:LONG:h21
Wait for first stop / trail_stop / horizon. Target-only tape is incomplete.
Empty book in bear is valid (hostile_unproven=True blocks new longs).
Do not panic if hunt fails in-sample on rank-window research; carry + paper-green hold it if tape is green.
21-22 Aug: universe re-ingest. Ranking photo only.
Job search > retune. Cloud is the computer.


11) WHAT NOT TO BREAK

Horizon on positions; 2R cap; R-gate as loser-timer vs winner-cap.
Rank window (no tail fill). xyz: skip (no equity in this pool).
Paper persist of monitored book + log reconcile.
Fetch frames for OPEN seats even off-window.
Paper-green veto; decay still evicts.
Concurrency group names can change; workflow FILENAMES cannot (cron).
MIN_NET_EDGE 0.002; PER_SLICE 5; do not lift 2R.
Do not port self-improving agents into Breakwater.


12) TAPE CHEAT-SHEET (2026-08-20)

Hunt closes: 5 target, +34.80 ZAR, 0 stops.
All-time fills: 31, +30.57 ZAR.
Open: 5/5 hunt (BTC trailed; others from fill-quota era still marking).
Live: 401. Research #78 did not rotate the book.
Operator: hawk.


13) VENUE DIRECTION + GO-LIVE MODEL (2026-08-21, DECIDED)

VALR support reply (asked 14 Aug, answered 21 Aug):
  Perps are NOT on the VALR API. No timeline. 401 = signature OR permissions.
  Only docs.valr.com routes are supported. /simple-futures/* stays unsupported.
  This is confirmation, not a new break: the canary already records 401 -93.
  Nothing to fix. Spot on VALR is unaffected.

Do NOT tear down HL/VALR work. All of it stays. Paper keeps marking public
  Hyperliquid candles. VALR spot untouched. The hunt (feat_ext_vs_ma_50:2:LONG:h21)
  keeps printing.

New direction (parallel by function, not redundancy):
  VALR = spot (ZAR).          Keep as-is; keep hunting a promotable spot slice.
  OKX  = perps (USDT, single-currency, perp-only).  New live path when ready.

OKX is a RE-RESEARCH, not a port.
  Feature library carries over (price-state features are venue-independent).
  Slices do NOT carry: HL tape != OKX tape (liquidity, funding, fee schedule).
  Slices must find themselves again on OKX candles. Do not seed the hunt as a
  granted edge; seed the same FAMILIES as hypotheses to re-test.

Go-live gate = mechanism canary, NOT "wait for a paper stop" (agreed).
  Prove the stop system works mechanically: tiny real OKX position -> SL/TP
  reduce-only -> trigger -> verify it closed. That is "a system that can stop".
  Ladder: OKX paper -> canary -> micro-live-capped -> scale.
  Calibration (3.5-ATR stop level on OKX tape) still comes from OKX paper.

Custody (OKX exchange, no wallet involved for perp collateral):
  Bot gets a SUB-ACCOUNT + trade-only API key (read_only,trade, NO withdraw)
  + passphrase + IP binding. Main account: 2FA + withdrawal whitelist/freeze.
  Trade-only key = venue-level kill switch: a fully owned bot cannot withdraw.

"Switch of a button" (decided shape):
  One engine, two fail-closed executors behind a venue abstraction:
    VALR spot executor + OKX perp executor.
  Arm only via GitHub secrets/vars: mode=live + live_ack + per-venue canary
  passed. Fail closed if venue unreachable or positions unverifiable in live.
  Nothing lives on the machine. (This is already the VALR pattern; add OKX.)

Open items (decide later, do not code yet):
  a) Account mode: USDT single-currency margin.
  b) IP binding vs GitHub Actions shared/rotating egress (or rely on OKX
     14-day idle-key auto-expiry as a backstop).
  c) Fee/cost refit: OKX taker ~0.05% one-way + funding; re-fit cost_bps and
     MIN_NET_EDGE for OKX (current 26 bps perp is HL/VALR-derived).
  d) Equity aggregation: guardian sums VALR ZAR + OKX USDT via USDTZAR
     (VALR lists USDTZAR, so the rate path already exists).

Tape snapshot (2026-08-21): hunt 13 closes, 12W/1L, +113.9994 ZAR, 0 stops
  (the 1 loss is a horizon exit, PAXG). Open 2 (atr_norm_ext: ETH, BNB).
  Still stop-free; mechanism canary is the unlock, not waiting for a stop.


14) BOOK ROTATION + ZERO-TRADE SLICES (2026-08-21, EXPLAINED)

Research #79 (21 Aug 00:25Z) promoted SIX new LONG slices onto the book:
  feat_trend_slope_20:2:LONG:h10   (hostile_unproven=False)
  feat_ext_vs_ma_50:2:LONG:h11     (hostile_unproven=True)  <- hunt family, 2nd horizon
  feat_ret_20:2:LONG:h14           (False)
  feat_atr_norm_ext:2:LONG:h21     (False)  <- has 2 OPEN paper positions (ETH, BNB)
  feat_trend_strength_20:0:LONG:h16(False)
  feat_ext_vs_ma_10:2:LONG:h23     (False)

Why they all show paper_trades=0 (expected, NOT failure):
  1) They are ~12h old (promoted 00:25Z).
  2) paper_trades counts CLOSED trades only. atr_norm_ext holds 2 OPEN
     positions (ETH, BNB) not yet closed -> still 0.
  3) One-position-per-pair: paper holds at most ONE position per pair. These
     are all LONG on the SAME crypto universe (BTC/ETH/SOL/HYPE/BNB...). Their
     signals fire on pairs the hunt/atr_norm_ext already hold or recently held
     -> skipped as pair_held. Status shows pair_held up to 23 per scan.
     pair_held/slot_full/slice_full skips are SILENT (no log row); only
     not_book/regime/adverse/no_price are logged. Read status.csv counters.
  4) Feature state must be ACTIVE: a slice signals only while its feature
     state equals the slice state (mostly state=2 = price extended). Off that
     state -> no signal at all. This also silences the hunt between waves.

The important read: h11 is the HUNT FAMILY (ext_vs_ma_50:2:LONG) re-passing
  walk-forward at a SECOND horizon (h11 vs h21), with higher mean (.00619 vs
  .00547) and lower p (.098 vs .652). Same family confirming itself, not
  noise. The old "score only h21" rule hid it. Watch h11's first fills like
  you watched h21's.

Do not change anything. The 6 new slices should earn their own fills over
  the coming days. If they stay 0 while the hunt keeps filling, the reason is
  pair-competition (one seat per pair), not a dead book.


15) HYPERLIQUID PREPARATION (2026-08-23, SUPERSEDES OKX-FIRST)

Operator registered with Hyperliquid and selected HL as the first PERP venue.
Reason: Breakwater research and paper already use HL candles, so HL execution
matches the measured tape. OKX remains the fallback if agent-wallet isolation,
South African product eligibility, or mechanism canaries are unsatisfactory.

Implemented preparation only:
  - venue-neutral read-only PERP contract
  - normalized HL instruments, precision, candles and public-address account state
  - positions and open-order reconciliation
  - explicit xyz: exclusion
  - mainnet/testnet endpoint selection
  - read-only canary using HYPERLIQUID_ACCOUNT_ADDRESS
  - all writes code-locked; no signer/private-key path exists

Do not store a master or agent private key in the repository, .env, status,
logs, issues, or chat.

Testnet stage implemented 23 Aug:
  - official SDK is a pinned optional dependency, imported only by signed canary
  - executor is structurally testnet-only; mainnet cannot be selected
  - dedicated agent key required and rejected if it derives to the account address
  - explicit acknowledgement + hard 25 mock-USDC cap + flat-account precondition
  - local process/file nonce serialization and deterministic cloids
  - IOC entry -> independent position reconcile -> atomic native reduce-only SL/TP
  - independent open-order/stop verification; failed protection emergency-closes
  - staged state is ignored by Git; cleanup closes, cancels and verifies flat

A dead-man cancel must NOT cancel protective stops on a directional position;
it is therefore not armed around the protected hold.

Operator verification completed in Codespaces 23 Aug:
  - read-only mainnet canary: 232 instruments, six current paper symbols mapped,
    no unavailable names, account reachable and flat at 0 USDC
  - read-only testnet canary: same public address reachable and flat at 0 mock USDC
  - precision planner: ETHUSDC size step 0.0001; 0.0060 ETH was about 15.1848
    mock USDC at the observed testnet mark
  - pinned SDK extra installed successfully in Codespaces
  - no agent key created or supplied; no signed action has occurred

Funding gate PAUSED, not failed:
  Hyperliquid's faucet requires prior mainnet deposit/activation. Operator has
  no spare funds now. Do not borrow, pressure-fund, weaken the gate, use an
  unofficial faucet, or place a mainnet trade to hurry this. Paper/research
  continue normally. Resume by approving a dedicated TESTNET agent and running
  open-protected only after legitimate mock funds are available. Mainnet stays
  code-locked until protection, stop-trigger, cleanup and revocation evidence.


16) VENUE UNIVERSE AFTER DIRECT HYPERLIQUID ACCESS (2026-08-23, DECIDED)

The old reason for excluding xyz:/HIP-3 was the VALR-mediated path and the need
not to contaminate the crypto sample. Direct Hyperliquid access removes the
venue-access limitation. It does NOT make equities, commodities and indices
statistically interchangeable with crypto.

Three parallel lanes are now the intended shape:
  A) VALR SPOT (ZAR): keep unchanged. This remains the South African fiat/spot lane.
  B) HL native crypto PERPs (USDC): keep current research and paper book unchanged.
  C) HL HIP-3 PERPs (including xyz:): add as a separate research/paper lane.

Expand, but do not pool:
  - preserve DEX-prefixed instrument identity (for example xyz:NVDA)
  - discover/rank HIP-3 only against other HIP-3 names; no crypto tail-fill
  - separate candles, discovered/validated/monitored books, paper state and logs
  - separate fee, funding, slippage, oracle-staleness and minimum-notional model
  - session/calendar features for equities, indices and commodities; account for
    market closures, weekends, stale oracles and gap risk even if the perp trades 24/7
  - run walk-forward research from zero; do not grant crypto slices or the h21 hunt
    an edge on HIP-3 because the feature library happens to be reusable
  - paper only initially; no HIP-3 signed/live path before native crypto testnet
    mechanism canary passes
  - one portfolio guardian eventually aggregates downside across VALR spot, HL
    crypto and HL HIP-3; separate research books must not become separate risk silos

Current code intentionally keeps xyz: excluded from the native crypto adapter.
That guard remains correct until the dedicated HIP-3 lane lands. Do not simply
remove the colon check or add xyz: rows to the existing crypto CSVs.

Next engineering order when work resumes:
  1) read-only HIP-3 venue metadata/instrument discovery and candle coverage
  2) dedicated HIP-3 state paths and universe snapshots
  3) calendar/oracle/fee-aware research and validation
  4) HIP-3 paper cycle under the shared aggregate-risk guardian
  5) only later consider execution, after the native crypto mechanism canary


17) HYPERLIQUID-AUTHORITATIVE PERPS + OPTIONAL VALR (2026-08-23, ACTIONED)

Operator can fund Hyperliquid directly and does not require VALR as the PERP
or collateral gateway. Decision:
  - Hyperliquid is authoritative for all PERP metadata, candles and eventual execution.
  - VALR remains available only for ZAR spot/fiat utility. No need to delete working code.
  - Existing VALR spot evidence stays venue-specific; no slices are fabricated.

Code posture:
  - production universe refresh now takes native crypto PERP metadata directly
    from Hyperliquid, while VALR supplies only active spot pairs and spot volume
  - universe rows persist their source venue; legacy VALR-PERP snapshots force a
    direct-HL refresh instead of remaining cached for seven days
  - dedicated `hip3-discover` queries `perpDexs` plus each DEX's
    `metaAndAssetCtxs`, preserves DEX prefixes and ranks within each DEX
  - HIP-3 writes isolated `localdata/hip3/universe.csv` and `status.csv` only
  - HIP-3 discovery records deployer/oracle, collateral, margin/growth mode,
    mark/oracle deviation, funding, OI, leverage and volume
  - no HIP-3 strategy promotion, paper position or execution is enabled yet

Workflow filename:
  .github/workflows/hip3-discovery.yml
External cron:
  none; keep hip3-discovery.yml as a manual inventory diagnostic
Command:
  PYTHONPATH=src python scripts/breakwater.py hip3-discover
Persistence role:
  bash scripts/commit_state.sh hip3


18) HIP-3 ISOLATED RESEARCH STAGE (2026-08-23, ACTIONED)

Command:
  PYTHONPATH=src python scripts/breakwater.py hip3-research
GitHub workflow filename:
  .github/workflows/hip3-research.yml
External cron (ONE new recurring job, discovery is included first):
  daily 03:40 UTC

Safety posture:
  - refreshes HIP-3 inventory before every research pass
  - excludes inactive/zero-volume names, >2% current mark-oracle deviation,
    and builder duplicates of validator-operated native crypto
  - ranks the remaining active universe globally by observed notional volume;
    default top 60, 1000 hourly bars each
  - audits bar count and maximum gaps before including a frame
  - groups evidence by DEX + market class + collateral token, with distinct
    `kind` pools and prefixed slice IDs; deployer/margin domains never pool
  - provisional 30 bps all-in research cost; must be replaced by measured
    DEX/asset fee, funding and slippage before any promotion
  - horizons 1 through 24, matching native PERP research breadth
  - native-PERP-aligned walk-forward doctrine: Bonferroni off, relaxed minimum
    2 passes, strict floor 3, breadth 6 names / 10 rows / 40% positive
  - writes isolated candle coverage, discovered and validated files
  - promotion_enabled=False and paper_enabled=False by design; no monitored
    HIP-3 book, signal, order or risk allocation is created

Calendar classification remains provisional. Single-name non-crypto products
are labelled provisional_equity, not trusted equity. The research output is an
audit corpus to show where continuity and candidate edges exist; it is not yet
permission to trade. Next gate is authoritative annotations/region calendars,
collateral resolution and measured costs, then a reviewed promotion policy.


19) HIP-3 PARITY + ACTIONS CONFIG HYGIENE (2026-08-23, ACTIONED)

HIP-3 research now emits a durable methodology_parity block comparing the
actual run against native-PERP doctrine: 60 names, 1000 bars, horizons 1-24,
rolling 200, matching quantiles, fold rules and breadth. Drift is reported as
named mismatches instead of silently changing the lane.

Promotion remains hard blocked and status names every missing production gate:
  - authoritative classification
  - enforced market calendars
  - historical oracle quality
  - measured effective costs
  - resolved collateral tokens
  - HIP-3 paper evidence

Discovery now queries Hyperliquid `perpConciseAnnotations` and persists raw
category/keywords. Recognized categories improve research grouping, but native
crypto identity always wins so misleading builder annotations cannot leak a
BTC duplicate into equity research. Legacy HIP-3 universe CSV remains readable
and the next discovery refresh upgrades it.

Actions configuration direction:
  - one private BREAKWATER_MANDATE_JSON object replaces 12 mandate Secrets
  - mixed consolidated + legacy mandate sources fail closed
  - malformed/partial/extra mandate keys fail closed
  - research/paper knobs and ACK strings move to Actions Variables
  - only VALR credentials and consolidated mandate remain repository Secrets
    during the current architecture
  - future HL agent key belongs in a protected live Environment; master key never GitHub

Actions configuration migration completed on main. Workflows now reference
only VALR_API_KEY, VALR_API_SECRET and BREAKWATER_MANDATE_JSON as Secrets;
non-sensitive knobs use Variables. The one-time migration script, duplicate
workflow templates and migration-only document were removed after use. Do not
delete old Secrets until guardian, paper, native research and HIP-3 research
all pass with the migrated workflows.


20) PROSPECTIVE EXIT COUNTERFACTUALS (2026-08-23, ACTIONED)

Do not reinterpret SHORT as loss. BUY/SELL are direction; win/loss is
pnl_outcome after fees. A short that profits from a price decline is a win.
Paper status now reports performance separately by side and exit reason.

The actual paper doctrine remains unchanged at 2R while evidence accumulates.
Every surviving/new paper position is mirrored into non-trading ghost policies:
  - target_2r_trail_1r (control; should match actual mechanics)
  - target_3r_trail_1r
  - target_4r_trail_1r
  - no_target_trail_1r
  - no_target_trail_2r

Ghosts use the same entry, initial stop, fees, stop-first OHLC convention,
+1R winner gate and loser horizon. They consume no seats, write no lifecycle
feedback and continue after the real 2R trade closes. A 240-bar diagnostic
maximum prevents immortal ghosts. Existing open positions are migrated using
persisted entry/initial stop/peak/trough; closed historical trades are not
backfilled because post-exit paths cannot be reconstructed honestly.

Persisted state:
  localdata/research/paper_counterfactuals.json
  localdata/research/paper_counterfactual_log.csv

Both actual and counterfactual closes now expose enough decision data:
  MFE/MAE in R, gross/net R, peak giveback, initial/final stop, fees, bars,
  side, exit reason, actual PnL and policy delta versus actual. MFE/MAE use
  hourly OHLC upper-bound extremes while exits retain stop-first ordering;
  intrabar path is unknowable and labelled `ohlc_upper_bound_stop_first_exit`.

Do not change the actual 2R target from one boom. Compare completed policy
samples by net PnL, win rate, delta versus actual, drawdown/giveback and side.
The 2R control must mechanically match actual exits before alternatives are
trusted; status counts control comparisons and >R0.01/reason mismatches.
Counterfactual state corruption is reported and preserved rather than
silently overwritten; it does not stop the real paper risk cycle.


21) DEEP-HISTORY WEIGHTED CHALLENGER (2026-08-23, MANUAL/AUDIT ONLY)

Command:
  PYTHONPATH=src python scripts/breakwater.py deep-research-audit --lane native
  PYTHONPATH=src python scripts/breakwater.py deep-research-audit --lane hip3

One shared implementation inside the existing research workflow; no new workflow
or cron. Normal dispatch skips it. A manual deep-audit dispatch commits transparent
artifacts under `localdata/deep_audit/`. It cannot call sync_book, paper or execution.

Frozen design (do not tune after seeing results):
  - 5000 hourly candles
  - horizons 1-48
  - forced LONG and SHORT evaluation for every feature/state/horizon; discovery's
    preferred side cannot suppress the opposite-direction red-team test
  - weights by bar age in 1000h blocks: 1, .5, .25, .125, .0625
  - recent-1000, full-5000 and weighted-5000 means all reported
  - weighted effective sample size
  - deterministic 48h block bootstrap
  - raw-symbol and >=0.80-correlation-cluster breadth
  - at least 3 contiguous passing horizons for an audit plateau
  - native and HIP-3 groups remain isolated; HIP-3 keeps DEX/class/collateral boundaries

Every result remains blocked by selection-holdout, funding, slippage and
point-in-time-universe gaps; HIP-3 additionally remains blocked by oracle
history, calendars and provisional costs. This challenger is for deciding
whether to replace the current method, not a second permanent research system.
Benchmark runtime and candidate stability manually first. Actual paper remains
2R while its independent prospective exit policies accumulate.

First hosted `all` audit completed calculations in 16m56s but its state commit
raced another workflow. The reset removed the new deep_audit directory and the
restore path failed before push. `commit_state.sh` now recreates every owned
file's parent after reset, so new nested state paths survive role-based races.
The failed runner's local audit output was not pushed; rerun after this fix.


22) RUNNER-DELAY BAR REPLAY (2026-08-24, ACTIONED)

GitHub's ubuntu-24.04 pool queued Paper for 30+ minutes while status remained
operational. Paper correctness no longer assumes one workflow run per bar:
  - every real position and counterfactual tracker persists last_processed_bar_start
  - all unseen frame bars replay chronologically on the next successful cycle
  - each bar applies stop before target, then horizon/time stop, then trail ratchet
  - an earlier unseen stop wins even if a later unseen bar reaches target
  - trail ratcheted on one unseen bar can be hit on the next unseen bar
  - a duplicate run seeing no new candle does not increment bars_held
  - new entries stamp the current bar so they are not immediately reprocessed
  - legacy positions/trackers migrate by processing only the latest bar once
  - actual/counterfactual logs record exit_bar_start separately from process time
  - status reports replayed_bars and positions_without_new_bars

This protects paper evidence from hosted-runner queues; it does not require
switching runner images or running another cron.


23) HIP-3 PAPER LANE ARMED + GATE V2 (2026-08-25, ACTIONED)

BREAKWATER_HIP3_PAPER=1 (paper.yml default) arms the HIP-3 paper sub-pool.
  - Paper cycle reads the isolated hip3 book
    (localdata/hip3/research/monitored_slices.csv); slice ids are
    namespaced hip3_* and group-scoped matching means a dex_class_cN slice
    only fires on its own group's frames. Never pooled with native.
  - Sub-pool: BREAKWATER_HIP3_MAX_POSITIONS=6 seats (does not consume
    native old/fat seats). BREAKWATER_HIP3_MAX_POSITIONS_PER_SLICE=3 -
    one edge cannot hold half the pool. The cap governs NEW entries only;
    the pre-cap legacy state (5/6 on realized_vol_20) converges as
    positions rotate. Do not force-close the legacy seats.
  - Gate v2 at book level: collateral SET check against operator-confirmed
    tokens (BREAKWATER_HIP3_USDC_TOKEN_ID=0,235), native min-net-edge floor
    applied to the HIP-3 book, min-net-edge parity canary.
  - 25 Aug state: 6 open (4 xyz_equity realized_vol_20:2:LONG,
    2 vol_regime:1:LONG; COIN MSTR PURRDAT RIVN AMAT AMD), 2 closes:
    CRCL stop -6.59 ZAR (-1.09R) cut clean, BABA trail +0.71.
  - HIP-3 LIVE gate unchanged (sections 18-19): 25 closed paper trades
    AND 25 positive ghost rows AND positive PnL, plus the production gates.
    Paper is the measurement instrument; do not shortcut it.


24) FACT-BASED COST MODEL (2026-08-25, ACTIONED)

The old 20 bps spot / 26 bps perp were assumptions, wrong in BOTH
directions. Replaced with published venue schedules, verified 25 Aug:
  - VALR "spot fiat-quoted" (BTCZAR class) tier 1 (zero 30-day volume -
    exactly a paper account): taker 0.350%/side = 70 bps round trip.
  - Hyperliquid base tier (native AND HIP-3 builder perps):
    taker 0.045%/side = 9 bps round trip.

Env (read by BOTH engine.research_pass cost-adjusted edges AND the paper
close-fee path - one number, one place, same defaults):
  BREAKWATER_SPOT_FEE_BPS = 70
  BREAKWATER_PERP_FEE_BPS = 9

scripts/fee_audit.py (PYTHONPATH=src python3 scripts/fee_audit.py) prints
the modeled bps, the published schedules, and with VALR credentials the
account's LIVE fee schedule. Run it before changing the bps; the number
only moves when the tier does.

perpdata.py now retries Hyperliquid /info 429/5xx (3 attempts, backoff,
honours Retry-After). VALR already retried; the asymmetry caused a
32-pair error burst on 25 Aug 10:17Z. Watch pair_errors in status.csv.

The 26 bps also over-costed perp validation: at true cost 150 MORE
candidates clear the 40 bps bar than the old model admitted, and spot's
"validated" slices were fabricated by the under-cost (best true spot edge
93.6 bps vs the 140 bps floor). Do not re-derive these numbers from memory.


25) AUTO-TUNING NET-EDGE FLOOR (2026-08-25, ACTIONED)

The quality bar is no longer a hand-maintained number. Per research run,
per kind:
  effective_floor = max( static bar, k x cost(kind), pool quantile )
  - static bar = BREAKWATER_MIN_NET_EDGE, operator-set to 0.004 (40 bps).
    It is a GUARANTEE (the bar never drops below it), not a dial.
  - k = BREAKWATER_MIN_NET_EDGE_COST_MULT (2 in research.yml; code default
    0 = static-only for bare local runs). Margin of safety: the edge must
    survive fees/slippage doubling.
  - pool quantile = top 25% of THIS run's candidate pool for NEW
    promotions (BREAKWATER_MIN_NET_EDGE_TOP_QUANTILE=0.25); existing book
    rows carry on the looser top 40% (KEEP_QUANTILE=0.40).
    Enter-tight / keep-loose = hysteresis, no boundary flapping.

The concentrated (hunt) path also respects the floor - no backdoor.
status.csv now reports net_edge_floor_enter_bps / net_edge_floor_keep_bps
per kind on every research run. That is the auditable bar.

First reading (25 Aug 12:27Z run): PERP enter 41.7 / keep 40.0;
SPOT 140.0 (cost floor dominates; the pool cannot lift it, and nothing
clears it - max observed spot edge 93.6 bps). Spot is off by arithmetic.

Book after the first two honest re-scores (25 Aug): 15 PERP slices,
ALL LONG, 40.0-198.3 bps net, zero spot; 275 of 1872 candidates validated.
The h21-era "score only h21" rule is dead - the book breathes daily at
02:25 SAST; multi-horizon gate re-picks horizons per family each run.

LONG-ONLY NOTE: 15/15 BUY = long beta. The short side is not offering
40 bps+ edges right now; that is the data, not a bug. The 7% aggregate
leash caps the pull. Watch it in a red tape; do not "fix" it with knobs.


26) COMPOUNDING PAPER SIZING (2026-08-25, ACTIONED)

BREAKWATER_PAPER_SIZE_FROM_EQUITY=1 (paper.yml default):
  - R = BREAKWATER_PAPER_RISK_OF_EQUITY (0.01) x equity
  - notional cap = BREAKWATER_PAPER_MAX_POSITION_NOTIONAL_OF_EQUITY (0.20)
    x equity. The old absolute 200 ZAR mandate cap is a FLAT-MODE boundary
    only; in equity mode it no longer caps compounding.
  - equity = seed (BREAKWATER_PAPER_EQUITY_SEED=2000) + realized paper PnL.

25 Aug state: equity 2121.09 ZAR, 79 closes 47W/32L, +121.09.
First tickets on the new cap: 424.2 ZAR notionals (20% of 2121) vs the old
200 fence. Pre-refactor positions ride at 200 until close - do not force-
resize them. The 7% aggregate leash (BREAKWATER_PAPER_MAX_AGGREGATE_RISK_OF_
EQUITY=0.07, ~148 ZAR) is now the binding constraint (~91% utilized); it
scales with equity, so the whole risk system compounds.

Paper caps (paper.yml): MAX_POSITIONS=24, PER_KIND=30, PER_SLICE=5,
OLD_SEATS=12, FAT_SEATS=10, HIP-3 sub-pool 6/3 (section 23).


27) CADENCE, STOP FIDELITY, OPS (2026-08-25, DECIDED)

VERIFIED MECHANICS (do not re-derive from vibes):
  - The paper cycle manages positions on COMPLETED 1-hour bars only
    (last_processed_bar_start only advances on closed bars; the forming
    bar is never marked). Every run re-scans signals on fresh prices, so
    entries can happen on any run.
  - 30-min cadence: stop detection averages ~30 min, worst ~60 min.
    DO NOT go to 15 min: 3 of 4 runs would add zero stop information at
    4x the public-API load. The API, not the runner, is the soft limit.
  - If 429s become chronic (pair_errors on MOST runs), the fix is candle
    caching, not a slower cadence.

Cron (cron-job.org, SAST): paper :00/:30; guardian :05/:35; research
daily 02:25; hip3-research daily 03:40. Filenames are the API - never
rename (section 9).

CI (every push to main): ruff + pytest (240) + compileall + bash -n, ~27s.
The Arena agent app CANNOT push .github/workflows/* - workflow edits go
through the operator's terminal block (python heredoc); the agent pushes
code and tests only. CI "red" = real; clean the commit, don't delete the
commit. (25 Aug: fee_audit ruff errors fixed in d1ce23a, CI #241 green.)

FIRST GHOST READING (16 mirrors, 76 rows): max MFE 2.25R, ZERO 3R+ trades.
3R ghost +2.72 ZAR is ONE trade (BTCUSDC, +3.74 on it) - a whisper.
Wide 2R-trail ghost is the one clearly-bad policy (keeps losers alive).
2R control stays. Ghosts are EVIDENCE for the HIP-3 live gate (25/25),
not a tuning menu. Revisit the target only when MFEs print 3R+.

CURRENT DAILY HAWK ROUTINE (replaces section 10):
  1) status.csv: pair_errors, aggregate_risk_status, replayed_bars.
  2) research run: net_edge_floor_enter_bps / keep_bps, validated count.
  3) book: any slice frozen/carried and why (status counters).
  4) HIP-3: closed-trade count toward 25; MFEs.
  5) In a red tape: the long-only book's leash utilization.
  No knob change without a number. No YAML fondling.

Variables (25 Aug): HIP3_USDC_TOKEN_ID=0,235; MIN_NET_EDGE=0.004;
  MODE=readonly; PAPER_EQUITY_SEED=2000; PERP_CANDLE_COUNT=1000;
  RESEARCH_HORIZONS=1..24; RUNNER=ubuntu-22.04; SPOT_CANDLE_COUNT=1000.
Secrets: BREAKWATER_MANDATE_JSON, VALR_API_KEY, VALR_API_SECRET.


28) PRE-MARKET FILL FIX + THE WEEK (2026-08-26/27, ACTIONED/DECIDED)

26 Aug bug (caught by the operator from trade timestamps): the session
gate checked the bar's NOMINAL close, but the paper engine fills at the
latest known price. The 13:00Z cycle filled at 13:00:24Z = 09:00:24 ET -
30 minutes PRE-OPEN - and four equity horizon exits got through (MSTR
AMD AAPL AMZN; net +2.90 ZAR that day, so the damage was small, but the
rule was doing something other than what it claimed).
Fix (dafc6f2): the gate checks min(server_time, bar close) = the actual
fill time, on BOTH entry (monitor) and planned-exit (horizon/time-stop
deferral; _mark_position_bar now receives the cycle's server_time).
Regression tests pin the exact 13:00:24Z scenario. Book-management
rotations are deliberately left OUTSIDE the session gate (a rotated
position sitting 10h in a dead market is worse than a thin-tape exit);
operator can gate those too - one line.
Since the fix: 1,000+ session blocks, all in dead windows, zero in-session.

OPERATOR DECISION (27 Aug, 05:30 SAST): run the system ONE FULL WEEK
(27 Aug -> 3 Sep) without intervention, EVEN IF paper equity goes below
2,000 ZAR. Then an autopsy on the evidence.

Rules of the week (pre-committed):
- No knob changes (R%, floors, caps, sessions, fees, books). The daily
  research votes may rotate the book - that is the system, not
  intervention.
- Mechanical bug fixes remain allowed (a broken mechanism is not a data
  point; the 26 Aug pre-market fill bug is the example).
- Balance below 2,000 is DATA, not a stop.

Reference line (27 Aug 03:30Z state, in git):
- Equity 2,046.53 ZAR | 105 closed, 57W/48L | 6-day net +46.53 (+2.3%)
- 8 open, ALL crypto (AAVE BTC KPEPE ADA DOGE LINK SUI XMR); 0 equities
- HIP-3 book: realized_vol_20:h23 (72.3 bps), atr_norm_ext:h23 (43.8,
  rotated in from h24 by the 27 Aug vote), trend_strength_20:h23 (41.2)
- HEADLINE FACT: the ENTIRE +46.53 profit is ONE slice -
  feat_ext_vs_ma_50:2:LONG:h21, +114.00 (13 closes, 12W/1L). All other
  37 slices net -67.47 COMBINED. The book is one hit plus a field of
  small losers. The autopsy is really about h21.

Autopsy questions (answer from logs, not memory):
  1) Week P&L by book (native vs hip3) and by entry session.
  2) Is h21 real? n, R-distribution and MFE pattern after +7 days.
  3) Worst 5 losses: mechanism (clean <=1.26R stops) or bug
     (>1.25R, off-schedule, off-session)?
  4) Gates: any fill outside market hours? any cap/leash breach?
  5) Ghosts with 30+ closes: does any exit policy beat the 2R control
     beyond noise?
  6) HIP-3: any slice with n>=25 and positive net (the live-gate
     evidence)?
Post-week decision (by data, not mood): scale up, hold, shrink, or
retire lanes.

END
