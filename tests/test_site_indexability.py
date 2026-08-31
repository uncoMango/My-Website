"""Whole-site guards for public indexing signals and internal discovery."""

import json
import re
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import urlparse

import pytest

import app as app_module
import blueprints.payments as payments
import blueprints.pages as pages_module
import content


BASE = "https://keaupuniakeakua.faith"
AFFECTED_PATHS = [
    "/myron-golden",
    "/wellness/ancestral-eating-patterns",
    "/aloha-wellness",
    "/kingdom/stewardship-in-the-kingdom-of-god",
    "/kingdom/understanding-scripture-through-original-words",
    "/wellness/kupuna-wisdom-and-modern-health",
    "/wellness/the-rotten-fencepost-principle",
    "/wellness/eating-when-hungry",
    "/wealth/biblical-stewardship-principles",
    "/wellness/why-diets-fail",
    "/wellness/lose-weight-without-dieting",
]

# These product routes exist for checkout plumbing or intentionally consolidate
# onto a stronger public page.  Every other active, non-partnership product is
# independently indexable and therefore must be represented in the sitemap.
INTENTIONALLY_NON_INDEXABLE_PRODUCTS = {
    "rotten_fencepost_field_guide",
    "partner_tier1",
    "partner_tier2",
    "partner_tier3",
    "partner_tier4",
}

# Public indexable routes that are not data-driven through DEFAULT_PAGES,
# _SEO_PAGES, CAMPAIGNS, or the product catalog.
INDEXABLE_BESPOKE_PATHS = {
    "/aloha-wellness",
    "/ecosystem",
    "/kingdom-study",
    "/myron-golden",
    "/partner",
    "/products",
    "/rotten-fencepost",
    "/wellness",
    "/kingdom",
    "/wealth",
    "/scripture-tools",
}


class IndexingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()
        self.canonicals = []
        self.descriptions = []
        self.robots = []
        self.h1_count = 0
        self.title_text = []
        self.schema_text = []
        self._in_title = False
        self._schema = None

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "a" and values.get("href"):
            self.links.add(values["href"])
        if tag == "link" and "canonical" in values.get("rel", "").split():
            self.canonicals.append(values.get("href"))
        if tag == "meta" and values.get("name", "").lower() == "description":
            self.descriptions.append(values.get("content", ""))
        if tag == "meta" and values.get("name", "").lower() == "robots":
            self.robots.append(values.get("content", ""))
        if tag == "h1":
            self.h1_count += 1
        if tag == "title":
            self._in_title = True
        if tag == "script" and values.get("type") == "application/ld+json":
            self._schema = []

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._schema is not None:
            self.schema_text.append("".join(self._schema))
            self._schema = None

    def handle_data(self, value):
        if self._in_title:
            self.title_text.append(value)
        if self._schema is not None:
            self._schema.append(value)


@pytest.fixture
def client():
    payments.PAYPAL_CLIENT_ID = "fake_id"
    payments.PAYPAL_CLIENT_SECRET = "fake_secret"
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as test_client:
        yield test_client


def sitemap_paths(client):
    xml = client.get("/sitemap.xml", base_url=BASE).get_data(as_text=True)
    return [urlparse(url).path for url in re.findall(r"<loc>(.*?)</loc>", xml)]


def parse_response(response):
    parser = IndexingParser()
    parser.feed(response.get_data(as_text=True))
    return parser


def expected_indexable_paths():
    """Build the public indexing universe from the route-owning registries.

    This deliberately does not copy the sitemap list.  A new real page,
    article, campaign, or active product therefore fails the audit until its
    public indexing decision is made explicitly.
    """
    paths = set(INDEXABLE_BESPOKE_PATHS)
    for page_id in content.DEFAULT_PAGES["pages"]:
        paths.add("/" if page_id == "home" else f"/{page_id}")
    paths.update(f"/{parent}/{slug}" for parent, slug in pages_module._SEO_PAGES)
    paths.update(f"/campaign/{campaign_id}" for campaign_id in content.CAMPAIGNS)
    for product in content.load_digital_products().get("products", []):
        if product.get("active", True) and product["id"] not in INTENTIONALLY_NON_INDEXABLE_PRODUCTS:
            paths.add(f"/product/{product['id']}")
    return paths


