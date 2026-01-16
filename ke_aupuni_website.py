# ke_aupuni_finalized_with_image_placeholders.py
from flask import Flask, request, redirect, render_template_string, abort, url_for, send_file
import json
from pathlib import Path
import markdown
import os

app = Flask(__name__)

ORDER = ["home", "kingdom_wealth", "call_to_repentance", "aloha_wellness", "pastor_planners", "nahenahe_voice"]

BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"

DEFAULT_PAGES = {
    "order": ORDER,
    "pages": {
        "home": {
            "title": "Ke Aupuni O Ke Akua - The Kingdom of God",
            "hero_image": "https://i.imgur.com/wmHEyDo.png",
            "body_md": "## Welcome to Ke Aupuni O Ke Akua - The Kingdom of God\r\n\r\nMahalo for visiting. This site is dedicated to rediscovering the revolutionary Kingdom message that Jesus actually preached.\r\n\r\n### Our Mission: Kingdom, Not Religion\r\nJesus's central focus was the Kingdom of God. Our resources aim to guide you into a deeper understanding of Kingdom principles.\r\n\r\n**[Download FREE Kingdom Keys →](/kingdom_keys)**",
            "product_url": "https://amzn.to/3FfH9ep"
        },
        "kingdom_wealth": {
            "title": "Kingdom Wealth",
            "hero_image": "https://i.imgur.com/G2YmSka.jpeg",
            "body_md": "## Biblical Stewardship & Economic Increase\r\n\r\nThe Kingdom of God operates on a system of stewardship, not ownership. \r\n\r\n**[Explore Kingdom Wealth Principles →](/kingdom_wealth)**",
            "product_url": ""
        },
        "aloha_wellness": {
            "title": "Aloha Wellness - Island Health & Healing",
            "hero_image": "https://i.imgur.com/xGeWW3Q.jpeg",
            "body_md": "## Aloha Wellness - The Sacred Art of How You Eat\r\n\r\nDiscover the life-changing power of **how** you eat, not just what you eat.\r\n\r\n**[Discover Kingdom Living Principles →](/kingdom_wealth)**",
            "products": [{"title": "Aloha Wellness Book", "cover": "https://m.media-amazon.com/images/I/712tO3wmGEL._SL1499_.jpg", "amazon": "", "gumroad": ""}]
        },
        "call_to_repentance": {
            "title": "The Call to Repentance - The Kingdom Series",
            "hero_image": "https://i.imgur.com/tG1vBp9.jpeg",
            "body_md": "## The Call to Repentance\r\n\r\nStep beyond religious tradition and rediscover the revolutionary Kingdom message.\r\n\r\n**[Get Free Kingdom Keys →](/kingdom_keys)**",
            "products": [{"title": "The Call to Repentance - Kingdom Book", "cover": "", "amazon": "", "gumroad": "https://uncomango.gumroad.com/l/myold"}]
        },
        "pastor_planners": {
            "title": "Pastor Planners",
            "hero_image": "https://i.imgur.com/tWnn5UY.png",
            "body_md": "## Organize Your Ministry with Purpose\r\n\r\nEffective ministry requires both spiritual sensitivity and practical organization.\r\n\r\n**[Get Free Kingdom Keys →](/kingdom_keys)**",
            "products": [
                {"title": "Hawaiian Pastor Planner", "cover": "https://public-files.gumroad.com/p4346cgzkcd4iivhsgkf7pjtypr2", "amazon": "", "gumroad": ""},
                {"title": "Samoan Pastor Planner", "cover": "https://public-files.gumroad.com/worm4zkkn4hm5k0f81icc4e4pofp", "amazon": "", "gumroad": ""}
            ]
        },
        "nahenahe_voice": {
            "title": "The Nahenahe Voice",
            "hero_image": "https://i.imgur.com/Vyz6nFJ.png",
            "body_md": "## Live from Molokai Ranch Lodge\r\n\r\nExperience the soul-stirring sounds of authentic Hawaiian music captured live in 2000.",
            "gallery_images": ["/static/covers/cover1.jpg", "/static/covers/cover2.jpg", "/static/covers/cover3.jpg"],
            "product_links": [{"name": "Amazon Music", "url": "https://music.amazon.com/search/nahenahe%20voice", "icon": "🛒"}]
        },
        "kingdom_keys": {
            "title": "FREE Kingdom Keys Booklets",
            "hero_image": "https://i.imgur.com/wmHEyDo.png",
            "body_md": "## 🌺 FREE Kingdom Keys Booklets 🌺\r\n\r\nDownload these FREE mini-devotionals that will transform how you see Jesus's message.",
            "products": [{"title": "7 Scriptures of the Kingdom", "cover": "", "amazon": "", "gumroad": ""}]
        }
    }
}

