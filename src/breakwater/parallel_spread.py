"""Fail-closed preflight and isolated paths for the dormant spread engine.

This module is intentionally not imported by the baseline paper engine or any
workflow. It defines the pre-registered research gate and the storage namespace
for the future parallel lane; it does not fetch data, create files, or trade.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

MIN_CONSECUTIVE_RESEARCH_RUNS = 3
MIN_NONOVERLAP_BARS = 30
MIN_MEAN_RET_COSTADJ = 0.0015  # +15 bps on gross notional
MIN_T_NONOVERLAP = 2.0
MIN_FOLD_PASSES = 4
MAX_ABS_MARKET_CORR = 0.30
MIN_LEG_BREADTH = 4.0


@dataclass(frozen=True)
class SpreadRunEvidence:
    """Evidence for one spread from one completed research run.

    Runs must be supplied oldest-to-newest. ``research_qualifies`` is the
    source spread-research row's qualification flag. ``long_alpha_bps`` and
    ``short_alpha_bps`` are the matching legs' residual alpha from that same
    run's validated-slice output; missing evidence must fail closed as zero.
    """

    run_id: str
    spread_id: str
    kind: str
    research_qualifies: bool
    n_nonoverlap: int
    mean_ret_costadj: float
    t_nonoverlap: float
    fold_pass_count: int
    worst_fold_mean: float
    market_corr: float
    avg_n_long: float
    avg_n_short: float
    long_alpha_bps: float
    short_alpha_bps: float


@dataclass(frozen=True)
class ResearchGateResult:
    ready: bool
    reasons: tuple[str, ...]


def _finite_float(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def evaluate_research_gate(runs: Sequence[SpreadRunEvidence]) -> ResearchGateResult:
    """Require one spread to pass every pre-paper gate on 3 successive runs.

    The caller supplies one row per completed run, ordered by run time. This
    checks the last three supplied rows; it does not infer missing runs from
    calendar dates, so callers must pass the last three consecutive successful
    research runs (not arbitrary historical rows).
    """
    if len(runs) < MIN_CONSECUTIVE_RESEARCH_RUNS:
        return ResearchGateResult(False, ("need_three_consecutive_runs",))

    recent = tuple(runs[-MIN_CONSECUTIVE_RESEARCH_RUNS:])
    reasons: list[str] = []
    run_ids = [str(run.run_id or "").strip() for run in recent]
    spread_ids = [str(run.spread_id or "").strip() for run in recent]
    if any(not run_id for run_id in run_ids):
        reasons.append("missing_run_id")
    if len(set(run_ids)) != MIN_CONSECUTIVE_RESEARCH_RUNS:
        reasons.append("run_ids_not_distinct")
    if len(set(spread_ids)) != 1:
        reasons.append("spread_id_not_persistent")
    if any(not spread_id for spread_id in spread_ids):
        reasons.append("missing_spread_id")
    if any(str(run.kind or "").upper() != "PERP" for run in recent):
        reasons.append("non_perp_evidence")

    numeric_fields = (
        "n_nonoverlap",
        "mean_ret_costadj",
        "t_nonoverlap",
        "fold_pass_count",
        "worst_fold_mean",
        "market_corr",
        "avg_n_long",
        "avg_n_short",
        "long_alpha_bps",
        "short_alpha_bps",
    )
    for index, run in enumerate(recent, start=1):
        prefix = f"run_{index}"
        if run.research_qualifies is not True:
            reasons.append(f"{prefix}_research_row_not_qualified")
        values = {field: _finite_float(getattr(run, field)) for field in numeric_fields}
        invalid = [field for field, value in values.items() if value is None]
        if invalid:
            reasons.extend(f"{prefix}_invalid_{field}" for field in invalid)
            continue

        if values["n_nonoverlap"] < MIN_NONOVERLAP_BARS:
            reasons.append(f"{prefix}_insufficient_nonoverlap")
        if values["mean_ret_costadj"] < MIN_MEAN_RET_COSTADJ:
            reasons.append(f"{prefix}_mean_below_15bps")
        if values["t_nonoverlap"] < MIN_T_NONOVERLAP:
            reasons.append(f"{prefix}_nonoverlap_too_low")
        if values["fold_pass_count"] < MIN_FOLD_PASSES:
            reasons.append(f"{prefix}_too_few_fold_passes")
        if abs(values["market_corr"]) > MAX_ABS_MARKET_CORR:
            reasons.append(f"{prefix}_market_corr_too_high")
        if values["avg_n_long"] < MIN_LEG_BREADTH:
            reasons.append(f"{prefix}_long_leg_too_thin")
        if values["avg_n_short"] < MIN_LEG_BREADTH:
            reasons.append(f"{prefix}_short_leg_too_thin")
        if values["worst_fold_mean"] <= -values["mean_ret_costadj"]:
            reasons.append(f"{prefix}_worst_fold_too_weak")
        if values["long_alpha_bps"] <= 0:
            reasons.append(f"{prefix}_long_leg_alpha_not_positive")
        if values["short_alpha_bps"] <= 0:
            reasons.append(f"{prefix}_short_leg_alpha_not_positive")

    return ResearchGateResult(not reasons, tuple(reasons))


@dataclass(frozen=True)
class ParallelSpreadPaths:
    """Separate storage paths; constructing them has no filesystem effects."""

    root: Path
    book: Path
    positions: Path
    ledger: Path
    status: Path

    @classmethod
    def under(cls, data_dir: Path | str) -> ParallelSpreadPaths:
        root = Path(data_dir) / "parallel_spread"
        return cls(
            root=root,
            book=root / "book.csv",
            positions=root / "positions.json",
            ledger=root / "ledger.csv",
            status=root / "status.json",
        )

    @property
    def files(self) -> tuple[Path, ...]:
        return (self.book, self.positions, self.ledger, self.status)

    def assert_disjoint_from(self, protected_paths: Iterable[Path | str]) -> None:
        """Raise if any parallel output would overwrite a protected baseline file."""
        owned = {path.resolve() for path in self.files}
        protected = {Path(path).resolve() for path in protected_paths}
        conflicts = sorted(str(path) for path in owned & protected)
        if conflicts:
            raise ValueError("parallel spread paths overlap protected files: " + ", ".join(conflicts))
