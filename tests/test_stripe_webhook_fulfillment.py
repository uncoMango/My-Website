# tests/test_stripe_webhook_fulfillment.py
# =========================================================
# Hurricane Readiness work order (2026-08-21): the acceptance test is
# that a customer can pay through Stripe, immediately lose their
# browser/connection, and server-side Stripe processing (the webhook)
# still automatically sends them access -- without Kahu Phil, and
# without ever depending on /stripe/success being reached at all.
#
# Also proves the required idempotency: a Stripe webhook retry of the
# exact same event, or the webhook and the browser both completing for
# the same real session, must never double-count a sale or send a
# duplicate fulfillment email.
# =========================================================

import smtplib
import sys
import types
from pathlib import Path

import pytest
import stripe

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from blueprints import payments as payments_module  # noqa: E402
import download_tokens as download_tokens_module  # noqa: E402
import app as app_module  # noqa: E402


@pytest.fixture
def client():
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


class FakeSMTP:
    sent = []

    def __init__(self, host, port):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def starttls(self):
        pass

    def login(self, user, password):
        pass

    def sendmail(self, from_addr, to_addrs, msg):
        FakeSMTP.sent.append({"from": from_addr, "to": to_addrs, "msg": msg})


def _enable_smtp(monkeypatch):
    monkeypatch.setattr(payments_module, "SMTP_HOST", "smtp.test.local")
    monkeypatch.setattr(payments_module, "SMTP_PORT", 587)
    monkeypatch.setattr(payments_module, "SMTP_USER", "noreply@test.local")
    monkeypatch.setattr(payments_module, "SMTP_PASS", "fake-password-not-real")
    FakeSMTP.sent = []


def _sent_to(address):
    return [m for m in FakeSMTP.sent if m["to"] == [address]]


def _checkout_completed_event(session_id="evt_sess_1", product_id="prod_find_the_cause_not_the_symptoms",
                               email="jane@example.test", payment_status="paid"):
    """A minimal, realistic stand-in for the real event dict Stripe's own
    stripe.Webhook.construct_event would return for a checkout.session.completed
    event -- shaped exactly as blueprints.payments.stripe_webhook() reads it
    (dict access throughout, matching Stripe's real event payload shape)."""
    return {
        "type": "checkout.session.completed",
        "data": {"object": {
            "id": session_id,
            "payment_status": payment_status,
            "metadata": {"product_id": product_id},
            "customer_details": {"name": "Jane Buyer", "email": email},
        }},
    }


def _post_webhook(client, event, monkeypatch):
    monkeypatch.setattr(payments_module, "STRIPE_ENABLED", True)
    monkeypatch.setattr(stripe.Webhook, "construct_event", staticmethod(lambda payload, sig, secret: event))
    return client.post("/stripe/webhook", data=b"{}", headers={"Stripe-Signature": "fake"})


def test_webhook_fulfills_purchase_without_the_browser_ever_visiting_success(client, monkeypatch):
    """The core acceptance test: the webhook alone -- never /stripe/success --
    counts the sale and emails the customer their real download link."""
    _enable_smtp(monkeypatch)
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(payments_module, "save_digital_products", lambda data: None)
    monkeypatch.setattr(download_tokens_module, "DOWNLOAD_TOKEN_SECRET", "test-only-download-secret-not-real")

    resp = _post_webhook(client, _checkout_completed_event(), monkeypatch)

    assert resp.status_code == 200
    to_buyer = _sent_to("jane@example.test")
    assert len(to_buyer) == 1
    assert "/download/product/prod_find_the_cause_not_the_symptoms/" in to_buyer[0]["msg"]


def test_webhook_ignores_unpaid_sessions(client, monkeypatch):
    _enable_smtp(monkeypatch)
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(payments_module, "save_digital_products", lambda data: None)
    monkeypatch.setattr(download_tokens_module, "DOWNLOAD_TOKEN_SECRET", "test-only-download-secret-not-real")

    resp = _post_webhook(client, _checkout_completed_event(payment_status="unpaid"), monkeypatch)

    assert resp.status_code == 200
    assert FakeSMTP.sent == []


