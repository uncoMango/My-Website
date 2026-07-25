# tests/test_indexing_readiness.py
# =========================================================
# Work Order 009: guards search-engine indexing readiness --
# sitemap completeness/exclusions, robots.txt, and noindex correctness.
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


@pytest.fixture
def client():
    payments.PAYPAL_CLIENT_ID = "fake_id"
    payments.PAYPAL_CLIENT_SECRET = "fake_secret"
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


def _sitemap_locs(client):
    resp = client.get("/sitemap.xml", base_url=BASE)
    xml = resp.get_data(as_text=True)
    return re.findall(r"<loc>(.*?)</loc>", xml)


ACTIVE_PRODUCT_PAGES = [
    "/product/prod_find_the_cause_not_the_symptoms",
    "/product/prod_aloha_wellness",
    "/product/prod_kingdom_booklet1",
    "/product/prod_kingdom_booklet2",
    "/product/prod_nahenahe_cd",
]

DELIBERATELY_EXCLUDED_PRODUCT_PAGES = [
    "/product/rotten_fencepost_field_guide",
    "/product/partner_tier1",
    "/product/partner_tier2",
    "/product/partner_tier3",
    "/product/partner_tier4",
]

PRIVATE_PAGES = [
    "/checkout/rotten_fencepost_field_guide",
    "/thank-you",
    "/rotten-fencepost/success",
]


class TestSitemapCompleteness:
    def test_all_active_product_pages_are_in_sitemap(self, client):
        locs = _sitemap_locs(client)
        for path in ACTIVE_PRODUCT_PAGES:
            assert BASE + path in locs, f"{path} should be in sitemap.xml"

    def test_deliberately_excluded_product_pages_are_not_in_sitemap(self, client):
        locs = _sitemap_locs(client)
        for path in DELIBERATELY_EXCLUDED_PRODUCT_PAGES:
            assert BASE + path not in locs, f"{path} should NOT be in sitemap.xml"

    def test_transactional_and_admin_paths_not_in_sitemap(self, client):
        locs = _sitemap_locs(client)
        for loc in locs:
            assert "/checkout/" not in loc
            assert "/download/" not in loc
            assert "/kahu" not in loc
            assert "/admin" not in loc
            assert "/thank-you" not in loc
            assert "/success" not in loc

    def test_no_lastmod_present(self, client):
        resp = client.get("/sitemap.xml", base_url=BASE)
        xml = resp.get_data(as_text=True)
        assert "<lastmod>" not in xml

    def test_every_sitemap_url_resolves_200(self, client):
        for loc in _sitemap_locs(client):
            path = loc.replace(BASE, "")
            resp = client.get(path, base_url=BASE)
            assert resp.status_code == 200, f"{path} returned {resp.status_code}"

    def test_sitemap_has_no_duplicate_urls(self, client):
        locs = _sitemap_locs(client)
        assert len(locs) == len(set(locs))


class TestRobotsTxt:
    def test_robots_disallows_admin_areas(self, client):
        resp = client.get("/robots.txt", base_url=BASE)
        text = resp.get_data(as_text=True)
        assert "Disallow: /kahu" in text
        assert "Disallow: /admin" in text

    def test_robots_references_sitemap(self, client):
        resp = client.get("/robots.txt", base_url=BASE)
        text = resp.get_data(as_text=True)
        assert "Sitemap: https://keaupuniakeakua.faith/sitemap.xml" in text

    def test_robots_allows_root(self, client):
        resp = client.get("/robots.txt", base_url=BASE)
        text = resp.get_data(as_text=True)
        assert "Allow: /" in text


class TestNoindexCorrectness:
    @pytest.mark.parametrize("path", ACTIVE_PRODUCT_PAGES + [
        "/", "/kingdom_wealth", "/ecosystem", "/rotten-fencepost", "/kingdom-study",
        "/myron-golden", "/aloha-wellness", "/wellness/why-diets-fail",
    ])
    def test_public_pages_have_no_noindex(self, client, path):
        resp = client.get(path, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert not re.search(r'<meta\s+name="robots"[^>]*noindex', html, re.I), \
            f"{path} unexpectedly has a noindex directive"

    @pytest.mark.parametrize("path", PRIVATE_PAGES)
    def test_private_pages_have_noindex(self, client, path):
        resp = client.get(path, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert re.search(r'<meta\s+name="robots"[^>]*noindex', html, re.I), \
            f"{path} is missing its noindex directive"


class Test404Handling:
    @pytest.mark.parametrize("path", [
        "/this-page-does-not-exist",
        "/wellness/nonexistent-slug",
        "/product/fake_product_id",
    ])
    def test_nonexistent_pages_return_real_404(self, client, path):
        resp = client.get(path, base_url=BASE)
        assert resp.status_code == 404
