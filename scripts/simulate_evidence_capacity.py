#!/usr/bin/env python3
"""Evidence-capacity simulator for the Breakwater paper books.

Answers two questions from the committed paper history:

  1. Where is the knee in total paper capacity (seats) for time-to-evidence,
     i.e. how fast do all native book slices reach the per-slice round-trip
     (RT) target?
  2. What is the smallest HIP-3 seat ring-fence that does not measurably
     slow the native book?

Method: cycle-level (hourly) discrete-event simulation.

  - Signal process: the observed daily episode structure (16h on from
    08:00 UTC, 8h off; four consecutive days matched in the status history).
    Per-slice Poisson intensity fitted to the most recent episode.
  - Hold time and per-trade risk: sampled from the empirical closed-trade
    distribution (recent trades only, so current entry guards are reflected).
  - HIP-3 book: sized from its validated research families. Until real
    HIP-3 trades exist, it is assumed to match native per-slice behaviour
    (same intensity and hold distribution). This is a LABELED ASSUMPTION:
    the sim sizes the isolation, it does not predict HIP-3 edge. Re-fit
    with real HIP-3 trade data once the lane has ~2 weeks of history.

Deterministic: seeded per (config, seed). Manual research tool - no cron,
same category as deep-research-audit. Output: localdata/sim/*.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
import sys
import time
from pathlib import Path

ON_HOUR_START = 8  # observed episodes start 08:15 UTC, run 16 cycles
NATIVE_PAIR_POOL = 232  # native perp universe size
HIP3_PAIR_POOL = 20  # largest HIP-3 equity group size
MAX_PER_SLICE = 5  # engine: BREAKWATER_PAPER_MAX_POSITIONS_PER_SLICE
NOTIONAL_ZAR = 200.0  # engine: policy max notional (median fill)
RISK_FRACTION_CAP = 0.03  # engine: BREAKWATER_PAPER_MAX_RISK_FRACTION
RT_TARGET = 10  # per-slice round-trip target (1h class)
RECENT_SINCE = "2026-08-20"  # trades since current entry guards exist
SIGNAL_ENUM_CAP = 12  # per-slice signals enumerated per cycle (see note)
EQUITY_ZAR = 2100.0
RISK_CAP_FRACTION = 0.05  # live-proxy constraint, fixed in this study


def poisson(rng: random.Random, lam: float) -> int:
    if lam <= 0:
        return 0
    limit = math.exp(-lam)
    k = 0
    p = 1.0
    while True:
        k += 1
        p *= rng.random()
        if p <= limit:
            return k - 1


def load_data(data_dir: Path) -> dict:
    """Fit the simulation process from the committed paper state."""
    paper_log = data_dir / "research" / "paper_trade_log.csv"
    status_csv = data_dir / "status.csv"
    book_csv = data_dir / "research" / "monitored_slices.csv"
    hip3_validated = data_dir / "hip3" / "research" / "validated_slices.csv"

    # --- closed trades: hold time + per-trade risk (recent only) ---
    holds: list[int] = []
    risks: list[float] = []
    with paper_log.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("outcome") not in {"win", "loss"}:
                continue
            closed_at = str(row.get("closed_at") or "")[:10]
            if closed_at < RECENT_SINCE:
                continue
            try:
                bars = int(row.get("bars_held") or 0)
                notional = float(row.get("notional_zar") or 0)
                frac = float(row.get("risk_fraction") or 0)
            except (TypeError, ValueError):
                continue
            if bars > 0:
                holds.append(bars)
            risk = min(notional * frac, NOTIONAL_ZAR * RISK_FRACTION_CAP)
            if risk > 0:
                risks.append(risk)
    if not holds or not risks:
        raise RuntimeError("no recent closed trades found; cannot fit process")

    # --- episode intensity: most recent run of new_signals > 0 ---
    cycles: list[dict] = []
    with status_csv.open(newline="") as handle:
        for row in csv.DictReader(handle):
            try:
                detail = json.loads(row.get("detail") or "{}")
            except json.JSONDecodeError:
                continue
            if isinstance(detail, dict) and "paper" in detail:
                cycles.append(
                    {"t": row["timestamp_utc"], "ns": int(detail["paper"].get("new_signals") or 0)}
                )
    episodes = []
    i = 0
    while i < len(cycles):
        if cycles[i]["ns"] > 0:
            j = i
            while j < len(cycles) and cycles[j]["ns"] > 0:
                j += 1
            episodes.append(cycles[i:j])
            i = j
        else:
            i += 1
    if not episodes:
        raise RuntimeError("no signal episodes found in status history")
    last = episodes[-1]
    intensity = sum(c["ns"] for c in last) / len(last)

    # --- native book slice count ---
    with book_csv.open(newline="") as handle:
        book_rows = [r for r in csv.DictReader(handle) if r.get("status") == "monitored"]
    n_native = max(len(book_rows), 1)

    # --- HIP-3 first book: validated families (one slice promoted per family) ---
    families = set()
    if hip3_validated.exists():
        with hip3_validated.open(newline="") as handle:
            for row in csv.DictReader(handle):
                if row.get("validated") != "True":
                    continue
                sid = row.get("slice_id") or ""
                head, _, base = sid.partition(":")
                families.add((head, base.rsplit(":h", 1)[0]))

    return {
        "holds": holds,
        "risks": risks,
        "intensity": intensity,
        "n_native": n_native,
        "n_hip3": len(families),
        "median_hold": statistics.median(holds),
        "median_risk": statistics.median(risks),
    }


def simulate(
    fit: dict,
    *,
    native_old: int,
    native_fat: int,
    hip3_seats: int,
    intensity: float,
    days: int,
    seed: int,
) -> dict:
    """One seeded run of the two-book paper account (shared 5% wallet).

    Native seats are two pools, exactly as the engine runs them: `native_fat`
    seats for slices without paper history (exploration) and `native_old`
    seats for incumbent slices (slices with >=1 RT). HIP-3 gets a flat pool
    of `hip3_seats`.
    """
    rng = random.Random(f"capacity|{native_old}|{native_fat}|{hip3_seats}|{intensity:.0f}|{seed}")
    holds = fit["holds"]
    risks = fit["risks"]
    n_native = fit["n_native"]
    n_hip3 = fit["n_hip3"]
    risk_cap = fit["risk_cap"]

    native_seats = native_old + native_fat
    lam_native = intensity / n_native if n_native else 0.0
    lam_hip3 = lam_native  # LABELED ASSUMPTION: same per-slice matching rate

    live: list[list] = []  # [pair, slice, bars_left, risk, book]
    open_native = 0
    open_hip3 = 0
    open_risk = 0.0
    peak_risk = 0.0
    seat_denials = 0
    risk_denials = 0
    pair_used: set[str] = set()
    slice_open: dict[str, int] = {}
    rts: dict[str, int] = {}
    all10_day: float | None = None

    for cycle in range(days * 24):
        # 1) age positions and close matured ones
        for pos in live:
            pos[2] -= 1
        still = []
        for p in live:
            if p[2] <= 0:
                pair_used.discard(p[0])
                open_risk -= p[3]
                if p[4] == "native":
                    open_native -= 1
                else:
                    open_hip3 -= 1
                slice_open[p[1]] = slice_open.get(p[1], 1) - 1
                rts[p[1]] = rts.get(p[1], 0) + 1
            else:
                still.append(p)
        live = still

        # 2) metric: first day every native slice reached the RT target
        if (
            all10_day is None
            and n_native
            and all(rts.get(f"n{i}", 0) >= RT_TARGET for i in range(n_native))
        ):
            all10_day = cycle / 24 + 1

        if cycle % 24 < ON_HOUR_START:  # overnight drought: no signals
            continue

        # 3) demand: per-slice Poisson signals. Enumerating beyond the cap is
        #    immaterial: a cycle can fill at most ~total_seats entries, so
        #    excess signals would be seat-denied regardless of order.
        fat: list[tuple] = []
        old: list[tuple] = []
        for i in range(n_native):
            sl = f"n{i}"
            n_sig = min(poisson(rng, lam_native), SIGNAL_ENUM_CAP)
            bucket = rts.get(sl, 0) > 0 and old or fat
            for _ in range(n_sig):
                bucket.append((sl, f"P{rng.randrange(NATIVE_PAIR_POOL)}"))
        for i in range(n_hip3):
            sl = f"h{i}"
            n_sig = min(poisson(rng, lam_hip3), SIGNAL_ENUM_CAP)
            for _ in range(n_sig):
                fat.append((sl, f"P{rng.randrange(HIP3_PAIR_POOL)}"))
        rng.shuffle(fat)
        rng.shuffle(old)

        # 4) entries: fat (new slices) first, matching the engine's
        #    explore-first ordering, against the shared wallet.
        # (count open POSITIONS on incumbent slices, as the engine does -
        #  not distinct slices, or the book deadlocks once every slice is an
        #  incumbent)
        open_old_now = 0
        for sl, count in slice_open.items():
            if sl.startswith("n") and rts.get(sl, 0) > 0:
                open_old_now += count
        for sl, pair in fat + old:
            if pair in pair_used:
                continue
            is_native = sl.startswith("n")
            if is_native:
                if open_native >= native_seats:
                    seat_denials += 1
                    continue
                is_old = rts.get(sl, 0) > 0
                if is_old and open_old_now >= native_old:
                    seat_denials += 1
                    continue
                if not is_old and open_native - open_old_now >= native_seats - native_old:
                    seat_denials += 1
                    continue
            else:
                if open_hip3 >= hip3_seats:
                    seat_denials += 1
                    continue
            if slice_open.get(sl, 0) >= MAX_PER_SLICE:
                continue
            risk = min(rng.choice(risks), NOTIONAL_ZAR * RISK_FRACTION_CAP)
            if open_risk + risk > risk_cap:
                risk_denials += 1
                continue
            live.append([pair, sl, max(rng.choice(holds), 1), risk, "native" if is_native else "hip3"])
            pair_used.add(pair)
            slice_open[sl] = slice_open.get(sl, 0) + 1
            open_risk += risk
            peak_risk = max(peak_risk, open_risk)
            if is_native:
                open_native += 1
                if rts.get(sl, 0) > 0:
                    open_old_now += 1
            else:
                open_hip3 += 1

    native_rts = sum(v for k, v in rts.items() if k.startswith("n"))
    hip3_rts = sum(v for k, v in rts.items() if k.startswith("h"))
    native_slice_rts = [rts.get(f"n{i}", 0) for i in range(n_native)]
    return {
        "all10_day": all10_day if all10_day is not None else float(days),
        "native_rts": native_rts,
        "hip3_rts": hip3_rts,
        "min_slice_rts": min(native_slice_rts) if n_native else 0,
        "seat_denials": seat_denials,
        "risk_denials": risk_denials,
        "peak_risk": peak_risk,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Two-book evidence-capacity simulator")
    parser.add_argument("--data-dir", default="localdata")
    parser.add_argument("--days", type=int, default=36)
    parser.add_argument("--seeds", type=int, default=40)
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    out_dir = Path(args.out_dir) if args.out_dir else data_dir / "sim"
    out_dir.mkdir(parents=True, exist_ok=True)

    started = time.time()
    fit = load_data(data_dir)
    fit["risk_cap"] = RISK_CAP_FRACTION * EQUITY_ZAR

    print(
        "fit: intensity={:.0f} sigs/cycle | native_slices={} hip3_families={} | "
        "median_hold={}h median_risk={:.2f}Z | risk_cap={:.0f}Z".format(
            fit["intensity"], fit["n_native"], fit["n_hip3"],
            fit["median_hold"], fit["median_risk"], fit["risk_cap"],
        )
    )

    intensities = [100.0, fit["intensity"], 300.0]  # sensitivity band
    results = []
    for intensity in intensities:
        for old_cap in (3, 5, 8, 12, 15):
            for h3 in (0, 2, 4, 6):
                runs = [
                    simulate(
                        fit, native_old=old_cap, native_fat=10, hip3_seats=h3,
                        intensity=intensity, days=args.days, seed=s,
                    )
                    for s in range(args.seeds)
                ]
                cell = {
                    "intensity": round(intensity, 1),
                    "old_cap": old_cap,
                    "fat_cap": 10,
                    "total_native": old_cap + 10,
                    "hip3_seats": h3,
                }
                for key, agg in (
                    ("all10_day", statistics.median),
                    ("native_rts", statistics.median),
                    ("hip3_rts", statistics.median),
                    ("min_slice_rts", statistics.median),
                    ("peak_risk", max),
                ):
                    cell[f"med_{key}"] = round(float(agg(r[key] for r in runs)), 2)
                for key in ("seat_denials", "risk_denials"):
                    cell[f"sum_{key}"] = int(sum(r[key] for r in runs))
                results.append(cell)

    grid_path = out_dir / "capacity_sim_grid.csv"
    with grid_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    summary = {
        "as_of": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "days": args.days,
        "seeds_per_cell": args.seeds,
        "rt_target": RT_TARGET,
        "fit": {
            "intensity_per_cycle": round(fit["intensity"], 1),
            "native_slices": fit["n_native"],
            "hip3_families": fit["n_hip3"],
            "median_hold_hours": fit["median_hold"],
            "median_risk_zar": fit["median_risk"],
            "risk_cap_zar": fit["risk_cap"],
            "recent_since": RECENT_SINCE,
        },
        "assumptions": [
            "episode: 16h on from 08:00 UTC / 8h off (observed 4/4 days)",
            "native seats are two pools exactly as the engine runs them: fat (slices without paper history) cap 10, old (incumbents) cap grid-varied",
            "HIP-3 per-slice matching rate and hold time assumed equal to native until real trades exist",
            "risk cap fixed at 5% of equity (live-proxy constraint); not varied",
            "per-slice signal enumeration capped per cycle; excess would be seat-denied anyway",
        ],
        "grid": results,
        "elapsed_seconds": round(time.time() - started, 1),
    }
    summary_path = out_dir / "capacity_sim_summary.json"
    summary_path.write_text(json.dumps(summary, indent=1) + "\n")
    print(f"wrote {summary_path} and {grid_path} in {summary['elapsed_seconds']}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
