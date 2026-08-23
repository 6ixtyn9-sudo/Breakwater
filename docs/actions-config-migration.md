# GitHub Actions configuration migration

Breakwater supports one consolidated private capital mandate through
`BREAKWATER_MANDATE_JSON`. Research and paper knobs belong in GitHub Actions
**Variables**, not Secrets. The only repository Secrets expected after this
migration are:

- `VALR_API_KEY`
- `VALR_API_SECRET`
- `BREAKWATER_MANDATE_JSON`

A future Hyperliquid agent key should use a protected GitHub Environment, not
a repository secret. Never upload a Hyperliquid master key or recovery phrase.

## 1. Create non-sensitive Actions Variables

Create or verify these repository Variables before rewriting workflows. Values
shown are current doctrine defaults; preserve a deliberate existing value when
it differs.

| Variable | Default |
|---|---:|
| `BREAKWATER_MODE` | `readonly` |
| `BREAKWATER_LIVE_ACK` | `off` |
| `BREAKWATER_MIN_NET_EDGE` | `0.002` |
| `BREAKWATER_RESEARCH_HORIZONS` | `1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24` |
| `BREAKWATER_SPOT_CANDLE_COUNT` | `1000` |
| `BREAKWATER_PERP_CANDLE_COUNT` | `1000` |
| `BREAKWATER_DISCOVERY_STATE_QUANTILES` | `0.333333,0.666666` |
| `BREAKWATER_BREADTH_MIN_SYMBOLS` | `6` |
| `BREAKWATER_BREADTH_MIN_ROWS_PER_SYMBOL` | `10` |
| `BREAKWATER_BREADTH_MIN_POSITIVE_FRACTION` | `0.40` |
| `BREAKWATER_CONCENTRATED_PROMOTE` | `1` |
| `BREAKWATER_CONCENTRATED_MIN_MEAN` | `0.004` |
| `BREAKWATER_PROMOTION_MULTI_HORIZON_MIN_PASSES` | `2` |
| `BREAKWATER_PROMOTION_MULTI_HORIZON_SELECT` | `edge_per_bar` |
| `BREAKWATER_PAPER_ENTRY_MODE` | `aligned` |
| `BREAKWATER_PAPER_SELECTION_MODE` | `profit` |
| `BREAKWATER_PAPER_SESSIONS` | `eu,us` |
| `BREAKWATER_PAPER_R_GATE` | `1` |
| `BREAKWATER_ENABLE_SPOT_MARGIN_SHORTS` | `0` |
| `BREAKWATER_SPOT_MARGIN_ACK` | `off` |

Other workflow values already hard-coded or already read only from `vars.*` do
not need duplicate Secrets.

## 2. Create the consolidated mandate Secret

Secret values cannot be read back from GitHub. Reconstruct these values from
your original mandate records; do not infer or guess them from paper PnL.
Create an exact JSON object with all keys and no extras:

```json
{
  "initial_equity_zar": "REPLACE",
  "absolute_equity_floor_zar": "REPLACE",
  "max_total_loss_zar": "REPLACE",
  "max_drawdown_fraction": "REPLACE",
  "risk_per_trade_zar": "REPLACE",
  "daily_loss_limit_zar": "REPLACE",
  "seven_day_loss_limit_zar": "REPLACE",
  "max_aggregate_open_risk_zar": "REPLACE",
  "max_position_notional_zar": "REPLACE",
  "max_effective_leverage": "REPLACE",
  "perp_leverage_cap": "REPLACE",
  "max_positions": "REPLACE"
}
```

Store the minified object as repository Secret `BREAKWATER_MANDATE_JSON`.
Breakwater rejects missing keys, unknown keys, booleans, fractional
`max_positions`, malformed decimals, and simultaneous JSON plus legacy mandate
environment variables.

## 3. Rewrite workflows from an authorized Codespace

```bash
cd /workspaces/Breakwater
python scripts/migrate_actions_config.py
python scripts/migrate_actions_config.py --check

git diff -- .github/workflows
git add .github/workflows
git commit -m "Separate Actions variables from private secrets"
git push origin main
```

The migration keeps only `VALR_API_KEY`, `VALR_API_SECRET`, and
`BREAKWATER_MANDATE_JSON` as workflow Secret references.

## 4. Validate before deleting old Secrets

Manually run and inspect, in order:

1. `guardian.yml`
2. `paper.yml`
3. `research.yml`
4. `hip3-research.yml`

Confirm mandate parsing, paper cycle status, and research knobs. Keep all old
Secrets until these runs succeed.

## 5. Delete obsolete Secrets

After successful validation, delete the twelve individual mandate Secrets and
all non-sensitive strategy/configuration Secrets migrated to Variables. Also
delete the unused `FILTER_NONPOSITIVE_BOOK` Secret; the actual workflow key is
`BREAKWATER_FILTER_NONPOSITIVE_BOOK` and is explicitly set by `paper.yml`.
