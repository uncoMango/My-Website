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
def preserve_owned_discovery_attribution(response):
    """Keep bounded, non-sensitive discovery identity through checkout.

    GA4 reads the standard UTM values on arrival. These first-party cookies
    preserve the same campaign identity for downstream Stripe reconciliation
    without creating a second analytics store. Only explicitly governed owned
    sources are accepted; arbitrary query-string values never become durable
    attribution.
    """
    verification_flag = request.args.get("rf_verify", "").lower()
    if verification_flag == "1":
        response.set_cookie(
            "rf_verification", "1", max_age=60 * 60 * 24 * 90,
            secure=bool(os.environ.get("RENDER")), httponly=True,
            samesite="Lax",
        )
    elif verification_flag == "0":
        response.delete_cookie("rf_verification")

    source = request.args.get("utm_source", "").lower()
    if source in {"pinterest", "youtube"}:
        defaults = {
            "pinterest": ("organic", "pinterest_fence_line", "feed", "unknown"),
            "youtube": ("organic_video", "unknown", "related_video", "unknown"),
        }
        medium, campaign, bridge, content = defaults[source]
        values = {
            "rf_source": source,
            "rf_medium": request.args.get("utm_medium", medium)[:100],
            "rf_campaign": request.args.get("utm_campaign", campaign)[:100],
            "rf_bridge": request.args.get("utm_term", bridge)[:100],
            "rf_content": request.args.get("utm_content", content)[:100],
        }
        for name, value in values.items():
            response.set_cookie(
                name, value, max_age=60 * 60 * 24 * 90,
                secure=bool(os.environ.get("RENDER")), httponly=True,
                samesite="Lax",
            )
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