def test_sitemap_exactly_matches_public_indexing_universe(client):
    actual = set(sitemap_paths(client))
    expected = expected_indexable_paths()
    assert actual == expected, (
        f"missing from sitemap: {sorted(expected - actual)}; "
        f"unexpected in sitemap: {sorted(actual - expected)}"
    )


def test_affected_urls_are_all_in_sitemap_once(client):
    paths = sitemap_paths(client)
    for path in AFFECTED_PATHS:
        assert paths.count(path) == 1, f"{path} must appear exactly once in sitemap.xml"


@pytest.mark.parametrize("path", AFFECTED_PATHS + ["/wellness", "/kingdom", "/wealth", "/scripture-tools"])
def test_priority_pages_have_complete_indexing_signals(client, path):
    response = client.get(path, base_url=BASE)
    parser = parse_response(response)
    assert response.status_code == 200
    assert parser.canonicals == [BASE + path]
    assert len(parser.descriptions) == 1 and parser.descriptions[0].strip()
    assert " ".join(parser.title_text).strip()
    assert parser.h1_count == 1
    assert not any("noindex" in value.lower() for value in parser.robots)


def test_every_sitemap_page_has_unique_canonical_and_valid_metadata(client):
    canonical_owners = {}
    titles = Counter()
    for path in sitemap_paths(client):
        response = client.get(path, base_url=BASE)
        parser = parse_response(response)
        title = " ".join(parser.title_text).strip()
        assert response.status_code == 200, path
        assert parser.canonicals == [BASE + path], path
        assert parser.canonicals[0] not in canonical_owners, path
        canonical_owners[parser.canonicals[0]] = path
        assert len(parser.descriptions) == 1 and parser.descriptions[0].strip(), path
        assert title, path
        assert parser.h1_count == 1, path
        assert not any("noindex" in value.lower() for value in parser.robots), path
        titles[title] += 1
        for schema in parser.schema_text:
            json.loads(schema)
    assert not [title for title, count in titles.items() if count > 1]


def test_every_sitemap_page_is_publicly_discoverable_and_links_are_sound(client):
    paths = sitemap_paths(client)
    public_paths = set(paths)
    inbound = Counter()
    broken = []
    for source in paths:
        parser = parse_response(client.get(source, base_url=BASE))
        for href in parser.links:
            parsed = urlparse(href)
            if href.startswith("/"):
                target = parsed.path
            elif parsed.netloc == "keaupuniakeakua.faith":
                target = parsed.path
            else:
                continue
            if target in public_paths and target != source:
                inbound[target] += 1
            if target in public_paths:
                status = client.get(target, base_url=BASE).status_code
                if status >= 400:
                    broken.append((source, target, status))
    assert not broken
    assert not [path for path in paths if path != "/" and inbound[path] == 0]


def _schema_urls(value):
    if isinstance(value, dict):
        for child in value.values():
            yield from _schema_urls(child)
    elif isinstance(value, list):
        for child in value:
            yield from _schema_urls(child)
    elif isinstance(value, str) and value.startswith(BASE):
        yield value


def test_all_internal_schema_urls_resolve(client):
    checked = set()
    for source in sitemap_paths(client):
        parser = parse_response(client.get(source, base_url=BASE))
        for schema_text in parser.schema_text:
            for url in _schema_urls(json.loads(schema_text)):
                path = urlparse(url).path or "/"
                if path in checked:
                    continue
                checked.add(path)
                response = client.get(path, base_url=BASE)
                assert response.status_code == 200, f"{source} schema points to broken {url}"


@pytest.mark.parametrize("path", ["/wellness", "/kingdom", "/wealth", "/scripture-tools"])
def test_category_hubs_emit_collection_and_breadcrumb_schema(client, path):
    parser = parse_response(client.get(path, base_url=BASE))
    schemas = [json.loads(value) for value in parser.schema_text]
    schema_types = {schema.get("@type") for schema in schemas if isinstance(schema, dict)}
    assert {"CollectionPage", "BreadcrumbList"}.issubset(schema_types)
