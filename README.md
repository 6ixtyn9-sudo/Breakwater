# Breakwater

Breakwater is a venue-separated, self-contained market research and guarded
execution system. VALR remains an optional ZAR spot/fiat rail; Hyperliquid is
the authoritative PERP venue. Native crypto PERPs and HIP-3 builder PERPs use
separate universes and evidence stores. Breakwater runs price-state research,
monitors validated slices, paper-trades with stops and fees, and only then
allows a strategy to approach execution through layered gates. Each venue
remains authoritative for its own balances, orders, positions and fills.
The system is designed for periodic cloud execution through GitHub Actions
and does not depend on a local computer remaining powered.

`HANDOVER.md` is the living record: current posture, the lessons audit
against its predecessor system, known placeholders and the process rules.

## What it does, end to end

```text
VALR ZAR spot pairs + direct Hyperliquid native crypto PERPs
        |
        +---- separate Hyperliquid HIP-3 DEX discovery/state lane
        |
        v
Venue-separated universe ingestion (ranked, committed)
        |
        v
OHLCV research bars per symbol
        |
        v
Price-state features (extension, ATR, returns, volatility, trend)
        |
        v
Slice discovery (binned feature states x forward returns,
                  Bonferroni-controlled, side/cost-correct)
        |
        v
Walk-forward validation (time folds, pass patterns, recency required,
                         hostile-regime audit, side/cost-correct)
        |
        v
Monitored book (lifecycle gates, live decay, PnL decay, stopout-only cooldown)
        |
        v
Signal monitoring on completed bars (evidence-aware regime gating)
        |
        v
Paper trading (horizon-aligned exits, fees, journals, truth metric feedback)
        |
        v
Risk-managed live execution (spot cash longs; spot margin shorts gated; perps code-locked)
```

Nothing in this pipeline is a hand-authored strategy. Features are
descriptive price states; the system discovers which states carry stable
forward behaviour and only promotes slices that survive validation.

## Core research math (side/cost-correct)

Breakwater discovery/validation evaluate both trade directions correctly from raw forward returns.

Let:

- raw forward return over horizon h: `r = close[t+h] / close[t] - 1`
- cost as fraction: `cost = cost_bps / 10000`

Then the cost-adjusted net returns are:

- LONG net: `r - cost`
- SHORT net: `-r - cost`

Discovery computes both and chooses the side with the higher net mean per slice. Validation uses the same net-return definition when scoring folds, hostile-regime checks, and session audits.

## Inherited safeguards

Breakwater carries the hard-won operational lessons of its predecessor
research system as first-class safeguards:

- **Falling-knife entry guard.** Entries are compared against the latest
  price before opening: if the market has moved adversely beyond
  min(1.0 ATR, 2 percent) of the signal close, the entry is skipped.
  This is the guard the predecessor system built after systematically buying
  declines with limits resting on the signal close.
- **Winner-capture entry premium.** The reference entry is adjusted by
  min(0.25 ATR, 1 percent) in the trade's direction so modest
  follow-through can fill instead of only adverse moves.
- **Fail-open visibility.** Every skipped entry is journaled with its
  reason (adverse, no price, hostile regime, not in book). A guard that
  cannot see a price never silently pretends it blocked anything.
- **MAE-calibrated per-slice stops.** Each slice's stop distance is the
  90th percentile of its own adverse excursion in ATR units, clamped to
  [1.5, 3.5] ATR. Percentiles, not in-sample optima.
- **Evidence-aware regime gate.** Longs are blocked in a confirmed bear
  (SMA50 below SMA200) and shorts in a confirmed bull. Neutral and
  unknown regimes never block. If the slice has hostile-regime evidence
  (`hostile_unproven=False`), gating can be relaxed to avoid biased
  evidence collection. Strict gating can be forced via
  `BREAKWATER_REGIME_GATE_STRICT=1`.
