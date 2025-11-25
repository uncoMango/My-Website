"""
===============================================================================
KE AUPUNI O KE AKUA - MOBILE-RESPONSIVE WEBSITE
Complete Single-File Version with FIXED BUY BUTTONS
===============================================================================

FIXES:
✅ Pastor Planners page - Amazon buy button restored
✅ Nahanahe page - THREE buy buttons added

INSTRUCTIONS:
1. Copy this ENTIRE file
2. Save it as: ke_aupuni_mobile.py
3. Run: python ke_aupuni_mobile.py
4. Visit: http://localhost:5000

That's it! Your mobile-responsive website will be running.

===============================================================================
"""

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
        "products": [
            {
                "title": "🎵 Listen on Apple Music",
                "url": "https://music.apple.com/us/browse"
            },
            {
                "title": "🎵 Listen on Amazon Music",
                "url": "https://music.amazon.com/"
            },
            {
                "title": "🎵 Listen on Spotify",
                "url": "https://open.spotify.com/"
            }
        ]
    }
}

# MOBILE-RESPONSIVE CSS with Hamburger Menu
ENHANCED_STYLE = """
:root {
    --primary-blue: #0A4C6A;
    --accent-teal: #2A9D8F;
    --coral: #E76F51;
    --sand: #F4A261;
    --light-bg: #F8F9FA;
    --text-dark: #2C3E50;
    --text-light: #FFFFFF;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Georgia', 'Times New Roman', serif;
    line-height: 1.8;
    color: var(--text-dark);
    background-color: var(--light-bg);
}

/* NAVIGATION */
nav {
    background-color: var(--primary-blue);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    position: sticky;
    top: 0;
    z-index: 1000;
}

.nav-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    min-height: 60px;
}

.nav-title {
    color: var(--text-light);
    font-size: 1.2rem;
    font-weight: 600;
    text-decoration: none;
}

.nav-menu {
    display: flex;
    list-style: none;
    gap: 1.5rem;
}

.nav-menu a {
    color: var(--text-light);
    text-decoration: none;
    padding: 0.75rem 1rem;
    border-radius: 4px;
    transition: background-color 0.3s ease;
    font-size: 1rem;
}

.nav-menu a:hover,
.nav-menu a.active {
    background-color: var(--accent-teal);
}

/* HAMBURGER MENU TOGGLE (hidden on desktop) */
.nav-toggle {
    display: none;
    flex-direction: column;
    gap: 4px;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.5rem;
}

.nav-toggle span {
    width: 25px;
    height: 3px;
    background-color: var(--text-light);
    transition: all 0.3s ease;
    border-radius: 2px;
}

/* HERO SECTION */
.hero {
    background-size: cover;
    background-position: center;
    height: 50vh;
    min-height: 300px;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
}

.hero-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(10, 76, 106, 0.7), rgba(42, 157, 143, 0.5));
}

.hero-content {
    position: relative;
    z-index: 1;
    text-align: center;
}

.hero h1 {
    color: var(--text-light);
    font-size: 2rem;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    padding: 0.5rem 1rem;
}

/* MAIN CONTENT */
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1rem;
}

.content-card {
    background: white;
    border-radius: 8px;
    padding: 2rem 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 2rem;
}

.content-card h2 {
    color: var(--primary-blue);
    font-size: 1.8rem;
    margin: 1.5rem 0 1rem 0;
}

.content-card h3 {
    color: var(--accent-teal);
    font-size: 1.4rem;
    margin: 1.25rem 0 0.75rem 0;
}

.content-card p {
    margin-bottom: 1rem;
    font-size: 1.05rem;
}

.content-card strong {
    color: var(--coral);
}

/* BUY BUTTONS */
.buy-section {
    margin-top: 2.5rem;
    padding-top: 2rem;
    border-top: 3px solid var(--accent-teal);
    text-align: center;
}

.buy-button {
    display: inline-block;
    background-color: var(--coral);
    color: var(--text-light);
    padding: 1rem 2.5rem;
    text-decoration: none;
    border-radius: 6px;
    font-size: 1.1rem;
    font-weight: 600;
    transition: all 0.3s ease;
    margin: 0.5rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    min-height: 44px;
    min-width: 44px;
}

.buy-button:hover {
    background-color: var(--primary-blue);
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

.buy-button:active {
    transform: translateY(0);
}

/* MULTIPLE PRODUCTS GRID */
.products-grid {
    display: grid;
    gap: 1rem;
    margin-top: 2rem;
}

/* FOOTER */
.footer {
    background-color: var(--primary-blue);
    color: var(--text-light);
    text-align: center;
    padding: 2rem 1rem;
    margin-top: 3rem;
}

/* MOBILE RESPONSIVE BREAKPOINTS */
@media (max-width: 767px) {
    /* Hide regular menu, show hamburger */
    .nav-toggle {
        display: flex;
    }
    
    .nav-menu {
        position: fixed;
        top: 60px;
        right: -100%;
        width: 70%;
        max-width: 300px;
        height: calc(100vh - 60px);
        background-color: var(--primary-blue);
        flex-direction: column;
        padding: 2rem 1rem;
        gap: 0;
        transition: right 0.3s ease;
        box-shadow: -2px 0 8px rgba(0,0,0,0.2);
    }
    
    .nav-menu.active {
        right: 0;
    }
    
    .nav-menu a {
        padding: 1rem;
        width: 100%;
        text-align: left;
        border-radius: 4px;
        margin-bottom: 0.5rem;
        min-height: 44px;
        display: flex;
        align-items: center;
    }
    
    .nav-toggle.active span:nth-child(1) {
        transform: rotate(45deg) translate(6px, 6px);
    }
    
    .nav-toggle.active span:nth-child(2) {
        opacity: 0;
    }
    
    .nav-toggle.active span:nth-child(3) {
        transform: rotate(-45deg) translate(6px, -6px);
    }
    
    .hero {
        height: 40vh;
        min-height: 250px;
    }
    
    .hero h1 {
        font-size: 1.5rem;
        padding: 0.5rem;
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
    
    .buy-button {
        display: block;
        width: 100%;
        margin: 0.75rem 0;
    }
    
    .products-grid {
        grid-template-columns: 1fr;
    }
}

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
    
    .products-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

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
    
    .products-grid {
        grid-template-columns: repeat(3, 1fr);
    }
}

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

# Page Template with Hamburger Menu JavaScript and Multiple Product Support
PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page.title }}</title>
    <style>{{ style }}</style>
</head>
<body>
    <nav>
        <div class="nav-container">
            <a href="/" class="nav-title">🌺 Ke Aupuni O Ke Akua</a>
            
            <button class="nav-toggle" aria-label="Toggle menu">
                <span></span>
                <span></span>
                <span></span>
            </button>
            
            <ul class="nav-menu">
                {% for item in nav_items %}
                <li><a href="{{ item.url }}" {% if item.slug == current_page %}class="active"{% endif %}>{{ item.title }}</a></li>
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
            
            {% if page.products %}
            <!-- Multiple products (for Nahanahe page) -->
            <div class="buy-section">
                <h2>🎵 Stream Our Music</h2>
                <div class="products-grid">
                    {% for product in page.products %}
                    <a href="{{ product.url }}" target="_blank" class="buy-button">
                        🛒 {{ product.title }}
                    </a>
                    {% endfor %}
                </div>
            </div>
            {% elif page.product_url %}
            <!-- Single product (for other pages) -->
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
        const navToggle = document.querySelector('.nav-toggle');
        const navMenu = document.querySelector('.nav-menu');

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
    </script>
</body>
</html>"""

