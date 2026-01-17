# ke_aupuni_finalized_with_image_placeholders.py
# FIXED VERSION - CSS working, products restored
# NOW WITH KINGDOM KEYS FREE BOOKLETS PAGE
# ADDED: MYRON GOLDEN AFFILIATE PAGE
# FIXES: Kit form URL + Link colors + Duplicate body_md removed

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
            "body_md": "## Welcome to Ke Aupuni O Ke Akua - The Kingdom of God\r\n\r\nMahalo for visiting. This site is dedicated to rediscovering the revolutionary Kingdom message that Jesus actually preached, which is often missed in modern religious traditions.\r\n\r\n### Our Mission: Kingdom, Not Religion\r\nJesus's central focus was the Kingdom of God—the reign and rule of God breaking into the human experience here and now. Our resources aim to guide you into a deeper understanding of Kingdom principles, citizenship, and authority, moving you from religious performance into authentic, transformative living.\r\n\r\n**Start your journey today by exploring 'The Call to Repentance' series in the navigation.**\r\n\r\n### What Jesus Actually Taught\r\n\r\n**Kingdom Principles Over Religious Rules** - Discover how Jesus consistently chose kingdom living over religious compliance.\r\n\r\n**Repentance as Transformation** - Move beyond feeling sorry for sins to understanding a complete transformation of mind, heart, and lifestyle.\r\n\r\n**Heaven on Earth** - Learn how the Kingdom of God is meant to manifest in our daily lives, relationships, and communities right now.\r\n\r\n---\r\n\r\n### 🎁 NEW TO KINGDOM THEOLOGY? START HERE!\r\n\r\n**FREE Kingdom Keys Booklets** - Bite-sized teachings that will transform your understanding of what Jesus really taught. Perfect introduction before diving into the full series.\r\n\r\n**[Download FREE Kingdom Keys →](/kingdom_keys)**\r\n\r\n---\r\n\r\n### 💰 Kingdom Wealth & Biblical Prosperity\r\n\r\nDiscover God's economic system and how the Kingdom operates on principles of stewardship, multiplication, and generosity.\r\n\r\n**[Explore Kingdom Wealth Principles →](/kingdom_wealth)**",
            "product_url": "https://amzn.to/3FfH9ep"
        },
        "kingdom_wealth": {
            "title": "Kingdom Wealth",
            "hero_image": "https://i.imgur.com/wmHEyDo.png",
            "body_md": "## Biblical Stewardship & Economic Increase\r\n\r\nThe Kingdom of God operates on a system of stewardship, not ownership. Understanding Kingdom Wealth means shifting from a \"poverty mindset\" to a \"provision mindset.\"\r\n\r\n### Core Principles of Kingdom Wealth\r\n\r\n**Source vs. Resource** - Recognizing that God is the Source, and everything else is just a resource.\r\n\r\n**Seed Time and Harvest** - The spiritual law of multiplication through giving and wisdom.\r\n\r\n**Economic Mandate** - We are blessed to be a blessing, establishing God's covenant on the earth.\r\n\r\n### Practical Application\r\n\r\nTrue wealth in the Kingdom is measured by your capacity to influence your community for good and provide for the needs of the ministry and the poor.\r\n\r\n---\r\n\r\n### 📚 Recommended Kingdom Wealth Resources\r\n\r\n**The Call to Repentance Series** - Includes comprehensive teaching on Kingdom economics and biblical stewardship principles.\r\n\r\n**[Get the Complete Kingdom Series →](/call_to_repentance)**\r\n\r\n---\r\n\r\n### 💡 Transform Your Financial Mindset\r\n\r\nMove from religious poverty thinking into Kingdom abundance. Learn how Jesus taught about money, provision, and the Father's desire to bless His children.\r\n\r\n**Scripture Foundation:** \"Seek first the kingdom of God and His righteousness, and all these things shall be added to you.\" - Matthew 6:33\r\n\r\n---\r\n\r\n### 📖 Learning Biblical Business Principles\r\n\r\nAfter 30 years of biblical study and 8 years in pastoral ministry on Molokaʻi, I'm applying Myron Golden's Kingdom approach to business. His teaching on biblical wealth creation aligns with the Kingdom economics I've been teaching.\r\n\r\nI'm building my ministry using these ethical, scripture-based principles - because God's Kingdom deserves to be funded with integrity, not manipulation.\r\n\r\nIf you're called to ministry or Christian business, these resources can help you build on a solid biblical foundation.\r\n\r\n**[Explore Myron Golden's Biblical Business Training →](/myron-golden)**",
            "product_url": ""
        },
        "aloha_wellness": {
            "title": "Aloha Wellness - Island Health & Healing",
            "hero_image": "https://i.imgur.com/xGeWW3Q.jpeg",
            "body_md": "## Aloha Wellness - The Sacred Art of How You Eat\r\n\r\nDiscover the life-changing power of **how** you eat, not just what you eat. This groundbreaking wellness book combines cutting-edge scientific research with ancient Hawaiian mana'o (wisdom) to transform your relationship with food and nourishment.\r\n\r\n### Beyond Diet Culture - A Hawaiian Perspective\r\n\r\nTraditional Hawaiian culture understood something modern society has forgotten: eating is a sacred act that connects us to the land, our ancestors, and our own spiritual well-being. This book bridges that ancient wisdom with contemporary nutritional science.\r\n\r\n### Revolutionary Approach: How, Not What\r\n\r\n**Mindful Consumption** - Learn the scientific basis for how mindful eating practices affect digestion, metabolism, and overall health.\r\n\r\n**Cultural Eating Wisdom** - Discover how Hawaiian ancestors approached meals as community ceremonies, gratitude practices, and spiritual connections.\r\n\r\n**Stress and Digestion** - Research-backed insights into how your emotional state during meals affects nutrient absorption and digestive health.\r\n\r\n**Rhythm and Timing** - Ancient Hawaiian understanding of eating in harmony with natural rhythms, supported by modern chronobiology research.\r\n\r\n**Scientific Research Meets Island Wisdom** - This book offers a comprehensive look at the intersection of modern science and ancient practice.\r\n\r\n### Hawaiian Mana'o (Wisdom Principles)\r\n\r\n**Ho'oponopono with Food** - Making right relationships with nourishment and healing food-related guilt or shame.\r\n\r\n**Aloha 'Āina** - Love of the land extends to gratitude for the food it provides and mindful consumption practices.\r\n\r\n**Lōkahi** - Finding unity and balance in your relationship with food, body, and spirit.\r\n\r\n**Mālama** - Caring for your body as a sacred temple through conscious eating practices.\r\n\r\nTransform your health from the inside out by changing not what you eat, but how you approach the sacred act of nourishment.\r\n\r\n---\r\n\r\n### 🌺 Body, Soul & Spirit Wellness\r\n\r\nTrue wellness integrates physical health with spiritual vitality. Explore how Kingdom principles apply to caring for the temple God gave you.\r\n\r\n**[Discover Kingdom Living Principles →](/kingdom_wealth)**",
            "product_url": "https://amzn.to/3FfH9ep",
            "products": [
                {
                    "title": "Aloha Wellness Book",
                    "cover": "https://m.media-amazon.com/images/I/712tO3wmGEL._SL1499_.jpg",
                    "amazon": "",
                    "gumroad": ""
                }
            ]
        },
        "call_to_repentance": {
            "title": "The Call to Repentance - The Kingdom Series",
            "hero_image": "https://i.imgur.com/tG1vBp9.jpeg",
            "body_md": "## The Call to Repentance - Rediscovering Jesus's Kingdom Message\r\n\r\nStep beyond religious tradition and rediscover the revolutionary Kingdom message that Jesus actually preached. This transformative book series cuts through centuries of religious interpretation to reveal the pure, life-changing teachings of the Kingdom of God.\r\n\r\n### Series Overview (Volumes 1-5)\r\n\r\nThis isn't a single book but a comprehensive series that systematically unpacks Jesus's kingdom teachings.\r\n\r\n### A Call to Authentic Christianity\r\n\r\nThis series challenges readers to move beyond:\r\n- Religious performance into authentic relationship\r\n- Sunday Christianity into daily kingdom living\r\n- Denominational identity into kingdom citizenship\r\n- Waiting for heaven into experiencing God's kingdom now\r\n\r\n**Join the revolution that Jesus started. Discover the Kingdom message that changes everything.**\r\n\r\n---\r\n\r\n### 🎁 New to Kingdom Theology?\r\n\r\nStart with our **FREE Kingdom Keys booklets** - perfect introduction to the core concepts before diving into the full series.\r\n\r\n**[Get Free Kingdom Keys →](/kingdom_keys)**\r\n\r\n---\r\n\r\n### 💰 Kingdom Wealth Principles\r\n\r\nBook 3 in the series covers biblical prosperity, stewardship, and God's economic system. Learn how Jesus taught about money, provision, and Kingdom increase.\r\n\r\n**[Explore Kingdom Wealth Teaching →](/kingdom_wealth)**",
            "product_url": "https://www.amazon.com/CALL-REPENTANCE-Foundation-Application-Lifestyle-ebook/dp/B0FXYDD9SN",
            "products": [
                {
                    "title": "The Call to Repentance - Kingdom Book",
                    "cover": "",
                    "amazon": "",
                    "gumroad": "https://uncomango.gumroad.com/l/myold"
                }
            ]
        },
        "pastor_planners": {
            "title": "Pastor Planners - Tools for Ministry Excellence",
            "hero_image": "https://i.imgur.com/tWnn5UY.png",
            "body_md": "## Organize Your Ministry with Purpose and Prayer\r\n\r\nEffective ministry requires both spiritual sensitivity and practical organization. Our Pastor Planners combine beautiful design with functional tools to help you lead with excellence and peace.\r\n\r\n### Features of Our Ministry Planning System\r\n\r\n**Sermon Planning Sections** - Map out your preaching calendar with space for themes, scriptures, and prayer requests.\r\n\r\n**Prayer and Pastoral Care** - Dedicated sections for tracking prayer requests, hospital visits, counseling sessions, and follow-up care.\r\n\r\n**Meeting and Event Coordination** - Organize board meetings, committee sessions, special events, and outreach activities.\r\n\r\n**Personal Spiritual Disciplines** - Maintain your own spiritual health with guided sections for daily devotions.\r\n\r\n### Why Pastors Love Our Planners\r\n\r\n**Hawaiian-Inspired Design** - Beautiful layouts featuring island imagery and scripture verses.\r\n\r\n**Flexible Formatting** - Works for churches of all sizes and denominations.\r\n\r\n**Durable Construction** - High-quality materials that withstand daily use.\r\n\r\n**Spiritual Focus** - More than just organization - designed to keep your heart centered on God's calling.\r\n\r\n---\r\n\r\n### 📚 Pastor Resources\r\n\r\n**Complete Kingdom Theology Series** - Equip yourself with solid biblical teaching to share with your congregation.\r\n\r\n**[Browse Kingdom Teaching Resources →](/call_to_repentance)**\r\n\r\n---\r\n\r\n### 🎁 FREE Ministry Tools\r\n\r\nDownload our **FREE Kingdom Keys booklets** - perfect for small groups, new believers, or sermon prep inspiration.\r\n\r\n**[Get Free Kingdom Keys →](/kingdom_keys)**",
            "product_url": "https://www.amazon.com/s?k=pastor+planner+ministry+organizer",
            "products": [
                {
                    "title": "Hawaiian Pastor Planner - Yearly",
                    "cover": "https://public-files.gumroad.com/p4346cgzkcd4iivhsgkf7pjtypr2",
                    "amazon": "",
                    "gumroad": ""
                },
                {
                    "title": "Hawaiian Pastor Planner - Monthly",
                    "cover": "https://public-files.gumroad.com/ccssij259a3729na9xx5s12skasm",
                    "amazon": "",
                    "gumroad": ""
                },
                {
                    "title": "Samoan Pastor Planner - Yearly",
                    "cover": "https://public-files.gumroad.com/worm4zkkn4hm5k0f81icc4e4pofp",
                    "amazon": "",
                    "gumroad": ""
                },
                {
                    "title": "Samoan Pastor Planner - Monthly",
                    "cover": "https://public-files.gumroad.com/ztbnhmb1azeotsvxga3979n6dw4g",
                    "amazon": "",
                    "gumroad": ""
                }
            ]
        },
        "nahenahe_voice": {
            "title": "The Nahenahe Voice of Nahono'opi'ilani - Musical Legacy",
            "hero_image": "https://i.imgur.com/Vyz6nFJ.png",
            "body_md": "## The Nahenahe Voice of Nahono'opi'ilani - Live from Molokai Ranch Lodge\r\n\r\nExperience the soul-stirring sounds of authentic Hawaiian music captured live at the historic Molokai Ranch Lodge in the year 2000. This intimate recording showcases the true meaning of **nahenahe** - the gentle, soothing voice that carries the spirit of aloha across the islands.\r\n\r\n### A Sacred Musical Journey\r\n\r\nRecorded in the peaceful setting of Molokai Ranch Lodge, this collection features solo guitar and traditional Hawaiian melodies that speak directly to the heart.\r\n\r\n**Nahenahe** means more than just \"soft\" or \"sweet\" - it represents music that heals, soothes, and connects us to the divine presence that flows through all creation.\r\n\r\n### What You'll Experience:\r\n\r\n**Traditional Hawaiian Melodies** - Time-honored songs passed down through generations.\r\n\r\n**Solo Guitar Mastery** - Intimate acoustic performances showcasing Hawaiian slack-key guitar traditions.\r\n\r\n**Authentic Island Atmosphere** - The natural acoustics and peaceful energy of Molokai Ranch Lodge.\r\n\r\n**Healing Through Song** - Each track brings peace, comfort, and the healing power of aloha.\r\n\r\n*\"Music is the language that speaks when words are not enough. The nahenahe voice carries aloha to every heart that listens.\"*\r\n\r\nPerfect for meditation, relaxation, spiritual practice, or any time you need the gentle embrace of island peace.",
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
        "kingdom_keys": {
            "title": "FREE Kingdom Keys Booklets",
            "hero_image": "https://i.imgur.com/wmHEyDo.png",
            "body_md": "## 🌺 FREE Kingdom Keys Booklets 🌺\r\n\r\n**Hoʻomau i ke Aupuni o ke Akua** (Continue in the Kingdom of God)\r\n\r\n**Aloha!** I'm Pastor Phil Stephens from Molokaʻi. After 30 years of biblical study, I've discovered the Kingdom truths the church forgot. Download these FREE mini-devotionals that will transform how you see Jesus's message.\r\n\r\n---\r\n\r\n## 📧 Get Weekly Kingdom Teaching\r\n\r\nJoin believers worldwide discovering Kingdom truth. Sign up at **[YOUR-EMAIL-SERVICE]**\r\n\r\n---\r\n\r\n## 📚 Ready for Deeper Teaching?\r\n\r\nThese free booklets are just the beginning. Explore the complete **54-book Kingdom Series** for comprehensive biblical teaching.\r\n\r\n**[Browse Complete Kingdom Series →](/call_to_repentance)**\r\n\r\n---\r\n\r\n## 💝 Was This Helpful?\r\n\r\nIf these booklets blessed you, consider sowing back into this Kingdom ministry:\r\n\r\n**PayPal:** paypal.me/YOUR-PAYPAL  \r\n**Gumroad:** YOUR-GUMROAD.gumroad.com/l/donation\r\n\r\n*Every seed sown helps us reach more people with the Kingdom message.*",
            "products": [
                {
                    "title": "7 Scriptures That Prove the Kingdom Is Inside You Now",
                    "cover": "",
                    "amazon": "",
                    "gumroad": ""
                },
                {
                    "title": "How to Release Kingdom Healing in 10 Minutes a Day",
                    "cover": "",
                    "amazon": "",
                    "gumroad": ""
                },
                {
                    "title": "The 5 Kingdom Prayers My Hawaiian Grandma Taught Me",
                    "cover": "",
                    "amazon": "",
                    "gumroad": ""
                },
                {
                    "title": "Kingdom Wealth: 7 Bible Verses the Prosperity Preachers Won't Tell You",
                    "cover": "",
                    "amazon": "",
                    "gumroad": ""
                }
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
    color: var(--text-dark);
    background: var(--primary-bg);
    background-image: 
        radial-gradient(circle at 20% 50%, rgba(175, 216, 248, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(212, 165, 116, 0.1) 0%, transparent 50%);
}

a {
    color: #d4af37;
    text-decoration: none;
    transition: color 0.3s ease;
}

a:hover {
    color: #f5d76e;
    text-decoration: underline;
}

a:visited {
    color: #b8962e;
}

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

.nav-title {
    font-size: 1.5rem;
    font-weight: bold;
    color: #2c3e50;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.nav-logo {
    height: 40px;
    width: auto;
}

.nav-menu {
    display: flex;
    list-style: none;
    gap: 1.5rem;
    align-items: center;
}

.nav-menu li a {
    color: #1a1a1a;
    text-decoration: none;
    font-weight: 700;
    font-size: 0.95rem;
    padding: 0.75rem 1.25rem;
    border-radius: 8px;
    transition: all 0.3s ease;
    text-shadow: 0 1px 2px rgba(255,255,255,0.5);
    letter-spacing: 0.3px;
}

.nav-menu li a:hover {
    color: white;
    background: rgba(95, 158, 160, 0.8);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.hamburger {
    display: none;
    flex-direction: column;
    cursor: pointer;
    gap: 4px;
}

.hamburger span {
    width: 25px;
    height: 3px;
    background-color: #2c3e50;
    transition: 0.3s;
}

@media (max-width: 768px) {
    .nav-menu {
        position: fixed;
        left: -100%;
        top: 70px;
        flex-direction: column;
        background-color: #d4b896;
        width: 100%;
        text-align: center;
        transition: 0.3s;
        box-shadow: 0 10px 27px rgba(0,0,0,0.05);
        padding: 2rem 0;
        gap: 1rem;
    }

    .nav-menu.active {
        left: 0;
    }

    .hamburger {
        display: flex;
    }
    
    .nav-title {
        font-size: 1.2rem;
    }
    
    .nav-logo {
        height: 30px;
    }
}

.hero {
    min-height: 85vh;
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    margin-bottom: 3rem;
}

.hero-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(44, 62, 80, 0.4) 0%, rgba(95, 158, 160, 0.4) 100%);
}

.hero-content {
    position: relative;
    z-index: 1;
    text-align: center;
    color: white;
    padding: 2rem;
    max-width: 900px;
    background: transparent;
}

.hero h1 {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    line-height: 1.2;
}

@media (max-width: 768px) {
    .hero {
        height: 40vh;
    }
    .hero h1 {
        font-size: 2rem;
    }
}

.container {
    max-width: 1200px;
    margin: -45vh auto 0;
    padding: 0 2rem 4rem;
    position: relative;
    z-index: 10;
}

.content-card {
    background-color: rgba(255, 255, 255, 0.75);
    border: 2px solid rgba(212, 165, 116, 0.3);
    background-image: 
        linear-gradient(45deg, rgba(201, 168, 118, 0.25) 25%, transparent 25%),
        linear-gradient(-45deg, rgba(201, 168, 118, 0.25) 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, rgba(191, 160, 104, 0.25) 75%),
        linear-gradient(-45deg, transparent 75%, rgba(191, 160, 104, 0.25) 75%);
    background-size: 20px 20px;
    background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
    border-radius: 12px;
    padding: 3rem;
    box-shadow: var(--shadow-soft);
    backdrop-filter: blur(10px);
}

.content-card h2 {
    color: var(--text-dark);
    font-size: 2rem;
    margin: 2rem 0 1rem;
    border-bottom: 3px solid var(--accent-warm);
    padding-bottom: 0.5rem;
}

.content-card h3 {
    color: var(--accent-teal);
    font-size: 1.5rem;
    margin: 1.5rem 0 0.75rem;
}

.content-card p {
    margin-bottom: 1rem;
    line-height: 1.8;
}

.content-card strong {
    color: var(--accent-teal);
    font-weight: 600;
}

.content-card ul {
    margin: 1rem 0 1rem 2rem;
    line-height: 1.8;
}

.content-card li {
    margin-bottom: 0.5rem;
}

.buy-section {
    text-align: center;
    margin: 3rem 0;
    padding: 2rem;
    background: linear-gradient(135deg, rgba(95, 158, 160, 0.1) 0%, rgba(212, 165, 116, 0.1) 100%);
    border-radius: 12px;
}

.buy-button {
    display: inline-block;
    padding: 1rem 2.5rem;
    background: linear-gradient(135deg, var(--accent-teal), #4a8b8e);
    color: white;
    text-decoration: none;
    border-radius: 50px;
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

.gallery-section {
    margin: 3rem 0;
}

.gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-top: 1.5rem;
}

.gallery-item {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    transition: transform 0.3s ease;
}

.gallery-item:hover {
    transform: scale(1.05);
}

.gallery-item img {
    width: 100%;
    height: auto;
    display: block;
}

.music-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 1.5rem;
}

.music-button {
    display: inline-block;
    padding: 0.875rem 2rem;
    background: linear-gradient(135deg, var(--accent-teal), #4a8b8e);
    color: white;
    text-decoration: none;
    border-radius: 50px;
    font-weight: bold;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(95, 158, 160, 0.3);
}

.music-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(95, 158, 160, 0.4);
}

.footer {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    color: white;
    text-align: center;
    padding: 2rem;
    margin-top: 4rem;
}

@media (max-width: 768px) {
    .content-card {
        padding: 1.5rem;
    }
    
    .gallery-grid {
        grid-template-columns: 1fr;
    }
    
    .music-buttons {
        flex-direction: column;
    }
}
"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page.title }}</title>
    <style>{{ style|safe }}
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

    .content-card div[style*="background: rgba(255,255,255,0.1)"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.5) !important;
    }
</style>
</head>
<body>
    <nav class="site-nav">
        <div class="nav-container">
            <a href="/" class="nav-title">
                <img src="/static/image/output-onlinepngtools.png" alt="Ke Aupuni Logo" class="nav-logo">
                Ke Aupuni O Ke Akua
            </a>
            <div class="hamburger" onclick="toggleMenu()">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <ul class="nav-menu" id="navMenu">
                {% for item in nav_items %}
                <li><a href="{{ item.url }}">{{ item.title }}</a></li>
                {% endfor %}
                <li><a href="/kingdom_keys" style="background:#d4af37;color:#fff;padding:0.5rem 1rem;border-radius:6px;">🎁 FREE Booklets</a></li>
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
            
            {% if page.products %}
            <div style="margin: 3rem 0; padding: 2rem 0; border-top: 2px solid rgba(255,255,255,0.2);">
                <h2 style="color: white; text-align: center; margin-bottom: 2rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.9);">📚 Available Products</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 1.5rem; max-width: 1200px; margin: 0 auto;">
                    {% for product in page.products %}
                    <div style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 1.5rem; backdrop-filter: blur(10px); box-shadow: 0 4px 15px rgba(0,0,0,0.3); transition: transform 0.3s ease;">
                        {% if product.cover %}
                        <img src="{{ product.cover }}" alt="{{ product.title }}" style="width: 100%; height: auto; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
                        {% endif %}
                        <h3 style="color: white; font-size: 1rem; margin-bottom: 1rem; min-height: 2.5rem; text-shadow: 1px 1px 3px rgba(0,0,0,0.7);">{{ product.title }}</h3>
                        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                            {% if product.amazon %}
                            <a href="{{ product.amazon }}" target="_blank" style="display: block; background: linear-gradient(135deg, var(--accent-teal), #4a8b8e); color: white; padding: 0.6rem; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 0.9rem; text-align: center; transition: transform 0.2s;">🛒 Amazon</a>
                            {% endif %}
                            {% if product.gumroad %}
                            <a href="{{ product.gumroad }}" target="_blank" style="display: block; background: linear-gradient(135deg, #FF90E8, #FFA500); color: white; padding: 0.6rem; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 0.9rem; text-align: center; transition: transform 0.2s;">💳 Gumroad</a>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            {% if page.product_links %}
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
            
            <div class="buy-section">
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

MYRON_GOLDEN_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transform Your Financial Future | Biblical Business Principles</title>
    <style>{{ style|safe }}
    .email-capture { 
        background: rgba(212, 165, 116, 0.2); 
        padding: 30px; 
        margin: 30px 0; 
        text-align: center; 
        border: 3px solid rgba(212, 165, 116, 0.5); 
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    .email-capture h2 { color: white; margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); }
    .email-form { max-width: 500px; margin: 0 auto; }
    .email-form input { width: 100%; padding: 15px; margin: 10px 0; font-size: 16px; border: 2px solid #ddd; border-radius: 6px; }
    .email-form button { width: 100%; padding: 15px; background: #d4af37; color: white; font-size: 18px; font-weight: bold; border: none; cursor: pointer; border-radius: 6px; }
    .email-form button:hover { background: #b8962e; }
    .section { padding: 40px 0; }
    .section h2 { color: white; font-size: 2em; margin-bottom: 30px; text-align: center; text-shadow: 2px 2px 4px rgba(0,0,0,0.9); }
    .product-box { background: rgba(0, 0, 0, 0.5); padding: 30px; margin: 20px 0; border: 2px solid rgba(255,255,255,0.2); border-radius: 12px; backdrop-filter: blur(10px); }
    .product-box h3 { color: white; margin-bottom: 15px; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); }
    .product-box ul { margin: 20px 0; padding-left: 20px; color: white; }
    .product-box li { margin: 10px 0; text-shadow: 1px 1px 3px rgba(0,0,0,0.7); }
    .product-box p { color: white; line-height: 1.8; text-shadow: 1px 1px 3px rgba(0,0,0,0.7); }
    .btn { display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, var(--accent-teal), #4a8b8e); color: white; text-decoration: none; font-weight: bold; margin: 10px 5px; text-align: center; border-radius: 8px; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(95, 158, 160, 0.3); }
    .btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(95, 158, 160, 0.4); }
    .btn-container { text-align: center; margin-top: 20px; }
    </style>
</head>
<body>
    <nav class="site-nav">
        <div class="nav-container">
            <a href="/" class="nav-title">
                <img src="/static/image/output-onlinepngtools.png" alt="Ke Aupuni Logo" class="nav-logo">
                Ke Aupuni O Ke Akua
            </a>
            <div class="hamburger" onclick="toggleMenu()">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <ul class="nav-menu" id="navMenu">
                <li><a href="/">Home</a></li>
                <li><a href="/kingdom_wealth">Kingdom Wealth</a></li>
                <li><a href="/call_to_repentance">The Call to Repentance</a></li>
                <li><a href="/aloha_wellness">Aloha Wellness</a></li>
                <li><a href="/pastor_planners">Pastor Planners</a></li>
                <li><a href="/nahenahe_voice">Nahenahe Voice</a></li>
                <li><a href="/kingdom_keys" style="background:#d4af37;color:#fff;padding:0.5rem 1rem;border-radius:6px;">🎁 FREE Booklets</a></li>
            </ul>
        </div>
    </nav>
    
    <header class="hero" style="background-image: url('https://i.imgur.com/wmHEyDo.png');">
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <h1>Transform Your Financial Future</h1>
            <p style="font-size: 1.3rem; margin-top: 1rem;">Biblical Business Principles That Actually Work</p>
            <p style="font-size: 1.1rem; margin-top: 0.5rem;"><em>From Pastor Phil Stephens, Molokaʻi</em></p>
        </div>
    </header>
    
    <main class="container">
        <article class="content-card">
            <div class="email-capture">
                <h2>🌴 Get My FREE Kingdom Business Guide 🌴</h2>
                <p style="margin-bottom: 20px; color: white; text-shadow: 1px 1px 3px rgba(0,0,0,0.7);">Learn the 3 biggest mistakes keeping Christians broke (and how to fix them using biblical principles)</p>
                
                <div class="email-form">
                    <form action="https://app.kit.com/forms/8979853/subscriptions" method="post">
                        <input type="text" name="fields[first_name]" placeholder="First Name" required>
                        <input type="email" name="email_address" placeholder="Email Address" required>
                        <button type="submit">GET FREE GUIDE →</button>
                    </form>
                </div>
            </div>

            <div class="section">
                <h2>📚 SECTION 1: Start Your Journey</h2>
                <div class="product-box">
                    <h3>Start here if:</h3>
                    <ul>
                        <li>You're tired of financial struggle and ready for a complete mindset shift</li>
                        <li>You want to understand the biblical principles of wealth creation</li>
                        <li>You're curious about Myron Golden's transformation story (from garbage collector to multi-millionaire)</li>
                        <li>You need practical frameworks you can implement immediately</li>
                        <li>You prefer learning through reading before investing in courses</li>
                    </ul>
                    <h3>What you get:</h3>
                    <ul>
                        <li>Two foundational books that reveal the mindset secrets of the wealthy</li>
                        <li>Biblical wealth-building principles that actually work in today's marketplace</li>
                        <li>Myron's proven frameworks for transforming your income potential</li>
                        <li>Stories and strategies you can apply starting today</li>
                        <li>The lowest-cost entry point to Myron Golden's teachings ($27-47 total)</li>
                    </ul>
                    <div class="btn-container">
                        <a href="https://www.trashmantocashman.com/tmcm-book?affiliate_id=4319525" class="btn">GET TRASH MAN TO CASH MAN →</a>
                        <a href="https://www.bossmovesbook.com/bossmoves?affiliate_id=4319525" class="btn">GET BOSS MOVES BOOK →</a>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🧠 SECTION 2: Transform Your Money Blueprint</h2>
                <div class="product-box">
                    <h3>Take this if:</h3>
                    <ul>
                        <li>You've read the books and you're ready to go deeper</li>
                        <li>You know your money mindset is holding you back from your potential</li>
                        <li>You want to break generational poverty cycles in your family</li>
                        <li>You're ready to invest in yourself and your financial future</li>
                        <li>You need to rewire your subconscious beliefs about money</li>
                    </ul>
                    <h3>What you get:</h3>
                    <ul>
                        <li>Comprehensive training that reprograms your money blueprint</li>
                        <li>Biblical perspectives on wealth that eliminate guilt and confusion</li>
                        <li>Practical exercises to identify and eliminate limiting beliefs</li>
                        <li>Strategies for developing millionaire-level thinking patterns</li>
                        <li>Tools to overcome fear, doubt, and scarcity mindset forever</li>
                    </ul>
                    <div class="btn-container">
                        <a href="https://www.mindovermoneymastery.com/momm?affiliate_id=4319525" class="btn">TRANSFORM YOUR MINDSET →</a>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🎯 SECTION 3: Master the Art of Making Offers</h2>
                <div class="product-box">
                    <h3>Make More Offers Challenge ($97)</h3>
                    <p>This intensive 5-day challenge teaches you the exact framework for creating irresistible offers that sell themselves. Myron Golden reveals why most businesses struggle (they don't make enough offers) and shows you how to create multiple income streams by making better, more frequent offers. You'll learn the psychology of buying decisions, how to stack value that makes price irrelevant, and the specific language patterns that compel people to say "yes." Perfect for entrepreneurs, coaches, consultants, and anyone who needs to sell their products or services. The challenge includes daily training videos, live Q&A sessions, worksheets, and a supportive community of fellow offer-makers.</p>
                    <div class="btn-container">
                        <a href="https://www.makemoreofferschallenge.com/mmoc?affiliate_id=4319525" class="btn">JOIN THE CHALLENGE →</a>
                    </div>
                </div>
                <div class="product-box">
                    <h3>Offer Mastery Live ($297)</h3>
                    <p>This is Myron Golden's signature event where he spends three full days teaching you the complete system for creating high-ticket offers that transform your business. You'll discover the four core offer types that generate predictable revenue, learn how to structure offers that sell at $2,000, $5,000, $10,000 or higher, and master the art of presenting offers that create instant buying decisions. Myron breaks down the psychology, strategy, and implementation of world-class offer creation. This event includes access to recordings, workbooks, and ongoing support. If you're serious about scaling your business through premium offers, this is where you level up from making offers to mastering them.</p>
                    <div class="btn-container">
                        <a href="https://www.offermasterylive.com/offer-mastery-livevetfk4nn?affiliate_id=4319525" class="btn">MASTER YOUR OFFERS →</a>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🚀 SECTION 4: Build Your Million-Dollar Infrastructure</h2>
                <div class="product-box">
                    <h3>Golden OPS ($997)</h3>
                    <p>This is Myron Golden's most comprehensive program for building a complete business operating system that generates consistent six and seven-figure revenue. Golden OPS (Operational Procedures and Systems) teaches you how to construct the four foundational pillars every million-dollar business requires: lead generation systems, lead nurture systems, sales conversion systems, and product delivery systems. You'll learn how to create automated funnels, build email sequences that convert, develop premium programs and masterminds, and structure your business for scalability. The program includes video training modules, implementation templates, funnel blueprints, marketing scripts, and access to a private community of serious entrepreneurs. Myron also reveals his personal business systems and shows you exactly how he structures his multi-million dollar empire. If you're ready to stop trading time for money and build a business that runs systematically, Golden OPS is your blueprint.</p>
                    <div class="btn-container">
                        <a href="https://www.mygoldenops.com/golden-opsm1y8y7bx?affiliate_id=4319525" class="btn">BUILD YOUR SYSTEM →</a>
                    </div>
                </div>
            </div>

            <div class="footer" style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.3);">
                <p style="color: white; text-shadow: 1px 1px 3px rgba(0,0,0,0.7);"><em>Affiliate Disclosure: I may earn a commission if you purchase through these links, at no extra cost to you.</em></p>
                <p style="color: white; text-shadow: 1px 1px 3px rgba(0,0,0,0.7); margin-top: 1rem;">© 2025 Ke Aupuni O Ke Akua Press | Pastor Phil Stephens, Molokaʻi</p>
            </div>
        </article>
    </main>
    
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

# REST OF FILE CONTINUES EXACTLY AS BEFORE...

ADMIN_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Manager</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
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
        <h1>🏝️ Ke Aupuni Content Manager</h1>
        <p class="subtitle">Aloha, Kahu! Edit your website pages here.</p>
        <div class="page-list">
            {% for page_id, page in pages.items() %}
            <div class="page-card">
                <div class="page-title">{{ page.title }}</div>
                <div class="page-info">
                    <div><strong>URL:</strong> /{{ page_id }}</div>
                    <div><strong>Hero Image:</strong> {{ page.hero_image or 'None' }}</div>
                    {% if page.product_url %}
                    <div><strong>Product Link:</strong> {{ page.product_url }}</div>
                    {% endif %}
                    {% if page.gallery_images %}
                    <div><strong>Gallery:</strong> {{ page.gallery_images|length }} images</div>
                    <div class="gallery-preview">
                        {% for img in page.gallery_images[:5] %}
                        <img src="{{ img }}" alt="Gallery preview">
                        {% endfor %}
                    </div>
                    {% endif %}
                    {% if page.products %}
                    <div><strong>Products:</strong> {{ page.products|length }} items</div>
                    {% endif %}
                </div>
                <a href="/kahu/edit/{{ page_id }}" class="edit-btn">✏️ Edit Page</a>
            </div>
            {% endfor %}
        </div>
        <a href="/" class="back-btn">← Back to Website</a>
    </div>
</body>
</html>"""

EDIT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit {{ page.title }}</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 1.5rem;
            font-size: 2rem;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        label {
            display: block;
            color: #2c3e50;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        input[type="text"], input[type="url"], textarea {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1rem;
            font-family: inherit;
            transition: border-color 0.3s ease;
        }
        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            min-height: 400px;
            font-family: 'Consolas', 'Monaco', monospace;
            line-height: 1.5;
        }
        .hint {
            color: #7f8c8d;
            font-size: 0.875rem;
            margin-top: 0.25rem;
        }
        .btn-group {
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
        }
        .save-btn, .back-btn {
            padding: 0.875rem 2rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        .save-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            flex: 1;
        }
        .save-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        .back-btn {
            background: #6c757d;
            color: white;
        }
        .back-btn:hover {
            background: #5a6268;
        }
        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            border: 1px solid #c3e6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>✏️ Edit: {{ page.title }}</h1>
        
        {% if success %}
        <div class="success-message">
            ✅ Changes saved successfully!
        </div>
        {% endif %}
        
        <form method="POST">
            <div class="form-group">
                <label for="title">Page Title</label>
                <input type="text" id="title" name="title" value="{{ page.title }}" required>
            </div>
            
            <div class="form-group">
                <label for="hero_image">Hero Image URL</label>
                <input type="url" id="hero_image" name="hero_image" value="{{ page.hero_image or '' }}" placeholder="https://imgur.com/...">
                <div class="hint">Use Imgur or another image host</div>
            </div>
            
            <div class="form-group">
                <label for="body_md">Page Content (Markdown)</label>
                <textarea id="body_md" name="body_md" required>{{ page.body_md }}</textarea>
                <div class="hint">Use Markdown formatting: **bold**, *italic*, ## Headers, [links](url)</div>
            </div>
            
            <div class="form-group">
                <label for="product_url">Product Link (optional)</label>
                <input type="url" id="product_url" name="product_url" value="{{ page.product_url or '' }}" placeholder="https://amazon.com/...">
            </div>
            
            <div class="btn-group">
                <a href="/kahu" class="back-btn">← Cancel</a>
                <button type="submit" class="save-btn">💾 Save Changes</button>
            </div>
        </form>
    </div>
</body>
</html>"""

def save_content(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_content():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_PAGES

@app.route("/")
def home():
    return redirect("/home")

@app.route("/<page_id>")
def show_page(page_id):
    content = load_content()
    pages = content["pages"]
    
    if page_id not in pages:
        abort(404)
    
    page = pages[page_id]
    body_html = markdown.markdown(
        page["body_md"],
        extensions=['extra', 'nl2br']
    )
    
    nav_items = [
        {"title": pages[pid]["title"], "url": f"/{pid}"}
        for pid in content["order"]
    ]
    
    return render_template_string(
        PAGE_TEMPLATE,
        page=page,
        body_html=body_html,
        nav_items=nav_items,
        style=ENHANCED_STYLE
    )

@app.route("/myron-golden")
def myron_golden_page():
    return render_template_string(
        MYRON_GOLDEN_TEMPLATE,
        style=ENHANCED_STYLE
    )

@app.route("/kingdom_keys")
def kingdom_keys():
    return show_page("kingdom_keys")

@app.route("/kahu")
def admin_panel():
    content = load_content()
    return render_template_string(
        ADMIN_TEMPLATE,
        pages=content["pages"]
    )

@app.route("/kahu/edit/<page_id>", methods=["GET", "POST"])
def edit_page(page_id):
    content = load_content()
    pages = content["pages"]
    
    if page_id not in pages:
        abort(404)
    
    success = False
    
    if request.method == "POST":
        pages[page_id].update({
            "title": request.form.get("title"),
            "hero_image": request.form.get("hero_image") or None,
            "body_md": request.form.get("body_md"),
            "product_url": request.form.get("product_url") or ""
        })
        save_content(content)
        success = True
    
    return render_template_string(
        EDIT_TEMPLATE,
        page=pages[page_id],
        page_id=page_id,
        success=success
    )

if __name__ == "__main__":
    if not DATA_FILE.exists():
        save_content(DEFAULT_PAGES)
    
    port = int(os.environ.get("PORT", 5000))
    print("🌺 Starting...")
    print(f"🌊 Visit: http://localhost:{port}")
    print(f"⚙️  Admin: http://localhost:{port}/kahu")
    print(f"🎁  Kingdom Keys: http://localhost:{port}/kingdom_keys")
    print(f"💰  Myron Golden: http://localhost:{port}/myron-golden")
    app.run(host="0.0.0.0", port=port, debug=False)
