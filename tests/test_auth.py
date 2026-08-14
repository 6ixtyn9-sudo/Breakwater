from breakwater.valr import sign_request

OFFICIAL_SECRET = (
    "4961b74efac86b25cce8fbe4c9811c4c"
    "7a787b7a5996660afcc2e287ad864363"
)
OFFICIAL_GET_SIGNATURE = (
    "9d52c181ed69460b49307b7891f04658"
    "e938b21181173844b5018b2fe783a6d4"
    "c62b8e67a03de4d099e7437ebfabe12"
    "c56233b73c6a0cc0f7ae87e05f6289928"
)
OFFICIAL_POST_SIGNATURE = (
    "09f536e3dfdad58443f16010a97a0a21"
    "ad27486b7b8d6d4103170d885410ed77"
    "f037f1fa628474190d4f5c08ca12c1ac"
    "c850901f1c2e75c6d906ec3b32b008d0"
)


def test_official_get_signature_vector():
    signature = sign_request(
        OFFICIAL_SECRET,
        1558014486185,
        "GET",
        "/v1/account/balances",
    )
    assert signature == OFFICIAL_GET_SIGNATURE


def test_official_post_signature_vector():
    body = (
        '{"customerOrderId":"ORDER-000001","pair":"BTCUSDC",'
        '"side":"BUY","quoteAmount":"80000"}'
    )
    signature = sign_request(
        OFFICIAL_SECRET,
        1558017528946,
        "POST",
        "/v1/orders/market",
        body,
    )
    assert signature == OFFICIAL_POST_SIGNATURE


def test_single_character_secret_change_changes_signature():
    changed = OFFICIAL_SECRET[:-1] + "4"
    assert sign_request(changed, 1558014486185, "GET", "/v1/account/balances") != (
        OFFICIAL_GET_SIGNATURE
    )


def test_subaccount_is_part_of_signature():
    base = sign_request("secret", 1, "GET", "/path")
    scoped = sign_request("secret", 1, "GET", "/path", subaccount_id="42")
    assert scoped != base
