# ke_aupuni_website.py - FINAL CORRECTED VERSION
# Kahu Phil's CORRECT content + Mobile Responsive + Working Admin + Multi-Link/Multi-Volume Support

from flask import Flask, request, redirect, render_template_string, abort, url_for, send_file
import json
from pathlib import Path
import markdown
import os
import re

app = Flask(__name__)

# Page order for navigation
ORDER = ["home", "aloha_wellness", "call_to_repentance", "pastor_planners", "nahenahe_voice"]

# Data storage
BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"

# KAHU PHIL'S ACTUAL CONTENT - Kingdom Message, No Mythology!
# NOTE: product_url is replaced by the more flexible 'buy_links' list.
DEFAULT_PAGES = {
    "order": [
        "home",
        "aloha_wellness",
        "call_to_repentance",
        "pastor_planners",
        "nahenahe_voice"
    ],
    "pages": {
        "home": {
            "title": "Ke Aupuni O Ke Akua - The Kingdom of God",
            "hero_image": "https://i.imgur.com/wmHEyDo.png",
            "intro_text": "## The Call to Repentance - Rediscovering Jesus's Kingdom Message",
            "body_md": "Step beyond religious tradition and rediscover the revolutionary Kingdom message that Jesus actually preached. This transformative book series cuts through centuries of religious interpretation to reveal the pure, life-changing teachings of the Kingdom of God.\r\n\r\n### Jesus Preached Kingdom, Not Religion\r\n\r\nFor too long, the church has focused on getting people into heaven instead of bringing heaven to earth. Jesus's primary message wasn't about religion, denominations, or institutional Christianity - it was about the Kingdom of God breaking into human reality here and now.\r\n\r\n**A Comprehensive Series** - This multi-volume series systematically unpacks Jesus's kingdom teachings. **Visit the Call to Repentance page** to see all volumes and discover how to live a life transformed by the Kingdom of God.\r\n\r\n*\"Repent, for the kingdom of heaven has come near.\" - Matthew 4:17*",
            "buy_links": [
                {"name": "Amazon", "url": "https://amzn.to/3FfH9ep", "icon": "🛒"},
                {"name": "Gumroad", "url": "https://gumroad.com/your-series-link", "icon": "📚"} # Example Gumroad link
            ]
        },
        "aloha_wellness": {
            "title": "Aloha Wellness - Island Health & Healing",
            "hero_image": "https://i.imgur.com/xGeWW3Q.jpeg",
            "intro_text": "## Aloha Wellness - The Sacred Art of How You Eat",
            "body_md": "Discover the life-changing power of **how** you eat, not just what you eat. This groundbreaking wellness book combines cutting-edge scientific research with ancient Hawaiian mana'o (wisdom) to transform your relationship with food and nourishment.\r\n\r\n### Beyond Diet Culture - A Hawaiian Perspective\r\n\r\nTraditional Hawaiian culture understood something modern society has forgotten: eating is a sacred act that connects us to the land, our ancestors, and our own spiritual well-being. This book bridges that ancient wisdom with contemporary nutritional science.",
            "buy_links": [
                {"name": "Amazon", "url": "https://amzn.to/3FfH9ep", "icon": "🛒"}
            ]
        },
        "call_to_repentance": {
            "title": "The Call to Repentance - Foundation for Kingdom Living",
            "hero_image": "https://i.imgur.com/tG1vBp9.jpeg",
            "intro_text": "## The Multi-Volume Series: Embracing True Repentance for Spiritual Growth",
            "body_md": "Repentance is not merely feeling sorry for our mistakes - it is a complete transformation of heart and mind that leads us into the fullness of Kingdom living.\r\n\r\n**This multi-volume series systematically unpacks the depth of Kingdom living through true repentance. Click on each volume below for its specific description and purchase links.**",
            # This 'volumes' array is the new structured way to manage the series books.
            "volumes": [
                {
                    "title": "Volume 1: The Foundation",
                    "body_md": "Understanding what the Kingdom of God actually is and why Jesus made it His central message. This volume provides the spiritual and biblical groundwork for the entire series.",
                    "buy_links": [
                        {"name": "Amazon", "url": "https://www.amazon.com/CALL-REPENTANCE-Foundation-Application-Lifestyle-ebook/dp/B0FXYDD9SN", "icon": "🛒"},
                        {"name": "Gumroad", "url": "https://gumroad.com/link-v1", "icon": "📚"} # Example Gumroad link for Volume 1
                    ]
                },
                {
                    "title": "Volume 2: Kingdom Citizenship",
                    "body_md": "What it means to be a citizen of God's kingdom while living in earthly systems. Discover the rights and responsibilities of a Kingdom citizen.",
                    "buy_links": [
                        {"name": "Amazon", "url": "https://www.amazon.com/CALL-REPENTANCE-Vol-2/dp/B0FXYSQJ4P", "icon": "🛒"},
                        {"name": "Gumroad", "url": "https://gumroad.com/link-v2", "icon": "📚"}
                    ]
                }
                # When you add Volume 6, you will add a new block here in the admin.
            ]
        },
        "pastor_planners": {
            "title": "Pastor Planners - Tools for Ministry Excellence",
            "hero_image": "https://i.imgur.com/tWnn5UY.png",
            "intro_text": "## Organize Your Ministry with Purpose and Prayer",
            "body_md": "Effective ministry requires both spiritual sensitivity and practical organization. Our Pastor Planners combine beautiful design with functional tools to help you lead with excellence and peace.",
            "buy_links": [
                {"name": "Amazon", "url": "https://www.amazon.com/s?k=pastor+planner+ministry+organizer", "icon": "🛒"}
            ]
        },
        "nahenahe_voice": {
            "title": "The Nahenahe Voice of Nahono'opi'ilani - Musical Legacy",
            "hero_image": "https://i.imgur.com/Vyz6nFJ.png",
            "intro_text": "## The Nahenahe Voice of Nahono'opi'ilani - Live from Molokai Ranch Lodge",
            "body_md": "Experience the soul-stirring sounds of authentic Hawaiian music captured live at the historic Molokai Ranch Lodge in the year 2000. This intimate recording showcases the true meaning of **nahenahe** - the gentle, soothing voice that carries the spirit of aloha across the islands.",
            "gallery_images": [
                "/static/covers/cover1.jpg",
                "/static/covers/cover2.jpg",
                "/static/covers/cover3.jpg"
            ],
            # Reusing 'buy_links' for music platforms since they are functionally the same as book links
            "buy_links": [
                {
                    "name": "Amazon Music",
                    "url": "https://music.amazon.com/search/nahenahe%20voice",
                    "icon": "🛒"
                },
                {
                    "name": "Apple Music",
                    "url": "https://music.apple.com/us/search?term=nahenahe%20voice",
                    "icon": "🍎"
                },
                {
                    "name": "Spotify",
                    "url": "https://open.spotify.com/search/nahenahe%20voice",
                    "icon": "🎧"
                }
            ]
        }
    }
}

