# blueprints/payments.py
# =========================================================
# Payment processing: PayPal (active) + Stripe (ready).
#
# TO ACTIVATE STRIPE:
#   1. Get your keys from stripe.com > Developers > API Keys
#   2. Paste them into config.py
#   3. Set STRIPE_ENABLED = True in config.py
#   That's it - the Stripe button will appear automatically.
# =========================================================

import json
import base64
import smtplib
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from email.mime.text import MIMEText

from flask import Blueprint, abort, redirect, render_template, request, url_for
from content import load_digital_products, save_digital_products, get_product_by_id
from download_tokens import generate_download_token
from config import (
    PAYPAL_CLIENT_ID,
    PAYPAL_CLIENT_SECRET,
    PAYPAL_BASE_URL,
    PAYPAL_RETURN_URL,
    PAYPAL_CANCEL_URL,
    STRIPE_PUBLISHABLE_KEY,
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
    STRIPE_ENABLED,
    LOGO_PATH,
    LOGO_HEIGHT,
    FOOTER_TEXT,
    SITE_DOMAIN,
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASS,
    NOTIFY_EMAIL,
    CONTACT_EMAIL,
)

payments_bp = Blueprint("payments", __name__)


# =========================================================
# SUCCESS PAGE HELPER
# Partnership tiers have no digital file to deliver, so they get
# a dedicated thank-you template instead of the "your download is
# ready" page used for real digital products.
# =========================================================

def _render_payment_success(product, order_id):
    if product.get("category") == "partnership":
        return render_template(
            "partner_success.html",
            product=product,
            order_id=order_id,
            logo_path=LOGO_PATH,
            logo_height=LOGO_HEIGHT,
            footer_text=FOOTER_TEXT,
        )
    token = generate_download_token(product["id"], order_id)
    download_url = f"/download/product/{product['id']}/{token}" if token else None
    return render_template(
        "payment_success.html",
        product=product,
        order_id=order_id,
        download_url=download_url,
        contact_email=CONTACT_EMAIL,
        logo_path=LOGO_PATH,
        logo_height=LOGO_HEIGHT,
        footer_text=FOOTER_TEXT,
    )


# =========================================================
# EMAIL NOTIFICATION HELPER
# =========================================================

def _send_sale_notification(product_name, amount, order_id, buyer_name="", buyer_email=""):
    """Send a sale notification email to the admin. Silently skipped if SMTP is not configured."""
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
        return
    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        msg = MIMEText(
            f"New sale received!\n\n"
            f"Buyer Name:  {buyer_name or '(not available)'}\n"
            f"Buyer Email: {buyer_email or '(not available)'}\n"
            f"Product:     {product_name}\n"
            f"Amount:      ${amount:.2f}\n"
            f"Order ID:    {order_id}\n"
            f"Date/Time:   {now}\n"
        )
        msg["Subject"] = f"Sale: {product_name} — ${amount:.2f}"
        msg["From"] = SMTP_USER
        msg["To"] = NOTIFY_EMAIL
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [NOTIFY_EMAIL], msg.as_string())
    except Exception:
        pass  # Never fail the payment flow due to email errors


# =========================================================
# CHECKOUT PAGE
# Shows PayPal button (always) and Stripe button (if enabled)
# =========================================================

@payments_bp.route("/checkout/<product_id>")
def checkout_page(product_id):
    product = get_product_by_id(product_id)
    if not product or not product.get("active", True):
        abort(404)
    if not (PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET):
        abort(503, "Payments are not configured on this server. Set PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET.")
    return render_template(
        "checkout.html",
        product=product,
        paypal_client_id=PAYPAL_CLIENT_ID,
        stripe_enabled=STRIPE_ENABLED,
        stripe_publishable_key=STRIPE_PUBLISHABLE_KEY if STRIPE_ENABLED else "",
        logo_path=LOGO_PATH,
        logo_height=LOGO_HEIGHT,
        footer_text=FOOTER_TEXT,
    )


# =========================================================
# PAYPAL HELPERS
# =========================================================

