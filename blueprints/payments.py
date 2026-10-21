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
import os
import base64
import smtplib
import urllib.error
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from email.mime.text import MIMEText

from flask import Blueprint, abort, make_response, redirect, render_template, request, url_for
from content import load_digital_products, save_digital_products, get_product_by_id
from download_tokens import generate_download_token
import sale_alerts
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
    STRIPE_FULFILLED_SESSIONS_FILE,
    PAYPAL_DISABLED_PRODUCT_IDS,
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

def _render_success_template(product, order_id, download_url):
    """Pure rendering, no side effects -- the caller is responsible for
    having already counted the sale and sent whatever confirmation
    emails are appropriate (see _render_payment_success for the single-
    caller PayPal path, and _fulfill_stripe_purchase for the idempotent,
    possibly-multi-caller Stripe path)."""
    if product.get("category") == "partnership":
        return render_template(
            "partner_success.html",
            product=product,
            order_id=order_id,
            logo_path=LOGO_PATH,
            logo_height=LOGO_HEIGHT,
            footer_text=FOOTER_TEXT,
        )
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


def _render_payment_success(product, order_id, buyer_email=""):
    """PayPal's own success path (single caller -- there is no PayPal
    webhook, so no idempotency concern here): mints one token, emails
    the buyer, and renders the page. Stripe no longer uses this function
    directly -- see _fulfill_stripe_purchase, which is idempotent across
    its two real callers (the browser and the webhook)."""
    if product.get("category") == "partnership":
        return _render_success_template(product, order_id, None)
    token = generate_download_token(product["id"], order_id)
    download_url = f"/download/product/{product['id']}/{token}" if token else None
    if download_url:
        # Hurricane Readiness work order (2026-08-21): the on-screen link
        # was the customer's only copy -- if they lost this tab or the
        # owner was genuinely unavailable to resend it by hand, a real,
        # already-paid customer had no self-service way to get what they
        # bought. This never blocks or delays rendering the success page.
        _send_customer_confirmation(buyer_email, product, download_url, order_id)
    return _render_success_template(product, order_id, download_url)


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


def _already_fulfilled(session_id):
    """True if this exact Stripe checkout session has already had its
    sale counted and its customer confirmation sent -- by either the
    webhook or the browser-facing /stripe/success route, whichever
    reached it first (Hurricane Readiness work order, 2026-08-21). Read
    fresh from disk every call, never cached in memory, so this stays
    correct across repeated webhook retries and separate requests."""
    try:
        with open(STRIPE_FULFILLED_SESSIONS_FILE, "r", encoding="utf-8") as f:
            return session_id in json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return False