- **Regime-stratified validation.** Chronological
  walk-forward folds cannot distinguish a durable price-state edge from
  a regime artifact. Every slice is therefore also measured on its
  hostile-regime rows: bear rows for longs, bull rows for shorts. A
  slice whose hostile-regime mean net return is non-positive (at least 20
  hostile rows) is marked `regime_confounded` and is not validated,
  with `hostile_n` and `hostile_mean_ret` recorded in the evidence.
- **Book-only paper trading.** Only slices promoted into the monitored
  book by walk-forward validation are paper-traded. Unvalidated
  fallback signals are research-only.
- **Chronological bar replay.** Every position persists its last processed
  candle. Delayed runners replay all unseen bars in order with stop-before-target
  semantics; repeated runs in the same hour do not increment holding time twice.
- **Immortal-trade guard.** Positions whose pair data has vanished are
  closed at entry with fees after 24 missing bars instead of living
  forever.
- **Stale-data refusal.** The universe snapshot is re-ingested if it is
  older than seven days.
- **Provenance honesty.** Every book row records the gate that promoted
  it (`validated_walk_forward`), so the audit trail never overstates the
  evidence behind the book.
- **Serialized state commits.** All workflows share one concurrency
  group, so two runs can never commit research and trading state to
  `main` at the same time.
- **Research and paper execution are separate workflows**, following
  the separation doctrine.
- **Stopout-only cooldown.** Slice cooldowns are applied only on stopout-style
  adverse exits (stop / trail_stop / stale_data safety), not every small
  horizon loss.
- **Truth-metric paper feedback.** Paper logs preserve directional `outcome`,
  while lifecycle feedback is driven by after-fees truth (`pnl_outcome`).
- **Prospective exit counterfactuals.** Every open paper position is mirrored
  without consuming seats into 2R, 3R, 4R, no-target/1R-trail and
  no-target/2R-trail policies. Ghost trackers continue after the real 2R exit
  and record MFE, MAE, peak giveback, fees, R returns and delta versus actual.
  Counterfactuals never feed promotion, cooldown, paper P&L or execution.
- **Direction is not outcome.** `BUY`/`SELL` describe long/short direction;
  `pnl_outcome` records win/loss after fees. A profitable short is a win.

Deliberate deviations from the predecessor system's anti-drift rules,
recorded honestly: the predecessor system forbade leverage entirely; Breakwater permits per-position
exchange leverage up to the mandate's cap (default 3x) on VALR Perps
only, where the isolated-margin model bounds the worst-case loss of a
position to its allocated margin.

## Instruments

- **VALR spot (cash)**:
  - Live execution supports cash spot long entries (BUY).
  - Cash spot sells (SELL) are conceptually “reduce/close long exposure”, not “open a short”.

- **VALR spot margin (optional)**:
  - VALR offers spot margin trading (borrow/repay), enabling spot short exposure (SELL to open).
  - Breakwater supports live spot-margin shorts, but it is **disabled by default** and requires explicit operator gating:
    - `BREAKWATER_ENABLE_SPOT_MARGIN_SHORTS=1`
    - `BREAKWATER_SPOT_MARGIN_ACK=I_ACCEPT_BREAKWATER_SPOT_MARGIN_RISK`
  - Spot margin adds borrow interest and liquidation risk; paper/research do not model borrow interest or liquidation fees.

- **Hyperliquid native crypto PERPs**: Hyperliquid is authoritative for
  metadata, candles, marks, funding and the eventual execution path. Research,
  shadow signals, positions and paper trading are supported. Signed mainnet
  entry remains code-locked until the native protection canary passes.

- **Hyperliquid HIP-3 PERPs**: builder DEXs have isolated discovery and research
  state. Classification, calendars, historical oracle quality, collateral and
  measured costs remain promotion blockers. No HIP-3 paper or execution path is
  enabled.

- VALR remains an optional ZAR spot/fiat rail. VALR PERP and sub-account futures
  are not targeted.

