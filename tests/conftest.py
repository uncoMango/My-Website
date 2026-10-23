# tests/conftest.py
# =========================================================
# Hurricane Readiness work order (2026-08-21): the Stripe fulfillment
# idempotency tracker (blueprints/payments.py's STRIPE_FULFILLED_SESSIONS_FILE)
# is a new, real file on disk. Without isolating it, any test that
# exercises /stripe/success or /stripe/webhook would write real
# idempotency state into the actual repository file -- this autouse
# fixture gives every test its own disposable copy instead, with no
# changes required to any existing test file.
# =========================================================

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from blueprints import payments as payments_module  # noqa: E402
from blueprints import downloads as downloads_module  # noqa: E402
import content as content_module  # noqa: E402


@pytest.fixture(autouse=True)
def _isolate_stripe_fulfillment_tracking(tmp_path, monkeypatch):
    monkeypatch.setattr(payments_module, "STRIPE_FULFILLED_SESSIONS_FILE", tmp_path / "stripe_fulfilled_sessions.json")


@pytest.fixture(autouse=True)
def _isolate_subscribers(tmp_path, monkeypatch):
    """Same reasoning as _isolate_stripe_fulfillment_tracking above:
    blueprints/downloads.py's SUBSCRIBERS_FILE is a real file on disk --
    without isolating it, any test exercising /subscribe or /unsubscribe
    would write real subscriber data into the actual repository file."""
    monkeypatch.setattr(downloads_module, "SUBSCRIBERS_FILE", tmp_path / "subscribers.json")


@pytest.fixture(autouse=True)
def _isolate_shelf_live_files(tmp_path, monkeypatch):
    """The buyer's shelf keeps what the Foreman adds, and the list of buyers, in shelf.LIVE_DIR (on the
    persistent disk on Render). Every test gets its own empty one, so no test touches real shelf data."""
    import shelf
    monkeypatch.setattr(shelf, "LIVE_DIR", tmp_path / "shelf_live")


@pytest.fixture(autouse=True)
def _isolate_admin_content(tmp_path, monkeypatch):
    """Same reasoning again: content.py's DATA_FILE (admin_content_overrides.json,
    2026-09-27) is a real file on disk once save_content() actually writes --
    without isolating it, any test that hits /kahu's edit routes would write
    real admin content into the actual repository file."""
    monkeypatch.setattr(content_module, "DATA_FILE", tmp_path / "admin_content_overrides.json")


# ---------------------------------------------------------------------------
# 2026-10-21: the PayPal success page now asks PayPal whether the order was really paid, and sale/delivery alerts go to a phone.
# Tests must never reach PayPal or a phone. By default a test gets the OLD lenient behaviour (the order is taken as paid; buyer name
# and email are read from whatever the test mocked), and every alert is captured in `sale_alert_log`.
# A test of the real check marks itself: @pytest.mark.real_paypal_verification
# ---------------------------------------------------------------------------

def pytest_configure(config):
    config.addinivalue_line("markers", "real_paypal_verification: use the real PayPal order check (with PayPal itself mocked)")


@pytest.fixture(autouse=True)
def sale_alert_log(monkeypatch, tmp_path):
    import sale_alerts
    log = []
    monkeypatch.setattr(sale_alerts, "SENT_FILE", tmp_path / "sale_alerts_sent.json")
    monkeypatch.setattr(sale_alerts, "send", lambda title, body, urgent=False, **kw: log.append((title, body, urgent)) or True)
    return log


@pytest.fixture(autouse=True)
def _lenient_paypal_check_unless_marked(request, monkeypatch):
    if request.node.get_closest_marker("real_paypal_verification"):
        return

    def lenient(order_id, product):
        try:
            order = payments_module._get_paypal_order(order_id, payments_module._get_paypal_token())
        except Exception:
            order = {}
        payer = order.get("payer", {})
        name = f"{payer.get('name', {}).get('given_name', '')} {payer.get('name', {}).get('surname', '')}".strip()
        return True, "", name, payer.get("email_address", "")

    monkeypatch.setattr(payments_module, "_verify_paypal_payment", lenient)

