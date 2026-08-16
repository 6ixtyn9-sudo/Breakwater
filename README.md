# Breakwater

Breakwater is a VALR-native, self-contained crypto universe research and
guarded execution system. It ingests the full VALR market universe, runs an
end-to-end research cycle over price-state slices, monitors the validated
book for signals, paper-trades those signals with stops and fees, and only
then allows a strategy to approach live execution through layered gates.
The venue remains authoritative for balances, orders, positions and fills.
The system is designed for periodic cloud execution through GitHub Actions
and does not depend on a local computer remaining powered.

`HANDOVER.md` is the living record: current posture, the lessons audit
against its predecessor system, known placeholders and the process rules.

## What it does, end to end

```text
VALR spot pairs + VALR Perps symbols
        |
        v
Universe ingestion (full universe, ranked, committed)
        |
        v
OHLCV research bars per symbol
        |
        v
Price-state features (extension, ATR, returns, volatility, trend)
        |
        v
Slice discovery (feature state bins x forward returns, side/cost-correct,
                  Bonferroni-controlled)
        |
        v
Walk-forward validation (time folds, pass patterns, recency required,
                        hostile-regime audit)
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
Risk-managed live execution (spot path; perps remain code-locked)
```

Nothing in this pipeline is a hand-authored strategy. Features are
descriptive price states; the system discovers which states carry stable
forward behaviour and only promotes slices that survive validation.

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
  unknown regimes never block. If a slice has hostile-regime evidence
  (`hostile_unproven=False`), gating can be relaxed to avoid biased
  evidence collection. Strict gating can be forced via
  `BREAKWATER_REGIME_GATE_STRICT=1`.
- **Regime-stratified validation.** Chronological walk-forward folds cannot
  distinguish a durable price-state edge from a regime artifact. Every slice
  is therefore also measured on its hostile-regime rows: bear rows for longs,
  bull rows for shorts. A slice whose hostile-regime mean net return is
  non-positive (at least 20 hostile rows) is marked `regime_confounded` and
  is not validated, with hostile evidence recorded.
- **Book-only paper trading.** Only slices promoted into the monitored book
  by walk-forward validation are paper-traded. Unvalidated fallback signals
  are research-only.
- **Immortal-trade guard.** Positions whose pair data has vanished are
  closed at entry with fees after 24 missing bars instead of living forever.
- **Stale-data refusal.** The universe snapshot is re-ingested if it is older
  than seven days.
- **Provenance honesty.** Every book row records the gate that promoted it
  (`validated_walk_forward`), so the audit trail never overstates the evidence
  behind the book.
- **Serialized state commits.** All workflows share one concurrency group,
  so two runs can never commit research and trading state to `main` at the
  same time.
- **Research and paper execution are separate workflows**, following the
  separation doctrine.
- **Stopout-only cooldown.** A slice cooldown is applied only on stopout-style
  adverse exits (stop / trail_stop / stale_data safety), not every small
  horizon loss.
- **Truth-metric paper feedback.** Paper logs preserve directional `outcome`,
  but lifecycle feedback is driven by after-fees truth (`pnl_outcome`).

Deliberate deviations from the predecessor system's anti-drift rules,
recorded honestly: the predecessor system forbade leverage entirely;
Breakwater permits per-position exchange leverage up to the mandate's cap
(default 3x) on VALR Perps only, where the isolated-margin model bounds the
worst-case loss of a position to its allocated margin.

## Instruments

- **VALR spot (cash)**: execution-capable after promotion; supports live long
  entries (BUY). Cash spot SELL is treated as reducing/closing exposure, not
  borrowing to short.
- **VALR spot margin (optional)**: Breakwater supports live spot-margin shorts
  (SELL to open), but this is **disabled by default** and requires explicit
  operator gating:
  - `BREAKWATER_ENABLE_SPOT_MARGIN_SHORTS=1`
  - `BREAKWATER_SPOT_MARGIN_ACK=I_ACCEPT_BREAKWATER_SPOT_MARGIN_RISK`

  Spot margin adds borrowing costs and liquidation risk. Paper/research do not
  model borrow interest or liquidation fees.
- **VALR Perps**: the USDC-quoted perpetual product on the main account,
  executing on Hyperliquid. Perp market data (candles, mark prices, volume,
  funding) is sourced from the Hyperliquid public info API and needs no VALR
  credentials, which is how the VALR web application sources it as well.
  Builder-listed pairs (xyz: prefixed) are skipped until their coin mapping is
  published. Research, shadow signals, positions and paper trading are supported.

  As of 2026-08-14, some VALR perps trading routes may be authenticated by web
  session only (HTTP 401 / code -93 to API keys). Breakwater probes this on every
  guardian run and records `perps_api` in the result, so the moment VALR opens the
  product to API keys the system will report it automatically. Live perp entry
  remains code-locked regardless, until take-profit and stop-loss semantics have
  passed an authenticated canary.

  Note that order execution, liquidation and mark prices are provider-managed,
  TPSL execution is not guaranteed, and position data synchronisation can lag.
