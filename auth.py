# auth.py
# =========================================================
# Session-based login gate for /kahu and all admin/content
# write routes. Shared by blueprints/admin.py and
# blueprints/products.py.
# =========================================================

import secrets
from functools import wraps
from flask import session, redirect, request

from config import ADMIN_PASSWORD

SESSION_KEY = "admin_authenticated"


def admin_configured():
    """True only if a real admin password has been set via environment variable."""
    return bool(ADMIN_PASSWORD)


def check_password(candidate):
    """Constant-time password check. Always False if no password is configured."""
    if not admin_configured():
        return False
    return secrets.compare_digest(candidate or "", ADMIN_PASSWORD)


def is_logged_in():
    return session.get(SESSION_KEY) is True


def require_admin(view_func):
    """Route decorator: redirects to /kahu/login unless the session is authenticated."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not is_logged_in():
            return redirect(f"/kahu/login?next={request.path}")
        return view_func(*args, **kwargs)
    return wrapped
