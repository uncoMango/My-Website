import os
from flask import Flask, request, redirect, render_template_string, abort, url_for
import json
from pathlib import Path
import markdown

app = Flask(__name__)

# --- 1. THE FOUNDATION ---
BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"
KEYWORDS = "Biblical weight loss, natural weight loss, Kingdom understanding of the bible, kingdom living vs religion, kingdom of god wealth, Myron Golden"

# --- 2. THE DESIGN (80% HERO + 70% CENTERED BOX) ---
STYLE = """
:root {
    --white-70: rgba(255, 255, 255, 0.7);
    --teal: #5f9ea0;
    --gold: #d4a574;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Georgia', serif;
    background-color: #f8f5f0;
    color: #2c3e50;
    margin: 0;
}
.site-nav { 
    background: white; 
    padding: 1.2rem; 
    text-align: center; 
    border-bottom: 2px solid var(--gold);
}
.site-nav a { 
    margin: 0 15px; 
    text-decoration: none; 
    color: #2c3e50; 
    font-weight: bold; 
    text-transform: uppercase;
}
.hero-viewport {
    width: 100%;
    min-height: 80vh; /* 80% OF THE PAGE */
    background-image: url('https://i.imgur.com/wmHEyDo.png');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    display: flex;
    justify-content: center;
    align-items: center;
}
.content-box {
    background: var(--white-70) !important; /* 70% TRANSPARENT */
    width: 90%;
    max-width: 800px;
    padding: 3rem;
    border-radius: 20px;
    border: 3px solid var(--gold);
    box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    backdrop-filter: blur(8px);
}
.buy-button {
    display: inline-block;
    background: var(--teal);
    color: white !important;
    padding: 1rem 2rem;
    border-radius: 10px;
    text-decoration: none;
    font-weight: bold;
    margin-top: 20px;
}
"""

# --- 3. DATABASE LOGIC ---
def get_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"pages": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# --- 4. THE EXPLICIT ROUTES ---

@app.route("/")
def home():
    data = get_data()
    content = data["pages"].get("home", {"title": "Ke Aupuni O Ke Akua", "body": "# Aloha\nWelcome to the Kingdom Embassy."})
    return render_page(content)

@app.route("/kingdom_wealth")
def kingdom_wealth():
    # WE HARD-CODE THIS PAGE DATA SO IT CANNOT BE MISSING
    content = {
        "title": "Kingdom Wealth & Stewardship",
        "body": "## Funding the 20-Volume Mandate\nI have aligned with **Myron Golden** and the 'Make More Offers Challenge' to provide the financial foundation for our mission.",
        "product_url": "https://www.makemoreofferschallenge.com/join?am_id=uncomango777"
    }
    return render_page(content)

@app.route("/aloha_wellness")
def aloha_wellness():
    data = get_data()
    content = data["pages"].get("aloha_wellness", {"title": "Aloha Wellness", "body": "Biblical Weight Loss..."})
    return render_page(content)

# --- 5. RENDER ENGINE ---
def render_page(content):
    body_html = markdown.markdown(content.get("body", ""))
    return render_template_string(HTML_TEMPLATE, content=content, body_html=body_html)

HTML_TEMPLATE = """
<!DOCTYPE html><html><head><style>{{ style|safe }}</style></head>
<body>
    <nav class="site-nav">
        <a href="/">HOME</a>
        <a href="/kingdom_wealth">KINGDOM WEALTH</a>
        <a href="/aloha_wellness">ALOHA WELLNESS</a>
        <a href="/admin" style="color:var(--gold);">ADMIN</a>
    </nav>
    <div class="hero-viewport">
        <div class="content-box">
            <h1>{{ content.title }}</h1>
            <div>{{ body_html|safe }}</div>
            {% if content.product_url %}
            <center><a href="{{ content.product_url }}" class="buy-button">JOIN THE CHALLENGE</a></center>
            {% endif %}
        </div>
    </div>
</body></html>
"""

# --- 6. ADMIN SYSTEM ---
@app.route("/admin")
def admin():
    data = get_data()
    return render_template_string(ADMIN_TEMPLATE, pages=data["pages"])

@app.route("/admin/save", methods=["POST"])
def admin_save():
    data = get_data()
    pid = request.form.get("page_id")
    data["pages"][pid] = {
        "title": request.form.get("title"),
        "body": request.form.get("body"),
        "product_url": request.form.get("product_url", "")
    }
    save_data(data)
    return redirect("/admin")

ADMIN_TEMPLATE = """
<!DOCTYPE html><html><body><h1>Admin Panel</h1>
<form method="POST" action="/admin/save">
    <input type="text" name="page_id" placeholder="page_id (e.g. home)">
    <input type="text" name="title" placeholder="Title">
    <input type="text" name="product_url" placeholder="Link">
    <textarea name="body" placeholder="Markdown body"></textarea>
    <button type="submit">SAVE PAGE</button>
</form>
</body></html>
"""

style_context = STYLE # Passing to template

@app.context_processor
def inject_style():
    return dict(style=STYLE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
