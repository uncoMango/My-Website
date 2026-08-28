# unsubscribe_tokens.py
# =========================================================
# Signed, non-expiring, email-bound unsubscribe tokens.
#
# CAN-SPAM requires a working one-or-two-click unsubscribe path that stays
# functional for at least 30 days after send. Mirrors download_tokens.py's
# and publishing_media_tokens.py's own established pattern exactly: reuses
# the one existing DOWNLOAD_TOKEN_SECRET with a distinct itsdangerous salt
# -- no second Render secret needed. Deliberately NOT time-limited (no
# max_age on load): an unsubscribe link must keep working well past 30
# days, so the simplest correct choice is a link that never expires.
# =========================================================

from itsdangerous import URLSafeSerializer, BadSignature

from config import DOWNLOAD_TOKEN_SECRET

_SALT = "unsubscribe"


def _serializer(secret=None):
    return URLSafeSerializer(secret if secret is not None else DOWNLOAD_TOKEN_SECRET, salt=_SALT)


def generate_unsubscribe_token(email):
    """Mint a signed, non-expiring token binding one subscriber email.
    Returns None if DOWNLOAD_TOKEN_SECRET is not configured -- callers
    must handle that (fail closed: no usable link is ever minted, rather
    than one signed with an empty/guessable secret)."""
    if not DOWNLOAD_TOKEN_SECRET:
        return None
    return _serializer().dumps({"email": email})


def resolve_unsubscribe_token(token):
    """Returns (email, None) on a valid token, or (None, reason) where
    reason is one of: "not_configured", "invalid". Callers should map
    every failure to the same generic response -- the reason is for
    logs/tests, not for telling a requester which part was wrong."""
    if not DOWNLOAD_TOKEN_SECRET:
        return None, "not_configured"
    try:
        payload = _serializer().loads(token)
    except BadSignature:
        return None, "invalid"
    email = payload.get("email")
    if not email:
        return None, "invalid"
    return email, None
