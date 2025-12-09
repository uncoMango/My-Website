# ke_aupuni_website.py - FIXED FOR DEPLOYMENT AND NEW FEATURES
# Kahu Phil's CORRECT content + Mobile Responsive + Working Admin

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
            "body_md": "Step beyond religious tradition and rediscover the revolutionary Kingdom message that Jesus actually preached. This transformative book series cuts through centuries of religious interpretation to reveal the pure, life-changing teachings of the Kingdom of God.\r\n\r\n### Jesus Preached Kingdom, Not Religion\r\n\r\nFor too long, the church has focused on getting people into heaven instead of bringing heaven to earth. Jesus's primary message wasn't about religion, denominations, or institutional Christianity - it was about the Kingdom of God breaking into human reality here and now.\r\n\r\n### What Jesus Actually Taught\r\n\r\n**Kingdom Principles Over Religious Rules** - Discover how Jesus consistently chose kingdom living over religious compliance, and what that means for us today.\r\n\r\n**Repentance as Transformation** - Move beyond feeling sorry for sins to understanding repentance as a complete transformation of mind, heart, and lifestyle.\r\n\r\n**Heaven on Earth** - Learn how the Kingdom of God is meant to manifest in our daily lives, relationships, and communities right now.\r\n\r\n**Power and Authority** - Understand what Jesus meant when He gave His followers authority to heal, deliver, and demonstrate kingdom reality.\r\n\r\n### Series Overview\r\n\r\nThis isn't a single book but a comprehensive series that systematically unpacks Jesus's kingdom teachings:\r\n\r\n**Volume 1: The Foundation** - Understanding what the Kingdom of God actually is and why Jesus made it His central message.\r\n\r\n**Volume 2: Kingdom Citizenship** - What it means to be a citizen of God's kingdom while living in earthly systems.\r\n\r\n**Volume 3: Kingdom Economics** - How kingdom principles transform our relationship with money, work, and provision.\r\n\r\n**Volume 4: Kingdom Relationships** - Love, forgiveness, and community the way Jesus intended.\r\n\r\n**Volume 5: Kingdom Authority** - Walking in the supernatural power that Jesus demonstrated and promised to His followers.\r\n\r\n### Beyond Denominational Walls\r\n\r\nThese teachings transcend denominational boundaries and religious traditions. Whether you're Baptist, Methodist, Catholic, Pentecostal, or from any other background, Jesus's kingdom message is for you. It's not about changing your church affiliation - it's about discovering what Jesus actually said and living it out.\r\n\r\n### Practical Kingdom Living\r\n\r\nEach volume includes:\r\n- **Biblical Foundation** - What scripture actually says when we remove religious filters\r\n- **Historical Context** - Understanding Jesus's teachings in their original setting\r\n- **Modern Application** - How to live these principles in contemporary life\r\n- **Personal Transformation** - Practical steps for implementing kingdom living\r\n- **Community Impact** - How kingdom principles change families, neighborhoods, and society\r\n\r\n### A Call to Authentic Christianity\r\n\r\nThis series challenges readers to move beyond:\r\n- Religious performance into authentic relationship\r\n- Sunday Christianity into daily kingdom living\r\n- Denominational identity into kingdom citizenship\r\n- Waiting for heaven into experiencing God's kingdom now\r\n\r\n### The Message That Changes Everything\r\n\r\nWhen you truly understand what Jesus taught about the Kingdom of God, everything changes. Your purpose becomes clear, your identity gets established, and your daily life becomes an adventure of seeing God's kingdom manifest through ordinary moments.\r\n\r\n*\"Repent, for the kingdom of heaven has come near.\" - Matthew 4:17*\r\n\r\nThis isn't just what Jesus said - it's what He lived, demonstrated, and called His followers to experience. The Kingdom of God isn't a future destination; it's a present reality waiting to transform your life today.\r\n\r\n**Join the revolution that Jesus started. Discover the Kingdom message that changes everything.**",
            "product_url": "https://amzn.to/3FfH9ep"
        },
        "aloha_wellness": {
            "title": "Aloha Wellness - Island Health & Healing",
            "hero_image": "https://i.imgur.com/xGeWW3Q.jpeg",
            "intro_text": "## Aloha Wellness - The Sacred Art of How You Eat",
            "body_md": "Discover the life-changing power of **how** you eat, not just what you eat. This groundbreaking wellness book combines cutting-edge scientific research with ancient Hawaiian mana'o (wisdom) to transform your relationship with food and nourishment.\r\n\r\n### Beyond Diet Culture - A Hawaiian Perspective\r\n\r\nTraditional Hawaiian culture understood something modern society has forgotten: eating is a sacred act that connects us to the land, our ancestors, and our own spiritual well-being. This book bridges that ancient wisdom with contemporary nutritional science.\r\n\r\n### Revolutionary Approach: How, Not What\r\n\r\n**Mindful Consumption** - Learn the scientific basis for how mindful eating practices affect digestion, metabolism, and overall health.\r\n\r\n**Cultural Eating Wisdom** - Discover how Hawaiian ancestors approached meals as community ceremonies, gratitude practices, and spiritual connections.\r\n\r\n**Stress and Digestion** - Research-backed insights into how your emotional state during meals affects nutrient absorption and digestive health.\r\n\r\n**Rhythm and Timing** - Ancient Hawaiian understanding of eating in harmony with natural rhythms, supported by modern chronobiology research.\r\n\r\n### Scientific Research Meets Island Wisdom\r\n\r\n**Neuroplasticity and Food Habits** - How changing the way you approach eating can literally rewire your brain for better health.\r\n\r\n**Microbiome Science** - Research on how eating practices (speed, stress level, gratitude) affect gut health and overall wellness.\r\n\r\n**Inflammation Studies** - Scientific evidence showing how eating practices impact inflammatory responses in the body.\r\n\r\n**Community and Longevity** - Research on how social eating practices contribute to the longevity seen in island cultures.\r\n\r\n### Hawaiian Mana'o (Wisdom Principles)\r\n\r\n**Ho'oponopono with Food** - Making right relationships with nourishment and healing food-related guilt or shame.\r\n\r\n**Aloha 'Āina** - Love of the land extends to gratitude for the food it provides and mindful consumption practices.\r\n\r\n**Lōkahi** - Finding unity and balance in your relationship with food, body, and spirit.\r\n\r\n**Mālama** - Caring for your body as a sacred temple through conscious eating practices.\r\n\r\n### Practical Application\r\n\r\nThis isn't another diet book filled with restrictions. Instead, you'll learn practical, science-based techniques for:\r\n- Eating with presence and gratitude\r\n- Reducing stress during meals\r\n- Creating sacred eating spaces\r\n- Building healthy food relationships\r\n- Honoring your body's natural wisdom\r\n\r\n### Cultural Healing\r\n\r\nMany of us carry wounds around food from diet culture, family patterns, or cultural disconnection. This book offers a path to healing that honors both scientific understanding and spiritual wisdom.\r\n\r\n*\"The land gives freely of its abundance. When we receive with gratitude and consume with reverence, we participate in the sacred circle of life.\"*\r\n\r\nTransform your health from the inside out by changing not what you eat, but how you approach the sacred act of nourishment.",
            "product_url": "https://amzn.to/3FfH9ep"
        },
        "call_to_repentance": {
            "title": "The Call to Repentance - Foundation for Kingdom Living",
            "hero_image": "https://i.imgur.com/tG1vBp9.jpeg",
            "intro_text": "## Embracing True Repentance for Spiritual Growth",
            "body_md": "Repentance is not merely feeling sorry for our mistakes - it is a complete transformation of heart and mind that leads us into the fullness of Kingdom living.\r\n\r\n### Understanding Biblical Repentance\r\n\r\nThe Hebrew word **teshuvah** means \"to return\" or \"to turn around.\" It implies a complete change of direction - turning away from patterns that separate us from God and turning toward His kingdom ways.\r\n\r\n**The Three Dimensions of True Repentance:**\r\n\r\n**1. Metanoia (Change of Mind)**\r\nRepentance begins with a fundamental shift in how we think. We must align our thoughts with God's thoughts, seeing ourselves and others through His eyes of love and truth.\r\n\r\n**2. Transformation of Heart**\r\nTrue repentance touches our emotions and desires. Our hearts must be softened and purified, learning to love what God loves and grieve what grieves His heart.\r\n\r\n**3. Changed Actions**\r\nRepentance must bear fruit in our daily choices. We demonstrate our changed hearts through new patterns of behavior that reflect Kingdom values.\r\n\r\n### Practical Steps for Daily Repentance\r\n\r\n**Morning Reflection** - Begin each day by asking the Holy Spirit to search your heart and reveal areas needing His touch.\r\n\r\n**Confession and Forgiveness** - Practice honest confession to God and others, and extend forgiveness as you have been forgiven.\r\n\r\n**Restitution When Possible** - Make amends where you have caused harm, restoring relationships and making wrongs right.\r\n\r\n**Accountability** - Partner with trusted friends or mentors who can speak truth in love and help you stay on the path of righteousness.\r\n\r\n### The Joy of Restoration\r\n\r\nRemember that repentance leads to joy, not condemnation. As we turn our hearts toward God, He celebrates our return like the father welcoming the prodigal son. Every step toward repentance is a step toward freedom, peace, and abundant life in His kingdom.\r\n\r\n*\"Create in me a clean heart, O God, and renew a right spirit within me.\" - Psalm 51:10*",
            "product_url": "https://www.amazon.com/CALL-REPENTANCE-Foundation-Application-Lifestyle-ebook/dp/B0FXYDD9SN"
        },
        "pastor_planners": {
            "title": "Pastor Planners - Tools for Ministry Excellence",
            "hero_image": "https://i.imgur.com/tWnn5UY.png",
            "intro_text": "## Organize Your Ministry with Purpose and Prayer",
            "body_md": "Effective ministry requires both spiritual sensitivity and practical organization. Our Pastor Planners combine beautiful design with functional tools to help you lead with excellence and peace.\r\n\r\n### Features of Our Ministry Planning System\r\n\r\n**Sermon Planning Sections** - Map out your preaching calendar with space for themes, scriptures, and prayer requests. Plan seasonal series and track the spiritual journey of your congregation.\r\n\r\n**Prayer and Pastoral Care** - Dedicated sections for tracking prayer requests, hospital visits, counseling sessions, and follow-up care. Never let a member of your flock slip through the cracks.\r\n\r\n**Meeting and Event Coordination** - Organize board meetings, committee sessions, special events, and outreach activities with integrated calendars and checklists.\r\n\r\n**Personal Spiritual Disciplines** - Maintain your own spiritual health with guided sections for daily devotions, sabbath planning, and personal growth goals.\r\n\r\n### Why Pastors Love Our Planners\r\n\r\n**Hawaiian-Inspired Design** - Beautiful layouts featuring island imagery and scripture verses that bring peace to your planning time.\r\n\r\n**Flexible Formatting** - Works for churches of all sizes and denominations, with customizable sections for your unique ministry context.\r\n\r\n**Durable Construction** - High-quality materials that withstand daily use throughout the church year.\r\n\r\n**Spiritual Focus** - More than just organization - designed to keep your heart centered on God's calling throughout your busy ministry schedule.\r\n\r\n### Testimonials\r\n\r\n*\"This planner has transformed how I approach ministry. I feel more organized and more connected to God's heart for our church.\"* - Pastor Sarah M.\r\n\r\n*\"The prayer tracking section alone has revolutionized my pastoral care. I never forget to follow up anymore.\"* - Pastor David L.\r\n\r\n*\"Beautiful design that actually helps me pray more, not just plan more.\"* - Pastor Maria R.\r\n\r\nOrder your Pastor Planner today and experience the peace that comes from organized, prayer-centered ministry leadership.",
            "product_url": "https://www.amazon.com/s?k=pastor+planner+ministry+organizer"
        },
        "nahenahe_voice": {
            "title": "The Nahenahe Voice of Nahono'opi'ilani - Musical Legacy",
            "hero_image": "https://i.imgur.com/Vyz6nFJ.png",
            "intro_text": "## The Nahenahe Voice of Nahono'opi'ilani - Live from Molokai Ranch Lodge",
            "body_md": "Experience the soul-stirring sounds of authentic Hawaiian music captured live at the historic Molokai Ranch Lodge in the year 2000. This intimate recording showcases the true meaning of **nahenahe** - the gentle, soothing voice that carries the spirit of aloha across the islands.\r\n\r\n### A Sacred Musical Journey\r\n\r\nRecorded in the peaceful setting of Molokai Ranch Lodge, this collection features solo guitar and traditional Hawaiian melodies that speak directly to the heart. Each song was performed live, capturing the mana (spiritual energy) and authentic aloha that can only come from the sacred island of Molokai.\r\n\r\n**Nahenahe** means more than just \"soft\" or \"sweet\" - it represents music that heals, soothes, and connects us to the divine presence that flows through all creation. This recording embodies that sacred tradition.\r\n\r\n### What You'll Experience:\r\n\r\n**Traditional Hawaiian Melodies** - Time-honored songs that have been passed down through generations, preserving the cultural wisdom of our ancestors.\r\n\r\n**Solo Guitar Mastery** - Intimate acoustic performances that showcase the beauty of Hawaiian slack-key guitar traditions and contemporary island sounds.\r\n\r\n**Authentic Island Atmosphere** - The natural acoustics and peaceful energy of Molokai Ranch Lodge create an immersive listening experience.\r\n\r\n**Healing Through Song** - Each track is designed to bring peace, comfort, and the healing power of aloha to your daily life.\r\n\r\n### The Heart of Aloha\r\n\r\nThis recording is more than entertainment - it's a spiritual journey that invites you to slow down, breathe deeply, and connect with the tranquil spirit of Hawaiʻi. Whether you're seeking meditation music, background for quiet reflection, or simply the beauty of authentic Hawaiian sounds, this collection offers a pathway to inner peace.\r\n\r\n*\"Music is the language that speaks when words are not enough. The nahenahe voice carries aloha to every heart that listens.\"*\r\n\r\nPerfect for meditation, relaxation, spiritual practice, or any time you need the gentle embrace of island peace.",
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
    
    .music-buttons {
        flex-direction: column;
    }
    
    .music-button {
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
            data = DEFAULT_PAGES
            save_content(data)
    else:
        # If file doesn't exist, create it with default content
        data = DEFAULT_PAGES
        save_content(data)
    
    # Ensure 'intro_text' is present for all pages for template rendering safety
    for page_id in data.get("pages", {}):
        if "intro_text" not in data["pages"][page_id]:
            data["pages"][page_id]["intro_text"] = ""
    
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
        # Render both intro and body_md
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
            
            {# === NEW: DISPLAY INTRO TEXT HERE (e.g. above the full content) === #}
            {% if intro_html %}
            <div class="intro-text">
                {{ intro_html|safe }}
                <hr style="border-top: 1px solid rgba(255, 255, 255, 0.3); margin: 2rem 0;">
            </div>
            {% endif %}
            
            {{ body_html|safe }}
            
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
            {% elif page.product_url %}
            <div class="buy-section">
                <a href="{{ page.product_url }}" target="_blank" class="buy-button">
                    🛒 Buy Now on Amazon
                </a>
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
    # We assume 'covers' is inside 'static' which is next to this script
    cover_path = BASE / "static" / "covers" / filename
    if cover_path.exists():
        return send_file(cover_path, mimetype='image/jpeg')
    abort(404)


# ============================================
# ADMIN PANEL
# ============================================

ADMIN_PASSWORD = "Kingdom2024"  # Change this in production!

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
        product_url = page_data.get("product_url", "N/A")
        gallery_images = page_data.get("gallery_images", [])
        product_links = page_data.get("product_links", [])
        
        admin_html += f"""
            <div class="page-card">
                <a href="/admin/delete/{page_id}" class="delete-btn" onclick="return confirm('Are you sure you want to delete the page: {page_title}? This cannot be undone.');">🗑️ Delete</a>
                <div class="page-title">{page_title}</div>
                <div class="page-info">
                    <div><strong>URL Slug:</strong> /{page_id}</div>
                    <div><strong>Hero Image:</strong> {hero_image[:60]}...</div>
"""
        
        if product_url != "N/A":
            admin_html += f'                    <div><strong>Product URL:</strong> <a href="{product_url}" target="_blank">View</a></div>\n'
        
        if product_links:
            admin_html += f'                    <div><strong>Music Links:</strong> {len(product_links)} platforms</div>\n'
        
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

# Helper to create a clean slug from a title
def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')

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
            
        new_page_data = {
            "title": new_title,
            "hero_image": request.form.get("hero_image", "https://i.imgur.com/placeholder.png"),
            "intro_text": request.form.get("intro_text", "## New Book Introduction Here"),
            "body_md": request.form.get("body_md", "Full content of the new book/series page goes here."),
            "product_url": request.form.get("product_url", "")
        }
        
        data["pages"][new_slug] = new_page_data
        
        # Add the new page to the end of the navigation order
        if new_slug not in data.get("order", []):
            data.setdefault("order", []).append(new_slug)

        save_content(data)
        return redirect(f"/admin/edit/{new_slug}")
    
    # GET request: show the add new page form
    
    # NOTE: I am redefining the minimal CSS here to ensure it works, 
    # as the main ADMIN_CSS is too heavy for this small form.
    
    add_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add New Page</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: system-ui, -apple-system, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 2rem; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
        h1 {{ color: #2c3e50; margin-bottom: 0.5rem; }}
        .subtitle {{ color: #7f8c8d; margin-bottom: 2rem; }}
        .form-group {{ margin-bottom: 1.5rem; }}
        label {{ display: block; color: #2c3e50; font-weight: 600; margin-bottom: 0.5rem; }}
        input[type="text"], textarea {{ width: 100%; padding: 0.75rem; border: 2px solid #e9ecef; border-radius: 8px; font-size: 1rem; font-family: inherit; transition: border-color 0.3s ease; }}
        input[type="text"]:focus, textarea:focus {{ outline: none; border-color: #667eea; }}
        textarea {{ min-height: 200px; resize: vertical; }}
        .help-text {{ font-size: 0.85rem; color: #6c757d; margin-top: 0.25rem; }}
        .btn-group {{ display: flex; gap: 1rem; margin-top: 2rem; }}
        .btn {{ padding: 0.75rem 1.5rem; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: all 0.2s ease; text-decoration: none; display: inline-block; }}
        .btn-primary {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4); }}
        .btn-secondary {{ background: #6c757d; color: white; }}
        .btn-secondary:hover {{ background: #5a6268; }}
    </style>
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
                <label for="product_url">Product/Buy Button URL (Optional)</label>
                <input type="text" id="product_url" name="product_url">
                <div class="help-text">Amazon or other product link for the main 'Buy Now' button.</div>
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
    
    if request.method == "POST":
        # Update page data
        pages[page_id]["title"] = request.form.get("title", "")
        pages[page_id]["hero_image"] = request.form.get("hero_image", "")
        
        # === NEW: Handling Intro Text ===
        pages[page_id]["intro_text"] = request.form.get("intro_text", "")
        # ================================
        
        pages[page_id]["body_md"] = request.form.get("body_md", "")
        
        # Handle product URL
        product_url = request.form.get("product_url", "").strip()
        if product_url:
            pages[page_id]["product_url"] = product_url
        elif "product_url" in pages[page_id]:
            del pages[page_id]["product_url"]
        
        # Handle gallery images (book covers/CD images)
        gallery_str = request.form.get("gallery_images", "").strip()
        if gallery_str:
            gallery_images = [img.strip() for img in gallery_str.split("\n") if img.strip()]
            # Ensure static path for your uploaded images
            pages[page_id]["gallery_images"] = [
                img if img.startswith('http') else url_for('static', filename='covers/' + img.lstrip('/static/covers/')) 
                for img in gallery_images
            ]
        elif "gallery_images" in pages[page_id]:
            del pages[page_id]["gallery_images"]
        
        # Handle product links (for music page)
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
        return redirect("/admin")
    
    page = pages[page_id]
    
    # Format gallery images for display in the form
    gallery_str = "\n".join(page.get("gallery_images", []))
    
    # Format product links for display in the form
    links_str = ""
    if "product_links" in page:
        links_str = "\n".join([
            f"{link['name']}|{link['url']}|{link['icon']}"
            for link in page["product_links"]
        ])
    
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
                <label for="product_url">Product/Buy Button URL (Optional)</label>
                <input type="text" id="product_url" name="product_url" value="{page.get('product_url', '')}">
                <div class="help-text">Amazon or other product link</div>
            </div>
            
            <div class="form-group">
                <label for="gallery_images">Gallery Images (Optional - One URL per line)</label>
                <textarea id="gallery_images" name="gallery_images" style="min-height: 100px;">{gallery_str}</textarea>
                <div class="help-text">For your covers: **start with /static/covers/** (e.g., /static/covers/my-new-book.jpg). One per line.</div>
            </div>
            
            <div class="form-group">
                <label for="product_links">Music Platform Links (Optional - Format: Name|URL|Icon)</label>
                <textarea id="product_links" name="product_links" style="min-height: 100px;">{links_str}</textarea>
                <div class="help-text">Example: Amazon Music|https://music.amazon.com/...|🛒</div>
            </div>
            
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
    
    port = int(os.environ.get("PORT", 5000))
    print("🌺 Starting Ke Aupuni O Ke Akua website...")
    print(f"🌊 Visit: http://localhost:{port}")
    print("=" * 50)
    app.run(host="0.0.0.0", port=port, debug=True)
