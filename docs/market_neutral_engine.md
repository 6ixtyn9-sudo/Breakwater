# Market-neutral long/short engine — scoping note

Status: **research-only**. Nothing in this note trades, promotes, or changes a
gate. It defines the evidence that must exist before an engine is built, and
the engine's shape if that evidence arrives.

## 1. Thesis

Every validated slice today is a LONG. That is not because the market only
offers longs; it is because `mean_positive` is scored on *raw* returns, and the
sample's market drift is positive. On a rising sample a raw-return gate admits
longs and rejects shorts regardless of whether the feature carries
cross-sectional information. It is, structurally, a beta gate.

The residualized scoring added in #13 exposed the asymmetry directly. On the
2026-10-17 run:

| slice | resid alpha (bps) | folds | raw mean (bps) | only failing gate |
|---|---|---|---|---|
| `feat_vol_regime:0:SHORT:h24` | +31.2 | 11110 | −45.3 | `mean_net<=0` |
| `feat_vol_regime:0:SHORT:h20` | +29.2 | 11110 | −39.0 | `mean_net<=0` |
| `feat_vol_regime:0:SHORT:h15` | +24.5 | 11110 | −31.0 | `mean_net<=0` |

(`feat_vol_contraction:0:SHORT` is the same slice under another name.) The
symbols the signal says to short *do* underperform peers by 25–31 bps per
trade after costs — they just do not fall outright in a rising tape.

A cross-sectional signal traded outright inherits the tape. The instrument that
collects a cross-sectional signal without the tape is the **spread**: long the
names in one state, short the names in the opposite state, dollar-neutral,
same horizon, same stop rule, on a venue where both legs are cheap and
short-able. That venue is Hyperliquid perps (9 bps round trip per leg vs 70 bps
on ZAR spot, and spot cannot short).

## 2. What is now measured (this PR)

`src/breakwater/spread_research.py` runs inside the existing research pass on
PERP shards only and writes `localdata/research/spread_slices.csv` (merged
across horizon shards by the workflow, committed by `commit_state.sh`, and
summarised in section 8 of the daily print).

For every feature, horizon, and pairing (`L2S0` = long state 2 / short state 0,
and the reverse `L0S2`), per bar `t`:

```
long_leg(t)  = mean fwd_trade_net_long  over symbols in long_state  at t
short_leg(t) = mean fwd_trade_net_short over symbols in short_state at t
spread(t)    = 0.5 * (long_leg + short_leg)      # return on gross notional
```

Both legs use the same stop-aware, cost-adjusted trade model as directional
research, so each leg pays the 9 bps perp round trip. Bars with fewer than 3
names on either side are skipped (`BREAKWATER_SPREAD_MIN_LEG_SYMBOLS`).

Reported per spread: `n_bars`, `n_nonoverlap` (stride-`h` subsample, because
hourly bars with an `h`-bar horizon overlap), `mean_ret_costadj`, both leg
means, hit rate, naive and non-overlap `t`, 5-fold walk-forward pattern with
horizon purge, worst fold, last-20% mean, max drawdown of the non-overlap
cumulative series, `market_corr` (correlation of the spread with the universe
raw return — the neutrality check), and average leg breadth.

`qualifies` is true when **all** hold (env-tunable, defaults shown):

| check | default | why |
|---|---|---|
| `n_nonoverlap >= 30` | `BREAKWATER_SPREAD_MIN_NONOVERLAP` | enough independent observations |
| `mean_ret_costadj > 0` | — | positive after both legs' costs |
| `t_nonoverlap >= 2.0` | `BREAKWATER_SPREAD_MIN_T` | significance on non-overlapping bars |
| `fold_pass_count >= 4` of 5 | `BREAKWATER_SPREAD_MIN_FOLD_PASSES` | stability through time |
| `abs(market_corr) <= 0.30` | `BREAKWATER_SPREAD_MAX_MARKET_CORR` | it is actually neutral |

The `market_corr` check matters more than it looks. In the synthetic crash test
the `L2S0` spread is *positive* with `t ≈ 2.9` — because stops truncate the
long leg while the short leg runs — and its market correlation is −0.88. That
is a crash bet, not alpha, and the check rejects it. Expect the same shape on
real data in any sample with a sharp move.

