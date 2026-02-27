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
EMAILS_FILE = BASE / "email_subscribers.json"

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
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]

# ----- PAYPAL -----
# Live credentials (already active)
PAYPAL_CLIENT_ID = os.environ["PAYPAL_CLIENT_ID"]
PAYPAL_CLIENT_SECRET = os.environ["PAYPAL_CLIENT_SECRET"]
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
SMTP_HOST = os.environ["SMTP_HOST"]
SMTP_PORT = int(os.environ["SMTP_PORT"])
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASS = os.environ["SMTP_PASS"]
NOTIFY_EMAIL = "kahuphil@keaupuni.faith"

# ----- SITE INFO -----
SITE_NAME = "Ke Aupuni O Ke Akua"
SITE_DOMAIN = "https://keaupuniakeakua.faith"
CONTACT_EMAIL = "kahuphil@keaupuni.faith"
LOGO_PATH = "/static/images/output-onlinepngtools.png"
LOGO_HEIGHT = "180px"
FOOTER_TEXT = "© 2025 Ke Aupuni O Ke Akua. All rights reserved. Made with aloha in Hawaiʻi."
