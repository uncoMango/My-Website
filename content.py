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
    "order": ORDER,
    "pages": {
        "home": {
            "title": "Ke Aupuni O Ke Akua - The Kingdom of God",
            "hero_image": "https://i.imgur.com/wmHEyDo.png",
            "body_md": "## Welcome to Ke Aupuni O Ke Akua - The Kingdom of God\r\n\r\nMahalo for visiting. This site is dedicated to rediscovering the revolutionary Kingdom message that Jesus actually preached, which is often missed in modern religious traditions.\r\n\r\n### Our Mission: Kingdom, Not Religion\r\nJesus's central focus was the Kingdom of God—the reign and rule of God breaking into the human experience here and now. Our resources aim to guide you into a deeper understanding of Kingdom principles, citizenship, and authority, moving you from religious performance into authentic, transformative living.\r\n\r\n**Start your journey today by exploring 'The Call to Repentance' series in the navigation.**\r\n\r\n### What Jesus Actually Taught\r\n\r\n**Kingdom Principles Over Religious Rules** - Discover how Jesus consistently chose kingdom living over religious compliance.\r\n\r\n**Repentance as Transformation** - Move beyond feeling sorry for sins to understanding a complete transformation of mind, heart, and lifestyle.\r\n\r\n**Heaven on Earth** - Learn how the Kingdom of God is meant to manifest in our daily lives, relationships, and communities right now.",
            "product_url": "https://amzn.to/3FfH9ep",
            "gumroad_url": "https://keaupuni.gumroad.com",
        },
        "kingdom_wealth": {
            "title": "Kingdom Wealth",
            "hero_image": "https://i.imgur.com/G2YmSka.jpeg",
            "body_md": "## Biblical Stewardship & Economic Increase\r\n\r\nThe Kingdom operates on stewardship, not ownership.\r\n\r\n### Core Principles\r\n\r\n**Source vs. Resource** - God is your Source.\r\n\r\n**[FREE Kingdom Keys →](/kingdom_keys)**\r\n\r\n**[FREE Kingdom Booklets →](/free_booklets)**\r\n\r\n**[Complete Kingdom Series →](/call_to_repentance)**\r\n\r\n**[Myron Golden Training →](/myron-golden)**",
            "product_url": "",
        },
        "aloha_wellness": {
            "title": "Aloha Wellness - Island Health & Healing",
            "hero_image": "https://i.imgur.com/xGeWW3Q.jpeg",
            "body_md": "## Aloha Wellness - The Sacred Art of How You Eat\r\n\r\nDiscover the life-changing power of **how** you eat, not just what you eat. This groundbreaking wellness book combines cutting-edge scientific research with ancient Hawaiian mana'o (wisdom) to transform your relationship with food and nourishment.\r\n\r\n### Beyond Diet Culture - A Hawaiian Perspective\r\n\r\nTraditional Hawaiian culture understood something modern society has forgotten: eating is a sacred act that connects us to the land, our ancestors, and our own spiritual well-being. This book bridges that ancient wisdom with contemporary nutritional science.\r\n\r\n### Revolutionary Approach: How, Not What\r\n\r\n**Mindful Consumption** - Learn the scientific basis for how mindful eating practices affect digestion, metabolism, and overall health.\r\n\r\n**Cultural Eating Wisdom** - Discover how Hawaiian ancestors approached meals as community ceremonies, gratitude practices, and spiritual connections.\r\n\r\n**Stress and Digestion** - Research-backed insights into how your emotional state during meals affects nutrient absorption and digestive health.\r\n\r\n**Rhythm and Timing** - Ancient Hawaiian understanding of eating in harmony with natural rhythms, supported by modern chronobiology research.\r\n\r\n### Hawaiian Mana'o (Wisdom Principles)\r\n\r\n**Ho'oponopono with Food** - Making right relationships with nourishment and healing food-related guilt or shame.\r\n\r\n**Aloha 'Āina** - Love of the land extends to gratitude for the food it provides and mindful consumption practices.\r\n\r\n**Lōkahi** - Finding unity and balance in your relationship with food, body, and spirit.\r\n\r\n**Mālama** - Caring for your body as a sacred temple through conscious eating practices.\r\n\r\nTransform your health from the inside out by changing not what you eat, but how you approach the sacred act of nourishment.",
            "product_url": "https://a.co/d/6YrcnQp",
            "gumroad_url": "https://keaupuni.gumroad.com/l/aloha-wellness",
            "direct_buy_url": "",
        },
        "call_to_repentance": {
            "title": "The Call to Repentance - The Kingdom Series",
            "hero_image": "https://i.imgur.com/tG1vBp9.jpeg",
            "body_md": "## The Call to Repentance - Rediscovering Jesus's Kingdom Message\r\n\r\nStep beyond religious tradition and rediscover the revolutionary Kingdom message that Jesus actually preached.\r\n\r\n### Volume 1: The Foundation\r\n![Volume 1 Cover](https://via.placeholder.com/300x450/4A90E2/FFFFFF?text=Volume+1)\r\nUnderstanding what the Kingdom of God actually is.\r\n\r\n### Volume 2: Kingdom Citizenship\r\n![Volume 2 Cover](https://via.placeholder.com/300x450/50C878/FFFFFF?text=Volume+2)\r\nWhat it means to be a citizen of God's kingdom.\r\n\r\n### Volume 3: Kingdom Economics\r\n![Volume 3 Cover](https://via.placeholder.com/300x450/FFB347/FFFFFF?text=Volume+3)\r\nHow kingdom principles transform our relationship with money.\r\n\r\n### Volume 4: Kingdom Relationships\r\n![Volume 4 Cover](https://via.placeholder.com/300x450/FF6B6B/FFFFFF?text=Volume+4)\r\nLove, forgiveness, and community the way Jesus intended.\r\n\r\n### Volume 5: Kingdom Authority\r\n![Volume 5 Cover](https://via.placeholder.com/300x450/9B59B6/FFFFFF?text=Volume+5)\r\nWalking in the supernatural power Jesus demonstrated.\r\n\r\n*\"Repent, for the kingdom of heaven has come near.\" - Matthew 4:17*",
            "product_url": "https://a.co/d/fgbAVMs",
            "gumroad_url": "https://keaupuni.gumroad.com/l/call-to-repentance",
        },
        "pastor_planners": {
            "title": "Pastor Planners - Tools for Ministry Excellence",
            "hero_image": "https://i.imgur.com/tWnn5UY.png",
            "body_md": "## Organize Your Ministry with Purpose and Prayer\r\n\r\nEffective ministry requires both spiritual sensitivity and practical organization.\r\n\r\n### Available in Multiple Pacific Islander Languages\r\n\r\n**Ke Kauoha La Haku (Hawaiian Edition 2026)**\r\n📖 [Get on Amazon](https://a.co/d/gatnNET) | 💳 [Get on Gumroad](https://uncomango.gumroad.com/l/ulrmu)\r\n\r\n**Tusi Fuataiaga a le Faifeau (Samoan Enhanced Edition 2026)**\r\n📖 [Get on Amazon](https://a.co/d/gs0WRPh) | 💳 [Get on Gumroad](https://uncomango.gumroad.com/l/ubzevn)",
        },
        "nahenahe_voice": {
            "title": "The Nahenahe Voice of Nahono'opi'ilani - Musical Legacy",
            "hero_image": "https://i.imgur.com/Vyz6nFJ.png",
            "body_md": "## The Nahenahe Voice of Nahono'opi'ilani - Live from Molokai Ranch Lodge\r\n\r\nExperience the soul-stirring sounds of authentic Hawaiian music captured live at the historic Molokai Ranch Lodge in the year 2000.",
            "gallery_images": [
                "/static/covers/cover1.jpg",
                "/static/covers/cover2.jpg",
                "/static/covers/cover3.jpg",
            ],
            "product_links": [
                {"name": "Amazon Music", "url": "https://music.amazon.com/search/nahenahe%20voice", "icon": "🛒"},
                {"name": "Apple Music", "url": "https://music.apple.com/us/search?term=nahenahe%20voice", "icon": "🍎"},
                {"name": "Spotify", "url": "https://open.spotify.com/search/nahenahe%20voice", "icon": "🎧"},
            ],
        },
        "free_booklets": {
            "title": "FREE Booklets",
            "hero_image": "https://i.imgur.com/wmHEyDo.png",
            "body_md": "## 🎁 FREE Kingdom Booklets\r\n\r\nDownload all 6:",
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
            "hero_image": "https://i.imgur.com/wmHEyDo.png",
            "body_md": "## 🌺 FREE Kingdom Keys 🌺\r\n\r\nAfter 30 years of biblical study.\r\n\r\n**[Browse Complete Kingdom Series →](/call_to_repentance)**",
            "products": [
                {"title": "7 Scriptures Kingdom Inside You", "download": "/download/pamphlet1"},
                {"title": "Kingdom Healing in 10 Minutes", "download": "/download/pamphlet2"},
                {"title": "5 Kingdom Prayers", "download": "/download/pamphlet3"},
                {"title": "Kingdom Wealth Verses", "download": "/download/pamphlet4"},
            ],
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
