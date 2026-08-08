# tests/test_content_card_readability.py
# =========================================================
# 2026-08-07: .content-card (the long-form article reading surface used
# by every page.html render except the homepage) used to rely on a
# translucent rgba(0,0,0,0.25) panel with white text, assuming a dark
# hero image was always visible behind it. Real photos broke that
# assumption (busy/light regions killed contrast) and mobile's
# background-attachment:scroll fallback exposed the near-white page
# background directly under white text. Fixed by making the reading
# surface itself opaque and self-sufficient. This is a narrow regression
# guard against reintroducing the transparent-panel pattern -- not a
# substitute for actual visual review.
# =========================================================

import re
from pathlib import Path

STYLES_PATH = Path(__file__).resolve().parent.parent / "templates" / "partials" / "styles.css"

_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")


def _rules_for(css_text, prefix, *, exclude_prefix=None):
    """Every CSS rule whose selector list contains a selector starting
    with `prefix` (e.g. '.content-card'), excluding any selector that
    also starts with `exclude_prefix` (e.g. '.home-content-card', which
    would otherwise also match a plain '.content-card' prefix check).
    Comments are stripped first -- otherwise a /* ... */ block sitting
    between two rules gets swallowed into the following selector by the
    naive [^{}]+ match, since a comment contains neither brace."""
    css_text = _COMMENT_RE.sub("", css_text)
    matched = []
    for selectors, body in _RULE_RE.findall(css_text):
        parts = [s.strip() for s in selectors.split(",")]
        for part in parts:
            if part.startswith(prefix) and (exclude_prefix is None or not part.startswith(exclude_prefix)):
                matched.append(body)
                break
    return matched


def test_content_card_uses_an_opaque_reading_surface():
    css = STYLES_PATH.read_text(encoding="utf-8")
    rules = _rules_for(css, ".content-card", exclude_prefix=".home-content-card")
    joined = " ".join(rules)
    assert "rgba(0,0,0,0.25)" not in joined
    assert "var(--primary-bg)" in joined


def test_content_card_text_is_dark_on_light_not_white_on_transparent():
    css = STYLES_PATH.read_text(encoding="utf-8")
    rules = _rules_for(css, ".content-card", exclude_prefix=".home-content-card")
    joined = " ".join(rules)
    assert "var(--text-dark)" in joined
    assert "color: white" not in joined


def test_home_content_card_is_left_untouched():
    """The homepage's own dark, colorful card styling is a deliberately
    separate class and must not be affected by the article-reading-surface
    fix -- this work order is not a homepage redesign."""
    css = STYLES_PATH.read_text(encoding="utf-8")
    rules = _rules_for(css, ".home-content-card")
    joined = " ".join(rules)
    assert "rgba(0,0,0,0.25)" in joined
    assert "color: white" in joined
