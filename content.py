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
# ---------------------------------------------------------

DEFAULT_PAGES = {
    "funnel_youtube_url": "https://www.youtube.com/embed/O_-J8t0NHLc",
    "order": ORDER,
    "pages": {
        "home": {
            "title": "Ke Aupuni O Ke Akua - The Kingdom of God",
            "hero_image": "/static/images/molokai_coast.jpg",
            "body_md": "## What If Everything You Were Taught About Christianity Was Missing the Most Important Part?\r\n\r\nJesus mentioned the Kingdom of God **53 times**. He mentioned \"church\" **twice**.\r\n\r\nThere's a reason for that - and it changes everything.\r\n\r\n---\r\n\r\nI'm **Kahu Phil Stephens** - a pastor, Paniolo, and 30-year student of Scripture in the original Greek and Hebrew, writing to you from Moloka'i, Hawai'i.\r\n\r\nAfter three decades of study, I made a discovery that turned my faith upside down - in the best way. Jesus didn't come to start a religion. He came to establish a **Kingdom**. And that Kingdom has three dimensions that touch every part of your life.\r\n\r\n---\r\n\r\n### The Three Pillars of Ke Aupuni O Ke Akua\r\n\r\n**The Kingdom of God** - Rediscover what Jesus actually preached. Not church. Not religion. The revolutionary Kingdom message that transforms your mind, your identity, and your purpose.\r\n\r\n**[Explore the Kingdom Series](/call_to_repentance)**\r\n\r\n---\r\n\r\n**Kingdom Wellness** - Your body is not a burden. It is a temple - and the Kingdom has a design for it. Discover how a Paniolo pastor from Moloka'i lost 54 pounds without dieting, through a revelation rooted in Scripture and confirmed by a life on horseback.\r\n\r\n**[Discover Aloha Wellness](/aloha_wellness)**\r\n\r\n---\r\n\r\n**Kingdom Wealth** - The Kingdom operates on stewardship, not ownership. Learn the biblical principles of increase that most churches never teach.\r\n\r\n**[Learn Kingdom Wealth](/kingdom_wealth)**\r\n\r\n---\r\n\r\n### Start Here - FREE\r\n\r\nNot sure where to begin? Start with our **FREE Kingdom Keys** - short, powerful booklets drawn from 30 years of studying Scripture in the original Greek and Hebrew.\r\n\r\n**[Get Your FREE Kingdom Keys](/kingdom_keys)**\r\n\r\n*Aloha. You are in the right place.*",
            "product_url": "https://amzn.to/3FfH9ep",
            "gumroad_url": "https://keaupuni.gumroad.com",
        },
        "kingdom_wealth": {
            "title": "Kingdom Wealth",
            "hero_image": "/static/images/scottsdale-mint-ATq9BSFebRE-unsplash.jpg",
            "body_md": "## Biblical Stewardship & Economic Increase\r\n\r\nThe Kingdom operates on stewardship, not ownership.\r\n\r\n### Core Principles\r\n\r\n**Source vs. Resource** - God is your Source.\r\n\r\n**[FREE Kingdom Keys](/kingdom_keys)**\r\n\r\n**[FREE Kingdom Booklets](/free_booklets)**\r\n\r\n**[Complete Kingdom Series](/call_to_repentance)**\r\n\r\n**[Myron Golden Training](/myron-golden)**",
            "product_url": "",
        },
        "aloha_wellness": {
            "title": "Aloha Wellness - Island Health & Healing",
            "hero_image": "/static/images/ulu_kalo_mango.jpg",
            "body_md": "## Aloha Wellness - The Sacred Art of How You Eat\r\n\r\nDiscover the life-changing power of **how** you eat, not just what you eat.",
            "product_url": "https://a.co/d/6YrcnQp",
            "gumroad_url": "https://keaupuni.gumroad.com/l/aloha-wellness",
            "direct_buy_url": "/checkout/prod_aloha_wellness",
        },
        "call_to_repentance": {
            "title": "The Call to Repentance - The Kingdom Series",
            "hero_image": "/static/images/sunlight_bursting.jpg",
            "body_md": "## The Call to Repentance\r\n\r\nRediscover the revolutionary Kingdom message that Jesus actually preached.",
            "product_url": "https://a.co/d/fgbAVMs",
            "gumroad_url": "https://keaupuni.gumroad.com/l/call-to-repentance",
        },
        "pastor_planners": {
            "title": "Pastor Planners - Tools for Ministry Excellence",
            "hero_image": "/static/images/bible_scroll.jpg",
            "body_md": "## Organize Your Ministry with Purpose and Prayer\r\n\r\n### Available in Multiple Pacific Islander Languages\r\n\r\n**Ke Kauoha La Haku (Hawaiian Edition 2026)**\r\n[Get on Amazon](https://a.co/d/gatnNET) | [Get on Gumroad](https://uncomango.gumroad.com/l/ulrmu)\r\n\r\n**Tusi Fuataiaga a le Faifeau (Samoan Enhanced Edition 2026)**\r\n[Get on Amazon](https://a.co/d/gs0WRPh) | [Get on Gumroad](https://uncomango.gumroad.com/l/ubzevn)",
        },
        "nahenahe_voice": {
            "title": "The Nahenahe Voice of Nahono'opi'ilani - Musical Legacy",
            "hero_image": "/static/images/molokai_ranch.jpg",
            "body_md": "## The Nahenahe Voice - Live from Molokai Ranch Lodge\r\n\r\nExperience the soul-stirring sounds of authentic Hawaiian music captured live at the historic Molokai Ranch Lodge in the year 2000.",
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
            "body_md": "## FREE Kingdom Booklets\r\n\r\nDownload all 6:",
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
            "body_md": "## FREE Kingdom Keys\r\n\r\nAfter 30 years of biblical study.\r\n\r\n**[Browse Complete Kingdom Series](/call_to_repentance)**",
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

def _deep_merge(base, override):
    """Merge override into base. Override wins for scalar values.
    For dicts, recurse. For lists, override wins entirely."""
    result = dict(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result


def load_content():
    """Load pages from the project-directory JSON file. Never writes to disk.
    Falls back to DEFAULT_PAGES if the file is missing or unreadable."""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                disk_data = json.load(f)
            merged_pages = {}
            default_pages = DEFAULT_PAGES.get("pages", {})
            disk_pages = disk_data.get("pages", {})
            for slug, default_page in default_pages.items():
                disk_page = disk_pages.get(slug, {})
                merged_pages[slug] = _deep_merge(default_page, disk_page)
            disk_data["pages"] = merged_pages
            return disk_data
        except Exception:
            pass
    return DEFAULT_PAGES.copy()


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