# tests/test_package_and_shelf.py
# =========================================================
# The Rotten Fencepost Package (2026-10-23): the free Introduction page, the $47 package page, the buyer's private
# shelf, and the locked door the Foreman uses to add things to every shelf.
# Nothing here reaches Stripe, PayPal, a mail server, Google Sheets or a phone: all are faked.
# =========================================================
import io
import json
import re
import smtplib
import sys
import types
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import app as app_module  # noqa: E402
import config  # noqa: E402
import download_tokens  # noqa: E402
import shelf  # noqa: E402
from blueprints import downloads as downloads_module  # noqa: E402
from blueprints import payments as payments_module  # noqa: E402

SECRET = "test-only-download-secret-not-real"
KEY = "test-only-shelf-admin-key"
PACKAGE = "prod_wyk_package"


@pytest.fixture
def client():
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def secrets(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "DOWNLOAD_TOKEN_SECRET", SECRET)
    monkeypatch.setattr(download_tokens, "DOWNLOAD_TOKEN_SECRET", SECRET)
    monkeypatch.setattr(download_tokens, "DOWNLOAD_TOKEN_USAGE_FILE", tmp_path / "usage.json")
    monkeypatch.setattr(config, "SHELF_ADMIN_KEY", KEY)
    # the unlimited-in-tests rate limiter
    app_module.limiter.enabled = False


def _text(html):
    import html as htmllib
    html = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", html)
    return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", html)))


def _shelf_url(order="order-1"):
    return shelf.shelf_path(order)


def _auth(extra=None):
    return dict({"Authorization": "Bearer " + KEY}, **(extra or {}))


# ----------------------------------------------------------------- the package page
def test_package_page_uses_the_wording_exactly_and_hides_notes(client):
    html = client.get("/what-your-body-forgot").get_data(as_text=True)
    text = _text(html)
    source = (ROOT / "content_text" / "what_your_body_forgot.md").read_text(encoding="utf-8")
    for line in source.splitlines():
        plain = re.sub(r"[*#]|\[|\]\(.*?\)|^\d+\.\s", "", line).strip()
        if plain and plain != "@@BUY_BUTTON@@":
            assert plain in text, f"missing from the page: {plain!r}"
    assert "[" not in text and "OPTIONAL" not in text and "BUY BUTTON" not in text
    assert "lived this myself" not in text          # his results line stays off until he writes it
    assert "Is there a workbook for every chapter?" in text      # the approved workbook item and question stay
    assert "Four workbooks for the foundation videos." in text
    assert "Headline" not in text


def test_package_page_has_exactly_one_buy_button_to_the_checkout(client):
    html = client.get("/what-your-body-forgot").get_data(as_text=True)
    assert html.count("Get the Package, $47") == 1
    assert html.count('href="/checkout/prod_wyk_package"') == 1
    assert 'href="/smoke-is-not-the-fire"' in html       # "Not ready yet?" link to the free Introduction


def test_package_page_has_only_noto_fonts_and_no_emoji(client):
    for path in ("/what-your-body-forgot", "/smoke-is-not-the-fire"):
        html = client.get(path).get_data(as_text=True)
        assert not re.search(r"[\U0001F300-\U0001FAFF☀-➿]", html)
        assert "Helvetica" not in html and "Arial" not in html
        assert "/static/fonts/noto.css" in html
    assert "ʻ" in client.get("/what-your-body-forgot").get_data(as_text=True)       # the okina in Molokaʻi


def test_the_book_is_not_sold_by_itself():
    from content import load_digital_products
    sold = [p for p in load_digital_products()["products"] if "forgot" in p["name"].lower() or "body" in p["name"].lower()]
    assert [p["id"] for p in sold] == [PACKAGE]
    assert sold[0]["price"] == 47 and sold[0]["delivery"] == "shelf"


def test_package_is_listed_under_products_and_on_the_rotten_fencepost_page(client):
    products = client.get("/products").get_data(as_text=True)
    assert 'href="/what-your-body-forgot"' in products
    assert "/product/prod_wyk_package" not in products
    fencepost = client.get("/rotten-fencepost").get_data(as_text=True)
    study = fencepost.index("Study the Principle")
    assert 'href="/what-your-body-forgot"' in fencepost[study:]
    assert fencepost.index("What Your Body Forgot") > study


