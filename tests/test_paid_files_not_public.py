# tests/test_paid_files_not_public.py
# =========================================================
# Symptom (found 2026-10-20): the $9 Rotten Fencepost Field Guide could be downloaded by anyone, without paying, from
# /static/downloads/rotten_fencepost_field_guide.pdf.
# Root cause: the PDF was added on 2026-06-28 into static/ -- the one folder the web server hands out to everybody. On
# 2026-07-23 downloads were put behind signed purchase tokens, but that only protected the /download/product/<id>/<token>
# ROUTE; the old file stayed in static/, and nothing checked that a sold file can never be fetched directly.
# These tests make that mistake impossible to repeat:
#   * no sold file is inside static/ (or a copy of it anywhere in static/),
#   * every sold file is reachable ONLY through the paid, token-checked route,
#   * after a (mocked) payment the buyer still gets the real file.
# =========================================================
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import content as content_module  # noqa: E402
import download_tokens  # noqa: E402
from blueprints import payments as payments_module  # noqa: E402
import app as app_module  # noqa: E402

TEST_SECRET = "test-only-download-secret-not-real"


def _sold_files():
    data = json.loads((ROOT / "digital_products.json").read_text(encoding="utf-8"))
    return [p for p in data["products"] if p.get("file_path") and p.get("price", 0) > 0]


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def test_no_sold_file_lives_inside_the_public_static_folder():
    for p in _sold_files():
        parts = Path(p["file_path"]).parts
        assert parts[0] != "static", f"{p['id']}: {p['file_path']} is in the public static folder"
        assert (ROOT / p["file_path"]).is_file(), f"{p['id']}: file is missing"


def test_no_copy_of_a_sold_file_is_anywhere_in_static():
    sold = {_sha(ROOT / p["file_path"]): p["id"] for p in _sold_files() if (ROOT / p["file_path"]).is_file()}
    for f in (ROOT / "static").rglob("*"):
        if f.is_file() and f.suffix.lower() in {".pdf", ".html", ".zip", ".epub", ".docx", ".mobi"}:
            assert _sha(f) not in sold, f"{f} is a public copy of the paid file {sold[_sha(f)]}"


@pytest.fixture
def client(tmp_path, monkeypatch):
    tmp_products = tmp_path / "digital_products.json"
    shutil.copy(content_module.PRODUCTS_FILE, tmp_products)
    monkeypatch.setattr(content_module, "PRODUCTS_FILE", tmp_products)
    monkeypatch.setattr(download_tokens, "DOWNLOAD_TOKEN_USAGE_FILE", tmp_path / "usage.json")
    monkeypatch.setattr(download_tokens, "DOWNLOAD_TOKEN_SECRET", TEST_SECRET)
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


@pytest.mark.parametrize("product", _sold_files(), ids=lambda p: p["id"])
def test_a_sold_file_cannot_be_fetched_without_paying(client, product):
    name = Path(product["file_path"]).name
    for url in (f"/static/downloads/{name}", f"/static/{name}", f"/static/digital_products/{name}",
                f"/digital_products/{name}", f"/{name}", f"/download/product/{product['id']}",
                f"/download/product/{product['id']}/not-a-real-token"):
        assert client.get(url).status_code in (403, 404), f"{url} was reachable without paying"


@pytest.mark.parametrize("product", _sold_files(), ids=lambda p: p["id"])
def test_after_a_mocked_paypal_payment_the_buyer_gets_the_real_file(client, monkeypatch, product):
    monkeypatch.setattr(payments_module, "_get_paypal_token", lambda: "t")
    monkeypatch.setattr(payments_module, "_get_paypal_order", lambda order_id, token: {
        "payer": {"name": {"given_name": "Test", "surname": "Buyer"}, "email_address": "buyer@example.com"}})
    resp = client.get(f"/paypal/success?orderID=ORDER-X&product_id={product['id']}")
    assert resp.status_code == 200
    url = re.search(r'href="(/download/product/[^"]+)"', resp.get_data(as_text=True))
    assert url, "no download link on the success page"
    got = client.get(url.group(1))
    assert got.status_code == 200 and got.data == (ROOT / product["file_path"]).read_bytes()
