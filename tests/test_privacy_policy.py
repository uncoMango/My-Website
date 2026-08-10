# tests/test_privacy_policy.py
# =========================================================
# Rotten Fencepost Foreman YouTube API compliance audit: the one public
# page Google's Audit and Quota Extension Form requires (Privacy Policy
# URL, evidence screenshots) before the Foreman's already-proven upload
# pipeline can publish public (not just private) videos. Copy approved
# verbatim by Kahu Phil -- see the Discovery Engine's own PROJECT_LOG.md,
# 2026-08-10, and Long_Form_Video_Publishing_Agent/evidence/
# YOUTUBE_COMPLIANCE_AUDIT_PACKAGE.md for the full review trail.
# =========================================================

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import app as app_module  # noqa: E402
import blueprints.payments as payments  # noqa: E402

BASE = "https://keaupuniakeakua.faith"
CONTACT_EMAIL = "kahuphil@keaupuni.faith"


@pytest.fixture
def client():
    payments.PAYPAL_CLIENT_ID = "fake_id"
    payments.PAYPAL_CLIENT_SECRET = "fake_secret"
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


class TestPrivacyPolicyPage:
    def test_returns_200(self, client):
        resp = client.get("/privacy-policy", base_url=BASE)
        assert resp.status_code == 200

    def test_states_youtube_api_services_use(self, client):
        html = client.get("/privacy-policy", base_url=BASE).get_data(as_text=True)
        assert "YouTube API Services" in html

    def test_states_scope_requested(self, client):
        html = client.get("/privacy-policy", base_url=BASE).get_data(as_text=True)
        assert "youtube.upload" in html

    def test_states_what_it_accesses_and_stores(self, client):
        html = client.get("/privacy-policy", base_url=BASE).get_data(as_text=True)
        assert "does not access, collect, or store YouTube data belonging to any other channel or person" in html

    def test_states_revocation_language(self, client):
        html = client.get("/privacy-policy", base_url=BASE).get_data(as_text=True)
        assert "Revoking authorization prevents the Foreman from making further authorized YouTube API calls" in html
        assert "does not itself delete videos or other information already stored by YouTube" in html

    def test_links_to_google_account_permissions(self, client):
        html = client.get("/privacy-policy", base_url=BASE).get_data(as_text=True)
        assert 'href="https://myaccount.google.com/permissions"' in html

    def test_links_to_google_privacy_policy(self, client):
        html = client.get("/privacy-policy", base_url=BASE).get_data(as_text=True)
        assert 'href="https://policies.google.com/privacy"' in html

    def test_links_to_youtube_terms_of_service(self, client):
        html = client.get("/privacy-policy", base_url=BASE).get_data(as_text=True)
        assert 'href="https://www.youtube.com/t/terms"' in html

    def test_contact_email_is_clickable_mailto(self, client):
        html = client.get("/privacy-policy", base_url=BASE).get_data(as_text=True)
        assert f'href="mailto:{CONTACT_EMAIL}"' in html
        assert CONTACT_EMAIL in html

    def test_canonical_tag_correct(self, client):
        html = client.get("/privacy-policy", base_url=BASE).get_data(as_text=True)
        assert '<link rel="canonical" href="https://keaupuniakeakua.faith/privacy-policy" />' in html

    def test_no_generic_sitewide_privacy_content(self, client):
        # Scope discipline: this is the narrow YouTube-integration disclosure
        # the compliance audit requires, not a generic sitewide privacy
        # policy (cookies, analytics, checkout data handling, etc.). Scoped
        # to the page's own article body -- the sitewide <head> already
        # carries an unrelated, pre-existing Google Analytics snippet on
        # every page, which this work order did not add and is not in scope
        # to remove.
        html = client.get("/privacy-policy", base_url=BASE).get_data(as_text=True)
        match = re.search(r'<article class="content-card">(.*?)</article>', html, re.DOTALL)
        assert match, "content-card article body not found"
        body = match.group(1).lower()
        assert "cookie" not in body
        assert "analytics" not in body


class TestSitewideFooterLink:
    def test_homepage_footer_links_to_privacy_policy(self, client):
        html = client.get("/", base_url=BASE).get_data(as_text=True)
        assert 'href="/privacy-policy"' in html
        assert "Privacy Policy" in html

    def test_footer_link_present_on_a_second_page_too(self, client):
        # Confirms this is the shared base.html footer, not a one-page fix.
        html = client.get("/author", base_url=BASE).get_data(as_text=True)
        assert 'href="/privacy-policy"' in html

    def test_only_one_privacy_policy_link_in_footer(self, client):
        html = client.get("/", base_url=BASE).get_data(as_text=True)
        assert html.count('href="/privacy-policy"') == 1

    def test_sitemap_includes_privacy_policy_no_duplicates(self, client):
        xml = client.get("/sitemap.xml", base_url=BASE).get_data(as_text=True)
        assert xml.count("<loc>https://keaupuniakeakua.faith/privacy-policy</loc>") == 1


class TestExistingSurfacesUnaffected:
    """Regression guard: this narrow deployment must not have touched
    unrelated pages, funnels, routes, styles, or integrations."""

    def test_homepage_still_200(self, client):
        assert client.get("/", base_url=BASE).status_code == 200

    def test_author_page_still_200(self, client):
        assert client.get("/author", base_url=BASE).status_code == 200

    def test_rotten_fencepost_hub_still_200(self, client):
        assert client.get("/rotten-fencepost", base_url=BASE).status_code == 200

    def test_campaign_002_still_200(self, client):
        assert client.get("/campaign/002", base_url=BASE).status_code == 200

    def test_products_listing_still_200(self, client):
        assert client.get("/products", base_url=BASE).status_code == 200
