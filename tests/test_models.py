from decimal import Decimal

import pytest

from breakwater.decimal_utils import D, ceil_to_step, floor_to_step, plain
from breakwater.models import PairSpec, PairType

PAIR = {
    "symbol": "ETHUSDTPERP",
    "baseCurrency": "ETH",
    "quoteCurrency": "USDT",
    "active": True,
    "minBaseAmount": "0.001",
    "maxBaseAmount": "32",
    "minQuoteAmount": "1",
    "maxQuoteAmount": "100000",
    "tickSize": "0.1",
    "baseDecimalPlaces": "3",
    "currencyPairType": "FUTURE",
}


def test_pair_metadata_preserves_fixed_point_values():
    spec = PairSpec.from_payload(PAIR)
    assert spec.pair_type is PairType.FUTURE
    assert spec.quantity_step == Decimal("0.001")
    assert spec.tick_size == Decimal("0.1")


def test_inactive_requires_real_boolean():
    row = dict(PAIR, active="true")
    assert PairSpec.from_payload(row).active is False


def test_decimal_helpers_do_not_use_binary_float_rounding():
    assert floor_to_step(Decimal("1.239"), Decimal("0.01")) == Decimal("1.23")
    assert ceil_to_step(Decimal("1.231"), Decimal("0.01")) == Decimal("1.24")
    assert plain(Decimal("1.2300")) == "1.23"


def test_non_finite_decimal_is_rejected():
    with pytest.raises(ValueError, match="finite"):
        D("NaN")
