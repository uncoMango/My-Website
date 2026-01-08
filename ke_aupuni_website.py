# ke_aupuni_finalized_with_image_placeholders.py
# FIXED VERSION - CSS working, products restored

from flask import Flask, request, redirect, render_template_string, abort, url_for, send_file
import json
from pathlib import Path
import markdown
import os

app = Flask(__name__)

ORDER = ["home", "call_to_repentance", "aloha_wellness", "pastor_planners", "nahenahe_voice"]

BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"

DEFAULT_PAGES = {
    "order": ORDER,
    "pages": {
        "home": {
            "title": "Ke Aupuni O Ke Akua - The Kingdom of God",
            "hero_image": "https://i.imgur.com/wmHEyDo.png",
            "body_md": "## Welcome to Ke Aupuni O Ke Akua - The Kingdom of God\r\n\r\nMahalo for visiting. This site is dedicated to rediscovering the revolutionary Kingdom message that Jesus actually preached, which is often missed in modern religious traditions.\r\n\r\n### Our Mission: Kingdom, Not Religion\r\nJesus's central focus was the Kingdom of God—the reign and rule of God breaking into the human experience here and now. Our resources aim to guide you into a deeper understanding of Kingdom principles, citizenship, and authority, moving you from religious performance into authentic, transformative living.\r\n\r\n**Start your journey today by exploring 'The Call to Repentance' series in the navigation.**\r\n\r\n### What Jesus Actually Taught\r\n\r\n**Kingdom Principles Over Religious Rules** - Discover how Jesus consistently chose kingdom living over religious compliance.\r\n\r\n**Repentance as Transformation** - Move beyond feeling sorry for sins to understanding a complete transformation of mind, heart, and lifestyle.\r\n\r\n**Heaven on Earth** - Learn how the Kingdom of God is meant to manifest in our daily lives, relationships, and communities right now.",
            "product_url": "https://amzn.to/3FfH9ep"
        },
        "aloha_wellness": {
            "title": "Aloha Wellness - Island Health & Healing",
            "hero_image": "https://i.imgur.com/xGeWW3Q.jpeg",
            "body_md": "## Aloha Wellness - The Sacred Art of How You Eat\r\n\r\nDiscover the life-changing power of **how** you eat, not just what you eat. This groundbreaking wellness book combines cutting-edge scientific research with ancient Hawaiian mana'o (wisdom) to transform your relationship with food and nourishment.\r\n\r\n### Beyond Diet Culture - A Hawaiian Perspective\r\n\r\nTraditional Hawaiian culture understood something modern society has forgotten: eating is a sacred act that connects us to the land, our ancestors, and our own spiritual well-being. This book bridges that ancient wisdom with contemporary nutritional science.\r\n\r\n### Revolutionary Approach: How, Not What\r\n\r\n**Mindful Consumption** - Learn the scientific basis for how mindful eating practices affect digestion, metabolism, and overall health.\r\n\r\n**Cultural Eating Wisdom** - Discover how Hawaiian ancestors approached meals as community ceremonies, gratitude practices, and spiritual connections.\r\n\r\n**Stress and Digestion** - Research-backed insights into how your emotional state during meals affects nutrient absorption and digestive health.\r\n\r\n**Rhythm and Timing** - Ancient Hawaiian understanding of eating in harmony with natural rhythms, supported by modern chronobiology research.\r\n\r\n**Scientific Research Meets Island Wisdom** - This book offers a comprehensive look at the intersection of modern science and ancient practice.\r\n\r\n### Hawaiian Mana'o (Wisdom Principles)\r\n\r\n**Ho'oponopono with Food** - Making right relationships with nourishment and healing food-related guilt or shame.\r\n\r\n**Aloha 'Āina** - Love of the land extends to gratitude for the food it provides and mindful consumption practices.\r\n\r\n**Lōkahi** - Finding unity and balance in your relationship with food, body, and spirit.\r\n\r\n**Mālama** - Caring for your body as a sacred temple through conscious eating practices.\r\n\r\nTransform your health from the inside out by changing not what you eat, but how you approach the sacred act of nourishment.",
            "product_url": "https://amzn.to/3FfH9ep",
            "products": [
                {
                    "title": "Aloha Wellness Book",
                    "cover": "https://m.media-amazon.com/images/I/712tO3wmGEL._SL1499_.jpg",
                    "amazon": "",
                    "gumroad": ""
                }
            ]
        },
        "call_to_repentance": {
            "title": "The Call to Repentance - The Kingdom Series",
            "hero_image": "https://i.imgur.com/tG1vBp9.jpeg",
            "body_md": "## The Call to Repentance - Rediscovering Jesus's Kingdom Message\r\n\r\nStep beyond religious tradition and rediscover the revolutionary Kingdom message that Jesus actually preached. This transformative book series cuts through centuries of religious interpretation to reveal the pure, life-changing teachings of the Kingdom of God.\r\n\r\n### Series Overview (Volumes 1-5)\r\n\r\nThis isn't a single book but a comprehensive series that systematically unpacks Jesus's kingdom teachings.\r\n\r\n### A Call to Authentic Christianity\r\n\r\nThis series challenges readers to move beyond:\r\n- Religious performance into authentic relationship\r\n- Sunday Christianity into daily kingdom living\r\n- Denominational identity into kingdom citizenship\r\n- Waiting for heaven into experiencing God's kingdom now\r\n\r\n**Join the revolution that Jesus started. Discover the Kingdom message that changes everything.**",
            "product_url": "https://www.amazon.com/CALL-REPENTANCE-Foundation-Application-Lifestyle-ebook/dp/B0FXYDD9SN",
            "products": [
                {
                    "title": "The Call to Repentance - Kingdom Book",
                    "cover": "",
                    "amazon": "",
                    "gumroad": "https://uncomango.gumroad.com/l/myold"
                }
            ]
        },
        "pastor_planners": {
            "title": "Pastor Planners - Tools for Ministry Excellence",
            "hero_image": "https://i.imgur.com/tWnn5UY.png",
            "body_md": "## Organize Your Ministry with Purpose and Prayer\r\n\r\nEffective ministry requires both spiritual sensitivity and practical organization. Our Pastor Planners combine beautiful design with functional tools to help you lead with excellence and peace.\r\n\r\n### Features of Our Ministry Planning System\r\n\r\n**Sermon Planning Sections** - Map out your preaching calendar with space for themes, scriptures, and prayer requests.\r\n\r\n**Prayer and Pastoral Care** - Dedicated sections for tracking prayer requests, hospital visits, counseling sessions, and follow-up care.\r\n\r\n**Meeting and Event Coordination** - Organize board meetings, committee sessions, special events, and outreach activities.\r\n\r\n**Personal Spiritual Disciplines** - Maintain your own spiritual health with guided sections for daily devotions.\r\n\r\n### Why Pastors Love Our Planners\r\n\r\n**Hawaiian-Inspired Design** - Beautiful layouts featuring island imagery and scripture verses.\r\n\r\n**Flexible Formatting** - Works for churches of all sizes and denominations.\r\n\r\n**Durable Construction** - High-quality materials that withstand daily use.\r\n\r\n**Spiritual Focus** - More than just organization - designed to keep your heart centered on God's calling.",
            "product_url": "https://www.amazon.com/s?k=pastor+planner+ministry+organizer",
            "products": [
                {
                    "title": "Hawaiian Pastor Planner - Yearly",
                    "cover": "https://public-files.gumroad.com/p4346cgzkcd4iivhsgkf7pjtypr2",
                    "amazon": "",
                    "gumroad": ""
                },
                {
                    "title": "Hawaiian Pastor Planner - Monthly",
                    "cover": "https://public-files.gumroad.com/ccssij259a3729na9xx5s12skasm",
                    "amazon": "",
                    "gumroad": ""
                },
                {
                    "title": "Samoan Pastor Planner - Yearly",
                    "cover": "https://public-files.gumroad.com/worm4zkkn4hm5k0f81icc4e4pofp",
                    "amazon": "",
                    "gumroad": ""
                },
                {
                    "title": "Samoan Pastor Planner - Monthly",
                    "cover": "https://public-files.gumroad.com/ztbnhmb1azeotsvxga3979n6dw4g",
                    "amazon": "",
                    "gumroad": ""
                }
            ]
        },
        "nahenahe_voice": {
            "title": "The Nahenahe Voice of Nahono'opi'ilani - Musical Legacy",
            "hero_image": "https://i.imgur.com/Vyz6nFJ.png",
            "body_md": "## The Nahenahe Voice of Nahono'opi'ilani - Live from Molokai Ranch Lodge\r\n\r\nExperience the soul-stirring sounds of authentic Hawaiian music captured live at the historic Molokai Ranch Lodge in the year 2000. This intimate recording showcases the true meaning of **nahenahe** - the gentle, soothing voice that carries the spirit of aloha across the islands.\r\n\r\n### A Sacred Musical Journey\r\n\r\nRecorded in the peaceful setting of Molokai Ranch Lodge, this collection features solo guitar and traditional Hawaiian melodies that speak directly to the heart.\r\n\r\n**Nahenahe** means more than just \"soft\" or \"sweet\" - it represents music that heals, soothes, and connects us to the divine presence that flows through all creation.\r\n\r\n### What You'll Experience:\r\n\r\n**Traditional Hawaiian Melodies** - Time-honored songs passed down through generations.\r\n\r\n**Solo Guitar Mastery** - Intimate acoustic performances showcasing Hawaiian slack-key guitar traditions.\r\n\r\n**Authentic Island Atmosphere** - The natural acoustics and peaceful energy of Molokai Ranch Lodge.\r\n\r\n**Healing Through Song** - Each track brings peace, comfort, and the healing power of aloha.\r\n\r\n*\"Music is the language that speaks when words are not enough. The nahenahe voice carries aloha to every heart that listens.\"*\r\n\r\nPerfect for meditation, relaxation, spiritual practice, or any time you need the gentle embrace of island peace.",
            "gallery_images": [
                "/static/covers/cover1.jpg",
                "/static/covers/cover2.jpg",
                "/static/covers/cover3.jpg"
            ],
            "product_links": [
                {
                    "name": "Amazon Music",
                    "url": "https://music.amazon.com/search/nahenahe%20voice",
                    "icon": "🛒"
                },
                {
                    "name": "Apple Music",
                    "url": "https://music.apple.com/us/search?term=nahenahe%20voice",
                    "icon": "🍎"
                },
                {
                    "name": "Spotify",
                    "url": "https://open.spotify.com/search/nahenahe%20voice",
                    "icon": "🎧"
                }
            ]
        }
    }
}

