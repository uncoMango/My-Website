import os
import json
import markdown
from flask import Flask, render_template_string, request, redirect, abort
from pathlib import Path

app = Flask(__name__)
BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"

# --- 1. THE DATA ENGINE ---
ORDER = ["home", "kingdom_wealth", "call_to_repentance", "aloha_wellness", "pastor_planners", "nahenahe_voice", "kingdom_keys"]

# Your hardcoded fallback content
DEFAULT_PAGES = {
    "home": {
        "title": "Ke Aupuni O Ke Akua",
        "hero_image": "https://images.unsplash.com/photo-1505852679233-d9fd70aff56d",
        "body_md": "# Welcome to the Kingdom\nBringing biblical principles to life in Hawaiʻi.",
    },
    "kingdom_keys": {
        "title": "🎁 FREE Booklets",
        "hero_image": "https://i.imgur.com/G2YmSka.jpeg",
        "body_md": "### Download Your Digital Copies",
        "products": [{"title": "Kingdom Keys Vol 1", "cover": "", "amazon": "#", "gumroad": "#"}]
    }
}

def md_to_html(md_text):
    return markdown.markdown(md_text, extensions=["extra", "nl2br"])

def load_content():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    data = {"pages": DEFAULT_PAGES, "order": ORDER}
    save_content(data)
    return data

def save_content(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- 2. THE MASTER STYLE ---
ENHANCED_STYLE = """
:root { --accent: #5f9ea0; --gold: #d4af37; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { 
    font-family: 'Segoe UI', sans-serif; background: #1a1a1a; color: white;
    background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('https://images.unsplash.com/photo-1505852679233-d9fd70aff56d');
    background-attachment: fixed; background-size: cover; line-height: 1.6;
}
.site-nav { background: rgba(0,0,0,0.9); padding: 0.8rem 0; position: sticky; top: 0; z-index: 1000; border-bottom: 1px solid var(--gold); }
.nav-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 0 1rem; }
.nav-logo { height: 45px; }
.nav-menu { list-style: none; display: flex; gap: 1.5rem; align-items: center; }
.nav-menu a { color: white; text-decoration: none; font-weight: 500; transition: 0.3s; }
.hero { height: 45vh; display: flex; align-items: center; justify-content: center; background-size: cover; background-position: center; position: relative; }
.hero-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.5); }
.hero-content { position: relative; text-align: center; }
.container { max-width: 1100px; margin: -60px auto 60px; padding: 0 20px; position: relative; z-index: 10; }
.content-card { background: rgba(255,255,255,0.08); backdrop-filter: blur(20px); padding: 3rem; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); }
@media (max-width: 768px) { .nav-menu { display: none; } .content-card { padding: 1.5rem; } }

/* Admin Area Styles */
.admin-card { background: white; color: #333; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; }
.btn-edit { background: var(--accent); color: white; padding: 8px 16px; border-radius: 4px; text-decoration: none; }
"""

# --- 3. THE FRONTEND TEMPLATE ---
PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page.title }} | Ke Aupuni O Ke Akua</title>
    <style>{{ style|safe }}</style>
</head>
<body>
    <nav class="site-nav">
        <div class="nav-container">
            <a href="/" style="color:white;text-decoration:none;font-weight:bold;display:flex;align-items:center;">
                <img src="https://keaupuniakeakua.faith/output-onlinepngtools.png" class="nav-logo">
                <span style="margin-left:10px;">Ke Aupuni O Ke Akua</span>
            </a>
            <ul class="nav-menu">
                {% for item in nav_items %}<li><a href="{{ item.url }}">{{ item.title }}</a></li>{% endfor %}
            </ul>
        </div>
    </nav>
    <header class="hero" style="background-image: url('{{ page.hero_image }}');">
        <div class="hero-overlay"></div><div class="hero-content"><h1>{{ page.title }}</h1></div>
    </header>
    <main class="container">
        <article class="content-card">
            {{ body_html|safe }}
            {% if page.products %}
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap:20px; margin-top:30px;">
                {% for p in page.products %}
                <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:10px; border:1px solid rgba(255,255,255,0.1); text-align:center;">
                    {% if p.cover %}<img src="{{ p.cover }}" style="width:100%; border-radius:5px; margin-bottom:10px;">{% endif %}
                    <h4>{{ p.title }}</h4>
                    <a href="{{ p.amazon }}" style="color:var(--accent);">Amazon</a> | <a href="{{ p.gumroad }}" style="color:var(--gold);">Gumroad</a>
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </article>
    </main>