# Enhanced CSS with Mobile Hamburger Menu - UPDATED WITH LAUHALA NAV
ENHANCED_STYLE = """
:root {
    --primary-bg: #f8f5f0;
    --text-dark: #2c3e50;
    --accent-teal: #5f9ea0;
    --accent-warm: #d4a574;
    --white-transparent: rgba(255, 255, 255, 0.95);
    --shadow-soft: 0 2px 10px rgba(0,0,0,0.1);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'Georgia', 'Times New Roman', serif;
    line-height: 1.6;
    color: var(--text-dark);
    background: var(--primary-bg);
    background-image: 
        radial-gradient(circle at 20% 50%, rgba(175, 216, 248, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(212, 165, 116, 0.1) 0%, transparent 50%);
}

/* UPDATED: Lauhala mat woven pattern navigation */
.site-nav {
    background-color: #d4b896;
    background-image: 
        linear-gradient(45deg, #c9a876 25%, transparent 25%),
        linear-gradient(-45deg, #c9a876 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, #bfa068 75%),
        linear-gradient(-45deg, transparent 75%, #bfa068 75%);
    background-size: 16px 16px;
    background-position: 0 0, 0 8px, 8px -8px, -8px 0px;
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: var(--shadow-soft);
}

.nav-container {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
}

/* UPDATED: Darker title for visibility on lauhala */
.nav-title {
    font-size: 1.5rem;
    font-weight: bold;
    color: #2c3e50;
    text-decoration: none;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
}

/* Desktop Menu */
.nav-menu {
    display: flex;
    list-style: none;
    gap: 2rem;
}

.nav-menu a {
    text-decoration: none;
    color: var(--text-dark);
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    transition: all 0.3s ease;
}

.nav-menu a:hover {
    background: var(--accent-teal);
    color: white;
}

/* Hamburger Menu */
.hamburger {
    display: none;
    flex-direction: column;
    cursor: pointer;
    padding: 0.5rem;
}

/* UPDATED: Darker hamburger lines for visibility on lauhala */
.hamburger span {
    width: 25px;
    height: 3px;
    background: #2c3e50;
    margin: 3px 0;
    transition: 0.3s;
}

.hero {
    height: 100vh;
    min-height: 600px;
    background-size: cover;
    background-position: center;
    position: relative;
    display: flex;
    align-items: flex-end;
}

.hero-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(0deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 50%, rgba(0,0,0,0.1) 100%);
}

.hero-content {
    position: relative;
    z-index: 2;
    color: white;
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
}

.hero h1 {
    font-size: 3rem;
    font-weight: 400;
    text-shadow: 0 2px 8px rgba(0,0,0,0.8);
    margin-bottom: 0.5rem;
    background: rgba(0,0,0,0.3);
    padding: 1rem 2rem;
    border-radius: 8px;
}

.container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    height: 100vh;
    overflow-y: auto;
    z-index: 3;
}

.content-card {
    background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)),
                repeating-linear-gradient(90deg, 
                    rgba(210, 180, 140, 0.3) 0px,
                    rgba(210, 180, 140, 0.3) 2px,
                    rgba(139, 90, 43, 0.2) 2px,
                    rgba(139, 90, 43, 0.2) 4px);
    border: none;
    padding: 3rem 2rem;
    box-shadow: none;
    margin-top: 20vh;
    color: white;
}

.content-card h2 {
    color: white;
    margin-bottom: 1rem;
    font-size: 2.2rem;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.9);
}

.content-card h3 {
    color: white;
    margin: 2rem 0 1rem;
    font-size: 1.6rem;
    text-shadow: 2px 2px 5px rgba(0,0,0,0.8);
}

.content-card p {
    margin-bottom: 1.5rem;
    font-size: 1.1rem;
    color: white;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.7);
    line-height: 1.8;
}

.content-card strong {
    color: white;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
}

.content-card li {
    color: white;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.7);
    line-height: 1.8;
}

.volume-card {
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 12px;
    padding: 2rem;
    margin-top: 2rem;
    background: rgba(0, 0, 0, 0.5); /* Slightly lighter background for separation */
}

.volume-card h3 {
    margin-top: 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

.buy-section {
    text-align: center;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(255, 255, 255, 0.3);
}

/* Updated button class to be more generic */
.buy-button {
    display: inline-block;
    background: linear-gradient(135deg, var(--accent-teal), #4a8b8e);
    color: white;
    padding: 1rem 2rem;
    border-radius: 8px;
    text-decoration: none;
    font-weight: bold;
    font-size: 1.1rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(95, 158, 160, 0.3);
    margin: 0.5rem;
}

.buy-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(95, 158, 160, 0.4);
}

.button-group {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 1rem;
    margin-top: 1.5rem;
}


/* CD Cover Gallery */
.gallery-section {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(255, 255, 255, 0.3);
}

.gallery-section h2 {
    color: white;
    text-align: center;
    margin-bottom: 1.5rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.9);
}

.gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.gallery-item {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.gallery-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.7);
}

.gallery-item img {
    width: 100%;
    height: auto;
    display: block;
}

@media (max-width: 768px) {
    .gallery-grid {
        grid-template-columns: 1fr;
    }
}


.footer {
    text-align: center;
    padding: 2rem;
    color: white;
    background: none;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    margin-top: 2rem;
}

/* Mobile Styles */
@media (max-width: 768px) {
    .hamburger {
        display: flex;
    }
    
    /* UPDATED: Lauhala pattern for mobile dropdown menu */
    .nav-menu {
        display: none;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background-color: #d4b896;
        background-image: 
            linear-gradient(45deg, #c9a876 25%, transparent 25%),
            linear-gradient(-45deg, #c9a876 25%, transparent 25%),
            linear-gradient(45deg, transparent 75%, #bfa068 75%),
            linear-gradient(-45deg, transparent 75%, #bfa068 75%);
        background-size: 16px 16px;
        background-position: 0 0, 0 8px, 8px -8px, -8px 0px;
        flex-direction: column;
        gap: 0;
        padding: 1rem 0;
        box-shadow: var(--shadow-soft);
    }
    
    .nav-menu.active {
        display: flex;
    }
    
    .nav-menu a {
        padding: 1rem 2rem;
        border-radius: 0;
    }
    
    .nav-container {
        padding: 0 1rem;
    }
    
    .hero {
        height: 45vh;
        min-height: 300px;
    }
    
    .hero h1 {
        font-size: 1.8rem;
        padding: 0.75rem 1.5rem;
    }
    
    .container {
        position: relative;
        height: auto;
        margin-top: 0;
        padding: 0 1rem 2rem;
        transform: none;
        left: 0;
    }
    
    .content-card {
        padding: 2rem 1.5rem;
    }
    
    .content-card h2 {
        font-size: 1.8rem;
    }
    
    .content-card h3 {
        font-size: 1.4rem;
    }
    
    .button-group {
        flex-direction: column;
    }
    
    .buy-button {
        width: 100%;
    }
}
"""