def test_old_product_address_goes_to_the_package_page(client):
    resp = client.get("/product/prod_wyk_package")
    assert resp.status_code == 301 and resp.headers["Location"].endswith("/what-your-body-forgot")


def test_both_pages_are_in_the_sitemap(client):
    xml = client.get("/sitemap.xml").get_data(as_text=True)
    assert xml.count("/what-your-body-forgot<") == 1 and xml.count("/smoke-is-not-the-fire<") == 1


def test_checkout_for_the_package_shows_card_first_then_paypal(client, monkeypatch):
    monkeypatch.setattr(payments_module, "STRIPE_ENABLED", True)
    monkeypatch.setattr(payments_module, "PAYPAL_CLIENT_ID", "test-id")
    monkeypatch.setattr(payments_module, "PAYPAL_CLIENT_SECRET", "test-secret")
    resp = client.get("/checkout/prod_wyk_package")
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert html.index("Pay with Credit / Debit Card") < html.index('id="paypal-button-container"')
    assert "$47.00" in html
    assert "Instant access. Your shelf link appears right after you pay, and comes to your email too." in html
    assert "Wellness Community" not in html


# ----------------------------------------------------------------- the free Introduction
def _intro_paragraphs():
    return json.loads((ROOT / "content_text" / "smoke_is_not_the_fire.json").read_text(encoding="utf-8"))["paragraphs"]


def test_introduction_page_shows_the_whole_text_with_no_sign_up(client):
    resp = client.get("/smoke-is-not-the-fire")
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    paragraphs = _intro_paragraphs()
    assert paragraphs[0] == "Every rancher knows there comes a day when he has to walk the fence."
    assert paragraphs[-1] == "We begin building something that can stand."
    assert len(paragraphs) == 123
    import html as htmllib
    unescaped = htmllib.unescape(html)
    for paragraph in paragraphs:
        assert "<p>" + paragraph + "</p>" in unescaped
    assert "Continue" not in html                      # the leftover "(Continue...)" note is not his words
    assert "Read the whole Introduction here, free. No sign-up needed." in html
    assert 'href="/smoke-is-not-the-fire/download"' in html and 'href="/what-your-body-forgot"' in html
    for words in ("Want a copy to keep?", "Want to hear when new chapters come out?", "Ready for the rest?", "Keep Me Posted"):
        assert words in html


def test_introduction_pdf_downloads_and_is_noto_only(client):
    resp = client.get("/smoke-is-not-the-fire/download")
    assert resp.status_code == 200 and resp.mimetype == "application/pdf"
    data = resp.get_data()
    assert data.startswith(b"%PDF")
    fonts = set(re.findall(rb"/BaseFont\s*/(?:[A-Z]{6}\+)?([A-Za-z\-]+)", data))
    assert fonts and all(b"Noto" in f for f in fonts)


def test_keep_me_posted_saves_the_email_and_sends_nothing_to_the_person(client, monkeypatch):
    events, sent = [], []
    monkeypatch.setattr(downloads_module, "_append_sheet_event", lambda *a: events.append(a))
    monkeypatch.setattr(downloads_module, "_notify_new_subscriber", lambda *a, **k: None)
    monkeypatch.setattr(downloads_module, "_send_welcome_email", lambda *a, **k: sent.append("welcome"))
    monkeypatch.setattr(downloads_module, "_schedule_followups", lambda *a, **k: sent.append("followups"))
    monkeypatch.setattr(smtplib, "SMTP", lambda *a, **k: sent.append("smtp"))
    resp = client.post("/smoke-is-not-the-fire/keep-me-posted", data={"email": "Reader@example.com"}, headers={"User-Agent": "Mozilla/5.0"})
    assert resp.status_code == 302 and "saved=1" in resp.headers["Location"]
    saved = downloads_module._load_subscribers()
    assert [(s["email"], s["source"]) for s in saved] == [("reader@example.com", "introduction_signup")]
    assert events and events[0][1] == "reader@example.com" and events[0][2] == "Introduction Signup"
    assert sent == []
    assert "Mahalo. Your email is saved." in client.get("/smoke-is-not-the-fire?saved=1").get_data(as_text=True)


