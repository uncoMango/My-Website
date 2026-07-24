# tests/test_partner_payments.py
# =========================================================
# Focused tests for the /partner payment repair (Phase 3):
#   - the four partner tier product IDs resolve in the catalog
#   - Stripe checkout no longer 404s on "product not found" for them
#     when Stripe is enabled (Stripe API itself is mocked - no real
#     network calls, no real Stripe account needed)
#   - Stripe buttons are hidden entirely when Stripe is disabled
#   - the partner success page (both payment methods) returns 200
#     without claiming a download, and without a fake, unverified
#     "success" - Stripe's payment_status and PayPal's order lookup
#     are exercised the same way the real routes already use them
#   - the Stripe cancellation destination returns 200 (a real product
#     page now exists for these IDs, so it's no longer a broken link)
#   - every visible PayPal button on /partner targets a real element
#     ID that actually exists in the rendered page - no detached,
#     unattached elements
# =========================================================

import sys
from pathlib import Path

import pytest
import stripe

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from blueprints import payments as payments_module  # noqa: E402
from blueprints import pages as pages_module  # noqa: E402
from content import get_product_by_id  # noqa: E402
import download_tokens as download_tokens_module  # noqa: E402
import app as app_module  # noqa: E402

PARTNER_TIER_IDS = ["partner_tier1", "partner_tier2", "partner_tier3", "partner_tier4"]


@pytest.fixture
def client():
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


class FakeStripeSession:
    """Stands in for a stripe.checkout.Session object without calling Stripe."""
    def __init__(self, url="https://checkout.stripe.com/fake-session", payment_status="paid"):
        self.url = url
        self.payment_status = payment_status
        self.customer_details = {}


# ---------------------------------------------------------------------------
# Catalog: the four partner tier IDs actually resolve now
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tier_id", PARTNER_TIER_IDS)
def test_partner_tier_resolves_in_catalog(tier_id):
    product = get_product_by_id(tier_id)
    assert product is not None
    assert product["active"] is True
    assert product["category"] == "partnership"


# ---------------------------------------------------------------------------
# Stripe: no longer 404s for "product not found" on partner tiers
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tier_id,expected_amount_cents", [
    ("partner_tier1", 2500),
    ("partner_tier2", 10000),
    ("partner_tier3", 25000),
    ("partner_tier4", 45000),
])
def test_stripe_checkout_session_created_for_partner_tiers(client, monkeypatch, tier_id, expected_amount_cents):
    monkeypatch.setattr(payments_module, "STRIPE_ENABLED", True)

    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return FakeStripeSession()

    monkeypatch.setattr(stripe.checkout.Session, "create", staticmethod(fake_create))

    resp = client.post(f"/stripe/create-session/{tier_id}")
    assert resp.status_code == 303  # redirect to Stripe, not a 404
    assert resp.headers["Location"] == "https://checkout.stripe.com/fake-session"
    assert captured["line_items"][0]["price_data"]["unit_amount"] == expected_amount_cents


def test_stripe_checkout_sends_absolute_image_urls(client, monkeypatch):
    """Stripe rejects product_data.images entries that aren't fully-qualified
    (http/https) URLs with a 400 InvalidRequestError, which - uncaught -
    surfaces to the buyer as a 500. Catalog entries store cover_image as a
    site-relative path (e.g. "/static/covers/foo.jpg"), so the route must
    qualify it with SITE_DOMAIN before handing it to Stripe."""
    monkeypatch.setattr(payments_module, "STRIPE_ENABLED", True)

    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return FakeStripeSession()

    monkeypatch.setattr(stripe.checkout.Session, "create", staticmethod(fake_create))

    resp = client.post("/stripe/create-session/prod_find_the_cause_not_the_symptoms")
    assert resp.status_code == 303
    images = captured["line_items"][0]["price_data"]["product_data"]["images"]
    assert images == ["https://keaupuniakeakua.faith/static/covers/find_the_cause_not_the_symptoms_cover_web.jpg"]
    assert images[0].startswith(("http://", "https://"))


def test_stripe_checkout_still_404s_for_genuinely_unknown_product(client, monkeypatch):
    monkeypatch.setattr(payments_module, "STRIPE_ENABLED", True)
    monkeypatch.setattr(stripe.checkout.Session, "create", staticmethod(lambda **kw: FakeStripeSession()))
    resp = client.post("/stripe/create-session/not_a_real_product")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Stripe buttons hidden when Stripe is disabled - no dead buttons
# ---------------------------------------------------------------------------

def test_partner_page_hides_stripe_buttons_when_disabled(client, monkeypatch):
    monkeypatch.setattr(pages_module, "STRIPE_ENABLED", False)
    html = client.get("/partner").get_data(as_text=True)
    assert "/stripe/create-session/partner_tier1" not in html
    assert "/stripe/create-session/partner_tier2" not in html
    assert "/stripe/create-session/partner_tier3" not in html
    assert "/stripe/create-session/partner_tier4" not in html
    assert "/stripe/create-session/prod_nahenahe_cd" not in html


