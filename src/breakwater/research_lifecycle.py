"""Slice lifecycle: discovered to validated to monitored, with decay.
Key behaviors:
- Monitored slices decay out when they stop firing or lose money on paper.
- Cooldown is reserved for STOP-OUT style losses (hard adverse outcomes),
  not every small after-fee loss (especially at horizon exits).
- Cooldown expiry is refreshed when the book is read so slices can recover
  without requiring a separate research rebuild.
IMPORTANT COMPATIBILITY:
Paper trading calls apply_signal_feedback(..., stopout=bool). This module must
accept that kwarg and must not cooldown on every non-win.
Edge meaning marker:
Breakwater needs one bit of information:

"This book row was written under the directional net-edge convention."
vs
"This row was carried forward from older state and might not match it."

We store that as a plain boolean string:
- edge_is_directional_net="True" for newly validated/promoted rows
- edge_is_directional_net="False" for carried legacy rows (or when unknown)
For backwards compatibility, if a carried row has edge_semantics_version
(net_v1/legacy_v0), we convert it into edge_is_directional_net and remove the
old field before writing.
"""

from __future__ import annotations

import csv
import json
import os
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from breakwater.validation import ValidatedSlice, read_validated

BOOK_HEADERS = [
    "slice_id",
    "kind",
    "feature",
    "state",
    "side",
    "status",
    "validated_at",
    "last_signal_bar",
    "paper_trades",
    "paper_wins",
    "paper_losses",
    "paper_pnl_zar",
    "cooldown_until",
    "mean_ret_costadj",
    "n",
    "p_value",
    "horizon_bars",
    "stop_atr_mult",
    "source",
    "hostile_unproven",
    # New, human marker: can we trust mean_ret_costadj as directional net edge?
    "edge_is_directional_net",
]
MONITORED = "monitored"
COOLDOWN = "cooldown"
DECAYED = "decayed"
PROVENANCE_VALIDATED = "validated_walk_forward"

MIN_BOOK_ROWS = 60
LIVE_DECAY_BARS = 96
PNL_DECAY_MIN_TRADES = 3
STOPOUT_COOLDOWN_BARS = 24
BAR_SECONDS = 3600


def _coerce_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _refresh_expired_cooldowns_inplace(rows: list[dict], *, now_epoch: int) -> int:
    changed = 0
    for row in rows:
        if row.get("status") != COOLDOWN:
            continue
        cooldown_until = _coerce_int(row.get("cooldown_until"), 0)
        if cooldown_until and cooldown_until <= now_epoch:
            row["status"] = MONITORED
            row["cooldown_until"] = ""
            changed += 1
    return changed


def read_book(path: Path) -> list[dict]:
    """Read the monitored book.
    Side effect (intentional): expired cooldown rows are reactivated and persisted.
    """
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not {
            "slice_id",
            "kind",
            "feature",
            "state",
            "side",
            "status",
        }.issubset(set(reader.fieldnames)):
            raise RuntimeError("monitored book has an unsupported schema")
        rows = list(reader)
    now_epoch = int(datetime.now(timezone.utc).timestamp())
    if _refresh_expired_cooldowns_inplace(rows, now_epoch=now_epoch):
        _write_book(path, rows)
    return rows


def _min_net_edge() -> float:
    raw = os.getenv("BREAKWATER_MIN_NET_EDGE", "0")
    try:
        value = float(raw)
    except (TypeError, ValueError):
        value = 0.0
    return max(0.0, value)


def _directional_edge(row: ValidatedSlice) -> bool:
    # mean_ret_costadj is NET return for the chosen side (already cost-aware).
    return row.mean_ret_costadj > 0 and row.mean_ret_costadj >= _min_net_edge()


def _env_bool(name: str, default: str = "0") -> bool:
    value = str(os.getenv(name, default)).strip().lower()
    return value in {"1", "true", "yes", "y", "on"}