- VALR-native sub-account futures are not targeted by this system.

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
these values at runtime. Averaging down, martingale, grids, withdrawals and
transfers are not implemented. Spot margin shorts are supported only behind
explicit operator gates and are off by default.

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
return.

Discovery and validation are **side/cost-correct**:

- raw return: `r = close[t+h] / close[t] - 1`
- LONG net: `r - cost`
- SHORT net: `-r - cost`

Discovery evaluates both sides per `(feature,state)` and chooses the side with
the higher net mean. Validation splits pooled rows into contiguous time folds;
a slice must pass most folds, including the most recent one, and must not be
regime-confounded in hostile rows.

The monitored book applies lifecycle gates on top of validation: a minimum
row count, the correct directional edge, live decay for slices that stop
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
BREAKWATER_MODE=shadow PYTHONPATH=src python scripts/breakwater.py shadow-scan --max-pairs 12
BREAKWATER_MODE=readonly PYTHONPATH=src python scripts/breakwater.py operate --max-pairs 12
PYTHONPATH=src python scripts/breakwater.py health
```

No credentials are needed for public market checks and the spot slice
research pass. Perp candle research and account reconciliation require the
API key.

### Connectivity canary

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

## GitHub configuration

```bash
gh secret set VALR_API_KEY --repo 6ixtyn9-sudo/Breakwater
gh secret set VALR_API_SECRET --repo 6ixtyn9-sudo/Breakwater

# mandate
gh secret set BREAKWATER_INITIAL_EQUITY_ZAR --repo 6ixtyn9-sudo/Breakwater
gh secret set BREAKWATER_ABSOLUTE_EQUITY_FLOOR_ZAR --repo 6ixtyn9-sudo/Breakwater
gh secret set BREAKWATER_MAX_TOTAL_LOSS_ZAR --repo 6ixtyn9-sudo/Breakwater
gh secret set BREAKWATER_MAX_TOTAL_DRAWDOWN_FRACTION --repo 6ixtyn9-sudo/Breakwater
gh secret set BREAKWATER_RISK_PER_TRADE_ZAR --repo 6ixtyn9-sudo/Breakwater
gh secret set BREAKWATER_DAILY_LOSS_LIMIT_ZAR --repo 6ixtyn9-sudo/Breakwater
gh secret set BREAKWATER_SEVEN_DAY_LOSS_LIMIT_ZAR --repo 6ixtyn9-sudo/Breakwater
gh secret set BREAKWATER_MAX_AGGREGATE_OPEN_RISK_ZAR --repo 6ixtyn9-sudo/Breakwater
gh secret set BREAKWATER_MAX_POSITION_NOTIONAL_ZAR --repo 6ixtyn9-sudo/Breakwater
gh secret set BREAKWATER_MAX_EFFECTIVE_LEVERAGE --repo 6ixtyn9-sudo/Breakwater
gh secret set BREAKWATER_PERP_LEVERAGE_CAP --repo 6ixtyn9-sudo/Breakwater
gh secret set BREAKWATER_MAX_POSITIONS --repo 6ixtyn9-sudo/Breakwater

# mode
gh variable set BREAKWATER_MODE --body readonly --repo 6ixtyn9-sudo/Breakwater

# optional spot margin gates (only relevant in live mode)
gh secret set BREAKWATER_ENABLE_SPOT_MARGIN_SHORTS --repo 6ixtyn9-sudo/Breakwater
gh secret set BREAKWATER_SPOT_MARGIN_ACK --repo 6ixtyn9-sudo/Breakwater

gh secret list --repo 6ixtyn9-sudo/Breakwater
```

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
```

Notes:
- GitHub Actions variables are visible as plain text; secrets are encrypted.
- Even if you set spot margin gates in repo variables or secrets, they only
  take effect for Actions if the workflow exports them into the job `env:`.

For example, in a workflow:

```yaml
env:
  BREAKWATER_ENABLE_SPOT_MARGIN_SHORTS: ${{ secrets.BREAKWATER_ENABLE_SPOT_MARGIN_SHORTS }}
  BREAKWATER_SPOT_MARGIN_ACK: ${{ secrets.BREAKWATER_SPOT_MARGIN_ACK }}
```
