# config.py
# =========================================================
# ALL SETTINGS FOR KE AUPUNI O KE AKUA WEBSITE
# Edit this file to change passwords, API keys, and paths.
# =========================================================

from pathlib import Path

# ----- PATHS -----
BASE = Path(__file__).parent
DATA_FILE = BASE / "website_content.json"
PRODUCTS_FILE = BASE / "digital_products.json"
PRODUCTS_FOLDER = BASE / "digital_products"

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
]

# ----- ADMIN -----
ADMIN_PASSWORD = "Kingdom2024"

# ----- PAYPAL -----
# Live credentials (already active)
PAYPAL_CLIENT_ID = "Af3hvjHUPRVuFeQ8xO_T18V234j-B-qvN9I9ydlWnEU9M0vKKOVyMw0si6r-N47Y_fg-Mw35VvAifkZ6"
PAYPAL_CLIENT_SECRET = "ECBlGV46JMgXmIk2H9u_i-kyMUO1X5--GYkjqYlqf2QMv4LbrWFhUNwd3rzCswN1-UfrwbPrk5WIUPHQ"
PAYPAL_BASE_URL = "https://api-m.paypal.com"
PAYPAL_RETURN_URL = "https://keaupuniakeakua.faith/paypal/success"
PAYPAL_CANCEL_URL = "https://keaupuniakeakua.faith/paypal/cancel"

# ----- STRIPE -----
# Sign up at https://stripe.com then paste your keys here.
# Get them from: Stripe Dashboard > Developers > API Keys
STRIPE_PUBLISHABLE_KEY = "pk_live_REPLACE_WITH_YOUR_STRIPE_PUBLISHABLE_KEY"
STRIPE_SECRET_KEY = "sk_live_REPLACE_WITH_YOUR_STRIPE_SECRET_KEY"
STRIPE_WEBHOOK_SECRET = "whsec_REPLACE_WITH_YOUR_STRIPE_WEBHOOK_SECRET"
# Set STRIPE_ENABLED = True once you have your keys
STRIPE_ENABLED = False

# ----- EMAIL / KIT.COM -----
KIT_FORM_URL = "https://app.kit.com/forms/8979853/subscriptions"

# ----- SITE INFO -----
SITE_NAME = "Ke Aupuni O Ke Akua"
SITE_DOMAIN = "https://keaupuniakeakua.faith"
CONTACT_EMAIL = "kahuphil@keaupuni.faith"
LOGO_PATH = "/static/images/output-onlinepngtools.png"
LOGO_HEIGHT = "180px"
FOOTER_TEXT = "© 2025 Ke Aupuni O Ke Akua. All rights reserved. Made with aloha in Hawaiʻi."
