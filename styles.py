# styles.py
# =========================================================
# Shared CSS for all public-facing pages.
# Kept here so it's easy to update site-wide appearance.
# =========================================================

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
    font-family: 'Noto Sans', 'Arial', 'Helvetica', sans-serif;
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
    font-family: 'Noto Sans', 'Arial', 'Helvetica', sans-serif;
    text-shadow: 2px 2px 6px rgba(0,0,0,1);
    border-radius: 6px;
    transition: all 0.3s ease;
}

.nav-menu a:hover {
    background: var(--accent-teal) !important;
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

.hero h1 { display: none; }

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

.gallery-item img { width: 100%; height: auto; display: block; }

.footer {
    text-align: center;
    padding: 2rem;
    color: white;
    background: none;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    margin-top: 2rem;
}

/* ---- RESPONSIVE ---- */
@media (max-width: 768px) {
    .hamburger { display: flex; }

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

    .nav-menu.active { display: flex; }

    .nav-menu a {
        background: transparent !important;
        padding: 1rem 2rem;
        border-radius: 0;
    }

    .nav-container { padding: 0 1rem; }

    .hero { height: 45vh; min-height: 300px; }

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

    .content-card h2 { font-size: 1.8rem; }
    .content-card h3 { font-size: 1.4rem; }

    .music-buttons { flex-direction: column; }
    .music-button { width: 100%; }

    .content-card img[alt*="Cover"],
    .content-card img[alt*="Volume"] { max-width: 100%; }

    .gallery-grid { grid-template-columns: 1fr; }
}
"""

# Admin panel CSS (used by admin blueprint)
ADMIN_STYLE = """
* { margin: 0; padding: 0; box-sizing: border-box; }
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
h1 { color: #2c3e50; margin-bottom: 0.5rem; font-size: 2rem; }
.subtitle { color: #7f8c8d; margin-bottom: 2rem; }
.btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
    display: inline-block;
}
.btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102,126,234,0.4); }
.btn-secondary { background: #6c757d; color: white; }
.btn-secondary:hover { background: #5a6268; }
.btn-success { background: #28a745; color: white; }
.btn-danger { background: #dc3545; color: white; }
.btn-sm { padding: 0.5rem 1rem; font-size: 0.875rem; }
.form-group { margin-bottom: 1.5rem; }
.form-group label { display: block; color: #2c3e50; font-weight: 600; margin-bottom: 0.5rem; }
.form-group input, .form-group textarea, .form-group select {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    font-size: 1rem;
    font-family: inherit;
    transition: border-color 0.3s ease;
}
.form-group input:focus, .form-group textarea:focus, .form-group select:focus {
    outline: none;
    border-color: #667eea;
}
.form-group textarea { min-height: 200px; resize: vertical; }
.help-text { font-size: 0.85rem; color: #6c757d; margin-top: 0.25rem; }
"""
