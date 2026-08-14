from decimal import Decimal

import pytest

from breakwater.config import (
    ABSOLUTE_EQUITY_FLOOR_ZAR,
    INITIAL_EQUITY_ZAR,
    MAX_TOTAL_LOSS_ZAR,
    get_settings,
)


def test_capital_boundary_is_exact():
    assert INITIAL_EQUITY_ZAR == Decimal("331.45")
    assert MAX_TOTAL_LOSS_ZAR == Decimal("109.38")
    assert ABSOLUTE_EQUITY_FLOOR_ZAR == Decimal("222.07")
    assert INITIAL_EQUITY_ZAR - ABSOLUTE_EQUITY_FLOOR_ZAR == MAX_TOTAL_LOSS_ZAR


def test_default_mode_is_readonly(monkeypatch, tmp_path):
    monkeypatch.delenv("BREAKWATER_MODE", raising=False)
    monkeypatch.setenv("BREAKWATER_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("VALR_API_KEY", raising=False)
    monkeypatch.delenv("VALR_API_SECRET", raising=False)
    settings = get_settings()
    assert settings.mode == "readonly"
    assert settings.writes_allowed is False


def test_live_requires_exact_ack(monkeypatch, tmp_path):
    monkeypatch.setenv("BREAKWATER_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("BREAKWATER_MODE", "live")
    monkeypatch.setenv("BREAKWATER_LIVE_ACK", "yes")
    settings = get_settings()
    assert settings.writes_allowed is False

    monkeypatch.setenv("BREAKWATER_LIVE_ACK", "I_ACCEPT_BREAKWATER_LIVE_RISK")
    assert get_settings().writes_allowed is True


def test_partial_credentials_fail(monkeypatch, tmp_path):
    monkeypatch.setenv("BREAKWATER_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("VALR_API_KEY", "key")
    monkeypatch.delenv("VALR_API_SECRET", raising=False)
    with pytest.raises(RuntimeError, match="configured together"):
        get_settings()


def test_unknown_mode_fails(monkeypatch, tmp_path):
    monkeypatch.setenv("BREAKWATER_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("BREAKWATER_MODE", "aggressive")
    with pytest.raises(RuntimeError, match="readonly, shadow, or live"):
        get_settings()