# The CSS for the Admin Panel is kept separate and will be correctly embedded.
ADMIN_CSS = """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        h1 {
            color: #2c3e50;
            margin-bottom: 0.5rem;
            font-size: 2rem;
        }
        
        .subtitle {
            color: #7f8c8d;
            margin-bottom: 2rem;
            font-size: 1rem;
        }
        
        .page-list {
            display: grid;
            gap: 1.5rem;
        }
        
        .page-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 12px;
            border: 2px solid #e9ecef;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .page-card:hover {
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        }
        
        .page-title {
            font-size: 1.25rem;
            color: #2c3e50;
            margin-bottom: 1rem;
            font-weight: 600;
        }
        
        .page-info {
            display: grid;
            gap: 0.5rem;
            margin-bottom: 1rem;
            font-size: 0.9rem;
            color: #495057;
        }
        
        .page-info strong {
            color: #2c3e50;
            font-weight: 600;
        }
        
        .edit-btn, .add-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            text-decoration: none;
            display: inline-block;
            margin-right: 1rem;
        }
        
        .add-btn {
            background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%);
            margin-bottom: 2rem;
        }
        
        .edit-btn:hover, .add-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        
        .back-btn {
            background: #6c757d;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            text-decoration: none;
            display: inline-block;
            margin-top: 2rem;
        }
        
        .back-btn:hover {
            background: #5a6268;
        }
        
        .delete-btn {
            background: #dc3545;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.9rem;
            position: absolute;
            top: 1.5rem;
            right: 1.5rem;
            transition: background 0.2s;
        }
        .delete-btn:hover {
            background: #c82333;
        }
        
        .gallery-preview {
            display: flex;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }
        
        .gallery-preview img {
            width: 60px;
            height: 60px;
            object-fit: cover;
            border-radius: 4px;
            border: 2px solid #dee2e6;
        }
"""