def test_partner_page_shows_stripe_buttons_when_enabled(client, monkeypatch):
    monkeypatch.setattr(pages_module, "STRIPE_ENABLED", True)
    html = client.get("/partner").get_data(as_text=True)
    assert "/stripe/create-session/partner_tier1" in html
    assert "/stripe/create-session/partner_tier4" in html


# ---------------------------------------------------------------------------
# PayPal: every button targets a real, attached element - no detached div
# ---------------------------------------------------------------------------

def _enable_paypal(monkeypatch):
    monkeypatch.setattr(pages_module, "PAYPAL_CLIENT_ID", "fake-client-id-for-test")
    monkeypatch.setattr(pages_module, "PAYPAL_CLIENT_SECRET", "fake-secret-for-test")


def _disable_paypal(monkeypatch):
    monkeypatch.setattr(pages_module, "PAYPAL_CLIENT_ID", "")
    monkeypatch.setattr(pages_module, "PAYPAL_CLIENT_SECRET", "")


def test_partner_page_has_no_detached_paypal_elements(client, monkeypatch):
    _enable_paypal(monkeypatch)
    html = client.get("/partner").get_data(as_text=True)
    assert "document.createElement('div')" not in html
    assert "payWithPayPal(" not in html  # old broken function name is gone


@pytest.mark.parametrize("container_id", [
    "paypal-btn-tier1", "paypal-btn-tier2", "paypal-btn-tier3", "paypal-btn-tier4", "paypal-btn-cd",
])
def test_partner_page_paypal_container_exists_and_is_mounted(client, monkeypatch, container_id):
    _enable_paypal(monkeypatch)
    html = client.get("/partner").get_data(as_text=True)
    # The container is a real element in the rendered HTML...
    assert f'id="{container_id}"' in html
    # ...and the page explicitly asks to mount a PayPal button into that exact element.
    assert f"mountPartnerPayPalButton('{container_id}'" in html
    # mountPartnerPayPalButton renders into the real, passed-in container ID
    # (not a detached node) - confirm that function's render call targets
    # whatever ID it's given, by ID, rather than an in-memory element.
    assert ".render('#' + containerId)" in html
    assert "document.getElementById(containerId)" in html


def test_partner_page_paypal_sdk_script_present_when_enabled(client, monkeypatch):
    _enable_paypal(monkeypatch)
    html = client.get("/partner").get_data(as_text=True)
    assert "https://www.paypal.com/sdk/js?client-id=fake-client-id-for-test" in html


# ---------------------------------------------------------------------------
# PayPal unavailable: no dead/empty controls, one truthful message, no crash
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("container_id", [
    "paypal-btn-tier1", "paypal-btn-tier2", "paypal-btn-tier3", "paypal-btn-tier4", "paypal-btn-cd",
])
def test_partner_page_omits_paypal_containers_when_unconfigured(client, monkeypatch, container_id):
    _disable_paypal(monkeypatch)
    html = client.get("/partner").get_data(as_text=True)
    assert f'id="{container_id}"' not in html


def test_partner_page_omits_paypal_sdk_script_when_unconfigured(client, monkeypatch):
    _disable_paypal(monkeypatch)
    html = client.get("/partner").get_data(as_text=True)
    assert "www.paypal.com/sdk/js" not in html


def test_partner_page_shows_single_unavailable_notice_when_unconfigured(client, monkeypatch):
    _disable_paypal(monkeypatch)
    html = client.get("/partner").get_data(as_text=True)
    assert html.count("PayPal is temporarily unavailable.") == 1
    # And it's actually visible without needing JS - not hidden by default.
    assert 'id="paypal-unavailable-notice" style="display:block' in html


def test_partner_page_notice_hidden_by_default_when_paypal_enabled(client, monkeypatch):
    _enable_paypal(monkeypatch)
    html = client.get("/partner").get_data(as_text=True)
    assert html.count("PayPal is temporarily unavailable.") == 1  # element exists once either way
    assert 'id="paypal-unavailable-notice" style="display:none' in html  # but hidden


def test_partner_page_js_has_defensive_sdk_checks(client, monkeypatch):
    """To the extent practical without a real browser: confirm the page's own
    JS guards against a missing/failed SDK rather than assuming it worked."""
    _enable_paypal(monkeypatch)
    html = client.get("/partner").get_data(as_text=True)
    assert "function paypalSdkReady()" in html
    assert "typeof paypal !== 'undefined'" in html
    assert "typeof paypal.Buttons === 'function'" in html
    assert "showPayPalUnavailableNotice" in html
    assert "try {" in html and "catch (e)" in html


