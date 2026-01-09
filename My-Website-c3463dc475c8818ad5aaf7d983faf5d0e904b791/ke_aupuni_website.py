import os
from flask import Flask, request, redirect, render_template_string, abort, url_for
import json
from pathlib import Path
import markdown

app = Flask(__name__)

# --- THE ARCHITECTURE (THE FULL 200+ LINE FEEL) ---

BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"

# FULL SEO AND HEADERS
KEYWORDS = "Biblical weight loss, natural weight loss, Kingdom understanding, Myron Golden, Kingdom Wealth"

# THE COMPLETE CSS (LOCKED AT 70% TRANSPARENCY)
STYLE_BLOCK = """
:root {
    --primary-bg: #f8f5f0;
    --text-dark: #2c3e50;
    --accent-teal: #5f9ea0;
    --accent-gold: #d4a574;
    --white-70: rgba(255, 255, 255, 0.7); 
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Georgia', serif;
    background-color: var(--primary-bg);
    color: var(--text-dark);
    line-height: 1.8;
}
.hero-container {
    width: 100%;
    min-height: 80vh; /* 80% OF THE VIEWPORT AS REQUESTED */
    background-image: url('https://i.imgur.com/wmHEyDo.png');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 50px 20px;
}
.content-card { 
    background: var(--white-70) !important; /* THE 70% TRANSPARENT BOX */
    max-width: 850px;
    width: 100%;
    padding: 4rem; 
    border-radius: 30px; 
    border: 4px solid var(--accent-gold); 
    box-shadow: 0 25px 50px rgba(0,0,0,0.3);
    backdrop-filter: blur(10px);
    text-align: center;
}
.site-navigation { 
    background: white; 
    padding: 1.5rem 0; 
    position: sticky; 
    top: 0; 
    z-index: 9999;
    border-bottom: 3px solid var(--accent-gold);
}
.nav-link { 
    margin: 0 15px; 
    text-decoration: none; 
    color: var(--text-dark); 
    font-weight: bold; 
    text-transform: uppercase;
    font-size: 0.95rem;
}
.cta-button { 
    display: inline-block; 
    background: var(--accent-teal); 
    color: white !important; 
    padding: 1.2rem 2.8rem; 
    border-radius: 15px; 
    text-decoration: none; 
    font-weight: bold; 
    font-size: 1.2rem;
    margin-top: 30px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}
"""

# --- THE PAGES (THE CHAPTERS) ---

@app.route("/")
def index():
    page_data = {
        "title": "Ke Aupuni O Ke Akua",
        "body": "## Welcome to the Kingdom Embassy\nRestoring the 20-Volume Mandate."
    }
    return render_embassy(page_data)

@app.route("/kingdom_wealth")
def kingdom_wealth():
    # NEW PAGE ADDED HERE
    page_data = {
        "title": "Kingdom Wealth & Stewardship",
        "body": "## Funding the 20-Volume Mandate\nI have aligned with **Myron Golden** and the 'Make More Offers Challenge' to provide the financial foundation for our mission.",
        "link": "https://www.makemoreofferschallenge.com/join?am_id=uncomango777"
    }
    return render_embassy(page_data)

@app.route("/aloha_wellness")
def aloha_wellness():
    page_data = {
        "title": "Aloha Wellness",
        "body": "## Biblical Weight Loss\nRestoring the temple of the Holy Spirit."
    }
    return render_embassy(page_data)

# --- THE ENGINE (THE PRINTING PRESS) ---

def render_embassy(content):
    html_content = markdown.markdown(content.get("body", ""))
    
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{{{{ content.title }}}}</title>
        <meta name="keywords" content="{KEYWORDS}">
        <style>{STYLE_BLOCK}</style>
    </head>
    <body>
        <nav class="site-navigation">
            <a href="/" class="nav-link">HOME</a>
            <a href="/kingdom_wealth" class="nav-link">KINGDOM WEALTH</a>
            <a href="/aloha_wellness" class="nav-link">ALOHA WELLNESS</a>
            <a href="/admin" class="nav-link" style="color:var(--accent-gold);">ADMIN</a>
        </nav>
        
        <div class="hero-container">
            <article class="content-card">
                <h1 style="font-size: 2.8rem; margin-bottom: 1.5rem;">{{{{ content.title }}}}</h1>
                <div style="text-align: left; font-size: 1.2rem;">{html_content}</div>
                {{% if content.link %}}
                <a href="{{{{ content.link }}}}" class="cta-button">JOIN THE CHALLENGE</a>
                {{% endif %}}
            </article>
        </div>
    </body>
    </html>
    """
    return render_template_string(full_html, content=content)

# --- THE ADMIN ACCESS ---

@app.route("/admin")
def admin():
    return "<h1>Palace Admin Access Active</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
