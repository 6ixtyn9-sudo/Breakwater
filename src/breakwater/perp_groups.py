"""Perp OI cohorts: discover slices inside homogeneous groups, beside the global pool.

Why
---
Native research pools every perp into one cross-section and validates a
slice on the pooled bars. That assumes the mechanism is the same everywhere.
For positioning inputs it is not: funding on BTC is a carry rate, funding on
a three-week-old listing is a squeeze gauge. Pooling the two yields a slice
that describes neither, and the per-asset veto then rescues the symbols
where it happens to work. The per-symbol lane (``engines/``) was the other
extreme: 128 separate overfits (22 closes, -38 ZAR, silent since 09-17).

This is the middle. Pairs are cut into three cohorts by open-interest
notional (``oi_hi`` / ``oi_mid`` / ``oi_lo``, ~40 pairs each) and the SAME
discovery -> validation -> book -> paper pipeline runs once per cohort, in
addition to the global pass. Nothing about the judge changes; only the
cross-section it judges on.

Identity
--------
A cohort slice is ``feature@group:state:side:hN``. The ``@group`` lives in the
head token so the ``:hN`` suffix parsers keep working and the book row's
``feature`` column stays the real column name the monitor binns on.

Membership at trade time comes from the per-asset edges research wrote for
that slice: those rows exist only for the pairs that were in the cohort when
it was validated, so a cohort slice can never fire on a pair it was not
judged on, even when OI ranks drift between research runs.

Scope: the lane exists for positioning inputs, so by default it searches
only ``POSITIONING_FEATURE_COLUMNS``. The first full run over every feature
put 105 cohort rows in the book, 102 of them price/vol slices that gain
nothing from a crowdedness split. ``BREAKWATER_PERP_GROUP_FEATURES`` (comma
list) overrides the default.

Kill switch: ``BREAKWATER_PERP_GROUPS=0``.
"""

from __future__ import annotations

import os
from dataclasses import asdict
from datetime import datetime, timedelta

import pandas as pd

from breakwater.perpdata import pair_to_coin
from breakwater.positioning_features import POSITIONING_FEATURE_COLUMNS

GROUP_SEP = "@"
GROUP_NAMES = ("oi_hi", "oi_mid", "oi_lo")
MIN_GROUPABLE_PAIRS = 12  # fewer than 4 per cohort is not a cross-section


def enabled() -> bool:
    return os.getenv("BREAKWATER_PERP_GROUPS", "1").strip().lower() not in {"0", "false", "no", "off"}


def feature_columns(available) -> list[str]:
    """Features the cohort lane searches, in ``available`` order."""
    raw = os.getenv("BREAKWATER_PERP_GROUP_FEATURES", "").strip()
    wanted = {c.strip() for c in raw.split(",") if c.strip()} if raw else set(POSITIONING_FEATURE_COLUMNS)
    return [c for c in available if c in wanted]


def oi_window_days() -> int:
    try:
        return max(1, int(os.getenv("BREAKWATER_PERP_GROUP_OI_DAYS", "7")))
    except ValueError:
        return 7


def tag_slice_id(slice_id: str, group: str) -> str:
    """``feat_x:2:SHORT`` -> ``feat_x@oi_hi:2:SHORT`` (idempotent)."""
    head, sep, rest = str(slice_id).partition(":")
    if GROUP_SEP in head:
        return str(slice_id)
    return f"{head}{GROUP_SEP}{group}{sep}{rest}"


def group_of_slice(slice_id: str) -> str | None:
    head = str(slice_id or "").partition(":")[0]
    if GROUP_SEP not in head:
        return None
    return head.split(GROUP_SEP, 1)[1] or None


def retag_candidates(candidates, group: str):
    """New candidate objects (SliceStat / ValidatedSlice) with the cohort tag."""
    out = []
    for row in candidates:
        payload = asdict(row)
        payload["slice_id"] = tag_slice_id(payload["slice_id"], group)
        out.append(type(row)(**payload))
    return out


def assign_oi_groups(
    pairs,
    tape: pd.DataFrame | None,
    *,
    now: datetime,
    days: int | None = None,
) -> dict[str, str]:
    """Map native perp pair -> cohort by mean OI notional over the last ``days``.

    Pairs with no tape coin (or no OI rows in the window) are left out and stay
    in the global pool only. Returns {} when too few pairs are groupable.
    """
    if tape is None or not len(tape) or "pos_oi_notional" not in tape.columns:
        return {}
    window_days = oi_window_days() if days is None else days
    since = pd.Timestamp(now).tz_convert("UTC") if pd.Timestamp(now).tzinfo else pd.Timestamp(now, tz="UTC")
    since = since - timedelta(days=window_days)
    recent = tape.loc[pd.to_datetime(tape["start"], utc=True) >= since, ["coin", "pos_oi_notional"]]
    recent = recent.assign(coin=recent["coin"].astype(str).str.upper(), oi=pd.to_numeric(recent["pos_oi_notional"], errors="coerce"))
    oi_by_coin = recent.dropna(subset=["oi"]).groupby("coin")["oi"].mean()

    scored: list[tuple[float, str]] = []
    for pair in pairs:
        pair_u = str(pair).upper()
        coin = pair_to_coin(pair_u)
        if coin is None:
            continue
        oi = oi_by_coin.get(coin.upper())
        if oi is None or not (oi > 0):
            continue
        scored.append((float(oi), pair_u))
    if len(scored) < MIN_GROUPABLE_PAIRS:
        return {}
    scored.sort(key=lambda item: (-item[0], item[1]))
    n = len(scored)
    cut_hi, cut_mid = n // 3, (2 * n) // 3
    out: dict[str, str] = {}
    for idx, (_, pair_u) in enumerate(scored):
        out[pair_u] = GROUP_NAMES[0] if idx < cut_hi else GROUP_NAMES[1] if idx < cut_mid else GROUP_NAMES[2]
    return out


def split_book_rows(book_rows: list[dict]) -> tuple[list[dict], dict[str, list[dict]]]:
    """(global rows, {group: rows}) from one monitored book."""
    plain: list[dict] = []
    grouped: dict[str, list[dict]] = {}
    for row in book_rows:
        group = group_of_slice(str(row.get("slice_id", "")))
        if group is None:
            plain.append(row)
        else:
            grouped.setdefault(group, []).append(row)
    return plain, grouped


def group_members_from_asset_edges(asset_edge_lookup: dict[tuple[str, str], str]) -> dict[str, set[str]]:
    """{group: pairs} — the pairs research actually judged each cohort on."""
    members: dict[str, set[str]] = {}
    for slice_id, asset in asset_edge_lookup:
        group = group_of_slice(slice_id)
        if group is not None:
            members.setdefault(group, set()).add(str(asset).upper())
    return members
