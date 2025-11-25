# ke_aupuni_o_ke_akua_mobile_responsive.py
# Mobile-Responsive Hawaiian Kingdom website with working admin and beautiful content

from flask import Flask, request, redirect, render_template_string, abort, url_for
import json
from pathlib import Path
import markdown

app = Flask(__name__)

# Page order for navigation
ORDER = ["home", "aloha_wellness", "call_to_repentance", "pastor_planners", "nahenahe_voice"]

# Data storage
BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"

# Complete default content with rich Hawaiian-themed pages
DEFAULT_PAGES = {
    "home": {
        "title": "Ke Aupuni O Ke Akua - The Kingdom of God",
        "hero_image": "https://images.unsplash.com/photo-1580656449195-8c8203e0edd0?auto=format&fit=crop&w=1200&q=80",
        "body_md": """## Aloha and Welcome to Our Sacred Space

Welcome to **Ke Aupuni O Ke Akua** (The Kingdom of God), a peaceful digital sanctuary where Hawaiian wisdom meets spiritual growth. Our mission is to share the beauty of island life, traditional mo'olelo (stories), and kingdom principles that nurture both body and soul.

### Traditional Hawaiian Mo'olelo (Sacred Stories)

**The Story of Maui and the Sun (Lā)**
Long ago, the sun raced across the sky so quickly that the people of Hawaiʻi couldn't dry their kapa cloth or grow their crops properly. The clever hero Maui decided to help his people. He climbed to the top of Haleakalā with strong ropes made from his sister's hair. When the sun rose, Maui lassoed its rays and held it tight. "You must slow down and give us longer days!" he demanded. The sun agreed, and from that day forward, we have been blessed with the perfect balance of daylight for our island life.

**Pele's Gift of Creation**
Pele, the volcano goddess, is both creator and destroyer. As she moves through the islands, her fiery spirit shapes new land while transforming the old. She teaches us that all things must change and grow, and that even in destruction, there is the promise of new life. The black sand beaches and fertile volcanic soil are Pele's gifts to the people.

### Navigate Our Sacred Spaces

- **Aloha Wellness**: Traditional Hawaiian healing practices and modern wellness
- **Call to Repentance**: Spiritual foundations for kingdom living
- **Pastor Planners**: Tools for ministry and spiritual organization  
- **Nahenahe Voice**: The gentle musical legacy of Nahono'opi'ilani

May you find peace, wisdom, and aloha in these pages. Mahalo for visiting our sacred digital space.

*E komo mai* - Welcome!""",
        "product_url": ""
    },
    
    "aloha_wellness": {
        "title": "Aloha Wellness - Island Health & Healing",
        "hero_image": "https://images.unsplash.com/photo-1600298881974-6be191ceeda1?auto=format&fit=crop&w=1200&q=80",
        "body_md": """## Traditional Hawaiian Wellness Practices

Discover the ancient Hawaiian approach to health and wellness that harmonizes mind, body, and spirit with the natural world.

### Laʻau Lapaʻau - Traditional Hawaiian Medicine

For over 1,000 years, Hawaiian healers have used the plants and practices of these sacred islands to promote healing and wellness. Our ancestors understood that true health comes from balance - between ourselves and nature, between work and rest, between giving and receiving.

**Key Principles of Hawaiian Wellness:**

**Hoʻoponopono** - The practice of making right relationships. This ancient conflict resolution process helps heal emotional wounds and restore harmony in families and communities.

**Pono Living** - Living in righteousness and balance. This means making choices that honor both yourself and your community, treating the land with respect, and maintaining spiritual practices.

**Lokahi** - Unity and harmony. True wellness comes when we align our physical, mental, and spiritual selves in balance.

### Traditional Healing Plants of Hawaiʻi

**ʻŌlena (Hawaiian Turmeric)** - Used for inflammation and digestive health
**Māmaki** - A gentle tea plant that supports overall wellness
**ʻAwapuhi (Wild Ginger)** - Traditional remedy for nausea and digestive issues
**Kalo (Taro)** - Sacred food plant that nourishes both body and spirit

### Modern Application

Today, we can incorporate these timeless principles into our daily lives through mindful eating, regular connection with nature, practice of gratitude, and maintaining healthy relationships.

*Note: Always consult with healthcare providers before using any traditional remedies.*""",
        "product_url": "https://www.amazon.com/s?k=hawaiian+wellness+books"
    },
    
    "call_to_repentance": {
        "title": "The Call to Repentance - Foundation for Kingdom Living",
        "hero_image": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?auto=format&fit=crop&w=1200&q=80",
        "body_md": """## Embracing True Repentance for Spiritual Growth

Repentance is not merely feeling sorry for our mistakes - it is a complete transformation of heart and mind that leads us into the fullness of Kingdom living.

### Understanding Biblical Repentance

The Hebrew word **teshuvah** means "to return" or "to turn around." It implies a complete change of direction - turning away from patterns that separate us from God and turning toward His kingdom ways.

**The Three Dimensions of True Repentance:**

**1. Metanoia (Change of Mind)**
Repentance begins with a fundamental shift in how we think. We must align our thoughts with God's thoughts, seeing ourselves and others through His eyes of love and truth.

**2. Transformation of Heart**
True repentance touches our emotions and desires. Our hearts must be softened and purified, learning to love what God loves and grieve what grieves His heart.

**3. Changed Actions**
Repentance must bear fruit in our daily choices. We demonstrate our changed hearts through new patterns of behavior that reflect Kingdom values.

### Practical Steps for Daily Repentance

**Morning Reflection** - Begin each day by asking the Holy Spirit to search your heart and reveal areas needing His touch.

**Confession and Forgiveness** - Practice honest confession to God and others, and extend forgiveness as you have been forgiven.

**Restitution When Possible** - Make amends where you have caused harm, restoring relationships and making wrongs right.

**Accountability** - Partner with trusted friends or mentors who can speak truth in love and help you stay on the path of righteousness.

### The Joy of Restoration

Remember that repentance leads to joy, not condemnation. As we turn our hearts toward God, He celebrates our return like the father welcoming the prodigal son. Every step toward repentance is a step toward freedom, peace, and abundant life in His kingdom.

*"Create in me a clean heart, O God, and renew a right spirit within me." - Psalm 51:10*""",
        "product_url": "https://www.amazon.com/s?k=repentance+spiritual+growth+books"
    },
    
    "pastor_planners": {
        "title": "Pastor Planners - Tools for Ministry Excellence",
        "hero_image": "https://images.unsplash.com/photo-1583212292454-1fe6229603b7?auto=format&fit=crop&w=1200&q=80",
        "body_md": """## Organize Your Ministry with Purpose and Prayer

Effective ministry requires both spiritual sensitivity and practical organization. Our Pastor Planners combine beautiful design with functional tools to help you lead with excellence and peace.

### Features of Our Ministry Planning System

**Sermon Planning Sections** - Map out your preaching calendar with space for themes, scriptures, and prayer requests. Plan seasonal series and track the spiritual journey of your congregation.

**Prayer and Pastoral Care** - Dedicated sections for tracking prayer requests, hospital visits, counseling sessions, and follow-up care. Never let a member of your flock slip through the cracks.

**Meeting and Event Coordination** - Organize board meetings, committee sessions, special events, and outreach activities with integrated calendars and checklists.

**Personal Spiritual Disciplines** - Maintain your own spiritual health with guided sections for daily devotions, sabbath planning, and personal growth goals.

### Why Pastors Love Our Planners

**Hawaiian-Inspired Design** - Beautiful layouts featuring island imagery and scripture verses that bring peace to your planning time.

**Flexible Formatting** - Works for churches of all sizes and denominations, with customizable sections for your unique ministry context.

**Durable Construction** - High-quality materials that withstand daily use throughout the church year.

**Spiritual Focus** - More than just organization - designed to keep your heart centered on God's calling throughout your busy ministry schedule.

### Testimonials

*"This planner has transformed how I approach ministry. I feel more organized and more connected to God's heart for our church."* - Pastor Sarah M.

*"The prayer tracking section alone has revolutionized my pastoral care. I never forget to follow up anymore."* - Pastor David L.

*"Beautiful design that actually helps me pray more, not just plan more."* - Pastor Maria R.

Order your Pastor Planner today and experience the peace that comes from organized, prayer-centered ministry leadership.""",
        "product_url": "https://www.amazon.com/s?k=pastor+planner+ministry+organizer"
    },
    
    "nahenahe_voice": {
        "title": "The Nahenahe Voice of Nahono'opi'ilani - Musical Legacy",
        "hero_image": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=1200&q=80",
        "body_md": """## Preserving the Gentle Voice of Hawaiian Music

**Nahenahe** means "soft, sweet, melodious" in Hawaiian - the perfect description for the musical legacy we celebrate and preserve through the work of Nahono'opi'ilani.

### The Heritage of Hawaiian Music

Hawaiian music is more than entertainment - it is our living history, our poetry, and our connection to the land and ancestors. Each mele (song) carries stories, genealogies, and sacred knowledge passed down through generations.

**Traditional Hawaiian Instruments:**

**ʻUkulele** - The "jumping flea" brought joy and melody to the islands
**Slack-Key Guitar** - Unique Hawaiian tunings that echo the sound of waves
**Pahu** - Sacred drum used in hula and ceremony
**ʻIpū** - Gourd percussion that keeps the rhythm of life

### The Nahenahe Style

The nahenahe style emphasizes:
- Gentle, sweet vocal quality
- Emotional depth and sincerity
- Clear pronunciation of Hawaiian lyrics
- Respect for traditional melodies
- Connection to ancestral teachings

### Preserving Our Musical Heritage

Through careful documentation, recording, and teaching, we ensure that future generations can experience the beauty of authentic Hawaiian music. We honor the composers, performers, and kumu (teachers) who have kept these traditions alive.

### Learning Hawaiian Music

Whether you're a beginner or experienced musician, learning Hawaiian music connects you to something greater than yourself. It teaches patience, respect, and the value of carrying forward sacred traditions with care.

*"Music is the heartbeat of our people, the voice of our land, and the prayer of our souls."*

Explore our collection of traditional Hawaiian music and educational resources to deepen your connection to this beautiful cultural legacy.""",
        "product_url": "https://www.amazon.com/s?k=hawaiian+music+ukulele"
    }
}