ENHANCED_STYLE = """
:root {
    --primary-bg: #f8f5f0;
    --text-dark: #2c3e50;
    --accent-teal: #5f9ea0;
    --accent-warm: #d4a574;
    --white-transparent: rgba(255, 255, 255, 0.95);
    --shadow-soft: 0 2px 10px rgba(0,0,0,0.1);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'Georgia', 'Times New Roman', serif;
    line-height: 1.6;
    color: var(--text-dark);
    background: var(--primary-bg);
    background-image: 
        radial-gradient(circle at 20% 50%, rgba(175, 216, 248, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(212, 165, 116, 0.1) 0%, transparent 50%);
}

.site-nav {
    background-color: #d4b896;
    background-image: 
        linear-gradient(45deg, #c9a876 25%, transparent 25%),
        linear-gradient(-45deg, #c9a876 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, #bfa068 75%),
        linear-gradient(-45deg, transparent 75%, #bfa068 75%);
    background-size: 16px 16px;
    background-position: 0 0, 0 8px, 8px -8px, -8px 0px;
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: var(--shadow-soft);
}

.nav-container {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
}

.nav-title {
    font-size: 1.5rem;
    font-weight: bold;
    color: #2c3e50;
    text-decoration: none;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
}

.nav-menu {
    display: flex;
    list-style: none;
    gap: 2rem;
}

.nav-menu a {
    text-decoration: none;
    color: var(--text-dark);
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    transition: all 0.3s ease;
}

.nav-menu a:hover {
    background: var(--accent-teal);
    color: white;
}

.hamburger {
    display: none;
    flex-direction: column;
    cursor: pointer;
    padding: 0.5rem;
}

.hamburger span {
    width: 25px;
    height: 3px;
    background: #2c3e50;
    margin: 3px 0;
    transition: 0.3s;
}

.hero {
    height: 100vh;
    min-height: 600px;
    background-size: cover;
    background-position: center;
    position: relative;
    display: flex;
    align-items: flex-end;
}

.hero-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(0deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 50%, rgba(0,0,0,0.1) 100%);
}

.hero-content {
    position: relative;
    z-index: 2;
    color: white;
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
}

.hero h1 {
    font-size: 3rem;
    font-weight: 400;
    text-shadow: 0 2px 8px rgba(0,0,0,0.8);
    margin-bottom: 0.5rem;
    background: rgba(0,0,0,0.3);
    padding: 1rem 2rem;
    border-radius: 8px;
}

.container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    height: 100vh;
    overflow-y: auto;
    z-index: 3;
}

.content-card {
    background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)),
                repeating-linear-gradient(90deg, 
                    rgba(210, 180, 140, 0.3) 0px,
                    rgba(210, 180, 140, 0.3) 2px,
                    rgba(139, 90, 43, 0.2) 2px,
                    rgba(139, 90, 43, 0.2) 4px);
    border: none;
    padding: 3rem 2rem;
    box-shadow: none;
    margin-top: 20vh;
    color: white;
}

.content-card h2 {
    color: white;
    margin-bottom: 1rem;
    font-size: 2.2rem;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.9);
}

.content-card h3 {
    color: white;
    margin: 2rem 0 1rem;
    font-size: 1.6rem;
    text-shadow: 2px 2px 5px rgba(0,0,0,0.8);
}

.content-card p {
    margin-bottom: 1.5rem;
    font-size: 1.1rem;
    color: white;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.7);
    line-height: 1.8;
}

.content-card strong {
    color: white;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
}

.content-card li {
    color: white;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.7);
    line-height: 1.8;
}

.buy-section {
    text-align: center;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(255, 255, 255, 0.3);
}

.buy-button, .music-button {
    display: inline-block;
    background: linear-gradient(135deg, var(--accent-teal), #4a8b8e);
    color: white;
    padding: 1rem 2rem;
    border-radius: 8px;
    text-decoration: none;
    font-weight: bold;
    font-size: 1.1rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(95, 158, 160, 0.3);
    margin: 0.5rem;
}

.buy-button:hover, .music-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(95, 158, 160, 0.4);
}

.music-buttons {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 1rem;
    margin-top: 1.5rem;
}

.gallery-section {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(255, 255, 255, 0.3);
}

.gallery-section h2 {
    color: white;
    text-align: center;
    margin-bottom: 1.5rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.9);
}

.gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.gallery-item {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.gallery-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.7);
}

.gallery-item img {
    width: 100%;
    height: auto;
    display: block;
}

@media (max-width: 768px) {
    .gallery-grid {
        grid-template-columns: 1fr;
    }
}

.footer {
    text-align: center;
    padding: 2rem;
    color: white;
    background: none;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    margin-top: 2rem;
}

@media (max-width: 768px) {
    .hamburger {
        display: flex;
    }
    
    .nav-menu {
        display: none;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background-color: #d4b896;
        background-image: 
            linear-gradient(45deg, #c9a876 25%, transparent 25%),
            linear-gradient(-45deg, #c9a876 25%, transparent 25%),
            linear-gradient(45deg, transparent 75%, #bfa068 75%),
            linear-gradient(-45deg, transparent 75%, #bfa068 75%);
        background-size: 16px 16px;
        background-position: 0 0, 0 8px, 8px -8px, -8px 0px;
        flex-direction: column;
        gap: 0;
        padding: 1rem 0;
        box-shadow: var(--shadow-soft);
    }
    
    .nav-menu.active {
        display: flex;
    }
    
    .nav-menu a {
        padding: 1rem 2rem;
        border-radius: 0;
    }
    
    .nav-container {
        padding: 0 1rem;
    }
    
    .hero {
        height: 45vh;
        min-height: 300px;
    }
    
    .hero h1 {
        font-size: 1.8rem;
        padding: 0.75rem 1.5rem;
    }
    
    .container {
        position: relative;
        height: auto;
        margin-top: 0;
        padding: 0 1rem 2rem;
        transform: none;
        left: 0;
    }
    
    .content-card {
        padding: 2rem 1.5rem;
    }
    
    .content-card h2 {
        font-size: 1.8rem;
    }
    
    .content-card h3 {
        font-size: 1.4rem;
    }
    
    .music-buttons {
        flex-direction: column;
    }
    
    .music-button {
        width: 100%;
    }
}
"""

