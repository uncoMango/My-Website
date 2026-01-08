import os
from flask import Flask, request, redirect, render_template_string, abort, url_for
import json
from pathlib import Path
import markdown

app = Flask(__name__)

# --- THE MANDATE: NAVIGATION ---
ORDER = ["home", "kingdom_wealth", "aloha_wellness", "call_to_repentance", "pastor_planners", "nahenahe_voice"]
BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"

# --- THE DESIGN DNA: FULL CSS RESTORED ---
ENHANCED_STYLE = """
:root {
    --primary-bg: #f8f5f0;
    --text-dark: #2c3e50;
    --accent-teal: #5f9ea0;
    --accent-warm: #d4a574;
    --white-transparent: rgba(255, 255, 255, 0.7); /* CHANGED TO 70% TRANSPARENCY */
    --shadow-soft: 0 4px 15px rgba(0,0,0,0.1);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Georgia', 'Times New Roman', serif;
    line-height: 1.8;
    color: var(--text-dark);
    background-image: url('https://i.imgur.com/wmHEyDo.png');
    background-attachment: fixed;
    background-size: cover;
    background-color: var(--primary-bg);
}
.site-nav {
    background: rgba(255, 255, 255, 0.85);
    padding: 1.5rem 0;
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
.nav-title { font-size: 1.8rem; font-weight: bold; color: var(--accent-teal); text-decoration: none; }
.nav-menu { display: flex; list-style: none; gap: 2rem; }
.nav-menu a { text-decoration: none; color: var(--text-dark); font-weight: 600; padding: 0.5rem 1rem; border-radius: 6px; transition: all 0.3s; }
.nav-menu a:hover { background: var(--accent-teal); color: white; }

.container { max-width: 1000px; margin: 60px auto; padding: 0 2rem; }
.content-card { 
    background: var(--white-transparent); /* THIS IS THE 70% BOX */
    padding: 4rem 3rem; 
    border-radius: 25px; 
    border: 2px solid var(--accent-warm); 
    box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    backdrop-filter: blur(5px); /* Adds a nice glass effect over the Lauhala */
}
.hero-title { font-size: 3rem; margin-bottom: 2rem; color: var(--text-dark); border-bottom: 3px solid var(--accent-warm); display: inline-block; }
.buy-button { 
    display: inline-block; 
    background: var(--accent-teal); 
    color: white !important; 
    padding: 1.2rem 2.5rem; 
    border-radius: 12px; 
    text-decoration: none; 
    font-weight: bold; 
    font-size: 1.2rem;
    margin-top: 30px;
    box-shadow: 0 4px 15px rgba(95, 158, 160, 0.4);
}
.admin-panel { background: white; border-radius: 12px; padding: 3rem; box-shadow: var(--shadow-soft); }
.form-control { width: 100%; padding: 1rem; border: 2px solid #ddd; border-radius: 8px; margin-bottom: 1.5rem; font-size: 1rem; }
"""

# --- THE CONTENT ENGINE ---
DEFAULT_PAGES = {
    "home": {
        "title": "Ke Aupuni O Ke Akua",
        "hero_image": "https://i.imgur.com/wmHEyDo.png",
        "body_md": "## Aloha and Welcome\n\nWelcome to the Kingdom of God digital sanctuary.",
        "product_url": ""
    },
    "kingdom_wealth": {
        "title": "Kingdom Wealth & Stewardship",
        "hero_image": "https://i.imgur.com/wmHEyDo.png",
        "body_md": "## Funding the 20-Volume Mandate\n\nI have aligned with **Myron Golden** and the 'Make More Offers Challenge' to provide the financial foundation for our mission to release the Kingdom series.",
        "product_url": "https://www.makemoreofferschallenge.com/join?am_id=uncomango777"
    },
    "aloha_wellness": { "title": "Aloha Wellness", "hero_image": "https://i.imgur.com/wmHEyDo.png", "body_md": "Wellness content...", "product_url": "" },
    "call_to_repentance": { "title": "The Call to Repentance", "hero_image": "https://i.imgur.com/wmHEyDo.png", "body_md": "Message...", "product_url": "" },
    "pastor_planners": { "title": "Pastor Planners", "hero_image": "https://i.imgur.com/wmHEyDo.png", "body_md": "Organization...", "product_url": "" },
    "nahenahe_voice": { "title": "The Nahenahe Voice", "hero_image": "https://i.imgur.com/wmHEyDo.png", "body_md": "Music...", "product_url": "" }
}

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

