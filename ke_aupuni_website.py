# ke_aupuni_website.py
# FIXED: Transparent nav bar - no white background
from flask import Flask, request, redirect, render_template_string, abort, url_for, send_file
import json
from pathlib import Path
import markdown
import os

app = Flask(__name__)
ORDER = ["home", "kingdom_wealth", "free_booklets", "kingdom_keys", "call_to_repentance", "aloha_wellness", "pastor_planners", "nahenahe_voice"]
BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"

# ===== DIGITAL PRODUCTS SETUP =====
from datetime import datetime
from werkzeug.utils import secure_filename

PRODUCTS_FILE = BASE / "digital_products.json"
PRODUCTS_FOLDER = BASE / "digital_products"

# Create products folder if it doesn't exist
PRODUCTS_FOLDER.mkdir(exist_ok=True)

DEFAULT_PAGES = {
    "order": ORDER,
    "pages": {
        "home": {
            "title": "Ke Aupuni O Ke Akua - The Kingdom of God",
            "hero_image": "https://i.imgur.com/wmHEyDo.png",
            "body_md": "## Welcome to Ke Aupuni O Ke Akua - The Kingdom of God\r\n\r\nMahalo for visiting. This site is dedicated to rediscovering the revolutionary Kingdom message that Jesus actually preached, which is often missed in modern religious traditions.\r\n\r\n### Our Mission: Kingdom, Not Religion\r\nJesus's central focus was the Kingdom of God—the reign and rule of God breaking into the human experience here and now. Our resources aim to guide you into a deeper understanding of Kingdom principles, citizenship, and authority, moving you from religious performance into authentic, transformative living.\r\n\r\n**Start your journey today by exploring 'The Call to Repentance' series in the navigation.**\r\n\r\n### What Jesus Actually Taught\r\n\r\n**Kingdom Principles Over Religious Rules** - Discover how Jesus consistently chose kingdom living over religious compliance.\r\n\r\n**Repentance as Transformation** - Move beyond feeling sorry for sins to understanding a complete transformation of mind, heart, and lifestyle.\r\n\r\n**Heaven on Earth** - Learn how the Kingdom of God is meant to manifest in our daily lives, relationships, and communities right now.",
            "product_url": "https://amzn.to/3FfH9ep",
            "gumroad_url": "https://keaupuni.gumroad.com"
        },
        "kingdom_wealth": {
            "title": "Kingdom Wealth",
            "hero_image": "https://i.imgur.com/G2YmSka.jpeg",
            "body_md": "## Biblical Stewardship & Economic Increase\r\n\r\nThe Kingdom operates on stewardship, not ownership.\r\n\r\n### Core Principles\r\n\r\n**Source vs. Resource** - God is your Source.\r\n\r\n**[FREE Kingdom Keys →](/kingdom_keys)**\r\n\r\n**[FREE Kingdom Booklets →](/free_booklets)**\r\n\r\n**[Complete Kingdom Series →](/call_to_repentance)**\r\n\r\n**[Myron Golden Training →](/myron-golden)**",
            "product_url": ""
        },
        "aloha_wellness": {
            "title": "Aloha Wellness - Island Health & Healing",
            "hero_image": "https://i.imgur.com/xGeWW3Q.jpeg",
            "body_md": "## Aloha Wellness - The Sacred Art of How You Eat\r\n\r\nDiscover the life-changing power of **how** you eat, not just what you eat. This groundbreaking wellness book combines cutting-edge scientific research with ancient Hawaiian mana'o (wisdom) to transform your relationship with food and nourishment.\r\n\r\n### Beyond Diet Culture - A Hawaiian Perspective\r\n\r\nTraditional Hawaiian culture understood something modern society has forgotten: eating is a sacred act that connects us to the land, our ancestors, and our own spiritual well-being. This book bridges that ancient wisdom with contemporary nutritional science.\r\n\r\n### Revolutionary Approach: How, Not What\r\n\r\n**Mindful Consumption** - Learn the scientific basis for how mindful eating practices affect digestion, metabolism, and overall health.\r\n\r\n**Cultural Eating Wisdom** - Discover how Hawaiian ancestors approached meals as community ceremonies, gratitude practices, and spiritual connections.\r\n\r\n**Stress and Digestion** - Research-backed insights into how your emotional state during meals affects nutrient absorption and digestive health.\r\n\r\n**Rhythm and Timing** - Ancient Hawaiian understanding of eating in harmony with natural rhythms, supported by modern chronobiology research.\r\n\r\n**Scientific Research Meets Island Wisdom** - This book offers a comprehensive look at the intersection of modern science and ancient practice.\r\n\r\n### Hawaiian Mana'o (Wisdom Principles)\r\n\r\n**Ho'oponopono with Food** - Making right relationships with nourishment and healing food-related guilt or shame.\r\n\r\n**Aloha 'Āina** - Love of the land extends to gratitude for the food it provides and mindful consumption practices.\r\n\r\n**Lōkahi** - Finding unity and balance in your relationship with food, body, and spirit.\r\n\r\n**Mālama** - Caring for your body as a sacred temple through conscious eating practices.\r\n\r\nTransform your health from the inside out by changing not what you eat, but how you approach the sacred act of nourishment.",
            "product_url": "https://a.co/d/6YrcnQp",
            "gumroad_url": "https://keaupuni.gumroad.com/l/aloha-wellness",
            "direct_buy_url": ""
        },
        "call_to_repentance": {
            "title": "The Call to Repentance - The Kingdom Series",
            "hero_image": "https://i.imgur.com/tG1vBp9.jpeg",
            "body_md": "## The Call to Repentance - Rediscovering Jesus's Kingdom Message\r\n\r\nStep beyond religious tradition and rediscover the revolutionary Kingdom message that Jesus actually preached. This transformative book series cuts through centuries of religious interpretation to reveal the pure, life-changing teachings of the Kingdom of God.\r\n\r\n### Series Overview (Volumes 1-5)\r\n\r\nThis isn't a single book but a comprehensive series that systematically unpacks Jesus's kingdom teachings. **To display the book covers, simply replace the placeholder URL below each Volume with your image URL from Imgur or Amazon.**\r\n\r\n---\r\n\r\n### **Volume 1: The Foundation**\r\n![The Call to Repentance Volume 1 Cover](https://via.placeholder.com/300x450/4A90E2/FFFFFF?text=Volume+1) \r\nUnderstanding what the Kingdom of God actually is and why Jesus made it His central message.\r\n\r\n---\r\n\r\n### **Volume 2: Kingdom Citizenship**\r\n![The Call to Repentance Volume 2 Cover](https://via.placeholder.com/300x450/50C878/FFFFFF?text=Volume+2)\r\nWhat it means to be a citizen of God's kingdom while living in earthly systems.\r\n\r\n---\r\n\r\n### **Volume 3: Kingdom Economics**\r\n![The Call to Repentance Volume 3 Cover](https://via.placeholder.com/300x450/FFB347/FFFFFF?text=Volume+3)\r\nHow kingdom principles transform our relationship with money, work, and provision.\r\n\r\n---\r\n\r\n### **Volume 4: Kingdom Relationships**\r\n![The Call to Repentance Volume 4 Cover](https://via.placeholder.com/300x450/FF6B6B/FFFFFF?text=Volume+4)\r\nLove, forgiveness, and community the way Jesus intended.\r\n\r\n---\r\n\r\n### **Volume 5: Kingdom Authority**\r\n![The Call to Repentance Volume 5 Cover](https://via.placeholder.com/300x450/9B59B6/FFFFFF?text=Volume+5)\r\nWalking in the supernatural power that Jesus demonstrated and promised to His followers.\r\n\r\n---\r\n\r\n## Embracing True Repentance for Spiritual Growth\r\n\r\nRepentance is not merely feeling sorry for our mistakes - it is a complete transformation of heart and mind that leads us into the fullness of Kingdom living.\r\n\r\n### Understanding Biblical Repentance\r\n\r\nThe Hebrew word **teshuvah** means \"to return\" or \"to turn around.\" It implies a complete change of direction - turning away from patterns that separate us from God and turning toward His kingdom ways.\r\n\r\n**The Three Dimensions of True Repentance:**\r\n\r\n**1. Metanoia (Change of Mind)**\r\nRepentance begins with a fundamental shift in how we think. We must align our thoughts with God's thoughts, seeing ourselves and others through His eyes of love and truth.\r\n\r\n**2. Transformation of Heart**\r\nTrue repentance touches our emotions and desires. Our hearts must be softened and purified, learning to love what God loves and grieve what grieves His heart.\r\n\r\n**3. Changed Actions**\r\nRepentance must bear fruit in our daily choices. We demonstrate our changed hearts through new patterns of behavior that reflect Kingdom values.\r\n\r\n*\"Repent, for the kingdom of heaven has come near.\" - Matthew 4:17*\r\n\r\n---\r\n\r\n### A Call to Authentic Christianity\r\n\r\nThis series challenges readers to move beyond:\r\n- Religious performance into authentic relationship\r\n- Sunday Christianity into daily kingdom living\r\n- Denominational identity into kingdom citizenship\r\n- Waiting for heaven into experiencing God's kingdom now\r\n\r\n**Join the revolution that Jesus started. Discover the Kingdom message that changes everything.**",
            "product_url": "https://a.co/d/fgbAVMs",
            "gumroad_url": "https://keaupuni.gumroad.com/l/call-to-repentance"
        },
        "pastor_planners": {
            "title": "Pastor Planners - Tools for Ministry Excellence",
            "hero_image": "https://i.imgur.com/tWnn5UY.png",
            "body_md": "## Organize Your Ministry with Purpose and Prayer\r\n\r\nEffective ministry requires both spiritual sensitivity and practical organization. Our Pastor Planners combine beautiful design with functional tools to help you lead with excellence and peace.\r\n\r\n### Features of Our Ministry Planning System\r\n\r\n**Sermon Planning Sections** - Map out your preaching calendar with space for themes, scriptures, and prayer requests. Plan seasonal series and track the spiritual journey of your congregation.\r\n\r\n**Prayer and Pastoral Care** - Dedicated sections for tracking prayer requests, hospital visits, counseling sessions, and follow-up care. Never let a member of your flock slip through the cracks.\r\n\r\n**Meeting and Event Coordination** - Organize board meetings, committee sessions, special events, and outreach activities with integrated calendars and checklists.\r\n\r\n**Personal Spiritual Disciplines** - Maintain your own spiritual health with guided sections for daily devotions, sabbath planning, and personal growth goals.\r\n\r\n### Why Pastors Love Our Planners\r\n\r\n**Hawaiian-Inspired Design** - Beautiful layouts featuring island imagery and scripture verses that bring peace to your planning time.\r\n\r\n**Flexible Formatting** - Works for churches of all sizes and denominations, with customizable sections for your unique ministry context.\r\n\r\n**Durable Construction** - High-quality materials that withstand daily use throughout the church year.\r\n\r\n**Spiritual Focus** - More than just organization - designed to keep your heart centered on God's calling throughout your busy ministry schedule.\r\n\r\n### Available in Multiple Pacific Islander Languages\r\n\r\n**Ke Kauoha La Haku (Hawaiian Edition 2026)**\r\n📖 [Get on Amazon](https://a.co/d/gatnNET) | 💳 [Get on Gumroad](https://uncomango.gumroad.com/l/ulrmu)\r\n\r\n**Tusi Fuataiaga a le Faifeau (Samoan Enhanced Edition 2026)**\r\n📖 [Get on Amazon](https://a.co/d/gs0WRPh) | 💳 [Get on Gumroad](https://uncomango.gumroad.com/l/ubzevn)\r\n\r\nOrder your Pastor Planner today and experience the peace that comes from organized, prayer-centered ministry leadership."
        },
        "nahenahe_voice": {
            "title": "The Nahenahe Voice of Nahono'opi'ilani - Musical Legacy",
            "hero_image": "https://i.imgur.com/Vyz6nFJ.png",
            "body_md": "## The Nahenahe Voice of Nahono'opi'ilani - Live from Molokai Ranch Lodge\r\n\r\nExperience the soul-stirring sounds of authentic Hawaiian music captured live at the historic Molokai Ranch Lodge in the year 2000. This intimate recording showcases the true meaning of **nahenahe** - the gentle, soothing voice that carries the spirit of aloha across the islands.\r\n\r\n### A Sacred Musical Journey\r\n\r\nRecorded in the peaceful setting of Molokai Ranch Lodge, this collection features solo guitar and traditional Hawaiian melodies that speak directly to the heart. Each song was performed live, capturing the mana (spiritual energy) and authentic aloha that can only come from the sacred island of Molokai.\r\n\r\n**Nahenahe** means more than just \"soft\" or \"sweet\" - it represents music that heals, soothes, and connects us to the divine presence that flows through all creation. This recording embodies that sacred tradition.\r\n\r\n### What You'll Experience:\r\n\r\n**Traditional Hawaiian Melodies** - Time-honored songs that have been passed down through generations, preserving the cultural wisdom of our ancestors.\r\n\r\n**Solo Guitar Mastery** - Intimate acoustic performances that showcase the beauty of Hawaiian slack-key guitar traditions and contemporary island sounds.\r\n\r\n**Authentic Island Atmosphere** - The natural acoustics and peaceful energy of Molokai Ranch Lodge create an immersive listening experience.\r\n\r\n**Healing Through Song** - Each track is designed to bring peace, comfort, and the healing power of aloha to your daily life.\r\n\r\n### The Heart of Aloha\r\n\r\nThis recording is more than entertainment - it's a spiritual journey that invites you to slow down, breathe deeply, and connect with the tranquil spirit of Hawaiʻi. Whether you're seeking meditation music, background for quiet reflection, or simply the beauty of authentic Hawaiian sounds, this collection offers a pathway to inner peace.\r\n\r\n*\"Music is the language that speaks when words are not enough. The nahenahe voice carries aloha to every heart that listens.\"*\r\n\r\nPerfect for meditation, relaxation, spiritual practice, or any time you need the gentle embrace of island peace.",
            "gallery_images": [
                "/static/covers/cover1.jpg",
                "/static/covers/cover2.jpg",
                "/static/covers/cover3.jpg"
            ],
            "product_links": [
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
        },
        "free_booklets": {
            "title": "FREE Booklets",
            "hero_image": "https://i.imgur.com/wmHEyDo.png",
            "body_md": "## 🎁 FREE Kingdom Booklets\r\n\r\nDownload all 6:",
            "products": [
                {"title": "Kingdom Wealth Principles", "download": "/download/booklet1"},
                {"title": "Kingdom Wealth for Couples", "download": "/download/booklet2"},
                {"title": "Kingdom Wellness Principles", "download": "/download/booklet3"},
                {"title": "Kingdom Wellness for Couples", "download": "/download/booklet4"},
                {"title": "Kingdom Living Principles", "download": "/download/booklet5"},
                {"title": "Kingdom Living for Couples", "download": "/download/booklet6"}
            ]
        },
        "kingdom_keys": {
            "title": "FREE Kingdom Keys Booklets",
            "hero_image": "https://i.imgur.com/wmHEyDo.png",
            "body_md": "## 🌺 FREE Kingdom Keys 🌺\r\n\r\nAfter 30 years of biblical study.\r\n\r\n**[Browse Complete Kingdom Series →](/call_to_repentance)**",
            "products": [
                {"title": "7 Scriptures Kingdom Inside You", "download": "/download/pamphlet1"},
                {"title": "Kingdom Healing in 10 Minutes", "download": "/download/pamphlet2"},
                {"title": "5 Kingdom Prayers", "download": "/download/pamphlet3"},
                {"title": "Kingdom Wealth Verses", "download": "/download/pamphlet4"}
            ]
        }
    }
}

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
    color: white;
    background: transparent;
    background-image: 
        radial-gradient(circle at 20% 50%, rgba(175, 216, 248, 0.05) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(212, 165, 116, 0.05) 0%, transparent 50%);
}