def test_webhook_rejects_invalid_signature(client, monkeypatch):
    monkeypatch.setattr(payments_module, "STRIPE_ENABLED", True)
    monkeypatch.setattr(
        stripe.Webhook, "construct_event",
        staticmethod(lambda payload, sig, secret: (_ for _ in ()).throw(stripe.error.SignatureVerificationError("bad sig", "sig"))),
    )
    resp = client.post("/stripe/webhook", data=b"{}", headers={"Stripe-Signature": "forged"})
    assert resp.status_code == 400


def test_webhook_retry_of_the_same_event_never_double_counts_or_double_emails(client, monkeypatch):
    """The explicit idempotency requirement: Stripe may deliver the same
    real event more than once (retries on slow/failed responses)."""
    _enable_smtp(monkeypatch)
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    saved_products = []
    monkeypatch.setattr(payments_module, "save_digital_products", lambda data: saved_products.append(data))
    monkeypatch.setattr(download_tokens_module, "DOWNLOAD_TOKEN_SECRET", "test-only-download-secret-not-real")

    event = _checkout_completed_event(session_id="evt_retry_test")
    first = _post_webhook(client, event, monkeypatch)
    second = _post_webhook(client, event, monkeypatch)  # Stripe's own retry of the identical event

    assert first.status_code == 200
    assert second.status_code == 200
    assert len(_sent_to("jane@example.test")) == 1  # not 2
    # Sales counted exactly once, not twice, across both deliveries.
    total_increments = sum(
        1 for data in saved_products for p in data["products"]
        if p["id"] == "prod_find_the_cause_not_the_symptoms"
    )
    assert total_increments == 1


def test_webhook_and_browser_success_for_the_same_session_never_double_fulfill(client, monkeypatch):
    """The webhook and the customer's own browser can both genuinely
    complete for the same real purchase -- whichever reaches the session
    first does the real work; the other still shows/returns a valid link
    without re-counting the sale or re-emailing."""
    _enable_smtp(monkeypatch)
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(payments_module, "save_digital_products", lambda data: None)
    monkeypatch.setattr(download_tokens_module, "DOWNLOAD_TOKEN_SECRET", "test-only-download-secret-not-real")

    class FakeStripeSession:
        payment_status = "paid"
        customer_details = types.SimpleNamespace(name="Jane Buyer", email="jane@example.test")

    monkeypatch.setattr(stripe.checkout.Session, "retrieve", staticmethod(lambda session_id: FakeStripeSession()))

    webhook_resp = _post_webhook(client, _checkout_completed_event(session_id="evt_both_paths"), monkeypatch)
    browser_resp = client.get(
        "/stripe/success?session_id=evt_both_paths&product_id=prod_find_the_cause_not_the_symptoms"
    )

    assert webhook_resp.status_code == 200
    assert browser_resp.status_code == 200
    # The browser still gets a real, working download link even though
    # the webhook already fulfilled the sale first.
    assert "/download/product/prod_find_the_cause_not_the_symptoms/" in browser_resp.get_data(as_text=True)
    # But the customer was only actually emailed once.
    assert len(_sent_to("jane@example.test")) == 1


def test_webhook_missing_product_id_is_a_safe_no_op(client, monkeypatch):
    _enable_smtp(monkeypatch)
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    event = _checkout_completed_event()
    del event["data"]["object"]["metadata"]["product_id"]

    resp = _post_webhook(client, event, monkeypatch)

    assert resp.status_code == 200
    assert FakeSMTP.sent == []


def test_webhook_unknown_product_id_is_a_safe_no_op(client, monkeypatch):
    _enable_smtp(monkeypatch)
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)

    resp = _post_webhook(client, _checkout_completed_event(product_id="not_a_real_product"), monkeypatch)

    assert resp.status_code == 200
    assert FakeSMTP.sent == []