# --- THE ROUTES ---
@app.route("/")
@app.route("/<page_id>")
def serve_palace(page_id="home"):
    data = load_content()
    
    # Ensure Kingdom Wealth is present even if JSON is old
    if "kingdom_wealth" not in data["pages"]:
        data["pages"]["kingdom_wealth"] = DEFAULT_PAGES["kingdom_wealth"]
        save_content(data)

    if page_id == "admin":
        curr = request.args.get("page", "home")
        return render_template_string(ADMIN_TEMPLATE, style=ENHANCED_STYLE, pages=data["pages"], current_page=curr, current_data=data["pages"].get(curr))
    
    if page_id not in data["pages"]: abort(404)
    
    page = data["pages"][page_id]
    nav_items = [{"slug": s, "title": s.replace("_", " ").upper(), "url": f"/{s}" if s != "home" else "/"} for s in ORDER]
    body_html = markdown.markdown(page["body_md"], extensions=['extra', 'nl2br'])
    
    return render_template_string(PAGE_TEMPLATE, page=page, nav_items=nav_items, style=ENHANCED_STYLE, body_html=body_html)

@app.route("/admin/save", methods=["POST"])
def admin_save():
    data = load_content()
    page_id = request.form.get("page_id")
    if page_id in data["pages"]:
        data["pages"][page_id]["title"] = request.form.get("title")
        data["pages"][page_id]["body_md"] = request.form.get("body_md")
        save_content(data)
    return redirect(url_for('serve_palace', page_id='admin', page=page_id))

# --- FULL TEMPLATES ---
PAGE_TEMPLATE = """
<!DOCTYPE html><html><head><title>{{ page.title }}</title><style>{{ style|safe }}</style></head>
<body>
    <nav class="site-nav"><div class="nav-container">
        <a href="/" class="nav-title">KE AUPUNI O KE AKUA</a>
        <ul class="nav-menu">
            {% for item in nav_items %}<li><a href="{{ item.url }}">{{ item.title }}</a></li>{% endfor %}
            <li><a href="/admin" style="color:var(--accent-warm);">ADMIN</a></li>
        </ul>
    </div></nav>
    <div class="container"><article class="content-card">
        <h1 class="hero-title">{{ page.title }}</h1>
        <div class="content-body">{{ body_html|safe }}</div>
        {% if page.product_url %}<center><a href="{{ page.product_url }}" class="buy-button" target="_blank">JOIN THE CHALLENGE NOW</a></center>{% endif %}
    </article></div>
</body></html>
"""

ADMIN_TEMPLATE = """
<!DOCTYPE html><html><head><title>Admin Panel</title><style>{{ style|safe }}</style></head>
<body><div class="container"><div class="admin-panel"><h1>Palace Management</h1>
<form method="POST" action="/admin/save">
    <label>Select Page:</label>
    <select name="page_id" class="form-control" onchange="window.location.href='/admin?page='+this.value">
        {% for pid in pages.keys() %}<option value="{{ pid }}" {% if pid == current_page %}selected{% endif %}>{{ pid.upper() }}</option>{% endfor %}
    </select>
    <label>Page Title:</label>
    <input type="text" name="title" class="form-control" value="{{ current_data.title }}">
    <label>Content (Markdown):</label>
    <textarea name="body_md" class="form-control" rows="15">{{ current_data.body_md }}</textarea>
    <button type="submit" class="buy-button">SAVE TO THE PALACE</button>
</form>
<p><a href="/">Return to Site</a></p></div></div></body></html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
