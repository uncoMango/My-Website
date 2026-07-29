# tests/test_campaign_pages.py
# =========================================================
# Work Order P-001: Discovery Operations campaign pages
# (/campaign/<id>, generic route + content.py's CAMPAIGNS dict).
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


class TestCampaignPageRenders:
    def test_campaign_001_returns_200(self, client):
        resp = client.get("/campaign/001", base_url=BASE)
        assert resp.status_code == 200

    def test_unknown_campaign_id_is_404(self, client):
        resp = client.get("/campaign/999", base_url=BASE)
        assert resp.status_code == 404

    def test_embeds_correct_video(self, client):
        resp = client.get("/campaign/001", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "https://www.youtube.com/embed/GywmvlrxXQ0" in html

    def test_links_to_rotten_fencepost_hub(self, client):
        resp = client.get("/campaign/001", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert 'href="/rotten-fencepost"' in html

    def test_links_to_product_001(self, client):
        resp = client.get("/campaign/001", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert 'href="/product/prod_find_the_cause_not_the_symptoms"' in html

    def test_has_title_and_meta_description(self, client):
        resp = client.get("/campaign/001", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "<title>Watch: Find the Cause, Not the Symptoms | Rotten Fencepost</title>" in html
        assert 'name="description"' in html


class TestCampaignPageSEOPreserved:
    def test_canonical_tag_present_and_correct(self, client):
        resp = client.get("/campaign/001", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert f'<link rel="canonical" href="{BASE}/campaign/001" />' in html

    def test_webpage_schema_present(self, client):
        resp = client.get("/campaign/001", base_url=BASE)
        html = resp.get_data(as_text=True)
        scripts = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL
        )
        assert any('"@type": "WebPage"' in s for s in scripts)

    def test_breadcrumb_schema_present(self, client):
        resp = client.get("/campaign/001", base_url=BASE)
        html = resp.get_data(as_text=True)
        scripts = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL
        )
        assert any('"@type": "BreadcrumbList"' in s for s in scripts)

    def test_og_and_twitter_tags_present(self, client):
        resp = client.get("/campaign/001", base_url=BASE)
        html = resp.get_data(as_text=True)
        for tag in ("og:title", "og:description", "og:image", "twitter:card"):
            assert tag in html


class TestSitemapAndInternalLinks:
    def test_sitemap_includes_campaign_001(self, client):
        resp = client.get("/sitemap.xml", base_url=BASE)
        xml = resp.get_data(as_text=True)
        locs = re.findall(r"<loc>(.*?)</loc>", xml)
        assert f"{BASE}/campaign/001" in locs
        assert len(locs) == len(set(locs))  # no duplicates introduced

    def test_rotten_fencepost_hub_links_to_campaign(self, client):
        resp = client.get("/rotten-fencepost", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert 'href="/campaign/001"' in html

    def test_rotten_fencepost_hub_still_links_to_product_001(self, client):
        # Pre-existing Work Order 010 link -- must survive this change.
        resp = client.get("/rotten-fencepost", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert 'href="/product/prod_find_the_cause_not_the_symptoms"' in html
