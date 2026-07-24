# config.py
# =========================================================
# ALL SETTINGS FOR KE AUPUNI O KE AKUA WEBSITE
# Edit this file to change passwords, API keys, and paths.
# =========================================================

import os
from pathlib import Path

# ----- PATHS -----
BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"
PRODUCTS_FILE = BASE / "digital_products.json"
PRODUCTS_FOLDER = BASE / "digital_products"
DOWNLOAD_TOKEN_USAGE_FILE = BASE / "download_token_usage.json"
EMAILS_FILE = BASE / "email_subscribers.json"
SUBSCRIBERS_FILE = BASE / "data" / "subscribers.json"

# ----- PAGE ORDER (controls nav menu order) -----
ORDER = [
    "home",
    "kingdom_wealth",
    "free_booklets",
    "kingdom_keys",
    "call_to_repentance",
    "aloha_wellness",
    "pastor_planners",
    "nahenahe_voice",
    "partner",
]

# ----- ADMIN -----
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

# ----- DOWNLOAD TOKENS -----
# Signs the time-limited, product-bound tokens minted after a verified
# PayPal/Stripe payment (see download_tokens.py). Deliberately separate
# from FLASK_SECRET_KEY so rotating one never invalidates the other.
# If unset, /download/product/<id>/<token> fails closed (403) rather
# than falling back to an unsigned or shared secret.
DOWNLOAD_TOKEN_SECRET = os.environ.get("DOWNLOAD_TOKEN_SECRET", "")

# ----- SESSIONS -----
# Signs the admin login session cookie. Required for /kahu auth to work.
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "")

# ----- PAYPAL -----
# Live credentials (already active)
PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = os.environ.get("PAYPAL_CLIENT_SECRET", "")
PAYPAL_BASE_URL = "https://api-m.paypal.com"
PAYPAL_RETURN_URL = "https://keaupuniakeakua.faith/paypal/success"
PAYPAL_CANCEL_URL = "https://keaupuniakeakua.faith/paypal/cancel"

# ----- STRIPE -----
# Sign up at https://stripe.com then paste your keys here.
# Get them from: Stripe Dashboard > Developers > API Keys
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_ENABLED = os.environ.get("STRIPE_ENABLED", "false").lower() == "true"

# ----- EMAIL / KIT.COM -----
KIT_FORM_URL = "https://app.kit.com/forms/8979853/subscriptions"

# ----- SMTP (for subscriber notifications) -----
# Optional — email notifications are skipped if these are not set.
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
NOTIFY_EMAIL = "kahuphil@keaupuni.faith"

# ----- SITE INFO -----
SITE_NAME = "Ke Aupuni O Ke Akua"
SITE_DOMAIN = "https://keaupuniakeakua.faith"
CONTACT_EMAIL = "kahuphil@keaupuni.faith"
LOGO_PATH = "/static/images/output-onlinepngtools.png"
# Actual displayed size is set responsively by .site-logo in
# templates/partials/styles.css (210px desktop / 140px / 110px / 90px at
# narrower breakpoints), not by this value -- kept here as the documented
# desktop reference size only.
LOGO_HEIGHT = "210px"
FOOTER_TEXT = "© 2025 Ke Aupuni O Ke Akua. All rights reserved. Made with aloha in Hawaiʻi."
