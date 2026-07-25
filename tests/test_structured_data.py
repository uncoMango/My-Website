# tests/test_structured_data.py
# =========================================================
# Work Order 007: guards the JSON-LD structured data implementation.
# =========================================================

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import app as app_module  # noqa: E402
import content  # noqa: E402
import blueprints.payments as payments  # noqa: E402


@pytest.fixture
def client():
    # /checkout/<id> 503s without PayPal credentials configured -- match
    # the pattern used elsewhere in this suite so the checkout noindex
    # test actually exercises the rendered page, not the 503 error page.
    payments.PAYPAL_CLIENT_ID = "fake_id"
    payments.PAYPAL_CLIENT_SECRET = "fake_secret"
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


def _ld_entities(html):
    """Return every JSON-LD entity on a page as a flat list of dicts,
    expanding any @graph into its members."""
    entities = []
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        data = json.loads(block)  # raises if invalid -- that's the point
        if "@graph" in data:
            entities.extend(data["@graph"])
        else:
            entities.append(data)
    return entities


ORG_ID = "https://keaupuniakeakua.faith/#organization"
PERSON_ID = "https://keaupuniakeakua.faith/#person"
WEBSITE_ID = "https://keaupuniakeakua.faith/#website"

STANDARD_PAGES = [
    "/", "/kingdom_wealth", "/aloha_wellness", "/call_to_repentance",
    "/pastor_planners", "/nahenahe_voice", "/free_booklets", "/kingdom_keys",
    "/partner",
]

ARTICLE_PAGES = [
    "/wellness/why-diets-fail", "/wellness/lose-weight-without-dieting",
    "/kingdom/what-is-the-kingdom-of-god", "/wealth/biblical-stewardship-principles",
    "/scripture-tools/hebrew-greek-meaning-tool",
]

TRANSACTIONAL_PAGES = [
    "/checkout/prod_find_the_cause_not_the_symptoms",
    "/thank-you",
    "/rotten-fencepost/success",
]


@pytest.mark.parametrize("path", STANDARD_PAGES + ARTICLE_PAGES + ["/ecosystem", "/products", "/rotten-fencepost"])
def test_every_schema_block_is_valid_json(client, path):
    html = client.get(path).get_data(as_text=True)
    entities = _ld_entities(html)  # json.loads inside will raise on invalid JSON
    assert len(entities) >= 3  # at least Organization + Person + WebSite


@pytest.mark.parametrize("path", STANDARD_PAGES)
def test_standard_pages_get_webpage_schema(client, path):
    html = client.get(path).get_data(as_text=True)
    types = [e.get("@type") for e in _ld_entities(html)]
    assert "WebPage" in types
    assert "Product" not in types
    assert "Article" not in types


@pytest.mark.parametrize("path", ARTICLE_PAGES)
def test_seo_articles_get_article_and_breadcrumb_schema(client, path):
    html = client.get(path).get_data(as_text=True)
    entities = _ld_entities(html)
    types = [e.get("@type") for e in entities]
    assert "Article" in types
    assert "BreadcrumbList" in types
    article = next(e for e in entities if e.get("@type") == "Article")
    assert "headline" in article and article["headline"]
    assert "datePublished" not in article  # no real dates exist -- must never be invented
    assert "dateModified" not in article
    assert article["author"] == {"@id": PERSON_ID}
    assert article["publisher"] == {"@id": ORG_ID}


def test_ecosystem_gets_collectionpage(client):
    html = client.get("/ecosystem").get_data(as_text=True)
    types = [e.get("@type") for e in _ld_entities(html)]
    assert "CollectionPage" in types
    assert "Article" not in types


def test_products_listing_gets_collectionpage_not_product(client):
    html = client.get("/products").get_data(as_text=True)
    types = [e.get("@type") for e in _ld_entities(html)]
    assert "CollectionPage" in types
    assert "Product" not in types  # explicit requirement: no Product schema on the listing page


