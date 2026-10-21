# tests/test_stripe_card_button.py
# =========================================================
# Symptom (found 2026-10-20): the "Pay with Credit / Debit Card" button answered "Internal Server Error" on every product.
# Cause 1 (certain, in the code): any refusal from Stripe was not caught, so the buyer saw a bare 500 page.
# Cause 2 (probable, from the timeline: the last working card session was 2026-08-23, attribution tags were added on 2026-09-02):
#   the request sent several metadata keys with EMPTY values; Stripe reads an empty value as "remove this key".
# Cause 3 (cannot be tested from here): the Stripe key on Render may lack permission to create Checkout Sessions.
# These tests: only keys with a value are sent; a Stripe refusal gives a plain page + PayPal pointer (never a 500), writes the real
# cause to the log, and never leaks a key.
# =========================================================
import sys
from pathlib import Path

import pytest
import stripe

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from blueprints import payments as payments_module  # noqa: E402
import app as app_module  # noqa: E402

PRODUCT = "prod_find_the_cause_not_the_symptoms"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(payments_module, "STRIPE_ENABLED", True)
    monkeypatch.setattr(payments_module, "STRIPE_SECRET_KEY", "sk_test_dummy")
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


class _Session:
    url = "https://checkout.stripe.example/pay/cs_test_1"


def test_a_normal_visit_sends_no_empty_metadata_and_goes_to_stripe(client, monkeypatch):
    seen = {}
    monkeypatch.setattr(stripe.checkout.Session, "create", staticmethod(lambda **kw: seen.update(kw) or _Session()))
    resp = client.post(f"/stripe/create-session/{PRODUCT}")
    assert resp.status_code == 303 and resp.headers["Location"] == _Session.url
    assert seen["metadata"] == {"product_id": PRODUCT, "attribution_source": "direct"}
    assert all(v for v in seen["metadata"].values())


def test_attribution_cookies_are_still_carried_when_present(client, monkeypatch):
    seen = {}
    monkeypatch.setattr(stripe.checkout.Session, "create", staticmethod(lambda **kw: seen.update(kw) or _Session()))
    client.set_cookie("rf_source", "pinterest")
    client.set_cookie("rf_campaign", "pinterest_fence_line")
    client.post(f"/stripe/create-session/{PRODUCT}")
    assert seen["metadata"]["attribution_source"] == "pinterest" and seen["metadata"]["attribution_campaign"] == "pinterest_fence_line"
    assert "attribution_medium" not in seen["metadata"]


@pytest.mark.parametrize("error,category", [
    (stripe.PermissionError("Permission denied. The provided key 'rk_live_51ABCdef_xyz' does not have the required permissions", http_status=403),
     "stripe_key_permission"),
    (stripe.AuthenticationError("Invalid API Key provided: sk_live_****abcd", http_status=401), "stripe_key_rejected"),
    (stripe.InvalidRequestError("Invalid string: metadata", param="metadata", http_status=400), "stripe_rejected_request"),
    (stripe.APIConnectionError("could not connect"), "stripe_unreachable"),
    (RuntimeError("something else"), "stripe_other"),
])
def test_a_stripe_refusal_gives_a_plain_page_not_a_500_and_names_the_cause(client, monkeypatch, capsys, error, category):
    def boom(**kw):
        raise error
    monkeypatch.setattr(stripe.checkout.Session, "create", staticmethod(boom))
    resp = client.post(f"/stripe/create-session/{PRODUCT}")
    assert resp.status_code == 502 and resp.headers["X-Checkout-Problem"] == category
    page = resp.get_data(as_text=True)
    assert "Nothing was charged" in page and f"/checkout/{PRODUCT}" in page and "PayPal" in page
    assert "Internal Server Error" not in page
    out = capsys.readouterr().out
    assert "[stripe] create-session FAILED" in out and PRODUCT in out
    assert "51ABCdef" not in out and "abcd" not in out and "_xyz" not in out   # no part of a key reaches the log


def test_unknown_product_is_still_a_404_and_disabled_stripe_still_a_404(client, monkeypatch):
    assert client.post("/stripe/create-session/not_a_product").status_code == 404
    monkeypatch.setattr(payments_module, "STRIPE_ENABLED", False)
    assert client.post(f"/stripe/create-session/{PRODUCT}").status_code == 404
