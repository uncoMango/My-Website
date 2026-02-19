# app.py
# =========================================================
# KE AUPUNI O KE AKUA - Main Application Entry Point
#
# This file just starts Flask and registers all blueprints.
# It should rarely need to be edited.
#
# To add a new section to the site:
#   1. Create blueprints/my_new_section.py
#   2. Import and register it below (copy the pattern)
#   Done.
# =========================================================

import os
from flask import Flask
from config import PRODUCTS_FOLDER
from content import load_content, save_content, DEFAULT_PAGES

# ----- Import all blueprints -----
from blueprints.pages import pages_bp
from blueprints.downloads import downloads_bp
from blueprints.products import products_bp
from blueprints.payments import payments_bp
from blueprints.admin import admin_bp

# ----- Create Flask app -----
app = Flask(__name__)

# ----- Register all blueprints -----
# Each blueprint handles its own group of routes.
# Order matters: more specific blueprints before the catch-all pages_bp.
app.register_blueprint(downloads_bp)
app.register_blueprint(products_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(pages_bp)   # ← catch-all last

# ----- Startup tasks -----
def initialize():
    """Create required folders and default data on first run."""
    PRODUCTS_FOLDER.mkdir(exist_ok=True)
    from config import DATA_FILE
    if not DATA_FILE.exists():
        save_content(DEFAULT_PAGES)
        print("✅ Created default website_content.json")

# ----- Run -----
if __name__ == "__main__":
    initialize()
    port = int(os.environ.get("PORT", 5000))
    print("🌺 Starting Ke Aupuni O Ke Akua website...")
    print(f"🌊 Visit: http://localhost:{port}")
    print("=" * 50)
    app.run(host="0.0.0.0", port=port, debug=True)