def _concentrated_min_mean() -> float:
    raw = os.getenv("BREAKWATER_CONCENTRATED_MIN_MEAN", "0.004")
    try:
        return max(0.0, float(raw))
    except (TypeError, ValueError):
        return 0.004


def _is_concentrated_candidate(row: ValidatedSlice) -> bool:
    """Fat, temporally honest edges that fail only the 40% name-breadth rule.

    Hunt path (OFF unless BREAKWATER_CONCENTRATED_PROMOTE=1): do not lower
    global posf; promote a labelled concentrated family instead.
    """
    if not _env_bool("BREAKWATER_CONCENTRATED_PROMOTE", "0"):
        return False
    reasons = {tok.strip() for tok in str(row.fail_reasons or "").split(",") if tok.strip()}
    if reasons - {"breadth_ok"}:
        return False
    if not (row.temporal_pass and row.direction_ok and row.mean_positive):
        return False
    if row.regime_confounded:
        return False
    if int(row.n) < 2000 or int(row.breadth_symbols_used) < 10:
        return False
    return float(row.mean_ret_costadj) >= _concentrated_min_mean()


# === Multi-horizon robustness gate (promotion-time) ===
def _promotion_multi_horizon_min_passes() -> int:
    """Minimum number of distinct horizons per slice family required for promotion.

    Default: 1 (off / legacy behavior).
    Suggested quick-win: 2 (robustness without nuking the book).
    """
    raw = os.getenv("BREAKWATER_PROMOTION_MULTI_HORIZON_MIN_PASSES", "1")
    try:
        value = int(str(raw).strip())
    except (TypeError, ValueError):
        value = 1
    return max(1, value)


def _promotion_multi_horizon_select() -> str:
    """How to select which horizon to promote within a passing family."""
    mode = str(os.getenv("BREAKWATER_PROMOTION_MULTI_HORIZON_SELECT", "edge_per_bar")).strip().lower()
    allowed = {"edge", "edge_per_bar", "shortest", "longest"}
    return mode if mode in allowed else "edge_per_bar"


def _family_key(row: ValidatedSlice) -> tuple[str, str, int, str]:
    # Horizon intentionally excluded: defines a slice family.
    return (str(row.kind), str(row.feature), int(row.state), str(row.side))


def _select_family_candidate(candidates: list[ValidatedSlice], *, mode: str) -> ValidatedSlice:
    if mode == "shortest":
        return min(candidates, key=lambda r: int(r.horizon_bars))
    if mode == "longest":
        return max(candidates, key=lambda r: int(r.horizon_bars))
    if mode == "edge":
        return max(candidates, key=lambda r: float(r.mean_ret_costadj))
    # default: edge_per_bar (tie-breaker: raw edge)
    return max(
        candidates,
        key=lambda r: (
            float(r.mean_ret_costadj) / max(1, int(r.horizon_bars)),
            float(r.mean_ret_costadj),
        ),
    )


def _truthy_bool_str(value) -> str:
    return "True" if str(value).strip() == "True" else "False"


def _convert_legacy_semantics_inplace(row: dict) -> None:
    """Ensure row has edge_is_directional_net and no edge_semantics_version key.
    Needed because DictWriter will raise if a row contains keys not in BOOK_HEADERS.
    """
    # Map any existing edge_semantics_version (net_v1/legacy_v0) to boolean.
    version = str(row.pop("edge_semantics_version", "") or "")
    flag = row.get("edge_is_directional_net")
    if flag is None or str(flag).strip() not in {"True", "False"}:
        if version == "net_v1":
            row["edge_is_directional_net"] = "True"
        elif version == "legacy_v0":
            row["edge_is_directional_net"] = "False"
        else:
            # Unknown/missing => treat as legacy/untrusted
            row["edge_is_directional_net"] = "False"
    else:
        row["edge_is_directional_net"] = _truthy_bool_str(flag)


