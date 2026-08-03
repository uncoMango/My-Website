# publishing_media_tokens.py
# =========================================================
# Signed, time-limited, asset-bound tokens for the Discovery
# Workforce's publishing-media bridge.
#
# Same pattern as download_tokens.py (itsdangerous.URLSafeTimedSerializer,
# fail-closed if the secret is unset), reusing DOWNLOAD_TOKEN_SECRET with a
# distinct salt so the two token families can never be swapped for one
# another, without requiring a second Render secret. A token authorizes
# GET /publishing-media/<asset_id>/<token> in
# blueprints/publishing_media.py — see that file and publish_media.py.
# =========================================================

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from config import DOWNLOAD_TOKEN_SECRET

# Long enough for Buffer (and whatever platform Buffer hands the URL to —
# YouTube/Facebook) to fetch the asset even with real-world delay, short
# enough that a leaked URL doesn't stay valid indefinitely.
TOKEN_MAX_AGE_SECONDS = 14 * 24 * 60 * 60  # 14 days
_SALT = "publishing-media"


def _serializer(secret=None):
    return URLSafeTimedSerializer(secret if secret is not None else DOWNLOAD_TOKEN_SECRET, salt=_SALT)


def generate_publishing_media_token(asset_id):
    """Mint a signed token for one asset_id. Returns None if
    DOWNLOAD_TOKEN_SECRET is not configured — callers must handle that
    (fail closed: no usable media link, not an unsigned one)."""
    if not DOWNLOAD_TOKEN_SECRET:
        return None
    return _serializer().dumps({"aid": asset_id})


def validate_publishing_media_token(asset_id, token):
    """Validate a token for asset_id.

    Returns (True, None) on success, or (False, reason) where reason is
    one of: "not_configured", "expired", "invalid", "wrong_asset".
    Callers should map every failure to the same generic HTTP response
    (403) except "not_configured" (503) — same convention as
    download_tokens.validate_and_consume_token.
    """
    if not DOWNLOAD_TOKEN_SECRET:
        return False, "not_configured"

    try:
        payload = _serializer().loads(token, max_age=TOKEN_MAX_AGE_SECONDS)
    except SignatureExpired:
        return False, "expired"
    except BadSignature:
        return False, "invalid"

    if payload.get("aid") != asset_id:
        return False, "wrong_asset"

    return True, None