def md_to_html(md_text):
    return markdown.markdown(md_text, extensions=["extra", "nl2br"])

def load_content():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = DEFAULT_PAGES
            save_content(data)
    else:
        data = DEFAULT_PAGES
        save_content(data)
    return data

def save_content(data):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def render_page(page_id, data):
    pages = data.get("pages", data)
    if page_id not in pages:
        abort(404)
    
    page = pages[page_id]
    
    nav_items = []
    page_order = data.get("order", ORDER)
    for slug in page_order:
        if slug in pages:
            nav_items.append({
                "slug": slug,
                "title": pages[slug].get("title", slug.replace("_", " ").title()),
                "url": f"/{slug}" if slug != "home" else "/"
            })
    
    return render_template_string(PAGE_TEMPLATE, 
        page=page,
        nav_items=nav_items,
        style=ENHANCED_STYLE,
        body_html=md_to_html(page.get("body_md", "")),
        current_page=page_id
    )

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page.title }}</title>
    <style>{{ style|safe }}
    .content-card img {
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        margin: 20px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        display: block;
    }
    
    .content-card img[alt*="Cover"],
    .content-card img[alt*="Volume"] {
        max-width: 300px;
        margin: 20px auto;
    }
    
    @media (max-width: 768px) {
        .content-card img[alt*="Cover"],
        .content-card img[alt*="Volume"] {
            max-width: 100%;
        }
    }

    .content-card div[style*="background: rgba(255,255,255,0.1)"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.5) !important;
    }