</body>
</html>"""

# --- 4. ROUTES ---
@app.route("/")
def home(): return render_page("home", load_content())

@app.route("/<page_id>")
def page(page_id):
    data = load_content()
    if page_id not in data["pages"]: abort(404)
    return render_page(page_id, data)

def render_page(page_id, data):
    pages = data["pages"]
    page = pages[page_id]
    nav_items = [{"title": pages[s].get("title", s), "url": f"/{s}" if s != "home" else "/"} for s in data["order"] if s in pages]
    return render_template_string(PAGE_TEMPLATE, page=page, nav_items=nav_items, style=ENHANCED_STYLE, body_html=md_to_html(page.get("body_md", "")))

# --- 5. THE ADMIN PANEL ---
@app.route("/kahu")
def admin_panel():
    data = load_content()
    pages = data["pages"]
    admin_html = f"<html><head><style>{ENHANCED_STYLE}</style></head><body style='background:#f4f7f6; color:#333;'><div class='container' style='margin-top:50px;'><h1>🌺 Admin</h1><hr><br>"
    for pid, pdata in pages.items():
        admin_html += f"<div class='admin-card'><span>{pdata.get('title', pid)}</span><a href='/kahu/edit/{pid}' class='btn-edit'>Edit Page</a></div>"
    return admin_html + "</div></body></html>"

@app.route("/kahu/edit/<page_id>", methods=["GET", "POST"])
def edit_page(page_id):
    data = load_content()
    if page_id not in data["pages"]: abort(404)
    if request.method == "POST":
        data["pages"][page_id]["title"] = request.form.get("title")
        data["pages"][page_id]["hero_image"] = request.form.get("hero_image")
        data["pages"][page_id]["body_md"] = request.form.get("body_md")
        
        # Logic to process "Pipe Delimited" products
        prod_raw = request.form.get("products_text", "").strip()
        if prod_raw:
            prods = []
            for line in prod_raw.split("\n"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 1:
                    prods.append({"title": parts[0], "cover": parts[1] if len(parts)>1 else "", "amazon": parts[2] if len(parts)>2 else "", "gumroad": parts[3] if len(parts)>3 else ""})
            data["pages"][page_id]["products"] = prods
        
        save_content(data)
        return redirect("/kahu")

    p = data["pages"][page_id]
    prod_str = "\n".join([f"{x['title']}|{x.get('cover','')}|{x.get('amazon','')}|{x.get('gumroad','')}" for x in p.get("products", [])])
    
    return f"""<html><head><style>{ENHANCED_STYLE}</style></head>
    <body style='background:#f4f7f6; color:#333;'><div class='container'>
    <form method="post" style="background:white; padding:30px; border-radius:12px;">
        <h2>Editing: {page_id}</h2><br>
        <label>Title</label><br><input name="title" value="{p['title']}" style="width:100%; padding:10px; margin-bottom:15px;">
        <label>Hero URL</label><br><input name="hero_image" value="{p.get('hero_image','')}" style="width:100%; padding:10px; margin-bottom:15px;">
        <label>Content (Markdown)</label><br><textarea name="body_md" style="width:100%; height:200px; padding:10px;">{p['body_md']}</textarea>
        <label>Products (Title | Cover | Amazon | Gumroad)</label><br><textarea name="products_text" style="width:100%; height:100px; padding:10px;">{prod_str}</textarea>
        <br><button type="submit" class="btn-edit" style="border:none; cursor:pointer;">Save Changes</button>
    </form></div></body></html>"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
