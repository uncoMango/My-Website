import os
from flask import Flask, request, redirect, render_template_string, abort, url_for
import json
from pathlib import Path
import markdown

app = Flask(__name__)

# Page order for navigation - Updated with Kingdom Wealth
ORDER = ["home", "kingdom_wealth", "aloha_wellness", "call_to_repentance", "pastor_planners", "nahenahe_voice"]

# Data storage
BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"

# Complete default content with Kingdom Wealth added
DEFAULT_PAGES = {
    "home": {
        "title": "Ke Aupuni O Ke Akua - The Kingdom of God",
        "hero_image": "https://i.imgur.com/wmHEyDo.png",
        "body_md": """## Aloha and Welcome to Our Sacred Space\n\nWelcome to **Ke Aupuni O Ke Akua** (The Kingdom of God), a peaceful digital sanctuary where Hawaiian wisdom meets spiritual growth.""",
        "product_url": ""
    },
    "kingdom_wealth": {
        "title": "Kingdom Wealth & Stewardship",
        "hero_image": "https://i.imgur.com/wmHEyDo.png",
        "body_md": """## Funding the 20-Volume Mandate\n\nTo release the full weight of the Kingdom message, an Ambassador must master stewardship. I have aligned with **Myron Golden** and the "Make More Offers Challenge" to provide the financial foundation for our mission.""",
        "product_url": "https://www.makemoreofferschallenge.com/join?am_id=uncomango777"
    },
    "aloha_wellness": {
        "title": "Aloha Wellness - Island Health & Healing",
        "hero_image": "https://images.unsplash.com/photo-1600298881974-6be191ceeda1?auto=format&fit=crop&w=1200&q=80",
        "body_md": """## Traditional Hawaiian Wellness Practices\n\nDiscover the ancient Hawaiian approach to health and wellness that harmonizes mind, body, and spirit.""",
        "product_url": "https://www.amazon.com/s?k=hawaiian+wellness+books"
    },
    "call_to_repentance": {
        "title": "The Call to Repentance",
        "hero_image": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?auto=format&fit=crop&w=1200&q=80",
        "body_md": """## Embracing True Repentance for Spiritual Growth\n\nRepentance is a complete transformation of heart and mind.""",
        "product_url": ""
    },
    "pastor_planners": {
        "title": "Pastor Planners",
        "hero_image": "https://images.unsplash.com/photo-1583212292454-1fe6229603b7?auto=format&fit=crop&w=1200&q=80",
        "body_md": """## Organize Your Ministry with Purpose and Prayer\n\nEffective ministry requires both spiritual sensitivity and practical organization.""",
        "product_url": ""
    },
    "nahenahe_voice": {
        "title": "The Nahenahe Voice",
        "hero_image": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=1200&q=80",
        "body_md": """## Preserving the Gentle Voice of Hawaiian Music\n\n**Nahenahe** means soft, sweet, melodious.""",
        "product_url": ""
    }
}ENHANCED_STYLE = """
:root {
    --primary-bg: #f8f5f0;
    --text-dark: #2c3e50;
    --accent-teal: #5f9ea0;
    --accent-warm: #d4a574;
    --white-transparent: rgba(255, 255, 255, 0.95);
}
body {
    font-family: 'Georgia', serif;
    line-height: 1.6;
    color: var(--text-dark);
    background: var(--primary-bg);
    background-image: url('https://i.imgur.com/wmHEyDo.png');
    background-attachment: fixed;
    background-size: cover;
}
.site-nav {
    background: var(--white-transparent);
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
.nav-container {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
}
.nav-menu { display: flex; list-style: none; gap: 2rem; }
.nav-menu a { text-decoration: none; color: var(--text-dark); font-weight: bold; padding: 0.5rem 1rem; border-radius: 6px; }
.nav-menu a:hover { background: var(--accent-teal); color: white; }
.hero {
    height: 60vh;
    background-size: cover;
    background-position: center;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
}
.hero-overlay {
    position: absolute;
    inset: 0;
    background: rgba(0,0,0,0.4);
}
.hero h1 { position: relative; z-index: 2; font-size: 3rem; text-shadow: 2px 2px 8px rgba(0,0,0,0.8); }
.container { max-width: 1000px; margin: 0 auto; padding: 2rem; }
.content-card {
    background: var(--white-transparent);
    padding: 3rem;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    margin-top: -100px;
    position: relative;
    z-index: 5;
    border: 1px solid var(--accent-warm);
}
.buy-button {
    display: inline-block;
    background: var(--accent-teal);
    color: white;
    padding: 1rem 2rem;
    border-radius: 8px;
    text-decoration: none;
    font-weight: bold;
    margin-top: 2rem;
}
/* Admin Panel Styles */
.admin-panel { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.form-group { margin-bottom: 1.5rem; }
.form-control { width: 100%; padding: 0.8rem; border: 1px solid #ccc; border-radius: 4px; }
"""
def md_to_html(md_text):
    return markdown.markdown(md_text, extensions=["extra", "nl2br"])

def load_content():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"order": ORDER, "pages": DEFAULT_PAGES}

def save_content(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

PAGE_TEMPLATE = """<!DOCTYPE html><html><head><style>{{ style }}</style></head>
<body>
    <nav class="site-nav"><div class="nav-container">
        <a href="/" class="nav-title">Ke Aupuni O Ke Akua</a>
        <ul class="nav-menu">
            {% for item in nav_items %}<li><a href="{{ item.url }}">{{ item.title }}</a></li>{% endfor %}
            <li><a href="/admin">Admin</a></li>
        </ul>
    </div></nav>
    <header class="hero" style="background-image: url('{{ page.hero_image }}');">
        <div class="hero-overlay"></div><h1>{{ page.title }}</h1>
    </header>
    <main class="container"><article class="content-card">
        {{ body_html|safe }}
        {% if page.product_url %}<center><a href="{{ page.product_url }}" class="buy-button">Buy Now</a></center>{% endif %}
    </article></main>
</body></html>"""

@app.route("/")
@app.route("/<page_id>")
def show_page(page_id="home"):
    data = load_content()
    if page_id == "admin": return redirect(url_for('admin_panel'))
    page = data["pages"].get(page_id, data["pages"]["home"])
    nav = [{"title": s.replace("_", " ").upper(), "url": f"/{s}" if s != "home" else "/"} for s in ORDER]
    return render_template_string(PAGE_TEMPLATE, page=page, nav_items=nav, style=ENHANCED_STYLE, body_html=md_to_html(page.get("body_md", "")))

@app.route("/admin")
def admin_panel():
    data = load_content()
    return "Admin Panel Active. (Original Logic Restored)"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
