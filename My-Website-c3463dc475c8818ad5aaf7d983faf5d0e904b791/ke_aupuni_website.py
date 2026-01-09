import os
from flask import Flask, request, redirect, render_template_string, abort, url_for
import json
from pathlib import Path
import markdown

app = Flask(__name__)

# --- 1. THE MANDATE (FORCED SEO & NAVIGATION) ---
# 'kingdom_wealth' is now hard-coded at index 1
ORDER = ["home", "kingdom_wealth", "aloha_wellness", "call_to_repentance", "pastor_planners", "nahenahe_voice"]
BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"

# --- 2. THE DESIGN DNA (70% ALPHA LOCK) ---
ENHANCED_STYLE = """
:root {
    --primary-bg: #f8f5f0;
    --text-dark: #2c3e50;
    --accent-teal: #5f9ea0;
    --accent-warm: #d4a574;
    --white-70: rgba(255, 255, 255, 0.7); /* THE TRANSPARENCY KEY */
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Georgia', serif;
    background-image: url('https://i.imgur.com/wmHEyDo.png');
    background-attachment: fixed;
    background-size: cover;
    color: var(--text-dark);
}
.site-nav { background: rgba(255, 255, 255, 0.85); padding: 1.5rem 0; position: sticky; top: 0; z-index: 1000; }
.nav-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; padding: 0 2rem; }
.nav-menu { display: flex; list-style: none; gap: 1.5rem; }
.nav-menu a { text-decoration: none; color: var(--text-dark); font-weight: 600; padding: 0.5rem 1rem; }

.container { max-width: 900px; margin: 50px auto; padding: 0 20px; }
.content-card { 
    background: var(--white-70) !important; /* FORCED TRANSPARENCY */
    padding: 3rem; 
    border-radius: 20px; 
    border: 2px solid var(--accent-warm); 
    backdrop-filter: blur(5px);
}
.buy-button { 
    display: inline-block; background: var(--accent-teal); color: white !important; 
    padding: 1.2rem 2.5rem; border-radius: 10px; text-decoration: none; font-weight: bold;
}
"""

# --- 3. THE HARD-CODED CONTENT (SEE THE WEALTH PAGE HERE) ---
DEFAULT_PAGES = {
    "home": {
        "title": "Ke Aupuni O Ke Akua",
        "body_md": "## Aloha\nWelcome to your Kingdom Embassy.",
        "product_url": ""
    },
    "kingdom_wealth": {
        "title": "Kingdom Wealth & Stewardship",
        "body_md": "## Funding the 20-Volume Mandate\nI have aligned with **Myron Golden** and the 'Make More Offers Challenge' to provide the financial foundation for our mission to release the Kingdom series. Stewardship is the key to Kingdom expansion.",
        "product_url": "https://www.makemoreofferschallenge.com/join?am_id=uncomango777"
    },
    "aloha_wellness": {
        "title": "Aloha Wellness: Biblical Weight Loss",
        "body_md": "## Natural Healing\nRestoring the temple through Biblical principles.",
        "product_url": ""
    }
}

def load_content():
    data = {"order": ORDER, "pages": DEFAULT_PAGES}
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r") as f:
                saved = json.load(f)
                data["pages"].update(saved.get("pages", {}))
        except: pass
    
    # THE REASON IT ADDS THE PAGE: We force the dictionary to include these keys
    data["pages"]["kingdom_wealth"] = DEFAULT_PAGES["kingdom_wealth"]
    data["order"] = ORDER
    return data

# --- 4. THE ROUTES & LOGIC ---
@app.route("/")
@app.route("/<page_id>")
def serve_site(page_id="home"):
    data = load_content()
    
    if page_id == "admin":
        curr = request.args.get("page", "home")
        return render_template_string(ADMIN_TEMPLATE, pages=data["pages"], current_page=curr, current_data=data["pages"].get(curr), style=ENHANCED_STYLE)
    
    page = data["pages"].get(page_id, data["pages"]["home"])
    nav = [{"slug": s, "title": s.replace("_", " ").upper(), "url": f"/{s}" if s != "home" else "/"} for s in ORDER]
    
    return render_template_string(PAGE_TEMPLATE, page=page, nav_items=nav, style=ENHANCED_STYLE, body_html=markdown.markdown(page.get("body_md", "")))

@app.route("/admin/save", methods=["POST"])
def admin_save():
    data = load_content()
    pid = request.form.get("page_id")
    if pid:
        if pid not in data["pages"]: data["pages"][pid] = {}
        data["pages"][pid]["title"] = request.form.get("title")
        data["pages"][pid]["body_md"] = request.form.get("body_md")
        data["pages"][pid]["product_url"] = request.form.get("product_url", "")
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    return redirect(f"/admin?page={pid}")

# --- 5. THE TEMPLATES ---
PAGE_TEMPLATE = """
<!DOCTYPE html><html><head><title>{{ page.title }}</title><style>{{ style|safe }}</style></head>
<body>
    <nav class="site-nav"><div class="nav-container">
        <a href="/" style="text-decoration:none; color:var(--accent-teal); font-weight:bold;">KE AUPUNI</a>
        <ul class="nav-menu">
            {% for item in nav_items %}<li><a href="{{ item.url }}">{{ item.title }}</a></li>{% endfor %}
            <li><a href="/admin">ADMIN</a></li>
        </ul>
    </div></nav>
    <div class="container"><article class="content-card">
        <h1>{{ page.title }}</h1>
        <div>{{ body_html|safe }}</div>
        {% if page.product_url %}<center><a href="{{ page.product_url }}" class="buy-button">JOIN THE CHALLENGE</a></center>{% endif %}
    </article></div>
</body></html>
"""

ADMIN_TEMPLATE = """
<!DOCTYPE html><html><head><style>{{ style|safe }}</style></head>
<body><div class="container"><div class="content-card">
    <h1>Palace Management</h1>
    <form method="POST" action="/admin/save">
        <select name="page_id" onchange="window.location.href='/admin?page='+this.value">
            {% for pid in pages.keys() %}<option value="{{ pid }}" {% if pid == current_page %}selected{% endif %}>{{ pid.upper() }}</option>{% endfor %}
        </select>
        <input type="text" name="title" value="{{ current_data.title }}" style="width:100%; margin:10px 0;">
        <input type="text" name="product_url" value="{{ current_data.product_url }}" placeholder="Affiliate Link" style="width:100%; margin:10px 0;">
        <textarea name="body_md" style="width:100%; height:300px;">{{ current_data.body_md }}</textarea>
        <button type="submit" class="buy-button">SAVE CHANGES</button>
    </form>
</div></div></body></html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
