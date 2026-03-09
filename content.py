# content.py
# =========================================================
# Handles reading and writing website_content.json
# and digital_products.json.
# Also holds the DEFAULT page content used on first run.
# =========================================================

import json
from datetime import datetime
from config import DATA_FILE, PRODUCTS_FILE, ORDER

# ---------------------------------------------------------
# DEFAULT PAGE CONTENT
# This is used only if website_content.json doesn't exist.
# ---------------------------------------------------------

DEFAULT_PAGES = {
    "funnel_youtube_url": "https://www.youtube.com/embed/O_-J8t0NHLc",
    "order": ORDER,
    "pages": {
        "home": {
            "title": "Ke Aupuni O Ke Akua - The Kingdom of God",
            "hero_image": "/static/images/molokai_coast.jpg",
            "body_md": "## Welcome to Ke Aupuni O Ke Akua\r\n\r\nMahalo for visiting.",
            "product_url": "https://amzn.to/3FfH9ep",
            "gumroad_url": "https://keaupuni.gumroad.com",
        },
        "kingdom_wealth": {
            "title": "Kingdom Wealth",
            "hero_image": "/static/images/scottsdale-mint-ATq9BSFebRE-unsplash.jpg",
            "body_md": "## Biblical Stewardship & Economic Increase",
            "product_url": "",
        },
        "aloha_wellness": {
            "title": "Aloha Wellness - Island Health & Healing",
            "hero_image": "/static/images/ulu_kalo_mango.jpg",
            "body_md": "## Aloha Wellness",
            "product_url": "",
            "gumroad_url": "",
            "direct_buy_url": "/checkout/prod_aloha_wellness",
        },
        "call_to_repentance": {
            "title": "The Call to Repentance - The Kingdom Series",
            "hero_image": "/static/images/sunlight_bursting.jpg",
            "body_md": "## The Call to Repentance",
            "product_url": "https://a.co/d/fgbAVMs",
            "gumroad_url": "https://keaupuni.gumroad.com/l/call-to-repentance",
        },
        "pastor_planners": {
            "title": "Pastor Planners - Tools for Ministry Excellence",
            "hero_image": "/static/images/paniolo_phil.jpg",
            "body_md": "## Organize Your Ministry with Purpose and Prayer",
        },
        "nahenahe_voice": {
            "title": "The Nahenahe Voice of Nahono'opi'ilani - Musical Legacy",
            "hero_image": "/static/images/molokai_ranch.jpg",
            "body_md": "## The Nahenahe Voice - Live from Molokai Ranch Lodge",
            "gallery_images": [
                "/static/images/legacy-album/LeAnne_cover.jpg",
                "/static/images/legacy-album/Phil_ukulele-cover.jpg",
                "/static/images/legacy-album/arena_cover.jpg",
            ],
            "product_links": [
                {"name": "Amazon Music", "url": "https://music.amazon.com/search/nahenahe%20voice", "icon": "🎵"},
                {"name": "Apple Music", "url": "https://music.apple.com/us/search?term=nahenahe%20voice", "icon": "🎵"},
                {"name": "Spotify", "url": "https://open.spotify.com/search/nahenahe%20voice", "icon": "🎵"},
            ],
        },
        "free_booklets": {
            "title": "FREE Booklets",
            "hero_image": "/static/images/taro_field_1.jpg",
            "body_md": "## FREE Kingdom Booklets",
            "products": [
                {"title": "Kingdom Wealth Principles", "download": "/download/booklet1"},
                {"title": "Kingdom Wealth for Couples", "download": "/download/booklet2"},
                {"title": "Kingdom Wellness Principles", "download": "/download/booklet3"},
                {"title": "Kingdom Wellness for Couples", "download": "/download/booklet4"},
                {"title": "Kingdom Living Principles", "download": "/download/booklet5"},
                {"title": "Kingdom Living for Couples", "download": "/download/booklet6"},
            ],
        },
        "kingdom_keys": {
            "title": "FREE Kingdom Keys Booklets",
            "hero_image": "/static/images/taro_field_2.jpg",
            "body_md": "## FREE Kingdom Keys",
            "products": [
                {"title": "7 Scriptures Kingdom Inside You", "download": "/download/pamphlet1"},
                {"title": "Kingdom Healing in 10 Minutes", "download": "/download/pamphlet2"},
                {"title": "5 Kingdom Prayers", "download": "/download/pamphlet3"},
                {"title": "Kingdom Wealth Verses", "download": "/download/pamphlet4"},
            ],
        },
        "partner": {
            "title": "Partner With Us",
            "hero_image": "/static/images/helping_hands.jpg",
            "body_md": "",
        },
    },
}

# ---------------------------------------------------------
# WEBSITE CONTENT HELPERS
# ---------------------------------------------------------

def load_content():
    """Load pages from JSON, create defaults if missing."""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    data = DEFAULT_PAGES.copy()
    save_content(data)
    return data


def save_content(data):
    """Save pages to JSON."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_nav_items(data):
    """Build nav list from page order."""
    pages = data.get("pages", {})
    page_order = data.get("order", ORDER)
    nav = []
    for slug in page_order:
        if slug in pages:
            nav.append({
                "slug": slug,
                "title": pages[slug].get("title", slug.replace("_", " ").title()),
                "url": "/" if slug == "home" else f"/{slug}",
            })
    return nav


# ---------------------------------------------------------
# DIGITAL PRODUCTS HELPERS
# ---------------------------------------------------------

def load_digital_products():
    """Load digital products from JSON."""
    if PRODUCTS_FILE.exists():
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"products": []}


def save_digital_products(products_data):
    """Save digital products to JSON."""
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products_data, f, indent=2, ensure_ascii=False)


def generate_product_id():
    """Generate a unique product ID based on timestamp."""
    return f"prod_{datetime.now().strftime('%Y%m%d%H%M%S')}"


def get_product_by_id(product_id):
    """Find a single product by its ID. Returns None if not found."""
    products_data = load_digital_products()
    return next(
        (p for p in products_data["products"] if p["id"] == product_id), None
    )