.site-nav {
    background: none !important;
    padding: 0;
    margin: 0;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 9999;
}

.nav-container {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    padding: 0.5rem 2rem;
    background: none !important;
}

.nav-title {
    font-size: 1.5rem;
    font-weight: bold;
    color: #2c3e50;
    text-decoration: none;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
    display: flex;
    align-items: center;
    gap: 1rem;
}

.nav-menu {
    display: flex;
    list-style: none;
    gap: 2rem;
    background: none;
    margin: 0;
    padding: 0;
}

.nav-menu a {
    background: transparent !important;
    text-decoration: none;
    color: white;
    font-weight: 600;
    padding: 0.4rem 1rem; 
    font-size: 1.3rem; 
    font-family: 'Georgia', serif;
    text-shadow: 2px 2px 6px rgba(0,0,0,1);
    border-radius: 6px;
    transition: all 0.3s ease;
}

.nav-menu a:hover {
    background: var(--accent-teal);
    color: white;
}

.hamburger {
    display: none;
    flex-direction: column;
    cursor: pointer;
    padding: 0.5rem;
}

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
    overflow: hidden;
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
    display: none;
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
    background: rgba(0, 0, 0, 0.25);
    border: none;
    padding: 3rem 2rem;
    box-shadow: none;
    margin-top: 25vh;
    padding-top: 4rem;
    color: white;
}

.content-card h2 {
    color: white;
    margin-bottom: 1rem;
    font-size: 2.2rem;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.9);
    position: relative;
    z-index: 1;
}

.content-card h3 {
    color: white;
    margin: 2rem 0 1rem;
    font-size: 1.6rem;
    text-shadow: 2px 2px 5px rgba(0,0,0,0.8);
    position: relative;
    z-index: 1;
}

