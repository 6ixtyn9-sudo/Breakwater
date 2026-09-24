"""Honest paper evidence for the promotion gate.

The gate in ``promotion.py`` is only as truthful as the numbers fed to it. This
module derives those numbers from the committed paper ledger, and it derives
them the hard way on purpose:

**One entry per signal.** Measured on the 2026-09-24 ledger, 251 counted closes
came from 208 distinct signal_ids, and the 43 duplicates carried +387.65 ZAR of
the +474.64 lifetime P&L. A record that pays the same signal out repeatedly is
not evidence of an edge, so the primary statistic counts each signal once and
the raw figure is reported next to it rather than instead of it. Both are
always printed; neither is hidden.

**Every population delta is named.** The lane gate reads ``lane_gate.ACTUAL_EXITS``
(which excludes ``slice_gap``); the equity line and the sizing basis include
those fills. Rather than pick one silently, this module reports the closes it
counts, the closes it excludes and why, so a reader can reconcile the scorecard
against the daily print.

Nothing here trades, promotes or writes to a venue. It computes evidence and
prints a verdict; writing a registry row is opt-in via the CLI.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from breakwater.lane_gate import ACTUAL_EXITS
from breakwater.promotion import PromotionDecision, PromotionEvidence, PromotionGate

# The scorecard reads the same real-close population the green gate does, so a
# lane's verdict and its promotion evidence cannot disagree about what a trade
# is. ``slice_gap`` fills are counted separately (see ``SUMMARY_FIELDS``).
GATE_EXITS = frozenset(ACTUAL_EXITS)


def _as_float(value, default: float = 0.0) -> float:
    try:
        number = float(str(value))
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def _parse_time(value) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def read_ledger(log_path: Path) -> list[dict]:
    if not log_path.exists():
        return []
    with log_path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def real_closes(rows: list[dict]) -> list[dict]:
    """Rows the green gate itself would count as a closed trade."""
    return [
        row
        for row in rows
        if str(row.get("outcome") or "") in {"win", "loss"}
        and str(row.get("exit_reason") or "") in GATE_EXITS
    ]


def dedupe_by_signal(closes: list[dict]) -> list[dict]:
    """First close per signal_id, in close order.

    A signal is one decision. Repeat closes of the same signal_id are the
    artifact this whole exercise is about, so they cannot also be the evidence.
    """
    ordered = sorted(closes, key=lambda row: str(row.get("closed_at") or ""))
    seen: set[str] = set()
    out: list[dict] = []
    for row in ordered:
        signal_id = str(row.get("signal_id") or "")
        if not signal_id:
            continue
        if signal_id in seen:
            continue
        seen.add(signal_id)
        out.append(row)
    return out


def drops_for_lane(closes: list[dict], lane: str | None) -> list[dict]:
    if lane is None:
        return closes
    return [
        row
        for row in closes
        if ("hip3" if str(row.get("slice_id") or "").startswith("hip3_") else "native")
        == lane
    ]


@dataclass(frozen=True)
class Scorecard:
    trades: int
    wins: int
    losses: int
    net_zar: float
    expectancy_zar: float
    profit_factor: float
    max_drawdown: float
    mean_net_r: float
    shadow_days: int
    first_close: str
    last_close: str

    @property
    def win_rate(self) -> float:
        return self.wins / self.trades if self.trades else 0.0


def summarise(closes: list[dict], *, seed_zar: float = 2000.0) -> Scorecard:
    """Trade statistics from a list of closes, net of fees (pnl_zar is net).

    Drawdown is measured on the equity curve the seed implies, as a fraction of
    peak equity - the same shape the promotion gate's ``max_drawdown > 0.20``
    check means.
    """
    ordered = sorted(closes, key=lambda row: str(row.get("closed_at") or ""))
    pnls = [_as_float(row.get("pnl_zar")) for row in ordered]
    wins = [value for value in pnls if value > 0]
    losses = [value for value in pnls if value <= 0]
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))

    equity = seed_zar
    peak = seed_zar
    max_dd = 0.0
    for value in pnls:
        equity += value
        peak = max(peak, equity)
        if peak > 0:
            max_dd = max(max_dd, (peak - equity) / peak)

    net_r_values = [
        _as_float(row.get("net_r"))
        for row in ordered
        if str(row.get("net_r") or "").strip()
    ]
    first = _parse_time(ordered[0].get("closed_at")) if ordered else None
    last = _parse_time(ordered[-1].get("closed_at")) if ordered else None
    days = 0
    if first is not None and last is not None:
        days = max(0, (last.date() - first.date()).days)

    return Scorecard(
        trades=len(pnls),
        wins=len(wins),
        losses=len(losses),
        net_zar=sum(pnls),
        expectancy_zar=(sum(pnls) / len(pnls)) if pnls else 0.0,
        profit_factor=(gross_win / gross_loss) if gross_loss > 0 else float("inf"),
        max_drawdown=max_dd,
        mean_net_r=(sum(net_r_values) / len(net_r_values)) if net_r_values else 0.0,
        shadow_days=days,
        first_close=first.date().isoformat() if first else "",
        last_close=last.date().isoformat() if last else "",
    )


@dataclass(frozen=True)
class ResearchEvidence:
    """What the research artifacts actually carry for one slice."""

    observations: int = 0
    fold_windows: int = 0
    fold_passes: int = 0

    @property
    def mapped_fields(self) -> dict[str, tuple[str, object]]:
        """Gate field -> (source, value). Printed so the mapping is auditable."""
        return {
            "backtest_trades": ("research: slice observations (n)", self.observations),
            "validation_trades": ("paper: counted closes, one per signal", "see card"),
            "walk_forward_windows": ("research: walk-forward folds", self.fold_windows),
            "walk_forward_passes": ("research: folds passed", self.fold_passes),
            "shadow_trades": ("paper: counted closes, one per signal", "see card"),
            "shadow_days": ("paper: first-to-last close span", "see card"),
            "shadow_expectancy": ("paper: mean net P&L per close", "see card"),
            "reconciliation_passes": ("live canary counter", 0),
            "protection_passes": ("live canary counter", 0),
        }


def build_evidence(
    *,
    strategy_id: str,
    card: Scorecard,
    research: ResearchEvidence | None = None,
) -> PromotionEvidence:
    """Map a paper scorecard + research artifact onto the gate's evidence contract.

    The mapping is deliberately explicit, because two of these fields are not
    what their names suggest and pretending otherwise is how a gate gets
    flattered:

    - ``backtest_trades`` is fed the slice's observation count ``n`` from the
      research pool. Discovery counts binned observations, not simulated
      trades; the artifacts simply do not carry a trade count, and this number
      is printed as observations wherever it appears.
    - ``validation_trades`` is fed the counted paper closes (one per signal).
      Those are genuine out-of-sample forward trades in a walk-forward-validated
      slice, which is what the field is asking about.
    - ``reconciliation_passes`` and ``protection_passes`` stay at 0. They are
      counted by the live canary against a real venue; paper cannot fake them,
      and they are what stands between CANARY_ELIGIBLE and LIVE_CAPPED.
    """
    research = research or ResearchEvidence()
    return PromotionEvidence(
        strategy_id=strategy_id,
        valr_native=True,
        costs_included=True,
        completed_bar_only=True,
        backtest_trades=research.observations,
        validation_trades=card.trades,
        walk_forward_windows=research.fold_windows,
        walk_forward_passes=research.fold_passes,
        net_expectancy=Decimal(str(round(card.expectancy_zar, 6))),
        profit_factor=Decimal(
            str(round(card.profit_factor, 6)) if math.isfinite(card.profit_factor) else "999"
        ),
        max_drawdown=Decimal(str(round(card.max_drawdown, 6))),
        shadow_trades=card.trades,
        shadow_days=card.shadow_days,
        shadow_expectancy=Decimal(str(round(card.expectancy_zar, 6))),
        reconciliation_passes=0,
        protection_passes=0,
        unresolved_events=0,
    )


def load_research_evidence(data_dir: Path) -> dict[str, ResearchEvidence]:
    """Walk-forward shape per slice, from the committed validated pools.

    Reads every ``validated_slices.csv`` under the research and HIP-3 lanes so a
    slice's gate evidence reflects the fold structure it was promoted on.
    """
    out: dict[str, ResearchEvidence] = {}
    for path in (
        data_dir / "research" / "validated_slices.csv",
        data_dir / "hip3" / "research" / "validated_slices.csv",
    ):
        if not path.exists():
            continue
        try:
            with path.open(newline="") as handle:
                for row in csv.DictReader(handle):
                    slice_id = str(row.get("slice_id") or "")
                    if not slice_id:
                        continue
                    try:
                        observations = int(float(row.get("n") or 0))
                    except (TypeError, ValueError):
                        observations = 0
                    # `folds` is a count (5), and `walk_forward_pass_pattern`
                    # is the per-fold verdict string ("01011") - not a list of
                    # fold ids. Read the count first, then fall back to the
                    # pattern length so a missing column still reports windows.
                    try:
                        windows = int(float(row.get("folds") or 0))
                    except (TypeError, ValueError):
                        windows = 0
                    if windows <= 0:
                        pattern = str(row.get("walk_forward_pass_pattern") or "").strip()
                        windows = len(pattern)
                    try:
                        passes = int(float(row.get("walk_forward_pass_count") or 0))
                    except (TypeError, ValueError):
                        passes = 0
                    prior = out.get(slice_id)
                    if prior is None or observations > prior.observations:
                        out[slice_id] = ResearchEvidence(
                            observations=observations,
                            fold_windows=windows,
                            fold_passes=passes,
                        )
        except OSError:
            continue
    return out


def evaluate(evidence: PromotionEvidence, *, live_armed: bool) -> PromotionDecision:
    return PromotionGate().evaluate(evidence, live_armed=live_armed)


def summary_lines(
    *,
    label: str,
    lane: str | None,
    raw_closes: list[dict],
    all_fills: list[dict],
    seed_zar: float,
) -> list[str]:
    """Printable reconciliation: what was counted, what was not, and why."""
    counted = dedupe_by_signal(raw_closes)
    raw = summarise(raw_closes, seed_zar=seed_zar)
    card = summarise(counted, seed_zar=seed_zar)
    excluded_fills = [
        row
        for row in all_fills
        if str(row.get("exit_reason") or "") not in GATE_EXITS
    ]
    gap_zar = sum(_as_float(row.get("pnl_zar")) for row in excluded_fills)
    duplicate_count = len(raw_closes) - len(counted)
    duplicate_zar = raw.net_zar - card.net_zar
    scope = f"{label}" + (f" [{lane}]" if lane else "")
    return [
        f"{scope}:",
        f"  counted closes (one per signal_id): {card.trades}  "
        f"({card.first_close} -> {card.last_close}, {card.shadow_days} days)",
        f"  wins/losses: {card.wins}/{card.losses} ({card.win_rate * 100:.1f}% win)",
        f"  net: {card.net_zar:+.2f} ZAR | expectancy {card.expectancy_zar:+.3f} ZAR/trade | "
        f"profit factor {card.profit_factor:.2f}",
        f"  max drawdown: {card.max_drawdown * 100:.2f}% of peak equity | "
        f"mean net R {card.mean_net_r:+.3f}",
        f"  raw ledger closes: {raw.trades} | {raw.net_zar:+.2f} ZAR  "
        f"(duplicate signal closes removed: {duplicate_count}, {duplicate_zar:+.2f} ZAR)",
        f"  real fills outside the gate population: {len(excluded_fills)} "
        f"({gap_zar:+.2f} ZAR) - reported, not counted, matching lane_gate",
    ]


__all__ = [
    "GATE_EXITS",
    "ResearchEvidence",
    "Scorecard",
    "build_evidence",
    "dedupe_by_signal",
    "drops_for_lane",
    "evaluate",
    "load_research_evidence",
    "read_ledger",
    "real_closes",
    "summarise",
    "summary_lines",
]