def sync_book(
    *,
    validated_path: Path,
    book_path: Path,
    now: datetime | None = None,
) -> dict:
    now = now or datetime.now(timezone.utc)
    now_epoch = int(now.timestamp())

    validated_rows = read_validated(validated_path)
    validated_all = [row for row in validated_rows if row.validated]
    validated_by_id = {row.slice_id: row for row in validated_rows}
    existing_rows = read_book(book_path)
    existing = {row["slice_id"]: row for row in existing_rows}

    # Base promotability filter (legacy rules)
    promotable = [
        row
        for row in validated_all
        if row.n >= MIN_BOOK_ROWS and _directional_edge(row)
    ]
    concentrated = [
        row for row in validated_rows
        if (not row.validated) and _is_concentrated_candidate(row)
    ]
    # Prefer full validation; concentrated fills only if the family is absent.
    promotable_ids = {row.slice_id for row in promotable}
    promotable.extend(row for row in concentrated if row.slice_id not in promotable_ids)

    # Optional multi-horizon robustness promotion gate
    min_passes = _promotion_multi_horizon_min_passes()
    select_mode = _promotion_multi_horizon_select()
    families_considered = 0
    families_promoted = 0

    if min_passes <= 1:
        to_promote = promotable
    else:
        by_family: dict[tuple[str, str, int, str], list[ValidatedSlice]] = defaultdict(list)
        for row in promotable:
            by_family[_family_key(row)].append(row)
        families_considered = len(by_family)

        to_promote = []
        for _, candidates in by_family.items():
            horizons = {int(r.horizon_bars) for r in candidates if int(r.horizon_bars) > 0}
            if len(horizons) < min_passes:
                continue
            chosen = _select_family_candidate(candidates, mode=select_mode)
            to_promote.append(chosen)

        families_promoted = len(to_promote)

    # Carry-forward must be keyed off what actually promoted, not what merely validated,
    # otherwise a kind can be wiped when it validates rows but none pass promotion filters.
    promoted_kinds: set[str] = set()
    rows: list[dict] = []

    summary: dict = {
        "validated": len(validated_all),
        "concentrated": len(concentrated),
        "promotable": len(promotable),
        "multi_horizon_min_passes": min_passes,
        "multi_horizon_select": select_mode,
        "families_considered": families_considered,
        "families_promoted": families_promoted,
        "monitored": 0,
        "decayed": 0,
        "cooldown": 0,
        "carried_kinds": [],
        "carried_total": 0,
        "carried_monitored": 0,
        "carried_cooldown": 0,
        "carried_decayed": 0,
        "rows_total_after_sync": 0,
    }

    # Promote newly validated slices (filtered and/or gated)
    for row in to_promote:
        prior = existing.get(row.slice_id)

        promoted_kinds.add(row.kind)

        cooldown_until = _coerce_int(prior.get("cooldown_until"), 0) if prior else 0
        if cooldown_until > now_epoch:
            status = COOLDOWN
            summary["cooldown"] += 1
        elif prior and prior.get("status") == MONITORED:
            last_signal = _coerce_int(prior.get("last_signal_bar"), 0)
            paper_trades = _coerce_int(prior.get("paper_trades"), 0)
            paper_pnl = float(prior.get("paper_pnl_zar") or 0)
            stale = last_signal > 0 and (now_epoch - last_signal) > LIVE_DECAY_BARS * BAR_SECONDS
            losing = paper_trades >= PNL_DECAY_MIN_TRADES and paper_pnl < 0
            if stale or losing:
                status = DECAYED
                summary["decayed"] += 1
            else:
                status = MONITORED
                summary["monitored"] += 1
        else:
            status = MONITORED
            summary["monitored"] += 1

        rows.append(
            {
                "slice_id": row.slice_id,
                "kind": row.kind,
                "feature": row.feature,
                "state": str(row.state),
                "side": row.side,
                "status": status,
                "validated_at": now.isoformat(),
                "last_signal_bar": prior.get("last_signal_bar", "") if prior else "",
                "paper_trades": prior.get("paper_trades", "0") if prior else "0",
                "paper_wins": prior.get("paper_wins", "0") if prior else "0",
                "paper_losses": prior.get("paper_losses", "0") if prior else "0",
                "paper_pnl_zar": prior.get("paper_pnl_zar", "0") if prior else "0",
                "cooldown_until": prior.get("cooldown_until", "") if prior else "",
                "mean_ret_costadj": f"{row.mean_ret_costadj:.6f}",
                "n": str(row.n),
                "p_value": f"{row.p_value:.6f}",
                "horizon_bars": str(row.horizon_bars),
                "stop_atr_mult": f"{row.stop_atr_mult:.3f}",
                "source": (
                    "validated_concentrated"
                    if (not row.validated and _is_concentrated_candidate(row))
                    else PROVENANCE_VALIDATED
                ),
                "hostile_unproven": "True" if row.hostile_unproven else "False",
                "edge_is_directional_net": "True",
            }
        )

    def _carry_eligible(row: dict) -> bool:
        try:
            edge = float(row.get("mean_ret_costadj") or 0.0)
            n_rows = int(row.get("n") or 0)
        except (TypeError, ValueError):
            return False
        return n_rows >= MIN_BOOK_ROWS and edge >= _min_net_edge()

    # Carry rows for kinds that did not promote this run, but drop thin leftovers
    # that would fail today's net-edge / n floors.
    carried = [
        r
        for r in existing_rows
        if r.get("kind") not in promoted_kinds and _carry_eligible(r)
    ]
    if carried:
        summary["carried_kinds"] = sorted({str(r.get("kind")) for r in carried if r.get("kind")})
        summary["carried_total"] = len(carried)
        for r in carried:
            _convert_legacy_semantics_inplace(r)
            status = str(r.get("status") or "")
            if status == MONITORED:
                summary["carried_monitored"] += 1
            elif status == COOLDOWN:
                summary["carried_cooldown"] += 1
            elif status == DECAYED:
                summary["carried_decayed"] += 1

        rows.extend(carried)

    summary["rows_total_after_sync"] = len(rows)
    _write_book(book_path, rows)
    return summary