Synthetic sanity (tests): planted cross-sectional alpha qualifies only in the
correct pairing (`11111`, `market_corr ≈ 0.16`); a pure-beta universe produces
spreads near −9 bps (one leg of costs) and nothing qualifies.

## 3. Go / no-go gates

Build the paper engine only when, on the merged `spread_slices.csv`:

1. **Persistence** — at least one spread qualifies on **three consecutive**
   research runs (the file is overwritten each run; the daily print history in
   `localdata/daily/` is the record).
2. **Magnitude** — that spread's `mean_ret_costadj` is at least **+15 bps** on
   gross notional (≈ +30 bps on one leg's notional), leaving room for funding
   and slippage that the research does not model.
3. **Breadth** — `avg_n_long` and `avg_n_short` both ≥ 4, so a leg is never one
   name.
4. **Not a stop artefact** — `abs(market_corr) <= 0.30` on all three runs and
   `worst_fold_mean > −mean_ret_costadj` (no fold loses more than the average
   fold earns).
5. **Agreement with the directional read** — the long-state leg and short-state
   leg individually show positive residual alpha in `validated_slices.csv`
   (`alpha_bps > 0`) for the same feature and horizon. The spread must not be
   carried by one leg alone.

If gate 1 fails for four weeks, stop: the vol-regime SHORT finding was a
single-sample artefact and this note is closed.

## 4. Engine shape (only after the gates)

- **Universe**: Hyperliquid native perps only (not HIP-3; the HIP-3 lane is
  already net negative and has its own breadth problems). Minimum liquidity
  rank from `universe.csv`.
- **Signal**: the qualifying `feature × horizon × pairing`. State is the
  existing per-symbol expanding tercile, so no new feature code.
- **Position**: one *pair-position* per entry bar: long basket of state-2
  names, short basket of state-0 names, equal dollar on each side, equal weight
  within a basket, gross notional capped by the existing per-lane risk budget.
- **Exit**: joint. Both legs close at `h` bars or when the *spread* (not either
  leg) breaches the stop; a single-leg stop would re-introduce the exact
  asymmetry the `market_corr` check exists to catch.
- **Costs modelled in paper**: 9 bps per leg round trip, plus realised funding
  per 8h window per leg (Hyperliquid publishes it; it is currently not fetched
  — that fetch is a prerequisite task), plus a slippage haircut of 2 bps per
  leg on names outside the top-20 liquidity rank.
- **Sizing**: start at the lane minimum; promotion rules identical to the
  directional lanes (the registry does not need to know a position is a pair).
- **What has to change in code**: `paper_trade.py` positions are single-leg
  (`symbol`, `side`); a pair needs either a `group_id` linking two legs with a
  joint exit, or a synthetic instrument. The former is smaller and keeps the
  ledger per-leg honest. The guardian's open-risk summary must net the pair.

## 5. Risks and what they would look like

| risk | how it shows up in the evidence | mitigation |
|---|---|---|
| funding bleeds the spread | spread qualifies in research, paper lags by ≈ funding | fetch and log funding before paper; haircut gate 2 |
| short leg is the whole trade | `long_leg_mean ≈ 0`, gate 5 fails | require both legs' residual alpha |
| crash-stop artefact | `market_corr` strongly negative, folds `00111` style | `market_corr` check, joint exit |
| thin legs | `avg_n_*` < 3–4, high `max_drawdown` | breadth gate; liquidity floor |
| overlap inflation | `t_naive` ≫ `t_nonoverlap` | only `t_nonoverlap` counts |
| single-sample story | qualifies once, then not | persistence gate (3 runs) |

## 6. Open questions for the operator

- Is a 3-run persistence gate (≈ 3 weeks on the current cadence) acceptable, or
  should research run more often for this file alone? (It costs ~10 ms per
  feature-horizon; the cost is the shared frame fetch, not the spread maths.)
- Gross notional cap for a pair lane at seed: proposal is the same ZAR cap as
  one directional perp position, split across the two legs.