## Capital mandate

Every loss boundary is supplied by the operator through environment
variables and is never compiled into the repository. The engine fails
closed when any boundary is missing in an authenticated run. The mandate
fields are:

| Field | Environment variable |
|---|---|
| Initial equity (reference) | `BREAKWATER_INITIAL_EQUITY_ZAR` |
| Absolute equity floor | `BREAKWATER_ABSOLUTE_EQUITY_FLOOR_ZAR` |
| Maximum lifetime loss | `BREAKWATER_MAX_TOTAL_LOSS_ZAR` |
| High-water drawdown fraction | `BREAKWATER_MAX_TOTAL_DRAWDOWN_FRACTION` |
| Risk per trade | `BREAKWATER_RISK_PER_TRADE_ZAR` |
| Daily loss limit | `BREAKWATER_DAILY_LOSS_LIMIT_ZAR` |
| Seven-day loss limit | `BREAKWATER_SEVEN_DAY_LOSS_LIMIT_ZAR` |
| Maximum aggregate open risk | `BREAKWATER_MAX_AGGREGATE_OPEN_RISK_ZAR` |
| Maximum position notional | `BREAKWATER_MAX_POSITION_NOTIONAL_ZAR` |
| Maximum effective leverage | `BREAKWATER_MAX_EFFECTIVE_LEVERAGE` |
| Per-position exchange leverage cap | `BREAKWATER_PERP_LEVERAGE_CAP` |
| Maximum simultaneous positions | `BREAKWATER_MAX_POSITIONS` |

Perp sizing is bounded by the venue minimum notional and minimum margin.
When the venue minimum forces notional above the risk-sized amount, the
plan is rejected rather than silently enlarged. The strategy cannot modify
these values at runtime. Averaging down, martingale, grids, spot borrowing,
withdrawals and transfers are not implemented (spot margin shorts are gated).

## Security posture

A single VALR API key is used for everything: it must have **View access
plus Trade access only**. It must not have Withdraw, Internal Transfer or
Link Bank Account permissions. The client has no withdrawal, transfer or
banking methods, and every write request passes through a hard local gate
that only opens when both live gates are deliberately armed.

Modes:
- `readonly`: authenticated reads and research only; no writes.
- `shadow`: adds signal monitoring and paper trading; no broker writes.
- `live`: requires the acknowledgement gate and a promoted strategy.

Live mode additionally requires:
- the capital mandate configured through the environment;
- exactly View plus Trade permissions on the key;
- clean account reconciliation and protected open positions;
- a strategy promoted to `live_capped` by the promotion registry;
- unverifiable perp position state halts live operation.

The gates are `BREAKWATER_MODE=live` together with
`BREAKWATER_LIVE_ACK=I_ACCEPT_BREAKWATER_LIVE_RISK`. Do not set them during
initial deployment.

## Research cycle details

The atomic research row is one symbol, one bar timestamp, one forward
window: OHLCV inputs, descriptive price-state features, and a raw forward
return. Feature states are binned per symbol on expanding windows, so a
slice is a market state, not a rule.

Discovery measures (feature, state) slices across the pooled universe and
applies a Bonferroni correction to the number of slices tested. Validation
splits pooled rows into contiguous time folds; a slice must pass most folds,
including the most recent one. Hostile-regime and session audits are recorded.

The monitored book applies lifecycle gates on top of validation: a minimum
row count, the correct directional net edge, live decay for slices that stop
firing, PnL decay for slices that lose on paper, and a cooldown after
paper stopouts.

## Install

```bash
git clone --branch main --single-branch https://github.com/6ixtyn9-sudo/Breakwater.git
cd Breakwater
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --require-hashes -r requirements.lock
cp -n .env.example .env
${EDITOR:-vi} .env
PYTHONPATH=src python -m pytest -q
python -m ruff check .
```

## Local operation

