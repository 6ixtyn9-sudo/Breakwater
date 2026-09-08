"""Green-account gate: only let money keep flowing where it has printed green.

The daily-print mantra is "all lanes printing green." This module turns that
into a runtime entry/exit gate the engine consults on every paper cycle:

- A **lane** is green when its closed paper P&L is positive and it has enough
  closed trades to mean anything.
- A **slice** is green when its own closed paper P&L is positive. A slice with
  no closed trades is only allowed while its containing lane is not proven red,
  so an untested slice cannot be traded inside a losing lane.
- A lane that is not green is **frozen**: no new entries from it. Open positions
  are **not** force-closed; they exit on their own stop, target or horizon.
- A slice that is individually not green is blocked (and open positions in it
  are exited) even if the lane is otherwise green.
- **Cold-start aware:** a lane with fewer than LANE_MIN_CLOSED real closes is
  *warm-up*, not frozen. It has no evidence to be called red, so it is allowed
  to keep trading and accumulate the closes needed for a real verdict. Only a
  lane that has reached LANE_MIN_CLOSED and still prints negative P&L is frozen
  (proven red). This is what makes a fresh-slate / new-lane start possible
  without hand-disabling the gate.

Forced liquidation is retired (2026-09-08)
------------------------------------------
Until 2026-09-08 a red lane also force-closed every open position inside it at
the latest bar close (`exit_reason="lane_gate"`). That behaviour was removed on
purpose, in code, not flag-guarded.

Measured cost, on committed state: of 72 real closes between 02 and 08 Sep,
**32 (44%) were forced `lane_gate` exits** rather than stop/target/horizon. The
prospective exit counterfactual control (`target_2r_trail_1r`) reproduces real
exits to the cent on every natural exit (mean delta **+0.00 ZAR** on stop,
target, horizon, trail_stop and rotated) but scores **+4.56 ZAR/trade better on
the 31 trades the gate liquidated — +141.4 ZAR in total**. That is the single
largest P&L line in the log, and it was entirely self-inflicted.

It also fed back into the verdict: forced exits realise losers immediately,
which pushes cumulative lane P&L down, which keeps the lane red, which forces
the next liquidation. The reflex was manufacturing the evidence that justified
it. A position's stop is already the risk control; closing it early at an
arbitrary bar is not protection, it is a P&L event.

`lane_gate` stays in ``ACTUAL_EXITS`` so those 32 historical rows remain
countable. Dropping it would silently rewrite the very lane statistics the gate
reads to make its next decision.

Calibration (env-overridable):
  BREAKWATER_GREEN_LANE_MIN_CLOSED (default 10)   - closes a lane needs before it
                                                    can be called green.
  BREAKWATER_GREEN_SLICE_MIN_CLOSED (default 3)   - closes before a slice in a
                                                    green lane is judged non-green.
  BREAKWATER_GREEN_ISLAND_MIN_CLOSED (default 3)  - closes a slice needs to be a
                                                    green island inside a red lane.

Lane freeze is per-lane. A lane that has **no evidence** (fewer than
LANE_MIN_CLOSED real closes) is in **warm-up**: it is allowed to trade so it can
earn the closes needed for a real verdict, and it is reported in
`green_gate.warmup_lanes`. A lane that has **reached** LANE_MIN_CLOSED and still
prints negative P&L is frozen (proven red). HIP-3 paper volume is structurally
much lower than native, so HIP-3 typically stays in warm-up (allowed but low
evidence) longer than native; it only freezes once it has gathered the same
minimum and still failed. Inspect green_gate in the shadow_scan result or
status.csv to see which lanes are frozen vs warm-up and which slices are blocked.

This is paper observation logic: it never promotes anything, never writes to a
venue, and never loosens any research bar. It only stops *more* money from
flowing into lanes/slices that have not printed green.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

GREEN_GATE_ENABLED = str(os.getenv("BREAKWATER_GREEN_GATE", "1")).strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
LANE_MIN_CLOSED = int(os.getenv("BREAKWATER_GREEN_LANE_MIN_CLOSED", "10"))
# A slice is judged non-green only after enough closed trades to mean something.
# Judging on one loss is how you end up with no action: one stop would freeze
# a slice that was merely unlucky. The paper engine already uses 3 as its
# losing-slice threshold; the green gate must not be tighter or it zeroes action.
SLICE_MIN_CLOSED = int(os.getenv("BREAKWATER_GREEN_SLICE_MIN_CLOSED", "3"))

# 20 closes is ~4 days at current throughput: long enough to be a verdict,
# short enough that a lane which stops losing is allowed to trade again.
LANE_WINDOW = 20
# A slice inside a non-green lane can keep trading only when it is an
# individually proven green island (enough closed trades at positive P&L).
GREEN_ISLAND_MIN_CLOSED = int(os.getenv("BREAKWATER_GREEN_ISLAND_MIN_CLOSED", "3"))

PROBE_UNTESTED = True

# Exits that count as real closed trades when judging whether a lane/slice has
# printed money. Guard rows (regime/risk/session aggregates with no pnl) and
# generic "skipped" rows must not pollute the money signal.
ACTUAL_EXITS = {
    "stop",
    "trail_stop",
    "target",
    "horizon",
    "rotated",
    "time_stop",
    "regime_shift",
    "lane_gate",
}
_MISSING = object()


def _csv_rows(path: Path) -> Iterable[dict]:
    if not path.exists():
        return
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            yield row


def _as_float(value, default: float = 0.0) -> float:
    if value is _MISSING:
        return default
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return default


def _as_int(value, default: int = 0) -> int:
    if value is _MISSING:
        return default
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return default


def _lane(slice_id: object) -> str:
    return "hip3" if str(slice_id or "").startswith("hip3_") else "native"


def _is_real_close(row: dict) -> bool:
    outcome = str(row.get("outcome") or "").strip()
    exit_reason = str(row.get("exit_reason") or "").strip()
    return outcome in {"win", "loss"} and exit_reason in ACTUAL_EXITS


@dataclass
class LaneStats:
    closed: int
    pnl: float
    wins: int
    losses: int


@dataclass
class SliceStats:
    closed: int
    pnl: float
    wins: int
    losses: int


@dataclass
class GreenGate:
    native: LaneStats
    hip3: LaneStats
    slices: dict[str, SliceStats]
    native_green: bool
    hip3_green: bool
    frozen_lanes: set[str]
    warmup_lanes: set[str]
    blocked_slices: dict[str, str]
    enabled: bool

    def green(self, slice_id: str) -> bool:
        """True when a slice may still open new entries under the gate."""
        if not self.enabled:
            return True
        if str(slice_id) in self.blocked_slices:
            return False
        lane = _lane(slice_id)
        if lane not in self.frozen_lanes:
            return True
        if PROBE_UNTESTED:
            stats = self.slices.get(str(slice_id))
            if stats is None or stats.closed < SLICE_MIN_CLOSED:
                return True
        return str(slice_id) in self.green_islands

    # FORCED LIQUIDATION IS RETIRED (2026-09-08). ``should_exit()`` used to live
    # here and the paper engine called it to dump any open position whose lane
    # had flipped red. It is deliberately gone, not flag-guarded: see
    # "Forced liquidation is retired" in the module docstring for the
    # measurement that killed it. Do not reinstate it behind a switch - the
    # switch is what made it look safe the first time.

    @property
    def green_islands(self) -> dict[str, float]:
        """Slices kept alive inside a non-green lane (provable gainers)."""
        out: dict[str, float] = {}
        for slice_id, stats in self.slices.items():
            if (
                _lane(slice_id) in self.frozen_lanes
                and stats.closed >= GREEN_ISLAND_MIN_CLOSED
                and stats.pnl > 0
            ):
                out[slice_id] = round(stats.pnl, 4)
        return dict(sorted(out.items()))

    @property
    def summary(self) -> dict:
        return {
            "enabled": self.enabled,
            "native_green": self.native_green,
            "hip3_green": self.hip3_green,
            "frozen_lanes": sorted(self.frozen_lanes),
            "warmup_lanes": sorted(self.warmup_lanes),
            "lane_min_closed": LANE_MIN_CLOSED,
            "slice_min_closed": SLICE_MIN_CLOSED,
            "green_island_min_closed": GREEN_ISLAND_MIN_CLOSED,
            "green_islands": self.green_islands,
            "blocked_slices": dict(sorted(self.blocked_slices.items())),
            "native": {
                "closed": self.native.closed,
                "pnl": round(self.native.pnl, 4),
                "wins": self.native.wins,
                "losses": self.native.losses,
                "warmup": "native" in self.warmup_lanes,
            },
            "hip3": {
                "closed": self.hip3.closed,
                "pnl": round(self.hip3.pnl, 4),
                "wins": self.hip3.wins,
                "losses": self.hip3.losses,
                "warmup": "hip3" in self.warmup_lanes,
            },
        }


def _aggregate(rows: Iterable[dict]) -> tuple[LaneStats, LaneStats, dict[str, SliceStats]]:
    """Lifetime stats per slice; lane stats over the last LANE_WINDOW closes."""
    slice_counts: dict[str, dict] = {}
    lane_rows: dict[str, list] = {"native": [], "hip3": []}

    # First pass per row keeps the association between a real exit and its slice.
    for row in rows:
        if not _is_real_close(row):
            continue
        slice_id = str(row.get("slice_id") or "")
        lane = _lane(slice_id)
        pnl = _as_float(row.get("pnl_zar"))
        outcome = str(row.get("outcome") or "").strip()
        entry = slice_counts.setdefault(slice_id, {"closed": 0, "pnl": 0.0, "wins": 0, "losses": 0})
        entry["closed"] += 1
        entry["pnl"] += pnl
        if outcome == "win":
            entry["wins"] += 1
        elif outcome == "loss":
            entry["losses"] += 1
        if lane in lane_rows:
            lane_rows[lane].append((pnl, outcome))

    def lane_stats(lane: str) -> dict:
        # The log is append-only and ordered by close time, so the tail is the
        # recent record. Slicing the tail is the whole fix.
        closes = lane_rows[lane]
        if LANE_WINDOW > 0:
            closes = closes[-LANE_WINDOW:]
        return {
            "closed": len(closes),
            "pnl": sum(value for value, _ in closes),
            "wins": sum(1 for _, outcome in closes if outcome == "win"),
            "losses": sum(1 for _, outcome in closes if outcome == "loss"),
        }

    return (
        LaneStats(**lane_stats("native")),
        LaneStats(**lane_stats("hip3")),
        {key: SliceStats(**value) for key, value in slice_counts.items()},
    )


def compute_green_gate(log_path: Path) -> GreenGate:
    enabled = GREEN_GATE_ENABLED
    native, hip3, slices = _aggregate(_csv_rows(log_path))

    native_warmup = native.closed < LANE_MIN_CLOSED
    hip3_warmup = hip3.closed < LANE_MIN_CLOSED
    native_green = not native_warmup and native.pnl > 0
    hip3_green = not hip3_warmup and hip3.pnl > 0

    # Warm-up lanes have not gathered enough closes to be called red; they are
    # allowed to trade so a cold start can build the evidence the gate needs.
    # Only lanes that have reached the minimum and still print negative P&L
    # are frozen (proven red).
    frozen_lanes: set[str] = set()
    warmup_lanes: set[str] = set()
    if not native_green:
        if native_warmup:
            warmup_lanes.add("native")
        else:
            frozen_lanes.add("native")
    if not hip3_green:
        if hip3_warmup:
            warmup_lanes.add("hip3")
        else:
            frozen_lanes.add("hip3")

    blocked_slices: dict[str, str] = {}
    for slice_id, stats in slices.items():
        lane = _lane(slice_id)
        # A green island: enough closed trades, positive P&L. It survives a
        # red lane so the lane can keep printing green from its one working
        # slice while every non-green member is frozen.
        is_green_island = (
            lane in frozen_lanes and stats.closed >= GREEN_ISLAND_MIN_CLOSED and stats.pnl > 0
        )
        if lane in frozen_lanes:
            # Red lane: nothing trades unless it is a proven green island.
            # An untested or negative slice is frozen; stopping this is the
            # whole point of a red lane.
            if not is_green_island and not (PROBE_UNTESTED and stats.closed < SLICE_MIN_CLOSED):
                blocked_slices[slice_id] = "lane_not_green"
            continue
        # Warm-up or green lane: an untested slice (0-2 closes) is free to earn
        # its noise. Only judge non-green after SLICE_MIN_CLOSED closed trades,
        # so one stop does not freeze the book into inaction. A proven-negative
        # slice is blocked even in a warm-up lane so a cold start cannot keep
        # feeding a slice that has already printed red.
        if stats.closed >= SLICE_MIN_CLOSED and stats.pnl <= 0:
            blocked_slices[slice_id] = f"slice_pnl={stats.pnl:+.2f}"
            continue

    return GreenGate(
        native=native,
        hip3=hip3,
        slices=slices,
        native_green=native_green,
        hip3_green=hip3_green,
        frozen_lanes=frozen_lanes,
        warmup_lanes=warmup_lanes,
        blocked_slices=blocked_slices,
        enabled=enabled,
    )


def lane_tradability(
    gate: GreenGate,
    native_book_ids: Iterable[str],
    hip3_book_ids: Iterable[str],
) -> dict:
    """Report how many slices per lane may still open an entry, and any coma.

    A frozen lane can reach **zero** tradable slices: every member is blocked and
    no green island survives. At that point the lane cannot open an entry, so it
    can never print the closes that would turn it green again. That is an
    absorbing state, not a slow day. It must be reported loudly instead of
    sitting in silence while the runner cheerfully reports "operational", which
    is exactly how the 02-08 Sep freeze ran for five days unseen.
    """
    native = sorted({str(s) for s in native_book_ids if gate.green(s)})
    hip3 = sorted({str(s) for s in hip3_book_ids if gate.green(s)})

    def proven(lane: str, allowed: list[str]) -> int:
        """Slices trading on a record they have already earned.

        Inside a frozen lane the only proven slices are green islands; elsewhere
        admitted == proven. Audition slots from PROBE_UNTESTED are excluded on
        purpose: they are evidence-gathering, not evidence. If alarms counted
        them, a lane kept alive only by new ideas would read as healthy.
        """
        if lane in gate.frozen_lanes:
            return sum(1 for slice_id in allowed if slice_id in gate.green_islands)
        return len(allowed)

    coma = sorted(
        lane
        for lane, allowed in (("native", native), ("hip3", hip3))
        if lane in gate.frozen_lanes and proven(lane, allowed) == 0
    )
    return {
        "native_tradable": len(native),
        "hip3_tradable": len(hip3),
        "native_proven": proven("native", native),
        "hip3_proven": proven("hip3", hip3),
        "native_tradable_slices": native,
        "hip3_tradable_slices": hip3,
        "coma_lanes": coma,
        "coma": bool(coma),
    }


def filter_green_book_rows(rows: Iterable[dict], gate: GreenGate) -> tuple[list[dict], list[dict]]:
    """Split book rows into allowed and blocked by the green gate."""
    allowed: list[dict] = []
    blocked: list[dict] = []
    for row in rows:
        slice_id = str(row.get("slice_id") or "")
        if gate.green(slice_id):
            allowed.append(row)
        else:
            blocked.append(
                {
                    "slice_id": slice_id,
                    "reason": gate.blocked_slices.get(slice_id, "lane_not_green"),
                    "lane": _lane(slice_id),
                }
            )
    return allowed, blocked
