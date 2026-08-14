from pathlib import Path

from breakwater.valr import ValrClient

ROOT = Path(__file__).resolve().parents[1]


def test_client_exposes_no_withdrawal_or_transfer_methods():
    names = {name.lower() for name in dir(ValrClient)}
    assert not any("withdraw" in name for name in names)
    assert not any("transfer" in name for name in names)
    assert not any("bank" in name for name in names)


def test_environment_template_contains_no_credentials():
    text = (ROOT / ".env.example").read_text()
    assert "VALR_API_KEY=\n" in text
    assert "VALR_API_SECRET=\n" in text


def test_no_machine_specific_paths_in_product_code():
    for root in [ROOT / "src", ROOT / "scripts", ROOT / ".github"]:
        for path in root.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                text = path.read_text(errors="ignore")
                assert "/" + "Users/" not in text
                assert "/" + "home/" not in text
