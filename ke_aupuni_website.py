from flask import Flask, render_template_string, request, redirect, url_for, flash, get_flashed_messages
import os

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# ==================== CSS STYLES ====================
STYLE = """
/* ==================== RESET & BASE ==================== */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body {
    height: 100%;
    width: 100%;
    overflow-x: hidden;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f9f7f2;
    position: relative;
    min-height: 100vh;
}

/* ==================== FIX: FULL-PAGE HERO SECTIONS ==================== */
.hero-section {
    height: 100vh !important;
    min-height: 100vh !important;
    width: 100vw !important;
    position: relative !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}

/* Fix for background covering entire hero */
.hero-bg {
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    z-index: 1 !important;
    background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)) !important;
}

/* ==================== FIX: PREVENT TEXT OVERLAP ==================== */
.hero-content {
    position: relative !important;
    z-index: 100 !important;
    max-width: 800px !important;
    padding: 20px !important;
    margin-top: 0 !important;
}

.hero-title {
    font-size: 3.5rem !important;
    color: white !important;
    text-shadow: 3px 3px 10px rgba(0, 0, 0, 0.8) !important;
    margin-bottom: 20px !important;
    font-weight: bold !important;
    position: relative !important;
    z-index: 101 !important;
}

.hero-subtitle {
    font-size: 1.3rem !important;
    color: white !important;
    text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.7) !important;
    margin-bottom: 30px !important;
    position: relative !important;
    z-index: 101 !important;
}

/* ==================== NAVIGATION ==================== */
.navbar {
    position: fixed !important;
    top: 0 !important;
    width: 100% !important;
    z-index: 1000 !important;
    background-color: rgba(255, 255, 255, 0.98) !important;
    box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1) !important;
    padding: 15px 0 !important;
}

.nav-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 1.8rem;
    font-weight: bold;
    color: #2c5530;
    text-decoration: none;
    font-family: 'Georgia', serif;
}

.nav-links {
    display: flex;
    gap: 30px;
}

.nav-links a {
    color: #333;
    text-decoration: none;
    font-weight: 600;
    font-size: 1.1rem;
    transition: color 0.3s;
    padding: 5px 0;
    position: relative;
}

.nav-links a:hover {
    color: #2c5530;
}

.nav-links a.active {
    color: #2c5530;
    font-weight: bold;
}

.nav-links a.active::after {
    content: '';
    position: absolute;
    bottom: -5px;
    left: 0;
    width: 100%;
    height: 2px;
    background-color: #2c5530;
}

/* ==================== BUTTONS ==================== */
.btn {
    display: inline-block;
    background-color: #2c5530;
    color: white;
    padding: 14px 32px;
    border-radius: 5px;
    text-decoration: none;
    font-weight: bold;
    font-size: 1.1rem;
    border: none;
    cursor: pointer;
    transition: all 0.3s;
    margin: 10px 5px;
    position: relative;
    z-index: 101;
}

.btn:hover {
    background-color: #1a3a1f;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.btn-outline {
    background-color: transparent;
    border: 2px solid white;
    color: white;
}

.btn-outline:hover {
    background-color: white;
    color: #2c5530;
}

/* ==================== CONTENT SECTIONS ==================== */
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

.section {
    padding: 80px 0;
}

.section-title {
    text-align: center;
    color: #2c5530;
    margin-bottom: 50px;
    font-size: 2.5rem;
    font-family: 'Georgia', serif;
}

/* ==================== PRODUCTS GRID ==================== */
.products-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 30px;
    margin-top: 40px;
}

.product-card {
    background: white;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s;
}

.product-card:hover {
    transform: translateY(-10px);
}

.product-image {
    height: 200px;
    background-color: #f0e6d6;
    display: flex;
    align-items: center;
    justify-content: center;
}

.product-info {
    padding: 25px;
}

.product-info h3 {
    color: #2c5530;
    margin-bottom: 10px;
    font-size: 1.5rem;
}

.product-price {
    color: #2c5530;
    font-weight: bold;
    font-size: 1.3rem;
    margin: 15px 0;
}

/* ==================== FORMS ==================== */
.form-group {
    margin-bottom: 25px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #2c5530;
}

.form-control {
    width: 100%;
    padding: 12px 15px;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 1rem;
    font-family: inherit;
}

.form-control:focus {
    outline: none;
    border-color: #2c5530;
    box-shadow: 0 0 0 3px rgba(44, 85, 48, 0.1);
}

textarea.form-control {
    min-height: 150px;
    resize: vertical;
}

/* ==================== FOOTER ==================== */
footer {
    background-color: #2c5530;
    color: white;
    padding: 60px 0 20px;
    margin-top: 80px;
}

.footer-content {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 40px;
    margin-bottom: 40px;
}

.footer-section h3 {
    color: #f0e6d6;
    margin-bottom: 20px;
    font-size: 1.5rem;
}

.footer-section h4 {
    color: #f0e6d6;
    margin-bottom: 20px;
}

.footer-section a {
    color: #ddd;
    text-decoration: none;
    display: block;
    margin-bottom: 10px;
    transition: color 0.3s;
}

.footer-section a:hover {
    color: white;
}

.footer-section p {
    color: #ddd;
    margin-bottom: 10px;
}

.footer-bottom {
    text-align: center;
    padding-top: 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    color: #aaa;
    font-size: 0.9rem;
}

/* ==================== FLASH MESSAGES ==================== */
.flash-messages {
    position: fixed;
    top: 100px;
    right: 20px;
    z-index: 1001;
    max-width: 400px;
}

.flash {
    padding: 15px 20px;
    margin-bottom: 10px;
    border-radius: 5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    animation: slideIn 0.3s ease;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.flash-success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.flash-error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* ==================== RESPONSIVE DESIGN ==================== */
@media (max-width: 768px) {
    .nav-links {
        display: none;
        position: absolute;
        top: 100%;
        left: 0;
        width: 100%;
        background-color: white;
        flex-direction: column;
        padding: 20px;
        box-shadow: 0 5px 10px rgba(0, 0, 0, 0.1);
    }
    
    .nav-links.active {
        display: flex;
    }
    
    .mobile-menu-btn {
        display: block;
        font-size: 24px;
        color: #2c5530;
        cursor: pointer;
    }
    
    .hero-title {
        font-size: 2.5rem !important;
    }
    
    .hero-subtitle {
        font-size: 1.1rem !important;
    }
    
    .section {
        padding: 50px 0;
    }
    
    .products-grid {
        grid-template-columns: 1fr;
    }
    
    .footer-content {
        grid-template-columns: 1fr;
        text-align: center;
    }
}

/* ==================== UTILITY CLASSES ==================== */
.text-center { text-align: center; }
.mt-1 { margin-top: 10px; }
.mt-2 { margin-top: 20px; }
.mt-3 { margin-top: 30px; }
.mt-4 { margin-top: 40px; }
.mb-1 { margin-bottom: 10px; }
.mb-2 { margin-bottom: 20px; }
.mb-3 { margin-bottom: 30px; }
.mb-4 { margin-bottom: 40px; }
.p-1 { padding: 10px; }
.p-2 { padding: 20px; }
.p-3 { padding: 30px; }
.p-4 { padding: 40px; }
"""

