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
        # Click-to-play lite embed (2026-08-08 visual-rendering repair):
        # no raw <iframe> in the initial HTML anymore -- the real video id
        # is carried on data-yt-id and only becomes an iframe on click
        # (see base.html's rfPlayVideo). 2026-08-08 photo library work
        # order: Campaign 001 now has a real local branded thumbnail
        # (thumbnail_image), so it no longer falls back to YouTube's own
        # hqdefault.jpg -- the correct video is still unambiguous via
        # data-yt-id.
        resp = client.get("/campaign/001", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert 'data-yt-id="GywmvlrxXQ0"' in html
        assert "/static/rf_photo_library/derivatives/campaign_001_thumbnail_16x9.jpg" in html

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
        assert 'data-yt-id="GywmvlrxXQ0"' in html
        assert "/static/rf_photo_library/derivatives/campaign_001_thumbnail_16x9.jpg" in html

    def test_iframe_title_matches_campaign_title(self, client):
        resp = client.get("/rotten-fencepost", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert re.search(r'data-yt-title="Find the Cause, Not the Symptoms"', html)

    def test_links_to_campaign_page_for_sharing(self, client):
        resp = client.get("/rotten-fencepost", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert 'href="/campaign/001"' in html

    def test_hub_h1_is_the_principle(self, client):
        # Work Order V001-002: the hub leads with the Rotten Fencepost
        # Principle itself, not a product name -- the video embed must not
        # compete with that single, page-level H1.
        resp = client.get("/rotten-fencepost", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert re.search(r"<h1[^>]*>The Rotten Fencepost Principle</h1>", html)
        assert html.count("<h1") == 1

    def test_hub_only_renders_featured_campaigns_not_all(self, client):
        # The hub must loop over the curated HUB_FEATURED_CAMPAIGN_IDS
        # list, not every CAMPAIGNS entry -- this is what keeps the hub
        # from growing unbounded as the campaign library grows past 60.
        import content
        resp = client.get("/rotten-fencepost", base_url=BASE)
        html = resp.get_data(as_text=True)
        embed_count = html.count('class="yt-lite"')
        assert embed_count == len(content.HUB_FEATURED_CAMPAIGN_IDS)

    def test_campaign_003_is_discoverable_from_the_hub(self, client):
        # 2026-08-17 Campaign 003 website-fruition repair: Campaign 003's
        # own /campaign/003 page, article, and workbook were all live and
        # independently reachable, but HUB_FEATURED_CAMPAIGN_IDS was never
        # updated to include "003" -- reachable directly, undiscoverable
        # from the public hub a real visitor actually lands on. This test
        # guards against a future revert of that one-line fix.
        import content
        assert "003" in content.HUB_FEATURED_CAMPAIGN_IDS
        resp = client.get("/rotten-fencepost", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert 'href="/campaign/003"' in html


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


class TestVideoLiteEmbedAndHeroFit:
    """2026-08-08 (Urgent Visual Rendering Repair): YouTube's own iframe
    poster crops its custom thumbnail to fill the fixed 16:9 box, cutting
    off the subject (Campaign 001) or showing a generic placeholder before
    interaction (Campaign 002) -- neither is controllable from our CSS
    since the iframe's content is cross-origin. Fixed by rendering the
    real hqdefault.jpg thumbnail ourselves via object-fit:contain, only
    loading the real <iframe> on click (base.html's rfPlayVideo)."""

    def test_campaign_page_uses_lite_embed_not_raw_iframe(self, client):
        resp = client.get("/campaign/001", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "<iframe src=" not in html
        assert 'class="yt-lite"' in html
        assert 'data-yt-id="GywmvlrxXQ0"' in html
        assert "/static/rf_photo_library/derivatives/campaign_001_thumbnail_16x9.jpg" in html
        assert "object-fit: contain" in html

    def test_thumbnail_image_falls_back_to_youtube_when_unset(self, client):
        # Future-campaign standard: a campaign without a custom
        # thumbnail_image yet must still work, via the same YouTube
        # hqdefault.jpg fallback used before this library existed.
        import content
        original = content.CAMPAIGNS["001"].pop("thumbnail_image", None)
        try:
            resp = client.get("/campaign/001", base_url=BASE)
            html = resp.get_data(as_text=True)
            assert "https://i.ytimg.com/vi/GywmvlrxXQ0/hqdefault.jpg" in html
        finally:
            if original is not None:
                content.CAMPAIGNS["001"]["thumbnail_image"] = original

    def test_hub_card_uses_lite_embed_not_raw_iframe(self, client):
        resp = client.get("/rotten-fencepost", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "<iframe src=" not in html
        assert 'class="yt-lite"' in html

    def test_rf_play_video_function_defined_sitewide(self, client):
        resp = client.get("/rotten-fencepost", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "function rfPlayVideo(container)" in html

    def test_campaign_002_hero_uses_contain_not_cover(self, client):
        # 2026-08-08 photo library work order: hero_image now points at
        # the best-resolution recovered copy (still near-square) rather
        # than the old 203x206 static/images/paniolo_phil.jpg. Under the
        # shared .hero rule's background-size:cover, a box this much wider
        # than the image would still force a centered crop showing only
        # the middle band -- hero_fit="contain" letterboxes it instead so
        # the full composition (Kahu Phil, the horse, the ukulele) stays
        # visible.
        resp = client.get("/campaign/002", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "/static/rf_photo_library/sources/rf_phil_horse_ukulele_beach.jpg" in html
        assert "background-size: contain" in html

    def test_article_hero_also_uses_contain_not_cover(self, client):
        # The Campaign 002 article (/rotten-fencepost/why-do-i-keep-
        # starting-over) has its own separate hero_image field in
        # blueprints/pages.py's _SEO_PAGES, rendered by page.html (not
        # campaign_page.html) -- same underlying image, same crop defect,
        # so it needs the same hero_fit support and the same fix.
        resp = client.get("/rotten-fencepost/why-do-i-keep-starting-over", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "/static/rf_photo_library/sources/rf_phil_horse_ukulele_beach.jpg" in html
        assert "background-size: contain" in html

    def test_homepage_hero_still_uses_default_cover(self, client):
        # page.html's header now conditionally supports hero_fit -- must
        # not affect the homepage (which never sets that field).
        resp = client.get("/", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "background-size: contain" not in html

    def test_campaign_001_hero_still_uses_default_cover(self, client):
        # Campaign 001's hero is a properly-sized landscape photo -- must
        # not be affected by Campaign 002's per-campaign hero_fit override.
        resp = client.get("/campaign/001", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "background-size: contain" not in html


class TestCampaignWorkbookCTA:
    """2026-08-07: a produced, free, publicly-hosted workbook is not
    fruition unless a visitor can actually find it -- workbook_cta is a
    campaign-generic optional field (like `shorts`) that renders nothing
    when absent, and a clearly-labeled, prominently-placed callout when
    present."""

    def test_no_workbook_cta_when_field_absent(self, client):
        resp = client.get("/campaign/001", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "Free Companion Workbook" not in html

    def test_workbook_cta_renders_when_present(self, client):
        import content
        original = content.CAMPAIGNS["001"].get("workbook_cta")
        content.CAMPAIGNS["001"]["workbook_cta"] = {
            "title": "Test Workbook", "description": "A test description.",
            "label": "Download the Free Workbook", "url": "/media/test_workbook",
        }
        try:
            resp = client.get("/campaign/001", base_url=BASE)
            html = resp.get_data(as_text=True)
            assert "Free Companion Workbook" in html
            assert "Test Workbook" in html
            assert 'href="/media/test_workbook"' in html
            assert "Download the Free Workbook" in html
        finally:
            if original is None:
                content.CAMPAIGNS["001"].pop("workbook_cta", None)
            else:
                content.CAMPAIGNS["001"]["workbook_cta"] = original

    def test_campaign_002_workbook_cta_is_real_and_free(self, client):
        resp = client.get("/campaign/002", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "Free Companion Workbook" in html
        assert 'href="/media/campaign_002_planning_document_workbook_pdf_v9"' in html
        assert "Download the Free Workbook" in html

    def test_campaign_002_article_also_has_workbook_cta(self, client):
        resp = client.get("/rotten-fencepost/why-do-i-keep-starting-over", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "Free Companion Workbook" in html
        assert 'href="/media/campaign_002_planning_document_workbook_pdf_v9"' in html

    def test_campaign_002_workbook_cta_is_a_light_high_contrast_box_not_dark_on_dark(self, client):
        """2026-08-07 (second correction): the CTA on /campaign/002 previously
        used a dark teal gradient (#1a4040/#0d2b2b) on the page's #1a1a1a
        background -- effectively invisible. Kahu Phil could not find it on
        the live site despite it being present in the HTML. Fixed by matching
        the article page's already-proven light box (#eef2f0) treatment."""
        resp = client.get("/campaign/002", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "#1a4040" not in html
        assert "#0d2b2b" not in html
        assert "#eef2f0" in html


class TestFirstPersonTeachingVoice:
    """2026-08-07: Kahu Phil-authored teaching must speak FROM him, not
    describe him in third person (About/bio pages remain a legitimate
    exception -- see test_author_page_stays_third_person below)."""

    def test_campaign_001_article_uses_first_person(self, client):
        resp = client.get("/rotten-fencepost/find-the-cause-not-the-symptoms", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "Kahu Phil Stephens teaches this idea" not in html
        assert "I teach this idea through a simple" in html

    def test_campaign_002_article_uses_first_person(self, client):
        resp = client.get("/rotten-fencepost/why-do-i-keep-starting-over", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "Kahu Phil Stephens has been blessed" not in html
        assert "I&#39;ve been blessed to live and work as a paniolo" in html or "I've been blessed to live and work as a paniolo" in html

    def test_wellness_article_uses_first_person(self, client):
        resp = client.get("/wellness/the-rotten-fencepost-principle", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "Kahu Phil Stephens learned this lesson" not in html
        assert "I learned this lesson working cattle" in html

    def test_author_page_stays_third_person(self, client):
        # Legitimate exception: an "About the Author" page is genuinely
        # written about him, not as his own teaching voice.
        resp = client.get("/author", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "Kahu Phil Stephens is a pastor and author" in html


class TestRottenFencepostNotPrimarilyWellness:
    def test_wellness_article_frames_principle_as_overarching(self, client):
        resp = client.get("/wellness/the-rotten-fencepost-principle", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "isn&#39;t a wellness program" in html or "isn't a wellness program" in html
        assert 'href="/rotten-fencepost"' in html

    def test_wellness_article_title_is_rotten_fencepost_centered(self, client):
        """2026-08-07 (second correction): the old title, 'The Rotten
        Fencepost Principle and Modern Wellness Confusion', made wellness
        read as if it defined the Principle. Retitled around the article's
        own existing content instead of inventing new framing."""
        resp = client.get("/wellness/the-rotten-fencepost-principle", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "Modern Wellness Confusion" not in html
        assert "The Rotten Fencepost Principle: When the Foundation Is Off" in html

    def test_wellness_article_hero_image_is_not_taro(self, client):
        """The taro close-up (taro_root.jpg) read as generic food/wellness
        imagery unrelated to the fencepost teaching. Replaced with an
        existing, already-approved ranch photo (molokai_ranch.jpg) -- no
        new imagery was introduced."""
        resp = client.get("/wellness/the-rotten-fencepost-principle", base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "taro_root.jpg" not in html
        assert "molokai_ranch.jpg" in html

    def test_cross_references_use_updated_title_text(self, client):
        """Other pages that link to the wellness article using the OLD
        title as visible anchor text would otherwise still tell a visitor
        this is primarily about 'wellness confusion' -- undermining the
        retitle. All must be updated to matching anchor text."""
        for path in (
            "/rotten-fencepost",
            "/rotten-fencepost/find-the-cause-not-the-symptoms",
            "/campaign/001",
        ):
            resp = client.get(path, base_url=BASE)
            html = resp.get_data(as_text=True)
            assert "Modern Wellness Confusion" not in html, f"{path} still uses the old wellness-article title"


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
