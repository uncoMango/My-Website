from flask import Flask, render_template_string
import markdown
import os

app = Flask(__name__)

# --- HARD-CODED KINGDOM STYLE (Bypassing JSON issues) ---
CSS = """
:root { --bg: #f8f5f0; --text: #2c3e50; --teal: #5f9ea0; --brown: #8d6e63; --gold: #d4a574; }
body { 
    font-family: 'Georgia', serif; background-color: var(--bg);
    background-image: url('https://i.imgur.com/wmHEyDo.png'); 
    background-attachment: fixed; background-size: cover; margin: 0;
}
.site-nav { background: #d4b896; padding: 1.2rem; border-bottom: 4px solid var(--brown); }
.nav-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
.nav-menu { display: flex; list-style: none; gap: 1.5rem; margin: 0; padding: 0; }
.nav-menu a { text-decoration: none; color: var(--text); font-weight: bold; padding: 0.5rem 1rem; border-radius: 5px; }
.nav-menu a:hover { background: var(--teal); color: white; }
.container { max-width: 900px; margin: 40px auto; padding: 0 20px; }
.content-card { background: rgba(255, 255, 255, 0.95); padding: 3rem; border-radius: 20px; border: 2px solid var(--brown); box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
h1 { color: var(--brown); font-size: 2.5rem; }
.hero-img { width: 100%; border-radius: 10px; margin-bottom: 20px; border: 1px solid var(--brown); }
.buy-button { display: inline-block; background: linear-gradient(135deg, var(--teal), #4682b4); color: white !important; padding: 1.2rem 2.5rem; border-radius: 10px; text-decoration: none; font-weight: bold; margin-top: 20px; }
"""

# --- PAGE DATA ---
PAGES = {
    "home": {
        "title": "Ke Aupuni O Ke Akua",
        "hero": "https://i.imgur.com/wmHEyDo.png",
        "content": "## Rediscovering the Kingdom\nWelcome to the Embassy. We are transitioning from 108 volumes to a refined 20-volume mandate."
    },
    "myron_golden": {
        "title": "Kingdom Wealth & Stewardship",
        "hero": "https://i.imgur.com/wmHEyDo.png",
        "content": "## Funding the Mission\nI have aligned with **Myron Golden** to provide the financial foundation for our 20-volume series.",
        "link": "YOUR_MYRON_GOLDEN_LINK_HERE"
    }
}

HTML_TEMPLATE = """
<!DOCTYPE html><html><head><style>{{ css|safe }}</style></head>
<body>
    <nav class="site-nav"><div class="nav-container"><strong>Ke Aupuni</strong>
    <ul class="nav-menu">
        <li><a href="/">Home</a></li>
        <li><a href="/myron_golden">Kingdom Wealth</a></li>
    </ul></div></nav>
    <div class="container"><article class="content-card">
        <img src="{{ page.hero }}" class="hero-img">
        <h1>{{ page.title }}</h1>
        <div>{{ body|safe }}</div>
        {% if page.link %}<center><a href="{{ page.link }}" class="buy-button">JOIN THE CHALLENGE</a></center>{% endif %}
    </article></div>
</body></html>"""

@app.route("/")
def home():
    page = PAGES["home"]
    return render_template_string(HTML_TEMPLATE, css=CSS, page=page, body=markdown.markdown(page["content"]))

@app.route("/<page_id>")
def show_page(page_id):
    page = PAGES.get(page_id, PAGES["home"])
    return render_template_string(HTML_TEMPLATE, css=CSS, page=page, body=markdown.markdown(page["content"]))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
