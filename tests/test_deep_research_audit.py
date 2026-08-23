import numpy as np
import pandas as pd

from breakwater.deep_research_audit import (
    _attach_plateaus,
    _block_bootstrap_p,
    _weights,
)


def test_frozen_recency_weights_halve_each_thousand_hours():
    ages = np.array([0, 999, 1000, 1999, 2000, 3000, 4000, 4999])
    assert list(_weights(ages)) == [1.0, 1.0, 0.5, 0.5, 0.25, 0.125, 0.0625, 0.0625]


def test_block_bootstrap_is_deterministic_and_respects_time_blocks():
    frame = pd.DataFrame(
        {
            "start": pd.date_range("2026-01-01", periods=480, freq="h", tz="UTC"),
            "net": [0.01] * 480,
            "weight": [1.0] * 480,
        }
    )
    first = _block_bootstrap_p(frame, seed_text="candidate", replicates=100)
    second = _block_bootstrap_p(frame, seed_text="candidate", replicates=100)
    assert first == second
    assert first < 0.05


def test_only_contiguous_three_horizon_plateaus_pass():
    rows = []
    for horizon in range(1, 8):
        rows.append(
            {
                "lane": "native",
                "group": "crypto",
                "feature": "feat",
                "state": 1,
                "side": "LONG",
                "horizon_bars": horizon,
                "preliminary_pass": horizon in {1, 2, 4, 5, 6, 7},
                "plateau_start": "",
                "plateau_end": "",
                "plateau_width": 0,
                "audit_pass": False,
            }
        )
    _attach_plateaus(rows)
    assert not rows[0]["audit_pass"]
    assert not rows[1]["audit_pass"]
    for index in (3, 4, 5, 6):
        assert rows[index]["audit_pass"]
        assert rows[index]["plateau_start"] == 4
        assert rows[index]["plateau_end"] == 7
        assert rows[index]["plateau_width"] == 4
