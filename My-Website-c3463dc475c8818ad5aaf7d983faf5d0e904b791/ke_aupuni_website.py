# ke_aupuni_o_ke_akua_complete.py
# Complete Hawaiian Kingdom website with working admin and beautiful content

from flask import Flask, request, redirect, render_template_string, abort, url_for
import json
import os
from pathlib import Path
import markdown

app = Flask(__name__)

# --- RESTORED ORIGINAL NAVIGATION ORDER + NEW PAGE ---
ORDER = ["home", "kingdom_wealth", "aloha_wellness", "call_to_repentance", "pastor_planners", "nahenahe_voice"]

# Data storage
BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"

# --- RESTORED ORIGINAL CONTENT + NEW KINGDOM WEALTH ---
DEFAULT_PAGES = {
    "home": {
        "title": "Ke Aupuni O Ke Akua - The Kingdom of God",
        "hero_image": "https://images.unsplash.com/photo-1580656449195-8c8203e0edd0?auto=format&fit=crop&w=1200&q=80",
        "body_md": """## Aloha and Welcome to Our Sacred Space

Welcome to **Ke Aupuni O Ke Akua** (The Kingdom of God), a peaceful digital sanctuary where Hawaiian wisdom meets spiritual growth. Our mission is to share the beauty of island life, traditional mo'olelo (stories), and kingdom principles that nurture both body and soul.""",
        "product_url": ""
    },
    "kingdom_wealth": {
        "title": "Kingdom Wealth & Stewardship",
        "hero_image": "https://i.imgur.com/wmHEyDo.png",
        "body_md": """## Funding the 20-Volume Mandate

To release the full weight of the Kingdom message, an Ambassador must master stewardship. I have aligned with **Myron Golden** and the "Make More Offers Challenge" to provide the financial foundation for our mission to release the 20-volume Kingdom series.""",
        "product_url": "https://www.makemoreofferschallenge.com/join?am_id=uncomango777"
    },
    "aloha_wellness": {
        "title": "Aloha Wellness - Island Health & Healing",
        "hero_image": "https://images.unsplash.com/photo-1600298881974-6be191ceeda1?auto=format&fit=crop&w=1200&q=80",
        "body_md": """## Traditional Hawaiian Wellness Practices\n\nDiscover the ancient Hawaiian approach to health and wellness that harmonizes mind, body, and spirit with the natural world.""",
        "product_url": "https://www.amazon.com/s?k=hawaiian+wellness+books"
    },
    "call_to_repentance": {
        "title": "The Call to Repentance",
        "hero_image": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?auto=format&fit=crop&w=1200&q=80",
        "body_md": """## Embracing True Repentance for Spiritual Growth\n\nRepentance leads to joy, not condemnation. Every step toward repentance is a step toward freedom, peace, and abundant life in His kingdom.""",
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
        "body_md": """## Preserving the Gentle Voice of Hawaiian Music\n\n**Nahenahe** means "soft, sweet, melodious" in Hawaiian.""",
        "product_url": ""
    }
}