# ==================== HTML TEMPLATES ====================

def get_base_template(title, active_page='home'):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Keaupuni Akeakua</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Georgia:wght@400;700&family=Segoe+UI:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        {STYLE}
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="nav-container">
            <a href="/" class="logo">Keaupuni Akeakua</a>
            <div class="nav-links" id="navLinks">
                <a href="/" {'class="active"' if active_page == 'home' else ''}>Home</a>
                <a href="/about" {'class="active"' if active_page == 'about' else ''}>About</a>
                <a href="/products" {'class="active"' if active_page == 'products' else ''}>Products</a>
                <a href="/contact" {'class="active"' if active_page == 'contact' else ''}>Contact</a>
            </div>
            <div class="mobile-menu-btn" id="mobileMenuBtn">
                <i class="fas fa-bars"></i>
            </div>
        </div>
    </nav>

    <!-- Flash Messages -->
    <div class="flash-messages" id="flashMessages"></div>

    <!-- Main Content -->
    <main>
        {{% content %}}
    </main>

    <!-- Footer -->
    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>Keaupuni Akeakua</h3>
                    <p>Preserving Hawaiian spiritual traditions</p>
                </div>
                <div class="footer-section">
                    <h4>Navigation</h4>
                    <a href="/">Home</a>
                    <a href="/about">About</a>
                    <a href="/products">Products</a>
                    <a href="/contact">Contact</a>
                </div>
                <div class="footer-section">
                    <h4>Contact</h4>
                    <p><i class="fas fa-envelope"></i> info@keaupuniakeakua.faith</p>
                    <p><i class="fas fa-phone"></i> (808) 123-4567</p>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2024 Keaupuni Akeakua. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script>
        // Mobile menu toggle
        document.addEventListener('DOMContentLoaded', function() {{
            const mobileMenuBtn = document.getElementById('mobileMenuBtn');
            const navLinks = document.getElementById('navLinks');
            
            if (mobileMenuBtn) {{
                mobileMenuBtn.addEventListener('click', function() {{
                    navLinks.classList.toggle('active');
                }});
            }}
            
            // Close flash messages
            const flashMessages = document.getElementById('flashMessages');
            if (flashMessages) {{
                setTimeout(() => {{
                    flashMessages.style.opacity = '0';
                    flashMessages.style.transition = 'opacity 0.5s';
                    setTimeout(() => flashMessages.remove(), 500);
                }}, 5000);
            }}
            
            // Add padding to body for fixed nav
            const navbar = document.querySelector('.navbar');
            if (navbar) {{
                document.body.style.paddingTop = navbar.offsetHeight + 'px';
            }}
        }});
        
        // Handle window resize
        window.addEventListener('resize', function() {{
            const navLinks = document.getElementById('navLinks');
            if (window.innerWidth > 768) {{
                navLinks.classList.remove('active');
            }}
        }});
    </script>