# MOBILE-RESPONSIVE CSS with Hamburger Menu
ENHANCED_STYLE = """
:root {
    --ocean-blue: #0a4f6e;
    --sand-warm: #e8c89f;
    --accent-teal: #5f9ea0;
    --accent-warm: #d4a574;
    --text-dark: #2c3e50;
    --white-transparent: rgba(255, 255, 255, 0.97);
    --shadow-soft: 0 4px 20px rgba(0, 0, 0, 0.1);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    line-height: 1.7;
    color: var(--text-dark);
    font-size: 16px;
    overflow-x: hidden;
}

/* ==============================================
   MOBILE-RESPONSIVE NAVIGATION
   ============================================== */

.site-nav {
    background: var(--white-transparent);
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: var(--shadow-soft);
    backdrop-filter: blur(10px);
}

.nav-container {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 1rem;
    flex-wrap: wrap;
}

.nav-title {
    font-size: 1.2rem;
    font-weight: bold;
    color: var(--accent-teal);
    text-decoration: none;
    padding: 0.5rem 0;
}

/* Hamburger Menu Button (Mobile Only) */
.nav-toggle {
    display: none;
    flex-direction: column;
    justify-content: space-between;
    width: 44px;
    height: 44px;
    padding: 10px;
    background: transparent;
    border: none;
    cursor: pointer;
    z-index: 1001;
}

.nav-toggle span {
    display: block;
    width: 100%;
    height: 3px;
    background: var(--accent-teal);
    border-radius: 3px;
    transition: all 0.3s ease;
}

.nav-toggle.active span:nth-child(1) {
    transform: rotate(45deg) translate(5px, 5px);
}

.nav-toggle.active span:nth-child(2) {
    opacity: 0;
}

.nav-toggle.active span:nth-child(3) {
    transform: rotate(-45deg) translate(7px, -7px);
}

/* Navigation Menu */
.nav-menu {
    display: flex;
    list-style: none;
    gap: 1rem;
    flex-wrap: wrap;
}

.nav-menu a {
    text-decoration: none;
    color: var(--text-dark);
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    transition: all 0.3s ease;
    display: block;
    white-space: nowrap;
}

.nav-menu a:hover {
    background: var(--accent-teal);
    color: white;
}

/* ==============================================
   HERO SECTION
   ============================================== */

.hero {
    height: 50vh;
    min-height: 300px;
    max-height: 600px;
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
    padding: 1.5rem;
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
}

.hero h1 {
    font-size: 1.8rem;
    font-weight: 400;
    text-shadow: 0 2px 8px rgba(0,0,0,0.8);
    margin-bottom: 0.5rem;
    background: rgba(0,0,0,0.3);
    padding: 1rem;
    border-radius: 8px;
    line-height: 1.3;
}

/* ==============================================
   CONTENT AREA
   ============================================== */

.container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem 1rem;
    width: 100%;
}

.content-card {
    background: white;
    border-radius: 12px;
    padding: 2rem 1.5rem;
    box-shadow: var(--shadow-soft);
    margin-top: 2rem;
}

.content-card h2 {
    color: var(--accent-teal);
    margin-bottom: 1rem;
    font-size: 1.6rem;
    line-height: 1.3;
}

.content-card h3 {
    color: var(--accent-warm);
    margin: 2rem 0 1rem;
    font-size: 1.3rem;
}

.content-card p {
    margin-bottom: 1.2rem;
    font-size: 1rem;
    line-height: 1.8;
}

.content-card strong {
    color: var(--accent-teal);
}

.content-card ul, .content-card ol {
    margin: 1rem 0 1.5rem 1.5rem;
}

.content-card li {
    margin-bottom: 0.5rem;
    line-height: 1.8;
}

/* ==============================================
   BUY BUTTON
   ============================================== */

.buy-section {
    text-align: center;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(95, 158, 160, 0.2);
}

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
    min-height: 44px;
}

.buy-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(95, 158, 160, 0.4);
}

/* ==============================================
   ADMIN PANEL
   ============================================== */

.admin-panel {
    background: white;
    border-radius: 8px;
    padding: 2rem 1.5rem;
    margin: 2rem auto;
    max-width: 800px;
    box-shadow: var(--shadow-soft);
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: bold;
    color: var(--text-dark);
}

.form-control {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid #e1e5e9;
    border-radius: 6px;
    font-size: 16px;
    transition: border-color 0.3s ease;
}

.form-control:focus {
    outline: none;
    border-color: var(--accent-teal);
    box-shadow: 0 0 0 3px rgba(95, 158, 160, 0.1);
}

textarea.form-control {
    min-height: 150px;
    resize: vertical;
}

.btn {
    background: var(--accent-teal);
    color: white;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.3s ease;
    min-height: 44px;
}

.btn:hover {
    background: #4a8b8e;
}

/* ==============================================
   FOOTER
   ============================================== */

.footer {
    text-align: center;
    padding: 2rem 1rem;
    color: var(--text-dark);
    background: var(--white-transparent);
    margin-top: 3rem;
    box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.05);
}

/* ==============================================
   MOBILE BREAKPOINT (< 768px)
   ============================================== */

@media (max-width: 768px) {
    /* Show hamburger, hide menu items */
    .nav-toggle {
        display: flex;
    }
    
    .nav-container {
        padding: 0.5rem 1rem;
    }
    
    .nav-title {
        font-size: 1rem;
    }
    
    .nav-menu {
        display: none;
        flex-direction: column;
        width: 100%;
        background: var(--white-transparent);
        border-radius: 8px;
        margin-top: 1rem;
        padding: 0.5rem 0;
        gap: 0;
    }
    
    .nav-menu.active {
        display: flex;
    }
    
    .nav-menu a {
        padding: 1rem 1.5rem;
        border-radius: 0;
        text-align: center;
    }
    
    .hero {
        height: 40vh;
        min-height: 250px;
    }
    
    .hero h1 {
        font-size: 1.4rem;
        padding: 0.75rem;
    }
    
    .hero-content {
        padding: 1rem;
    }
    
    .content-card {
        padding: 1.5rem 1rem;
        margin-top: 1rem;
    }
    
    .content-card h2 {
        font-size: 1.4rem;
    }
    
    .content-card h3 {
        font-size: 1.2rem;
    }
    
    .content-card p {
        font-size: 1rem;
    }
}

/* ==============================================
   TABLET BREAKPOINT (768px - 1023px)
   ============================================== */

@media (min-width: 768px) and (max-width: 1023px) {
    .nav-menu {
        gap: 0.5rem;
    }
    
    .nav-menu a {
        padding: 0.5rem 0.75rem;
        font-size: 0.95rem;
    }
    
    .hero h1 {
        font-size: 2.2rem;
    }
}

/* ==============================================
   DESKTOP BREAKPOINT (≥ 1024px)
   ============================================== */

@media (min-width: 1024px) {
    .nav-container {
        padding: 0 2rem;
    }
    
    .nav-title {
        font-size: 1.5rem;
    }
    
    .nav-menu {
        gap: 2rem;
    }
    
    .hero {
        height: 60vh;
        min-height: 400px;
    }
    
    .hero h1 {
        font-size: 3rem;
        padding: 1rem 2rem;
    }
    
    .container {
        padding: 3rem 2rem;
    }
    
    .content-card {
        padding: 3rem 2.5rem;
    }
    
    .content-card h2 {
        font-size: 2.2rem;
    }
    
    .content-card h3 {
        font-size: 1.6rem;
    }
    
    .content-card p {
        font-size: 1.1rem;
    }
}

/* ==============================================
   ACCESSIBILITY
   ============================================== */

*:focus-visible {
    outline: 3px solid var(--accent-teal);
    outline-offset: 2px;
}

@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
"""

