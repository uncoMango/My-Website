# tests/test_customer_confirmation_email.py
# =========================================================
# Hurricane Readiness work order (2026-08-21): a real purchase must not
# depend on the buyer keeping the one on-screen success-page tab open,
# or on Kahu Phil being reachable to resend a download link by hand.
# These tests confirm the buyer's own copy of the real, working link is
# actually emailed to them (PayPal and Stripe alike), that it is never
# sent when SMTP isn't configured or no buyer email could be determined,
# and that a real SMTP failure never breaks the payment flow itself.
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
    """Stands in for smtplib.SMTP without any real network call."""
    sent = []

    def __init__(self, host, port):
        self.host = host
        self.port = port

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


class FailingSMTP(FakeSMTP):
    def sendmail(self, from_addr, to_addrs, msg):
        raise ConnectionRefusedError("simulated SMTP outage")


class FakeStripeSession:
    def __init__(self, url="https://checkout.stripe.com/fake-session", payment_status="paid", customer_details=None):
        self.url = url
        self.payment_status = payment_status
        self.customer_details = customer_details


def _enable_smtp(monkeypatch):
    monkeypatch.setattr(payments_module, "SMTP_HOST", "smtp.test.local")
    monkeypatch.setattr(payments_module, "SMTP_PORT", 587)
    monkeypatch.setattr(payments_module, "SMTP_USER", "noreply@test.local")
    monkeypatch.setattr(payments_module, "SMTP_PASS", "fake-password-not-real")
    FakeSMTP.sent = []


def _disable_smtp(monkeypatch):
    monkeypatch.setattr(payments_module, "SMTP_HOST", "")
    monkeypatch.setattr(payments_module, "SMTP_USER", "")
    monkeypatch.setattr(payments_module, "SMTP_PASS", "")
    FakeSMTP.sent = []


def _sent_to(address):
    """The pre-existing admin sale-notification email fires independently
    of the customer confirmation email these tests target — filter by
    recipient rather than assuming ``FakeSMTP.sent`` only ever holds one
    kind of message."""
    return [m for m in FakeSMTP.sent if m["to"] == [address]]


def test_stripe_success_emails_the_buyer_their_real_download_link(client, monkeypatch):
    _enable_smtp(monkeypatch)
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(payments_module, "STRIPE_ENABLED", True)
    monkeypatch.setattr(payments_module, "save_digital_products", lambda data: None)
    monkeypatch.setattr(download_tokens_module, "DOWNLOAD_TOKEN_SECRET", "test-only-download-secret-not-real")
    customer = types.SimpleNamespace(name="Jane Buyer", email="jane@example.test")
    monkeypatch.setattr(
        stripe.checkout.Session, "retrieve",
        staticmethod(lambda session_id: FakeStripeSession(payment_status="paid", customer_details=customer)),
    )

    resp = client.get("/stripe/success?session_id=sess_123&product_id=prod_find_the_cause_not_the_symptoms")

    assert resp.status_code == 200
    to_buyer = _sent_to("jane@example.test")
    assert len(to_buyer) == 1
    assert "/download/product/prod_find_the_cause_not_the_symptoms/" in to_buyer[0]["msg"]
    assert "sess_123" in to_buyer[0]["msg"]


def test_paypal_success_emails_the_buyer_their_real_download_link(client, monkeypatch):
    _enable_smtp(monkeypatch)
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(payments_module, "save_digital_products", lambda data: None)
    monkeypatch.setattr(download_tokens_module, "DOWNLOAD_TOKEN_SECRET", "test-only-download-secret-not-real")
    monkeypatch.setattr(payments_module, "_get_paypal_token", lambda: "fake-token")
    monkeypatch.setattr(
        payments_module, "_get_paypal_order",
        lambda order_id, token: {"payer": {"name": {"given_name": "Jane", "surname": "Buyer"}, "email_address": "jane@example.test"}},
    )

    resp = client.get("/paypal/success?orderID=order_123&product_id=prod_find_the_cause_not_the_symptoms")

    assert resp.status_code == 200
    to_buyer = _sent_to("jane@example.test")
    assert len(to_buyer) == 1
    assert "/download/product/prod_find_the_cause_not_the_symptoms/" in to_buyer[0]["msg"]


