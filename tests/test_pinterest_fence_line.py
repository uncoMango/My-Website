from xml.etree import ElementTree as ET
from pathlib import Path

import pytest
import stripe
from PIL import Image

import app as app_module
from blueprints import payments, pinterest


TOKEN = "a6cc7653b257e2d8051c0683296b3ca9"


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client


def test_verification_tag_is_in_shared_head(client):
    html = client.get("/").get_data(as_text=True)
    assert html.count('name="p:domain_verify"') == 1
    assert f'content="{TOKEN}"' in html
    assert 'rel="canonical"' in html
    assert "googletagmanager.com/gtag/js" in html


def test_feed_is_valid_curated_rss_with_stable_ids_images_and_attribution(client):
    response = client.get("/pinterest-feed.xml")
    assert response.status_code == 200
    assert response.mimetype == "application/rss+xml"
    root = ET.fromstring(response.data)
    items = root.findall("./channel/item")
    assert len(items) == len(pinterest.CAMPAIGNS)
    guids = [item.findtext("guid") for item in items]
    assert len(guids) == len(set(guids))
    for item in items:
        link = item.findtext("link")
        assert link.startswith("https://keaupuniakeakua.faith/")
        assert "utm_source=pinterest" in link
        assert "utm_medium=organic" in link
        assert item.find("{http://search.yahoo.com/mrss/}content").attrib["url"].startswith("http")
        assert item.findtext("description")
    assert not any(any(word in item.findtext("link") for word in ("/admin", "/checkout", "/unsubscribe", "/thank-you")) for item in items)
    assert not any("/product/" in item.findtext("link") for item in items)
    assert all("/campaign/" in item.findtext("link") for item in items)


def test_future_campaign_enters_feed_without_route_changes(monkeypatch):
    monkeypatch.setitem(pinterest.CAMPAIGNS, "999", {
        "title": "Future Teaching", "meta_description": "Useful future teaching.", "hero_image": "/static/images/molokai_coast.jpg",
    })
    assert any(item["id"] == "campaign-999" for item in pinterest.feed_items())


@pytest.mark.parametrize("slug, expected_title", [
    ("rotten-fencepost", "Rotten Fencepost"),
    ("kingdom-of-god", "Kingdom of God"),
    ("rotten-fencepost-wellness", "Rotten Fencepost Wellness"),
    ("biblical-stewardship", "Biblical Stewardship"),
    ("rotten-fencepost-wealth", "Rotten Fencepost Wealth"),
])
def test_each_existing_board_has_a_nonempty_valid_feed(client, slug, expected_title):
    response = client.get(f"/pinterest-feed/{slug}.xml")
    assert response.status_code == 200
    root = ET.fromstring(response.data)
    assert expected_title in root.findtext("./channel/title")
    assert root.findall("./channel/item")


def test_authoritative_category_addition_enters_matching_board(monkeypatch):
    key = ("wellness", "future-authoritative-article")
    monkeypatch.setitem(pinterest._SEO_PAGES, key, {
        "title": "Future Wellness Teaching",
        "meta_description": "A future authoritative teaching.",
        "hero_image": "/static/images/breadfruit.jpg",
    })
    ids = {item["id"] for item in pinterest.feed_items("rotten-fencepost-wellness")}
    assert "article-wellness-future-authoritative-article" in ids


def test_feed_architecture_excludes_duplicate_training_and_products():
    all_items = [
        item
        for board_slug in pinterest.BOARD_RULES
        for item in pinterest.feed_items(board_slug)
    ]
    paths = [item["path"] for item in all_items]
    assert not any(path.startswith("/training-") for path in paths)
    assert not any(path.startswith("/product/") for path in paths)


def test_every_feed_destination_is_indexable_canonical_mobile_and_social_ready(client):
    for board_slug in pinterest.BOARD_RULES:
        for item in pinterest.feed_items(board_slug):
            response = client.get(item["path"] + "?utm_source=pinterest&utm_medium=organic")
            assert response.status_code == 200
            html = response.get_data(as_text=True)
            assert '<meta name="viewport" content="width=device-width, initial-scale=1.0">' in html
            assert "noindex" not in html.lower()
            assert html.count('rel="canonical"') == 1
            assert f'href="https://keaupuniakeakua.faith{item["path"]}"' in html
            assert '<meta name="description" content="' in html
            assert '<meta property="og:title" content="' in html
            assert '<meta property="og:description" content="' in html
            assert '<meta property="og:image" content="' in html
            assert "<a href=" in html


def test_every_feed_image_is_local_and_large_enough_for_outward_use():
    repo_root = Path(__file__).resolve().parents[1]
    for board_slug in pinterest.BOARD_RULES:
        for item in pinterest.feed_items(board_slug):
            assert item["image"].startswith("/static/")
            width, height = Image.open(repo_root / item["image"].lstrip("/")).size
            assert width >= 600
            assert height >= 500


def test_campaign_open_graph_uses_feed_quality_image(client):
    for item in pinterest.feed_items("rotten-fencepost"):
        html = client.get(item["path"]).get_data(as_text=True)
        assert f'<meta property="og:image" content="http://localhost{item["image"]}"' in html


def test_shared_site_exposes_pinterest_without_changing_verification(client):
    html = client.get("/").get_data(as_text=True)
    assert html.count('name="p:domain_verify"') == 1
    assert 'type="application/rss+xml"' in html
    assert 'href="https://keaupuniakeakua.faith/pinterest-feed.xml"' in html
    assert 'href="https://www.pinterest.com/source/keaupuniakeakua.faith/"' in html
    assert "'channel': 'pinterest'" in html


def test_pinterest_query_sets_first_party_attribution_cookie(client):
    response = client.get("/campaign/001?utm_source=pinterest&utm_campaign=pinterest_fence_line&utm_content=campaign-001")
    cookie = "\n".join(response.headers.getlist("Set-Cookie"))
    assert "rf_source=pinterest" in cookie
    assert "rf_campaign=pinterest_fence_line" in cookie
    assert "rf_content=campaign-001" in cookie


def test_stripe_checkout_carries_pinterest_attribution(client, monkeypatch):
    captured = {}

    class FakeSession:
        url = "https://checkout.stripe.test/session"

    def fake_create(**kwargs):
        captured.update(kwargs)
        return FakeSession()

    monkeypatch.setattr(payments, "STRIPE_ENABLED", True)
    monkeypatch.setattr(payments, "STRIPE_SECRET_KEY", "sk_test_local")
    monkeypatch.setattr(stripe.checkout.Session, "create", fake_create)
    client.set_cookie("rf_source", "pinterest")
    client.set_cookie("rf_campaign", "pinterest_fence_line")
    client.set_cookie("rf_content", "product-rotten_fencepost_field_guide")

    response = client.post("/stripe/create-session/rotten_fencepost_field_guide")

    assert response.status_code == 303
    assert captured["metadata"] == {
        "product_id": "rotten_fencepost_field_guide",
        "attribution_source": "pinterest",
        "attribution_campaign": "pinterest_fence_line",
        "attribution_content": "product-rotten_fencepost_field_guide",
    }
