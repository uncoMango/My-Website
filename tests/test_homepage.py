# tests/test_homepage.py
# =========================================================
# Focused tests for the homepage "front door" welcome section
# added to improve the first-time-visitor experience.
# =========================================================

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import app as app_module  # noqa: E402


@pytest.fixture
def client():
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


def test_homepage_returns_200(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_homepage_contains_welcome_heading(client):
    html = client.get("/").get_data(as_text=True)
    assert "Aloha. You are in the right place." in html


def test_homepage_contains_where_to_begin_prompt(client):
    html = client.get("/").get_data(as_text=True)
    assert "Where would you like to begin?" in html


@pytest.mark.parametrize("title,href", [
    ("Understand the Kingdom", "/call_to_repentance"),
    ("Strengthen Your Health", "/aloha_wellness"),
    ("Practice Faithful Stewardship", "/kingdom_wealth"),
    ("Start With Something Free", "/kingdom_keys"),
])
def test_homepage_choice_card_present_with_correct_link(client, title, href):
    html = client.get("/").get_data(as_text=True)
    assert title in html
    assert f'href="{href}"' in html


@pytest.mark.parametrize("href", [
    "/call_to_repentance",
    "/aloha_wellness",
    "/kingdom_wealth",
    "/kingdom_keys",
])
def test_homepage_choice_link_target_resolves(client, href):
    """Every link in the new welcome section must point to a real, working page."""
    resp = client.get(href)
    assert resp.status_code == 200


def test_homepage_welcome_heading_appears_before_existing_bands(client):
    """The new welcome section must appear before the pre-existing
    Kingdom Study Tools / Ecosystem promo bands, not after."""
    html = client.get("/").get_data(as_text=True)
    welcome_pos = html.find("Aloha. You are in the right place.")
    study_tools_pos = html.find("Kingdom Study Tools")
    ecosystem_pos = html.find("The Ke Aupuni O Ke Akua Ecosystem")
    assert welcome_pos != -1
    assert study_tools_pos != -1
    assert ecosystem_pos != -1
    assert welcome_pos < study_tools_pos < ecosystem_pos


def test_homepage_welcome_heading_appears_before_founding_reader_offer(client):
    html = client.get("/").get_data(as_text=True)
    welcome_pos = html.find("Aloha. You are in the right place.")
    offer_pos = html.find("Founding Reader Offer")
    assert welcome_pos != -1
    assert offer_pos != -1
    assert welcome_pos < offer_pos


def test_homepage_still_has_founding_reader_offer(client):
    """The existing founding-reader offer must still work, just lower on the page."""
    html = client.get("/").get_data(as_text=True)
    assert "Founding Reader Offer" in html
    assert 'href="/aloha_wellness"' in html


def test_homepage_still_has_free_health_guide_form(client):
    """The existing free health-guide email capture must still work."""
    html = client.get("/").get_data(as_text=True)
    assert 'action="/download/aloha_wellness_freebie"' in html
    assert "Get the FREE Kingdom Health Guide" in html


def test_homepage_still_has_three_pillars_content(client):
    """Existing longer personal story / three pillars content must not be deleted."""
    html = client.get("/").get_data(as_text=True)
    assert "The Three Pillars of Ke Aupuni O Ke Akua" in html
    assert "Kingdom Wellness" in html
    assert "Kingdom Wealth" in html


def test_homepage_does_not_duplicate_closing_aloha_line(client):
    """The old trailing 'Aloha. You are in the right place.' line was moved to
    the top, not duplicated — it should appear exactly once on the page."""
    html = client.get("/").get_data(as_text=True)
    assert html.count("Aloha. You are in the right place.") == 1


@pytest.mark.parametrize("path", [
    "/",
    "/kingdom_wealth",
    "/free_booklets",
    "/kingdom_keys",
    "/call_to_repentance",
    "/aloha_wellness",
    "/pastor_planners",
    "/nahenahe_voice",
    "/partner",
    "/ecosystem",
    "/kingdom-study",
    "/product/prod_aloha_wellness",
])
def test_other_public_pages_unaffected(client, path):
    resp = client.get(path)
    assert resp.status_code == 200


def test_kahu_still_requires_login(client):
    """Homepage changes must not have touched admin auth."""
    resp = client.get("/kahu")
    assert resp.status_code in (302, 401, 403)
