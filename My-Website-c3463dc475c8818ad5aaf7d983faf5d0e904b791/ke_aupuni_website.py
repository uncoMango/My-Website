import os
from flask import Flask, request, redirect, render_template_string, abort, url_for
import json
from pathlib import Path
import markdown

app = Flask(__name__)

# --- 1. THE MANDATE (SEO & NAVIGATION) ---
KEYWORDS = "Biblical weight loss, natural weight loss, Kingdom understanding of the bible, kingdom living vs religion, kingdom of god wealth, Myron Golden"
# This list defines your core menu
ORDER = ["home", "kingdom_wealth", "aloha_wellness", "call_to_repentance", "pastor_planners", "nahenahe_voice"]

BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"

# --- 2. THE DESIGN DNA (FULL 70% TRANSPARENCY) ---
ENHANCED_STYLE = """
:root {
    --primary-bg: #f8f5f0;
    --text-dark: #2c3e50;
    --accent-teal: #5f9ea0;
    --accent-warm: #d4a574;
    --white-70: rgba(255, 255, 255, 0.7); /* THIS ALLOWS LAUHALA TO BE SEEN */
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Georgia', serif;
    line-height: 1.8;
    color: var(--text-dark);
    background-image: url('https://i.imgur.com/wmHEyDo.png');
    background-attachment: fixed;
    background-size: cover;
}
.site-nav {
    background: rgba(255, 255, 255, 0.85);
    padding: 1.5rem 0;
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
.nav-title { font-size: 1.8rem; font-weight: bold; color: var(--accent-teal); text-decoration: none; }
.nav-menu { display: flex; list-style: none; gap: 1.5rem; }
.nav-menu a { text-decoration: none; color: var(--text-dark); font-weight: 600; padding: 0.5rem 1rem; border-radius: 6px; }
.nav-menu a:hover { background: var(--accent-teal); color: white; }

.container { max-width: 1000px; margin: 60px auto; padding: 0 2rem; }
.content-card { 
    background: var(--white-70) !important; 
    padding: 4rem 3rem; 
    border-radius: 25px; 
    border: 2px solid var(--accent-warm); 
    box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    backdrop-filter: blur(5px);
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
}
.admin-panel { background: white; border-radius: 12px; padding: 3rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
.form-control { width: 100%; padding: 1rem; border: 2px solid #ddd; border-radius: 8px; margin-bottom: 1.5rem; font-size: 1rem; }
"""

# --- 3. THE CONTENT ENGINE (LOAD/SAVE LOGIC) ---
DEFAULT_PAGES = {
    "home": {"title": "Ke Aupuni O Ke Akua", "body_md": "## Aloha\nWelcome back to the restored Palace.", "product_url": ""},
    "kingdom_wealth": {
        "title": "Kingdom Wealth & Stewardship",
        "body_md": "## Funding the 20-Volume Mandate\\nI have aligned with **Myron Golden** and the 'Make More Offers Challenge' to provide the financial foundation for our mission.",
        "product_url": "https://www.makemoreofferschallenge.com/join?am_id=uncomango777"
    }
}

def load_content():
    # 1. Start with the hard-coded defaults
    data = {"order": ORDER, "pages": DEFAULT_PAGES}
    
    # 2. Try to load your 40+ pages from the JSON file
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
                # Merge saved pages into our current session
                if "pages" in saved_data:
                    data["pages"].update(saved_data["pages"])
        except:
            pass
            
    # 3. FORCE the Kingdom Wealth page to exist
    data["pages"]["kingdom_wealth"] = DEFAULT_PAGES["kingdom_wealth"]
    data["order"] = ORDER
    return data

def save_content(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- 4. THE ROUTES (THE PALACE GATES) ---
@app.route("/")
@app.route("/<page_id>")
def serve_palace(page_id="home"):
    data = load_content()
    
    # --- ADMIN ACCESS ---
    if page_id == "admin":
        curr_id = request.args.get("page", "home")
        return render_template_string(ADMIN_TEMPLATE, 
                                     style=ENHANCED_STYLE, 
                                     pages=data["pages"], 
                                     current_page=curr_id, 
                                     current_data=data["pages"].get(curr_id, data["pages"]["home"]))
    
    if page_id not in data["pages"]:
        abort(404)
        
    page = data["pages"][page_id]
    nav_items = [{"slug": s, "title": s.replace("_", " ").upper(), "url": f"/{s}" if s != "home" else "/"} for s in data["order"]]
    body_html = markdown.markdown(page.get("body_md", ""), extensions=['extra', 'nl2br'])
    
    return render_template_string(PAGE_TEMPLATE, 
                                 page=page, 
                                 nav_items=nav_items, 
                                 style=ENHANCED_STYLE, 
                                 body_html=body_html, 
                                 keywords=KEYWORDS)

@app.route("/admin/save", methods=["POST"])
def admin_save():
    data = load_content()
    page_id = request.form.get("page_id")
    if page_id:
        if page_id not in data["pages"]:
            data["pages"][page_id] = {}
        data["pages"][page_id]["title"] = request.form.get("title")
        data["pages"][page_id]["body_md"] = request.form.get("body_md")
        data["pages"][page_id]["product_url"] = request.form.get("product_url", "")
        save_content(data)
    return redirect(url_for('serve_palace', page_id='admin', page=page_id))

# --- 5. THE TEMPLATES (FULL HTML) ---
PAGE_TEMPLATE = """
<!DOCTYPE html><html><head><title>{{ page.title }}</title><meta name="keywords" content="{{ keywords }}"><style>{{ style|safe }}</style></head>
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
    <label>Select Page to Edit:</label>
    <select name="page_id" class="form-control" onchange="window.location.href='/admin?page='+this.value">
        {% for pid in pages.keys() %}<option value="{{ pid }}" {% if pid == current_page %}selected{% endif %}>{{ pid.upper() }}</option>{% endfor %}
    </select>
    <label>Page Title:</label>
    <input type="text" name="title" class="form-control" value="{{ current_data.title }}">
    <label>Affiliate/Product Link (Optional):</label>
    <input type="text" name="product_url" class="form-control" value="{{ current_data.product_url }}">
    <label>Content (Markdown):</label>
    <textarea name="body_md" class="form-control" rows="15">{{ current_data.body_md }}</textarea>
    <button type="submit" class="buy-button">SAVE TO THE PALACE</button>
</form>
<p><a href="/">Return to Site</a></p></div></div></body></html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