def _mark_fulfilled(session_id):
    """Records that this session has now been fulfilled. Best-effort: if
    this write fails, the idempotency check simply becomes less
    effective for that one session -- never a fatal error, the same
    'never fail the payment flow' discipline every helper in this file
    already follows. Mirrors download_tokens.py's own
    _load_usage()/_save_usage() pattern, not a new persistence
    mechanism."""
    try:
        try:
            with open(STRIPE_FULFILLED_SESSIONS_FILE, "r", encoding="utf-8") as f:
                fulfilled = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            fulfilled = {}
        fulfilled[session_id] = datetime.now(timezone.utc).isoformat()
        with open(STRIPE_FULFILLED_SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(fulfilled, f)
    except Exception:
        pass


def _delivery_ready(product, download_url):
    """(True, "") when a buyer of this product can really get the file right now; otherwise (False, plain reason)."""
    if product.get("category") == "partnership":
        return True, ""
    if not download_url:
        return False, "the download signing secret is not set on the website"
    path = product.get("file_path") or ""
    if not path or not os.path.isfile(path) or os.path.getsize(path) == 0:
        return False, "the product file is missing on the website"
    return True, ""


def _verify_paypal_payment(order_id, product):
    """Ask PayPal itself whether this order was really paid, for this product's price.
    Returns (ok, reason, buyer_name, buyer_email). reason: "" | "not_found" | "not_paid" | "wrong_amount" | "unreachable".
    Before 2026-10-21 the success address trusted whatever order number it was given (any made-up number delivered the file)."""
    try:
        token = _get_paypal_token()
        order = _get_paypal_order(order_id, token)
    except urllib.error.HTTPError as exc:
        return False, ("not_found" if exc.code in (400, 404, 422) else "unreachable"), "", ""
    except Exception:
        return False, "unreachable", "", ""
    payer = order.get("payer", {})
    name = f"{payer.get('name', {}).get('given_name', '')} {payer.get('name', {}).get('surname', '')}".strip()
    email = payer.get("email_address", "")
    if order.get("status") != "COMPLETED":
        return False, "not_paid", name, email
    units = order.get("purchase_units") or [{}]
    captures = ((units[0].get("payments") or {}).get("captures")) or []
    if captures and any(c.get("status") != "COMPLETED" for c in captures):
        return False, "not_paid", name, email
    paid = (captures[0].get("amount") if captures else units[0].get("amount")) or {}
    try:
        right = abs(float(paid.get("value", -1)) - float(product["price"])) < 0.01 and paid.get("currency_code", "USD") == "USD"
    except (TypeError, ValueError):
        right = False
    if not right:
        return False, "wrong_amount", name, email
    return True, "", name, email


def _fulfill_stripe_purchase(product, session_id, buyer_name="", buyer_email=""):
    """The one real fulfillment action for a Stripe session Stripe itself
    has already confirmed paid (Hurricane Readiness work order,
    2026-08-21): counts the sale, notifies the admin, mints a signed
    download token, and emails it to the buyer. Called identically from
    /stripe/success (the immediate browser experience) and
    /stripe/webhook (Stripe's own guaranteed, retried, browser-
    independent delivery) for the same real session_id -- idempotent via
    _already_fulfilled()/_mark_fulfilled(), so whichever caller reaches
    it first does the real work, and every later call (a webhook retry,
    or the other caller reaching it afterward) safely re-mints a token
    to return without re-counting the sale or re-emailing. Returns the
    download_url (None for a partnership tier, which has none)."""
    already_done = _already_fulfilled(session_id)

    download_url = None
    if product.get("category") != "partnership":
        token = generate_download_token(product["id"], session_id)
        download_url = f"/download/product/{product['id']}/{token}" if token else None

    if already_done:
        return download_url

    ready, reason = _delivery_ready(product, download_url)
    sale_alerts.sale(product["name"], float(product["price"]), "Stripe", session_id, ready, reason)

    products_data = load_digital_products()
    for p in products_data["products"]:
        if p["id"] == product["id"]:
            p["downloads"] = p.get("downloads", 0) + 1
            p["total_sales"] = p.get("total_sales", 0) + float(product["price"])
    save_digital_products(products_data)

    _send_sale_notification(product["name"], float(product["price"]), session_id, buyer_name, buyer_email)
    if download_url:
        _send_customer_confirmation(buyer_email, product, download_url, session_id)

    _mark_fulfilled(session_id)
    return download_url


def _send_customer_confirmation(buyer_email, product, download_url, order_id):
    """Sends the buyer their own copy of the real, working download link
    (Hurricane Readiness work order, 2026-08-21) -- so a real purchase
    does not depend on the buyer keeping the one on-screen success-page
    tab open, or on Kahu Phil being reachable to resend it by hand if
    they lose it. Silently skipped if SMTP is not configured or the
    buyer's email could not be determined (PayPal/Stripe sometimes
    withhold it) -- never fails or delays the payment flow."""
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS and buyer_email):
        return
    try:
        msg = MIMEText(
            f"Mahalo for your purchase of {product['name']}!\n\n"
            f"Your download link:\n{SITE_DOMAIN}{download_url}\n\n"
            f"This link is valid for 14 days and up to 5 downloads. If you have any "
            f"trouble at all, contact {CONTACT_EMAIL} with the Order ID below and we "
            f"will make sure you get your file.\n\n"
            f"Order ID: {order_id}\n"
        )
        msg["Subject"] = f"Your download: {product['name']}"
        msg["From"] = SMTP_USER
        msg["To"] = buyer_email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [buyer_email], msg.as_string())
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
    # Hurricane Readiness work order (2026-08-21, temporary, reversible):
    # PayPal has no server-side webhook, so it is withheld at checkout
    # for products listed in PAYPAL_DISABLED_PRODUCT_IDS only -- PayPal
    # itself and every other product's PayPal path are untouched.
    paypal_enabled = product_id not in PAYPAL_DISABLED_PRODUCT_IDS
    if paypal_enabled and not (PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET):
        abort(503, "Payments are not configured on this server. Set PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET.")
    if not paypal_enabled and not STRIPE_ENABLED:
        abort(503, "No active payment method is currently configured for this product.")
    return render_template(
        "checkout.html",
        product=product,
        paypal_client_id=PAYPAL_CLIENT_ID,
        paypal_enabled=paypal_enabled,
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

    # Nothing is delivered, counted or announced until PayPal itself says this order was paid (2026-10-21).
    verified, reason, buyer_name, buyer_email = _verify_paypal_payment(order_id, product)
    if not verified:
        if reason == "unreachable":
            if sale_alerts.once("paypal-unreachable:" + order_id):
                sale_alerts.send("FIX NOW: PayPal buyer may not have the file",
                                 f"A buyer came back from PayPal but the website could not confirm the payment right now "
                                 f"(order ...{order_id[-8:]}, {product['name']}). Check PayPal and send the file by hand if it was paid.",
                                 urgent=True)
            return ("We could not confirm your PayPal payment this minute. Please do not pay again. "
                    f"Write to {CONTACT_EMAIL} with your PayPal receipt and we will send your file right away.", 503)
        if reason == "wrong_amount" and sale_alerts.once("paypal-amount:" + order_id):
            sale_alerts.send("Check PayPal: amount did not match", f"Order ...{order_id[-8:]} for {product['name']} was paid but not for the "
                             f"listed price. No file was delivered.", urgent=True)
        return ("Payment not completed.", 402)

    first_time = sale_alerts.once("paypal:" + order_id)
    if first_time:
        # Update sales tracking
        products_data = load_digital_products()
        for p in products_data["products"]:
            if p["id"] == product_id:
                p["downloads"] = p.get("downloads", 0) + 1
                p["total_sales"] = p.get("total_sales", 0) + float(product["price"])
        save_digital_products(products_data)

        _send_sale_notification(product["name"], float(product["price"]), order_id, buyer_name, buyer_email)
        token = generate_download_token(product["id"], order_id)
        url = f"/download/product/{product['id']}/{token}" if token else None
        ready, why = _delivery_ready(product, url)
        sale_alerts.sale(product["name"], float(product["price"]), "PayPal", order_id, ready, why)

    return _render_payment_success(product, order_id, buyer_email if first_time else "")


@payments_bp.route("/paypal/cancel")
def paypal_cancel():
    return redirect("/")


# =========================================================
# STRIPE ROUTES
# These routes exist but only work when STRIPE_ENABLED=True.
# =========================================================

def _card_payment_unavailable(product_id, exc):
    """Stripe refused (or could not be reached). Nothing was charged. Log exactly why (no secrets) so the owner can see the
    cause in Render's Logs, tell the buyer plainly, and point to PayPal. The category is also sent as a response header
    (X-Checkout-Problem) so a test can read the cause without opening the logs."""
    import re
    name = type(exc).__name__
    code = getattr(exc, "code", None)
    status = getattr(exc, "http_status", None)
    message = re.sub(r"(sk|rk|pk)_(live|test)_[A-Za-z0-9_.*]*", lambda m: m.group(1) + "_" + m.group(2) + "_...", str(exc))[:300]
    print(f"[stripe] create-session FAILED for {product_id}: {name} http={status} code={code} message={message}", flush=True)
    if "ermission" in name or (status == 403):
        category = "stripe_key_permission"
    elif status in (401,) or "uthentication" in name:
        category = "stripe_key_rejected"
    elif "InvalidRequest" in name:
        category = "stripe_rejected_request"
    elif "Connection" in name or "APIConnection" in name:
        category = "stripe_unreachable"
    else:
        category = "stripe_other"
    response = make_response(render_template("checkout_problem.html", product_id=product_id, contact_email=CONTACT_EMAIL), 502)
    response.headers["X-Checkout-Problem"] = category
    # Short, harmless tokens that say WHAT Stripe objected to (never the full message, never a key).
    for header, value in (("X-Checkout-Param", getattr(exc, "param", None)), ("X-Checkout-Code", code),
                          ("X-Checkout-Status", status)):
        text = re.sub(r"[^A-Za-z0-9_.\[\]-]", "", str(value or ""))[:80]
        if text:
            response.headers[header] = text
    return response


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

    # Stripe treats an empty value as "remove this key". Only keys that actually have a value are sent
    # (2026-10-20: the card button had answered "Internal Server Error" since attribution tags were added).
    metadata = {k: v for k, v in {
        "product_id": product_id,
        "attribution_source": request.cookies.get("rf_source", "direct")[:100],
        "attribution_medium": request.cookies.get("rf_medium", "")[:100],
        "attribution_campaign": request.cookies.get("rf_campaign", "")[:100],
        "attribution_bridge": request.cookies.get("rf_bridge", "")[:100],
        "attribution_content": request.cookies.get("rf_content", "")[:100],
    }.items() if v}

    try:
        session = stripe.checkout.Session.create(
            # No payment_method_types here (2026-10-20): Stripe refused the forced ["card"] on every product (HTTP 400, parameter
            # payment_method_types). Leaving it out lets Stripe offer the methods switched on in the owner's Stripe dashboard.
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
            metadata=metadata,
        )
    except Exception as exc:  # noqa: BLE001 - a visitor must never see a bare "Internal Server Error" at the till
        return _card_payment_unavailable(product_id, exc)
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

    # Fulfillment itself (Hurricane Readiness work order, 2026-08-21) is
    # idempotent and shared with stripe_webhook() below -- if the webhook
    # already reached this same session_id first (a real, plausible order
    # if the customer's browser is slow to redirect), this call simply
    # re-mints a fresh, valid token to show here without re-counting the
    # sale or re-emailing.
    customer_details = session.customer_details or {}
    buyer_name = getattr(customer_details, "name", None) or ""
    buyer_email = getattr(customer_details, "email", None) or ""
    download_url = _fulfill_stripe_purchase(product, session_id, buyer_name, buyer_email)

    return _render_success_template(product, session_id, download_url)


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
        # Only ever acts on Stripe's own independently-confirmed payment
        # status carried on the event itself -- never assumes a
        # checkout.session.completed event means paid without checking,
        # matching stripe_success()'s own payment_status guard above.
        if session.get("payment_status") == "paid":
            product_id = session.get("metadata", {}).get("product_id")
            if product_id:
                product = get_product_by_id(product_id)
                if product:
                    # Hurricane Readiness work order (2026-08-21): this is
                    # the browser-independent fulfillment path -- Stripe
                    # guarantees this webhook fires (with its own retries)
                    # regardless of whether the customer's browser ever
                    # reaches /stripe/success. _fulfill_stripe_purchase()
                    # is idempotent on session_id, so a Stripe retry of
                    # this exact event, or the browser reaching
                    # /stripe/success either before or after this webhook,
                    # can never double-count the sale or double-email the
                    # customer.
                    customer_details = session.get("customer_details") or {}
                    buyer_name = customer_details.get("name") or ""
                    buyer_email = customer_details.get("email") or ""
                    session_id = session.get("id", "")
                    _fulfill_stripe_purchase(product, session_id, buyer_name, buyer_email)

    return ("", 200)


# =========================================================
# HEALTH (no secrets): can a buyer pay and get the file? Read by the Foreman's daily check.
# =========================================================

@payments_bp.route("/health/sales")
def health_sales():
    from flask import jsonify
    products = []
    problems = []
    for p in load_digital_products()["products"]:
        if not p.get("active", True) or not p.get("file_path") or float(p.get("price", 0)) <= 0:
            continue
        path = p["file_path"]
        file_ok = os.path.isfile(path) and os.path.getsize(path) > 0
        products.append({"id": p["id"], "price": p["price"], "file_ok": file_ok})
        if not file_ok:
            problems.append(f"{p['id']}: product file missing")
    from download_tokens import DOWNLOAD_TOKEN_SECRET
    status = {
        "stripe_enabled": bool(STRIPE_ENABLED and STRIPE_SECRET_KEY),
        "paypal_ready": bool(PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET),
        "download_secret": bool(DOWNLOAD_TOKEN_SECRET),
        "sale_alerts_configured": sale_alerts.configured(),
        "sale_email_configured": bool(SMTP_HOST and SMTP_USER and SMTP_PASS),
        "products": products,
    }
    if not status["download_secret"]:
        problems.append("download signing secret is not set: buyers would get no file")
    if not status["paypal_ready"]:
        problems.append("PayPal is not configured")
    if not status["stripe_enabled"]:
        problems.append("Stripe card payments are off")
    if not status["sale_alerts_configured"]:
        problems.append("sale phone alerts are not set up (set SALE_ALERT_NTFY_TOPIC on Render)")
    status["problems"] = problems
    status["ok"] = not problems
    return jsonify(status)