</style>
</head>
<body>
    <nav class="site-nav">
        <div class="nav-container">
            <a href="/" class="nav-title">Ke Aupuni O Ke Akua</a>
            <div class="hamburger" onclick="toggleMenu()">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <ul class="nav-menu" id="navMenu">
                {% for item in nav_items %}
                <li><a href="{{ item.url }}">{{ item.title }}</a></li>
                {% endfor %}
            </ul>
        </div>
    </nav>
    
    <header class="hero" style="background-image: url('{{ page.hero_image }}');">
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <h1>{{ page.title }}</h1>
        </div>
    </header>
    
    <main class="container">
        <article class="content-card">
            {{ body_html|safe }}
            
            {% if page.gallery_images %}
            <div class="gallery-section">
                <h2>📸 Album Covers</h2>
                <div class="gallery-grid">
                    {% for image in page.gallery_images %}
                    <div class="gallery-item">
                        <img src="{{ image }}" alt="CD Cover" loading="lazy">
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            {% if page.products %}
            <div style="margin: 3rem 0; padding: 2rem 0; border-top: 2px solid rgba(255,255,255,0.2);">
                <h2 style="color: white; text-align: center; margin-bottom: 2rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.9);">📚 Available Products</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 1.5rem; max-width: 1200px; margin: 0 auto;">
                    {% for product in page.products %}
                    <div style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 1.5rem; backdrop-filter: blur(10px); box-shadow: 0 4px 15px rgba(0,0,0,0.3); transition: transform 0.3s ease;">
                        {% if product.cover %}
                        <img src="{{ product.cover }}" alt="{{ product.title }}" style="width: 100%; height: auto; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
                        {% endif %}
                        <h3 style="color: white; font-size: 1rem; margin-bottom: 1rem; min-height: 2.5rem; text-shadow: 1px 1px 3px rgba(0,0,0,0.7);">{{ product.title }}</h3>
                        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                            {% if product.amazon %}
                            <a href="{{ product.amazon }}" target="_blank" style="display: block; background: linear-gradient(135deg, var(--accent-teal), #4a8b8e); color: white; padding: 0.6rem; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 0.9rem; text-align: center; transition: transform 0.2s;">🛒 Amazon</a>
                            {% endif %}
                            {% if product.gumroad %}
                            <a href="{{ product.gumroad }}" target="_blank" style="display: block; background: linear-gradient(135deg, #FF90E8, #FFA500); color: white; padding: 0.6rem; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 0.9rem; text-align: center; transition: transform 0.2s;">💳 Gumroad</a>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            {% if page.product_links %}
            <div class="buy-section">
                <h2 style="color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.9);">🎵 Stream Our Music</h2>
                <div class="music-buttons">
                    {% for link in page.product_links %}
                    <a href="{{ link.url }}" target="_blank" class="music-button">
                        {{ link.icon }} {{ link.name }}
                    </a>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            {% if page.product_images %}
            <div class="product-gallery" style="margin: 3rem 0;">
                <h2 style="color: white; text-align: center; margin-bottom: 2rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.9);">📚 Available Products</h2>
                <div class="gallery-grid">
                    {% for img in page.product_images %}
                    <div class="gallery-item">
                        <img src="{{ img }}" alt="Product Cover" loading="lazy">
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            {% if page.podcast_embed %}
            <div class="podcast-section" style="margin: 2rem 0; padding: 2rem; background: rgba(0,0,0,0.3); border-radius: 8px;">
                <h2 style="color: white; text-align: center; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.9);">🎙️ Listen to Our Podcast</h2>
                {{ page.podcast_embed|safe }}
            </div>
            {% endif %}
            
            <div class="buy-section">
                {% if page.product_url %}
                <a href="{{ page.product_url }}" target="_blank" class="buy-button">
                    🛒 Buy on Amazon
                </a>
                {% endif %}
                
                {% if page.gumroad_url %}
                <a href="{{ page.gumroad_url }}" target="_blank" class="buy-button" style="background: linear-gradient(135deg, #FF90E8, #FFA500);">
                    💳 Buy on Gumroad
                </a>
                {% endif %}
            </div>
        </article>
    </main>
    
    <footer class="footer">
        <p>© 2025 Ke Aupuni O Ke Akua. All rights reserved. Made with aloha in Hawaiʻi.</p>
    </footer>
    
    <script>
    function toggleMenu() {
        const menu = document.getElementById('navMenu');
        menu.classList.toggle('active');
    }
    
    document.addEventListener('click', function(event) {
        const nav = document.querySelector('.nav-container');
        const menu = document.getElementById('navMenu');
        if (!nav.contains(event.target) && menu.classList.contains('active')) {
            menu.classList.remove('active');
        }
    });
    </script>
