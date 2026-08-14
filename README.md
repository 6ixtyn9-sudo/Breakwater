# Breakwater

Breakwater is a VALR-native, lower-frequency crypto trend research and guarded
execution system. It imports versioned crypto candidates from Price, rebuilds
the decision using VALR-native market data, and manages account risk through
broker-authoritative reconciliation.

Breakwater is designed for periodic cloud execution through GitHub Actions and
an external dispatcher. It does not depend on a local computer remaining
powered. VALR remains authoritative for balances, orders, positions and fills.

## Current release boundary

Version 0.1 provides:

- official VALR HMAC-SHA512 request signing;
- public market, pair, candle, funding and risk-limit access;
- authenticated balance, fee, order, position and conditional-order reads;
- fixed-point price and quantity handling;
- dynamic pair constraints and completed-candle filtering;
- Price candidate import through a versioned boundary;
- one-hour long and short trend-breakout shadow signals;
- immutable account, drawdown, daily and seven-day limits;
- a SQLite event ledger plus Git-durable bounded risk state;
- strategy promotion stages from research to live-capped;
- spot order planning with synchronous fill and stop confirmation;
- workflows for CI, account guarding, shadow scanning and research refresh.

The default mode is `readonly`. Spot writes require two independent live gates
and a strategy promoted to `live_capped`. Perpetual market data, research,
positions, leverage and shadow signals are supported, but perpetual live entry
is deliberately locked until VALR's reduce-only `conditionalOrderData` contract
has passed an authenticated canary and TPSL reconciliation checks. This avoids
using an unverified protection payload with real funds.

## Immutable capital mandate

The compiled starting mandate is:

| Boundary | Value |
|---|---:|
| Initial global equity | R331.45 |
| Permanent loss limit | R109.38 |
| Absolute equity floor | R222.07 |
| High-water drawdown halt | 33% |
| Risk per trade | R3.31 |
| Daily loss halt | R9.94 |
| Seven-day loss halt | R19.89 |
| Maximum aggregate open risk | R6.63 |
| Maximum position notional | R99.43 |
| Maximum effective leverage | 1x |
| Maximum simultaneous positions | 1 |

The strategy cannot modify these values. Averaging down, martingale, grids,
spot borrowing, withdrawals and transfers are not implemented.

VALR perpetuals require a futures-enabled subaccount. A main-account API key
with View and Trade permissions can be scoped to that subaccount using
`VALR_SUBACCOUNT_ID`; it must not have Transfer, Withdraw or Link Bank Account
permissions. A subaccount key can be used for read-only or shadow operation,
but live mode requires global account visibility so the R222.07 global floor
can be verified.

## Strategy lifecycle

Every strategy moves through:

```text
research_only
shadow_candidate
shadow_validated
canary_eligible
live_capped
suspended
retired
```

Promotion requires VALR-native data, completed bars, costs and funding,
chronological validation, walk-forward evidence, positive net expectancy,
forward shadow observations, reconciliation passes, protection checks and no
unresolved events. Arming the global live gate does not bypass these gates.

## Architecture

```text
Price research output
        |
        v
Price candidate importer
        |
        v
VALR-native candles and market checks
        |
        v
Big-wave detector and promotion registry
        |
        v
Risk manager and execution planner
        |
        v
VALR account, order and position reconciliation
```

`localdata/breakwater.db` is a cached transactional event ledger and is not
committed. `risk_state.json`, `promotion_registry.json`, `price_candidates.csv`
and bounded `status.csv` are committed so loss and promotion state survive
cache loss. Broker state is reconstructed every pass.

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

## Local read-only operation

```bash
cd Breakwater
source .venv/bin/activate
set -a
source .env
set +a
PYTHONPATH=src python scripts/breakwater.py guardian
PYTHONPATH=src python scripts/breakwater.py refresh-price
BREAKWATER_MODE=shadow PYTHONPATH=src python scripts/breakwater.py shadow-scan --max-pairs 12
BREAKWATER_MODE=readonly PYTHONPATH=src python scripts/breakwater.py operate --max-pairs 12
```

No credentials are needed for public market checks and shadow scanning. Account
reconciliation requires a VALR API key with View permission.

## GitHub configuration

Configure a View-only key first:

```bash
gh secret set VALR_API_KEY --repo 6ixtyn9-sudo/Breakwater
gh secret set VALR_API_SECRET --repo 6ixtyn9-sudo/Breakwater
gh secret set VALR_SUBACCOUNT_ID --repo 6ixtyn9-sudo/Breakwater
gh variable set BREAKWATER_MODE --body readonly --repo 6ixtyn9-sudo/Breakwater
gh secret list --repo 6ixtyn9-sudo/Breakwater
gh variable list --repo 6ixtyn9-sudo/Breakwater
```

Dispatch the account guardian:

```bash
gh workflow run guardian.yml --repo 6ixtyn9-sudo/Breakwater --ref main
sleep 3
RUN_ID="$(gh run list --repo 6ixtyn9-sudo/Breakwater --workflow guardian.yml --branch main --limit 1 --json databaseId --jq '.[0].databaseId')"
gh run watch "$RUN_ID" --repo 6ixtyn9-sudo/Breakwater --exit-status
```

Dispatch the Price import and VALR-native research refresh:

```bash
gh workflow run research.yml --repo 6ixtyn9-sudo/Breakwater --ref main
sleep 3
RUN_ID="$(gh run list --repo 6ixtyn9-sudo/Breakwater --workflow research.yml --branch main --limit 1 --json databaseId --jq '.[0].databaseId')"
gh run watch "$RUN_ID" --repo 6ixtyn9-sudo/Breakwater --exit-status
```

An external scheduler may dispatch `guardian.yml` every 15 to 30 minutes and
`research.yml` daily. GitHub Actions is not a continuous WebSocket process;
server-side protection and broker reconciliation are therefore mandatory.

## Live activation

Live mode is intentionally unavailable until all of the following are true:

- a dedicated API key has only View and Trade permissions;
- global account equity is observable;
- the target strategy is `live_capped`;
- account and order reconciliation is clean;
- the spot protection canary has passed;
- the permanent loss boundary is unchanged;
- the operator deliberately sets both live gates.

The gates are:

```text
BREAKWATER_MODE=live
BREAKWATER_LIVE_ACK=I_ACCEPT_BREAKWATER_LIVE_RISK
```

Do not set them during initial deployment. Perpetual live execution remains
code-locked even when both gates are set until the reduce-only TPSL integration
is proven against the authenticated VALR API.

## Operational outcomes

`localdata/status.csv` records bounded outcomes:

- `public_ok` means public exchange, time and pair metadata were available;
- `guardian_ok` means authenticated state and risk checks passed;
- `risk_halted` means an immutable loss or exposure gate blocked entries;
- `unprotected_position` means an open position lacked confirmed stop
  protection and requires immediate operator attention;
- `shadow_scan_done` records the number of pairs, signals and errors;
- `failed` means required state was unavailable or malformed.

A successful workflow is not proof of profitability, future fills or guaranteed
stop execution. It proves only the checks performed by that run.
