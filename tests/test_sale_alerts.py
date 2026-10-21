# tests/test_sale_alerts.py
# =========================================================
# 2026-10-21 (owner order): every real payment (Stripe or PayPal) sends the owner a phone message saying what sold and whether the
# buyer's download is ready; a failed delivery says so at once. Also: the PayPal success page used to trust any order number
# (a made-up number delivered the file) -- it now asks PayPal whether the order was really paid.
# =========================================================
import json
import re
import shutil
import sys
import urllib.error
from pathlib import Path

import pytest
import stripe

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import content as content_module  # noqa: E402
import download_tokens  # noqa: E402
import sale_alerts  # noqa: E402
from blueprints import payments as payments_module  # noqa: E402
from content import get_product_by_id  # noqa: E402
import app as app_module  # noqa: E402

PRODUCT = "prod_find_the_cause_not_the_symptoms"   # $9.99
SECRET = "test-only-download-secret-not-real"


@pytest.fixture
def client(tmp_path, monkeypatch):
    shutil.copy(content_module.PRODUCTS_FILE, tmp_path / "digital_products.json")
    monkeypatch.setattr(content_module, "PRODUCTS_FILE", tmp_path / "digital_products.json")
    monkeypatch.setattr(download_tokens, "DOWNLOAD_TOKEN_USAGE_FILE", tmp_path / "usage.json")
    monkeypatch.setattr(download_tokens, "DOWNLOAD_TOKEN_SECRET", SECRET)
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


def _sales_counted(tmp_path, product_id=PRODUCT):
    data = json.loads((tmp_path / "digital_products.json").read_text(encoding="utf-8"))
    return next(p for p in data["products"] if p["id"] == product_id).get("total_sales", 0)


def _paid_order(amount="9.99", status="COMPLETED"):
    return {"status": status, "payer": {"name": {"given_name": "A", "surname": "Buyer"}, "email_address": "a@example.com"},
            "purchase_units": [{"amount": {"currency_code": "USD", "value": amount},
                                "payments": {"captures": [{"status": status, "amount": {"currency_code": "USD", "value": amount}}]}}]}


def _paypal(monkeypatch, order=None, error=None):
    monkeypatch.setattr(payments_module, "_get_paypal_token", lambda: "t")

    def get_order(order_id, token):
        if error:
            raise error
        return order
    monkeypatch.setattr(payments_module, "_get_paypal_order", get_order)


# ------------------------------------------------------------------ PayPal: must really be paid
@pytest.mark.real_paypal_verification
def test_a_made_up_paypal_order_number_gets_no_file_and_no_alert(client, monkeypatch, sale_alert_log, tmp_path):
    _paypal(monkeypatch, error=urllib.error.HTTPError("u", 404, "Not Found", {}, None))
    resp = client.get(f"/paypal/success?orderID=MADE-UP&product_id={PRODUCT}")
    assert resp.status_code == 402 and b"/download/product/" not in resp.data
    assert sale_alert_log == [] and _sales_counted(tmp_path) == 0


@pytest.mark.real_paypal_verification
@pytest.mark.parametrize("order", [_paid_order(status="CREATED"), _paid_order(status="APPROVED"), _paid_order(amount="0.01")])
def test_an_unpaid_or_wrong_amount_order_gets_no_file(client, monkeypatch, order, tmp_path):
    _paypal(monkeypatch, order=order)
    resp = client.get(f"/paypal/success?orderID=ORD-1&product_id={PRODUCT}")
    assert resp.status_code == 402 and b"/download/product/" not in resp.data and _sales_counted(tmp_path) == 0


@pytest.mark.real_paypal_verification
def test_when_paypal_cannot_be_reached_the_buyer_is_told_kindly_and_the_owner_is_alerted_once(client, monkeypatch, sale_alert_log):
    _paypal(monkeypatch, error=urllib.error.URLError("down"))
    for _ in range(2):
        resp = client.get(f"/paypal/success?orderID=ORD-77&product_id={PRODUCT}")
        assert resp.status_code == 503 and b"do not pay again" in resp.data and b"/download/product/" not in resp.data
    assert len(sale_alert_log) == 1 and sale_alert_log[0][2] is True and "FIX NOW" in sale_alert_log[0][0]


@pytest.mark.real_paypal_verification
def test_a_really_paid_order_delivers_counts_once_and_sends_one_sale_message(client, monkeypatch, sale_alert_log, tmp_path):
    _paypal(monkeypatch, order=_paid_order())
    first = client.get(f"/paypal/success?orderID=ORD-REAL-1&product_id={PRODUCT}")
    assert first.status_code == 200 and re.search(rb"/download/product/[^\"]+", first.data)
    again = client.get(f"/paypal/success?orderID=ORD-REAL-1&product_id={PRODUCT}")      # refreshing the page
    assert again.status_code == 200 and re.search(rb"/download/product/[^\"]+", again.data)
    assert _sales_counted(tmp_path) == pytest.approx(9.99)                              # counted once, not twice
    assert len(sale_alert_log) == 1
    title, body, urgent = sale_alert_log[0]
    assert title.startswith("SALE:") and "$9.99" in title and "PayPal" in body and "READY" in body and urgent is False
    assert "a@example.com" not in body and "A Buyer" not in body                          # no buyer details in the phone message


