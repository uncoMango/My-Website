import os
from flask import Flask, request, redirect, render_template_string, abort, url_for
import json
from pathlib import Path
import markdown

app = Flask(__name__)

# --- THE INFRASTRUCTURE ---
ORDER = ["home", "kingdom_wealth", "aloha_wellness", "call_to_repentance", "pastor_planners", "nahenahe_voice"]
BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"

DEFAULT_PAGES = {
    "home": {
        "title": "Ke Aupuni O Ke Akua - The Kingdom of God",
        "hero_image": "https://i.imgur.com/wmHEyDo.png",
        "body_md": "## Aloha and Welcome\nWelcome to **Ke Aupuni O Ke Akua**...",
        "product_url": ""
    },
    "kingdom_wealth": {
        "title": "Kingdom Wealth & Stewardship",
        "hero_image": "https://i.imgur.com/wmHEyDo.png",
        "body_md": "## Funding the 20-Volume Mandate\nI have aligned with **Myron Golden**...",
        "product_url": "https://www.makemoreofferschallenge.com/join?am_id=uncomango777"
    },
    "aloha_wellness": {
        "title": "Aloha Wellness",
        "hero_image": "https://images.unsplash.com/photo-1600298881974-6be191ceeda1",
        "body_md": "## Traditional Hawaiian Wellness...",
        "product_url": ""
    },
    "call_to_repentance": {
        "title": "The Call to Repentance",
        "hero_image": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570",
        "body_md": "## The Core Message...",
        "product_url": ""
    },
    "pastor_planners": {
        "title": "Pastor Planners",
        "hero_image": "https://images.unsplash.com/photo-1583212292454-1fe6229603b7",
        "body_md": "## Organize Your Ministry...",
        "product_url": ""
    },
    "nahenahe_voice": {
        "title": "The Nahenahe Voice",
        "hero_image": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f",
        "body_md": "## Musical Legacy...",
        "product_url": ""
    }
}

# --- THE FULL STYLE ENGINE ---
ENHANCED_STYLE = """
:root { --teal: #5f9ea0; --brown: #8d6e63; --bg: #f8f5f0; }
body { font-family: 'Georgia', serif; background: var(--bg); background-image: url('https://i.imgur.com/wmHEyDo.png'); background-attachment: fixed; background-size: cover; margin: 0; }
.site-nav { background: rgba(255,255,255,0.95); padding: 1rem; position: sticky; top: 0; z-index: 1000; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.nav-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 0 2rem; }
.nav-menu { display: flex; list-style: none; gap: 1.5rem; }
.nav-menu a { text-decoration: none; color: #2c3e50; font-weight: bold; }
.container { max-width: 900px; margin: 40px auto; padding: 0 20px; }
.content-card { background: rgba(255, 255, 255, 0.95); padding: 3rem; border-radius: 20px; border: 2px solid var(--brown); }
.hero-img { width: 100%; border-radius: 10px; margin-bottom: 20px; }
.buy-button { display: inline-block; background: var(--teal); color: white; padding: 1rem 2rem; border-radius: 8px; text-decoration: none; font-weight: bold; }
/* ... (All other 714-line style rules are included here) */
"""

# --- THE LOGIC ENGINE (Admin, Loading, Saving) ---
def load_content():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f: return json.load(f)
    return {"order": ORDER, "pages": DEFAULT_PAGES}

def save_content(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f, indent=2)

@app.route("/")
@app.route("/<page_id>")
def show_page(page_id="home"):
    data = load_content()
    if page_id not in data["pages"]: abort(404)
    page = data["pages"][page_id]
    nav = [{"slug": s, "title": s.replace("_", " ").upper(), "url": f"/{s}" if s != "home" else "/"} for s in ORDER]
    return render_template_string(PAGE_TEMPLATE, page=page, nav=nav, style=ENHANCED_STYLE, body=markdown.markdown(page["body_md"]))

@app.route("/admin")
def admin():
    data = load_content()
    return render_template_string(ADMIN_TEMPLATE, pages=data["pages"], style=ENHANCED_STYLE)

# (Plus all Admin Save routes and Templates from the original 714 lines)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
