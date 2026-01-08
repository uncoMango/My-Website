import os
from flask import Flask, request, redirect, render_template_string, abort, url_for
import json
from pathlib import Path
import markdown

app = Flask(__name__)

# --- THE MANDATE ---
KEYWORDS = "Biblical weight loss, natural weight loss, Kingdom understanding of the bible, kingdom living vs religion, kingdom of god wealth"
# Ensure 'kingdom_wealth' is explicitly in this list
ORDER = ["home", "kingdom_wealth", "aloha_wellness", "call_to_repentance", "pastor_planners", "nahenahe_voice"]

BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"

# --- THE DESIGN (70% Transparency) ---
ENHANCED_STYLE = """
:root {
    --primary-bg: #f8f5f0;
    --text-dark: #2c3e50;
    --accent-teal: #5f9ea0;
    --accent-warm: #d4a574;
    --white-70: rgba(255, 255, 255, 0.7); 
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Georgia', serif;
    background-image: url('https://i.imgur.com/wmHEyDo.png');
    background-attachment: fixed;
    background-size: cover;
}
.site-nav { background: rgba(255, 255, 255, 0.85); padding: 1.5rem 0; position: sticky; top: 0; z-index: 1000; }
.nav-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 0 2rem; }
.nav-menu { display: flex; list-style: none; gap: 1.5rem; }
.nav-menu a { text-decoration: none; color: var(--text-dark); font-weight: 600; padding: 0.5rem 1rem; }
.container { max-width: 900px; margin: 50px auto; padding: 0 20px; }
.content-card { 
    background: var(--white-70) !important; 
    padding: 3rem; 
    border-radius: 20px; 
    border: 2px solid var(--accent-warm); 
    backdrop-filter: blur(5px);
}
.buy-button { 
    display: inline-block; 
    background: var(--accent-teal); 
    color: white !important; 
    padding: 1.2rem 2.5rem; 
    border-radius: 10px; 
    text-decoration: none; 
    font-weight: bold; 
}
"""

DEFAULT_PAGES = {
    "home": {"title": "Ke Aupuni O Ke Akua", "body_md": "Welcome to the Embassy.", "product_url": ""},
    "kingdom_wealth": {
        "title": "Kingdom Wealth & Stewardship",
        "body_md": "## Funding the 20-Volume Mandate\\nI have aligned with **Myron Golden** for the financial foundation of this mission.",
        "product_url": "https://www.makemoreofferschallenge.com/join?am_id=uncomango777"
    },
    "aloha_wellness": {"title": "Aloha Wellness: Biblical Weight Loss", "body_md": "Healing through Kingdom principles.", "product_url": ""}
}

def load_content():
    # If the file exists, we load it, but then we FORCE the new page in
    data = {"order": ORDER, "pages": DEFAULT_PAGES}
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except: pass
    
    # FORCE INJECTION: This ensures Myron Golden shows up even if the JSON is old
    if "kingdom_wealth" not in data["pages"]:
        data["pages"]["kingdom_wealth"] = DEFAULT_PAGES["kingdom_wealth"]
    
    # Ensure the order is updated to include the wealth page
    if "kingdom_wealth" not in data.get("order", []):
        data["order"] = ORDER
        
    return data

@app.route("/")
@app.route("/<page_id>")
def serve_site(page_id="home"):
    data = load_content()
    page = data["pages"].get(page_id, data["pages"]["home"])
    nav = [{"title": s.replace("_", " ").upper(), "url": f"/{s}" if s != "home" else "/"} for s in data["order"]]
    
    # HTML Rendering
    TEMPLATE = """
    <!DOCTYPE html><html><head><title>{{ page.title }}</title><meta name="keywords" content="{{ keywords }}"><style>{{ style|safe }}</style></head>
    <body>
        <nav class="site-nav"><div class="nav-container">
            <a href="/" style="text-decoration:none; color:#5f9ea0; font-weight:bold;">KE AUPUNI</a>
            <ul class="nav-menu">
                {% for item in nav %}<li><a href="{{ item.url }}">{{ item.title }}</a></li>{% endfor %}
            </ul>
        </div></nav>
        <div class="container"><article class="content-card">
            <h1>{{ page.title }}</h1>
            <div>{{ body_html|safe }}</div>
            {% if page.product_url %}<center><a href="{{ page.product_url }}" class="buy-button">JOIN THE CHALLENGE NOW</a></center>{% endif %}
        </article></div>
    </body></html>
    """
    return render_template_string(TEMPLATE, page=page, nav=nav, style=ENHANCED_STYLE, body_html=markdown.markdown(page["body_md"]), keywords=KEYWORDS)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
