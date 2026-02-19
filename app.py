# app.py
import os
from flask import Flask
from config import PRODUCTS_FOLDER, DATA_FILE
from content import load_content, save_content, DEFAULT_PAGES

from blueprints.pages import pages_bp
from blueprints.downloads import downloads_bp
from blueprints.products import products_bp
from blueprints.payments import payments_bp
from blueprints.admin import admin_bp

app = Flask(__name__)

# Initialize on startup (works with gunicorn too)
PRODUCTS_FOLDER.mkdir(exist_ok=True)
if not DATA_FILE.exists():
    save_content(DEFAULT_PAGES)

app.register_blueprint(downloads_bp)
app.register_blueprint(products_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(pages_bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