def test_no_customer_email_sent_when_buyer_email_unknown(client, monkeypatch):
    """PayPal/Stripe sometimes withhold the buyer's email — must never crash
    or send to a bogus address; simply skipped, same as the admin path."""
    _enable_smtp(monkeypatch)
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(payments_module, "save_digital_products", lambda data: None)
    monkeypatch.setattr(download_tokens_module, "DOWNLOAD_TOKEN_SECRET", "test-only-download-secret-not-real")
    monkeypatch.setattr(
        payments_module, "_get_paypal_token",
        lambda: (_ for _ in ()).throw(Exception("no network in tests")),
    )

    resp = client.get("/paypal/success?orderID=order_456&product_id=prod_find_the_cause_not_the_symptoms")

    assert resp.status_code == 200
    assert all(m["to"] != [""] for m in FakeSMTP.sent)  # never sent to a blank/bogus address
    assert not any("jane@example.test" in m["to"][0] for m in FakeSMTP.sent)


def test_no_customer_email_sent_when_smtp_not_configured(client, monkeypatch):
    _disable_smtp(monkeypatch)
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(payments_module, "save_digital_products", lambda data: None)
    monkeypatch.setattr(download_tokens_module, "DOWNLOAD_TOKEN_SECRET", "test-only-download-secret-not-real")
    monkeypatch.setattr(payments_module, "_get_paypal_token", lambda: "fake-token")
    monkeypatch.setattr(
        payments_module, "_get_paypal_order",
        lambda order_id, token: {"payer": {"name": {"given_name": "Jane", "surname": "Buyer"}, "email_address": "jane@example.test"}},
    )

    resp = client.get("/paypal/success?orderID=order_789&product_id=prod_find_the_cause_not_the_symptoms")

    assert resp.status_code == 200
    assert FakeSMTP.sent == []


def test_smtp_outage_never_breaks_the_success_page_or_the_download_link(client, monkeypatch):
    """The customer must still see their working download link on-screen
    even if the confirmation email itself fails to send."""
    _enable_smtp(monkeypatch)
    monkeypatch.setattr(smtplib, "SMTP", FailingSMTP)
    monkeypatch.setattr(payments_module, "save_digital_products", lambda data: None)
    monkeypatch.setattr(download_tokens_module, "DOWNLOAD_TOKEN_SECRET", "test-only-download-secret-not-real")
    monkeypatch.setattr(payments_module, "_get_paypal_token", lambda: "fake-token")
    monkeypatch.setattr(
        payments_module, "_get_paypal_order",
        lambda order_id, token: {"payer": {"name": {"given_name": "Jane", "surname": "Buyer"}, "email_address": "jane@example.test"}},
    )

    resp = client.get("/paypal/success?orderID=order_999&product_id=prod_find_the_cause_not_the_symptoms")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "/download/product/prod_find_the_cause_not_the_symptoms/" in html


def test_partnership_products_do_not_error_on_missing_download_url(client, monkeypatch):
    """Partnership tiers have no download link at all — _render_payment_success
    must return before ever touching the email-sending path for them."""
    _enable_smtp(monkeypatch)
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(payments_module, "save_digital_products", lambda data: None)
    monkeypatch.setattr(
        payments_module, "_get_paypal_token",
        lambda: (_ for _ in ()).throw(Exception("no network in tests")),
    )

    resp = client.get("/paypal/success?orderID=order_partner&product_id=partner_tier1")

    assert resp.status_code == 200
    assert all("download" not in m["msg"].lower() for m in FakeSMTP.sent)
