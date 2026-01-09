import os
from flask import Flask, request, redirect, render_template_string, abort, url_for
import json
from pathlib import Path
import markdown

app = Flask(__name__)

# --- SECTION 1: THE FOUNDATION ---
KEYWORDS = "Biblical weight loss, natural weight loss, Kingdom understanding of the bible, kingdom living vs religion, kingdom of god wealth, Myron Golden"

# --- SECTION 2: THE FULL REGALIA DESIGN (CSS) ---
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

.site-nav { 
    background: white; 
    padding: 1.5rem 0; 
    position: sticky; 
    top: 0; 
    z-index: 9999;
    border-bottom: 3px solid var(--accent-gold);
    text-align: center;
}

.site-nav a { 
    margin: 0 15px; 
    text-decoration: none; 
    color: var(--text-dark); 
    font-weight: bold; 
    text-transform: uppercase;
    letter-spacing: 1px;
}

.hero-stage {
    width: 100%;
    min-height: 80vh; 
    background-image: url('https://i.imgur.com/wmHEyDo.png');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 60px 20px;
}

.content-card { 
    background: var(--white-70) !important; 
    max-width: 900px;
    width: 100%;
    padding: 5rem 4rem; 
    border-radius: 40px; 
    border: 5px solid var(--accent-gold); 
    box-shadow: 0 30px 70px rgba(0,0,0,0.4);
    backdrop-filter: blur(12px);
    text-align: center;
}

.hero-title {
    font-size: 3.2rem;
    margin-bottom: 2rem;
    color: var(--text-dark);
}

.content-body {
    font-size: 1.3rem;
    text-align: left;
    margin-bottom: 2rem;
}

.cta-button { 
    display: inline-block; 
    background: var(--accent-teal); 
    color: white !important; 
    padding: 1.5rem 3.5rem; 
    border-radius: 20px; 
    text-decoration: none; 
    font-weight: bold; 
    font-size: 1.4rem;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}
"""

# --- SECTION 3: THE PERMANENT PAGES ---

@app.route("/")
def home_page():
    content = {
        "title": "Ke Aupuni O Ke Akua",
        "body_md": "## Aloha and Welcome\\nWelcome to the Kingdom Embassy. We are here to fulfill the 20-Volume Mandate.",
        "link": ""
    }
    return render_embassy(content)

@app.route("/the_mandate")
def the_mandate_page():
    content = {
        "title": "The 20-Volume Mandate",
        "body_md": "## The Mandate Content\\nDetails about the mission go here.",
        "link": ""
    }
    return render_embassy(content)

@app.route("/kingdom_wealth")
def kingdom_wealth_page():
    content = {
        "title": "Kingdom Wealth",
        "body_md": "## Stewardship\\nFunding the mandate through Kingdom principles.",
        "link": "https://www.makemoreofferschallenge.com/join?am_id=uncomango777"
    }
    return render_embassy(content)

@app.route("/aloha_wellness")
def aloha_wellness_page():
    content = {
        "title": "Aloha Wellness",
        "body_md": "## Biblical Weight Loss\\nRestoring the Temple.",
        "link": ""
    }
    return render_embassy(content)

# --- SECTION 4: THE MASTER RENDERER ---

def render_embassy(content):
    html_body = markdown.markdown(content.get("body_md", ""))
    
    # I have checked this HTML block specifically to ensure the links are correct
    full_page = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{{{{ content.title }}}}</title>
        <meta name="keywords" content="{KEYWORDS}">
        <style>{STYLE_BLOCK}</style>
    </head>
    <body>
        <nav class="site-nav">
            <a href="/">HOME</a>
            <a href="/the_mandate">THE MANDATE</a>
            <a href="/kingdom_wealth">KINGDOM WEALTH</a>
            <a href="/aloha_wellness">ALOHA WELLNESS</a>
            <a href="/admin">ADMIN</a>
        </nav>
        
        <div class="hero-stage">
            <article class="content-card">
                <h1 class="hero-title">{{{{ content.title }}}}</h1>
                <div class="content-body">{html_body}</div>
                {{% if content.link %}}
                <center><a href="{{{{ content.link }}}}" class="cta-button">JOIN THE CHALLENGE NOW</a></center>
                {{% endif %}}
            </article>
        </div>
    </body>
    </html>
    """
    return render_template_string(full_page, content=content)

# --- SECTION 5: THE ADMIN GATE ---

@app.route("/admin")
def admin_portal():
    return "<h1>Admin Portal Active</h1><p>You can add more hard-coded routes to the script to expand your Tabernacle.</p>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
