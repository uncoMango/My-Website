# ke_aupuni_website.py
# Complete Hawaiian Kingdom website with CD photo gallery and multiple buy links

from flask import Flask, request, redirect, render_template_string, abort, url_for, send_from_directory
import json
from pathlib import Path
import markdown

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

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

Discover the ancient Hawaiian approach to health and wellness that harmonizes mind, body, and spirit with the natural world.""",
        "product_url": "https://www.amazon.com/s?k=hawaiian+wellness+books"
    },
    
    "call_to_repentance": {
        "title": "The Call to Repentance - Foundation for Kingdom Living",
        "hero_image": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?auto=format&fit=crop&w=1200&q=80",
        "body_md": """## Embracing True Repentance for Spiritual Growth

Repentance is not merely feeling sorry for our mistakes - it is a complete transformation of heart and mind that leads us into the fullness of Kingdom living.""",
        "product_url": "https://www.amazon.com/s?k=repentance+spiritual+growth+books"
    },
    
    "pastor_planners": {
        "title": "Pastor Planners - Tools for Ministry Excellence",
        "hero_image": "https://images.unsplash.com/photo-1583212292454-1fe6229603b7?auto=format&fit=crop&w=1200&q=80",
        "body_md": """## Organize Your Ministry with Purpose and Prayer

Effective ministry requires both spiritual sensitivity and practical organization.""",
        "product_url": "https://www.amazon.com/s?k=pastor+planner+ministry+organizer"
    },
    
    "nahenahe_voice": {
        "title": "The Nahenahe Voice of Nahono'opi'ilani - Musical Legacy",
        "hero_image": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=1200&q=80",
        "gallery_images": [
            "/static/images/legacy-album/cover1.jpg",
            "/static/images/legacy-album/cover2.jpg",
            "/static/images/legacy-album/cover3.jpg"
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
        ],
        "body_md": """## Preserving the Gentle Voice of Hawaiian Music

**Nahenahe** means "soft, sweet, melodious" in Hawaiian - the perfect description for the musical legacy we celebrate."""
    }
}

# Enhanced CSS with gallery styles and multiple buy buttons
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

/* CD Gallery Styles */
.cd-gallery {
    margin: 3rem 0;
    padding: 2rem 0;
    border-top: 2px solid rgba(255,255,255,0.3);
}

.cd-gallery h2 {
    text-align: center;
    margin-bottom: 2rem;
    font-size: 2rem;
    color: white;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.9);
}

.gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    max-width: 900px;
    margin: 0 auto;
}

.gallery-item {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    transition: all 0.3s ease;
    cursor: pointer;
}

.gallery-item:hover {
    transform: scale(1.05);
    box-shadow: 0 12px 30px rgba(0,0,0,0.6);
}

.gallery-item img {
    width: 100%;
    height: auto;
    display: block;
}

.modal {
    display: none;
    position: fixed;
    z-index: 9999;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.95);
}

.modal-content {
    margin: 50px auto;
    display: block;
    max-width: 90%;
    max-height: 90vh;
}

.close-modal {
    position: absolute;
    top: 20px;
    right: 40px;
    color: #fff;
    font-size: 50px;
    cursor: pointer;
}

.close-modal:hover {
    color: var(--accent-warm);
}

/* Buy Section with Multiple Buttons */
.buy-section {
    text-align: center;
    margin-top: 3rem;
    padding-top: 2rem;
    border-top: 2px solid rgba(255,255,255,0.3);
}

.buy-section h3 {
    color: white;
    font-size: 1.8rem;
    margin-bottom: 1.5rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
}

.buy-buttons {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 1.5rem;
}

.buy-button {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: linear-gradient(135deg, var(--accent-teal), #4a8b8e);
    color: white;
    padding: 1rem 2rem;
    border-radius: 8px;
    text-decoration: none;
    font-weight: bold;
    font-size: 1.1rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(95, 158, 160, 0.3);
    min-width: 180px;
}

.buy-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(95, 158, 160, 0.5);
}

.buy-button .icon {
    font-size: 1.3rem;
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
    .nav-container { flex-direction: column; gap: 1rem; padding: 0 1rem; }
    .nav-menu { flex-wrap: wrap; justify-content: center; gap: 1rem; }
    .hero { height: 45vh; min-height: 300px; }
    .hero h1 { font-size: 2rem; }
    .container { margin-top: -2rem; padding: 0 1rem 2rem; }
    .content-card { padding: 2rem 1.5rem; }
    .gallery-grid { grid-template-columns: 1fr; gap: 15px; }
    .buy-buttons { flex-direction: column; align-items: center; }
    .buy-button { min-width: 200px; }
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

# HTML Template with Gallery Support and Multiple Buy Buttons
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
            
            {% if page.get('gallery_images') %}
            <div class="cd-gallery">
                <h2>🎵 Album Gallery</h2>
                <div class="gallery-grid">
                    {% for img in page.gallery_images %}
                    <div class="gallery-item">
                        <img src="{{ img }}" alt="Legacy Album" onclick="openModal('{{ img }}')">
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            {% if page.get('product_links') %}
            <div class="buy-section">
                <h3>🎵 Listen & Purchase</h3>
                <div class="buy-buttons">
                    {% for link in page.product_links %}
                    <a href="{{ link.url }}" target="_blank" class="buy-button">
                        <span class="icon">{{ link.icon }}</span>
                        <span>{{ link.name }}</span>
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
        <p>&copy; 2025 Ke Aupuni O Ke Akua. All rights reserved. Made with aloha in Hawaiʻi.</p>
    </footer>
    
    <div id="imageModal" class="modal" onclick="closeModal()">
        <span class="close-modal">&times;</span>
        <img class="modal-content" id="modalImage">
    </div>
    
    <script>
        function openModal(src) {
            document.getElementById('imageModal').style.display = 'block';
            document.getElementById('modalImage').src = src;
        }
        function closeModal() {
            document.getElementById('imageModal').style.display = 'none';
        }
        document.onkeydown = function(e) {
            if (e.key === 'Escape') closeModal();
        };
    </script>
</body>
</html>"""

# Admin Template (unchanged)
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
    print("🌐 Visit: http://localhost:5000")
    print("🔐 Admin: http://localhost:5000/admin")

    app.run(debug=True, host="0.0.0.0", port=5000)