# ------------------------------------------------------------------ Stripe
class _Session:
    payment_status = "paid"
    customer_details = {"name": "S Buyer", "email": "s@example.com"}


def test_a_paid_stripe_session_sends_one_sale_message(client, monkeypatch, sale_alert_log):
    monkeypatch.setattr(payments_module, "STRIPE_ENABLED", True)
    monkeypatch.setattr(stripe.checkout.Session, "retrieve", staticmethod(lambda sid: _Session()))
    for _ in range(2):
        assert client.get(f"/stripe/success?session_id=cs_live_abcd1234&product_id={PRODUCT}").status_code == 200
    assert len(sale_alert_log) == 1 and sale_alert_log[0][0].startswith("SALE:") and "Stripe" in sale_alert_log[0][1]


def test_a_paid_stripe_order_with_no_file_ready_says_fix_now(client, monkeypatch, sale_alert_log):
    monkeypatch.setattr(payments_module, "STRIPE_ENABLED", True)
    monkeypatch.setattr(stripe.checkout.Session, "retrieve", staticmethod(lambda sid: _Session()))
    monkeypatch.setattr(download_tokens, "DOWNLOAD_TOKEN_SECRET", "")
    import blueprints.payments as pm
    monkeypatch.setattr(pm, "generate_download_token", lambda *a: None)
    client.get(f"/stripe/success?session_id=cs_live_zzzz9999&product_id={PRODUCT}")
    assert len(sale_alert_log) == 1 and sale_alert_log[0][2] is True
    assert sale_alert_log[0][0].startswith("FIX NOW") and "secret" in sale_alert_log[0][1]


# ------------------------------------------------------------------ the download itself
def _token_url(client, monkeypatch, order="ORD-D-1"):
    _paypal_url = client.get(f"/paypal/success?orderID={order}&product_id={PRODUCT}")
    return re.search(r'href="(/download/product/[^"]+)"', _paypal_url.get_data(as_text=True)).group(1)


def test_the_first_download_sends_a_delivered_message_and_later_ones_do_not(client, monkeypatch, sale_alert_log):
    url = _token_url(client, monkeypatch)
    sale_alert_log.clear()
    assert client.get(url).status_code == 200
    assert client.get(url).status_code == 200
    assert [t for t, _b, _u in sale_alert_log] == [f"DELIVERED: {get_product_by_id(PRODUCT)['name']}"]


def test_a_missing_file_gives_the_buyer_a_kind_page_and_the_owner_an_urgent_message(client, monkeypatch, sale_alert_log, tmp_path):
    url = _token_url(client, monkeypatch, order="ORD-D-2")
    sale_alert_log.clear()
    product = dict(get_product_by_id(PRODUCT), file_path=str(tmp_path / "gone.pdf"))
    import blueprints.products as pr
    monkeypatch.setattr(pr, "get_product_by_id", lambda pid: product)
    resp = client.get(url)
    assert resp.status_code == 503 and b"sorry" in resp.data and b"Internal Server Error" not in resp.data
    assert sale_alert_log and sale_alert_log[0][2] is True and sale_alert_log[0][0].startswith("FIX NOW")


# ------------------------------------------------------------------ health + alert plumbing
def test_health_page_reports_gaps_without_secrets(client, monkeypatch):
    monkeypatch.delenv("SALE_ALERT_NTFY_TOPIC", raising=False)
    data = client.get("/health/sales").get_json()
    assert data["sale_alerts_configured"] is False and data["ok"] is False
    assert any("sale phone alerts" in p for p in data["problems"])
    assert all(p["file_ok"] for p in data["products"]) and {p["id"] for p in data["products"]} >= {PRODUCT, "rotten_fencepost_field_guide"}
    text = json.dumps(data)
    assert SECRET not in text and "sk_" not in text and "@" not in text
    monkeypatch.setenv("SALE_ALERT_NTFY_TOPIC", "some-topic")
    assert client.get("/health/sales").get_json()["sale_alerts_configured"] is True


def test_alert_sender_needs_a_topic_and_never_raises(monkeypatch):
    real_send = sale_alerts.__dict__["send"]
    monkeypatch.delenv("SALE_ALERT_NTFY_TOPIC", raising=False)
    # the autouse fixture replaced send(); call the original through importlib
    import importlib
    fresh = importlib.reload(sale_alerts)
    assert fresh.send("t", "b") is False
    monkeypatch.setenv("SALE_ALERT_NTFY_TOPIC", "my-topic")
    seen = {}
    assert fresh.send("SALE: x", "body", post=lambda url, body, headers: seen.update(url=url, headers=headers) or True) is True
    assert seen["url"].endswith("/my-topic") and seen["headers"]["Priority"] == "default"
    assert fresh.send("x", "y", urgent=True, post=lambda *a: (_ for _ in ()).throw(RuntimeError("boom"))) is False


def test_once_remembers_and_fails_open(tmp_path, monkeypatch):
    import importlib
    fresh = importlib.reload(sale_alerts)
    monkeypatch.setattr(fresh, "SENT_FILE", tmp_path / "sent.json")
    assert fresh.once("k") is True and fresh.once("k") is False
    monkeypatch.setattr(fresh, "SENT_FILE", tmp_path / "no_such_dir" / "sent.json")
    assert fresh.once("new") is True                      # cannot write -> still True: a real sale is never silenced
