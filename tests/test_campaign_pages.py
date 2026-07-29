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


class TestRottenFencepostHubEmbed:
    """Work Order P-003: a curated, bounded set of campaign videos
    (content.py's HUB_FEATURED_CAMPAIGN_IDS) embedded directly on
    /rotten-fencepost, sourced from the same CAMPAIGNS data /campaign/001
    renders from."""

    def test_embeds_correct_video(self, client):
        resp = client.get("/rotten-fencepost", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "https://www.youtube.com/embed/GywmvlrxXQ0" in html

    def test_iframe_title_matches_campaign_title(self, client):
        resp = client.get("/rotten-fencepost", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert re.search(r'<iframe[^>]*title="Find the Cause, Not the Symptoms"', html)

    def test_links_to_campaign_page_for_sharing(self, client):
        resp = client.get("/rotten-fencepost", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert 'href="/campaign/001"' in html

    def test_hub_h1_unchanged(self, client):
        # The video embed must not replace or compete with the hub's own
        # product-focused title.
        resp = client.get("/rotten-fencepost", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "<h1" in html and "The Rotten Fencepost Field Guide" in html

    def test_hub_only_renders_featured_campaigns_not_all(self, client):
        # The hub must loop over the curated HUB_FEATURED_CAMPAIGN_IDS
        # list, not every CAMPAIGNS entry -- this is what keeps the hub
        # from growing unbounded as the campaign library grows past 60.
        import content
        resp = client.get("/rotten-fencepost", base_url=BASE)
        html = resp.get_data(as_text=True)
        embed_count = html.count("youtube.com/embed/")
        assert embed_count == len(content.HUB_FEATURED_CAMPAIGN_IDS)


class TestNoInternalIdentifierPublic:
    """Work Order P-002/P-003: 'Campaign 001' is an internal identifier
    and must never render on a public page."""

    def test_not_on_campaign_page(self, client):
        resp = client.get("/campaign/001", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "campaign 001" not in html.lower()

    def test_not_on_rotten_fencepost_hub(self, client):
        resp = client.get("/rotten-fencepost", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "campaign 001" not in html.lower()


class TestCampaignPageShorts:
    """Work Order P-003: campaign.shorts is a real, ready-to-use field on
    the CAMPAIGNS data structure, but must render nothing when empty --
    no fabricated/placeholder Shorts."""

    def test_no_shorts_section_when_none_published(self, client):
        resp = client.get("/campaign/001", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "Shorts From This Video" not in html

    def test_shorts_render_when_present(self, client):
        import content
        original = content.CAMPAIGNS["001"]["shorts"]
        content.CAMPAIGNS["001"]["shorts"] = [
            {"youtube_id": "abc123", "title": "Test Short"}
        ]
        try:
            resp = client.get("/campaign/001", base_url=BASE)
            html = resp.get_data(as_text=True)
            assert "Shorts From This Video" in html
            assert "youtube.com/embed/abc123" in html
            assert "Test Short" in html
        finally:
            content.CAMPAIGNS["001"]["shorts"] = original


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
