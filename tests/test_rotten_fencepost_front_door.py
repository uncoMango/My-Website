# tests/test_rotten_fencepost_front_door.py
# =========================================================
# Work Order V001-002: Rotten Fencepost is the Principle first, and every
# resource (video, books, field guide) is a doorway into it. Guards the
# approved visitor journey on /rotten-fencepost:
#   1. The Rotten Fencepost Principle
#   2. Begin Your Journey (Find the Cause, Not the Symptoms)
#   3. Watch the Foundation Series
#   4. Study the Principle (Rotten Fencepost Field Guide)
#   5. A Personal Invitation from Kahu Phil
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
PATH = "/rotten-fencepost"


@pytest.fixture
def client():
    payments.PAYPAL_CLIENT_ID = "fake_id"
    payments.PAYPAL_CLIENT_SECRET = "fake_secret"
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


def _ld_entities(html):
    entities = []
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        data = json.loads(block)
        if "@graph" in data:
            entities.extend(data["@graph"])
        else:
            entities.append(data)
    return entities


class TestPrincipleLeadsThePage:
    def test_h1_is_the_principle(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert re.search(r"<h1[^>]*>The Rotten Fencepost Principle</h1>", html)

    def test_title_leads_with_the_principle(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "<title>The Rotten Fencepost Principle" in html

    def test_webpage_schema_names_the_principle(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        entities = _ld_entities(html)
        page = next(e for e in entities if e.get("@type") == "WebPage")
        assert page["name"] == "The Rotten Fencepost Principle"


class TestApprovedJourneyOrder:
    """The five approved sections must appear, in this order, top to
    bottom -- verified by the position of each section's own text in the
    rendered HTML, not by visual layout."""

    def test_sections_present_and_in_order(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        markers = [
            "The Rotten Fencepost Principle",
            "Begin Your Journey",
            "Watch the Foundation Series",
            "Study the Principle",
            "A Personal Invitation from Kahu Phil",
        ]
        positions = [html.index(m) for m in markers]
        assert positions == sorted(positions)


class TestBeginYourJourney:
    def test_presents_find_the_cause_as_primary_resource(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert 'href="/product/prod_find_the_cause_not_the_symptoms"' in html
        assert "Find the Cause, Not the Symptoms" in html
        assert "$9.99" in html

    def test_appears_before_any_checkout_link(self, client):
        # The primary resource is introduced before the visitor is asked
        # to check out for the companion Field Guide.
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert html.index("Begin Your Journey") < html.index("/checkout/rotten_fencepost_field_guide")


class TestWatchTheFoundationSeries:
    def test_video_embed_present(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert 'data-yt-id="GywmvlrxXQ0"' in html

    def test_links_to_campaign_page(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert 'href="/campaign/001"' in html


class TestStudyThePrinciple:
    def test_field_guide_presented_as_companion(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "Rotten Fencepost Field Guide" in html
        assert 'href="/checkout/rotten_fencepost_field_guide"' in html
        assert "$9" in html

    def test_links_to_companion_wellness_article(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert 'href="/wellness/the-rotten-fencepost-principle"' in html

    def test_links_to_evergreen_article(self, client):
        # New for V001-002 -- strengthens discovery of the general-audience
        # evergreen article, which was reachable from /campaign/001 but not
        # previously linked from the hub itself.
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert 'href="/rotten-fencepost/find-the-cause-not-the-symptoms"' in html


class TestPersonalInvitation:
    def test_closes_with_kahu_phils_invitation(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "A Personal Invitation from Kahu Phil" in html
        assert "Find the cause, not the symptoms" in html


class TestContinuingRelationship:
    def test_names_the_promise_of_staying(self, client):
        html = client.get(PATH, base_url=BASE).get_data(as_text=True)
        assert "Keep Riding with the Ranch" in html
        assert "make corrections that hold" in html

    def test_uses_the_existing_owned_youtube_channel(self, client):
        html = client.get(PATH, base_url=BASE).get_data(as_text=True)
        assert 'href="https://www.youtube.com/@keaupuniokeakua?sub_confirmation=1"' in html
        assert "rf_relationship_follow" in html
        assert "No paid membership" in html


class TestNoPlaceholders:
    def test_no_workbook_placeholder(self, client):
        # No standalone Workbook product exists in the catalog -- do not
        # reserve a section for one.
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "Workbook" not in html

    def test_no_generic_future_resources_section(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert "More From the Rotten Fencepost Series" not in html


class TestExistingValuePreserved:
    def test_returns_200(self, client):
        resp = client.get(PATH, base_url=BASE)
        assert resp.status_code == 200

    def test_product_schema_still_present(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        entities = _ld_entities(html)
        product = next((e for e in entities if e.get("@type") == "Product"), None)
        assert product is not None
        assert product["offers"]["price"] == "9.00"

    def test_canonical_tag_unchanged(self, client):
        resp = client.get(PATH, base_url=BASE)
        html = resp.get_data(as_text=True)
        assert f'<link rel="canonical" href="{BASE}{PATH}" />' in html