# Page Template with Hamburger Menu JavaScript
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
            
            <!-- Hamburger Button (Mobile) -->
            <button class="nav-toggle" aria-label="Toggle navigation">
                <span></span>
                <span></span>
                <span></span>
            </button>
            
            <!-- Navigation Menu -->
            <ul class="nav-menu">
                {% for item in nav_items %}
                <li><a href="{{ item.url }}">{{ item.title }}</a></li>
                {% endfor %}
                <li><a href="/admin">Admin</a></li>
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
            
            {% if page.product_url %}
            <div class="buy-section">
                <a href="{{ page.product_url }}" target="_blank" class="buy-button">
                    🛒 Buy Now on Amazon
                </a>
            </div>
            {% endif %}
        </article>
    </main>
    
    <footer class="footer">
        <p>&copy; 2025 Ke Aupuni O Ke Akua. All rights reserved. Made with aloha in Hawaiʻi.</p>
    </footer>
    
    <script>
        // Hamburger Menu Toggle
        const navToggle = document.querySelector('.nav-toggle');
        const navMenu = document.querySelector('.nav-menu');

        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });

        // Close menu when clicking a link
        document.querySelectorAll('.nav-menu a').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            }
        });
    </script>
</body>
</html>"""

# Admin Template (unchanged, already mobile-friendly with form-control styles)
ADMIN_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - Ke Aupuni O Ke Akua</title>
    <style>{{ style }}</style>
</head>
<body>
    <nav class="site-nav">
        <div class="nav-container">
            <a href="/" class="nav-title">Ke Aupuni O Ke Akua</a>
            <button class="nav-toggle" aria-label="Toggle navigation">
                <span></span>
                <span></span>
                <span></span>
            </button>
            <ul class="nav-menu">
                <li><a href="/">Back to Site</a></li>
            </ul>
        </div>
    </nav>
    
    <div class="container">
        <div class="admin-panel">
            <h1>Website Admin Panel</h1>
            <p>Edit your website pages below:</p>
            
            <form method="POST" action="/admin/save">
                <div class="form-group">
                    <label for="page_id">Select Page to Edit:</label>
                    <select name="page_id" class="form-control" onchange="loadPage(this.value)">
                        {% for page_id in pages.keys() %}
                        <option value="{{ page_id }}" {% if page_id == current_page %}selected{% endif %}>
                            {{ pages[page_id].title }}
                        </option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="title">Page Title:</label>
                    <input type="text" name="title" id="title" class="form-control" 
                           value="{{ current_data.title if current_data else '' }}">
                </div>
                
                <div class="form-group">
                    <label for="hero_image">Hero Image URL:</label>
                    <input type="url" name="hero_image" id="hero_image" class="form-control" 
                           value="{{ current_data.hero_image if current_data else '' }}">
                </div>
                
                <div class="form-group">
                    <label for="body_md">Page Content (Markdown):</label>
                    <textarea name="body_md" id="body_md" class="form-control" rows="15">{{ current_data.body_md if current_data else '' }}</textarea>
                </div>
                
                <div class="form-group">
                    <label for="product_url">Product/Buy Now URL (optional):</label>
                    <input type="url" name="product_url" id="product_url" class="form-control" 
                           value="{{ current_data.product_url if current_data else '' }}">
                </div>
                
                <button type="submit" class="btn">Save Changes</button>
            </form>
        </div>
    </div>
    
    <script>
        function loadPage(pageId) {
            window.location.href = '/admin?page=' + pageId;
        }
        
        // Hamburger menu for admin page too
        const navToggle = document.querySelector('.nav-toggle');
        const navMenu = document.querySelector('.nav-menu');

        if (navToggle && navMenu) {
            navToggle.addEventListener('click', () => {
                navMenu.classList.toggle('active');
                navToggle.classList.toggle('active');
            });

            document.querySelectorAll('.nav-menu a').forEach(link => {
                link.addEventListener('click', () => {
                    navMenu.classList.remove('active');
                    navToggle.classList.remove('active');
                });
            });

            document.addEventListener('click', (e) => {
                if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                    navMenu.classList.remove('active');
                    navToggle.classList.remove('active');
                }
            });
        }
    </script>
</body>
</html>"""

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
            data = {"order": ORDER, "pages": DEFAULT_PAGES}
            save_content(data)
    else:
        data = {"order": ORDER, "pages": DEFAULT_PAGES}
        save_content(data)
    
    # Ensure all required pages exist
    for page_id in ORDER:
        if page_id not in data["pages"]:
            data["pages"][page_id] = DEFAULT_PAGES.get(page_id, {
                "title": page_id.replace("_", " ").title(),
                "hero_image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80",
                "body_md": f"Content for {page_id.replace('_', ' ').title()}",
                "product_url": ""
            })
    
    return data

