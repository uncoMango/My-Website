# tests/test_download_tokens.py
# =========================================================
# Tests for the token-gated /download/product/<id>/<token> flow.
#
# Before this change, /download/product/<id> served the file to anyone
# who knew or guessed a product ID - no proof of payment required, for
# every catalog product, not just one. These tests cover the fix:
#   - a real (mocked) PayPal/Stripe success generates a working,
#     product-bound, time-limited, limited-use token
#   - the old bare-ID request path is gone / rejected
#   - expired, tampered, wrong-product, and over-used tokens are all
#     rejected the same way (403), so a forged-token attempt can't be
#     fingerprinted from the response
#   - a missing DOWNLOAD_TOKEN_SECRET fails closed (503), matching how
#     this app already signals missing ADMIN_PASSWORD/PayPal secrets
#   - the free-booklet download routes (unrelated, always free) are
#     untouched by this change
#
# No real network calls are made - PayPal/Stripe API calls are mocked,
# same style as tests/test_partner_payments.py. digital_products.json
# is never written to by these tests: PRODUCTS_FILE is redirected to a
# tmp_path copy for the duration of each test.
# =========================================================

import re
import shutil
import sys
import time
from pathlib import Path

import pytest
import stripe

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import content as content_module  # noqa: E402
import download_tokens  # noqa: E402
from blueprints import payments as payments_module  # noqa: E402
from content import get_product_by_id  # noqa: E402
import app as app_module  # noqa: E402

TEST_PRODUCT_ID = "prod_aloha_wellness"
TEST_SECRET = "test-only-download-secret-not-real"


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Redirect digital_products.json writes to a throwaway copy so
    # running these tests never mutates the real, tracked catalog file.
    real_products_file = content_module.PRODUCTS_FILE
    tmp_products_file = tmp_path / "digital_products.json"
    shutil.copy(real_products_file, tmp_products_file)
    monkeypatch.setattr(content_module, "PRODUCTS_FILE", tmp_products_file)

    # Redirect the token-usage counter to a throwaway file too.
    monkeypatch.setattr(download_tokens, "DOWNLOAD_TOKEN_USAGE_FILE", tmp_path / "download_token_usage.json")
    monkeypatch.setattr(download_tokens, "DOWNLOAD_TOKEN_SECRET", TEST_SECRET)

    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


def _mock_paypal(monkeypatch):
    monkeypatch.setattr(payments_module, "_get_paypal_token", lambda: "fake-paypal-token")
    monkeypatch.setattr(
        payments_module,
        "_get_paypal_order",
        lambda order_id, token: {
            "payer": {
                "name": {"given_name": "Test", "surname": "Buyer"},
                "email_address": "test-buyer@example.com",
            }
        },
    )


def _extract_download_url(html):
    match = re.search(r'href="(/download/product/[^"]+)"', html)
    assert match, "no download link found in payment_success.html output"
    return match.group(1)


def _complete_paypal_purchase(client, monkeypatch, product_id=TEST_PRODUCT_ID, order_id="ORDER-1"):
    _mock_paypal(monkeypatch)
    resp = client.get(f"/paypal/success?orderID={order_id}&product_id={product_id}")
    assert resp.status_code == 200
    return _extract_download_url(resp.get_data(as_text=True))


# ---------------------------------------------------------------------------
# Valid paid download
# ---------------------------------------------------------------------------

def test_valid_paid_download_succeeds(client, monkeypatch):
    download_url = _complete_paypal_purchase(client, monkeypatch)
    resp = client.get(download_url)
    assert resp.status_code == 200
    product = get_product_by_id(TEST_PRODUCT_ID)
    expected_bytes = Path(product["file_path"]).read_bytes()
    assert resp.data == expected_bytes


def test_stripe_success_download_link_is_tokenized(client, monkeypatch):
    monkeypatch.setattr(payments_module, "STRIPE_ENABLED", True)

    class FakeSession:
        payment_status = "paid"
        customer_details = {"name": "Test Buyer", "email": "test-buyer@example.com"}

    monkeypatch.setattr(stripe.checkout.Session, "retrieve", staticmethod(lambda session_id: FakeSession()))
    resp = client.get(f"/stripe/success?session_id=sess_123&product_id={TEST_PRODUCT_ID}")
    assert resp.status_code == 200
    download_url = _extract_download_url(resp.get_data(as_text=True))
    assert download_url.startswith(f"/download/product/{TEST_PRODUCT_ID}/")
    assert download_url != f"/download/product/{TEST_PRODUCT_ID}"  # not the old bare form