def test_rotten_fencepost_gets_product_schema(client):
    html = client.get("/rotten-fencepost").get_data(as_text=True)
    entities = _ld_entities(html)
    product = next((e for e in entities if e.get("@type") == "Product"), None)
    assert product is not None
    assert product["offers"]["price"] == "9.00"
    assert product["offers"]["priceCurrency"] == "USD"


@pytest.mark.parametrize("product_id", [
    "prod_aloha_wellness", "prod_kingdom_booklet1", "prod_kingdom_booklet2",
    "prod_find_the_cause_not_the_symptoms", "rotten_fencepost_field_guide", "prod_nahenahe_cd",
])
def test_product_page_price_matches_catalog(client, product_id):
    catalog = {p["id"]: p for p in content.load_digital_products()["products"]}
    expected_price = "%.2f" % float(catalog[product_id].get("price") or 0)
    html = client.get("/product/" + product_id).get_data(as_text=True)
    entities = _ld_entities(html)
    product = next(e for e in entities if e.get("@type") == "Product")
    assert product["offers"]["price"] == expected_price
    assert product["name"] == catalog[product_id]["name"]
    assert product["offers"]["availability"] == "https://schema.org/InStock"
    # nothing fabricated
    assert "aggregateRating" not in product
    assert "review" not in product
    assert "sku" not in product
    assert "gtin" not in product


@pytest.mark.parametrize("tier_id", ["partner_tier1", "partner_tier2", "partner_tier3", "partner_tier4"])
def test_partnership_tiers_get_no_product_schema(client, tier_id):
    """Donation/membership tiers aren't goods for sale -- Product schema
    would misdescribe them."""
    html = client.get("/product/" + tier_id).get_data(as_text=True)
    types = [e.get("@type") for e in _ld_entities(html)]
    assert "Product" not in types
    assert "BreadcrumbList" not in types


@pytest.mark.parametrize("path", TRANSACTIONAL_PAGES)
def test_transactional_pages_have_noindex_and_no_promotional_schema(client, path):
    html = client.get(path).get_data(as_text=True)
    assert 'name="robots" content="noindex, nofollow"' in html
    types = [e.get("@type") for e in _ld_entities(html)]
    assert "Product" not in types
    assert "Article" not in types
    assert "CollectionPage" not in types


@pytest.mark.parametrize("path", STANDARD_PAGES + ARTICLE_PAGES + ["/ecosystem", "/rotten-fencepost"])
def test_shared_entities_have_consistent_ids(client, path):
    """Organization/Person/WebSite must resolve to the same @id everywhere,
    and appear exactly once per page (no duplicates from template
    inheritance)."""
    html = client.get(path).get_data(as_text=True)
    entities = _ld_entities(html)
    orgs = [e for e in entities if e.get("@type") == "Organization"]
    people = [e for e in entities if e.get("@type") == "Person"]
    sites = [e for e in entities if e.get("@type") == "WebSite"]
    assert len(orgs) == 1 and orgs[0]["@id"] == ORG_ID
    assert len(people) == 1 and people[0]["@id"] == PERSON_ID
    assert len(sites) == 1 and sites[0]["@id"] == WEBSITE_ID


@pytest.mark.parametrize("path", ["/", "/product/prod_find_the_cause_not_the_symptoms", "/wellness/why-diets-fail"])
def test_all_urls_in_schema_are_absolute_https(client, path):
    # Flask's test client defaults to http://localhost; force https so this
    # actually exercises the same scheme the live site uses (the deployed
    # site is HTTPS-only -- see canonical link tag), not a local-only quirk.
    html = client.get(path, base_url="https://keaupuniakeakua.faith").get_data(as_text=True)
    entities = _ld_entities(html)

    def check(value):
        if isinstance(value, str) and (value.startswith("/") or value.startswith("http://")):
            pytest.fail("non-absolute or non-https URL in schema: " + value)
        if isinstance(value, dict):
            for v in value.values():
                check(v)
        if isinstance(value, list):
            for v in value:
                check(v)

    for e in entities:
        for k, v in e.items():
            if k in ("url", "item", "image") or k.endswith("Image") or k == "mainEntityOfPage":
                check(v)
