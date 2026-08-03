# tests/test_rotten_fencepost_article.py
# =========================================================
# Discovery Workforce Campaign 001: the general-audience evergreen
# article ("Find the Cause, Not the Symptoms: The Rotten Fencepost
# Principle") at /rotten-fencepost/find-the-cause-not-the-symptoms,
# added via the existing _SEO_PAGES / generic /<parent>/<slug> route
# (blueprints/pages.py) -- no new route or template.
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
PATH = "/rotten-fencepost/find-the-cause-not-the-symptoms"


@pytest.fixture
def client():
    payments.PAYPAL_CLIENT_ID = "fake_id"
    payments.PAYPAL_CLIENT_SECRET = "fake_secret"
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


class TestArticleRenders:
    def test_returns_200(self, client):
        resp = client.get(PATH, base_url=BASE)
        assert resp.status_code == 200

    def test_has_title_and_meta_description(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "<title>Find the Cause, Not the Symptoms — The Rotten Fencepost Principle | Ke Aupuni O Ke Akua</title>" in html
        assert 'name="description"' in html

    def test_canonical_tag_correct(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert f'<link rel="canonical" href="{BASE}{PATH}" />' in html

    def test_article_schema_present(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
        assert any('"@type": "Article"' in s for s in scripts)


class TestArticleContentAndLinks:
    def test_hero_image_is_real_live_asset(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "/static/covers/find_the_cause_not_the_symptoms_cover_web.jpg" in html

    def test_links_to_rotten_fencepost_hub(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert 'href="/rotten-fencepost"' in html

    def test_links_to_product_001(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert 'href="/product/prod_find_the_cause_not_the_symptoms"' in html

    def test_links_to_companion_wellness_article(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert 'href="/wellness/the-rotten-fencepost-principle"' in html

    def test_no_internal_campaign_identifier_on_public_page(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "campaign 001" not in html.lower()
        assert "campaign_001" not in html.lower()


class TestCampaignPageLinksToArticle:
    def test_campaign_001_related_links_include_the_new_article(self, client):
        resp = client.get("/campaign/001", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert f'href="{PATH}"' in html


class TestSitemapIncludesArticle:
    def test_sitemap_includes_article_exactly_once(self, client):
        resp = client.get("/sitemap.xml", base_url=BASE)
        xml = resp.get_data(as_text=True)
        locs = re.findall(r"<loc>(.*?)</loc>", xml)
        assert locs.count(f"{BASE}{PATH}") == 1
        assert len(locs) == len(set(locs))  # no duplicates anywhere in the sitemap
