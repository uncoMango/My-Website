# tests/test_canonical_and_internal_links.py
# =========================================================
# Work Order 008: guards canonical tags and the new internal links.
# =========================================================

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import app as app_module  # noqa: E402
import blueprints.payments as payments  # noqa: E402


@pytest.fixture
def client():
    payments.PAYPAL_CLIENT_ID = "fake_id"
    payments.PAYPAL_CLIENT_SECRET = "fake_secret"
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


def _canonicals(html):
    return re.findall(r'<link rel="canonical" href="([^"]+)"\s*/?>', html)


BASE = "https://keaupuniakeakua.faith"

# Pages that extend base.html and therefore inherit the shared canonical tag.
BASE_TEMPLATE_PAGES = [
    "/", "/kingdom_wealth", "/aloha_wellness", "/ecosystem", "/partner",
    "/wellness/why-diets-fail", "/kingdom/what-is-the-kingdom-of-god",
    "/scripture-tools/hebrew-greek-meaning-tool", "/rotten-fencepost",
]

# Standalone templates that WO008 added a canonical to directly.
STANDALONE_CANONICAL_PAGES = [
    ("/aloha-wellness", "/aloha-wellness"),
    ("/kingdom-study", "/kingdom-study"),
    ("/myron-golden", "/myron-golden"),
]


class TestCanonicalTags:
    @pytest.mark.parametrize("path", BASE_TEMPLATE_PAGES)
    def test_base_template_pages_have_single_self_referencing_canonical(self, client, path):
        resp = client.get(path, base_url=BASE)
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        canonicals = _canonicals(html)
        assert len(canonicals) == 1, f"{path} should have exactly one canonical tag, found {canonicals}"
        assert canonicals[0] == BASE + path

    @pytest.mark.parametrize("path,expected_suffix", STANDALONE_CANONICAL_PAGES)
    def test_standalone_pages_have_correct_canonical(self, client, path, expected_suffix):
        resp = client.get(path, base_url=BASE)
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        canonicals = _canonicals(html)
        assert len(canonicals) == 1, f"{path} should have exactly one canonical tag, found {canonicals}"
        assert canonicals[0] == BASE + expected_suffix

    def test_canonical_urls_are_absolute_https(self, client):
        for path, _ in STANDALONE_CANONICAL_PAGES:
            resp = client.get(path, base_url=BASE)
            html = resp.get_data(as_text=True)
            for url in _canonicals(html):
                assert url.startswith("https://keaupuniakeakua.faith")


class TestInternalLinks:
    def test_rotten_fencepost_principle_article_links_to_field_guide(self, client):
        resp = client.get("/wellness/the-rotten-fencepost-principle", base_url=BASE)
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert 'href="/rotten-fencepost"' in html

    def test_field_guide_page_links_back_to_principle_article(self, client):
        resp = client.get("/rotten-fencepost", base_url=BASE)
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert 'href="/wellness/the-rotten-fencepost-principle"' in html

    def test_understanding_scripture_article_links_to_kingdom_study(self, client):
        resp = client.get("/kingdom/understanding-scripture-through-original-words", base_url=BASE)
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert 'href="/kingdom-study"' in html

    def test_scripture_tools_article_links_to_kingdom_study(self, client):
        resp = client.get("/scripture-tools/hebrew-greek-meaning-tool", base_url=BASE)
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert 'href="/kingdom-study"' in html

    @pytest.mark.parametrize("path", [
        "/wellness/the-rotten-fencepost-principle",
        "/rotten-fencepost",
        "/kingdom/understanding-scripture-through-original-words",
        "/scripture-tools/hebrew-greek-meaning-tool",
    ])
    def test_new_link_targets_all_resolve(self, client, path):
        # Sanity: every page carrying a new link must itself load, and every
        # link target introduced by WO008 must resolve with 200, not 404.
        resp = client.get(path, base_url=BASE)
        assert resp.status_code == 200

    @pytest.mark.parametrize("target", [
        "/rotten-fencepost",
        "/wellness/the-rotten-fencepost-principle",
        "/kingdom-study",
    ])
    def test_new_link_targets_return_200(self, client, target):
        resp = client.get(target, base_url=BASE)
        assert resp.status_code == 200