# ---------------------------------------------------------------------------
# Direct unpaid request
# ---------------------------------------------------------------------------

def test_direct_unpaid_request_with_no_token_404s(client):
    # The old bare-ID route no longer exists at all.
    resp = client.get(f"/download/product/{TEST_PRODUCT_ID}")
    assert resp.status_code == 404


def test_direct_unpaid_request_with_made_up_token_rejected(client):
    resp = client.get(f"/download/product/{TEST_PRODUCT_ID}/not-a-real-token")
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Expired token
# ---------------------------------------------------------------------------

def test_expired_token_rejected(client, monkeypatch):
    token = download_tokens.generate_download_token(TEST_PRODUCT_ID, "ORDER-EXP")
    monkeypatch.setattr(download_tokens, "TOKEN_MAX_AGE_SECONDS", 0)
    time.sleep(1.1)
    resp = client.get(f"/download/product/{TEST_PRODUCT_ID}/{token}")
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Tampered token
# ---------------------------------------------------------------------------

def test_tampered_token_rejected(client):
    token = download_tokens.generate_download_token(TEST_PRODUCT_ID, "ORDER-TAMPER")
    # Flip a character in the middle of the token, not the last character:
    # base64's final character can have insignificant trailing bits, so a
    # few different characters there can decode to the same bytes and
    # wouldn't reliably invalidate the signature.
    pos = len(token) // 2
    flipped = "A" if token[pos] != "A" else "B"
    tampered = token[:pos] + flipped + token[pos + 1:]
    resp = client.get(f"/download/product/{TEST_PRODUCT_ID}/{tampered}")
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Wrong-product token
# ---------------------------------------------------------------------------

def test_wrong_product_token_rejected(client):
    token = download_tokens.generate_download_token(TEST_PRODUCT_ID, "ORDER-WRONG")
    resp = client.get(f"/download/product/rotten_fencepost_field_guide/{token}")
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Limited use
# ---------------------------------------------------------------------------

def test_token_reusable_up_to_limit(client):
    token = download_tokens.generate_download_token(TEST_PRODUCT_ID, "ORDER-LIMIT")
    for _ in range(download_tokens.MAX_USES):
        resp = client.get(f"/download/product/{TEST_PRODUCT_ID}/{token}")
        assert resp.status_code == 200


def test_token_rejected_once_use_limit_exceeded(client):
    token = download_tokens.generate_download_token(TEST_PRODUCT_ID, "ORDER-LIMIT2")
    for _ in range(download_tokens.MAX_USES):
        assert client.get(f"/download/product/{TEST_PRODUCT_ID}/{token}").status_code == 200
    resp = client.get(f"/download/product/{TEST_PRODUCT_ID}/{token}")
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Missing secret fails closed
# ---------------------------------------------------------------------------

def test_download_503s_when_secret_unset(client, monkeypatch):
    monkeypatch.setattr(download_tokens, "DOWNLOAD_TOKEN_SECRET", "")
    resp = client.get(f"/download/product/{TEST_PRODUCT_ID}/anything")
    assert resp.status_code == 503


def test_payment_success_shows_support_message_when_secret_unset(client, monkeypatch):
    monkeypatch.setattr(download_tokens, "DOWNLOAD_TOKEN_SECRET", "")
    _mock_paypal(monkeypatch)
    resp = client.get(f"/paypal/success?orderID=ORDER-NOSECRET&product_id={TEST_PRODUCT_ID}")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "/download/product/" not in html
    assert "contact" in html.lower()


# ---------------------------------------------------------------------------
# Free-booklet routes are unrelated and untouched
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path", [
    "/download/booklet1",
    "/download/pamphlet1",
])
def test_free_booklet_routes_still_ungated(client, path):
    resp = client.get(path)
    assert resp.status_code in (200, 302)
