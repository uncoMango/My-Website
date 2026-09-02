# app.py
import os
from flask import Flask, request
from config import PRODUCTS_FOLDER, DATA_FILE, FLASK_SECRET_KEY
from content import load_content, save_content, DEFAULT_PAGES

from blueprints.pages import pages_bp
from blueprints.downloads import downloads_bp
from blueprints.products import products_bp
from blueprints.payments import payments_bp
from blueprints.admin import admin_bp
from blueprints.publishing_media import publishing_media_bp
from blueprints.pinterest import pinterest_bp
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
app.register_blueprint(publishing_media_bp)
app.register_blueprint(pinterest_bp)
app.register_blueprint(pages_bp)


@app.after_request
def preserve_pinterest_attribution(response):
    """Keep non-sensitive Pinterest campaign identity through checkout.

    These cookies carry no authentication or entitlement and are bounded to
    the known Pinterest source. They let Stripe metadata and GA purchase
    events reconcile a real downstream action without a competing analytics
    store.
    """
    if request.args.get("utm_source", "").lower() == "pinterest":
        values = {
            "rf_source": "pinterest",
            "rf_campaign": request.args.get("utm_campaign", "pinterest_fence_line")[:100],
            "rf_content": request.args.get("utm_content", "unknown")[:100],
        }
        for name, value in values.items():
            response.set_cookie(name, value, max_age=60 * 60 * 24 * 90, secure=bool(os.environ.get("RENDER")), httponly=True, samesite="Lax")
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