</body>
</html>
"""

# ==================== ROUTES ====================

@app.route('/')
def home():
    content = f"""
    <!-- Hero Section - FIXED: Full page, no overlap -->
    <section class="hero-section" style="background: url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e?ixlib=rb-4.0.3&auto=format&fit=crop&w=1350&q=80');">
        <div class="hero-bg"></div>
        <div class="hero-content">
            <h1 class="hero-title">Welcome to Keaupuni Akeakua</h1>
            <p class="hero-subtitle">Authentic Hawaiian Spiritual Products & Traditional Healing Wisdom</p>
            <div>
                <a href="/products" class="btn">Explore Products</a>
                <a href="/about" class="btn btn-outline">Our Story</a>
            </div>
        </div>
    </section>

    <!-- Mission Section -->
    <section class="section">
        <div class="container">
            <h2 class="section-title">Our Sacred Mission</h2>
            <div style="max-width: 800px; margin: 0 auto; text-align: center;">
                <p style="font-size: 1.2rem; margin-bottom: 30px; color: #555;">
                    Keaupuni Akeakua ("Realm of the Divine") is dedicated to preserving and sharing 
                    authentic Hawaiian spiritual practices. We honor the 'āina (land) and our kupuna 
                    (ancestors) through traditional products and healing wisdom.
                </p>
                <a href="/about" class="btn">Learn About Our Traditions</a>
            </div>
        </div>
    </section>

    <!-- Products Preview -->
    <section class="section" style="background-color: #f0e6d6;">
        <div class="container">
            <h2 class="section-title">Sacred Products</h2>
            <div class="products-grid">
                <div class="product-card">
                    <div class="product-image">
                        <i class="fas fa-leaf" style="font-size: 60px; color: #2c5530;"></i>
                    </div>
                    <div class="product-info">
                        <h3>Healing Herbs & Plants</h3>
                        <p>Traditional Hawaiian medicinal plants used for centuries in healing practices</p>
                        <div class="product-price">$45.00</div>
                        <a href="/products" class="btn" style="padding: 10px 20px; font-size: 1rem;">View Details</a>
                    </div>
                </div>
                
                <div class="product-card">
                    <div class="product-image">
                        <i class="fas fa-gem" style="font-size: 60px; color: #2c5530;"></i>
                    </div>
                    <div class="product-info">
                        <h3>Spiritual Stones</h3>
                        <p>Sacred stones for protection, energy work, and spiritual connection</p>
                        <div class="product-price">$35.00</div>
                        <a href="/products" class="btn" style="padding: 10px 20px; font-size: 1rem;">View Details</a>
                    </div>
                </div>
                
                <div class="product-card">
                    <div class="product-image">
                        <i class="fas fa-hand-holding-heart" style="font-size: 60px; color: #2c5530;"></i>
                    </div>
                    <div class="product-info">
                        <h3>Ceremonial Items</h3>
                        <p>Authentic tools for traditional Hawaiian ceremonies and rituals</p>
                        <div class="product-price">$75.00</div>
                        <a href="/products" class="btn" style="padding: 10px 20px; font-size: 1rem;">View Details</a>
                    </div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 50px;">
                <a href="/products" class="btn">View All Sacred Products</a>
            </div>
        </div>
    </section>

    <!-- Contact CTA -->
    <section class="section">
        <div class="container">
            <h2 class="section-title">Seeking Spiritual Guidance?</h2>
            <div style="text-align: center; max-width: 600px; margin: 0 auto;">
                <p style="font-size: 1.2rem; margin-bottom: 30px; color: #555;">
                    Connect with us for traditional Hawaiian spiritual consultations, 
                    personalized guidance, and healing sessions.
                </p>
                <a href="/contact" class="btn">Request Guidance</a>
            </div>
        </div>
    </section>
    """
    
    template = get_base_template("Home", "home")
    return template.replace("{{% content %}}", content)

@app.route('/about')
def about():
    content = f"""
    <!-- About Hero - FIXED: Full page -->
    <section class="hero-section" style="background: url('https://images.unsplash.com/photo-1544551763-46a013bb70d5?ixlib=rb-4.0.3&auto=format&fit=crop&w=1350&q=80');">
        <div class="hero-bg"></div>
        <div class="hero-content">
            <h1 class="hero-title">Our Story & Traditions</h1>
            <p class="hero-subtitle">Preserving Hawaiian spiritual wisdom for generations</p>
        </div>
    </section>

    <!-- Our Story -->
    <section class="section">
        <div class="container">
            <div style="max-width: 800px; margin: 0 auto;">
                <h2 class="section-title">Who We Are</h2>
                <div style="font-size: 1.1rem; line-height: 1.8; color: #555;">
                    <p style="margin-bottom: 20px;">
                        Keaupuni Akeakua, which translates to "Realm of the Divine," was founded with a deep 
                        reverence for Hawaiian culture and spiritual practices. Our journey began with a simple 
                        mission: to preserve and share the authentic spiritual wisdom of our kupuna (ancestors).
                    </p>
                    
                    <p style="margin-bottom: 20px;">
                        As modern life continues to evolve, we believe it's crucial to maintain the connection 
                        to traditional Hawaiian spirituality. Our offerings are more than just products – they 
                        are bridges to understanding, healing, and connecting with the 'āina (land) and our 
                        cultural heritage.
                    </p>
                    
                    <h3 style="color: #2c5530; margin: 30px 0 15px;">Our Mission</h3>
                    <p style="margin-bottom: 30px;">
                        To provide authentic Hawaiian spiritual products and guidance while honoring traditional 
                        practices, supporting local communities, and educating those seeking spiritual connection 
                        through Hawaiian wisdom.
                    </p>
                </div>
                
                <!-- Values Grid -->
                <h2 class="section-title" style="margin-top: 60px;">Our Values</h2>
                <div class="products-grid">
                    <div class="product-card">
                        <div class="product-image">
                            <i class="fas fa-mountain" style="font-size: 60px; color: #2c5530;"></i>
                        </div>
                        <div class="product-info">
                            <h3>Respect for 'Āina</h3>
                            <p>Honoring and protecting the land that sustains us</p>
                        </div>
                    </div>
                    
                    <div class="product-card">
                        <div class="product-image">
                            <i class="fas fa-history" style="font-size: 60px; color: #2c5530;"></i>
                        </div>
                        <div class="product-info">
                            <h3>Cultural Preservation</h3>
                            <p>Keeping traditional practices alive for future generations</p>
                        </div>
                    </div>
                    
                    <div class="product-card">
                        <div class="product-image">
                            <i class="fas fa-handshake" style="font-size: 60px; color: #2c5530;"></i>
                        </div>
                        <div class="product-info">
                            <h3>Authenticity</h3>
                            <p>Genuine products made with traditional knowledge</p>
                        </div>
                    </div>
                    
                    <div class="product-card">
                        <div class="product-image">
                            <i class="fas fa-heart" style="font-size: 60px; color: #2c5530;"></i>
                        </div>
                        <div class="product-info">
                            <h3>Healing & Aloha</h3>
                            <p>Promoting spiritual, emotional, and physical wellness</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    """
    
    template = get_base_template("About Us", "about")
    return template.replace("{{% content %}}", content)

@app.route('/products')
def products():
    content = f"""
    <!-- Products Hero - FIXED: Full page -->
    <section class="hero-section" style="background: url('https://images.unsplash.com/photo-1518837695005-2083093ee35b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1350&q=80');">
        <div class="hero-bg"></div>
        <div class="hero-content">
            <h1 class="hero-title">Sacred Hawaiian Products</h1>
            <p class="hero-subtitle">Authentic spiritual items for healing, protection, and connection</p>
        </div>
    </section>

    <!-- Products Content -->
    <section class="section">
        <div class="container">
            <div style="text-align: center; margin-bottom: 50px;">
                <h2 class="section-title">Our Spiritual Offerings</h2>
                <p style="max-width: 600px; margin: 0 auto; font-size: 1.1rem; color: #666;">
                    Each product is carefully selected or created with respect for traditional Hawaiian practices and spiritual significance.
                </p>
            </div>

            <!-- Healing Herbs Category -->
            <h3 style="color: #2c5530; margin: 40px 0 20px; padding-bottom: 10px; border-bottom: 2px solid #f0e6d6;">Healing Herbs & Plants</h3>
            <div class="products-grid">
                <div class="product-card">
                    <div class="product-image">
                        <i class="fas fa-leaf" style="font-size: 70px; color: #2c5530;"></i>
                    </div>
                    <div class="product-info">
                        <h3>Traditional Healing Herbs Bundle</h3>
                        <p>A collection of sacred Hawaiian medicinal plants used for centuries in traditional healing practices.</p>
                        <div class="product-price">$45.00</div>
                        <a href="/contact" class="btn" style="padding: 10px 20px; font-size: 1rem;">Inquire About Purchase</a>
                    </div>
                </div>
                
                <div class="product-card">
                    <div class="product-image">
                        <i class="fas fa-spa" style="font-size: 70px; color: #2c5530;"></i>
                    </div>
                    <div class="product-info">
                        <h3>Sacred Ti Leaf Bundle</h3>
                        <p>Ti leaves used for protection, purification, and blessing ceremonies.</p>
                        <div class="product-price">$25.00</div>
                        <a href="/contact" class="btn" style="padding: 10px 20px; font-size: 1rem;">Inquire About Purchase</a>
                    </div>
                </div>
                
                <div class="product-card">
                    <div class="product-image">
                        <i class="fas fa-seedling" style="font-size: 70px; color: #2c5530;"></i>
                    </div>
                    <div class="product-info">
                        <h3>Medicinal Plant Seeds</h3>
                        <p>Seeds of traditional Hawaiian healing plants for growing your own medicinal garden.</p>
                        <div class="product-price">$18.00</div>
                        <a href="/contact" class="btn" style="padding: 10px 20px; font-size: 1rem;">Inquire About Purchase</a>
                    </div>
                </div>
            </div>

            <!-- Spiritual Stones Category -->
            <h3 style="color: #2c5530; margin: 60px 0 20px; padding-bottom: 10px; border-bottom: 2px solid #f0e6d6;">Spiritual Stones & Crystals</h3>
            <div class="products-grid">
                <div class="product-card">
                    <div class="product-image">
                        <i class="fas fa-gem" style="font-size: 70px; color: #2c5530;"></i>
                    </div>
                    <div class="product-info">
                        <h3>Hawaiian Lava Stones</h3>
                        <p>Sacred stones from Hawaiian volcanoes, used for grounding and connection to Pele.</p>
                        <div class="product-price">$35.00</div>
                        <a href="/contact" class="btn" style="padding: 10px 20px; font-size: 1rem;">Inquire About Purchase</a>
                    </div>
                </div>
                
                <div class="product-card">
                    <div class="product-image">
                        <i class="fas fa-mountain" style="font-size: 70px; color: #2c5530;"></i>
                    </div>
                    <div class="product-info">
                        <h3>Protection Stone Set</h3>
                        <p>A collection of stones traditionally used for spiritual protection and energy clearing.</p>
                        <div class="product-price">$55.00</div>
                        <a href="/contact" class="btn" style="padding: 10px 20px; font-size: 1rem;">Inquire About Purchase</a>
                    </div>
                </div>
            </div>

            <!-- Ceremonial Items Category -->
            <h3 style="color: #2c5530; margin: 60px 0 20px; padding-bottom: 10px; border-bottom: 2px solid #f0e6d6;">Ceremonial Items</h3>
            <div class="products-grid">
                <div class="product-card">
                    <div class="product-image">
                        <i class="fas fa-fire" style="font-size: 70px; color: #2c5530;"></i>
                    </div>
                    <div class="product-info">
                        <h3>Traditional Ceremony Bowl</h3>
                        <p>Handcrafted bowl used in traditional Hawaiian ceremonies and offerings.</p>
                        <div class="product-price">$75.00</div>
                        <a href="/contact" class="btn" style="padding: 10px 20px; font-size: 1rem;">Inquire About Purchase</a>
                    </div>
                </div>
                
                <div class="product-card">
                    <div class="product-image">
                        <i class="fas fa-feather-alt" style="font-size: 70px; color: #2c5530;"></i>
                    </div>
                    <div class="product-info">
                        <h3>Sacred Feather Bundle</h3>
                        <p>Traditional feathers used in ceremonial dress and spiritual practices.</p>
                        <div class="product-price">$40.00</div>
                        <a href="/contact" class="btn" style="padding: 10px 20px; font-size: 1rem;">Inquire About Purchase</a>
                    </div>
                </div>
            </div>

            <div style="text-align: center; margin-top: 60px;">
                <p style="font-size: 1.1rem; margin-bottom: 20px; color: #666;">
                    Looking for something specific or need guidance on product selection?
                </p>
                <a href="/contact" class="btn">Contact Us for Guidance</a>
            </div>
        </div>
    </section>
    """
    
    template = get_base_template("Products", "products")
    return template.replace("{{% content %}}", content)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # Here you would typically save to database or send email
        flash('Mahalo for your message! We will contact you soon.', 'success')
        return redirect('/contact')
    
    # Get flash messages
    flash_html = ""
    messages = get_flashed_messages(with_categories=True)
    if messages:
        for category, message in messages:
            flash_html += f'<div class="flash flash-{category}">{message}</div>'
    
    content = f"""
    <!-- Contact Hero - FIXED: Full page -->
    <section class="hero-section" style="background: url('https://images.unsplash.com/photo-1516483638261-f4dbaf036963?ixlib=rb-4.0.3&auto=format&fit=crop&w=1350&q=80');">
        <div class="hero-bg"></div>
        <div class="hero-content">
            <h1 class="hero-title">Contact Us</h1>
            <p class="hero-subtitle">Connect with us for spiritual guidance and product inquiries</p>
        </div>
    </section>

    <!-- Contact Content -->
    <section class="section">
        <div class="container">
            <div class="products-grid">
                <!-- Contact Form -->
                <div class="product-card" style="grid-column: span 2;">
                    <div class="product-info">
                        <h2 style="color: #2c5530; margin-bottom: 30px;">Send Us a Message</h2>
                        <form method="POST" action="/contact">
                            <div class="form-group">
                                <label for="name">Your Name</label>
                                <input type="text" id="name" name="name" class="form-control" required>
                            </div>
                            <div class="form-group">
                                <label for="email">Your Email</label>
                                <input type="email" id="email" name="email" class="form-control" required>
                            </div>
                            <div class="form-group">
                                <label for="message">Your Message</label>
                                <textarea id="message" name="message" class="form-control" required></textarea>
                            </div>
                            <button type="submit" class="btn">Send Message</button>
                        </form>
                    </div>
                </div>
                
                <!-- Contact Info -->
                               <div class="product-card">
                    <div class="product-info">
                        <h2 style="color: #2c5530; margin-bottom: 30px;">Contact Information</h2>
                        <div style="margin-bottom: 20px;">
                            <h4 style="color: #2c5530; margin-bottom: 10px;"><i class="fas fa-envelope"></i> Email</h4>
                            <p>info@keaupuniakeakua.faith</p>
                        </div>
                        <div style="margin-bottom: 20px;">
                            <h4 style="color: #2c5530; margin-bottom: 10px;"><i class="fas fa-phone"></i> Phone</h4>
                            <p>(808) 123-4567</p>
                        </div>
                        <div style="margin-bottom: 20px;">
                            <h4 style="color: #2c5530; margin-bottom: 10px;"><i class="fas fa-map-marker-alt"></i> Location</h4>
                            <p>Hawaii</p>
                        </div>
                        <div>
                            <h4 style="color: #2c5530; margin-bottom: 10px;"><i class="fas fa-clock"></i> Response Time</h4>
                            <p>We typically respond within 24-48 hours</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Additional Contact Info -->
            <div style="text-align: center; margin-top: 50px;">
                <h3 style="color: #2c5530; margin-bottom: 20px;">Other Ways to Connect</h3>
                <div style="display: flex; justify-content: center; gap: 20px; margin-top: 30px;">
                    <a href="#" style="color: #2c5530; font-size: 24px;"><i class="fab fa-facebook"></i></a>
                    <a href="#" style="color: #2c5530; font-size: 24px;"><i class="fab fa-instagram"></i></a>
                    <a href="#" style="color: #2c5530; font-size: 24px;"><i class="fab fa-youtube"></i></a>
                </div>
            </div>
        </div>
    </section>
    """
    
    # Add flash messages to the template
    flash_script = ""
    if flash_html:
        flash_script = f"""
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const flashContainer = document.getElementById('flashMessages');
                flashContainer.innerHTML = `{flash_html}`;
                
                // Auto-remove flash messages after 5 seconds
                setTimeout(() => {{
                    flashContainer.style.opacity = '0';
                    flashContainer.style.transition = 'opacity 0.5s';
                    setTimeout(() => flashContainer.remove(), 500);
                }}, 5000);
            }});
        </script>
        """
    
    template = get_base_template("Contact", "contact")
    template = template.replace("{{% content %}}", content)
    
    # Insert flash script before closing body tag
    if flash_script:
        template = template.replace("</body>", flash_script + "</body>")
    
    return template

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def page_not_found(e):
    content = f"""
    <!-- 404 Hero -->
    <section class="hero-section" style="background: url('https://images.unsplash.com/photo-1519681393784-d120267933ba?ixlib=rb-4.0.3&auto=format&fit=crop&w=1350&q=80');">
        <div class="hero-bg"></div>
        <div class="hero-content">
            <h1 class="hero-title">Page Not Found</h1>
            <p class="hero-subtitle">The page you're looking for doesn't exist</p>
            <a href="/" class="btn">Return Home</a>
        </div>
    </section>
    
    <section class="section">
        <div class="container" style="text-align: center;">
            <p style="font-size: 1.2rem; margin-bottom: 30px;">
                The page you tried to access could not be found. It may have been moved or deleted.
            </p>
            <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
                <a href="/" class="btn">Home</a>
                <a href="/products" class="btn">Products</a>
                <a href="/about" class="btn">About</a>
                <a href="/contact" class="btn">Contact</a>
            </div>
        </div>
    </section>
    """
    
    template = get_base_template("Page Not Found", "home")
    return template.replace("{{% content %}}", content), 404

@app.errorhandler(500)
def internal_server_error(e):
    content = f"""
    <!-- 500 Hero -->
    <section class="hero-section" style="background: url('https://images.unsplash.com/photo-1519681393784-d120267933ba?ixlib=rb-4.0.3&auto=format&fit=crop&w=1350&q=80');">
        <div class="hero-bg"></div>
        <div class="hero-content">
            <h1 class="hero-title">Server Error</h1>
            <p class="hero-subtitle">Something went wrong on our end</p>
            <a href="/" class="btn">Return Home</a>
        </div>
    </section>
    
    <section class="section">
        <div class="container" style="text-align: center;">
            <p style="font-size: 1.2rem; margin-bottom: 30px;">
                We're experiencing technical difficulties. Please try again later.
            </p>
            <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
                <a href="/" class="btn">Home</a>
                <a href="/contact" class="btn">Contact Support</a>
            </div>
        </div>
    </section>
    """
    
    template = get_base_template("Server Error", "home")
    return template.replace("{{% content %}}", content), 500

# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