```bash
cd Breakwater
source .venv/bin/activate
set -a
source .env
set +a
PYTHONPATH=src python scripts/breakwater.py guardian
PYTHONPATH=src python scripts/breakwater.py research
PYTHONPATH=src python scripts/breakwater.py hip3-discover
PYTHONPATH=src python scripts/breakwater.py hip3-research
BREAKWATER_MODE=shadow PYTHONPATH=src python scripts/breakwater.py shadow-scan --max-pairs 12
BREAKWATER_MODE=readonly PYTHONPATH=src python scripts/breakwater.py operate --max-pairs 12
PYTHONPATH=src python scripts/breakwater.py health
```

No credentials are needed for public market checks, the spot slice research
pass, or Hyperliquid candles. VALR account reconciliation requires its API
key. Hyperliquid account inspection needs only the public master/subaccount
address.

### Hyperliquid read-only readiness

Breakwater has a venue-neutral PERP contract and a Hyperliquid adapter for
normalized instruments, precision, candles, public-address account state,
positions, and open orders. HIP-3 builder instruments (for example `xyz:`)
remain excluded from the crypto strategy pool. The adapter has no signer or
private-key path: all order and cancel methods are code-locked.

Set only the public address, then run the canary:

```bash
export HYPERLIQUID_ACCOUNT_ADDRESS=0xYourPublicAddress
export BREAKWATER_HYPERLIQUID_NETWORK=mainnet
PYTHONPATH=src python scripts/hyperliquid_canary.py
```

Use `--testnet` for the testnet public API. Never put a master-wallet or agent
private key in `.env`, GitHub variables, repository files, issues, logs, or
chat. Mainnet execution remains locked. The separate testnet mechanism-canary
executor is structurally pinned to Hyperliquid testnet and hard-capped at
25 mock USDC. It requires a dedicated agent key, an otherwise flat testnet
account, an explicit acknowledgement, deterministic client order IDs, and
native reduce-only SL/TP verification. A protection failure forces an
emergency testnet close.

Install the pinned optional SDK only in the environment used for the canary:

```bash
python -m pip install -e '.[hyperliquid]'
```

Inspect testnet without loading a signer:

```bash
export HYPERLIQUID_TESTNET_ACCOUNT_ADDRESS=0xYourTestnetMasterAddress
PYTHONPATH=src python scripts/hyperliquid_testnet_canary.py inspect
```

The write stage additionally reads `HYPERLIQUID_TESTNET_AGENT_PRIVATE_KEY`
from the process environment and requires:

```text
BREAKWATER_HYPERLIQUID_TESTNET_ACK=I_ACCEPT_BREAKWATER_HYPERLIQUID_TESTNET_ORDERS
```

The key must belong to a dedicated testnet API/agent wallet approved by the
testnet account. It must never be the master key, and must never be committed,
printed, pasted into chat, or saved in `.env`. `open-protected --execute`
stages one position with native stop and target; `close --execute` closes it,
cancels its known orders, and verifies the account is flat. Mainnet is not an
available endpoint in this executor.

### VALR connectivity canary

After creating or replacing the VALR key, probe every endpoint Breakwater
uses from your own machine. It performs no writes:

```bash
cd Breakwater
source .venv/bin/activate
set -a
source .env
set +a
PYTHONPATH=src python scripts/perps_canary.py
```

The output shows Hyperliquid candle availability, the top perps by volume,
the key permissions VALR reports, and the exact response of each perp
account endpoint as used by the VALR web application.

### HIP-3 discovery workflow

`hip3-discover` queries Hyperliquid's `perpDexs` and each DEX's
`metaAndAssetCtxs` directly. It preserves DEX-prefixed identities, ranks only
within each HIP-3 DEX, records collateral/margin/growth modes and oracle/mark
deviation, and writes only:

```text
localdata/hip3/universe.csv
localdata/hip3/status.csv
```