def test_the_hidden_trap_field_shows_no_words_to_any_reader_but_still_catches_bots(client):
    html = client.get("/smoke-is-not-the-fire").get_data(as_text=True)
    assert "Leave this empty" not in html and "Leave this empty" not in _text(html)
    assert 'name="website"' in html and 'class="intro-trap" aria-hidden="true"' in html
    client.post("/smoke-is-not-the-fire/keep-me-posted", data={"email": "bot@example.com", "website": "x"}, headers={"User-Agent": "Mozilla/5.0"})
    assert downloads_module._load_subscribers() == []


def test_keep_me_posted_has_the_same_spam_guards_as_the_other_forms(client):
    ua = {"User-Agent": "Mozilla/5.0"}
    client.post("/smoke-is-not-the-fire/keep-me-posted", data={"email": "bot@example.com", "website": "http://spam"}, headers=ua)
    client.post("/smoke-is-not-the-fire/keep-me-posted", data={"email": "not-an-email"}, headers=ua)
    client.post("/smoke-is-not-the-fire/keep-me-posted", data={"email": "someone@mailinator.com"}, headers=ua)
    client.post("/smoke-is-not-the-fire/keep-me-posted", data={"email": "real@example.com"}, headers={"User-Agent": ""})
    assert downloads_module._load_subscribers() == []


def test_a_rebuild_from_the_sheet_never_turns_introduction_signups_into_follow_up_recipients(monkeypatch):
    class Sheet:
        def get_all_values(self):
            now = datetime.now(timezone.utc).isoformat()
            return [["", "reader@example.com", "Introduction Signup", now],
                    ["Ann", "footer@example.com", "Website Signup", now]]
    monkeypatch.setattr(downloads_module, "_open_sheet", lambda: Sheet())
    state = downloads_module._read_sheet_state()
    assert state["reader@example.com"]["source"] == "introduction_signup"
    assert state["footer@example.com"]["source"] == "footer_signup"
    sends = []
    monkeypatch.setattr(downloads_module, "_schedule_followups", lambda *a: sends.append(a[0]))
    downloads_module._reconcile_subscribers_from_sheet()
    downloads_module._recover_pending_followups()
    assert "reader@example.com" not in sends


# ----------------------------------------------------------------- paying -> the shelf
class _FakeSMTP:
    sent = []

    def __init__(self, host, port): pass
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def starttls(self): pass
    def login(self, u, p): pass
    def sendmail(self, frm, to, msg): _FakeSMTP.sent.append({"to": to, "msg": msg})


def test_paying_by_paypal_shows_the_shelf_link_emails_it_and_records_the_buyer(client, monkeypatch):
    _FakeSMTP.sent = []
    for name, value in (("SMTP_HOST", "smtp.test"), ("SMTP_USER", "n@test"), ("SMTP_PASS", "x")):
        monkeypatch.setattr(payments_module, name, value)
    monkeypatch.setattr(smtplib, "SMTP", _FakeSMTP)
    monkeypatch.setattr(payments_module, "save_digital_products", lambda data: None)
    monkeypatch.setattr(payments_module, "_get_paypal_token", lambda: "t")
    monkeypatch.setattr(payments_module, "_get_paypal_order", lambda oid, t: {
        "payer": {"name": {"given_name": "Jane", "surname": "Buyer"}, "email_address": "jane@example.test"}})
    resp = client.get("/paypal/success?orderID=ORDER9&product_id=" + PACKAGE)
    html = resp.get_data(as_text=True)
    link = re.search(r'href="(/shelf/[^"]+)"', html).group(1)
    assert resp.status_code == 200 and "Open Your Shelf" in html and link == shelf.shelf_path("ORDER9")
    mails = [m for m in _FakeSMTP.sent if m["to"] == ["jane@example.test"]]
    assert len(mails) == 1 and "/shelf/" in mails[0]["msg"] and "does not expire" in mails[0]["msg"]
    assert shelf.buyers()["ORDER9"]["email"] == "jane@example.test"
    assert client.get(link).status_code == 200


