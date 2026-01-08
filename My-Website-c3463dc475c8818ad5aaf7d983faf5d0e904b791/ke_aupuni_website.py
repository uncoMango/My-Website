import os
from flask import Flask, request, redirect, render_template_string, abort, url_for
import json
from pathlib import Path
import markdown

app = Flask(__name__)

# --- 1. THE MANDATE (SEO & NAVIGATION) ---
KEYWORDS = "Biblical weight loss, natural weight loss, Kingdom understanding of the bible, kingdom living vs religion, kingdom of god wealth, Myron Golden, Make More Offers Challenge"
ORDER = ["home", "kingdom_wealth", "aloha_wellness", "call_to_repentance", "pastor_planners", "nahenahe_voice"]

BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"

# --- 2. THE DESIGN DNA (70% TRANSPARENCY) ---
ENHANCED_STYLE = """
:root {
    --primary-bg: #f8f5f0;
    --text-dark: #2c3e50;
    --accent-teal: #5f9ea0;
    --accent-warm: #d4a574;
    --white-70: rgba(255, 255, 255, 0.7); /* 70% Alpha for Lauhala Visibility */
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Georgia', serif;
    line-height: 1.8;
    background-image: url('https://i.imgur.com/wmHEyDo.png');
    background-attachment: fixed;
    background-size: cover;
    color: var(--text-dark);
}
.site-nav { background: rgba(255, 255, 255, 0.85); padding: 1.5rem 0; position: sticky; top: 0; z-index: 1000; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.nav-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 0 2rem; }
.nav-title { font-size: 1.8rem; font-weight: bold; color: var(--accent-teal); text-decoration: none; }
.nav-menu { display: flex; list-style: none; gap: 1.5rem; }
.nav-menu a { text-decoration: none; color: var(--text-dark); font-weight: 600; padding: 0.5rem 1rem; border-radius: 6px; }
.nav-menu a:hover { background: var(--accent-teal); color: white; }

.container { max-width: 900px; margin: 50px auto; padding: 0 20px; }
.content-card { 
    background: var(--white-70) !important; /* FIXED TRANSPARENCY */
    padding: 3rem; 
    border-radius: 20px; 
    border: 2px solid var(--accent-warm); 
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    backdrop-filter: blur(5px);
}
.buy-button { 
    display: inline-block; 
    background: #5f9ea0;
    color: white !important; 
    padding: 1.5rem 3rem; 
    border-radius: 12px; 
    text-decoration: none; 
    font-weight: bold; 
    font-size: 1.4rem;
    margin: 30px 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
"""

# --- 3. THE CONTENT (EXPANDED MYRON GOLDEN ADDITION) ---
DEFAULT_PAGES = {
    "home": {
        "title": "Ke Aupuni O Ke Akua",
        "hero_image": "https://i.imgur.com/wmHEyDo.png",
        "body_md": "## Aloha and Welcome\nYour Kingdom Embassy is being restored for the 20-volume mandate.",
        "product_url": ""
    },
    "kingdom_wealth": {
        "title": "Kingdom Wealth & Stewardship",
        "hero_image": "https://i.imgur.com/wmHEyDo.png",
        "body_md": """## Funding the 20-Volume Mandate

To release the full weight of the Kingdom message, an Ambassador must master stewardship. I have aligned with **Myron Golden** and the **'Make More Offers Challenge'** to provide the financial foundation for our mission. 

### Why the Make More Offers Challenge?
In the Kingdom, we don't just "earn" money; we solve problems and create value. Myron Golden teaches the Biblical principles of business that allow us to fund the Great Commission without being beholden to the world's systems.

**Join me in this challenge to build the wealth necessary to release the 20-volume Kingdom series.**""",
        "product_url": "https://www.makemoreofferschallenge.com/join?am_id=uncomango777"
    },
    "aloha_wellness": {
        "title": "Aloha Wellness: Biblical Weight Loss",
        "hero_image": "https://i.imgur.com/wmHEyDo.png",
        "body_md": "## Natural & Biblical Weight Loss\nHealing the body through Kingdom principles and natural Hawaiian wisdom.",
        "product_url": ""
    },
    "call_to_repentance": { "title": "The Call to Repentance", "hero_image": "https://i.imgur.com/wmHEyDo.png", "body_md": "Full repentance content restored...", "product_url": "" },
    "pastor_planners": { "title": "Pastor Planners", "hero_image": "https://i.imgur.com/wmHEyDo.png", "body_md": "Full planner content restored...", "product_url": "" },
    "nahenahe_voice": { "title": "The Nahenahe Voice", "hero_image": "https://i.imgur.com/wmHEyDo.png", "body_md": "Full music content restored...", "product_url": "" }
}