def md_to_html(md_text):
    """Convert markdown to HTML"""
    return markdown.markdown(md_text, extensions=["extra", "nl2br"])

def load_content():
    """Load content from JSON file or create default"""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            # If JSON is corrupt, fall back to default
            print("ERROR: Corrupt JSON file detected. Using default content.")
            data = DEFAULT_PAGES
            save_content(data)
    else:
        # If file doesn't exist, create it with default content
        data = DEFAULT_PAGES
        save_content(data)
    
    # Ensure all pages have 'intro_text' and 'volumes' for template rendering safety
    for page_id in data.get("pages", {}):
        if "intro_text" not in data["pages"][page_id]:
            data["pages"][page_id]["intro_text"] = ""
        # Convert old product_url (if it exists) to the new buy_links format for safety
        if "product_url" in data["pages"][page_id] and not data["pages"][page_id].get("buy_links"):
             data["pages"][page_id]["buy_links"] = [{"name": "Amazon", "url": data["pages"][page_id]["product_url"], "icon": "🛒"}]
             del data["pages"][page_id]["product_url"]
        
        # Ensure volumes list exists for series page if needed
        if page_id == "call_to_repentance" and "volumes" not in data["pages"][page_id]:
             data["pages"][page_id]["volumes"] = []

    return data

def save_content(data):
    """Save content to JSON file"""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def render_page(page_id, data):
    """Render a complete page"""
    pages = data.get("pages", data)
    if page_id not in pages:
        abort(404)
    
    page = pages[page_id]
    
    nav_items = []
    page_order = data.get("order", ORDER)
    for slug in page_order:
        if slug in pages:
            nav_items.append({
                "slug": slug,
                "title": pages[slug].get("title", slug.replace("_", " ").title()),
                "url": f"/{slug}" if slug != "home" else "/"
            })
    
    return render_template_string(PAGE_TEMPLATE, 
        page=page,
        nav_items=nav_items,
        style=ENHANCED_STYLE,
        intro_html=md_to_html(page.get("intro_text", "")),
        body_html=md_to_html(page.get("body_md", "")),
        current_page=page_id
    )

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page.title }}</title>
    <style>{{ style }}</style>