Discovery does not enter the native crypto research book or paper cycle. The
existing `hip3-discovery.yml` remains a useful manual inventory diagnostic;
it does not need its own external cron.

The combined daily `.github/workflows/hip3-research.yml` refreshes discovery,
audits up to 60 active non-crypto HIP-3 candle histories and runs the full
1-through-24 horizon sweep, grouped by DEX, provisional market class and
collateral token. Walk-forward and breadth knobs match native PERP research;
HIP-3 retains a conservative venue-specific cost. It writes candle coverage,
discovered slices and validated slices, but deliberately creates no monitored
book: promotion and paper remain off until classification/calendar metadata is
trustworthy.

### Manual deep-history research audit

The non-promoting challenger loads 5,000 hourly candles, applies frozen
1/0.5/0.25/0.125/0.0625 weights per 1,000-hour age bucket, tests both LONG and
SHORT for every feature/state across horizons 1–48, uses 48-hour block
bootstrap confidence, correlation-cluster breadth and
requires contiguous three-horizon plateaus. Outputs are committed as transparent
research artifacts but cannot alter books, paper state or promotion:

```bash
PYTHONPATH=src python scripts/breakwater.py deep-research-audit --lane native
PYTHONPATH=src python scripts/breakwater.py deep-research-audit --lane hip3
```

Results land under `localdata/deep_audit/`. The existing `research.yml` can run
this challenger only when manually dispatched with a deep-audit lane; ordinary
external cron dispatches retain the default and skip it. Do not add another
workflow or cron.

### Actions Secrets versus Variables

Non-sensitive research, paper, horizon and acknowledgement knobs belong in
GitHub Actions Variables. Private capital boundaries use the single
`BREAKWATER_MANDATE_JSON` Secret; VALR credentials remain separate Secrets.
Legacy mandate variables remain parser-compatible for rollback, but mixed JSON
and legacy sources fail closed.

## GitHub configuration

Required repository Secrets:

```text
VALR_API_KEY
VALR_API_SECRET
BREAKWATER_MANDATE_JSON
```

Keep non-sensitive overrides in Actions Variables. `BREAKWATER_MODE` should
remain `readonly` until every live gate is deliberately armed.

Dispatch the account guardian:

```bash
gh workflow run guardian.yml --repo 6ixtyn9-sudo/Breakwater --ref main
sleep 3
RUN_ID="$(gh run list --repo 6ixtyn9-sudo/Breakwater --workflow guardian.yml --branch main --limit 1 --json databaseId --jq '.[0].databaseId')"
gh run watch "$RUN_ID" --repo 6ixtyn9-sudo/Breakwater --exit-status
```

Dispatch the universe research refresh:

```bash
gh workflow run research.yml --repo 6ixtyn9-sudo/Breakwater --ref main
sleep 3
RUN_ID="$(gh run list --repo 6ixtyn9-sudo/Breakwater --workflow research.yml --branch main --limit 1 --json databaseId --jq '.[0].databaseId')"
gh run watch "$RUN_ID" --repo 6ixtyn9-sudo/Breakwater --exit-status
```

Dispatch the paper trading cycle (shadow mode; simulated fills, no orders reach the venue):

```bash
gh workflow run paper.yml --repo 6ixtyn9-sudo/Breakwater --ref main
sleep 3
RUN_ID="$(gh run list --repo 6ixtyn9-sudo/Breakwater --workflow paper.yml --branch main --limit 1 --json databaseId --jq '.[0].databaseId')"
gh run watch "$RUN_ID" --repo 6ixtyn9-sudo/Breakwater --exit-status
```

Important: GitHub secrets/variables are only available to your Python process if the workflow exports them into the job environment (`env:`). If you set:

- `BREAKWATER_ENABLE_SPOT_MARGIN_SHORTS`
- `BREAKWATER_SPOT_MARGIN_ACK`

…make sure the workflow job includes them in `env:` when you eventually go live.