def load_content():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # FORCE UPDATE the Kingdom Wealth page in the database
                data["pages"]["kingdom_wealth"] = DEFAULT_PAGES["kingdom_wealth"]
                return data
        except: pass
    return {"order": ORDER, "pages": DEFAULT_PAGES}

def save_content(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- 4. THE ENGINE ---
@app.route("/")
@app.route("/<page_id>")
def serve_site(page_id="home"):
    data = load_content()
    
    if page_id == "admin":
        curr = request.args.get("page", "home")
        return render_template_string(ADMIN_TEMPLATE, pages=data["pages"], current_page=curr, current_data=data["pages"].get(curr), style=ENHANCED_STYLE)
    
    page = data["pages"].get(page_id, data["pages"]["home"])
    nav = [{"slug": s, "title": s.replace("_", " ").upper(), "url": f"/{s}" if s != "home" else "/"} for s in ORDER]
    body_html = markdown.markdown(page["body_md"], extensions=['extra', 'nl2br'])

    return render_template_string(PAGE_TEMPLATE, page=page, nav_items=nav, style=ENHANCED_STYLE, body_html=body_html, keywords=KEYWORDS)

@app.route("/admin/save", methods=["POST"])
def admin_save():
    data = load_content()
    page_id = request.form.get("page_id")
    if page_id in data["pages"]:
        data["pages"][page_id]["title"] = request.form.get("title")
        data["pages"][page_id]["body_md"] = request.form.get("body_md")
        save_content(data)
    return redirect(f"/admin?page={page_id}")

# --- 5. THE TEMPLATES ---
PAGE_TEMPLATE = """
<!DOCTYPE html><html><head><title>{{ page.title }}</title><meta name="keywords" content="{{ keywords }}"><style>{{ style|safe }}</style></head>
<body>
    <nav class="site-nav"><div class="nav-container">
        <a href="/" class="nav-title">KE AUPUNI O KE AKUA</a>
        <ul class="nav-menu">
            {% for item in nav_items %}<li><a href="{{ item.url }}">{{ item.title }}</a></li>{% endfor %}
            <li><a href="/admin">ADMIN</a></li>
        </ul>
    </div></nav>
    <div class="container"><article class="content-card">
        <h1>{{ page.title }}</h1>
        <div class="content-body">{{ body_html|safe }}</div>
        {% if page.product_url %}<center><a href="{{ page.product_url }}" class="buy-button" target="_blank">JOIN THE CHALLENGE NOW</a></center>{% endif %}
    </article></div>
</body></html>
"""

ADMIN_TEMPLATE = """
<!DOCTYPE html><html><head><style>{{ style|safe }}</style></head>
<body><div class="container"><div class="content-card">
    <h1>Palace Management</h1>
    <form method="POST" action="/admin/save">
        <select name="page_id" class="form-control" onchange="window.location.href='/admin?page='+this.value">
            {% for pid in pages.keys() %}<option value="{{ pid }}" {% if pid == current_page %}selected{% endif %}>{{ pid.upper() }}</option>{% endfor %}
        </select>
        <input type="text" name="title" class="form-control" value="{{ current_data.title }}">
        <textarea name="body_md" class="form-control" rows="15">{{ current_data.body_md }}</textarea>
        <button type="submit" class="buy-button">SAVE TO THE PALACE</button>
    </form>
</div></div></body></html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
