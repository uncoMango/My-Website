# tests/test_shared_layout.py
# =========================================================
# Work Order 004-C: guards against the shared .container/.content-card
# hero/body overlap defect (position:absolute; top:0; height:100vh) ever
# coming back on any of the 26 page.html-driven pages it affected.
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


AFFECTED_PAGES = [
    "/kingdom_wealth",
    "/aloha_wellness",
    "/call_to_repentance",
    "/pastor_planners",
    "/nahenahe_voice",
    "/free_booklets",
    "/kingdom_keys",
    "/ecosystem",
    "/wellness/why-diets-fail",
    "/wellness/lose-weight-without-dieting",
    "/wellness/three-meals-a-day-necessary",
    "/wellness/ancestral-eating-patterns",
    "/wellness/why-modern-health-advice-feels-confusing",
    "/wellness/why-your-body-resists-diets",
    "/wellness/eating-when-hungry",
    "/wellness/the-rotten-fencepost-principle",
    "/wellness/kupuna-wisdom-and-modern-health",
    "/wellness/god-never-told-adam-when-to-eat",
    "/kingdom/what-is-the-kingdom-of-god",
    "/kingdom/jesus-kingdom-message",
    "/kingdom/understanding-scripture-through-original-words",
    "/kingdom/stewardship-in-the-kingdom-of-god",
    "/wealth/biblical-stewardship-principles",
    "/scripture-tools/translation-gap-in-scripture",
    "/scripture-tools/original-language-meaning",
    "/scripture-tools/hebrew-greek-meaning-tool",
]


def test_affected_page_count_matches_audit():
    """Sanity check on this test file itself -- SITE_LAYOUT_AUDIT.md found
    exactly 26 affected pages. If this ever drifts, the parametrized test
    below is silently covering the wrong set."""
    assert len(AFFECTED_PAGES) == 26


@pytest.mark.parametrize("path", AFFECTED_PAGES)
def test_affected_page_returns_200(client, path):
    resp = client.get(path)
    assert resp.status_code == 200


@pytest.mark.parametrize("path", AFFECTED_PAGES)
def test_affected_page_uses_shared_container_class(client, path):
    """Confirms these pages still render through the shared page.html
    container/content-card path (not some page-specific override)."""
    html = client.get(path).get_data(as_text=True)
    assert 'class="container"' in html
    assert 'class="content-card"' in html


def test_container_is_not_absolutely_positioned(client):
    """The actual regression guard: .container must never again be
    position:absolute -- that's the exact mechanism that caused body
    content to render on top of the hero instead of after it."""
    html = client.get("/kingdom_wealth").get_data(as_text=True)
    # isolate the .container rule block from the inlined stylesheet
    start = html.index(".container {")
    end = html.index("}", start)
    rule = html[start:end]
    assert "position: absolute" not in rule
    assert "position:absolute" not in rule


def test_home_layout_classes_untouched(client):
    """Correction 003-A's homepage-specific layout must still exist and
    still be what the homepage actually renders -- Work Order 004-C was
    explicitly told not to modify it."""
    html = client.get("/").get_data(as_text=True)
    assert 'class="home-container"' in html
    assert 'class="home-content-card"' in html
    assert 'class="container"' not in html  # home must not use the shared one


@pytest.mark.parametrize("path", [
    "/rotten-fencepost",
    "/partner",
    "/product/prod_find_the_cause_not_the_symptoms",
    "/products",
])
def test_independent_layout_pages_unaffected(client, path):
    """These templates never used .container/.content-card and must still
    render normally after the shared-layout CSS change."""
    resp = client.get(path)
    assert resp.status_code == 200
