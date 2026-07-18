# app.py
import os
from flask import Flask
from config import PRODUCTS_FOLDER, DATA_FILE, FLASK_SECRET_KEY
from content import load_content, save_content, DEFAULT_PAGES

from blueprints.pages import pages_bp
from blueprints.downloads import downloads_bp
from blueprints.products import products_bp
from blueprints.payments import payments_bp
from blueprints.admin import admin_bp
from limiter import limiter

app = Flask(__name__)
limiter.init_app(app)

# Session cookie used only for /kahu admin login. If FLASK_SECRET_KEY is not
# set, Flask falls back to a random key generated at process start — sessions
# still work, but won't survive a restart/redeploy, so admins would just be
# logged out rather than the site being left insecure.
app.secret_key = FLASK_SECRET_KEY or os.urandom(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    # Render sets RENDER=true for deployed services; only require HTTPS-only
    # cookies there so local `flask run` (plain http) can still log in.
    SESSION_COOKIE_SECURE=bool(os.environ.get("RENDER")),
)

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