def save_content(data):
    """Save content to JSON file"""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def render_page(page_id, data):
    """Render a complete page"""
    if page_id not in data["pages"]:
        abort(404)
    
    page = data["pages"][page_id]
    
    # Build navigation
    nav_items = []
    for slug in ORDER:
        if slug in data["pages"]:
            nav_items.append({
                "slug": slug,
                "title": data["pages"][slug].get("title", slug.replace("_", " ").title()),
                "url": f"/{slug}" if slug != "home" else "/"
            })
    
    return render_template_string(PAGE_TEMPLATE, 
        page=page,
        nav_items=nav_items,
        style=ENHANCED_STYLE,
        body_html=md_to_html(page.get("body_md", "")),
        current_page=page_id
    )

# Routes
@app.route("/")
def home():
    data = load_content()
    return render_page("home", data)

@app.route("/<page_id>")
def page(page_id):
    data = load_content()
    if page_id not in data["pages"]:
        abort(404)
    return render_page(page_id, data)

@app.route("/admin")
def admin():
    data = load_content()
    current_page = request.args.get("page", "home")
    current_data = data["pages"].get(current_page, {})
    
    return render_template_string(ADMIN_TEMPLATE,
        style=ENHANCED_STYLE,
        pages=data["pages"],
        current_page=current_page,
        current_data=current_data
    )

@app.route("/admin/save", methods=["POST"])
def admin_save():
    data = load_content()
    
    page_id = request.form.get("page_id")
    if page_id in data["pages"]:
        data["pages"][page_id] = {
            "title": request.form.get("title", ""),
            "hero_image": request.form.get("hero_image", ""),
            "body_md": request.form.get("body_md", ""),
            "product_url": request.form.get("product_url", "")
        }
        save_content(data)
    
    return redirect(url_for("admin", page=page_id))

if __name__ == "__main__":
    # Initialize data file if it doesn't exist
    if not DATA_FILE.exists():
        initial_data = {"order": ORDER, "pages": DEFAULT_PAGES}
        save_content(initial_data)
    
    print("🌺 Starting Ke Aupuni O Ke Akua website...")
    print("🌊🏝️ Visit: http://localhost:5000")
    print("⚙️ Admin: http://localhost:5000/admin")
    app.run(debug=True, host="0.0.0.0", port=5000)
