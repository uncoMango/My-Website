# tests/test_paypal_temporarily_disabled.py
# =========================================================
# Hurricane Readiness work order (2026-08-21): PayPal has no server-side
# webhook, so a customer whose browser disappears right after paying via
# PayPal is not guaranteed automatic fulfillment. Rather than build a new
# PayPal webhook under time pressure, PayPal is temporarily withheld at
# checkout for Training 001 only -- a reversible UI-level gate. PayPal
# itself, its credentials, and every other product's PayPal path stay
# completely untouched.
# =========================================================

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from blueprints import payments as payments_module  # noqa: E402
import app as app_module  # noqa: E402

TRAINING_001_ID = "prod_training_001_complete"


@pytest.fixture
def client():
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


def _enable_paypal(monkeypatch):
    monkeypatch.setattr(payments_module, "PAYPAL_CLIENT_ID", "fake-client-id-for-test")
    monkeypatch.setattr(payments_module, "PAYPAL_CLIENT_SECRET", "fake-secret-for-test")


def test_training_001_checkout_hides_the_paypal_section(client, monkeypatch):
    _enable_paypal(monkeypatch)
    html = client.get(f"/checkout/{TRAINING_001_ID}").get_data(as_text=True)
    assert 'id="paypal-button-container"' not in html
    assert "Secure checkout powered by PayPal" not in html


def test_training_001_checkout_omits_the_paypal_sdk_script(client, monkeypatch):
    _enable_paypal(monkeypatch)
    html = client.get(f"/checkout/{TRAINING_001_ID}").get_data(as_text=True)
    assert "www.paypal.com/sdk/js" not in html


def test_training_001_checkout_still_shows_the_stripe_option(client, monkeypatch):
    _enable_paypal(monkeypatch)
    monkeypatch.setattr(payments_module, "STRIPE_ENABLED", True)
    html = client.get(f"/checkout/{TRAINING_001_ID}").get_data(as_text=True)
    assert f'action="/stripe/create-session/{TRAINING_001_ID}"' in html


def test_training_001_checkout_does_not_require_paypal_credentials(client, monkeypatch):
    """Since PayPal is withheld for this product, the checkout page must
    not 503 merely because PAYPAL_CLIENT_ID/SECRET happen to be unset --
    Stripe alone is sufficient for this product while the gate is active."""
    monkeypatch.setattr(payments_module, "PAYPAL_CLIENT_ID", "")
    monkeypatch.setattr(payments_module, "PAYPAL_CLIENT_SECRET", "")
    monkeypatch.setattr(payments_module, "STRIPE_ENABLED", True)
    resp = client.get(f"/checkout/{TRAINING_001_ID}")
    assert resp.status_code == 200


def test_other_products_still_show_paypal_normally(client, monkeypatch):
    """The gate is scoped to Training 001 only -- every other product's
    checkout is completely untouched."""
    _enable_paypal(monkeypatch)
    html = client.get("/checkout/prod_find_the_cause_not_the_symptoms").get_data(as_text=True)
    assert 'id="paypal-button-container"' in html
    assert "www.paypal.com/sdk/js?client-id=fake-client-id-for-test" in html


def test_paypal_route_and_credentials_are_not_removed(monkeypatch):
    """Explicitly not a removal -- the real route and helper functions
    still exist and still work; only the checkout UI is gated."""
    assert hasattr(payments_module, "paypal_success")
    assert hasattr(payments_module, "_get_paypal_token")
    assert hasattr(payments_module, "_get_paypal_order")


def test_paypal_disabled_product_ids_contains_only_training_001():
    assert payments_module.PAYPAL_DISABLED_PRODUCT_IDS == {TRAINING_001_ID}