ENHANCED_STYLE = """
:root {
    --primary-bg: #fdfbf7;
    --text-dark: #2c3e50;
    --accent-gold: #d4af37; 
    --accent-gold-hover: #f5d76e;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Georgia', serif; background: var(--primary-bg); color: var(--text-dark); }
/* FIXED GOLD LINKS */
a { color: var(--accent-gold) !important; text-decoration: none; font-weight: bold; }
a:hover { color: var(--accent-gold-hover) !important; }
.site-nav { background: white; padding: 1rem; position: sticky; top: 0; z-index: 1000; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.nav-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
.nav-logo { height: 50px; margin-right: 12px; }
.nav-title { font-size: 1.4rem; font-weight: bold; display: flex; align-items: center; }
.nav-menu { display: flex; list-style: none; gap: 1rem; }
.nav-menu a { color: var(--text-dark) !important; }
.hero { height: 50vh; background-size: cover; background-position: center; position: relative; display: flex; align-items: center; justify-content: center; }
.hero-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.4); }
.hero-content { position: relative; z-index: 2; color: white; text-align: center; }
/* FIXED HERO VISIBILITY */
.container { max-width: 960px; margin: -50px auto 50px; position: relative; z-index: 10; padding: 0 20px; }
.content-card { background: white; padding: 3rem; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
.wealth-glow { border: 3px solid var(--accent-gold); box-shadow: 0 0 20px rgba(212, 175, 55, 0.3); }
.footer { text-align: center; padding: 3rem; color: #95a5a6; }
"""

def md_to_html(md_text):
    return markdown.markdown(md_text, extensions=["extra", "nl2br"])

def load_content():
    return DEFAULT_PAGES

def render_page(page_id, data):
    page = data["pages"][page_id]
    nav_items = [{"slug": s, "title": data["pages"][s]["title"], "url": f"/{s}" if s != "home" else "/"} for s in data["order"]]
    return render_template_string(PAGE_TEMPLATE, page=page, nav_items=nav_items, style=ENHANCED_STYLE, body_html=md_to_html(page.get("body_md", "")))

PAGE_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>{{ page.title }}</title>
    <style>{{ style|safe }}</style>
</head>
<body>
    <nav class="site-nav">
        <div class="nav-container">
            <a href="/" class="nav-title">
                <img src="https://keaupuniakeakua.faith/output-onlinepngtools.png" alt="Logo" class="nav-logo">
                Ke Aupuni O Ke Akua
            </a>
            <ul class="nav-menu">
                {% for item in nav_items %}<li><a href="{{ item.url }}">{{ item.title[:15] }}...</a></li>{% endfor %}
            </ul>
        </div>
    </nav>
    <header class="hero" style="background-image: url('{{ page.hero_image }}');">
        <div class="hero-overlay"></div>
        <div class="hero-content"><h1>{{ page.title }}</h1></div>
    </header>
    <main class="container">
        <article class="content-card {% if 'Wealth' in page.title %}wealth-glow{% endif %}">
            {{ body_html|safe }}
            {% if page.products %}
            <div style="margin-top:2rem; display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                {% for p in page.products %}
                <div style="border:1px solid #eee; padding:15px; border-radius:8px;">
                    <img src="{{ p.cover }}" style="width:100%;">
                    <h4>{{ p.title }}</h4>
                    <a href="{{ p.gumroad }}" style="background:gold; padding:5px; display:block; text-align:center;">Get Now</a>
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </article>
    </main>
    <footer class="footer"><p>© 2026 Ke Aupuni O Ke Akua</p></footer>
</body>
</html>"""

@app.route("/")
def home():
    return render_page("home", load_content())

@app.route("/<page_id>")
def page(page_id):
    return render_page(page_id, load_content())

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