def test_paying_by_card_delivers_to_the_shelf_once(monkeypatch):
    monkeypatch.setattr(payments_module, "save_digital_products", lambda data: None)
    from content import get_product_by_id
    product = get_product_by_id(PACKAGE)
    url = payments_module._fulfill_stripe_purchase(product, "cs_live_1", "Jane", "Jane@Example.test")
    again = payments_module._fulfill_stripe_purchase(product, "cs_live_1", "Jane", "Jane@Example.test")
    assert url == again == shelf.shelf_path("cs_live_1")
    assert list(shelf.buyers()) == ["cs_live_1"] and shelf.buyers()["cs_live_1"]["email"] == "jane@example.test"


def test_shelf_link_is_not_issued_when_the_signing_secret_is_missing(monkeypatch):
    monkeypatch.setattr(config, "DOWNLOAD_TOKEN_SECRET", "")
    assert shelf.shelf_path("x") is None
    ready, reason = payments_module._delivery_ready({"id": PACKAGE, "delivery": "shelf"}, None)
    assert not ready and "secret" in reason


def test_health_page_counts_the_shelf(client):
    data = client.get("/health/sales").get_json()
    entry = next(p for p in data["products"] if p["id"] == PACKAGE)
    assert entry["file_ok"] is True and entry["price"] == 47


# ----------------------------------------------------------------- the shelf itself
def test_shelf_link_never_expires_and_forged_links_fail(client):
    url = _shelf_url()
    assert client.get(url).status_code == 200
    token = url.rsplit("/", 1)[1]
    assert shelf.URLSafeSerializer(SECRET, salt="buyer-shelf").loads(token) == {"oid": "order-1"}   # no time stamp inside
    assert client.get(url[:-3] + "abc").status_code == 404
    assert client.get("/shelf/not-a-token").status_code == 404
    other = shelf.URLSafeSerializer("another-secret", salt="buyer-shelf").dumps({"oid": "order-1"})
    assert client.get("/shelf/" + other).status_code == 404


def test_shelf_page_is_private(client):
    resp = client.get(_shelf_url())
    assert "noindex" in resp.headers["X-Robots-Tag"] and resp.headers["Cache-Control"] == "no-store"
    assert "no-referrer" == resp.headers["Referrer-Policy"]
    assert 'content="noindex, nofollow"' in resp.get_data(as_text=True)
    assert "/shelf/" not in client.get("/sitemap.xml").get_data(as_text=True)


def test_day_one_shelf_holds_chapter_guides_workbooks_and_videos(client):
    html = client.get(_shelf_url()).get_data(as_text=True)
    text = _text(html)
    assert "Chapter 1: The Clock That Was Never There" in text
    assert "Find the Cause, Not the Symptoms" in text and "Field Guide" in text
    book = shelf.build_shelf("order-1")
    assert [g["id"] for g in book["groups"]] == ["001", "002", "003", "004"]
    for group in book["groups"]:
        kinds = sorted(v["kind"] for v in group["rows"])
        assert kinds == ["intro", "workbook"], group["id"]       # the workbook and the Introduction sit under each video
        assert group["video"]["link"] == f"/campaign/{group['id']}"
        assert group["title"]
        assert all(v["link"].startswith("/shelf/file/") for v in group["rows"])
    assert [v["title"] for v in book["book"]] == ["Chapter 1: The Clock That Was Never There"]
    assert [v["title"] for v in book["guides"]] == ["Find the Cause, Not the Symptoms", "The Rotten Fencepost Field Guide"]
    assert 'href="/campaign/001"' in html


def test_every_link_on_the_shelf_delivers_the_real_file(client):
    book = shelf.build_shelf("order-1")
    files = [v for v in book["book"] + book["guides"]] + [v for g in book["groups"] for v in g["rows"]]
    assert len(files) == 11            # chapter 1, two guides, four workbooks, four copies of the Introduction
    for view in files:
        resp = client.get(view["link"])
        assert resp.status_code == 200, view
        assert resp.get_data().startswith(b"%PDF"), view["title"]