def _get_paypal_token():
    """Exchange client ID + secret for a PayPal access token."""
    credentials = f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
    req = urllib.request.Request(
        f"{PAYPAL_BASE_URL}/v1/oauth2/token",
        data=data,
        headers={
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())["access_token"]


def _get_paypal_order(order_id, token):
    """Retrieve a PayPal order to obtain payer name and email."""
    req = urllib.request.Request(
        f"{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


# =========================================================
# PAYPAL SUCCESS
# Called after customer approves payment in PayPal popup.
# =========================================================

@payments_bp.route("/paypal/success")
def paypal_success():
    order_id = request.args.get("orderID")
    product_id = request.args.get("product_id")

    if not order_id or not product_id:
        abort(400)

    product = get_product_by_id(product_id)
    if not product:
        abort(404)

    # Update sales tracking
    products_data = load_digital_products()
    for p in products_data["products"]:
        if p["id"] == product_id:
            p["downloads"] = p.get("downloads", 0) + 1
            p["total_sales"] = p.get("total_sales", 0) + float(product["price"])
    save_digital_products(products_data)

    # Retrieve buyer info from PayPal order details
    buyer_name = ""
    buyer_email = ""
    try:
        token = _get_paypal_token()
        order_details = _get_paypal_order(order_id, token)
        payer = order_details.get("payer", {})
        given = payer.get("name", {}).get("given_name", "")
        surname = payer.get("name", {}).get("surname", "")
        buyer_name = f"{given} {surname}".strip()
        buyer_email = payer.get("email_address", "")
    except Exception:
        pass

    _send_sale_notification(product["name"], float(product["price"]), order_id, buyer_name, buyer_email)

    return _render_payment_success(product, order_id)


@payments_bp.route("/paypal/cancel")
def paypal_cancel():
    return redirect("/")


# =========================================================
# STRIPE ROUTES
# These routes exist but only work when STRIPE_ENABLED=True.
# =========================================================

@payments_bp.route("/stripe/create-session/<product_id>", methods=["POST"])
def stripe_create_session(product_id):
    if not STRIPE_ENABLED:
        abort(404)

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY
    except ImportError:
        abort(500, "Stripe library not installed. Run: pip install stripe")

    product = get_product_by_id(product_id)
    if not product or not product.get("active", True):
        abort(404)

    price_cents = int(float(product["price"]) * 100)

    # Stripe requires product_data.images to be fully-qualified (http/https)
    # URLs; it rejects relative paths like "/static/covers/foo.jpg" with a
    # 400 InvalidRequestError, which surfaces to the buyer as a 500.
    cover_image = product.get("cover_image", "")
    if cover_image and not cover_image.startswith(("http://", "https://")):
        cover_image = f"{SITE_DOMAIN}{cover_image}"

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": product["name"],
                    "images": [cover_image] if cover_image else [],
                },
                "unit_amount": price_cents,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=f"{SITE_DOMAIN}/stripe/success?session_id={{CHECKOUT_SESSION_ID}}&product_id={product_id}",
        cancel_url=f"{SITE_DOMAIN}/product/{product_id}?cancelled=true",
        metadata={"product_id": product_id},
    )
    return redirect(session.url, code=303)


@payments_bp.route("/stripe/success")
def stripe_success():
    if not STRIPE_ENABLED:
        abort(404)

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY
    except ImportError:
        abort(500)

    session_id = request.args.get("session_id")
    product_id = request.args.get("product_id")

    if not session_id or not product_id:
        abort(400)

    session = stripe.checkout.Session.retrieve(session_id)
    if session.payment_status != "paid":
        return ("Payment not completed.", 402)

    product = get_product_by_id(product_id)
    if not product:
        abort(404)

    products_data = load_digital_products()
    for p in products_data["products"]:
        if p["id"] == product_id:
            p["downloads"] = p.get("downloads", 0) + 1
            p["total_sales"] = p.get("total_sales", 0) + float(product["price"])
    save_digital_products(products_data)

    customer_details = session.customer_details or {}
    buyer_name = getattr(customer_details, "name", None) or ""
    buyer_email = getattr(customer_details, "email", None) or ""
    _send_sale_notification(product["name"], float(product["price"]), session_id, buyer_name, buyer_email)

    return _render_payment_success(product, session_id)


@payments_bp.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    if not STRIPE_ENABLED:
        abort(404)

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY
    except ImportError:
        abort(500)

    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception:
        abort(400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        product_id = session.get("metadata", {}).get("product_id")
        if product_id:
            product = get_product_by_id(product_id)
            if product:
                products_data = load_digital_products()
                for p in products_data["products"]:
                    if p["id"] == product_id:
                        p["downloads"] = p.get("downloads", 0) + 1
                        p["total_sales"] = p.get("total_sales", 0) + float(product["price"])
                save_digital_products(products_data)
                customer_details = session.get("customer_details") or {}
                buyer_name = customer_details.get("name") or ""
                buyer_email = customer_details.get("email") or ""
                _send_sale_notification(
                    product["name"], float(product["price"]), session.get("id", ""),
                    buyer_name, buyer_email,
                )

    return ("", 200)
