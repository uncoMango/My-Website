# ke_aupuni_o_ke_akua.py
# Complete Hawaiian Kingdom website with working admin and beautiful content

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

### La'au Lapa'au - Traditional Hawaiian Medicine

For over 1,000 years, Hawaiian healers have used the plants and practices of these sacred islands to promote healing and wellness. Our ancestors understood that true health comes from balance - between ourselves and nature, between work and rest, between giving and receiving.

**Key Principles of Hawaiian Wellness:**

**Ho'oponopono** - The practice of making right relationships. This ancient conflict resolution process helps heal emotional wounds and restore harmony in families and communities.

**Pono Living** - Living in righteousness and balance. This means making choices that honor both yourself and your community, treating the land with respect, and maintaining spiritual practices.

**Lokahi** - Unity and harmony. True wellness comes when we align our physical, mental, and spiritual selves in balance.

### Traditional Healing Plants of Hawai?i

**?Olena (Hawaiian Turmeric)** - Used for inflammation and digestive health
**Mamaki** - A gentle tea plant that supports overall wellness
**?Awapuhi (Wild Ginger)** - Traditional remedy for nausea and digestive issues
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

Hawaiian music carries the mana (spiritual power) of our islands. Through gentle melodies and poetic lyrics, traditional Hawaiian songs tell the stories of our people, honor our land, and connect us to the divine presence that moves through all creation.

### Nahono'opi'ilani's Musical Mission

Nahono'opi'ilani dedicated her life to preserving and sharing the nahenahe (gentle) voice of traditional Hawaiian music. Her work encompasses:

**Traditional Mele (Songs)** - Collecting and recording ancient Hawaiian chants and songs that might otherwise be lost to time.

**Contemporary Spiritual Music** - Creating new compositions that blend traditional Hawaiian musical elements with Christian themes and kingdom principles.

**Educational Outreach** - Teaching the cultural and spiritual significance of Hawaiian music to new generations.

**Healing Through Song** - Using music as a tool for emotional and spiritual healing, drawing on the traditional Hawaiian belief in the power of sound and rhythm.

### The Power of Nahenahe Music

In Hawaiian culture, music is never merely entertainment - it is a form of prayer, a way of storytelling, and a method of healing. The nahenahe voice carries several important functions:

**Ho'oponopono Through Song** - Music helps facilitate forgiveness and reconciliation, creating space for hearts to soften and relationships to heal.

**Cultural Preservation** - Each song carries forward the wisdom, values, and stories of our ancestors for future generations.

**Spiritual Connection** - Gentle melodies and meaningful lyrics help listeners connect with God, nature, and their own inner peace.

**Community Building** - Shared musical experiences create bonds between people and strengthen the fabric of community life.

### Experience the Nahenahe Voice

Through recordings, sheet music, and live performances, the legacy of Nahono'opi'ilani continues to touch hearts and transform lives. Whether you're seeking music for worship, meditation, or simply the peace that comes from beautiful sound, the nahenahe voice offers a pathway to tranquility and spiritual connection.

*"Music is the language of the heart, and the nahenahe voice speaks directly to the soul."* - Nahono'opi'ilani""",
        "product_url": "https://www.amazon.com/s?k=hawaiian+music+spiritual+songs"
    }
}

# Enhanced CSS with better styling
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
    padding: 0 2rem;
}

.nav-title {
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--accent-teal);
    text-decoration: none;
}

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
    background: none;
    border: none;
    padding: 3rem 2rem;
    box-shadow: none;
    margin-top: 20vh;
    color: white;
}

.content-card h2 {
    color: var(--accent-teal);
    margin-bottom: 1rem;
    font-size: 1.8rem;
}

.content-card h3 {
    color: var(--accent-warm);
    margin: 2rem 0 1rem;
    font-size: 1.3rem;
}

.content-card p {
    margin-bottom: 1.2rem;
    font-size: 1.05rem;
}

.content-card strong {
    color: var(--accent-teal);
}

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
}

.buy-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(95, 158, 160, 0.4);
}

.admin-panel {
    background: white;
    border-radius: 8px;
    padding: 2rem;
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
    font-size: 1rem;
    transition: border-color 0.3s ease;
}

.form-control:focus {
    outline: none;
    border-color: var(--accent-teal);
}

textarea.form-control {
    min-height: 120px;
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
}

.btn:hover {
    background: #4a8b8e;
}

.footer {
    text-align: center;
    padding: 2rem;
    color: white;
    background: none;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    margin-top: 2rem;
}

.content-card h2,
.content-card h3,
.content-card p,
.content-card strong,
.content-card li {
    color: white;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    line-height: 1.8;
}

.content-card h2 {
    font-size: 2.2rem;
    margin-bottom: 1.5rem;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.9);
}

.content-card h3 {
    font-size: 1.6rem;
    margin: 2rem 0 1rem;
    text-shadow: 2px 2px 5px rgba(0,0,0,0.8);
}

.content-card p {
    font-size: 1.1rem;
    margin-bottom: 1.5rem;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.7);
}

@media (max-width: 768px) {

@media (max-width: 768px) {
    .nav-container { flex-direction: column; gap: 1rem; padding: 0 1rem; }
    .nav-menu { flex-wrap: wrap; justify-content: center; gap: 1rem; }
    .hero { height: 45vh; min-height: 300px; }
    .hero h1 { font-size: 2rem; }
    .container { margin-top: -2rem; padding: 0 1rem 2rem; }
    .content-card { padding: 2rem 1.5rem; }
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

# HTML Template
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
        <p>&copy; 2025 Ke Aupuni O Ke Akua. All rights reserved. Made with aloha in Hawai?i.</p>
    </footer>
</body>
</html>"""