def test_chapter_pdf_is_noto_with_the_running_header_text():
    data = (ROOT / "shelf_seed" / "files" / "chapter-01.pdf").read_bytes()
    fonts = set(re.findall(rb"/BaseFont\s*/(?:[A-Z]{6}\+)?([A-Za-z\-]+)", data))
    assert fonts and all(b"Noto" in f for f in fonts)
    assert not re.search(rb"Helvetica|Arial|DejaVu|Georgia", data)


def test_a_shelf_file_link_works_only_for_its_own_file_and_is_use_limited(client):
    book = shelf.build_shelf("order-1")
    chapter = book["book"][0]["link"]
    token = chapter.rsplit("/", 1)[1]
    assert client.get("/shelf/file/guide-field-guide/" + token).status_code == 403     # token for another item
    assert client.get("/shelf/file/chapter-01/garbage").status_code == 403
    for _ in range(download_tokens.MAX_USES):
        assert client.get(chapter).status_code == 200
    assert client.get(chapter).status_code == 403                                        # the sixth use is refused...
    assert client.get(shelf.build_shelf("order-1")["book"][0]["link"]).status_code == 200   # ...a fresh page view mints a new one


def test_shelf_files_are_not_public_and_not_under_static():
    assert not list((ROOT / "static").rglob("chapter-01*"))
    for item in shelf._seed_items():
        if item.get("file"):
            assert (ROOT / "shelf_seed" / "files" / item["file"]).is_file(), item["id"]


def test_revoking_one_order_shuts_only_that_shelf(client):
    a, b = _shelf_url("order-a"), _shelf_url("order-b")
    resp = client.post("/api/shelf/revoke", json={"order_id": "order-a"}, headers=_auth())
    assert resp.status_code == 200
    assert client.get(a).status_code == 404 and client.get(b).status_code == 200


