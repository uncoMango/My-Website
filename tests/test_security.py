# tests/test_security.py
# =========================================================
# Focused tests for the Phase 2 security fixes:
#   - /kahu and content-write routes require a logged-in session
#   - unauthenticated writes are rejected without touching content
#   - website_content.json parses as valid JSON
#   - missing ADMIN_PASSWORD / PayPal env vars fail safely, not silently
#   - existing public pages still load
#
# These tests read the real local website_content.json (read-only) to
# confirm it parses, and confirm that a rejected write leaves it
# byte-for-byte unchanged. No test performs a successful authenticated
# write, so real site content is never modified by this suite.
# =========================================================

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import auth  # noqa: E402
import config  # noqa: E402
from blueprints import payments as payments_module  # noqa: E402
import app as app_module  # noqa: E402

TEST_PASSWORD = "test-only-password-not-real"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(auth, "ADMIN_PASSWORD", TEST_PASSWORD)
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


def _login(client, password=TEST_PASSWORD):
    return client.post("/kahu/login", data={"password": password}, follow_redirects=False)


# ---------------------------------------------------------------------------
# Unauthenticated access is denied
# ---------------------------------------------------------------------------

def test_kahu_denies_unauthenticated_access(client):
    resp = client.get("/kahu")
    assert resp.status_code in (302, 401, 403)
    if resp.status_code == 302:
        assert "/kahu/login" in resp.headers["Location"]


def test_admin_products_denies_unauthenticated_access(client):
    resp = client.get("/admin/products")
    assert resp.status_code in (302, 401, 403)


def test_admin_edit_page_denies_unauthenticated_get(client):
    resp = client.get("/admin/edit/home")
    assert resp.status_code in (302, 401, 403)


# ---------------------------------------------------------------------------
# Unauthorized POST/write requests are rejected AND leave content untouched
# ---------------------------------------------------------------------------

def test_unauthenticated_post_does_not_modify_content(client):
    before = (ROOT / "website_content.json").read_bytes()

    resp = client.post(
        "/admin/edit/home",
        data={"title": "HACKED BY TEST", "hero_image": "", "body_md": "pwned"},
        follow_redirects=False,
    )
    assert resp.status_code in (302, 401, 403)

    after = (ROOT / "website_content.json").read_bytes()
    assert before == after, "Unauthenticated POST must never modify website_content.json"


def test_unauthenticated_delete_page_is_rejected(client):
    before = (ROOT / "website_content.json").read_bytes()
    resp = client.post("/admin/delete-page/home", follow_redirects=False)
    assert resp.status_code in (302, 401, 403)
    after = (ROOT / "website_content.json").read_bytes()
    assert before == after


def test_unauthenticated_product_delete_is_rejected(client):
    before = (ROOT / "digital_products.json").read_bytes()
    resp = client.post("/admin/products/delete/prod_aloha_wellness", follow_redirects=False)
    assert resp.status_code in (302, 401, 403)
    after = (ROOT / "digital_products.json").read_bytes()
    assert before == after


def test_unauthenticated_product_add_is_rejected(client):
    resp = client.post("/admin/products/add", data={"name": "x", "price": "1"})
    assert resp.status_code in (302, 401, 403)


# ---------------------------------------------------------------------------
# Authenticated administrator access works
# ---------------------------------------------------------------------------

def test_login_with_correct_password_grants_session(client):
    resp = _login(client)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/kahu")

    resp2 = client.get("/kahu")
    assert resp2.status_code == 200
    assert b"Admin Panel" in resp2.data


def test_login_with_wrong_password_is_rejected(client):
    resp = _login(client, password="definitely-wrong")
    assert resp.status_code == 200  # re-renders login form
    assert b"Incorrect password" in resp.data

    resp2 = client.get("/kahu")
    assert resp2.status_code in (302, 401, 403)


def test_logout_clears_session(client):
    _login(client)
    assert client.get("/kahu").status_code == 200

    client.post("/kahu/logout")
    resp = client.get("/kahu")
    assert resp.status_code in (302, 401, 403)


def test_authenticated_admin_products_view_works(client):
    _login(client)
    resp = client.get("/admin/products")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# website_content.json is valid JSON
# ---------------------------------------------------------------------------

def test_website_content_json_is_valid():
    data = json.loads((ROOT / "website_content.json").read_text(encoding="utf-8"))
    assert "pages" in data
    assert "home" in data["pages"]


# ---------------------------------------------------------------------------
# Missing-secret behavior fails safely (does not silently allow access
# or crash the whole process)
# ---------------------------------------------------------------------------

def test_admin_configured_false_when_password_unset(monkeypatch):
    monkeypatch.setattr(auth, "ADMIN_PASSWORD", "")
    assert auth.admin_configured() is False
    assert auth.check_password("") is False
    assert auth.check_password("anything") is False


def test_login_503s_when_admin_password_unset(client, monkeypatch):
    monkeypatch.setattr(auth, "ADMIN_PASSWORD", "")
    resp = client.post("/kahu/login", data={"password": ""})
    assert resp.status_code == 503


def test_checkout_503s_when_paypal_credentials_unset(client, monkeypatch):
    monkeypatch.setattr(payments_module, "PAYPAL_CLIENT_ID", "")
    monkeypatch.setattr(payments_module, "PAYPAL_CLIENT_SECRET", "")
    resp = client.get("/checkout/prod_aloha_wellness")
    assert resp.status_code == 503


def test_checkout_works_when_paypal_credentials_present(client, monkeypatch):
    monkeypatch.setattr(payments_module, "PAYPAL_CLIENT_ID", "fake-client-id-for-test")
    monkeypatch.setattr(payments_module, "PAYPAL_CLIENT_SECRET", "fake-secret-for-test")
    resp = client.get("/checkout/prod_aloha_wellness")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Existing public pages remain accessible (auth changes did not break them)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path", [
    "/",
    "/kingdom_wealth",
    "/free_booklets",
    "/kingdom_keys",
    "/call_to_repentance",
    "/aloha_wellness",
    "/pastor_planners",
    "/nahenahe_voice",
    "/partner",
    "/product/prod_aloha_wellness",
])
def test_public_pages_still_load(client, path):
    resp = client.get(path)
    assert resp.status_code == 200, f"{path} returned {resp.status_code}"
