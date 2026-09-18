from breakwater.costs import is_fiat_quoted, quote_of, spot_round_trip_bps, spot_round_trip_decimal


def test_quote_of_and_fiat():
    assert quote_of("BTCZAR") == "ZAR"
    assert quote_of("XRPUSDC") == "USDC"
    assert quote_of("BTCUSDT") == "USDT"
    assert is_fiat_quoted("BTCZAR")
    assert not is_fiat_quoted("BTCUSDT")
    assert not is_fiat_quoted("ETHUSDC")


def test_spot_round_trip_defaults(monkeypatch):
    monkeypatch.delenv("BREAKWATER_SPOT_FEE_BPS", raising=False)
    monkeypatch.delenv("BREAKWATER_SPOT_CRYPTO_FEE_BPS", raising=False)
    assert spot_round_trip_bps("BTCZAR") == 70.0
    assert spot_round_trip_bps("BTCUSDT") == 20.0
    assert spot_round_trip_bps("ETHUSDC") == 20.0
    assert float(spot_round_trip_decimal("BTCZAR")) == 70.0
    assert float(spot_round_trip_decimal("XRPUSDC")) == 20.0