.content-card a {
    color: #FFD700;
    text-decoration: underline;
    font-weight: 600;
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

.buy-section {
    text-align: center;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(255, 255, 255, 0.3);
}

.buy-button, .music-button {
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

.buy-button:hover, .music-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(95, 158, 160, 0.4);
}

.music-buttons {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 1rem;
    margin-top: 1.5rem;
}

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

@media (max-width: 768px) {
    .hamburger {
        display: flex;
    }
    
    .nav-menu {
        display: none;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: rgba(0, 0, 0, 0.85) !important;
        flex-direction: column;
        gap: 0;
        padding: 0.5rem 0;
    }
    
    .nav-menu.active {
        display: flex;
    }
    
    .nav-menu a {
        background: transparent !important;
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
        margin-top: 2rem;
        padding-top: 3rem;
    }
    
    .content-card h2 {
        font-size: 1.8rem;
    }
    
    .content-card h3 {
        font-size: 1.4rem;
    }
    
    .music-buttons {
        flex-direction: column;
    }
    
    .music-button {
        width: 100%;
    }
}
"""

def md_to_html(md_text):
    return markdown.markdown(md_text, extensions=["extra", "nl2br"])

MYRON_GOLDEN_TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Transform Your Financial Future</title>
<style>{{ style|safe }}
.email-capture{background:rgba(212,165,116,0.2);padding:30px;margin:30px 0;text-align:center;border:3px solid rgba(212,165,116,0.5);border-radius:12px}
.section{padding:40px 0}.product-box{background:rgba(0,0,0,0.5);padding:30px;margin:20px 0;border-radius:12px;text-align:center}
.btn{display:inline-block;padding:15px 40px;background:linear-gradient(135deg,#5f9ea0,#4a8b8e);color:white;text-decoration:none;font-weight:bold;margin:10px;border-radius:8px}
</style></head><body>
<nav class="site-nav" style="background:transparent !important;">
<div class="nav-container" style="background:transparent !important;">
<a href="/"><img src="/static/images/output-onlinepngtools.png" alt="Logo" style="height:180px;width:auto;"></a>
<div class="hamburger" onclick="toggleMenu()">
<span></span>
<span></span>
<span></span>
</div>
<ul class="nav-menu" id="navMenu">
<li><a href="/">Ke Aupuni O Ke Akua</a></li>
<li><a href="/kingdom_wealth">Kingdom Wealth</a></li>
<li><a href="/free_booklets">FREE Booklets</a></li>
<li><a href="/kingdom_keys">FREE Kingdom Keys</a></li>
<li><a href="/call_to_repentance">Call to Repentance</a></li>
<li><a href="/aloha_wellness">Aloha Wellness</a></li>
<li><a href="/pastor_planners">Pastor Planners</a></li>
<li><a href="/nahenahe_voice">Nahenahe Voice</a></li>
</ul>
</div>
</nav>
<header class="hero" style="background-image:url('https://i.imgur.com/G2YmSka.jpeg')"><div class="hero-overlay"></div><div class="hero-content"><h1>Transform Your Financial Future</h1></div></header>
<main class="container"><article class="content-card">
<div class="email-capture"><h2>Get FREE Kingdom Business Guide</h2><form action="https://app.kit.com/forms/8979853/subscriptions" method="post"><input type="text" name="fields[first_name]" placeholder="First Name" required style="padding:15px;margin:10px 0;width:100%;border-radius:6px;border:1px solid #ccc"><input type="email" name="email_address" placeholder="Email" required style="padding:15px;margin:10px 0;width:100%;border-radius:6px;border:1px solid #ccc"><button type="submit" style="width:100%;padding:15px;background:#d4af37;color:white;font-weight:bold;border:none;border-radius:6px">GET FREE GUIDE</button></form></div>
<div class="section"><h2>SECTION 1: Start Your Journey</h2><div class="product-box"><a href="https://www.trashmantocashman.com/tmcm-book?affiliate_id=4319525" class="btn">TRASH MAN TO CASH MAN</a><a href="https://www.bossmovesbook.com/bossmoves?affiliate_id=4319525" class="btn">BOSS MOVES</a></div></div>
<div class="section"><h2>SECTION 2: Transform Your Money Blueprint</h2><div class="product-box"><a href="https://www.mindovermoneymastery.com/momm?affiliate_id=4319525" class="btn">MIND OVER MONEY MASTERY</a></div></div>
<div class="section"><h2>SECTION 3: Master Making Offers</h2><div class="product-box"><a href="https://www.makemoreofferschallenge.com/mmoc?affiliate_id=4319525" class="btn">MAKE MORE OFFERS</a><a href="https://www.offermasterylive.com/offer-mastery-livevetfk4nn?affiliate_id=4319525" class="btn">OFFER MASTERY LIVE</a></div></div>
<div class="section"><h2>SECTION 4: Build Your System</h2><div class="product-box"><a href="https://www.mygoldenops.com/golden-opsm1y8y7bx?affiliate_id=4319525" class="btn">GOLDEN OPS</a></div></div>
</article></main>
<script>
function toggleMenu() {
    const menu = document.getElementById('navMenu');
    menu.classList.toggle('active');
}
document.addEventListener('click', function(event) {
    const nav = document.querySelector('.nav-container');
    const menu = document.getElementById('navMenu');
    if (!nav.contains(event.target) && menu.classList.contains('active')) {
        menu.classList.remove('active');
    }
});
</script>
</body></html>"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page.title }}</title>
    <style>{{ style }}
    .content-card img {
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        margin: 20px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        display: block;
    }
    
    .content-card img[alt*="Cover"],
    .content-card img[alt*="Volume"] {
        max-width: 300px;
        margin: 20px auto;
    }
    
    @media (max-width: 768px) {
        .content-card img[alt*="Cover"],
        .content-card img[alt*="Volume"] {
            max-width: 100%;
        }
    }
</style>
</head>
<body>
    <nav class="site-nav" style="background:transparent !important;">
        <div class="nav-container" style="background:transparent !important;">
            <a href="/"><img src="/static/images/output-onlinepngtools.png" alt="Logo" style="height:180px;width:auto;"></a>
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
            {{ body_html|safe }}
            
            {% if page.gallery_images %}
            <div class="gallery-section">
                <h2>📸 Album Covers</h2>
                <div class="gallery-grid">
                    {% for image in page.gallery_images %}
                    <div class="gallery-item">
                        <img src="{{ image }}" alt="CD Cover" loading="lazy">
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            {% if page.product_links %}
            {% if page.get("products") %}
            <div class="products-section" style="margin: 3rem 0;">
                <h2 style="color: white; text-align: center; margin-bottom: 2rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.9);">📚 Available Resources</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem;">
                    {% for product in page.products %}
                    <div style="background: rgba(0,0,0,0.5); padding: 2rem; border-radius: 12px; text-align: center;">
                        {% if product.cover %}
                        <img src="{{ product.cover }}" alt="{{ product.title }}" style="width: 100%; border-radius: 8px; margin-bottom: 1rem;">
                        {% endif %}
                        <h3 style="color: white; font-size: 1.1rem; margin-bottom: 1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.7);">{{ product.title }}</h3>
                        <div style="display: flex; gap: 0.5rem; justify-content: center; flex-wrap: wrap;">
                            {% if product.get('download') %}
                            <a href="{{ product.download }}" style="display: inline-block; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #d4af37, #b8960c); color: white; text-decoration: none; border-radius: 6px; font-weight: bold;">📥 FREE Download</a>
                            {% endif %}
                            {% if product.amazon %}
                            <a href="{{ product.amazon }}" target="_blank" style="display: inline-block; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #5f9ea0, #4a8b8e); color: white; text-decoration: none; border-radius: 6px; font-weight: bold;">🛒 Amazon</a>
                            {% endif %}
                            {% if product.gumroad %}
                            <a href="{{ product.gumroad }}" target="_blank" style="display: inline-block; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #FF90E8, #FFA500); color: white; text-decoration: none; border-radius: 6px; font-weight: bold;">💳 Gumroad</a>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            <div class="buy-section">
                <h2 style="color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.9);">🎵 Stream Our Music</h2>
                <div class="music-buttons">
                    {% for link in page.product_links %}
                    <a href="{{ link.url }}" target="_blank" class="music-button">
                        {{ link.icon }} {{ link.name }}
                    </a>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            {% if page.product_images %}
            <div class="product-gallery" style="margin: 3rem 0;">
                <h2 style="color: white; text-align: center; margin-bottom: 2rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.9);">📚 Available Products</h2>
                <div class="gallery-grid">
                    {% for img in page.product_images %}
                    <div class="gallery-item">
                        <img src="{{ img }}" alt="Product Cover" loading="lazy">
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            {% if page.podcast_embed %}
            <div class="podcast-section" style="margin: 2rem 0; padding: 2rem; background: rgba(0,0,0,0.3); border-radius: 8px;">
                <h2 style="color: white; text-align: center; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.9);">🎙️ Listen to Our Podcast</h2>
                {{ page.podcast_embed|safe }}
            </div>
            {% endif %}
            
            {% if page.get("products") %}
            <div class="products-section" style="margin: 3rem 0;">
                <h2 style="color: white; text-align: center; margin-bottom: 2rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.9);">📚 Available Resources</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem;">
                    {% for product in page.products %}
                    <div style="background: rgba(0,0,0,0.5); padding: 2rem; border-radius: 12px; text-align: center;">
                        {% if product.cover %}
                        <img src="{{ product.cover }}" alt="{{ product.title }}" style="width: 100%; border-radius: 8px; margin-bottom: 1rem;">
                        {% endif %}
                        <h3 style="color: white; font-size: 1.1rem; margin-bottom: 1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.7);">{{ product.title }}</h3>
                        <div style="display: flex; gap: 0.5rem; justify-content: center; flex-wrap: wrap;">
                            {% if product.get('download') %}
                            <a href="{{ product.download }}" style="display: inline-block; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #d4af37, #b8960c); color: white; text-decoration: none; border-radius: 6px; font-weight: bold;">📥 FREE Download</a>
                            {% endif %}
                            {% if product.amazon %}
                            <a href="{{ product.amazon }}" target="_blank" style="display: inline-block; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #5f9ea0, #4a8b8e); color: white; text-decoration: none; border-radius: 6px; font-weight: bold;">🛒 Amazon</a>
                            {% endif %}
                            {% if product.gumroad %}
                            <a href="{{ product.gumroad }}" target="_blank" style="display: inline-block; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #FF90E8, #FFA500); color: white; text-decoration: none; border-radius: 6px; font-weight: bold;">💳 Gumroad</a>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            <div class="buy-section">
                {% if page.direct_buy_url %}
                <a href="{{ page.direct_buy_url }}" class="buy-button" style="background: linear-gradient(135deg, #28a745, #218838); font-size: 1.2rem; padding: 1rem 2rem;">
                    🌺 Instant Access - $47
                </a>
                {% endif %}
                
                {% if page.product_url %}
                <a href="{{ page.product_url }}" target="_blank" class="buy-button">
                    🛒 Buy on Amazon
                </a>
                {% endif %}
                
                {% if page.gumroad_url %}
                <a href="{{ page.gumroad_url }}" target="_blank" class="buy-button" style="background: linear-gradient(135deg, #FF90E8, #FFA500);">
                    💳 Buy on Gumroad
                </a>
                {% endif %}
            </div>
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

def load_content():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = DEFAULT_PAGES
            save_content(data)
    else:
        data = DEFAULT_PAGES
        save_content(data)
    return data

def save_content(data):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ===== DIGITAL PRODUCTS HELPER FUNCTIONS =====

def load_digital_products():
    """Load digital products from JSON file"""
    if PRODUCTS_FILE.exists():
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"products": []}

def save_digital_products(products_data):
    """Save digital products to JSON file"""
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(products_data, f, indent=2, ensure_ascii=False)

def generate_product_id():
    """Generate unique product ID"""
    return f"prod_{datetime.now().strftime('%Y%m%d%H%M%S')}"

def render_page(page_id, data):
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
        body_html=md_to_html(page.get("body_md", "")),
        current_page=page_id
    )

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

@app.route("/myron-golden")
def myron_golden_page():
    return render_template_string(MYRON_GOLDEN_TEMPLATE, style=ENHANCED_STYLE)

@app.route("/kingdom_keys")
def kingdom_keys():
    data = load_content()
    return render_page("kingdom_keys", data)

@app.route("/free_booklets")
def free_booklets():
    data = load_content()
    return render_page("free_booklets", data)

@app.route("/download/pamphlet1")
def download_pamphlet1():
    return send_file(BASE / "Kingdom_Keys_1_Kingdom_Inside_You.pdf", mimetype='application/pdf', as_attachment=True)

@app.route("/download/pamphlet2")
def download_pamphlet2():
    return send_file(BASE / "Kingdom_Keys_2_Release_Healing.pdf", mimetype='application/pdf', as_attachment=True)

@app.route("/download/pamphlet3")
def download_pamphlet3():
    return send_file(BASE / "Kingdom_Keys_3_Hawaiian_Grandmas_Prayers.pdf", mimetype='application/pdf', as_attachment=True)

@app.route("/download/pamphlet4")
def download_pamphlet4():
    return send_file(BASE / "Kingdom_Keys_4_Kingdom_Wealth.pdf", mimetype='application/pdf', as_attachment=True)

@app.route("/download/booklet1")
def download_booklet1():
    return send_file(BASE / "Free_Booklet_1_Kingdom_Wealth.pdf", mimetype='application/pdf', as_attachment=True)

@app.route("/download/booklet2")
def download_booklet2():
    return send_file(BASE / "Free_Booklet_2_Kingdom_Wealth_Couples.pdf", mimetype='application/pdf', as_attachment=True)

@app.route("/download/booklet3")
def download_booklet3():
    return send_file(BASE / "Free_Booklet_3_Kingdom_Wellness.pdf", mimetype='application/pdf', as_attachment=True)

@app.route("/download/booklet4")
def download_booklet4():
    return send_file(BASE / "Free_Booklet_4_Kingdom_Wellness_Couples.pdf", mimetype='application/pdf', as_attachment=True)

@app.route("/download/booklet5")
def download_booklet5():
    return send_file(BASE / "Free_Booklet_5_Kingdom_Living.pdf", mimetype='application/pdf', as_attachment=True)

@app.route("/download/booklet6")
def download_booklet6():
    return send_file(BASE / "Free_Booklet_6_Kingdom_Living_Couples.pdf", mimetype='application/pdf', as_attachment=True)

@app.route("/wellness")
def wellness_funnel():
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aloha Wellness — God's Original Design for Your Body</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Lato:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Lato', sans-serif; background: #f9f6f0; color: #2d2d2d; }
        .hero {
            background: linear-gradient(135deg, #1a4a2e 0%, #2E6B3E 50%, #3d8c52 100%);
            color: white; padding: 80px 20px; text-align: center;
        }
        .hero-tag { font-size: 0.9rem; letter-spacing: 3px; text-transform: uppercase; color: #C9A84C; margin-bottom: 20px; }
        .hero h1 { font-family: 'Playfair Display', serif; font-size: clamp(2rem, 5vw, 3.5rem); line-height: 1.2; margin-bottom: 20px; }
        .hero p { font-size: 1.2rem; max-width: 650px; margin: 0 auto 40px; opacity: 0.9; line-height: 1.7; }
        .stats-bar {
            background: #C9A84C; padding: 30px 20px; display: flex;
            justify-content: center; flex-wrap: wrap; gap: 40px;
        }
        .stat { text-align: center; color: #1a1a1a; }
        .stat-number { font-family: 'Playfair Display', serif; font-size: 2.5rem; font-weight: 900; display: block; }
        .stat-label { font-size: 0.85rem; letter-spacing: 1px; text-transform: uppercase; }
        .section { max-width: 800px; margin: 0 auto; padding: 60px 20px; }
        .section h2 { font-family: 'Playfair Display', serif; font-size: clamp(1.6rem, 3vw, 2.2rem); color: #1a4a2e; margin-bottom: 20px; }
        .section p { font-size: 1.05rem; line-height: 1.8; margin-bottom: 18px; color: #3d3d3d; }
        .quote-block {
            background: #1a4a2e; color: white; padding: 40px;
            border-radius: 12px; margin: 40px 0; text-align: center;
        }
        .quote-block p { font-family: 'Playfair Display', serif; font-size: 1.4rem; font-style: italic; color: white; margin-bottom: 10px; }
        .quote-block span { color: #C9A84C; font-size: 0.9rem; }
        .results-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px; margin: 40px 0;
        }
        .result-card {
            background: white; border-radius: 12px; padding: 30px 20px;
            text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border-top: 4px solid #C9A84C;
        }
        .result-icon { font-size: 2.5rem; margin-bottom: 10px; }
        .result-card h3 { font-family: 'Playfair Display', serif; font-size: 1rem; color: #1a4a2e; }
        .cta-section {
            background: linear-gradient(135deg, #1a4a2e, #2E6B3E);
            color: white; padding: 80px 20px; text-align: center;
        }
        .cta-section h2 { font-family: 'Playfair Display', serif; font-size: clamp(1.8rem, 3vw, 2.5rem); margin-bottom: 20px; }
        .cta-section p { font-size: 1.1rem; max-width: 600px; margin: 0 auto 30px; opacity: 0.9; line-height: 1.7; }
        .btn-gold {
            display: inline-block; background: #C9A84C; color: #1a1a1a;
            padding: 18px 45px; border-radius: 50px; font-size: 1.1rem;
            font-weight: 700; text-decoration: none; letter-spacing: 1px;
            transition: all 0.3s; margin-top: 10px;
        }
        .btn-gold:hover { background: #b8973b; transform: translateY(-2px); box-shadow: 0 8px 25px rgba(201,168,76,0.4); }
        .coming-soon {
            background: #fff8e7; border: 2px dashed #C9A84C;
            border-radius: 12px; padding: 40px; text-align: center; margin: 40px 0;
        }
        .coming-soon h3 { font-family: 'Playfair Display', serif; font-size: 1.5rem; color: #1a4a2e; margin-bottom: 10px; }
        .footer { background: #1a1a1a; color: #888; text-align: center; padding: 30px 20px; font-size: 0.85rem; }
        .footer a { color: #C9A84C; text-decoration: none; }
    </style>
</head>
<body>

<div class="hero">
    <p class="hero-tag">Kahu Phil Stephens · Molokaʻi, Hawaiʻi</p>
    <h1>54 Pounds. 9 Months.<br>God's Original Design.</h1>
    <p>A Hawaiian pastor shares the ancient wellness wisdom that helped him lose 54 pounds, shrink 8 inches from his waist, and watch his blood sugar drop from 101 to 83 — without dieting, without suffering, and without giving up the foods he loves.</p>
    <a href="/wellness#get-the-book" class="btn-gold">I Want This For Myself →</a>
</div>

<div class="stats-bar">
    <div class="stat"><span class="stat-number">54 lbs</span><span class="stat-label">Released Naturally</span></div>
    <div class="stat"><span class="stat-number">8"</span><span class="stat-label">Off the Waist</span></div>
    <div class="stat"><span class="stat-number">101→83</span><span class="stat-label">Blood Sugar</span></div>
    <div class="stat"><span class="stat-number">9 mo.</span><span class="stat-label">Transformation</span></div>
</div>

<div class="section">
    <h2>The Kupuna Who Changed Everything</h2>
    <p>A woman in her fifties handed me a health assessment form. The form was clear — score 3 or above and you are in danger. I looked down at my number and then looked up at her and said it myself: "I am dead."</p>
    <p>My score was 11. And here is what made it even more striking — I had already lost the weight by then. I had already seen the transformation in my own body. But their form, built around conventional eating advice that I do not believe helps anyone, had me scoring 11.</p>
    <p>That moment told me everything. By their standard I was failing. By God's original design for the human body I was thriving. The difference between those two things is exactly what this book is about.</p>
</div>

<div class="quote-block">
    <p>"Your body is the temple of the Holy Spirit. God did not design His temple to be sick, exhausted, and struggling. He designed it to thrive."</p>
    <span>— Kahu Phil Stephens</span>
</div>

<div class="section">
    <h2>30 Years in the Saddle Taught Me Something</h2>
    <p>I spent 30 years as a Paniolo — a Hawaiian cowboy — working the ranches of Molokaʻi, Parker Ranch, and beyond. I watched animals every single day. I noticed something that took me years to understand:</p>
    <p>Animals in the wild, eating what God designed them to eat, moving the way God designed them to move — they do not get fat. They do not develop the diseases we struggle with. They live fully until they do not.</p>
    <p>It was only when we penned them, changed their feed, and altered their rhythms that they began to suffer the same things we suffer. That observation sat with me for decades until the day God connected it to what He says in His Word about how He designed the human body.</p>
    <p>That connection became this book.</p>
</div>

<div class="results-grid">
    <div class="result-card"><div class="result-icon">⚖️</div><h3>Natural Weight Release</h3></div>
    <div class="result-card"><div class="result-icon">🩸</div><h3>Blood Sugar Balance</h3></div>
    <div class="result-card"><div class="result-icon">❤️</div><h3>Blood Pressure Normalized</h3></div>
    <div class="result-card"><div class="result-icon">⚡</div><h3>Energy Restored</h3></div>
    <div class="result-card"><div class="result-icon">🌺</div><h3>Hawaiian Wisdom Restored</h3></div>
    <div class="result-card"><div class="result-icon">🙏</div><h3>Spirit, Soul & Body United</h3></div>
</div>

<div class="section">
    <h2>And Then My Wife's Story</h2>
    <p>After 11 years of failed attempts — diets, programs, plans that promised everything and delivered nothing — my wife began applying these same principles. The results she experienced moved me to tears.</p>
    <p>This is not a diet book. It is not a weight loss program. It is a return to what God originally designed — for your body, your health, and your wholeness.</p>
</div>

<div class="coming-soon">
    <h3>📖 Aloha Wellness Volume 2 — Coming Soon</h3>
    <p style="color:#3d3d3d; margin-top:10px;">Whole Life Health: God's Original Design. The deeper journey continues. Get Book 1 now and be the first to know when Volume 2 arrives.</p>
</div>

<div class="cta-section" id="get-the-book">
    <h2>Begin Your Aloha Wellness Journey</h2>
    <p>Book 1 is available now. Start with God's original design for your body and experience the transformation that 30 years of Paniolo wisdom and 8 years of pastoral study revealed.</p>
    <a href="https://keaupuniakeakua.faith/aloha_wellness" class="btn-gold">Get Aloha Wellness Book 1 →</a>
</div>

<div class="footer">
    <p>Ke Aupuni O Ke Akua Press · Molokaʻi, Hawaiʻi · <a href="https://keaupuniakeakua.faith">keaupuniakeakua.faith</a> · <a href="mailto:kahuphil@keaupuniakeakua.faith">kahuphil@keaupuniakeakua.faith</a></p>
    <p style="margin-top:10px;">© 2025 Kahu Phil Stephens. All rights reserved.</p>
</div>

</body>
</html>"""
    return html


@app.route("/kingdom-business")
def kingdom_business_funnel():
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kingdom Business Blueprint — What They Never Taught Us About Money</title>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=DM+Sans:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'DM Sans', sans-serif; background: #0a0a0a; color: #e8e0d0; }
        .hero {
            background: linear-gradient(160deg, #0a0a0a 0%, #1a1200 50%, #0a0a0a 100%);
            border-bottom: 1px solid #C9A84C33;
            padding: 80px 20px; text-align: center;
        }
        .hero-tag { font-size: 0.85rem; letter-spacing: 4px; text-transform: uppercase; color: #C9A84C; margin-bottom: 24px; }
        .hero h1 { font-family: 'Cormorant Garamond', serif; font-size: clamp(2.2rem, 5vw, 4rem); line-height: 1.15; color: #f5edd8; margin-bottom: 24px; }
        .hero h1 span { color: #C9A84C; }
        .hero p { font-size: 1.15rem; max-width: 620px; margin: 0 auto 40px; opacity: 0.85; line-height: 1.8; }
        .stat-strip { background: #C9A84C; padding: 20px; text-align: center; }
        .stat-strip p { color: #0a0a0a; font-weight: 700; font-size: 1.05rem; letter-spacing: 1px; }
        .section { max-width: 780px; margin: 0 auto; padding: 70px 24px; }
        .section h2 { font-family: 'Cormorant Garamond', serif; font-size: clamp(1.8rem, 3vw, 2.6rem); color: #C9A84C; margin-bottom: 24px; }
        .section p { font-size: 1.05rem; line-height: 1.85; margin-bottom: 18px; color: #ccc5b5; }
        .divider { border: none; border-top: 1px solid #C9A84C33; margin: 0; }
        .products { background: #111; padding: 70px 20px; }
        .products h2 { font-family: 'Cormorant Garamond', serif; font-size: clamp(1.8rem, 3vw, 2.4rem); color: #C9A84C; text-align: center; margin-bottom: 50px; }
        .products-grid { max-width: 800px; margin: 0 auto; display: flex; flex-direction: column; gap: 24px; }
        .product-card {
            background: #1a1a1a; border: 1px solid #C9A84C33; border-radius: 12px;
            padding: 30px; display: flex; justify-content: space-between;
            align-items: center; gap: 20px; flex-wrap: wrap;
        }
        .product-card h3 { font-family: 'Cormorant Garamond', serif; font-size: 1.4rem; color: #f5edd8; margin-bottom: 6px; }
        .product-card p { font-size: 0.95rem; color: #999; line-height: 1.6; margin: 0; }
        .product-level { font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase; color: #C9A84C; margin-bottom: 8px; }
        .btn-gold {
            display: inline-block; background: #C9A84C; color: #0a0a0a;
            padding: 14px 30px; border-radius: 50px; font-size: 0.95rem;
            font-weight: 700; text-decoration: none; white-space: nowrap;
            transition: all 0.3s;
        }
        .btn-gold:hover { background: #b8973b; transform: translateY(-2px); }
        .cta-section { background: linear-gradient(135deg, #1a1200, #0a0a0a); padding: 80px 20px; text-align: center; border-top: 1px solid #C9A84C33; }
        .cta-section h2 { font-family: 'Cormorant Garamond', serif; font-size: clamp(2rem, 4vw, 3rem); color: #f5edd8; margin-bottom: 20px; }
        .cta-section p { font-size: 1.1rem; color: #ccc5b5; max-width: 580px; margin: 0 auto 36px; line-height: 1.8; }
        .transparency { background: #111; border: 1px solid #C9A84C55; border-radius: 12px; padding: 30px; max-width: 680px; margin: 0 auto 40px; text-align: left; }
        .transparency h4 { color: #C9A84C; font-size: 0.85rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; }
        .transparency p { color: #999; font-size: 0.95rem; line-height: 1.7; margin: 0; }
        .footer { background: #050505; color: #555; text-align: center; padding: 30px 20px; font-size: 0.85rem; border-top: 1px solid #1a1a1a; }
        .footer a { color: #C9A84C; text-decoration: none; }
    </style>
</head>
<body>

<div class="hero">
    <p class="hero-tag">Kahu Phil Stephens · Molokaʻi, Hawaiʻi</p>
    <h1>What They Never Taught Us<br>About <span>Money</span></h1>
    <p>On Molokaʻi, over 70% of our community depends on government assistance. I spent 30 years as a Paniolo and 8 years as a Kahu — and nobody ever taught me the Kingdom principles of wealth. Until I found them myself.</p>
    <a href="https://kahuphil.systeme.io/9868a94d" class="btn-gold">Send Me the Free Kingdom Blueprint →</a>
</div>

<div class="stat-strip">
    <p>FREE · The Kingdom Business Blueprint · Instant Access · No Credit Card Required</p>
</div>

<div class="section">
    <h2>The Question That Woke Me Up</h2>
    <p>If God owns everything — and Scripture is clear that He does — then why are so many of His people broke? Why are the most faithful, most prayerful, most hardworking people in my community struggling to make ends meet?</p>
    <p>I asked that question for years. Then I started finding answers — in Scripture, in the teachings of men like Myron Golden, and in the ancient wisdom of our Hawaiian kūpuna who understood abundance long before the modern world got confused about money.</p>
    <p>What I found changed the way I think about business, income, and what God actually intends for His people financially. And I want to share it with you — starting with a free blueprint that lays it all out.</p>
</div>

<hr class="divider">

<div class="section">
    <h2>Resources That Helped Me Most</h2>
    <p>I do not promote anything I have not personally studied and found valuable. These are the Kingdom business resources that have shaped my thinking — offered here in order from lowest cost to highest, because everyone deserves a starting point.</p>
</div>

<div class="products">
    <h2>Kingdom Business Resources</h2>
    <div class="products-grid">

        <div class="product-card">
            <div>
                <div class="product-level">Entry Level · Book</div>
                <h3>Trash Man to Cash Man</h3>
                <p>Myron Golden's foundational book on how ordinary people create extraordinary income using biblical principles.</p>
            </div>
            <a href="https://www.trashmantocashman.com/tmcm-book?affiliate_id=4319525" class="btn-gold" target="_blank">Get the Book →</a>
        </div>

        <div class="product-card">
            <div>
                <div class="product-level">Entry Level · Book</div>
                <h3>Boss Moves</h3>
                <p>The strategies successful entrepreneurs use to think differently, act boldly, and create lasting wealth.</p>
            </div>
            <a href="https://www.bossmovesbook.com/bossmoves?affiliate_id=4319525" class="btn-gold" target="_blank">Get the Book →</a>
        </div>

        <div class="product-card">
            <div>
                <div class="product-level">Challenge · Training</div>
                <h3>Make More Offers Challenge</h3>
                <p>A live challenge that teaches you how to craft irresistible offers — the foundation of any successful business.</p>
            </div>
            <a href="https://www.makemoreofferschallenge.com/mmoc?affiliate_id=4319525" class="btn-gold" target="_blank">Join the Challenge →</a>
        </div>

        <div class="product-card">
            <div>
                <div class="product-level">Intermediate · Course</div>
                <h3>Mind Over Money Mastery</h3>
                <p>Transform your relationship with money at the deepest level — mindset, belief, and Kingdom identity.</p>
            </div>
            <a href="https://www.mindovermoneymastery.com/momm?affiliate_id=4319525" class="btn-gold" target="_blank">Learn More →</a>
        </div>

        <div class="product-card">
            <div>
                <div class="product-level">Live Event</div>
                <h3>Offer Mastery Live</h3>
                <p>An immersive live event to master the art and science of creating offers that sell themselves.</p>
            </div>
            <a href="https://www.offermasterylive.com/offer-mastery-livevetfk4nn?affiliate_id=4319525" class="btn-gold" target="_blank">Reserve Your Seat →</a>
        </div>

        <div class="product-card">
            <div>
                <div class="product-level">Complete System</div>
                <h3>Golden OPS</h3>
                <p>The complete Kingdom business operating system. Everything you need to build, scale, and sustain a thriving business.</p>
            </div>
            <a href="https://www.mygoldenops.com/golden-opsm1y8y7bx?affiliate_id=4319525" class="btn-gold" target="_blank">See the System →</a>
        </div>

    </div>
</div>

<div class="cta-section">
    <h2>Start Here — It Is Free</h2>
    <p>Get the Kingdom Business Blueprint and begin understanding what the Bible actually says about wealth, business, and God's original design for your financial life.</p>
    <div class="transparency">
        <h4>A Pastor's Transparency</h4>
        <p>Some of the links above are affiliate links. If you purchase through them I may receive a commission — at no extra cost to you. I share these resources because I have found them genuinely valuable in my own Kingdom journey. I will never recommend something I do not believe in. That is my covenant with you.</p>
    </div>
    <a href="https://kahuphil.systeme.io/9868a94d" class="btn-gold">Send Me the Free Blueprint →</a>
</div>

<div class="footer">
    <p>Ke Aupuni O Ke Akua Press · Molokaʻi, Hawaiʻi · <a href="https://keaupuniakeakua.faith">keaupuniakeakua.faith</a> · <a href="mailto:kahuphil@keaupuniakeakua.faith">kahuphil@keaupuniakeakua.faith</a></p>
    <p style="margin-top:10px;">© 2025 Kahu Phil Stephens. All rights reserved.</p>
</div>

</body>
</html>"""
    return html


if __name__ == "__main__":
    if not DATA_FILE.exists():
        save_content(DEFAULT_PAGES)
    
    port = int(os.environ.get("PORT", 5000))
    print("🌺 Starting Ke Aupuni O Ke Akua website...")
    print(f"🌊 Visit: http://localhost:{port}")
    print("=" * 50)
    app.run(host="0.0.0.0", port=port, debug=True)

@app.route("/static/covers/<filename>")
def serve_cover(filename):
    cover_path = BASE / filename
    if cover_path.exists():
        return send_file(cover_path, mimetype='image/jpeg')
    abort(404)

ADMIN_PASSWORD = "Kingdom2024"

@app.route("/kahu")
def admin_panel():
    data = load_content()
    pages = data.get("pages", data)
    
    admin_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - Ke Aupuni O Ke Akua</title>
    <style>
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
        
        .edit-btn {
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
        }
        
        .edit-btn:hover {
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
    </style>
</head>
<body>
    <div class="container">
        <h1>🌺 Admin Panel</h1>
        <p class="subtitle">Manage your website content</p>
        
        <div class="page-list">
"""
    
    for page_id, page_data in pages.items():
        page_title = page_data.get("title", page_id)
        hero_image = page_data.get("hero_image", "")
        product_url = page_data.get("product_url", "N/A")
        gallery_images = page_data.get("gallery_images", [])
        product_links = page_data.get("product_links", [])
        
        admin_html += f"""
            <div class="page-card">
                <div class="page-title">{page_title}</div>
                <div class="page-info">
                    <div><strong>Page ID:</strong> {page_id}</div>
                    <div><strong>Hero Image:</strong> {hero_image[:60]}...</div>
"""
        
        if product_url != "N/A":
            admin_html += f'                    <div><strong>Product URL:</strong> <a href="{product_url}" target="_blank">View</a></div>\n'
        
        if product_links:
            admin_html += f'                    <div><strong>Music Links:</strong> {len(product_links)} platforms</div>\n'
        
        if gallery_images:
            admin_html += f'                    <div><strong>Gallery:</strong> {len(gallery_images)} images</div>\n'
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
        
        <div style="margin-top: 2rem; padding-top: 2rem; border-top: 2px solid #e9ecef;">
            <a href="/admin/products" class="edit-btn" style="display: inline-block; margin-right: 1rem;">💰 Manage Digital Products</a>
            <a href="/" class="back-btn" style="display: inline-block;">← Back to Website</a>
        </div>
    </div>
</body>
</html>"""
    
    return admin_html

@app.route("/admin/edit/<page_id>", methods=["GET", "POST"])
def edit_page(page_id):
    data = load_content()
    pages = data.get("pages", data)
    
    if page_id not in pages:
        abort(404)
    
    if request.method == "POST":
        pages[page_id]["title"] = request.form.get("title", "")
        pages[page_id]["hero_image"] = request.form.get("hero_image", "")
        pages[page_id]["body_md"] = request.form.get("body_md", "")
        
        direct_buy_url = request.form.get("direct_buy_url", "").strip()
        if direct_buy_url:
            pages[page_id]["direct_buy_url"] = direct_buy_url
        elif "direct_buy_url" in pages[page_id]:
            del pages[page_id]["direct_buy_url"]
        
        product_url = request.form.get("product_url", "").strip()
        if product_url:
            pages[page_id]["product_url"] = product_url
        elif "product_url" in pages[page_id]:
            del pages[page_id]["product_url"]
        
        gumroad_url = request.form.get("gumroad_url", "").strip()
        if gumroad_url:
            pages[page_id]["gumroad_url"] = gumroad_url
        elif "gumroad_url" in pages[page_id]:
            del pages[page_id]["gumroad_url"]
        
        podcast_embed = request.form.get("podcast_embed", "").strip()
        if podcast_embed:
            pages[page_id]["podcast_embed"] = podcast_embed
        elif "podcast_embed" in pages[page_id]:
            del pages[page_id]["podcast_embed"]
        
        product_images_raw = request.form.get("product_images", "")
        if product_images_raw:
            pages[page_id]["product_images"] = [line.strip() for line in product_images_raw.split("\n") if line.strip()]
        else:
            pages[page_id]["product_images"] = []
        
        gallery_str = request.form.get("gallery_images", "").strip()
        if gallery_str:
            gallery_images = [img.strip() for img in gallery_str.split("\n") if img.strip()]
            pages[page_id]["gallery_images"] = gallery_images
        elif "gallery_images" in pages[page_id]:
            del pages[page_id]["gallery_images"]
        
        links_str = request.form.get("product_links", "").strip()
        if links_str:
            links = []
            for line in links_str.split("\n"):
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        links.append({
                            "name": parts[0].strip(),
                            "url": parts[1].strip(),
                            "icon": parts[2].strip()
                        })
            if links:
                pages[page_id]["product_links"] = links
        elif "product_links" in pages[page_id]:
            del pages[page_id]["product_links"]
        
        save_content({"pages": pages, "order": data.get("order", ORDER)})
        return redirect("/kahu")
    
    page = pages[page_id]
    
    gallery_str = "\n".join(page.get("gallery_images", []))
    
    product_images_str = ""
    if page.get("product_images"):
        product_images_str = "\n".join(page["product_images"])
    
    links_str = ""
    if "product_links" in page:
        links_str = "\n".join([
            f"{link['name']}|{link['url']}|{link['icon']}"
            for link in page["product_links"]
        ])
    
    edit_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit {page['title']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        
        h1 {{
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }}
        
        .subtitle {{
            color: #7f8c8d;
            margin-bottom: 2rem;
        }}
        
        .form-group {{
            margin-bottom: 1.5rem;
        }}
        
        label {{
            display: block;
            color: #2c3e50;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        
        input[type="text"],
        textarea {{
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1rem;
            font-family: inherit;
            transition: border-color 0.3s ease;
        }}
        
        input[type="text"]:focus,
        textarea:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        textarea {{
            min-height: 200px;
            resize: vertical;
        }}
        
        .help-text {{
            font-size: 0.85rem;
            color: #6c757d;
            margin-top: 0.25rem;
        }}
        
        .btn-group {{
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
        }}
        
        .btn {{
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-block;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }}
        
        .btn-secondary {{
            background: #6c757d;
            color: white;
        }}
        
        .btn-secondary:hover {{
            background: #5a6268;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>✏️ Edit Page</h1>
        <p class="subtitle">{page['title']}</p>
        
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
                <label for="body_md">Content (Markdown)</label>
                <textarea id="body_md" name="body_md" required>{page.get('body_md', '')}</textarea>
                <div class="help-text">Use Markdown formatting (## for headings, ** for bold, **![]()** for images).</div>
            </div>
            
            <div class="form-group">
                <label for="direct_buy_url">🌺 Direct Buy URL (Your Website Checkout)</label>
                <input type="text" id="direct_buy_url" name="direct_buy_url" value="{page.get('direct_buy_url', '')}">
                <div class="help-text">Paste your product checkout URL here - e.g. /checkout/prod_20260216123456 - This shows the green "Instant Access - $47" button on your page!</div>
            </div>
            
            <div class="form-group">
                <label for="product_url">Product/Buy Button URL (Optional)</label>
                <input type="text" id="product_url" name="product_url" value="{page.get('product_url', '')}">
                <div class="help-text">Amazon or other product link.</div>
            </div>
            
            <div class="form-group">
                <label for="gumroad_url">Gumroad Product URL (Optional)</label>
                <input type="text" id="gumroad_url" name="gumroad_url" value="{page.get('gumroad_url', '')}">
                <div class="help-text">Your Gumroad product link (e.g., https://yourusername.gumroad.com/l/product)</div>
            </div>
            
            <div class="form-group">
                <label for="podcast_embed">Podcast Embed Code (Optional)</label>
                <textarea id="podcast_embed" name="podcast_embed" style="min-height: 100px;">{page.get('podcast_embed', '')}</textarea>
                <div class="help-text">Paste your podcast embed code (Spotify, Apple, etc.)</div>
            </div>
            
            <div class="form-group">
                <label for="product_images">Product Images - Book Covers, Planner Covers, etc. (One URL per line)</label>
                <textarea id="product_images" name="product_images" style="min-height: 120px;">{product_images_str}</textarea>
                <div class="help-text">Direct image URLs only (https://i.imgur.com/ABC123.jpg) - one per line. These will display in a grid on your page.</div>
            </div>
            
            <div class="form-group">
                <label for="gallery_images">Gallery Images (Optional - One URL per line)</label>
                <textarea id="gallery_images" name="gallery_images" style="min-height: 100px;">{gallery_str}</textarea>
                <div class="help-text">For CD covers: /static/covers/cover1.jpg (one per line)</div>
            </div>
            
            <div class="form-group">
                <label for="product_links">Music Platform Links (Optional - Format: Name|URL|Icon)</label>
                <textarea id="product_links" name="product_links" style="min-height: 100px;">{links_str}</textarea>
                <div class="help-text">Example: Amazon Music|https://music.amazon.com/...|🛒</div>
            </div>
            
            <div class="btn-group">
                <button type="submit" class="btn btn-primary">💾 Save Changes</button>
                <a href="/kahu" class="btn btn-secondary">← Cancel</a>
            </div>
        </form>
    </div>
</body>
</html>"""
    
    return edit_html

# ===== DIGITAL PRODUCTS ROUTES =====

@app.route("/admin/products")
def admin_products():
    """Digital Products Management Page"""
    products_data = load_digital_products()
    products = products_data.get("products", [])
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Products Manager</title>
    <style>
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
        }
        
        .actions {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.2s ease;
            border: none;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .products-grid {
            display: grid;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .product-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 12px;
            border: 2px solid #e9ecef;
            transition: all 0.3s ease;
        }
        
        .product-card:hover {
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        }
        
        .product-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 1rem;
        }
        
        .product-title {
            font-size: 1.25rem;
            color: #2c3e50;
            font-weight: 600;
            flex: 1;
        }
        
        .product-price {
            font-size: 1.5rem;
            color: #28a745;
            font-weight: bold;
        }
        
        .product-info {
            display: grid;
            gap: 0.5rem;
            margin-bottom: 1rem;
            font-size: 0.9rem;
            color: #495057;
        }
        
        .product-info strong {
            color: #2c3e50;
        }
        
        .product-actions {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }
        
        .btn-sm {
            padding: 0.5rem 1rem;
            font-size: 0.875rem;
        }
        
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .status-active {
            background: #d4edda;
            color: #155724;
        }
        
        .status-inactive {
            background: #f8d7da;
            color: #721c24;
        }
        
        .empty-state {
            text-align: center;
            padding: 3rem;
            color: #6c757d;
        }
        
        .empty-state h3 {
            margin-bottom: 1rem;
            color: #495057;
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
        }
        
        .modal-content {
            background: white;
            margin: 5% auto;
            padding: 2rem;
            border-radius: 16px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: #2c3e50;
            font-weight: 600;
        }
        
        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1rem;
            font-family: inherit;
        }
        
        .form-group textarea {
            min-height: 100px;
            resize: vertical;
        }
        
        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .form-actions {
            display: flex;
            gap: 1rem;
            justify-content: flex-end;
            margin-top: 2rem;
        }
        
        .close {
            float: right;
            font-size: 2rem;
            font-weight: bold;
            color: #aaa;
            cursor: pointer;
        }
        
        .close:hover {
            color: #000;
        }
        
        .file-info {
            font-size: 0.875rem;
            color: #6c757d;
            margin-top: 0.5rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💰 Digital Products Manager</h1>
        <p class="subtitle">Sell your ebooks, planners, and digital downloads directly from your website</p>
        
        <div class="actions">
            <button class="btn btn-primary" onclick="openAddModal()">➕ Add New Product</button>
            <a href="/kahu" class="btn btn-secondary">← Back to Admin</a>
            <a href="/" class="btn btn-secondary">🏠 View Website</a>
        </div>
"""
    
    if products:
        html += '<div class="products-grid">'
        for product in products:
            status_class = "status-active" if product.get("active", True) else "status-inactive"
            status_text = "Active" if product.get("active", True) else "Inactive"
            
            html += f"""
            <div class="product-card">
                <div class="product-header">
                    <div class="product-title">{product['name']}</div>
                    <div class="product-price">${product['price']}</div>
                </div>
                <div class="product-info">
                    <div><span class="status-badge {status_class}">{status_text}</span></div>
                    <div><strong>Description:</strong> {product.get('description', 'No description')[:100]}...</div>
                    <div><strong>File:</strong> {product.get('filename', 'Not uploaded')}</div>
                    <div><strong>Downloads:</strong> {product.get('downloads', 0)}</div>
                    <div><strong>Sales:</strong> ${product.get('total_sales', 0):.2f}</div>
                    <div><strong>Product ID:</strong> {product['id']}</div>
                </div>
                <div class="product-actions">
                    <a href="/product/{product['id']}" class="btn btn-sm btn-primary" target="_blank">👁️ View Sales Page</a>
                    <button class="btn btn-sm btn-success" onclick="editProduct('{product['id']}')">✏️ Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteProduct('{product['id']}')">🗑️ Delete</button>
                </div>
            </div>
            """
        html += '</div>'
    else:
        html += """
        <div class="empty-state">
            <h3>📦 No Products Yet</h3>
            <p>Start selling by adding your first digital product!</p>
            <p style="margin-top: 1rem;">Click "Add New Product" above to get started.</p>
        </div>
        """
    
    html += """
    </div>
    
    <div id="addModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeAddModal()">&times;</span>
            <h2>➕ Add New Product</h2>
            <form id="addProductForm" action="/admin/products/add" method="POST" enctype="multipart/form-data">
                
                <div class="form-group">
                    <label for="name">📌 Product Name *</label>
                    <input type="text" id="name" name="name" required placeholder="e.g., Aloha Wellness: Island-Inspired Natural Weight Management">
                    <div class="file-info">The title customers will see on the sales page</div>
                </div>
                
                <div class="form-group">
                    <label for="description">📝 Description *</label>
                    <textarea id="description" name="description" required style="min-height: 150px;" placeholder="Describe what customers will get, what problems it solves, and why they need it...">A respectful integration of Hawaiian wisdom and modern science for sustainable health. Discover the Four Pillars of Aloha Wellness - Malama, Pono, Ohana, and Aloha - and how they transform your relationship with food, your body, and your health. Written by Kahu Phil Stephens from Molokai, this cutting-edge book combines ancient Hawaiian cultural wisdom with evidence-based nutritional science for lasting, sustainable wellness.</textarea>
                    <div class="file-info">This appears on your sales page. Be descriptive - sell the transformation!</div>
                </div>
                
                <div class="form-group">
                    <label for="price">💰 Price (USD) *</label>
                    <input type="number" id="price" name="price" step="0.01" min="0" required value="47.00">
                    <div class="file-info">Your price is $47.00 - customers pay this via PayPal</div>
                </div>
                
                <div class="form-group">
                    <label for="file">📁 Product File * (The actual ebook customers will download)</label>
                    <input type="file" id="file" name="file" required accept=".pdf,.epub,.zip,.html">
                    <div class="file-info">
                        ✅ Upload your <strong>aloha_wellness_ebook_COMPLETE.html</strong> file here<br>
                        📌 Find it in your Downloads folder from this session<br>
                        📋 Accepted formats: PDF, HTML, EPUB, ZIP (max 50MB)
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="category">🏷️ Category</label>
                    <select id="category" name="category">
                        <option value="ebook" selected>Ebook</option>
                        <option value="planner">Planner</option>
                        <option value="booklet">Booklet</option>
                        <option value="course">Course</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="cover_image">🖼️ Cover Image URL (optional but recommended!)</label>
                    <input type="url" id="cover_image" name="cover_image" value="https://i.imgur.com/xGeWW3Q.jpeg" placeholder="https://i.imgur.com/...">
                    <div class="file-info">Pre-filled with your Aloha Wellness image. Change if needed.</div>
                </div>
                
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeAddModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">🌺 Add Product & Start Selling!</button>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        function openAddModal() {
            document.getElementById('addModal').style.display = 'block';
        }
        
        function closeAddModal() {
            document.getElementById('addModal').style.display = 'none';
        }
        
        function editProduct(productId) {
            window.location.href = '/admin/products/edit/' + productId;
        }
        
        function deleteProduct(productId) {
            if (confirm('Are you sure you want to delete this product? This cannot be undone.')) {
                fetch('/admin/products/delete/' + productId, {
                    method: 'POST'
                }).then(response => {
                    if (response.ok) {
                        location.reload();
                    } else {
                        alert('Error deleting product');
                    }
                });
            }
        }
        
        window.onclick = function(event) {
            const modal = document.getElementById('addModal');
            if (event.target == modal) {
                closeAddModal();
            }
        }
    </script>
</body>
</html>
"""
    
    return html

@app.route("/admin/products/add", methods=["POST"])
def add_product():
    """Add new digital product"""
    name = request.form.get("name")
    description = request.form.get("description")
    price = float(request.form.get("price", 0))
    category = request.form.get("category", "ebook")
    cover_image = request.form.get("cover_image", "")
    
    file = request.files.get("file")
    if not file:
        return "No file uploaded", 400
    
    filename = secure_filename(file.filename)
    product_id = generate_product_id()
    file_path = PRODUCTS_FOLDER / f"{product_id}_{filename}"
    file.save(file_path)
    
    products_data = load_digital_products()
    new_product = {
        "id": product_id,
        "name": name,
        "description": description,
        "price": price,
        "category": category,
        "filename": filename,
        "file_path": str(file_path),
        "cover_image": cover_image,
        "active": True,
        "downloads": 0,
        "total_sales": 0,
        "created_at": datetime.now().isoformat()
    }
    
    products_data["products"].append(new_product)
    save_digital_products(products_data)
    
    return redirect("/admin/products")

@app.route("/admin/products/edit/<product_id>", methods=["GET", "POST"])
def edit_product_route(product_id):
    """Edit existing product"""
    products_data = load_digital_products()
    product = next((p for p in products_data["products"] if p["id"] == product_id), None)
    
    if not product:
        abort(404)
    
    if request.method == "POST":
        product["name"] = request.form.get("name")
        product["description"] = request.form.get("description")
        product["price"] = float(request.form.get("price", 0))
        product["category"] = request.form.get("category", "ebook")
        product["cover_image"] = request.form.get("cover_image", "")
        product["active"] = request.form.get("active") == "on"
        
        save_digital_products(products_data)
        return redirect("/admin/products")
    
    checked = "checked" if product.get("active", True) else ""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Product - {product['name']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        
        h1 {{
            color: #2c3e50;
            margin-bottom: 2rem;
        }}
        
        .form-group {{
            margin-bottom: 1.5rem;
        }}
        
        .form-group label {{
            display: block;
            margin-bottom: 0.5rem;
            color: #2c3e50;
            font-weight: 600;
        }}
        
        .form-group input,
        .form-group textarea,
        .form-group select {{
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1rem;
            font-family: inherit;
        }}
        
        .form-group textarea {{
            min-height: 100px;
            resize: vertical;
        }}
        
        .checkbox-group {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .checkbox-group input {{
            width: auto;
        }}
        
        .form-actions {{
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
        }}
        
        .btn {{
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            border: none;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .btn-secondary {{
            background: #6c757d;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Edit Product</h1>
        
        <form method="POST">
            <div class="form-group">
                <label for="name">Product Name *</label>
                <input type="text" id="name" name="name" value="{product['name']}" required>
            </div>
            
            <div class="form-group">
                <label for="description">Description *</label>
                <textarea id="description" name="description" required>{product['description']}</textarea>
            </div>
            
            <div class="form-group">
                <label for="price">Price (USD) *</label>
                <input type="number" id="price" name="price" step="0.01" min="0" value="{product['price']}" required>
            </div>
            
            <div class="form-group">
                <label for="category">Category</label>
                <select id="category" name="category">
                    <option value="ebook" {"selected" if product.get('category') == 'ebook' else ""}>Ebook</option>
                    <option value="planner" {"selected" if product.get('category') == 'planner' else ""}>Planner</option>
                    <option value="booklet" {"selected" if product.get('category') == 'booklet' else ""}>Booklet</option>
                    <option value="course" {"selected" if product.get('category') == 'course' else ""}>Course</option>
                    <option value="other" {"selected" if product.get('category') == 'other' else ""}>Other</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="cover_image">Cover Image URL</label>
                <input type="url" id="cover_image" name="cover_image" value="{product.get('cover_image', '')}">
            </div>
            
            <div class="form-group">
                <div class="checkbox-group">
                    <input type="checkbox" id="active" name="active" {checked}>
                    <label for="active" style="margin-bottom: 0;">Product is Active (visible for sale)</label>
                </div>
            </div>
            
            <div class="form-group">
                <label>Current File</label>
                <div style="padding: 0.75rem; background: #f8f9fa; border-radius: 8px;">
                    {product['filename']}
                </div>
            </div>
            
            <div class="form-actions">
                <a href="/admin/products" class="btn btn-secondary">Cancel</a>
                <button type="submit" class="btn btn-primary">Save Changes</button>
            </div>
        </form>
    </div>
</body>
</html>
"""
    
    return html

@app.route("/admin/products/delete/<product_id>", methods=["POST"])
def delete_product(product_id):
    """Delete a product"""
    from flask import jsonify
    
    products_data = load_digital_products()
    product = next((p for p in products_data["products"] if p["id"] == product_id), None)
    
    if product:
        file_path = Path(product["file_path"])
        if file_path.exists():
            file_path.unlink()
        
        products_data["products"] = [p for p in products_data["products"] if p["id"] != product_id]
        save_digital_products(products_data)
    
    return jsonify({"success": True})

@app.route("/product/<product_id>")
def product_page(product_id):
    """Public product sales page"""
    products_data = load_digital_products()
    product = next((p for p in products_data["products"] if p["id"] == product_id), None)
    
    if not product or not product.get("active", True):
        abort(404)
    
    cover_image = product.get("cover_image", "https://i.imgur.com/wmHEyDo.png")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{product['name']} - Ke Aupuni O Ke Akua</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        
        .product-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
        }}
        
        .product-header h1 {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}
        
        .product-content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            padding: 2rem;
        }}
        
        .product-image {{
            text-align: center;
        }}
        
        .product-image img {{
            max-width: 100%;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .product-details h2 {{
            color: #2c3e50;
            margin-bottom: 1rem;
        }}
        
        .product-description {{
            color: #495057;
            line-height: 1.6;
            margin-bottom: 2rem;
        }}
        
        .price {{
            font-size: 3rem;
            color: #28a745;
            font-weight: bold;
            margin-bottom: 2rem;
        }}
        
        .buy-button {{
            display: block;
            width: 100%;
            padding: 1.5rem;
            background: #28a745;
            color: white;
            text-align: center;
            font-size: 1.25rem;
            font-weight: bold;
            border-radius: 8px;
            text-decoration: none;
            transition: all 0.3s ease;
        }}
        
        .buy-button:hover {{
            background: #218838;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
        }}
        
        .features {{
            list-style: none;
            margin-bottom: 2rem;
        }}
        
        .features li {{
            padding: 0.5rem 0;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .features li:before {{
            content: "✓ ";
            color: #28a745;
            font-weight: bold;
            margin-right: 0.5rem;
        }}
        
        @media (max-width: 768px) {{
            .product-content {{
                grid-template-columns: 1fr;
            }}
            
            .product-header h1 {{
                font-size: 1.75rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="product-header">
            <h1>{product['name']}</h1>
            <p>From Ke Aupuni O Ke Akua Press</p>
        </div>
        
        <div class="product-content">
            <div class="product-image">
                <img src="{cover_image}" alt="{product['name']}">
            </div>
            
            <div class="product-details">
                <h2>About This Product</h2>
                <div class="product-description">
                    {product['description']}
                </div>
                
                <ul class="features">
                    <li>Instant digital download</li>
                    <li>Read on any device</li>
                    <li>Full lifetime access</li>
                    <li>No DRM - yours forever</li>
                </ul>
                
                <div class="price">${product['price']}</div>
                
                <a href="mailto:keaupuniakeakua@gmail.com?subject=Purchase: {product['name']}&body=I would like to purchase {product['name']} for ${product['price']}. Please send me payment instructions." class="buy-button">
                    📧 Email to Purchase
                </a>
                <p style="text-align: center; margin-top: 1rem; color: #6c757d; font-size: 0.9rem;">
                    Click to email for payment instructions (PayPal, Venmo, or Zelle)
                </p>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    return html

@app.route("/download/<product_id>")
def download_product(product_id):
    """Download product file"""
    products_data = load_digital_products()
    product = next((p for p in products_data["products"] if p["id"] == product_id), None)
    
    if not product:
        abort(404)
    
    product["downloads"] = product.get("downloads", 0) + 1
    save_digital_products(products_data)
    
    file_path = Path(product["file_path"])
    return send_file(file_path, as_attachment=True, download_name=product["filename"])


# ===== PAYPAL API CHECKOUT SYSTEM =====

import urllib.request
import urllib.parse
import base64

PAYPAL_CLIENT_ID = "Af3hvjHUPRVuFeQ8xO_T18V234j-B-qvN9I9ydlWnEU9M0vKKOVyMw0si6r-N47Y_fg-Mw35VvAifkZ6"
PAYPAL_CLIENT_SECRET = "ECBlGV46JMgXmIk2H9u_i-kyMUO1X5--GYkjqYlqf2QMv4LbrWFhUNwd3rzCswN1-UfrwbPrk5WIUPHQ"
PAYPAL_BASE_URL = "https://api-m.paypal.com"

def get_paypal_access_token():
    """Get PayPal access token using Client ID and Secret"""
    credentials = f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()
    
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
    req = urllib.request.Request(
        f"{PAYPAL_BASE_URL}/v1/oauth2/token",
        data=data,
        headers={
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        return result["access_token"]

def create_paypal_order(product_id, product_name, price):
    """Create a PayPal order and return approval URL"""
    access_token = get_paypal_access_token()
    
    order_data = json.dumps({
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": str(price)
            },
            "description": product_name,
            "custom_id": product_id
        }],
        "application_context": {
            "brand_name": "Ke Aupuni O Ke Akua Press",
            "landing_page": "BILLING",
            "user_action": "PAY_NOW",
            "return_url": "https://keaupuniakeakua.faith/paypal/success",
            "cancel_url": "https://keaupuniakeakua.faith/paypal/cancel"
        }
    }).encode()
    
    req = urllib.request.Request(
        f"{PAYPAL_BASE_URL}/v2/checkout/orders",
        data=order_data,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        
        # Find the approval URL
        for link in result.get("links", []):
            if link["rel"] == "approve":
                return result["id"], link["href"]
        
        return None, None

def capture_paypal_order(order_id):
    """Capture payment after customer approves"""
    access_token = get_paypal_access_token()
    
    req = urllib.request.Request(
        f"{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture",
        data=b"{}",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    )
    
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

@app.route("/checkout/<product_id>")
def checkout_page(product_id):
    """Checkout page with PayPal button"""
    products_data = load_digital_products()
    product = next((p for p in products_data["products"] if p["id"] == product_id), None)
    
    if not product:
        abort(404)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Checkout - {product['name']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 2rem;
            padding-bottom: 2rem;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .header h1 {{
            color: #2c3e50;
            font-size: 1.75rem;
            margin-bottom: 0.5rem;
        }}
        
        .product-summary {{
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .product-name {{
            font-weight: 600;
            color: #2c3e50;
            font-size: 1.1rem;
        }}
        
        .product-type {{
            color: #6c757d;
            font-size: 0.9rem;
            margin-top: 0.25rem;
        }}
        
        .product-price {{
            font-size: 2rem;
            color: #28a745;
            font-weight: bold;
        }}
        
        .features {{
            list-style: none;
            margin-bottom: 2rem;
        }}
        
        .features li {{
            padding: 0.5rem 0;
            border-bottom: 1px solid #e9ecef;
            color: #495057;
        }}
        
        .features li:before {{
            content: "✓ ";
            color: #28a745;
            font-weight: bold;
        }}
        
        .paypal-section {{
            text-align: center;
        }}
        
        .paypal-section p {{
            color: #6c757d;
            font-size: 0.9rem;
            margin-top: 1rem;
        }}
        
        #paypal-button-container {{
            margin: 1rem 0;
        }}
        
        .secure-badge {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            color: #6c757d;
            font-size: 0.85rem;
            margin-top: 1rem;
        }}
        
        .back-link {{
            display: block;
            text-align: center;
            margin-top: 1.5rem;
            color: #6c757d;
            text-decoration: none;
            font-size: 0.9rem;
        }}
        
        .back-link:hover {{
            color: #2c3e50;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌺 Complete Your Purchase</h1>
            <p style="color: #6c757d;">Ke Aupuni O Ke Akua Press</p>
        </div>
        
        <div class="product-summary">
            <div>
                <div class="product-name">{product['name']}</div>
                <div class="product-type">Digital Ebook - Instant Download</div>
            </div>
            <div class="product-price">${product['price']}</div>
        </div>
        
        <ul class="features">
            <li>Instant digital download after payment</li>
            <li>Read on any device - phone, tablet, computer</li>
            <li>Full lifetime access</li>
            <li>From Kahu Phil Stephens, Molokaʻi</li>
        </ul>
        
        <div class="paypal-section">
            <div id="paypal-button-container"></div>
            <div class="secure-badge">
                🔒 Secure checkout powered by PayPal
            </div>
            <p>You don't need a PayPal account - credit and debit cards accepted</p>
        </div>
        
        <a href="/product/{product_id}" class="back-link">← Back to product page</a>
    </div>

    <script src="https://www.paypal.com/sdk/js?client-id={PAYPAL_CLIENT_ID}&currency=USD"></script>
    <script>
        paypal.Buttons({{
            style: {{
                layout: 'vertical',
                color: 'gold',
                shape: 'rect',
                label: 'pay'
            }},
            createOrder: function(data, actions) {{
                return actions.order.create({{
                    purchase_units: [{{
                        amount: {{
                            value: '{product['price']}'
                        }},
                        description: '{product['name']}',
                        custom_id: '{product_id}'
                    }}],
                    application_context: {{
                        brand_name: 'Ke Aupuni O Ke Akua Press',
                        user_action: 'PAY_NOW'
                    }}
                }});
            }},
            onApprove: function(data, actions) {{
                return actions.order.capture().then(function(details) {{
                    // Payment successful - redirect to download page
                    window.location.href = '/paypal/success?orderID=' + data.orderID + '&product_id={product_id}';
                }});
            }},
            onCancel: function(data) {{
                window.location.href = '/product/{product_id}?cancelled=true';
            }},
            onError: function(err) {{
                alert('Payment error. Please try again or contact keaupuniakeakua@gmail.com');
            }}
        }}).render('#paypal-button-container');
    </script>
</body>
</html>"""
    
    return html

@app.route("/paypal/success")
def paypal_success():
    """Handle successful PayPal payment and deliver download"""
    order_id = request.args.get("orderID")
    product_id = request.args.get("product_id")
    
    if not order_id or not product_id:
        abort(400)
    
    # Get product details
    products_data = load_digital_products()
    product = next((p for p in products_data["products"] if p["id"] == product_id), None)
    
    if not product:
        abort(404)
    
    # Update sales tracking
    product["downloads"] = product.get("downloads", 0) + 1
    product["total_sales"] = product.get("total_sales", 0) + float(product["price"])
    save_digital_products(products_data)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mahalo! Your Download Is Ready</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .container {{
            max-width: 600px;
            width: 100%;
            background: white;
            border-radius: 16px;
            padding: 3rem 2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
        }}
        
        .success-icon {{
            font-size: 4rem;
            margin-bottom: 1rem;
        }}
        
        h1 {{
            color: #2c3e50;
            font-size: 2rem;
            margin-bottom: 1rem;
        }}
        
        .subtitle {{
            color: #6c757d;
            margin-bottom: 2rem;
            font-size: 1.1rem;
        }}
        
        .download-btn {{
            display: inline-block;
            padding: 1.25rem 2.5rem;
            background: #28a745;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-size: 1.25rem;
            font-weight: bold;
            transition: all 0.3s ease;
            margin-bottom: 2rem;
        }}
        
        .download-btn:hover {{
            background: #218838;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
        }}
        
        .message {{
            background: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: left;
            margin-bottom: 2rem;
            color: #2c3e50;
            line-height: 1.6;
        }}
        
        .order-info {{
            color: #6c757d;
            font-size: 0.85rem;
            margin-top: 1rem;
        }}
        
        .home-link {{
            display: inline-block;
            margin-top: 1.5rem;
            color: #6c757d;
            text-decoration: none;
        }}
        
        .home-link:hover {{
            color: #2c3e50;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">🌺</div>
        <h1>Mahalo! Payment Received!</h1>
        <p class="subtitle">Your copy of <strong>{product['name']}</strong> is ready!</p>
        
        <a href="/download/{product_id}" class="download-btn">
            ⬇️ Download Your Ebook Now
        </a>
        
        <div class="message">
            <p><strong>Aloha friend!</strong></p>
            <br>
            <p>Mahalo nui for your purchase! This book represents years of study combining ancient Hawaiian wisdom with modern science.</p>
            <br>
            <p>May it bring you health, harmony, and the spirit of aloha in your wellness journey.</p>
            <br>
            <p>If you have any questions, email me at <strong>keaupuniakeakua@gmail.com</strong></p>
            <br>
            <p>A hui hou,<br><strong>Kahu Phil Stephens</strong><br>Molokaʻi, Hawaiʻi 🌺</p>
        </div>
        
        <div class="order-info">Order ID: {order_id}</div>
        
        <a href="/" class="home-link">← Return to Ke Aupuni O Ke Akua</a>
    </div>
    
    <script>
        // Auto-trigger download
        window.onload = function() {{
            setTimeout(function() {{
                window.location.href = '/download/{product_id}';
            }}, 2000);
        }};
    </script>
</body>
</html>"""
    
    return html

@app.route("/paypal/cancel")
def paypal_cancel():
    """Handle cancelled PayPal payment"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payment Cancelled</title>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            max-width: 500px;
            background: white;
            border-radius: 16px;
            padding: 3rem 2rem;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        h1 { color: #2c3e50; margin-bottom: 1rem; }
        p { color: #6c757d; margin-bottom: 2rem; line-height: 1.6; }
        
        .btn {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin: 0.5rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>No worries! 🌺</h1>
        <p>Your payment was cancelled. No charge was made.</p>
        <p>Whenever you're ready, the book will be here waiting for you.</p>
        <a href="/" class="btn">← Back to Website</a>
    </div>
</body>
</html>"""
    
    return html
