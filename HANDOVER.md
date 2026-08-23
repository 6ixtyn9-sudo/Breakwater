BREAKWATER HANDOVER / RUNBOOK
Date: 2026-08-20 (Africa/Johannesburg)

This is the canonical handover. Plain text. Copy this whole file.

Breakwater is VALR-native crypto (spot + mapped crypto perps).
Do not port Hermes/YouTube agents here.
Do not mix HIP-3 equity perps (xyz:) into this book.


0) EXECUTIVE SUMMARY

Hands-off paper on one hunt slice:

PERP feat_ext_vs_ma_50:2:LONG:h21

Source: validated_concentrated (19 Aug). Mean +0.005465, n=2282, 17 names, fail only breadth_ok, hostile_n=0 at promote.

Paper (score this only): n=5 closes, all target, 0 stops, +34.80 ZAR on R200 notionals
  SOL +5.20, BTC +3.41, BTC +5.86, ETH +9.61, SOL +10.72
  Last close 2026-08-19T21:15Z

All-time paper fills (every slice, 16-19 Aug): n=31, +30.57 ZAR
  Hunt is the profit. Other slices about -4.2 ZAR.

Live: locked. VALR authenticated /simple-futures/* still HTTP 401 code -93.
Guardian equity about R345-352 ZAR, 0 live positions.
Paper marks public Hyperliquid candles, not VALR perps API.

Hawk, not pig. Do not click research. Cron research daily 02:25 UTC.
Do not raise 2R, MIN_NET_EDGE, or PER_SLICE.

One rule: score only h21 closes (target / trail_stop / horizon / stop).
First honest stop has not printed.


1) OPERATING MODE

BREAKWATER_MODE: paper workflow = shadow; guardian often readonly; research = readonly.
No live orders.

Cron (cron-job.org) hits FILENAMES. Do not rename workflows.
  guardian.yml  about :05 and :35
  paper.yml     about :15
  research.yml  daily 02:25 UTC

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


3) HUNT DOCTRINE (FROZEN)

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

One shared implementation, no workflow, no cron, no committed output. Audit
artifacts live under ignored `localdata/deep_audit/`. It cannot call sync_book,
paper or execution.

Frozen design (do not tune after seeing results):
  - 5000 hourly candles
  - horizons 1-48
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

END
