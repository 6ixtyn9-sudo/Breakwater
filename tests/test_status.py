import csv

import pytest

from breakwater.status import append_status


def test_status_is_bounded_and_keeps_header(tmp_path):
    path = tmp_path / "status.csv"
    for index in range(5):
        append_status(path, "stage", "shadow", str(index), keep=3)
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 3
    assert rows[-1]["detail"] == "4"


def test_malformed_status_schema_fails_closed(tmp_path):
    path = tmp_path / "status.csv"
    path.write_text("wrong,columns\n1,2\n")
    with pytest.raises(RuntimeError, match="unsupported schema"):
        append_status(path, "stage", "shadow")
