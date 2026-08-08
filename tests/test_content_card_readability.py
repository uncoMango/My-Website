# tests/test_content_card_readability.py
# =========================================================
# 2026-08-07 (two corrections same day):
#
# 1. .content-card (the long-form article reading surface used by every
#    page.html render except the homepage) relied on a translucent
#    rgba(0,0,0,0.25) panel with white text, assuming a dark hero image
#    was always visible behind it. Real photos broke that assumption.
#    First fix made it fully opaque and LIGHT (var(--primary-bg)) --
#    but that broke visual continuity with the rest of the site's
#    established dark, photo-backed identity (Kahu Phil's own rendered-
#    browser review). Corrected again: .content-card now uses the same
#    dark, white-text, gold-link treatment .home-content-card already
#    uses successfully, just at much higher (near-opaque) alpha so
#    contrast no longer depends on the image behind it.
#
# 2. A persistent, fixed-nav logo rendering at 210px tall on desktop
#    inflated the nav bar enough to collide with the hero title on a
#    long, wrapped title -- fixed by sizing the logo down to a
#    conventional nav scale at every breakpoint, plus a modest secondary
#    bump to .hero's min-height floor.
# =========================================================

import re
from pathlib import Path

STYLES_PATH = Path(__file__).resolve().parent.parent / "templates" / "partials" / "styles.css"

_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")


def _rules_for(css_text, prefix, *, exclude_prefix=None):
    """Every CSS rule whose selector list contains a selector starting
    with `prefix` (e.g. '.content-card'), excluding any selector that
    also starts with `exclude_prefix`."""
    css_text = _COMMENT_RE.sub("", css_text)
    matched = []
    for selectors, body in _RULE_RE.findall(css_text):
        parts = [s.strip() for s in selectors.split(",")]
        for part in parts:
            if part.startswith(prefix) and (exclude_prefix is None or not part.startswith(exclude_prefix)):
                matched.append(body)
                break
    return matched


def test_content_card_is_opaque_not_the_old_translucent_panel():
    css = STYLES_PATH.read_text(encoding="utf-8")
    rules = _rules_for(css, ".content-card", exclude_prefix=".home-content-card")
    joined = " ".join(rules)
    assert "rgba(10,10,10,0.88)" in joined  # near-opaque, not the old 0.25


def test_content_card_matches_established_dark_site_identity():
    """Must use the SAME visual language home-content-card already uses
    successfully (white text, gold links) -- not a separate light theme
    invented for this fix."""
    css = STYLES_PATH.read_text(encoding="utf-8")
    content_card_rules = " ".join(_rules_for(css, ".content-card", exclude_prefix=".home-content-card"))
    home_card_rules = " ".join(_rules_for(css, ".home-content-card"))
    assert "color: white" in content_card_rules
    assert "#FFD700" in content_card_rules
    # Not a near-white/light reading surface.
    assert "--primary-bg" not in content_card_rules
    assert "--text-dark" not in content_card_rules
    # Same color language as the already-proven homepage card.
    assert "color: white" in home_card_rules
    assert "#FFD700" in home_card_rules


def test_home_content_card_background_untouched():
    css = STYLES_PATH.read_text(encoding="utf-8")
    rules = _rules_for(css, ".home-content-card")
    joined = " ".join(rules)
    assert "rgba(0,0,0,0.25)" in joined


class TestNavLogoAndHeroClearance:
    """The reported desktop collision: a 210px persistent nav logo
    inflated the fixed nav's height enough to overlap the hero title."""

    def test_site_logo_is_a_conventional_nav_size_not_210px(self):
        css = STYLES_PATH.read_text(encoding="utf-8")
        rules = _rules_for(css, ".site-logo", exclude_prefix=".site-logo-wrap")
        joined = " ".join(rules)
        assert "210px" not in joined
        assert "height: 72px" in joined

    def test_site_logo_shrinks_further_at_every_smaller_breakpoint(self):
        css = STYLES_PATH.read_text(encoding="utf-8")
        # Extract each breakpoint's .site-logo height in document order and
        # confirm it's monotonically non-increasing as viewport shrinks.
        heights = []
        for match in re.finditer(r"\.site-logo\s*\{[^}]*height:\s*(\d+)px", css):
            heights.append(int(match.group(1)))
        assert len(heights) == 4  # base + 3 breakpoints
        assert heights == sorted(heights, reverse=True)
        assert heights[0] == 72
        assert heights[-1] < heights[0]

    def test_hero_min_height_raised_for_extra_clearance(self):
        css = STYLES_PATH.read_text(encoding="utf-8")
        rules = _rules_for(css, ".hero", exclude_prefix=".hero-")
        joined = " ".join(rules)
        assert "min-height: 760px" in joined
