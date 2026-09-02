"""Pinterest RSS fence-line blueprint.

The feed is a read-only projection of the site's existing authoritative
campaign, article and product registries. It never publishes to Pinterest
directly and has no Buffer dependency.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from email.utils import format_datetime
from urllib.parse import urlencode
from xml.etree import ElementTree as ET

from flask import Blueprint, Response

from content import CAMPAIGNS, load_digital_products
from blueprints.pages import _SEO_PAGES

pinterest_bp = Blueprint("pinterest", __name__)

SITE_URL = "https://keaupuniakeakua.faith"
MEDIA_NS = "http://search.yahoo.com/mrss/"
BUSINESS_NAME = os.environ.get("PINTEREST_BUSINESS_NAME", "Ke Aupuni O Ke Akua Media")
FEED_ENABLED = os.environ.get("PINTEREST_FEED_ENABLED", "true").lower() == "true"

# Deliberately small initial public fence line. Future campaigns enter
# automatically from CAMPAIGNS. Articles/products remain explicitly curated so
# admin, thin, duplicate, private and transactional URLs cannot leak into Pins.
ARTICLE_KEYS = [
    ("rotten-fencepost", "find-the-cause-not-the-symptoms"),
    ("rotten-fencepost", "why-do-i-keep-starting-over"),
    ("rotten-fencepost", "the-storm-did-not-rot-the-post"),
    ("training-001", "why-do-i-keep-starting-over"),
]
PRODUCT_IDS = [
    "prod_find_the_cause_not_the_symptoms",
    "rotten_fencepost_field_guide",
    "prod_training_001_complete",
]
FALLBACK_IMAGE = "/static/images/diana-sanders-c24miY2R0FI-unsplash.jpg"


def _absolute(value: str) -> str:
    if value.startswith(("https://", "http://")):
        return value
    return SITE_URL + (value if value.startswith("/") else "/" + value)


def _tracked(path: str, stable_id: str) -> str:
    query = urlencode({
        "utm_source": "pinterest",
        "utm_medium": "organic",
        "utm_campaign": "pinterest_fence_line",
        "utm_content": stable_id,
    })
    return f"{SITE_URL}{path}?{query}"


def feed_items() -> list[dict]:
    items: list[dict] = []
    for campaign_id, campaign in sorted(CAMPAIGNS.items()):
        stable_id = f"campaign-{campaign_id}"
        items.append({
            "id": stable_id,
            "title": campaign["title"],
            "description": campaign.get("meta_description") or campaign.get("subtitle") or campaign["title"],
            "path": f"/campaign/{campaign_id}",
            "image": campaign.get("thumbnail_image") or campaign.get("hero_image") or FALLBACK_IMAGE,
            "category": "Rotten Fencepost Teachings",
        })
    for parent, slug in ARTICLE_KEYS:
        page = _SEO_PAGES.get((parent, slug))
        if not page:
            continue
        stable_id = f"article-{parent}-{slug}"
        items.append({
            "id": stable_id,
            "title": page["title"].split(" | ")[0],
            "description": page.get("meta_description") or page["title"],
            "path": f"/{parent}/{slug}",
            "image": page.get("hero_image") or FALLBACK_IMAGE,
            "category": "Find the Cause, Build on Solid Ground",
        })
    products = {p["id"]: p for p in load_digital_products().get("products", [])}
    for product_id in PRODUCT_IDS:
        product = products.get(product_id)
        if not product or not product.get("active", True):
            continue
        stable_id = f"product-{product_id}"
        items.append({
            "id": stable_id,
            "title": product["name"],
            "description": product.get("description") or product["name"],
            "path": f"/product/{product_id}",
            "image": product.get("cover_image") or FALLBACK_IMAGE,
            "category": "Rotten Fencepost Resources",
        })
    return items


def build_feed() -> bytes:
    ET.register_namespace("media", MEDIA_NS)
    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = f"{BUSINESS_NAME} — Pinterest Fence Line"
    ET.SubElement(channel, "link").text = SITE_URL
    ET.SubElement(channel, "description").text = "Practical teaching and resources for finding causes, inspecting foundations, and making corrections that hold."
    ET.SubElement(channel, "language").text = "en-us"
    ET.SubElement(channel, "lastBuildDate").text = format_datetime(datetime.now(timezone.utc))
    for item in feed_items():
        node = ET.SubElement(channel, "item")
        ET.SubElement(node, "title").text = item["title"]
        ET.SubElement(node, "link").text = _tracked(item["path"], item["id"])
        ET.SubElement(node, "guid", {"isPermaLink": "false"}).text = f"kaoa:pinterest:{item['id']}"
        ET.SubElement(node, "description").text = item["description"]
        ET.SubElement(node, "category").text = item["category"]
        ET.SubElement(node, f"{{{MEDIA_NS}}}content", {"url": _absolute(item["image"]), "medium": "image"})
    return ET.tostring(rss, encoding="utf-8", xml_declaration=True)


@pinterest_bp.route("/pinterest-feed.xml")
def pinterest_feed():
    if not FEED_ENABLED:
        return Response("Pinterest feed disabled", status=404, mimetype="text/plain")
    response = Response(build_feed(), mimetype="application/rss+xml")
    response.headers["Cache-Control"] = "public, max-age=900"
    response.headers["X-Robots-Tag"] = "noindex, follow"
    return response
