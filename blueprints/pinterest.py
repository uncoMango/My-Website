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

from content import CAMPAIGNS
from blueprints.pages import _SEO_PAGES

pinterest_bp = Blueprint("pinterest", __name__)

SITE_URL = "https://keaupuniakeakua.faith"
MEDIA_NS = "http://search.yahoo.com/mrss/"
BUSINESS_NAME = os.environ.get("PINTEREST_BUSINESS_NAME", "Ke Aupuni O Ke Akua Media")
FEED_ENABLED = os.environ.get("PINTEREST_FEED_ENABLED", "true").lower() == "true"

# Board membership is derived from the authoritative content taxonomy, never
# from a second list of item IDs. Adding an article to an existing public
# category automatically places it in the corresponding feed. Products,
# transactional pages, generic pages and duplicate training copies are absent
# by construction because they are not entries in these category projections.
BOARD_RULES = {
    "rotten-fencepost": {
        "name": "Rotten Fencepost",
        "campaigns": True,
        "parents": set(),
    },
    "kingdom-of-god": {
        "name": "Kingdom of God",
        "campaigns": False,
        "parents": {"kingdom"},
    },
    "rotten-fencepost-wellness": {
        "name": "Rotten Fencepost Wellness",
        "campaigns": False,
        "parents": {"wellness"},
    },
    "biblical-stewardship": {
        "name": "Biblical Stewardship",
        "campaigns": False,
        "parents": {"wealth"},
        "title_terms": {"stewardship"},
    },
    "rotten-fencepost-wealth": {
        "name": "Rotten Fencepost Wealth",
        "campaigns": False,
        "parents": {"wealth"},
    },
}
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


def _article_matches(parent: str, page: dict, rule: dict) -> bool:
    if parent in rule["parents"]:
        return True
    terms = rule.get("title_terms", set())
    title = page.get("title", "").lower()
    return bool(terms and any(term in title for term in terms))


def feed_items(board_slug: str = "rotten-fencepost") -> list[dict]:
    rule = BOARD_RULES[board_slug]
    items: list[dict] = []
    if rule["campaigns"]:
        for campaign_id, campaign in sorted(CAMPAIGNS.items()):
            stable_id = f"campaign-{campaign_id}"
            items.append({
                "id": stable_id,
                "title": campaign["title"],
                "description": campaign.get("meta_description") or campaign.get("subtitle") or campaign["title"],
                "path": f"/campaign/{campaign_id}",
                # A campaign thumbnail is production-approved for outward use.
                # A missing thumbnail falls back to the established high-quality
                # fence image rather than repurposing an arbitrary small hero.
                "image": campaign.get("thumbnail_image") or FALLBACK_IMAGE,
                "category": rule["name"],
            })
    for (parent, slug), page in sorted(_SEO_PAGES.items()):
        if not _article_matches(parent, page, rule):
            continue
        stable_id = f"article-{parent}-{slug}"
        items.append({
            "id": stable_id,
            "title": page["title"].split(" | ")[0],
            "description": page.get("meta_description") or page["title"],
            "path": f"/{parent}/{slug}",
            "image": page.get("hero_image") or FALLBACK_IMAGE,
            "category": rule["name"],
        })
    return items


def build_feed(board_slug: str = "rotten-fencepost") -> bytes:
    rule = BOARD_RULES[board_slug]
    ET.register_namespace("media", MEDIA_NS)
    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = f"{BUSINESS_NAME} — {rule['name']}"
    ET.SubElement(channel, "link").text = SITE_URL
    ET.SubElement(channel, "description").text = "Practical teaching and resources for finding causes, inspecting foundations, and making corrections that hold."
    ET.SubElement(channel, "language").text = "en-us"
    ET.SubElement(channel, "lastBuildDate").text = format_datetime(datetime.now(timezone.utc))
    for item in feed_items(board_slug):
        node = ET.SubElement(channel, "item")
        ET.SubElement(node, "title").text = item["title"]
        ET.SubElement(node, "link").text = _tracked(item["path"], item["id"])
        ET.SubElement(node, "guid", {"isPermaLink": "false"}).text = f"kaoa:pinterest:{item['id']}"
        ET.SubElement(node, "description").text = item["description"]
        ET.SubElement(node, "category").text = item["category"]
        ET.SubElement(node, f"{{{MEDIA_NS}}}content", {"url": _absolute(item["image"]), "medium": "image"})
    return ET.tostring(rss, encoding="utf-8", xml_declaration=True)


@pinterest_bp.route("/pinterest-feed.xml")
@pinterest_bp.route("/pinterest-feed/<board_slug>.xml")
def pinterest_feed(board_slug: str = "rotten-fencepost"):
    if not FEED_ENABLED:
        return Response("Pinterest feed disabled", status=404, mimetype="text/plain")
    if board_slug not in BOARD_RULES:
        return Response("Pinterest board feed not found", status=404, mimetype="text/plain")
    response = Response(build_feed(board_slug), mimetype="application/rss+xml")
    response.headers["Cache-Control"] = "public, max-age=900"
    response.headers["X-Robots-Tag"] = "noindex, follow"
    return response