# Admin Template
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
            <ul class="nav-menu">
                <li><a href="/">Back to Site</a></li>
            </ul>
        </div>
    </nav>
    
    <div class="container">
        <div class="admin-panel">
            <h1>Website Admin Panel</h1>
            <p>Edit your website pages below:</p>
            
            <form method="POST" action="/admin/save?key=KeAupuni2025!">
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
    window.location.href = '/admin?page=' + pageId + '&key=KeAupuni2025!';
}
    </script>
</body>
</html>"""

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
    password = request.args.get("key")
    if password != "KeAupuni2025!":
        return "<h1>Access Denied</h1><p>Unauthorized access! 🌺</p>", 403
    
    data = load_content()
    current_page = request.args.get("page", "home")
    current_data = data["pages"].get(current_page, {})
    
    return render_template_string(ADMIN_TEMPLATE,
        style=ENHANCED_STYLE,
        pages=data["pages"],
        current_page=current_page,
        current_data=current_data
    )
    
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
    
    return redirect("/admin?key=KeAupuni2025!")

@app.route("/data-deletion")
def data_deletion():
    """Facebook Data Deletion Instructions Page"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Deletion Instructions - Ke Aupuni O Ke Akua Press</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; line-height: 1.6; color: #333; }
        h1 { color: #2c5282; border-bottom: 3px solid #2c5282; padding-bottom: 10px; }
        h2 { color: #4a5568; margin-top: 30px; }
        .contact-box { background: #f7fafc; border-left: 4px solid #2c5282; padding: 15px; margin: 20px 0; }
        ul { margin: 15px 0; }
        li { margin: 10px 0; }
        .highlight { background: #fef5e7; padding: 2px 5px; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>Data Deletion Instructions</h1>
    <p><strong>Ke Aupuni O Ke Akua Press - Social Media Manager Application</strong></p>
    
    <h2>What Data We Collect</h2>
    <p>Our Social Media Manager application uses Facebook Login to authenticate users and post content on their behalf. We collect and store:</p>
    <ul>
        <li>Your Facebook User ID</li>
        <li>Your name and email address</li>
        <li>Access tokens for posting to your Facebook pages</li>
        <li>Page IDs of pages you manage</li>
    </ul>
    
    <h2>How to Request Data Deletion</h2>
    
    <h3>Method 1: Revoke App Access (Immediate)</h3>
    <ol>
        <li>Go to your <a href="https://www.facebook.com/settings?tab=business_tools" target="_blank">Facebook Settings</a></li>
        <li>Click on "Apps and Websites"</li>
        <li>Find "Social Media Manager" or "AutoPoster"</li>
        <li>Click "Remove"</li>
    </ol>
    
    <h3>Method 2: Email Request</h3>
    <div class="contact-box">
        <p><strong>Send a data deletion request to:</strong></p>
        <p>Email: <span class="highlight">hoaaina61@gmail.com</span></p>
        <p>Subject Line: "Data Deletion Request - Social Media Manager"</p>
    </div>
    
    <h2>What Happens After Deletion Request</h2>
    <ul>
        <li><strong>Within 24 hours:</strong> Your access tokens will be invalidated</li>
        <li><strong>Within 7 days:</strong> All personal data will be permanently deleted</li>
        <li><strong>Within 30 days:</strong> All backup data will be purged</li>
    </ul>
    
    <h2>Questions or Concerns?</h2>
    <div class="contact-box">
        <p><strong>Contact:</strong> Ke Aupuni O Ke Akua Press, Molokaʻi, Hawaiʻi<br>
        Email: hoaaina61@gmail.com</p>
    </div>
    
    <hr style="margin: 40px 0;">
    <p style="text-align: center; color: #718096; font-size: 14px;">
        © 2025 Ke Aupuni O Ke Akua Press. All rights reserved.
    </p>
</body>
</html>'''

if __name__ == "__main__":
    # Initialize data file if it doesn't exist
    if not DATA_FILE.exists():
        initial_data = {"order": ORDER, "pages": DEFAULT_PAGES}
        save_content(initial_data)
    
    print("🌺 Starting Ke Aupuni O Ke Akua website...")
    print("🌐🌐 Visit: http://localhost:5000")
    print("🔐 Admin: http://localhost:5000/admin")

    app.run(debug=True, host="0.0.0.0", port=5000)
