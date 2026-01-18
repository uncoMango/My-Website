# ke_aupuni_website.py - COMPLETE PONO VERSION
# All features | Logo 175px | No fake lauhala | All buttons working

from flask import Flask, request, redirect, render_template_string, abort
import json
from pathlib import Path
import markdown
import os

app = Flask(__name__)

BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"

DEFAULT_PAGES = {
    "order": ["home", "kingdom_wealth", "call_to_repentance", "aloha_wellness", "pastor_planners", "nahenahe_voice"],
    "pages": {
        "home": {
            "title": "Ke Aupuni O Ke Akua - The Kingdom of God",
            "hero_image": "https://i.imgur.com/wmHEyDo.png",
            "body_md": """## Welcome to Ke Aupuni O Ke Akua - The Kingdom of God

Mahalo for visiting. This site is dedicated to rediscovering the revolutionary Kingdom message that Jesus actually preached.

### Our Mission: Kingdom, Not Religion

Jesus's central focus was the Kingdom of God—the reign and rule of God breaking into the human experience here and now.

**Start your journey today by exploring 'The Call to Repentance' series.**

### 🎁 NEW TO KINGDOM THEOLOGY? START HERE!

**FREE Kingdom Keys Booklets** - Bite-sized teachings that will transform your understanding.

**[Download FREE Kingdom Keys →](/kingdom_keys)**

### 💰 Kingdom Wealth & Biblical Prosperity

**[Explore Kingdom Wealth Principles →](/kingdom_wealth)**""",
            "product_url": "https://amzn.to/3FfH9ep"
        },
        "kingdom_wealth": {
            "title": "Kingdom Wealth",
            "hero_image": "https://i.imgur.com/G2YmSka.jpeg",
            "body_md": """## Biblical Stewardship & Economic Increase

The Kingdom of God operates on stewardship, not ownership.

### 📚 Recommended Kingdom Wealth Resources

**[Get the Complete Kingdom Series →](/call_to_repentance)**

### 📖 Learning Biblical Business Principles

After 30 years of biblical study and 8 years in pastoral ministry on Molokaʻi, I'm applying Myron Golden's Kingdom approach to business.

**[Explore Myron Golden's Biblical Business Training →](/myron-golden)**""",
            "product_url": ""
        },
        "call_to_repentance": {
            "title": "The Call to Repentance - The Kingdom Series",
            "hero_image": "https://i.imgur.com/tG1vBp9.jpeg",
            "body_md": """## The Call to Repentance - Rediscovering Jesus's Kingdom Message

Step beyond religious tradition and redisccover the revolutionary Kingdom message.

### 🎁 New to Kingdom Theology?

**[Get Free Kingdom Keys →](/kingdom_keys)**""",
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
        "aloha_wellness": {
            "title": "Aloha Wellness - Island Health & Healing",
            "hero_image": "https://i.imgur.com/xGeWW3Q.jpeg",
            "body_md": """## Aloha Wellness - The Sacred Art of How You Eat

Discover the life-changing power of **how** you eat, not just what you eat.

### 🌺 Body, Soul & Spirit Wellness

**[Discover Kingdom Living Principles →](/kingdom_wealth)**""",
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
        "pastor_planners": {
            "title": "Pastor Planners - Tools for Ministry Excellence",
            "hero_image": "https://i.imgur.com/tWnn5UY.png",
            "body_md": """## Organize Your Ministry with Purpose and Prayer

Effective ministry requires both spiritual sensitivity and practical organization.

### 🎁 FREE Ministry Tools

**[Get Free Kingdom Keys →](/kingdom_keys)**""",
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
            "title": "The Nahenahe Voice of Nahonoʻopiʻilani - Musical Legacy",
            "hero_image": "https://i.imgur.com/Vyz6nFJ.png",
            "body_md": """## The Nahenahe Voice - Live from Molokai Ranch Lodge

Experience the soul-stirring sounds of authentic Hawaiian music captured live at the historic Molokai Ranch Lodge in 2000.

**Nahenahe** means more than just "soft" - it represents music that heals, soothes, and connects us to the divine presence.""",
            "gallery_images": [
                "cover1.jpg",
                "cover2.jpg",
                "cover3.jpg"
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
        },
        "kingdom_keys": {
            "title": "FREE Kingdom Keys Booklets",
            "hero_image": "https://i.imgur.com/wmHEyDo.png",
            "body_md": """## 🌺 FREE Kingdom Keys Booklets 🌺

**Hoʻomau i ke Aupuni o ke Akua** (Continue in the Kingdom of God)

**Aloha!** I'm Pastor Phil Stephens from Molokaʻi. After 30 years of biblical study, I've discovered the Kingdom truths the church forgot.

### 📚 Ready for Deeper Teaching?

**[Browse Complete Kingdom Series →](/call_to_repentance)**

### 💝 Was This Helpful?

If these booklets blessed you, consider sowing back into this Kingdom ministry.""",
            "products": [
                {
                    "title": "7 Scriptures That Prove the Kingdom Is Inside You Now",
                    "cover": "",
                    "amazon": "",
                    "gumroad": ""
                },
                {
                    "title": "How to Release Kingdom Healing in 10 Minutes a Day",
                    "cover": "",
                    "amazon": "",
                    "gumroad": ""
                },
                {
                    "title": "The 5 Kingdom Prayers My Hawaiian Grandma Taught Me",
                    "cover": "",
                    "amazon": "",
                    "gumroad": ""
                },
                {
                    "title": "Kingdom Wealth: 7 Bible Verses the Prosperity Preachers Won't Tell You",
                    "cover": "",
                    "amazon": "",
                    "gumroad": ""
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
}

a {
    color: #87CEEB;
    text-decoration: none;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    transition: color 0.3s ease;
}

a:hover {
    color: #FFD700;
}

a:visited {
    color: #DDA0DD;
}

.site-nav {
    background-color: #d4b896;
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
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.nav-logo {
    height: 175px;
    width: auto;
}

.nav-menu {
    display: flex;
    list-style: none;
    gap: 2rem;
    align-items: center;
}

.nav-menu li a {
    color: #2c3e50;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s ease;
}

.nav-menu li a:hover {
    color: var(--accent-teal);
}

.hamburger {
    display: none;
    flex-direction: column;
    cursor: pointer;
    gap: 4px;
}

.hamburger span {
    width: 25px;
    height: 3px;
    background-color: #2c3e50;
    transition: 0.3s;
}

@media (max-width: 768px) {
    .nav-menu {
        position: fixed;
        left: -100%;
        top: 70px;
        flex-direction: column;
        background-color: #d4b896;
        width: 100%;
        text-align: center;
        transition: 0.3s;
        box-shadow: 0 10px 27px rgba(0,0,0,0.05);
        padding: 2rem 0;
        gap: 1rem;
    }

    .nav-menu.active {
        left: 0;
    }

    .hamburger {
        display: flex;
    }
    
    .nav-logo {
        height: 100px;
    }
}

.hero {
    height: 100vh;
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}

.hero-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(to bottom, rgba(0,0,0,0.2), rgba(0,0,0,0.6));
}

.hero-content {
    position: relative;
    z-index: 1;
    text-align: center;
    color: white;
    padding: 2rem;
    max-width: 900px;
}

.hero h1 {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    line-height: 1.2;
}

@media (max-width: 768px) {
    .hero {
        height: 45vh;
    }
    .hero h1 {
        font-size: 2rem;
    }
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem 4rem;
    position: absolute;
    top: 20vh;
    left: 0;
    right: 0;
    bottom: 0;
    overflow-y: auto;
}

.content-card {
    background: rgba(0, 0, 0, 0.4);
    border-radius: 12px;
    padding: 3rem;
    box-shadow: var(--shadow-soft);
    backdrop-filter: blur(10px);
    margin-top: 20vh;
    color: white;
}

.content-card h2 {
    color: white;
    font-size: 2rem;
    margin: 2rem 0 1rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.9);
}

.content-card h3 {
    color: white;
    font-size: 1.5rem;
    margin: 1.5rem 0 0.75rem;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.7);
}

.content-card p {
    margin-bottom: 1rem;
    line-height: 1.8;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
}

.content-card strong {
    color: white;
    font-weight: 600;
}

.buy-section {
    text-align: center;
    margin: 3rem 0;
    padding: 2rem;
    background: rgba(0,0,0,0.3);
    border-radius: 12px;
}

.buy-button {
    display: inline-block;
    padding: 1rem 2.5rem;
    background: linear-gradient(135deg, var(--accent-teal), #4a8b8e);
    color: white;
    text-decoration: none;
    border-radius: 50px;
    font-weight: bold;
    font-size: 1.1rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(95, 158, 160, 0.3);
    margin: 0.5rem;
}

.buy-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(95, 158, 160, 0.4);
}

.gallery-section {
    margin: 3rem 0;
}

.gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-top: 1.5rem;
}

.gallery-item {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    transition: transform 0.3s ease;
}

.gallery-item:hover {
    transform: scale(1.05);
}

.gallery-item img {
    width: 100%;
    height: auto;
    display: block;
}

.music-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 1.5rem;
}

.music-button {
    display: inline-block;
    padding: 0.875rem 2rem;
    background: linear-gradient(135deg, var(--accent-teal), #4a8b8e);
    color: white;
    text-decoration: none;
    border-radius: 50px;
    font-weight: bold;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(95, 158, 160, 0.3);
}

.music-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(95, 158, 160, 0.4);
}

@media (max-width: 768px) {
    .content-card {
        padding: 2rem 1.5rem;
    }
    
    .gallery-grid {
        grid-template-columns: 1fr;
    }
    
    .music-buttons {
        flex-direction: column;
    }
}
"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page.title }}</title>
    <style>{{ style|safe }}</style>
</head>
<body>
    <nav class="site-nav">
        <div class="nav-container">
            <a href="/" class="nav-title">
                <img src="/static/images/output-onlinepngtools.png" alt="Logo" class="nav-logo">
                Ke Aupuni O Ke Akua
            </a>
            <div class="hamburger" onclick="toggleMenu()">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <ul class="nav-menu" id="navMenu">
                {% for item in nav_items %}
                <li><a href="{{ item.url }}">{{ item.title }}</a></li>
                {% endfor %}
                <li><a href="/kingdom_keys" style="background:#d4af37;color:#fff;padding:0.5rem 1rem;border-radius:6px;">🎁 FREE Booklets</a></li>
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
            <div style="margin: 3rem 0;">
                <h2>📚 Available Products</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 1.5rem;">
                    {% for product in page.products %}
                    <div style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 1.5rem;">
                        {% if product.cover %}
                        <img src="{{ product.cover }}" alt="{{ product.title }}" style="width: 100%; border-radius: 8px; margin-bottom: 1rem;">
                        {% endif %}
                        <h3 style="font-size: 1rem; margin-bottom: 1rem;">{{ product.title }}</h3>
                        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                            {% if product.amazon %}
                            <a href="{{ product.amazon }}" target="_blank" style="background: linear-gradient(135deg, var(--accent-teal), #4a8b8e); color: white; padding: 0.6rem; border-radius: 6px; text-decoration: none; font-weight: bold; text-align: center;">🛒 Amazon</a>
                            {% endif %}
                            {% if product.gumroad %}
                            <a href="{{ product.gumroad }}" target="_blank" style="background: linear-gradient(135deg, #FF90E8, #FFA500); color: white; padding: 0.6rem; border-radius: 6px; text-decoration: none; font-weight: bold; text-align: center;">💳 Gumroad</a>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            {% if page.product_links %}
            <div class="buy-section">
                <h2>🎵 Stream Our Music</h2>
                <div class="music-buttons">
                    {% for link in page.product_links %}
                    <a href="{{ link.url }}" target="_blank" class="music-button">
                        {{ link.icon }} {{ link.name }}
                    </a>
                    {% endfor %}
                </div>
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
    
    <script>
    function toggleMenu() {
        document.getElementById('navMenu').classList.toggle('active');
    }
    </script>
</body>
</html>"""

MYRON_GOLDEN_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transform Your Financial Future | Biblical Business Principles</title>
    <style>{{ style|safe }}
    .email-capture { 
        background: rgba(212, 165, 116, 0.2); 
        padding: 30px; 
        margin: 30px 0; 
        text-align: center; 
        border: 3px solid rgba(212, 165, 116, 0.5); 
        border-radius: 12px;
    }
    .email-form input { width: 100%; padding: 15px; margin: 10px 0; font-size: 16px; border: 2px solid #ddd; border-radius: 6px; }
    .email-form button { width: 100%; padding: 15px; background: #d4af37; color: white; font-size: 18px; font-weight: bold; border: none; cursor: pointer; border-radius: 6px; }
    .section { padding: 40px 0; }
    .product-box { background: rgba(0, 0, 0, 0.5); padding: 30px; margin: 20px 0; border-radius: 12px; }
    .btn { display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, var(--accent-teal), #4a8b8e); color: white; text-decoration: none; font-weight: bold; margin: 10px 5px; border-radius: 8px; }
    </style>
</head>
<body>
    <nav class="site-nav">
        <div class="nav-container">
            <a href="/" class="nav-title">
                <img src="/static/images/output-onlinepngtools.png" alt="Logo" class="nav-logo">
                Ke Aupuni O Ke Akua
            </a>
            <ul class="nav-menu">
                <li><a href="/">Home</a></li>
                <li><a href="/kingdom_wealth">Kingdom Wealth</a></li>
                <li><a href="/call_to_repentance">Kingdom Series</a></li>
            </ul>
        </div>
    </nav>
    
    <header class="hero" style="background-image: url('https://i.imgur.com/G2YmSka.jpeg');">
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <h1>Transform Your Financial Future</h1>
            <p style="font-size: 1.3rem;">Biblical Business Principles That Actually Work</p>
        </div>
    </header>
    
    <main class="container">
        <article class="content-card">
            <div class="email-capture">
                <h2>🌴 Get My FREE Kingdom Business Guide 🌴</h2>
                <div class="email-form">
                    <form action="https://app.kit.com/forms/8979853/subscriptions" method="post">
                        <input type="text" name="fields[first_name]" placeholder="First Name" required>
                        <input type="email" name="email_address" placeholder="Email Address" required>
                        <button type="submit">GET FREE GUIDE →</button>
                    </form>
                </div>
            </div>

            <div class="section">
                <h2>📚 SECTION 1: Start Your Journey</h2>
                <div class="product-box">
                    <div style="text-align: center;">
                        <a href="https://www.trashmantocashman.com/tmcm-book?affiliate_id=4319525" class="btn">GET TRASH MAN TO CASH MAN →</a>
                        <a href="https://www.bossmovesbook.com/bossmoves?affiliate_id=4319525" class="btn">GET BOSS MOVES BOOK →</a>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🧠 SECTION 2: Transform Your Money Blueprint</h2>
                <div class="product-box">
                    <div style="text-align: center;">
                        <a href="https://www.mindovermoneymastery.com/momm?affiliate_id=4319525" class="btn">TRANSFORM YOUR MINDSET →</a>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🎯 SECTION 3: Master the Art of Making Offers</h2>
                <div class="product-box">
                    <h3>Make More Offers Challenge ($97)</h3>
                    <div style="text-align: center;">
                        <a href="https://www.makemoreofferschallenge.com/mmoc?affiliate_id=4319525" class="btn">JOIN THE CHALLENGE →</a>
                    </div>
                </div>
                <div class="product-box">
                    <h3>Offer Mastery Live ($297)</h3>
                    <div style="text-align: center;">
                        <a href="https://www.offermasterylive.com/offer-mastery-livevetfk4nn?affiliate_id=4319525" class="btn">MASTER YOUR OFFERS →</a>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🚀 SECTION 4: Build Your Million-Dollar Infrastructure</h2>
                <div class="product-box">
                    <h3>Golden OPS ($997)</h3>
                    <div style="text-align: center;">
                        <a href="https://www.mygoldenops.com/golden-opsm1y8y7bx?affiliate_id=4319525" class="btn">BUILD YOUR SYSTEM →</a>
                    </div>
                </div>
            </div>
        </article>
    </main>
</body>
</html>"""

def load_content():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        # Merge DEFAULT_PAGES to restore missing fields
        for page_id, default_page in DEFAULT_PAGES["pages"].items():
            if page_id in saved_data["pages"]:
                for key, value in default_page.items():
                    if key not in saved_data["pages"][page_id]:
                        saved_data["pages"][page_id][key] = value
        return saved_data
    return DEFAULT_PAGES

def save_content(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route("/")
def home():
    return redirect("/home")

@app.route("/<page_id>")
def show_page(page_id):
    content = load_content()
    pages = content["pages"]
    
    if page_id not in pages:
        abort(404)
    
    page = pages[page_id]
    body_html = markdown.markdown(page["body_md"], extensions=['extra', 'nl2br'])
    
    nav_items = [
        {"title": pages[pid]["title"], "url": "/" if pid == "home" else f"/{pid}"}
        for pid in content["order"]
    ]
    
    return render_template_string(
        PAGE_TEMPLATE,
        page=page,
        body_html=body_html,
        nav_items=nav_items,
        style=ENHANCED_STYLE
    )

@app.route("/<path:filename>")
def serve_root_file(filename):
    """Serve files from repository root like cover1.jpg"""
    root_path = BASE / filename
    if root_path.exists() and root_path.is_file():
        from flask import send_file
        return send_file(root_path)
    abort(404)

@app.route("/myron-golden")
def myron_golden_page():
    return render_template_string(MYRON_GOLDEN_TEMPLATE, style=ENHANCED_STYLE)

@app.route("/kingdom_keys")
def kingdom_keys():
    return show_page("kingdom_keys")

@app.route("/kahu")
def admin_panel():
    content = load_content()
    pages = content["pages"]
    
    admin_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Content Manager</title>
    <style>
        body { font-family: system-ui; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 16px; padding: 2rem; }
        h1 { color: #2c3e50; margin-bottom: 2rem; }
        .page-card { background: #f8f9fa; padding: 1.5rem; margin: 1rem 0; border-radius: 12px; }
        .edit-btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 0.75rem 1.5rem; border-radius: 8px; text-decoration: none; display: inline-block; font-weight: 600; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏝️ Ke Aupuni Content Manager</h1>
"""
    
    for page_id, page in pages.items():
        admin_html += f"""
        <div class="page-card">
            <h3>{page['title']}</h3>
            <p>URL: /{page_id}</p>
            <a href="/kahu/edit/{page_id}" class="edit-btn">✏️ Edit Page</a>
        </div>
"""
    
    admin_html += """
        <a href="/" style="display:inline-block;margin-top:2rem;padding:0.75rem 1.5rem;background:#6c757d;color:white;border-radius:8px;text-decoration:none;">← Back to Website</a>
    </div>
</body>
</html>"""
    
    return admin_html

@app.route("/kahu/edit/<page_id>", methods=["GET", "POST"])
def edit_page(page_id):
    content = load_content()
    pages = content["pages"]
    
    if page_id not in pages:
        abort(404)
    
    if request.method == "POST":
        # Update basic fields
        pages[page_id]["title"] = request.form.get("title")
        pages[page_id]["hero_image"] = request.form.get("hero_image") or None
        pages[page_id]["body_md"] = request.form.get("body_md")
        pages[page_id]["product_url"] = request.form.get("product_url") or ""
        
        # Products (pipe-separated format)
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
                        "cover": parts[1] if len(parts) > 1 else "",
                        "amazon": parts[2] if len(parts) > 2 else "",
                        "gumroad": parts[3] if len(parts) > 3 else ""
                    }
                    products.append(product)
            if products:
                pages[page_id]["products"] = products
            elif "products" in pages[page_id]:
                del pages[page_id]["products"]
        elif "products" in pages[page_id]:
            del pages[page_id]["products"]
        
        # Gallery images
        gallery_str = request.form.get("gallery_images", "").strip()
        if gallery_str:
            pages[page_id]["gallery_images"] = [img.strip() for img in gallery_str.split("\n") if img.strip()]
        elif "gallery_images" in pages[page_id]:
            del pages[page_id]["gallery_images"]
        
        # Product links (music)
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
        elif "product_links" in pages[page_id]:
            del pages[page_id]["product_links"]
        
        save_content(content)
        return redirect("/kahu")
    
    page = pages[page_id]
    
    # Prepare form data
    gallery_str = "\n".join(page.get("gallery_images", []))
    
    products_text_lines = []
    if page.get("products"):
        for p in page["products"]:
            line = f"{p.get('title', '')} | {p.get('cover', '')} | {p.get('amazon', '')} | {p.get('gumroad', '')}"
            products_text_lines.append(line)
    products_json = "\n".join(products_text_lines)
    
    links_str = ""
    if "product_links" in page:
        links_str = "\n".join([
            f"{link['name']}|{link['url']}|{link['icon']}"
            for link in page["product_links"]
        ])
    
    edit_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Edit {page['title']}</title>
    <style>
        body {{ font-family: system-ui; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 16px; padding: 2rem; }}
        h1 {{ color: #2c3e50; margin-bottom: 2rem; }}
        .form-group {{ margin-bottom: 1.5rem; }}
        label {{ display: block; color: #2c3e50; font-weight: 600; margin-bottom: 0.5rem; }}
        input[type="text"], textarea {{ width: 100%; padding: 0.75rem; border: 2px solid #e9ecef; border-radius: 8px; font-size: 1rem; }}
        textarea {{ min-height: 200px; font-family: monospace; }}
        .btn-group {{ display: flex; gap: 1rem; margin-top: 2rem; }}
        .btn {{ padding: 0.75rem 1.5rem; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-block; }}
        .btn-primary {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; flex: 1; }}
        .btn-secondary {{ background: #6c757d; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>✏️ Edit {page['title']}</h1>
        
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
                <label for="product_url">Product URL (Amazon)</label>
                <input type="text" id="product_url" name="product_url" value="{page.get('product_url', '')}">
            </div>
            
            <div class="form-group">
                <label for="products_json">Products (Title | Cover | Amazon | Gumroad)</label>
                <textarea id="products_json" name="products_json" style="min-height: 150px;">{products_json}</textarea>
            </div>

            <div class="form-group">
                <label for="gallery_images">Gallery Images (One path per line)</label>
                <textarea id="gallery_images" name="gallery_images" style="min-height: 100px;">{gallery_str}</textarea>
            </div>
            
            <div class="form-group">
                <label for="product_links">Music Links (Name|URL|Icon)</label>
                <textarea id="product_links" name="product_links" style="min-height: 100px;">{links_str}</textarea>
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
    print(f"🎁  Kingdom Keys: http://localhost:{port}/kingdom_keys")
    print(f"💰  Myron Golden: http://localhost:{port}/myron-golden")
    app.run(host="0.0.0.0", port=port, debug=False)
