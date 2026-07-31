# tests/test_author_identity.py
# =========================================================
# Work Order D-003: Goodreads Author Program identity alignment.
# Verifies the /author page and its sitewide reinforcement (homepage
# link, Person schema email) present the three official-identity facts
# a Goodreads reviewer needs -- name, official website, official
# contact -- and that nothing else on the site was disturbed.
# =========================================================

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import app as app_module  # noqa: E402
import blueprints.payments as payments  # noqa: E402

BASE = "https://keaupuniakeakua.faith"
AUTHOR_NAME = "Kahu Phil Stephens"
AUTHOR_EMAIL = "kahuphil@keaupuni.faith"


@pytest.fixture
def client():
    payments.PAYPAL_CLIENT_ID = "fake_id"
    payments.PAYPAL_CLIENT_SECRET = "fake_secret"
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


class TestAuthorPage:
    def test_returns_200(self, client):
        resp = client.get("/author", base_url=BASE)
        assert resp.status_code == 200

    def test_states_official_name(self, client):
        html = client.get("/author", base_url=BASE).get_data(as_text=True)
        assert AUTHOR_NAME in html

    def test_states_official_website(self, client):
        html = client.get("/author", base_url=BASE).get_data(as_text=True)
        assert "keaupuniakeakua.faith" in html

    def test_states_official_contact_as_mailto(self, client):
        html = client.get("/author", base_url=BASE).get_data(as_text=True)
        assert f"mailto:{AUTHOR_EMAIL}" in html
        assert AUTHOR_EMAIL in html

    def test_links_to_a_real_published_work(self, client):
        html = client.get("/author", base_url=BASE).get_data(as_text=True)
        assert "/product/prod_find_the_cause_not_the_symptoms" in html
        assert "/products" in html

    def test_canonical_tag_correct(self, client):
        html = client.get("/author", base_url=BASE).get_data(as_text=True)
        assert '<link rel="canonical" href="https://keaupuniakeakua.faith/author" />' in html

    def test_webpage_schema_present_and_correct(self, client):
        html = client.get("/author", base_url=BASE).get_data(as_text=True)
        matches = re.findall(
            r'<script type="application/ld\+json">(\{.*?"@type": "WebPage".*?\})</script>',
            html,
            re.DOTALL,
        )
        assert matches, "no WebPage schema block found on /author"
        schema = json.loads(matches[0])
        assert schema["name"] == "Kahu Phil Stephens — About the Author"
        assert schema["url"] == "https://keaupuniakeakua.faith/author"

    def test_no_unpublished_book_claimed(self, client):
        html = client.get("/author", base_url=BASE).get_data(as_text=True)
        # Only genuinely active, real catalog products may be presented as
        # published works -- confirm every /product/<id> link on the page
        # resolves against the real catalog and returns 200.
        for product_id in re.findall(r'/product/([a-zA-Z0-9_]+)', html):
            resp = client.get(f"/product/{product_id}", base_url=BASE)
            assert resp.status_code == 200, f"/product/{product_id} does not resolve"


class TestSitewideIdentityReinforcement:
    def test_homepage_links_to_author_page(self, client):
        html = client.get("/", base_url=BASE).get_data(as_text=True)
        assert 'href="/author"' in html

    def test_person_schema_includes_contact_email(self, client):
        html = client.get("/", base_url=BASE).get_data(as_text=True)
        assert f'"email": "{AUTHOR_EMAIL}"' in html

    def test_person_schema_name_and_url_unchanged(self, client):
        html = client.get("/", base_url=BASE).get_data(as_text=True)
        assert '"name": "Kahu Phil Stephens"' in html
        assert '"url": "https://keaupuniakeakua.faith"' in html

    def test_sitemap_includes_author_no_duplicates(self, client):
        xml = client.get("/sitemap.xml", base_url=BASE).get_data(as_text=True)
        assert xml.count("<loc>https://keaupuniakeakua.faith/author</loc>") == 1


class TestExistingIdentitySurfacesUnaffected:
    """Regression guard: this work order must not have touched the
    pre-existing name/contact surfaces documented in prior work orders."""

    def test_product_page_still_shows_author_name(self, client):
        html = client.get(
            "/product/prod_find_the_cause_not_the_symptoms", base_url=BASE
        ).get_data(as_text=True)
        assert AUTHOR_NAME in html

    def test_products_listing_unaffected(self, client):
        resp = client.get("/products", base_url=BASE)
        assert resp.status_code == 200

    def test_rotten_fencepost_hub_unaffected(self, client):
        resp = client.get("/rotten-fencepost", base_url=BASE)
        assert resp.status_code == 200
