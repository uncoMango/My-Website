# tests/test_shared_layout.py
# =========================================================
# Work Order 004-C: guards against the shared .container/.content-card
# hero/body overlap defect (position:absolute; top:0; height:100vh) ever
# coming back on any of the 26 page.html-driven pages it affected.
#
# Work Order 004-D: guards the full-page background continuity added after
# 004-C (see the tests near the bottom of this file) to restore the visual
# ambiance the old overlap bug used to produce as a side effect, without
# reintroducing the overlap itself.
# =========================================================

import re
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


# =========================================================
# Work Order 004-D: full-page background continuity.
#
# .container/.content-card being normal-flow (above) removed the overlap,
# but also removed the accidental side effect that made the hero image
# appear to continue behind the whole page. This restores that continuity
# via a CSS variable (--page-hero-bg) set per-page on <body> by page.html,
# and a third background-image layer on body itself. Both are pure
# paint-time effects with no relationship to document position/flow, so
# they can't reintroduce overlap or clipping -- these tests exist to prove
# that, and that nothing outside page.html was affected.
# =========================================================

@pytest.mark.parametrize("path,expected_image", [
    ("/kingdom_wealth", "scottsdale-mint-ATq9BSFebRE-unsplash.jpg"),
    ("/ecosystem", "molokai_coast.jpg"),
    ("/kingdom_keys", "taro_field_2.jpg"),
    ("/", "molokai_coast.jpg"),
])
def test_page_hero_bg_variable_matches_hero_image(client, path, expected_image):
    """The body-level background variable must carry the same image the
    page's own hero uses, so the two visually match at the seam."""
    html = client.get(path).get_data(as_text=True)
    assert f"--page-hero-bg: url('/static/images/{expected_image}')" in html


def test_body_background_rule_layers_the_page_hero_bg_variable(client):
    """Regression guard on the mechanism itself: body's background-image
    must include var(--page-hero-bg, ...) as a real layer, and must not
    reintroduce a fixed body background-color that would visually affect
    the independently-designed templates that rely on the plain default."""
    html = client.get("/kingdom_wealth").get_data(as_text=True)
    start = html.index("body {")
    end = html.index("}", start)
    rule = html[start:end]
    assert "var(--page-hero-bg" in rule
    assert "background-color" not in rule


@pytest.mark.parametrize("path", [
    "/rotten-fencepost",
    "/partner",
    "/product/prod_find_the_cause_not_the_symptoms",
    "/products",
    "/rotten-fencepost/success",
])
def test_independent_templates_body_tag_has_no_page_hero_bg(client, path):
    """The body_attrs block defaults to empty for every template except
    page.html -- these pages' <body> tag must render with no attributes
    at all, exactly as before this change."""
    html = client.get(path).get_data(as_text=True)
    assert re.search(r"<body>", html), f"{path}: <body> tag should have no attributes"
    assert "--page-hero-bg:" not in re.search(r"<body[^>]*>", html).group(0)