</body>
</html>"""

@app.route("/")
def home():
    data = load_content()
    return render_page("home", data)

@app.route("/<page_id>")
def page(page_id):
    data = load_content()
    pages = data.get("pages", data)
    if page_id not in pages:
        abort(404)
    return render_page(page_id, data)

@app.route("/static/covers/<filename>")
def serve_cover(filename):
    cover_path = BASE / filename
    if cover_path.exists():
        return send_file(cover_path, mimetype='image/jpeg')
    abort(404)

@app.route("/kahu")
def admin_panel():
    data = load_content()
    pages = data.get("pages", data)
    
    admin_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 0.5rem;
            font-size: 2rem;
        }
        .subtitle {
            color: #7f8c8d;
            margin-bottom: 2rem;
            font-size: 1rem;
        }
        .page-list {
            display: grid;
            gap: 1.5rem;
        }
        .page-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 12px;
            border: 2px solid #e9ecef;
            transition: all 0.3s ease;
        }
        .page-card:hover {
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        }
        .page-title {
            font-size: 1.25rem;
            color: #2c3e50;
            margin-bottom: 1rem;
            font-weight: 600;
        }
        .page-info {
            display: grid;
            gap: 0.5rem;
            margin-bottom: 1rem;
            font-size: 0.9rem;
            color: #495057;
        }
        .page-info strong {
            color: #2c3e50;
            font-weight: 600;
        }
        .edit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            text-decoration: none;
            display: inline-block;
        }
        .edit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        .back-btn {
            background: #6c757d;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            text-decoration: none;
            display: inline-block;
            margin-top: 2rem;
        }
        .back-btn:hover {
            background: #5a6268;
        }
        .gallery-preview {
            display: flex;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }
        .gallery-preview img {
            width: 60px;
            height: 60px;
            object-fit: cover;
            border-radius: 4px;
            border: 2px solid #dee2e6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌺 Admin Panel</h1>
        <p class="subtitle">Manage website content</p>
        
        <div class="page-list">
"""
    
    for page_id, page_data in pages.items():
        page_title = page_data.get("title", page_id)
        hero_image = page_data.get("hero_image", "")
        product_url = page_data.get("product_url", "N/A")
        gallery_images = page_data.get("gallery_images", [])
        product_links = page_data.get("product_links", [])
        products = page_data.get("products", [])
        
        admin_html += f"""
            <div class="page-card">
                <div class="page-title">{page_title}</div>
                <div class="page-info">
                    <div><strong>Page ID:</strong> {page_id}</div>
                    <div><strong>Hero Image:</strong> {hero_image[:60]}...</div>
"""
        
        if products:
            admin_html += f'                    <div><strong>Products:</strong> {len(products)} items</div>\n'
        
        if product_url != "N/A":
            admin_html += f'                    <div><strong>Product URL:</strong> <a href="{product_url}" target="_blank">View</a></div>\n'
        
        if product_links:
            admin_html += f'                    <div><strong>Music Links:</strong> {len(product_links)} platforms</div>\n'
        
        if gallery_images:
            admin_html += f'                    <div><strong>Gallery:</strong> {len(gallery_images)} images</div>\n'
        
        admin_html += f"""
                </div>
                <a href="/kahu/edit/{page_id}" class="edit-btn">✏️ Edit Page</a>
            </div>
"""
    
    admin_html += """
        </div>
        
        <a href="/" class="back-btn">← Back to Website</a>
    </div>
</body>
</html>"""
    
    return admin_html