def apply_signal_feedback(
    book_path: Path,
    slice_id: str,
    *,
    bar_epoch: int,
    outcome: str,
    pnl_zar: float,
    stopout: bool = False,
    now: datetime | None = None,
) -> None:
    """Update per-slice paper outcomes.

    Losses are recorded always. Cooldown is applied ONLY when stopout=True.
    """
    now = now or datetime.now(timezone.utc)
    rows = read_book(book_path)
    for row in rows:
        if row["slice_id"] != slice_id:
            continue
        row["last_signal_bar"] = str(bar_epoch)

        trades = _coerce_int(row.get("paper_trades"), 0) + 1
        row["paper_trades"] = str(trades)
        current_pnl = float(row.get("paper_pnl_zar") or 0.0)
        row["paper_pnl_zar"] = f"{(current_pnl + pnl_zar):.4f}"
        if outcome == "win":
            row["paper_wins"] = str(_coerce_int(row.get("paper_wins"), 0) + 1)
            row["cooldown_until"] = ""
            if row.get("status") == COOLDOWN:
                row["status"] = MONITORED
        else:
            row["paper_losses"] = str(_coerce_int(row.get("paper_losses"), 0) + 1)
            if stopout:
                row["cooldown_until"] = str(bar_epoch + STOPOUT_COOLDOWN_BARS * BAR_SECONDS)
                row["status"] = COOLDOWN
        # Ensure marker exists for safety if book was older
        _convert_legacy_semantics_inplace(row)

    _write_book(book_path, rows)


def _write_book(path: Path, rows: list[dict]) -> None:
    # Ensure no legacy-only keys sneak into the writer
    for row in rows:
        _convert_legacy_semantics_inplace(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(file_descriptor, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=BOOK_HEADERS)
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def read_cooldown_journal(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text())
        return payload if isinstance(payload, list) else []
    except (OSError, json.JSONDecodeError):
        return []
