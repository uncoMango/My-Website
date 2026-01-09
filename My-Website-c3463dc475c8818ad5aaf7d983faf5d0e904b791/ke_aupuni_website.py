import os
from flask import Flask, request, redirect, render_template_string, abort, url_for
import json
from pathlib import Path
import markdown

app = Flask(__name__)

# --- THE MANDATE ---
# Adding 'kingdom_wealth' here is step 1
ORDER = ["home", "kingdom_wealth", "aloha_wellness", "call_to_repentance", "pastor_planners", "nahenahe_voice"]
BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"

# --- THE DESIGN (70% Transparency Fixed) ---
ENHANCED_STYLE = """
:root {
    --primary-bg: #f8f5f0;
    --text-dark: #2c3e50;
    --accent-teal: #5f9ea0;
    --white-70: rgba(255, 255, 255, 0.7); /* THIS IS THE 70% TRANSPARENCY */
}
body {
    font-family: 'Georgia', serif;
    background-image: url('https://i.imgur.com/wmHEyDo.png');
    background-attachment: fixed;
    background-size: cover;
    margin: 0;
}
.site-nav { background: rgba(255, 255, 255, 0.9); padding: 1.5rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.nav-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-around; }
.nav-menu a { text-decoration: none; color: var(--text-dark); font-weight: bold; }
.container { max-width: 900px; margin: 50px auto; padding: 0 20px; }
.content-card { 
    background: var(--white-70) !important; 
    padding: 3rem; 
    border-radius: 20px; 
    border: 2px solid #d4a574; 
    backdrop-filter: blur(5px);
}
.buy-button { 
    display: inline-block; background: var(--accent-teal); color: white !important; 
    padding: 1.2rem 2.5rem; border-radius: 10px; text-decoration: none; font-weight: bold; margin-top: 20px;
}
"""

# Step 2: Ensure the page content is defined in the script's memory
DEFAULT_PAGES = {
    "home": {"title": "Ke Aupuni O Ke Akua", "body_md": "## Aloha\nWelcome to the Kingdom Sanctuary."},
    "kingdom_wealth": {
        "title": "Kingdom Wealth & Stewardship",
        "body_md": "## Funding the 20-Volume Mandate\\nI have aligned with **Myron Golden** for the financial foundation of this mission.",
        "product_url": "https://www.makemoreofferschallenge.com/join?am_id=uncomango777"
    },
    "aloha_wellness": {"title": "Aloha Wellness", "body_md": "Biblical Weight Loss content..."},
    "call_to_repentance": {"title": "The Call to Repentance", "body_md": "Message..."},
    "pastor_planners": {"title": "Pastor Planners", "body_md": "Organization..."},
    "nahenahe_voice": {"title": "The Nahenahe Voice", "body_md": "Music..."}
}

def load_content():
    # START with the order and pages we want
    current_data = {"order": ORDER, "pages": DEFAULT_PAGES}
    
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r") as f:
                saved = json.load(f)
                # This merges your 30+ existing pages back in
                current_data["pages"].update(saved.get("pages", {}))
        except: pass
    
    # Step 3: THE FIX - We re-insert the Myron Golden page into the dictionary 
    # even if the JSON file tried to overwrite it with "nothing."
    current_data["pages"]["kingdom_wealth"] = DEFAULT_PAGES["kingdom_wealth"]
    return current_data

@app.route("/")
@app.route("/<page_id>")
def serve(page_id="home"):
    data = load_content()
    
    # Admin Logic
    if page_id == "admin":
        curr = request.args.get("page", "home")
        return render_template_string(ADMIN_HTML, pages=data["pages"], current_page=curr, current_data=data["pages"].get(curr), style=ENHANCED_STYLE)
    
    page = data["pages"].get(page_id, data["pages"]["home"])
    nav = [{"title": s.replace("_", " ").upper(), "url": f"/{s}" if s != "home" else "/"} for s in ORDER]
    
    return render_template_string(MAIN_HTML, page=page, nav=nav, style=ENHANCED_STYLE, body_html=markdown.markdown(page.get("body_md", "")))

@app.route("/admin/save", methods=["POST"])
def admin_save():
    data = load_content()
    pid = request.form.get("page_id")
    if pid in data["pages"]:
        data["pages"][pid]["title"] = request.form.get("title")
        data["pages"][pid]["body_md"] = request.form.get("body_md")
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    return redirect(f"/admin?page={pid}")

MAIN_HTML = """
<!DOCTYPE html><html><head><style>{{ style|safe }}</style></head><body>
    <nav class="site-nav"><div class="nav-container">
        {% for item in nav %}<a href="{{ item.url }}">{{ item.title }}</a>{% endfor %}
        <a href="/admin" style="color:#d4a574;">ADMIN</a>
    </div></nav>
    <div class="container"><article class="content-card">
        <h1>{{ page.title }}</h1>
        <div>{{ body_html|safe }}</div>
        {% if page.product_url %}<center><a href="{{ page.product_url }}" class="buy-button">JOIN THE CHALLENGE</a></center>{% endif %}
    </article></div>
</body></html>
"""

ADMIN_HTML = """
<!DOCTYPE html><html><head><style>{{ style|safe }}</style></head><body>
<div class="container"><div class="content-card">
    <h1>Admin</h1>
    <form method="POST" action="/admin/save">
        <select name="page_id" onchange="window.location.href='/admin?page='+this.value">
            {% for pid in pages.keys() %}<option value="{{ pid }}" {% if pid == current_page %}selected{% endif %}>{{ pid }}</option>{% endfor %}
        </select>
        <input type="text" name="title" value="{{ current_data.title }}" style="width:100%; margin:10px 0; padding:10px;">
        <textarea name="body_md" style="width:100%; height:300px;">{{ current_data.body_md }}</textarea>
        <button type="submit" class="buy-button">SAVE CHANGES</button>
    </form>
</div></div></body></html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
