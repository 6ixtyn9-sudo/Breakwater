"""Green-account gate: only let money keep flowing where it has printed green.

The daily-print mantra is "all lanes printing green." This module turns that
into a runtime entry/exit gate the engine consults on every paper cycle:

- A **lane** is green when its closed paper P&L is positive and it has enough
  closed trades to mean anything.
- A **slice** is green when its own closed paper P&L is positive. A slice with
  no closed trades is only allowed while its containing lane is green, so an
  untested slice cannot be traded inside a losing lane.
- A lane that is not green is **frozen**: no new entries from it, and any open
  positions inside it are defensively exited at the latest close so the lane
  stops bleeding.
- A slice that is individually not green is blocked (and open positions in it
  are exited) even if the lane is otherwise green.

Calibration (env-overridable):
  BREAKWATER_GREEN_LANE_MIN_CLOSED (default 10)   - closes a lane needs before it
                                                    can be called green.
  BREAKWATER_GREEN_SLICE_MIN_CLOSED (default 3)   - closes before a slice in a
                                                    green lane is judged non-green.
  BREAKWATER_GREEN_ISLAND_MIN_CLOSED (default 3)  - closes a slice needs to be a
                                                    green island inside a red lane.

Lane freeze is per-lane. A lane with fewer than LANE_MIN_CLOSED real closes is
always frozen regardless of P&L because it has no evidence. HIP-3 paper volume is
structurally much lower than native, so HIP-3 typically remains frozen (and its
non-green slices blocked) until it accumulates the same minimum. That is
intentional: a low-evidence lane should not keep taking entries on a short
positive sample. Inspect green_gate in the shadow_scan result or status.csv to
see which lanes/slices are frozen.

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
    "1", "true", "yes", "on",
}
LANE_MIN_CLOSED = int(os.getenv("BREAKWATER_GREEN_LANE_MIN_CLOSED", "10"))
# A slice is judged non-green only after enough closed trades to mean something.
# Judging on one loss is how you end up with no action: one stop would freeze
# a slice that was merely unlucky. The paper engine already uses 3 as its
# losing-slice threshold; the green gate must not be tighter or it zeroes action.
SLICE_MIN_CLOSED = int(os.getenv("BREAKWATER_GREEN_SLICE_MIN_CLOSED", "3"))
# A slice inside a non-green lane can keep trading only when it is an
# individually proven green island (enough closed trades at positive P&L).
GREEN_ISLAND_MIN_CLOSED = int(os.getenv("BREAKWATER_GREEN_ISLAND_MIN_CLOSED", "3"))

# Exits that count as real closed trades when judging whether a lane/slice has
# printed money. Guard rows (regime/risk/session aggregates with no pnl) and
# generic "skipped" rows must not pollute the money signal.
ACTUAL_EXITS = {"stop", "trail_stop", "target", "horizon", "rotated", "time_stop", "regime_shift", "lane_gate"}
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
        return str(slice_id) in self.green_islands

    def should_exit(self, slice_id: str) -> bool:
        """True when an open position must be defensively closed."""
        if not self.enabled:
            return False
        return not self.green(slice_id)

    @property
    def green_islands(self) -> dict[str, float]:
        """Slices kept alive inside a non-green lane (provable gainers)."""
        out: dict[str, float] = {}
        for slice_id, stats in self.slices.items():
            if _lane(slice_id) in self.frozen_lanes and stats.closed >= GREEN_ISLAND_MIN_CLOSED and stats.pnl > 0:
                out[slice_id] = round(stats.pnl, 4)
        return dict(sorted(out.items()))

    @property
    def summary(self) -> dict:
        return {
            "enabled": self.enabled,
            "native_green": self.native_green,
            "hip3_green": self.hip3_green,
            "frozen_lanes": sorted(self.frozen_lanes),
            "green_islands": self.green_islands,
            "blocked_slices": dict(sorted(self.blocked_slices.items())),
            "native": {
                "closed": self.native.closed,
                "pnl": round(self.native.pnl, 4),
                "wins": self.native.wins,
                "losses": self.native.losses,
            },
            "hip3": {
                "closed": self.hip3.closed,
                "pnl": round(self.hip3.pnl, 4),
                "wins": self.hip3.wins,
                "losses": self.hip3.losses,
            },
        }


def _aggregate(rows: Iterable[dict]) -> tuple[LaneStats, LaneStats, dict[str, SliceStats]]:
    lane_counts = {
        "native": {"closed": 0, "pnl": 0.0, "wins": 0, "losses": 0},
        "hip3": {"closed": 0, "pnl": 0.0, "wins": 0, "losses": 0},
    }
    slice_counts: dict[str, dict] = {}

    # First pass per row keeps the association between a real exit and its slice.
    for row in rows:
        if not _is_real_close(row):
            continue
        slice_id = str(row.get("slice_id") or "")
        lane = _lane(slice_id)
        pnl = _as_float(row.get("pnl_zar"))
        outcome = str(row.get("outcome") or "").strip()
        entry = slice_counts.setdefault(
            slice_id, {"closed": 0, "pnl": 0.0, "wins": 0, "losses": 0}
        )
        for bucket in (lane_counts[lane], entry):
            bucket["closed"] += 1
            bucket["pnl"] += pnl
            if outcome == "win":
                bucket["wins"] += 1
            elif outcome == "loss":
                bucket["losses"] += 1

    native = lane_counts["native"]
    hip3 = lane_counts["hip3"]
    return (
        LaneStats(**native),
        LaneStats(**hip3),
        {key: SliceStats(**value) for key, value in slice_counts.items()},
    )


def compute_green_gate(log_path: Path) -> GreenGate:
    enabled = GREEN_GATE_ENABLED
    native, hip3, slices = _aggregate(_csv_rows(log_path))

    native_green = native.closed >= LANE_MIN_CLOSED and native.pnl > 0
    hip3_green = hip3.closed >= LANE_MIN_CLOSED and hip3.pnl > 0

    frozen_lanes: set[str] = set()
    if not native_green:
        frozen_lanes.add("native")
    if not hip3_green:
        frozen_lanes.add("hip3")

    blocked_slices: dict[str, str] = {}
    for slice_id, stats in slices.items():
        lane = _lane(slice_id)
        # A green island: enough closed trades, positive P&L. It survives a
        # red lane so the lane can keep printing green from its one working
        # slice while every non-green member is frozen.
        is_green_island = (
            lane in frozen_lanes
            and stats.closed >= GREEN_ISLAND_MIN_CLOSED
            and stats.pnl > 0
        )
        if lane in frozen_lanes:
            # Red lane: nothing trades unless it is a proven green island.
            # An untested or negative slice is frozen; stopping this is the
            # whole point of a red lane.
            if not is_green_island:
                blocked_slices[slice_id] = "lane_not_green"
            continue
        # Green lane: an untested slice (0-2 closes) is free to earn its
        # noise. Only judge non-green after SLICE_MIN_CLOSED closed trades,
        # so one stop does not freeze the book into inaction.
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
        blocked_slices=blocked_slices,
        enabled=enabled,
    )


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