# Admin Template (similar structure, with products support)
ADMIN_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - Ke Aupuni O Ke Akua</title>
    <style>{{ style }}
    .admin-container {
        max-width: 1200px;
        margin: 2rem auto;
        padding: 0 1rem;
    }
    
    .admin-header {
        background: white;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .page-selector {
        margin: 1.5rem 0;
    }
    
    .page-selector label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 600;
        color: var(--primary-blue);
    }
    
    .page-selector select {
        width: 100%;
        padding: 0.75rem;
        border: 2px solid var(--accent-teal);
        border-radius: 4px;
        font-size: 1rem;
        background: white;
    }
    
    .editor-card {
        background: white;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .form-group {
        margin-bottom: 1.5rem;
    }
    
    .form-group label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 600;
        color: var(--primary-blue);
    }
    
    .form-control {
        width: 100%;
        padding: 0.75rem;
        border: 2px solid #ddd;
        border-radius: 4px;
        font-size: 1rem;
        font-family: inherit;
    }
    
    .form-control:focus {
        outline: none;
        border-color: var(--accent-teal);
    }
    
    textarea.form-control {
        font-family: 'Courier New', monospace;
        resize: vertical;
    }
    
    .btn {
        background-color: var(--coral);
        color: white;
        padding: 1rem 2rem;
        border: none;
        border-radius: 6px;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        min-height: 44px;
    }
    
    .btn:hover {
        background-color: var(--primary-blue);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .help-text {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.25rem;
    }
    </style>
</head>
<body>
    <nav>
        <div class="nav-container">
            <a href="/" class="nav-title">🌺 Ke Aupuni O Ke Akua</a>
            <button class="nav-toggle" aria-label="Toggle menu">
                <span></span>
                <span></span>
                <span></span>
            </button>
            <ul class="nav-menu">
                <li><a href="/">Home</a></li>
                <li><a href="/admin" class="active">Admin</a></li>
            </ul>
        </div>
    </nav>
    
    <div class="admin-container">
        <div class="admin-header">
            <h1>🛠️ Website Admin Panel</h1>
            <p>Edit your website content below. Changes save immediately.</p>
            
            <div class="page-selector">
                <label for="page-select">Select Page to Edit:</label>
                <select id="page-select" onchange="loadPage(this.value)">
                    {% for page_id, page_data in pages.items() %}
                    <option value="{{ page_id }}" {% if page_id == current_page %}selected{% endif %}>
                        {{ page_data.title }}
                    </option>
                    {% endfor %}
                </select>
            </div>
        </div>
        
        <div class="editor-card">
            <h2>Editing: {{ current_data.title }}</h2>
            
            <form method="POST" action="/admin/save">
                <input type="hidden" name="page_id" value="{{ current_page }}">
                
                <div class="form-group">
                    <label for="title">Page Title:</label>
                    <input type="text" name="title" id="title" class="form-control" 
                           value="{{ current_data.title if current_data else '' }}" required>
                </div>
                
                <div class="form-group">
                    <label for="hero_image">Hero Image URL:</label>
                    <input type="url" name="hero_image" id="hero_image" class="form-control" 
                           value="{{ current_data.hero_image if current_data else '' }}">
                    <p class="help-text">Use Unsplash or upload to your own hosting</p>
                </div>
                
                <div class="form-group">
                    <label for="body_md">Page Content (Markdown):</label>
                    <textarea name="body_md" id="body_md" class="form-control" rows="15">{{ current_data.body_md if current_data else '' }}</textarea>
                    <p class="help-text">Use Markdown formatting: **bold**, *italic*, ## Headings</p>
                </div>
                
                <div class="form-group">
                    <label for="product_url">Product/Buy Now URL (optional):</label>
                    <input type="url" name="product_url" id="product_url" class="form-control" 
                           value="{{ current_data.product_url if current_data else '' }}">
                    <p class="help-text">Amazon or other product link. Leave blank if no product to sell.</p>
                </div>
                
                <button type="submit" class="btn">💾 Save Changes</button>
            </form>
        </div>
    </div>
    
    <script>
        function loadPage(pageId) {
            window.location.href = '/admin?page=' + pageId;
        }
        
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
    
    # Ensure all pages from ORDER exist
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
    
    # Build navigation items
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
    # Force create fresh content with all fixes on startup
    initial_data = {"order": ORDER, "pages": DEFAULT_PAGES}
    save_content(initial_data)
    
    print("🌺 Starting Ke Aupuni O Ke Akua website...")
    print("🌊 Visit: http://localhost:5000")
    print("⚙️ Admin: http://localhost:5000/admin")
    print("\n✅ FIXES APPLIED:")
    print("  ✓ Pastor Planners - Amazon buy button RESTORED")
    print("  ✓ Nahanahe - THREE buy buttons added")
    print("\n📱 Mobile-Responsive Features:")
    print("  ✓ Hamburger menu on mobile")
    print("  ✓ Touch-friendly buttons (44px)")
    print("  ✓ Responsive text sizing")
    print("  ✓ Smart hero heights")
    print("  ✓ No horizontal scrolling")
    print("\n🧪 Test on phone:")
    print("  1. Find your IP: ifconfig (Mac/Linux) or ipconfig (Windows)")
    print("  2. On phone: http://YOUR_IP:5000")
    print("\nE ola mau ke Aupuni O Ke Akua! 🌺\n")
    
    app.run(debug=True, host="0.0.0.0", port=5000)
