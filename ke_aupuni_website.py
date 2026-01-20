# ke_aupuni_finalized_with_image_placeholders.py
# FIXED: Transparent nav + working hamburger on ALL pages
from flask import Flask, request, redirect, render_template_string, abort, url_for, send_file
import json
from pathlib import Path
import markdown
import os

app = Flask(__name__)
ORDER = ["home", "kingdom_wealth", "free_booklets", "kingdom_keys", "call_to_repentance", "aloha_wellness", "pastor_planners", "nahenahe_voice"]
BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"

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
            "product_url": "https://amzn.to/3FfH9ep",
            "gumroad_url": "https://keaupuni.gumroad.com/l/aloha-wellness"
        },
        "call_to_repentance": {
            "title": "The Call to Repentance - The Kingdom Series",
            "hero_image": "https://i.imgur.com/tG1vBp9.jpeg",
            "body_md": "## The Call to Repentance - Rediscovering Jesus's Kingdom Message\r\n\r\nStep beyond religious tradition and rediscover the revolutionary Kingdom message that Jesus actually preached. This transformative book series cuts through centuries of religious interpretation to reveal the pure, life-changing teachings of the Kingdom of God.\r\n\r\n### Series Overview (Volumes 1-5)\r\n\r\nThis isn't a single book but a comprehensive series that systematically unpacks Jesus's kingdom teachings. **To display the book covers, simply replace the placeholder URL below each Volume with your image URL from Imgur or Amazon.**\r\n\r\n---\r\n\r\n### **Volume 1: The Foundation**\r\n![The Call to Repentance Volume 1 Cover](https://via.placeholder.com/300x450/4A90E2/FFFFFF?text=Volume+1) \r\nUnderstanding what the Kingdom of God actually is and why Jesus made it His central message.\r\n\r\n---\r\n\r\n### **Volume 2: Kingdom Citizenship**\r\n![The Call to Repentance Volume 2 Cover](https://via.placeholder.com/300x450/50C878/FFFFFF?text=Volume+2)\r\nWhat it means to be a citizen of God's kingdom while living in earthly systems.\r\n\r\n---\r\n\r\n### **Volume 3: Kingdom Economics**\r\n![The Call to Repentance Volume 3 Cover](https://via.placeholder.com/300x450/FFB347/FFFFFF?text=Volume+3)\r\nHow kingdom principles transform our relationship with money, work, and provision.\r\n\r\n---\r\n\r\n### **Volume 4: Kingdom Relationships**\r\n![The Call to Repentance Volume 4 Cover](https://via.placeholder.com/300x450/FF6B6B/FFFFFF?text=Volume+4)\r\nLove, forgiveness, and community the way Jesus intended.\r\n\r\n---\r\n\r\n### **Volume 5: Kingdom Authority**\r\n![The Call to Repentance Volume 5 Cover](https://via.placeholder.com/300x450/9B59B6/FFFFFF?text=Volume+5)\r\nWalking in the supernatural power that Jesus demonstrated and promised to His followers.\r\n\r\n---\r\n\r\n## Embracing True Repentance for Spiritual Growth\r\n\r\nRepentance is not merely feeling sorry for our mistakes - it is a complete transformation of heart and mind that leads us into the fullness of Kingdom living.\r\n\r\n### Understanding Biblical Repentance\r\n\r\nThe Hebrew word **teshuvah** means \"to return\" or \"to turn around.\" It implies a complete change of direction - turning away from patterns that separate us from God and turning toward His kingdom ways.\r\n\r\n**The Three Dimensions of True Repentance:**\r\n\r\n**1. Metanoia (Change of Mind)**\r\nRepentance begins with a fundamental shift in how we think. We must align our thoughts with God's thoughts, seeing ourselves and others through His eyes of love and truth.\r\n\r\n**2. Transformation of Heart**\r\nTrue repentance touches our emotions and desires. Our hearts must be softened and purified, learning to love what God loves and grieve what grieves His heart.\r\n\r\n**3. Changed Actions**\r\nRepentance must bear fruit in our daily choices. We demonstrate our changed hearts through new patterns of behavior that reflect Kingdom values.\r\n\r\n*\"Repent, for the kingdom of heaven has come near.\" - Matthew 4:17*\r\n\r\n---\r\n\r\n### A Call to Authentic Christianity\r\n\r\nThis series challenges readers to move beyond:\r\n- Religious performance into authentic relationship\r\n- Sunday Christianity into daily kingdom living\r\n- Denominational identity into kingdom citizenship\r\n- Waiting for heaven into experiencing God's kingdom now\r\n\r\n**Join the revolution that Jesus started. Discover the Kingdom message that changes everything.**",
            "product_url": "https://www.amazon.com/CALL-REPENTANCE-Foundation-Application-Lifestyle-ebook/dp/B0FXYDD9SN",
            "gumroad_url": "https://keaupuni.gumroad.com/l/call-to-repentance"
        },
        "pastor_planners": {
            "title": "Pastor Planners - Tools for Ministry Excellence",
            "hero_image": "https://i.imgur.com/tWnn5UY.png",
            "body_md": "## Organize Your Ministry with Purpose and Prayer\r\n\r\nEffective ministry requires both spiritual sensitivity and practical organization. Our Pastor Planners combine beautiful design with functional tools to help you lead with excellence and peace.\r\n\r\n### Features of Our Ministry Planning System\r\n\r\n**Sermon Planning Sections** - Map out your preaching calendar with space for themes, scriptures, and prayer requests. Plan seasonal series and track the spiritual journey of your congregation.\r\n\r\n**Prayer and Pastoral Care** - Dedicated sections for tracking prayer requests, hospital visits, counseling sessions, and follow-up care. Never let a member of your flock slip through the cracks.\r\n\r\n**Meeting and Event Coordination** - Organize board meetings, committee sessions, special events, and outreach activities with integrated calendars and checklists.\r\n\r\n**Personal Spiritual Disciplines** - Maintain your own spiritual health with guided sections for daily devotions, sabbath planning, and personal growth goals.\r\n\r\n### Why Pastors Love Our Planners\r\n\r\n**Hawaiian-Inspired Design** - Beautiful layouts featuring island imagery and scripture verses that bring peace to your planning time.\r\n\r\n**Flexible Formatting** - Works for churches of all sizes and denominations, with customizable sections for your unique ministry context.\r\n\r\n**Durable Construction** - High-quality materials that withstand daily use throughout the church year.\r\n\r\n**Spiritual Focus** - More than just organization - designed to keep your heart centered on God's calling throughout your busy ministry schedule.\r\n\r\nOrder your Pastor Planner today and experience the peace that comes from organized, prayer-centered ministry leadership.",
            "product_url": "https://www.amazon.com/s?k=pastor+planner+ministry+organizer",
            "gumroad_url": "https://keaupuni.gumroad.com/l/pastor-planner"
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
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
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
    background: rgba(0, 0, 0, 0.25);
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

# ke_aupuni_finalized_with_image_placeholders.py
# FIXED: Transparent nav + working hamburger on ALL pages
from flask import Flask, request, redirect, render_template_string, abort, url_for, send_file
import json
from pathlib import Path
import markdown
import os

app = Flask(__name__)
ORDER = ["home", "kingdom_wealth", "free_booklets", "kingdom_keys", "call_to_repentance", "aloha_wellness", "pastor_planners", "nahenahe_voice"]
BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"

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
            "product_url": "https://amzn.to/3FfH9ep",
            "gumroad_url": "https://keaupuni.gumroad.com/l/aloha-wellness"
        },
        "call_to_repentance": {
            "title": "The Call to Repentance - The Kingdom Series",
            "hero_image": "https://i.imgur.com/tG1vBp9.jpeg",
            "body_md": "## The Call to Repentance - Rediscovering Jesus's Kingdom Message\r\n\r\nStep beyond religious tradition and rediscover the revolutionary Kingdom message that Jesus actually preached. This transformative book series cuts through centuries of religious interpretation to reveal the pure, life-changing teachings of the Kingdom of God.\r\n\r\n### Series Overview (Volumes 1-5)\r\n\r\nThis isn't a single book but a comprehensive series that systematically unpacks Jesus's kingdom teachings. **To display the book covers, simply replace the placeholder URL below each Volume with your image URL from Imgur or Amazon.**\r\n\r\n---\r\n\r\n### **Volume 1: The Foundation**\r\n![The Call to Repentance Volume 1 Cover](https://via.placeholder.com/300x450/4A90E2/FFFFFF?text=Volume+1) \r\nUnderstanding what the Kingdom of God actually is and why Jesus made it His central message.\r\n\r\n---\r\n\r\n### **Volume 2: Kingdom Citizenship**\r\n![The Call to Repentance Volume 2 Cover](https://via.placeholder.com/300x450/50C878/FFFFFF?text=Volume+2)\r\nWhat it means to be a citizen of God's kingdom while living in earthly systems.\r\n\r\n---\r\n\r\n### **Volume 3: Kingdom Economics**\r\n![The Call to Repentance Volume 3 Cover](https://via.placeholder.com/300x450/FFB347/FFFFFF?text=Volume+3)\r\nHow kingdom principles transform our relationship with money, work, and provision.\r\n\r\n---\r\n\r\n### **Volume 4: Kingdom Relationships**\r\n![The Call to Repentance Volume 4 Cover](https://via.placeholder.com/300x450/FF6B6B/FFFFFF?text=Volume+4)\r\nLove, forgiveness, and community the way Jesus intended.\r\n\r\n---\r\n\r\n### **Volume 5: Kingdom Authority**\r\n![The Call to Repentance Volume 5 Cover](https://via.placeholder.com/300x450/9B59B6/FFFFFF?text=Volume+5)\r\nWalking in the supernatural power that Jesus demonstrated and promised to His followers.\r\n\r\n---\r\n\r\n## Embracing True Repentance for Spiritual Growth\r\n\r\nRepentance is not merely feeling sorry for our mistakes - it is a complete transformation of heart and mind that leads us into the fullness of Kingdom living.\r\n\r\n### Understanding Biblical Repentance\r\n\r\nThe Hebrew word **teshuvah** means \"to return\" or \"to turn around.\" It implies a complete change of direction - turning away from patterns that separate us from God and turning toward His kingdom ways.\r\n\r\n**The Three Dimensions of True Repentance:**\r\n\r\n**1. Metanoia (Change of Mind)**\r\nRepentance begins with a fundamental shift in how we think. We must align our thoughts with God's thoughts, seeing ourselves and others through His eyes of love and truth.\r\n\r\n**2. Transformation of Heart**\r\nTrue repentance touches our emotions and desires. Our hearts must be softened and purified, learning to love what God loves and grieve what grieves His heart.\r\n\r\n**3. Changed Actions**\r\nRepentance must bear fruit in our daily choices. We demonstrate our changed hearts through new patterns of behavior that reflect Kingdom values.\r\n\r\n*\"Repent, for the kingdom of heaven has come near.\" - Matthew 4:17*\r\n\r\n---\r\n\r\n### A Call to Authentic Christianity\r\n\r\nThis series challenges readers to move beyond:\r\n- Religious performance into authentic relationship\r\n- Sunday Christianity into daily kingdom living\r\n- Denominational identity into kingdom citizenship\r\n- Waiting for heaven into experiencing God's kingdom now\r\n\r\n**Join the revolution that Jesus started. Discover the Kingdom message that changes everything.**",
            "product_url": "https://www.amazon.com/CALL-REPENTANCE-Foundation-Application-Lifestyle-ebook/dp/B0FXYDD9SN",
            "gumroad_url": "https://keaupuni.gumroad.com/l/call-to-repentance"
        },
        "pastor_planners": {
            "title": "Pastor Planners - Tools for Ministry Excellence",
            "hero_image": "https://i.imgur.com/tWnn5UY.png",
            "body_md": "## Organize Your Ministry with Purpose and Prayer\r\n\r\nEffective ministry requires both spiritual sensitivity and practical organization. Our Pastor Planners combine beautiful design with functional tools to help you lead with excellence and peace.\r\n\r\n### Features of Our Ministry Planning System\r\n\r\n**Sermon Planning Sections** - Map out your preaching calendar with space for themes, scriptures, and prayer requests. Plan seasonal series and track the spiritual journey of your congregation.\r\n\r\n**Prayer and Pastoral Care** - Dedicated sections for tracking prayer requests, hospital visits, counseling sessions, and follow-up care. Never let a member of your flock slip through the cracks.\r\n\r\n**Meeting and Event Coordination** - Organize board meetings, committee sessions, special events, and outreach activities with integrated calendars and checklists.\r\n\r\n**Personal Spiritual Disciplines** - Maintain your own spiritual health with guided sections for daily devotions, sabbath planning, and personal growth goals.\r\n\r\n### Why Pastors Love Our Planners\r\n\r\n**Hawaiian-Inspired Design** - Beautiful layouts featuring island imagery and scripture verses that bring peace to your planning time.\r\n\r\n**Flexible Formatting** - Works for churches of all sizes and denominations, with customizable sections for your unique ministry context.\r\n\r\n**Durable Construction** - High-quality materials that withstand daily use throughout the church year.\r\n\r\n**Spiritual Focus** - More than just organization - designed to keep your heart centered on God's calling throughout your busy ministry schedule.\r\n\r\nOrder your Pastor Planner today and experience the peace that comes from organized, prayer-centered ministry leadership.",
            "product_url": "https://www.amazon.com/s?k=pastor+planner+ministry+organizer",
            "gumroad_url": "https://keaupuni.gumroad.com/l/pastor-planner"
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
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
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
    background: rgba(0, 0, 0, 0.25);
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
<div class="email-capture"><h2>Get FREE Kingdom Business Guide</h2><form action="https://app.kit.com/forms/8979853/subscriptions" method="post"><input type="text" name="fields[first_name]" placeholder="First Name" required style="padding:15px;margin:10px 0;width:100%%;border-radius:6px;border:1px solid #ccc"><input type="email" name="email_address" placeholder="Email" required style="padding:15px;margin:10px 0;width:100%%;border-radius:6px;border:1px solid #ccc"><button type="submit" style="width:100%%;padding:15px;background:#d4af37;color:white;font-weight:bold;border:none;border-radius:6px">GET FREE GUIDE</button></form></div>
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