# --- RESTORED FULL ORIGINAL STYLING ---
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
    box-shadow: var(--shadow-soft);
    backdrop-filter: blur(10px);
}
.nav-container {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
}
.nav-title { font-size: 1.5rem; font-weight: bold; color: var(--accent-teal); text-decoration: none; }
.nav-menu { display: flex; list-style: none; gap: 2rem; }
.nav-menu a { text-decoration: none; color: var(--text-dark); font-weight: 500; padding: 0.5rem 1rem; border-radius: 6px; }
.nav-menu a:hover { background: var(--accent-teal); color: white; }
.hero { height: 60vh; background-size: cover; background-position: center; position: relative; display: flex; align-items: flex-end; }
.hero-overlay { position: absolute; inset: 0; background: linear-gradient(0deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 100%); }
.hero-content { position: relative; z-index: 2; color: white; padding: 2rem; max-width: 1200px; margin: 0 auto; width: 100%; }
.container { max-width: 1000px; margin: 0 auto; padding: 2rem; }
.content-card { background: rgba(255,255,255,0.9); padding: 3rem 2rem; border-radius: 15px; margin-top: -50px; position: relative; z-index: 3; box-shadow: var(--shadow-soft); }
.buy-button { display: inline-block; background: var(--accent-teal); color: white !important; padding: 1rem 2rem; border-radius: 8px; text-decoration: none; font-weight: bold; }
.admin-panel { background: white; border-radius: 8px; padding: 2rem; margin: 2rem auto; max-width: 800px; }
.form-control { width: 100%; padding: 0.75rem; border: 2px solid #e1e5e9; border-radius: 6px; margin-bottom: 1rem; }
"""

# --- RESTORED ORIGINAL LOGIC ---
def md_to_html(md_text):
    return markdown.markdown(md_text, extensions=["extra", "nl2br"])

def load_content():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"order": ORDER, "pages": DEFAULT_PAGES}

def save_content(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def render_page(page_id, data):
    page = data["pages"].get(page_id, data["pages"]["home"])
    nav_items = [{"slug": s, "title": data["pages"].get(s, {}).get("title", s.replace("_", " ").title()), "url": f"/{s}" if s != "home" else "/"} for s in ORDER]
    
    return render_template_string(PAGE_TEMPLATE, 
        page=page, nav_items=nav_items, style=ENHANCED_STYLE, 
        body_html=md_to_html(page.get("body_md", "")), current_page=page_id)

PAGE_TEMPLATE = """<!DOCTYPE html><html><head><style>{{ style }}</style></head>
<body>
    <nav class="site-nav"><div class="nav-container"><a href="/" class="nav-title">Ke Aupuni O Ke Akua</a>
    <ul class="nav-menu">{% for item in nav_items %}<li><a href="{{ item.url }}">{{ item.title }}</a></li>{% endfor %}<li><a href="/admin">Admin</a></li></ul></div></nav>
    <header class="hero" style="background-image: url('{{ page.hero_image }}');"><div class="hero-overlay"></div><div class="hero-content"><h1>{{ page.title }}</h1></div></header>
    <main class="container"><article class="content-card">{{ body_html|safe }}
    {% if page.product_url %}<center><br><a href="{{ page.product_url }}" class="buy-button">JOIN THE CHALLENGE NOW</a></center>{% endif %}</article></main>
</body></html>"""

ADMIN_TEMPLATE = """<!DOCTYPE html><html><head><style>{{ style }}</style></head>
<body><div class="container"><div class="admin-panel"><h1>Admin Panel</h1><form method="POST" action="/admin/save">
<select name="page_id" class="form-control" onchange="window.location.href='/admin?page='+this.value">
{% for pid in pages.keys() %}<option value="{{ pid }}" {% if pid == current_page %}selected{% endif %}>{{ pages[pid].title }}</option>{% endfor %}</select>
<input type="text" name="title" class="form-control" value="{{ current_data.title }}"><textarea name="body_md" class="form-control" rows="10">{{ current_data.body_md }}</textarea>
<button type="submit" class="buy-button">Save Changes</button></form></div></div></body></html>"""

@app.route("/")
@app.route("/<page_id>")
def home(page_id="home"):
    data = load_content()
    if page_id == "admin":
        current_p = request.args.get("page", "home")
        return render_template_string(ADMIN_TEMPLATE, style=ENHANCED_STYLE, pages=data["pages"], current_page=current_p, current_data=data["pages"].get(current_p))
    if page_id not in data["pages"]: abort(404)
    return render_page(page_id, data)

@app.route("/admin/save", methods=["POST"])
def admin_save():
    data = load_content()
    page_id = request.form.get("page_id")
    if page_id in data["pages"]:
        data["pages"][page_id]["title"] = request.form.get("title")
        data["pages"][page_id]["body_md"] = request.form.get("body_md")
        save_content(data)
    return redirect(f"/admin?page={page_id}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