</head>
<body>
    <nav class="site-nav">
        <div class="nav-container">
            <a href="/" class="nav-title">Ke Aupuni O Ke Akua</a>
            <div class="hamburger" onclick="toggleMenu()">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <ul class="nav-menu" id="navMenu">
                {% for item in nav_items %}
                <li><a href="{{ item.url }}">{{ item.title }}</a></li>
                {% endfor %}
            </ul>
        </div>
    </nav>
    
    <header class="hero" style="background-image: url('{{ page.hero_image }}');">
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <h1>{{ page.title }}</h1>
        </div>
    </header>
    
    <main class="container">
        <article class="content-card">
            
            {# DISPLAY INTRO TEXT #}
            {% if intro_html %}
            <div class="intro-text">
                {{ intro_html|safe }}
                <hr style="border-top: 1px solid rgba(255, 255, 255, 0.3); margin: 2rem 0;">
            </div>
            {% endif %}
            
            {# DISPLAY MAIN BODY CONTENT #}
            {{ body_html|safe }}
            
            {# NEW: LOOP THROUGH VOLUMES FOR SERIES PAGES #}
            {% if page.volumes %}
                <div class="volume-list">
                {% for volume in page.volumes %}
                    <div class="volume-card">
                        <h3>{{ volume.title }}</h3>
                        {{ md_to_html(volume.body_md)|safe }}
                        
                        {% if volume.buy_links %}
                            <div class="button-group">
                                {% for link in volume.buy_links %}
                                    <a href="{{ link.url }}" target="_blank" class="buy-button">
                                        {{ link.icon }} Buy {{ link.name }}
                                    </a>
                                {% endfor %}
                            </div>
                        {% endif %}
                    </div>
                {% endfor %}
                </div>
            {% endif %}

            {# DISPLAY GALLERY IMAGES #}
            {% if page.gallery_images %}
            <div class="gallery-section">
                <h2>📸 Album Covers / Book Images</h2>
                <div class="gallery-grid">
                    {% for image in page.gallery_images %}
                    <div class="gallery-item">
                        <img src="{{ image }}" alt="Cover Image" loading="lazy">
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            {# DISPLAY MAIN PAGE BUY LINKS (if no volumes exist) #}
            {% if page.buy_links and not page.volumes %}
            <div class="buy-section">
                <h2 style="color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.9);">Available Now</h2>
                <div class="button-group">
                    {% for link in page.buy_links %}
                    <a href="{{ link.url }}" target="_blank" class="buy-button">
                        {{ link.icon }} Buy {{ link.name }}
                    </a>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
        </article>
    </main>
    
    <footer class="footer">
        <p>© 2025 Ke Aupuni O Ke Akua. All rights reserved. Made with aloha in Hawaiʻi.</p>
    </footer>
    
    <script>
    function toggleMenu() {
        const menu = document.getElementById('navMenu');
        menu.classList.toggle('active');
    }
    
    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        const nav = document.querySelector('.nav-container');
        const menu = document.getElementById('navMenu');
        if (!nav.contains(event.target) && menu.classList.contains('active')) {
            menu.classList.remove('active');
        }
    });
    </script>
</body>
</html>"""

@app.route("/")
def home():
    data = load_content()
    return render_page("home", data)

@app.route("/<page_id>")
def page(page_id):
    data = load_content()
    pages = data.get("pages", data)
    if page_id not in pages:
        abort(404)
    return render_page(page_id, data)


@app.route("/static/covers/<filename>")
def serve_cover(filename):
    """Serve CD cover images"""
    # NOTE: This route should point to your actual static folder path
    cover_path = BASE / "static" / "covers" / filename
    if cover_path.exists():
        return send_file(cover_path, mimetype='image/jpeg')
    abort(404)


# ============================================
# ADMIN PANEL
# ============================================

# Helper to create a clean slug from a title
def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')

@app.route("/admin")
def admin_panel():
    """Admin panel for managing content"""
    data = load_content()
    pages = data.get("pages", data)
    
    admin_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - Ke Aupuni O Ke Akua</title>
    <style>{ADMIN_CSS}</style>
</head>
<body>
    <div class="container">
        <h1>🌺 Admin Panel</h1>
        <p class="subtitle">Manage your website content</p>
        
        <a href="/admin/add_new" class="add-btn">➕ Add New Book / Series Page</a>
        
        <div class="page-list">
"""
    
    # Sort pages according to the 'order' list, putting new ones last
    page_ids = data.get("order", []) + [pid for pid in pages if pid not in data.get("order", [])]
    
    for page_id in page_ids:
        if page_id not in pages:
            continue
            
        page_data = pages[page_id]
        page_title = page_data.get("title", page_id)
        hero_image = page_data.get("hero_image", "")
        buy_links = page_data.get("buy_links", [])
        gallery_images = page_data.get("gallery_images", [])
        volumes = page_data.get("volumes", [])
        
        admin_html += f"""
            <div class="page-card">
                <a href="/admin/delete/{page_id}" class="delete-btn" onclick="return confirm('Are you sure you want to delete the page: {page_title}? This cannot be undone.');">🗑️ Delete</a>
                <div class="page-title">{page_title}</div>
                <div class="page-info">
                    <div><strong>URL Slug:</strong> /{page_id}</div>
                    <div><strong>Hero Image:</strong> {hero_image[:60]}...</div>
"""
        
        if buy_links:
            link_names = ", ".join([link["name"] for link in buy_links[:3]])
            admin_html += f'                    <div><strong>Buy Links:</strong> {len(buy_links)} ({link_names}...)</div>\n'
        
        if volumes:
            admin_html += f'                    <div><strong>Series Volumes:</strong> {len(volumes)} books</div>\n'
        
        if gallery_images:
            admin_html += f'                    <div><strong>Gallery Images:</strong> {len(gallery_images)} images</div>\n'
            admin_html += '                    <div class="gallery-preview">\n'
            for img in gallery_images[:3]:
                admin_html += f'                        <img src="{img}" alt="Gallery">\n'
            admin_html += '                    </div>\n'
        
        admin_html += f"""
                </div>
                <a href="/admin/edit/{page_id}" class="edit-btn">✏️ Edit Page</a>
            </div>
"""
    
    admin_html += """
        </div>
        
        <a href="/" class="back-btn">← Back to Website</a>
    </div>
</body>
</html>"""
    
    return admin_html

@app.route("/admin/add_new", methods=["GET", "POST"])
def add_new_page():
    """Add a new book/series page"""
    if request.method == "POST":
        data = load_content()
        new_title = request.form.get("title", "").strip()
        
        if not new_title:
            return redirect("/admin")
            
        new_slug = slugify(new_title)
        
        # Ensure slug is unique
        i = 1
        original_slug = new_slug
        while new_slug in data["pages"]:
            new_slug = f"{original_slug}-{i}"
            i += 1
            
        # Parse buy links
        buy_links = []
        links_str = request.form.get("buy_links", "").strip()
        for line in links_str.split("\n"):
            if "|" in line:
                parts = line.split("|")
                if len(parts) >= 3:
                    buy_links.append({
                        "name": parts[0].strip(),
                        "url": parts[1].strip(),
                        "icon": parts[2].strip()
                    })

        new_page_data = {
            "title": new_title,
            "hero_image": request.form.get("hero_image", "https://i.imgur.com/placeholder.png"),
            "intro_text": request.form.get("intro_text", "## New Book Introduction Here"),
            "body_md": request.form.get("body_md", "Full content of the new book/series page goes here."),
            "buy_links": buy_links
        }
        
        data["pages"][new_slug] = new_page_data
        
        # Add the new page to the end of the navigation order
        if new_slug not in data.get("order", []):
            data.setdefault("order", []).append(new_slug)

        save_content(data)
        return redirect(f"/admin/edit/{new_slug}")
    
    # GET request: show the add new page form
    
    ADD_FORM_CSS = """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: system-ui, -apple-system, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 2rem; }
        .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        h1 { color: #2c3e50; margin-bottom: 0.5rem; }
        .subtitle { color: #7f8c8d; margin-bottom: 2rem; }
        .form-group { margin-bottom: 1.5rem; }
        label { display: block; color: #2c3e50; font-weight: 600; margin-bottom: 0.5rem; }
        input[type="text"], textarea { width: 100%; padding: 0.75rem; border: 2px solid #e9ecef; border-radius: 8px; font-size: 1rem; font-family: inherit; transition: border-color 0.3s ease; }
        input[type="text"]:focus, textarea:focus { outline: none; border-color: #667eea; }
        textarea { min-height: 200px; resize: vertical; }
        .help-text { font-size: 0.85rem; color: #6c757d; margin-top: 0.25rem; }
        .btn-group { display: flex; gap: 1rem; margin-top: 2rem; }
        .btn { padding: 0.75rem 1.5rem; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: all 0.2s ease; text-decoration: none; display: inline-block; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4); }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-secondary:hover { background: #5a6268; }
    """
    
    add_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add New Page</title>
    <style>{ADD_FORM_CSS}</style>
</head>
<body>
    <div class="container">
        <h1>➕ Add New Book/Series</h1>
        <p class="subtitle">Enter the details for your new page. A unique URL will be generated automatically.</p>
        
        <form method="POST">
            <div class="form-group">
                <label for="title">Page Title (e.g., New Book Series Title)</label>
                <input type="text" id="title" name="title" required>
            </div>
            
            <div class="form-group">
                <label for="hero_image">Hero Image URL</label>
                <input type="text" id="hero_image" name="hero_image" value="https://i.imgur.com/placeholder.png" required>
                <div class="help-text">Use an Imgur or similar URL for the banner image.</div>
            </div>
            
            <div class="form-group">
                <label for="intro_text">Book Intro/Excerpt (Markdown)</label>
                <textarea id="intro_text" name="intro_text" style="min-height: 100px;">## The brief introduction or first few paragraphs goes here.</textarea>
                <div class="help-text">This will be prominently displayed near the top.</div>
            </div>
            
            <div class="form-group">
                <label for="body_md">Full Content (Markdown)</label>
                <textarea id="body_md" name="body_md" required>The full chapter summary, testimonials, and detailed information about the new book or series goes here in **Markdown** format.</textarea>
                <div class="help-text">Use Markdown formatting (## for headings, ** for bold, etc.)</div>
            </div>
            
            <div class="form-group">
                <label for="buy_links">Buy/Platform Links (One Link Per Line, Format: Name|URL|Icon)</label>
                <textarea id="buy_links" name="buy_links" style="min-height: 100px;">Amazon|https://amazon.com/link|🛒
Gumroad|https://gumroad.com/link|📚</textarea>
                <div class="help-text">Example Icons: 🛒 (cart), 📚 (books), 🍎 (apple), 🎧 (headphones)</div>
            </div>
            
            <div class="btn-group">
                <button type="submit" class="btn btn-primary">✅ Create Page</button>
                <a href="/admin" class="btn btn-secondary">← Cancel</a>
            </div>
        </form>
    </div>
</body>
</html>"""
    
    return add_html

@app.route("/admin/delete/<page_id>")
def delete_page(page_id):
    """Delete a page"""
    data = load_content()
    
    if page_id in data["pages"] and page_id not in data.get("order", []):
        # We only allow deleting pages NOT in the hardcoded ORDER list for safety
        del data["pages"][page_id]
        if page_id in data.get("order", []):
            data["order"].remove(page_id)
        
        save_content(data)
        return redirect("/admin")
    
    # If the page is one of the original hardcoded ones, abort to prevent site breakage
    if page_id in DEFAULT_PAGES["pages"]:
        abort(403, description="Cannot delete default system pages.")
        
    abort(404)


@app.route("/admin/edit/<page_id>", methods=["GET", "POST"])
def edit_page(page_id):
    """Edit a specific page"""
    data = load_content()
    pages = data.get("pages", data)
    
    if page_id not in pages:
        abort(404)
    
    page = pages[page_id]

    if request.method == "POST":
        
        # --- 1. HANDLE SIMPLE FIELDS ---
        pages[page_id]["title"] = request.form.get("title", "")
        pages[page_id]["hero_image"] = request.form.get("hero_image", "")
        pages[page_id]["intro_text"] = request.form.get("intro_text", "")
        pages[page_id]["body_md"] = request.form.get("body_md", "")
        
        # --- 2. HANDLE BUY LINKS (Amazon, Gumroad, etc.) ---
        buy_links = []
        links_str = request.form.get("buy_links", "").strip()
        for line in links_str.split("\n"):
            if "|" in line:
                parts = line.split("|")
                if len(parts) >= 3:
                    buy_links.append({
                        "name": parts[0].strip(),
                        "url": parts[1].strip(),
                        "icon": parts[2].strip()
                    })
        if buy_links:
            pages[page_id]["buy_links"] = buy_links
        elif "buy_links" in pages[page_id]:
            del pages[page_id]["buy_links"]

        # --- 3. HANDLE GALLERY IMAGES ---
        gallery_str = request.form.get("gallery_images", "").strip()
        if gallery_str:
            gallery_images = [img.strip() for img in gallery_str.split("\n") if img.strip()]
            pages[page_id]["gallery_images"] = [
                img if img.startswith('http') else url_for('static', filename='covers/' + img.lstrip('/static/covers/')) 
                for img in gallery_images
            ]
        elif "gallery_images" in pages[page_id]:
            del pages[page_id]["gallery_images"]

        # --- 4. HANDLE SERIES VOLUMES (for pages like 'call_to_repentance') ---
        if "volumes" in page:
            volumes_str = request.form.get("volumes_list", "").strip()
            new_volumes = []
            
            # Split the entire block into separate volume blocks
            volume_blocks = volumes_str.split("--- VOLUME ---")
            
            for block in volume_blocks:
                block = block.strip()
                if not block:
                    continue
                
                # Use regex or simple split to extract fields within the block
                title_match = re.search(r'TITLE:\s*(.*)', block)
                md_match = re.search(r'DESCRIPTION:\s*(.*)', block, re.DOTALL)
                links_block_match = re.search(r'BUY_LINKS:\s*(.*)', block, re.DOTALL)
                
                if title_match and md_match:
                    vol_title = title_match.group(1).strip()
                    vol_body_md = md_match.group(1).split("BUY_LINKS:")[0].strip() # Get everything before BUY_LINKS
                    
                    vol_buy_links = []
                    if links_block_match:
                        links_lines = links_block_match.group(1).strip().split('\n')
                        for line in links_lines:
                            line = line.strip()
                            if "|" in line:
                                parts = line.split("|")
                                if len(parts) >= 3:
                                    vol_buy_links.append({
                                        "name": parts[0].strip(),
                                        "url": parts[1].strip(),
                                        "icon": parts[2].strip()
                                    })
                                
                    new_volumes.append({
                        "title": vol_title,
                        "body_md": vol_body_md,
                        "buy_links": vol_buy_links
                    })
            
            pages[page_id]["volumes"] = new_volumes
        
        save_content({"pages": pages, "order": data.get("order", ORDER)})
        return redirect("/admin")
    
    
    # --- GET REQUEST: DISPLAY FORM ---
    
    # Format Buy Links for form display
    links_str = ""
    if "buy_links" in page:
        links_str = "\n".join([
            f"{link['name']}|{link['url']}|{link['icon']}"
            for link in page["buy_links"]
        ])
    
    # Format Gallery Images for form display
    gallery_str = "\n".join(page.get("gallery_images", []))
    
    # Format Volumes for series page form display
    volumes_str = ""
    if "volumes" in page:
        volume_entries = []
        for volume in page["volumes"]:
            # Format buy links for this specific volume
            vol_links_str = "\n".join([
                f"{link['name']}|{link['url']}|{link['icon']}"
                for link in volume.get('buy_links', [])
            ])
            
            # Create the block for this volume
            volume_entries.append(f"""
--- VOLUME ---
TITLE: {volume.get('title', '')}
DESCRIPTION:
{volume.get('body_md', '')}
BUY_LINKS:
{vol_links_str}
            """.strip())
        
        volumes_str = "\n\n".join(volume_entries)
    
    # CSS for the edit form
    EDIT_FORM_CSS = """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: system-ui, -apple-system, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 2rem; }
        .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        h1 { color: #2c3e50; margin-bottom: 0.5rem; }
        .subtitle { color: #7f8c8d; margin-bottom: 2rem; }
        .form-group { margin-bottom: 1.5rem; }
        label { display: block; color: #2c3e50; font-weight: 600; margin-bottom: 0.5rem; }
        input[type="text"], textarea { width: 100%; padding: 0.75rem; border: 2px solid #e9ecef; border-radius: 8px; font-size: 1rem; font-family: inherit; transition: border-color 0.3s ease; }
        input[type="text"]:focus, textarea:focus { outline: none; border-color: #667eea; }
        textarea { min-height: 200px; resize: vertical; }
        .help-text { font-size: 0.85rem; color: #6c757d; margin-top: 0.25rem; }
        .btn-group { display: flex; gap: 1rem; margin-top: 2rem; }
        .btn { padding: 0.75rem 1.5rem; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: all 0.2s ease; text-decoration: none; display: inline-block; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4); }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-secondary:hover { background: #5a6268; }
        .alert { padding: 1rem; background: #fff3cd; border: 1px solid #ffeeba; color: #856404; border-radius: 8px; margin-bottom: 1.5rem; }
    """
    
    edit_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit {page['title']}</title>
    <style>{EDIT_FORM_CSS}</style>
</head>
<body>
    <div class="container">
        <h1>✏️ Edit Page</h1>
        <p class="subtitle">{page['title']} (URL: /{page_id})</p>
        
        <form method="POST">
            <div class="form-group">
                <label for="title">Page Title</label>
                <input type="text" id="title" name="title" value="{page.get('title', '')}" required>
            </div>
            
            <div class="form-group">
                <label for="hero_image">Hero Image URL</label>
                <input type="text" id="hero_image" name="hero_image" value="{page.get('hero_image', '')}" required>
                <div class="help-text">Use imgur.com URLs (e.g., https://i.imgur.com/ABC123.jpg)</div>
            </div>
            
            <div class="form-group">
                <label for="intro_text">Book/Series Introduction (Markdown)</label>
                <textarea id="intro_text" name="intro_text" style="min-height: 100px;">{page.get('intro_text', '')}</textarea>
                <div class="help-text">A short excerpt or introduction that appears prominently. Use Markdown formatting.</div>
            </div>
            
            <div class="form-group">
                <label for="body_md">Full Content (Markdown)</label>
                <textarea id="body_md" name="body_md" required>{page.get('body_md', '')}</textarea>
                <div class="help-text">Use Markdown formatting (## for headings, ** for bold, etc.)</div>
            </div>
            
            <div class="form-group">
                <label for="buy_links">Buy/Platform Links (One Link Per Line, Format: Name|URL|Icon)</label>
                <textarea id="buy_links" name="buy_links" style="min-height: 100px;">{links_str}</textarea>
                <div class="help-text">This will create buttons at the bottom of the page. Example: Amazon|https://link|🛒</div>
            </div>
            
            <div class="form-group">
                <label for="gallery_images">Gallery Images (Optional - One URL per line)</label>
                <textarea id="gallery_images" name="gallery_images" style="min-height: 100px;">{gallery_str}</textarea>
                <div class="help-text">For your covers: **start with /static/covers/** (e.g., /static/covers/my-new-book.jpg). One per line.</div>
            </div>
            
            {"""
            <div class="alert">
                <h3>📚 Series Volume List (Advanced)</h3>
                <p>This page is set up as a **Multi-Volume Series**. Edit the volumes below to add a new book to the series, including its unique description and purchase buttons.</p>
                <label for="volumes_list">Volume List Structure</label>
                <textarea id="volumes_list" name="volumes_list" style="min-height: 400px; font-family: monospace;">""" + volumes_str + """</textarea>
                <div class="help-text">
                    **CRITICAL:** To add a new volume, copy and paste one of the existing **--- VOLUME ---** blocks to the bottom and edit its content. Do not change the internal formatting (TITLE:, DESCRIPTION:, BUY_LINKS:).
                    <br>Inside BUY_LINKS, use the same format as above: Name|URL|Icon (one link per line).
                </div>
            </div>
            """ if 'volumes' in page else ''}
            
            <div class="btn-group">
                <button type="submit" class="btn btn-primary">💾 Save Changes</button>
                <a href="/admin" class="btn btn-secondary">← Cancel</a>
            </div>
        </form>
    </div>
</body>
</html>"""
    
    return edit_html

if __name__ == "__main__":
    if not DATA_FILE.exists():
        save_content(DEFAULT_PAGES)
    
    # Reload content to apply any necessary migrations (like product_url -> buy_links)
    load_content()
    
    port = int(os.environ.get("PORT", 5000))
    print("🌺 Starting Ke Aupuni O Ke Akua website...")
    print(f"🌊 Visit: http://localhost:{port}")
    print("=" * 50)
    app.run(host="0.0.0.0", port=port, debug=True)