# ---------------------------------------------------------------------------
# Success pages: verified before showing "success", no false download claim
# ---------------------------------------------------------------------------

def test_stripe_partner_success_returns_200_without_download_claim(client, monkeypatch):
    monkeypatch.setattr(payments_module, "STRIPE_ENABLED", True)
    monkeypatch.setattr(payments_module, "save_digital_products", lambda data: None)
    monkeypatch.setattr(
        stripe.checkout.Session, "retrieve",
        staticmethod(lambda session_id: FakeStripeSession(payment_status="paid")),
    )
    resp = client.get("/stripe/success?session_id=fake_session&product_id=partner_tier1")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Download Your Ebook" not in html
    assert "Mahalo" in html


def test_stripe_success_rejects_unpaid_session(client, monkeypatch):
    monkeypatch.setattr(payments_module, "STRIPE_ENABLED", True)
    monkeypatch.setattr(payments_module, "save_digital_products", lambda data: None)
    monkeypatch.setattr(
        stripe.checkout.Session, "retrieve",
        staticmethod(lambda session_id: FakeStripeSession(payment_status="unpaid")),
    )
    resp = client.get("/stripe/success?session_id=fake_session&product_id=partner_tier1")
    assert resp.status_code == 402  # existing verification behavior, now returns cleanly instead of crashing


def test_paypal_partner_success_returns_200_without_download_claim(client, monkeypatch):
    # PayPal order-detail lookup already fails safely (silently) in the
    # existing route if it can't reach PayPal's API - simulate that here
    # rather than making a real network call in the test suite.
    monkeypatch.setattr(
        payments_module, "_get_paypal_token",
        lambda: (_ for _ in ()).throw(Exception("no network in tests")),
    )
    monkeypatch.setattr(payments_module, "save_digital_products", lambda data: None)
    resp = client.get("/paypal/success?orderID=fake_order&product_id=partner_tier1")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Download Your Ebook" not in html
    assert "Mahalo" in html


def test_regular_product_paypal_success_still_offers_download(client, monkeypatch):
    """Non-partnership products must keep their existing download-success page.

    The download link is now a signed, token-gated URL (see
    tests/test_download_tokens.py) rather than the old bare product-ID
    URL, so this only checks the link still targets this product's
    download route, not the exact old URL string.
    """
    monkeypatch.setattr(download_tokens_module, "DOWNLOAD_TOKEN_SECRET", "test-only-download-secret-not-real")
    monkeypatch.setattr(
        payments_module, "_get_paypal_token",
        lambda: (_ for _ in ()).throw(Exception("no network in tests")),
    )
    monkeypatch.setattr(payments_module, "save_digital_products", lambda data: None)
    resp = client.get("/paypal/success?orderID=fake_order&product_id=prod_aloha_wellness")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "/download/product/prod_aloha_wellness/" in html


def test_success_template_selection_ignores_visitor_supplied_category(client, monkeypatch):
    """A visitor cannot force the partnership success page for a real,
    non-partnership product by adding an arbitrary 'category' query param -
    the route never reads request.args for category at all; it only ever
    trusts product.get('category') from the server-side catalog record
    resolved from product_id."""
    monkeypatch.setattr(download_tokens_module, "DOWNLOAD_TOKEN_SECRET", "test-only-download-secret-not-real")
    monkeypatch.setattr(
        payments_module, "_get_paypal_token",
        lambda: (_ for _ in ()).throw(Exception("no network in tests")),
    )
    monkeypatch.setattr(payments_module, "save_digital_products", lambda data: None)
    resp = client.get(
        "/paypal/success?orderID=fake_order&product_id=prod_aloha_wellness&category=partnership"
    )
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    # Still the real ebook's download-success page, not the partner template.
    assert "/download/product/prod_aloha_wellness/" in html
    assert "Mahalo, Partner." not in html


# ---------------------------------------------------------------------------
# Cancellation: Stripe's cancel_url now resolves to a real page, not a 404,
# and does not misrepresent a partnership as a downloadable product.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tier_id", PARTNER_TIER_IDS)
def test_stripe_cancel_destination_returns_200(client, tier_id):
    resp = client.get(f"/product/{tier_id}?cancelled=true")
    assert resp.status_code == 200


@pytest.mark.parametrize("tier_id", PARTNER_TIER_IDS)
def test_stripe_cancel_destination_has_partnership_wording_not_download_claims(client, tier_id):
    html = client.get(f"/product/{tier_id}?cancelled=true").get_data(as_text=True)
    assert "Your gift supports Kingdom teaching" in html
    assert "Instant digital download" not in html
    assert "No DRM" not in html


def test_paypal_cancel_destination_returns_200(client):
    resp = client.get("/paypal/cancel", follow_redirects=True)
    assert resp.status_code == 200