# ----------------------------------------------------------------- the Foreman's door
def test_the_door_is_shut_without_the_password(client, monkeypatch):
    assert client.get("/api/shelf/items").status_code == 401
    assert client.get("/api/shelf/items", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert client.put("/api/shelf/items/x", json={}).status_code == 401
    assert client.get("/api/shelf/buyers").status_code == 401
    monkeypatch.setattr(config, "SHELF_ADMIN_KEY", "")
    assert client.get("/api/shelf/items", headers=_auth()).status_code == 503


def test_foreman_adds_a_chapter_and_every_buyer_old_and_new_sees_it(client):
    old = _shelf_url("old-buyer")
    meta = {"kind": "chapter", "title": "Chapter 2: Test Chapter", "order": 11}
    resp = client.put("/api/shelf/items/chapter-02", data={"meta": json.dumps(meta), "file": (io.BytesIO(b"%PDF-1.4 chapter two"), "c2.pdf")},
                      headers=_auth(), content_type="multipart/form-data")
    assert resp.status_code == 200 and resp.get_json()["item"]["file"] == "chapter-02.pdf"
    for url in (old, _shelf_url("brand-new-buyer")):
        html = client.get(url).get_data(as_text=True)
        assert "Chapter 2: Test Chapter" in html
    link = [v for v in shelf.build_shelf("old-buyer")["book"] if v["id"] == "chapter-02"][0]["link"]
    assert client.get(link).get_data() == b"%PDF-1.4 chapter two"
    order = [v["title"] for v in shelf.build_shelf("old-buyer")["book"]]
    assert order == ["Chapter 1: The Clock That Was Never There", "Chapter 2: Test Chapter"]


def test_foreman_adds_video_005_and_moves_chapter_1_beside_it_without_new_files(client):
    meta = {"kind": "video", "title": "The video", "label": "Watch the video", "campaign": "005", "url": "/campaign/005", "order": 105}
    assert client.put("/api/shelf/items/video-005", json=meta, headers=_auth()).status_code == 200
    again = {"kind": "chapter", "title": "Chapter 1: The Clock That Was Never There", "order": 10, "campaign": "005"}
    assert client.put("/api/shelf/items/chapter-01", json=again, headers=_auth()).status_code == 200
    book = shelf.build_shelf("anyone")
    group = next(g for g in book["groups"] if g["id"] == "005")
    assert group["video"]["link"] == "/campaign/005" and [v["kind"] for v in group["rows"]] == ["chapter"]
    assert client.get(group["rows"][0]["link"]).get_data().startswith(b"%PDF")            # still the built-in file
    assert len(book["book"]) == 1


def test_foreman_adds_a_workbook_to_a_campaign(client):
    resp = client.put("/api/shelf/items/workbook-005", data={"meta": json.dumps({"kind": "workbook", "title": "Workbook", "campaign": "005"}),
                      "file": (io.BytesIO(b"%PDF-1.4 w"), "w.pdf")}, headers=_auth(), content_type="multipart/form-data")
    assert resp.status_code == 200
    assert [v["id"] for g in shelf.build_shelf("x")["groups"] if g["id"] == "005" for v in g["rows"]] == ["workbook-005"]


def test_the_door_refuses_bad_requests(client):
    def put(item_id, **kw):
        return client.put("/api/shelf/items/" + item_id, headers=_auth(), **kw)
    assert put("Bad Id", json={"kind": "chapter", "title": "x", "url": "/a"}).status_code == 400
    assert put("ok-id", json={"kind": "nonsense", "title": "x", "url": "/a"}).status_code == 400
    assert put("ok-id", json={"kind": "chapter", "title": "", "url": "/a"}).status_code == 400
    assert put("ok-id", json={"kind": "chapter", "title": "x"}).status_code == 400                       # nothing to deliver
    assert put("ok-id", json={"kind": "chapter", "title": "x", "url": "http://evil.example"}).status_code == 400
    assert put("ok-id", json={"kind": "chapter", "title": "x", "url": "//evil.example"}).status_code == 400
    assert put("ok-id", json={"kind": "chapter", "title": "x", "product": "nope"}).status_code == 400
    assert put("ok-id", json={"kind": "chapter", "title": "x", "campaign": "5"}).status_code == 400
    bad = put("ok-id", data={"meta": json.dumps({"kind": "chapter", "title": "x"}), "file": (io.BytesIO(b"MZ"), "run.exe")}, content_type="multipart/form-data")
    assert bad.status_code == 400
    assert shelf.item_count() == len(shelf._seed_items())


def test_removing_an_item_hides_built_in_ones_and_deletes_live_ones(client):
    client.put("/api/shelf/items/extra", json={"kind": "other", "title": "Extra", "url": "/campaign/001"}, headers=_auth())
    assert any(i["id"] == "extra" for i in client.get("/api/shelf/items", headers=_auth()).get_json()["items"])
    assert client.delete("/api/shelf/items/extra", headers=_auth()).status_code == 200
    assert client.delete("/api/shelf/items/video-004", headers=_auth()).status_code == 200
    ids = [i["id"] for i in client.get("/api/shelf/items", headers=_auth()).get_json()["items"]]
    assert "extra" not in ids and "video-004" not in ids and "workbook-004" in ids
    assert client.delete("/api/shelf/items/never-existed", headers=_auth()).status_code == 404


def test_the_foreman_can_list_buyers_with_their_shelf_addresses(client):
    shelf.record_buyer("o1", "A@Example.test", "Ann")
    shelf.record_buyer("o2", "", "")
    shelf.record_buyer("o2", "late@example.test", "Late")          # an email that arrives later is filled in
    rows = {r["order_id"]: r for r in client.get("/api/shelf/buyers", headers=_auth()).get_json()["buyers"]}
    assert rows["o1"]["email"] == "a@example.test" and rows["o2"]["email"] == "late@example.test"
    assert rows["o1"]["shelf_url"] == config.SITE_DOMAIN + shelf.shelf_path("o1")
    assert client.get(rows["o1"]["shelf_url"].replace(config.SITE_DOMAIN, "")).status_code == 200
