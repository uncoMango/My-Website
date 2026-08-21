# download_tokens.py
# =========================================================
# Signed, time-limited, product-bound download tokens.
#
# A token is minted once, right after a verified PayPal/Stripe payment
# (see blueprints/payments.py:_render_payment_success), and is required
# to hit /download/product/<product_id>/<token> in blueprints/products.py.
# Without a valid token, the file is never served — see config.py for
# the DOWNLOAD_TOKEN_SECRET this depends on.
# =========================================================

import json
import uuid

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from config import DOWNLOAD_TOKEN_SECRET, DOWNLOAD_TOKEN_USAGE_FILE

TOKEN_MAX_AGE_SECONDS = 14 * 24 * 60 * 60  # 14 days (Hurricane Readiness work order, 2026-08-21:
# the owner may be genuinely unavailable for several days at a time; a
# 72-hour window left a real customer with no self-service way to
# re-access a real purchase if they lost the link during that absence)
MAX_USES = 5
_SALT = "product-download"


def _serializer(secret=None):
    return URLSafeTimedSerializer(secret if secret is not None else DOWNLOAD_TOKEN_SECRET, salt=_SALT)


def generate_download_token(product_id, order_id):
    """Mint a signed token for one product/order. Returns None if
    DOWNLOAD_TOKEN_SECRET is not configured — callers must handle that
    (fail closed: no usable download link, not a broken/unsigned one)."""
    if not DOWNLOAD_TOKEN_SECRET:
        return None
    payload = {"pid": product_id, "oid": order_id, "jti": uuid.uuid4().hex}
    return _serializer().dumps(payload)


def _load_usage():
    if DOWNLOAD_TOKEN_USAGE_FILE.exists():
        try:
            with open(DOWNLOAD_TOKEN_USAGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_usage(usage):
    with open(DOWNLOAD_TOKEN_USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(usage, f)


def validate_and_consume_token(product_id, token):
    """Validate a token for product_id and, if valid, record one use.

    Returns (True, None) on success, or (False, reason) where reason is
    one of: "not_configured", "expired", "invalid", "wrong_product",
    "limit_exceeded". Callers should map every failure to the same
    generic HTTP response (403) — the reason is for logs/tests, not for
    telling a requester which part of their forged token was wrong.
    """
    if not DOWNLOAD_TOKEN_SECRET:
        return False, "not_configured"

    try:
        payload = _serializer().loads(token, max_age=TOKEN_MAX_AGE_SECONDS)
    except SignatureExpired:
        return False, "expired"
    except BadSignature:
        return False, "invalid"

    if payload.get("pid") != product_id:
        return False, "wrong_product"

    jti = payload.get("jti")
    if not jti:
        return False, "invalid"

    usage = _load_usage()
    uses = usage.get(jti, 0)
    if uses >= MAX_USES:
        return False, "limit_exceeded"

    usage[jti] = uses + 1
    _save_usage(usage)
    return True, None