@app.route("/kahu/edit/<page_id>", methods=["GET", "POST"])
def edit_page(page_id):
    data = load_content()
    pages = data.get("pages", data)
    
    if page_id not in pages:
        abort(404)
    
    if request.method == "POST":
        pages[page_id]["title"] = request.form.get("title", "")
        pages[page_id]["hero_image"] = request.form.get("hero_image", "")
        pages[page_id]["body_md"] = request.form.get("body_md", "")
        
        product_url = request.form.get("product_url", "").strip()
        if product_url:
            pages[page_id]["product_url"] = product_url
        elif "product_url" in pages[page_id]:
            del pages[page_id]["product_url"]
        
        gumroad_url = request.form.get("gumroad_url", "").strip()
        if gumroad_url:
            pages[page_id]["gumroad_url"] = gumroad_url
        elif "gumroad_url" in pages[page_id]:
            del pages[page_id]["gumroad_url"]
        
        podcast_embed = request.form.get("podcast_embed", "").strip()
        if podcast_embed:
            pages[page_id]["podcast_embed"] = podcast_embed
        elif "podcast_embed" in pages[page_id]:
            del pages[page_id]["podcast_embed"]

        products_text = request.form.get("products_json", "").strip()
        if products_text:
            products = []
            for line in products_text.split("\n"):
                line = line.strip()
                if not line or "|" not in line:
                    continue
                parts = [p.strip() for p in line.split("|")]
                if parts[0]:
                    product = {
                        "title": parts[0],
                        "cover": parts[1] if len(parts) > 1 and parts[1] else "",
                        "amazon": parts[2] if len(parts) > 2 and parts[2] else "",
                        "gumroad": parts[3] if len(parts) > 3 and parts[3] else ""
                    }
                    if product["amazon"] or product["gumroad"]:
                        products.append(product)
            if products:
                pages[page_id]["products"] = products
            elif "products" in pages[page_id]:
                del pages[page_id]["products"]
        elif "products" in pages[page_id]:
            del pages[page_id]["products"]
        
        product_images_raw = request.form.get("product_images", "")
        if product_images_raw:
            pages[page_id]["product_images"] = [line.strip() for line in product_images_raw.split("\n") if line.strip()]
        else:
            pages[page_id]["product_images"] = []
        
        gallery_str = request.form.get("gallery_images", "").strip()
        if gallery_str:
            gallery_images = [img.strip() for img in gallery_str.split("\n") if img.strip()]
            pages[page_id]["gallery_images"] = gallery_images
        elif "gallery_images" in pages[page_id]:
            del pages[page_id]["gallery_images"]
        
        links_str = request.form.get("product_links", "").strip()
        if links_str:
            links = []
            for line in links_str.split("\n"):
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        links.append({
                            "name": parts[0].strip(),
                            "url": parts[1].strip(),
                            "icon": parts[2].strip()
                        })
            if links:
                pages[page_id]["product_links"] = links
        elif "product_links" in pages[page_id]:
            del pages[page_id]["product_links"]
        
        save_content({"pages": pages, "order": data.get("order", ORDER)})
        return redirect("/kahu")
    
    page = pages[page_id]
    gallery_str = "\n".join(page.get("gallery_images", []))
    products_text_lines = []
    if page.get("products"):
        for p in page["products"]:
            line = f"{p.get('title', '')} | {p.get('cover', '')} | {p.get('amazon', '')} | {p.get('gumroad', '')}"
            products_text_lines.append(line)
    products_json = "\n".join(products_text_lines)
    
    product_images_str = ""
    if page.get("product_images"):
        product_images_str = "\n".join(page["product_images"])
    
    links_str = ""
    if "product_links" in page:
        links_str = "\n".join([
            f"{link['name']}|{link['url']}|{link['icon']}"
            for link in page["product_links"]
        ])
    
    edit_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit {page['title']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{ color: #2c3e50; margin-bottom: 0.5rem; }}
        .subtitle {{ color: #7f8c8d; margin-bottom: 2rem; }}
        .form-group {{ margin-bottom: 1.5rem; }}
        label {{
            display: block;
            color: #2c3e50;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        input[type="text"],
        textarea {{
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1rem;
            font-family: inherit;
            transition: border-color 0.3s ease;
        }}
        input[type="text"]:focus,
        textarea:focus {{
            outline: none;
            border-color: #667eea;
        }}
        textarea {{ min-height: 200px; resize: vertical; }}
        .help-text {{ font-size: 0.85rem; color: #6c757d; margin-top: 0.25rem; }}
        .btn-group {{ display: flex; gap: 1rem; margin-top: 2rem; }}
        .btn {{
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-block;
        }}
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }}
        .btn-secondary {{ background: #6c757d; color: white; }}
        .btn-secondary:hover {{ background: #5a6268; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>✏️ Edit Page</h1>
        <p class="subtitle">{page['title']}</p>
        
        <form method="POST">
            <div class="form-group">
                <label for="title">Page Title</label>
                <input type="text" id="title" name="title" value="{page.get('title', '')}" required>
            </div>
            
            <div class="form-group">
                <label for="hero_image">Hero Image URL</label>
                <input type="text" id="hero_image" name="hero_image" value="{page.get('hero_image', '')}" required>
            </div>
            
            <div class="form-group">
                <label for="body_md">Content (Markdown)</label>
                <textarea id="body_md" name="body_md" required>{page.get('body_md', '')}</textarea>
            </div>
            
            <div class="form-group">
                <label for="product_url">Product URL</label>
                <input type="text" id="product_url" name="product_url" value="{page.get('product_url', '')}">
            </div>
            
            <div class="form-group">
                <label for="gumroad_url">Gumroad URL</label>
                <input type="text" id="gumroad_url" name="gumroad_url" value="{page.get('gumroad_url', '')}">
            </div>
            
            <div class="form-group">
                <label for="podcast_embed">Podcast Embed</label>
                <textarea id="podcast_embed" name="podcast_embed" style="min-height: 100px;">{page.get('podcast_embed', '')}</textarea>
            </div>
            
            <div class="form-group">
                <label for="product_images">Product Images (One URL per line)</label>
                <textarea id="product_images" name="product_images" style="min-height: 120px;">{product_images_str}</textarea>
            </div>
            
            <div class="form-group">
                <label for="products_json">Products</label>
                <textarea id="products_json" name="products_json" style="min-height: 180px; font-family: 'Courier New', monospace;">{products_json}</textarea>
                <div class="help-text">Format: Title | Cover URL | Amazon URL | Gumroad URL</div>
            </div>

            <div class="form-group">
                <label for="gallery_images">Gallery Images</label>
                <textarea id="gallery_images" name="gallery_images" style="min-height: 100px;">{gallery_str}</textarea>
            </div>
            
            <div class="form-group">
                <label for="product_links">Music Links</label>
                <textarea id="product_links" name="product_links" style="min-height: 100px;">{links_str}</textarea>
                <div class="help-text">Format: Name|URL|Icon</div>
            </div>
            
            <div class="btn-group">
                <button type="submit" class="btn btn-primary">💾 Save</button>
                <a href="/kahu" class="btn btn-secondary">← Cancel</a>
            </div>
        </form>
    </div>
</body>
</html>"""
    
    return edit_html

if __name__ == "__main__":
    if not DATA_FILE.exists():
        save_content(DEFAULT_PAGES)
    
    port = int(os.environ.get("PORT", 5000))
    print("🌺 Starting...")
    print(f"🌊 Visit: http://localhost:{port}")
    print(f"⚙️  Admin: http://localhost:{port}/kahu")
    app.run(host="0.0.0.0", port=port, debug=True)
