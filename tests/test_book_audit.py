"""Offline tests for the shadow book-bootstrap auditor.

Everything here is network-free: slice-id parsing and book coverage. The
bootstrap itself needs live candles and is exercised by dispatching
``scripts/book_audit.py``, not by CI.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from book_audit import (  # noqa: E402
    HIP3_BOOK,
    NATIVE_BOOK,
    _parse_slice_id,
    _read_book,
)


def test_parse_native_slice_id():
    assert _parse_slice_id("feat_ext_vs_ma_50:0:LONG:h24") == (
        "native",
        "native_crypto_c0",
        "feat_ext_vs_ma_50",
        0,
        "LONG",
        24,
    )


def test_parse_hip3_slice_id_keeps_group():
    """The group is part of HIP-3 identity; dropping it would pool lanes."""
    assert _parse_slice_id("hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24") == (
        "hip3",
        "xyz_equity_c0",
        "feat_ext_vs_ma_50",
        0,
        "LONG",
        24,
    )


@pytest.mark.parametrize(
    "slice_id",
    [
        "",
        "garbage",
        "feat_ext_vs_ma_50:0:LONG",          # missing horizon
        "notafeature:0:LONG:h24",            # not a feature column
        "feat_ext_vs_ma_50:x:LONG:h24",      # non-integer state
        "feat_ext_vs_ma_50:0:LONG:hz",       # non-integer horizon
        "feat_ext_vs_ma_50:0:LONG:h24:extra",
    ],
)
def test_parse_rejects_malformed(slice_id):
    """A slice we cannot understand is skipped, never guessed at."""
    assert _parse_slice_id(slice_id) is None


def test_parse_short_side():
    lane, group, feature, state, side, horizon = _parse_slice_id(
        "feat_ret_20:2:SHORT:h8"
    )
    assert (lane, group, feature, state, side, horizon) == (
        "native",
        "native_crypto_c0",
        "feat_ret_20",
        2,
        "SHORT",
        8,
    )


def test_every_committed_book_row_parses():
    """If a book row cannot be parsed the audit would silently under-report.

    A silent skip is the exact failure mode this instrumentation exists to
    remove, so the whole committed book must be parseable.
    """
    rows = [(NATIVE_BOOK, row) for row in _read_book(NATIVE_BOOK)]
    rows += [(HIP3_BOOK, row) for row in _read_book(HIP3_BOOK)]
    assert rows, "no committed book rows found"
    unparseable = [
        (path.name, row["slice_id"])
        for path, row in rows
        if _parse_slice_id(row["slice_id"]) is None
    ]
    assert unparseable == [], f"unparseable book rows: {unparseable}"


def test_book_lanes_match_their_file():
    for path, expected in ((NATIVE_BOOK, "native"), (HIP3_BOOK, "hip3")):
        for row in _read_book(path):
            parsed = _parse_slice_id(row["slice_id"])
            assert parsed is not None
            assert parsed[0] == expected, (
                f"{row['slice_id']} in {path.name} parsed as lane {parsed[0]}"
            )
