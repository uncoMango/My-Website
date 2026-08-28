# tests/test_email_capture_compliance.py
# =========================================================
# ACTIVATE-001-003-OUTWARD work order (2026-08-27): the sitewide "Join the
# Kingdom Community" signup form (templates/base.html) was found live and
# working, but its three automated emails (welcome, day-3, day-7) carried
# no unsubscribe link and no physical mailing address -- a real CAN-SPAM
# gap -- and the day-3/day-7 follow-ups were scheduled only via an
# in-memory threading.Timer, lost on every process restart.
#
# These tests cover the real fix:
#   - PHYSICAL_MAILING_ADDRESS unset -> every automated marketing send
#     fails closed (no non-compliant email is ever sent), matching this
#     app's own established missing-secret convention; subscriber storage
#     itself is unaffected.
#   - PHYSICAL_MAILING_ADDRESS set -> the welcome email actually carries
#     the address and a working unsubscribe link.
#   - unsubscribe_tokens: real roundtrip, tampered rejection, missing-
#     secret fail-closed (mirrors tests/test_download_tokens.py's style).
#   - /unsubscribe/<token> actually marks the subscriber and -- proven
#     directly, not assumed -- a subsequent day-3/day-7 send is skipped
#     for that address.
#   - _recover_pending_followups() recomputes an overdue day-3/day-7 send
#     from the persisted subscriber record (surviving a lost in-memory
#     timer), scoped only to footer_signup subscribers (matching exactly
#     what was already being scheduled before this fix), and never
#     re-sends one already marked sent.
#
# No real network call is made anywhere in this file -- smtplib.SMTP and
# threading.Timer are both faked. tests/conftest.py's autouse
# _isolate_subscribers fixture redirects SUBSCRIBERS_FILE to a tmp_path
# copy for every test in this suite, so the real data/subscribers.json is
# never touched.
# =========================================================

import smtplib
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import app as app_module  # noqa: E402
from blueprints import downloads as downloads_module  # noqa: E402
import unsubscribe_tokens  # noqa: E402

TEST_SECRET = "test-only-unsubscribe-secret-not-real"


@pytest.fixture
def client():
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


class FakeSMTP:
    """Stands in for smtplib.SMTP without any real network call. downloads.py
    calls server.send_message(msg), unlike blueprints/payments.py's own
    server.sendmail(...) -- this fake matches the method actually used here."""
    sent = []

    def __init__(self, host, port):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def starttls(self):
        pass

    def login(self, user, password):
        pass

    def send_message(self, msg):
        FakeSMTP.sent.append(msg)


class FakeTimer:
    """Records what would have been scheduled, without starting a real
    background thread or waiting real time."""
    calls = []

    def __init__(self, interval, function, args=None):
        FakeTimer.calls.append((interval, function, tuple(args or ())))

    def start(self):
        pass


def _to(email):
    return [m for m in FakeSMTP.sent if m["To"] == email]


def _body_text(msg):
    """MIMEText auto-encodes (base64/quoted-printable) once the body
    contains non-ASCII characters (this template's own em dashes already
    did, before this fix) -- decode=True is required to get the real text
    back rather than the raw encoded payload."""
    payload = msg.get_payload(decode=True)
    charset = msg.get_content_charset() or "utf-8"
    return payload.decode(charset)


def _enable_smtp(monkeypatch):
    monkeypatch.setattr(downloads_module, "SMTP_HOST", "smtp.test.local")
    monkeypatch.setattr(downloads_module, "SMTP_PORT", 587)
    monkeypatch.setattr(downloads_module, "SMTP_USER", "noreply@test.local")
    monkeypatch.setattr(downloads_module, "SMTP_PASS", "fake-password-not-real")
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    FakeSMTP.sent = []


def _enable_compliance(monkeypatch, address="123 Test Way, Kaunakakai, HI 96748"):
    monkeypatch.setattr(downloads_module, "PHYSICAL_MAILING_ADDRESS", address)
    monkeypatch.setattr(unsubscribe_tokens, "DOWNLOAD_TOKEN_SECRET", TEST_SECRET)


def _fake_timers(monkeypatch):
    monkeypatch.setattr(downloads_module, "Timer", FakeTimer)
    FakeTimer.calls = []


# ---------------------------------------------------------------------------
# unsubscribe_tokens -- mirrors tests/test_download_tokens.py's own style
# ---------------------------------------------------------------------------

def test_generate_and_resolve_unsubscribe_token_roundtrip(monkeypatch):
    monkeypatch.setattr(unsubscribe_tokens, "DOWNLOAD_TOKEN_SECRET", TEST_SECRET)
    token = unsubscribe_tokens.generate_unsubscribe_token("jane@example.test")
    email, reason = unsubscribe_tokens.resolve_unsubscribe_token(token)
    assert email == "jane@example.test"
    assert reason is None


def test_resolve_rejects_tampered_token(monkeypatch):
    monkeypatch.setattr(unsubscribe_tokens, "DOWNLOAD_TOKEN_SECRET", TEST_SECRET)
    token = unsubscribe_tokens.generate_unsubscribe_token("jane@example.test")
    tampered = token[:-1] + ("a" if token[-1] != "a" else "b")
    email, reason = unsubscribe_tokens.resolve_unsubscribe_token(tampered)
    assert email is None
    assert reason == "invalid"


def test_generate_returns_none_without_secret(monkeypatch):
    monkeypatch.setattr(unsubscribe_tokens, "DOWNLOAD_TOKEN_SECRET", "")
    assert unsubscribe_tokens.generate_unsubscribe_token("jane@example.test") is None


def test_resolve_reports_not_configured_without_secret(monkeypatch):
    monkeypatch.setattr(unsubscribe_tokens, "DOWNLOAD_TOKEN_SECRET", "")
    email, reason = unsubscribe_tokens.resolve_unsubscribe_token("anything")
    assert email is None
    assert reason == "not_configured"


# ---------------------------------------------------------------------------
# /subscribe -- compliance fail-closed + real content when configured
# ---------------------------------------------------------------------------

def test_subscribe_skips_welcome_email_when_no_physical_address_configured(client, monkeypatch):
    _enable_smtp(monkeypatch)
    monkeypatch.setattr(downloads_module, "PHYSICAL_MAILING_ADDRESS", "")
    _fake_timers(monkeypatch)

    resp = client.post("/subscribe", data={"first_name": "Jane", "email": "jane@example.test"})

    assert resp.status_code == 302
    # No non-compliant email to the subscriber -- the admin new-subscriber
    # notification (to Kahu Phil himself, not a commercial email to the
    # subscriber) legitimately still fires and is not what this asserts.
    assert _to("jane@example.test") == []
    subscribers = downloads_module._load_subscribers()
    assert any(s["email"] == "jane@example.test" for s in subscribers)  # storage still works


def test_subscribe_sends_welcome_with_address_and_working_unsubscribe_link(client, monkeypatch):
    _enable_smtp(monkeypatch)
    _enable_compliance(monkeypatch, address="123 Test Way, Kaunakakai, HI 96748")
    _fake_timers(monkeypatch)

    resp = client.post("/subscribe", data={"first_name": "Jane", "email": "jane@example.test"})

    assert resp.status_code == 302
    welcome = _to("jane@example.test")
    assert len(welcome) == 1
    body = _body_text(welcome[0])
    assert "123 Test Way, Kaunakakai, HI 96748" in body
    assert "/unsubscribe/" in body


def test_subscribe_schedules_both_followups_on_signup(client, monkeypatch):
    _enable_smtp(monkeypatch)
    _enable_compliance(monkeypatch)
    _fake_timers(monkeypatch)

    client.post("/subscribe", data={"first_name": "Jane", "email": "jane@example.test"})

    scheduled_funcs = [call[1] for call in FakeTimer.calls]
    assert downloads_module._send_followup_day3 in scheduled_funcs
    assert downloads_module._send_followup_day7 in scheduled_funcs
    for interval, func, args in FakeTimer.calls:
        if func is downloads_module._send_followup_day3:
            assert 3 * 24 * 3600 - 5 <= interval <= 3 * 24 * 3600
        if func is downloads_module._send_followup_day7:
            assert 7 * 24 * 3600 - 5 <= interval <= 7 * 24 * 3600
        assert args[0] == "jane@example.test"


# ---------------------------------------------------------------------------
# /unsubscribe/<token> -- actually stops future automated mail, not just
# decorative text
# ---------------------------------------------------------------------------

def test_unsubscribe_marks_subscriber_and_returns_200(client, monkeypatch):
    _enable_compliance(monkeypatch)
    downloads_module._save_subscribers([
        {"email": "jane@example.test", "first_name": "Jane", "source": "footer_signup",
         "timestamp": datetime.now(timezone.utc).isoformat()},
    ])
    token = unsubscribe_tokens.generate_unsubscribe_token("jane@example.test")

    resp = client.get(f"/unsubscribe/{token}")

    assert resp.status_code == 200
    subscribers = downloads_module._load_subscribers()
    sub = next(s for s in subscribers if s["email"] == "jane@example.test")
    assert sub["unsubscribed"] is True
    assert "unsubscribed_at" in sub


def test_unsubscribe_rejects_invalid_token(client, monkeypatch):
    _enable_compliance(monkeypatch)
    resp = client.get("/unsubscribe/not-a-real-token")
    assert resp.status_code == 400


def test_unsubscribed_address_never_receives_day3_or_day7(client, monkeypatch):
    """The real requirement: an unsubscribe must actually stop future
    automated mail, not merely record a flag no sender ever checks."""
    _enable_smtp(monkeypatch)
    _enable_compliance(monkeypatch)
    downloads_module._save_subscribers([
        {"email": "jane@example.test", "first_name": "Jane", "source": "footer_signup",
         "timestamp": datetime.now(timezone.utc).isoformat()},
    ])
    token = unsubscribe_tokens.generate_unsubscribe_token("jane@example.test")
    client.get(f"/unsubscribe/{token}")

    downloads_module._send_followup_day3("jane@example.test", "Jane")
    downloads_module._send_followup_day7("jane@example.test", "Jane")

    assert _to("jane@example.test") == []


# ---------------------------------------------------------------------------
# _recover_pending_followups -- an in-memory threading.Timer lost to a
# restart must be recomputed from the persisted record, not silently
# dropped
# ---------------------------------------------------------------------------

def test_recover_sends_overdue_footer_signup_followups_and_marks_sent(monkeypatch):
    _enable_smtp(monkeypatch)
    _enable_compliance(monkeypatch)
    ten_days_ago = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    downloads_module._save_subscribers([
        {"email": "overdue@example.test", "first_name": "Overdue", "source": "footer_signup",
         "timestamp": ten_days_ago},
    ])

    downloads_module._recover_pending_followups()

    assert len(_to("overdue@example.test")) == 2  # both day-3 and day-7 fired
    sub = downloads_module._load_subscribers()[0]
    assert sub["day3_sent"] is True
    assert sub["day7_sent"] is True


def test_recover_ignores_non_footer_signup_sources(monkeypatch):
    """aloha_wellness_freebie signups never had a day-3/day-7 follow-up
    scheduled in the first place -- recovery must not start sending them
    one now."""
    _enable_smtp(monkeypatch)
    _enable_compliance(monkeypatch)
    ten_days_ago = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    downloads_module._save_subscribers([
        {"email": "freebie@example.test", "source": "aloha_wellness", "timestamp": ten_days_ago},
    ])

    downloads_module._recover_pending_followups()

    assert _to("freebie@example.test") == []


def test_recover_never_resends_an_already_sent_followup(monkeypatch):
    _enable_smtp(monkeypatch)
    _enable_compliance(monkeypatch)
    ten_days_ago = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    downloads_module._save_subscribers([
        {"email": "done@example.test", "first_name": "Done", "source": "footer_signup",
         "timestamp": ten_days_ago, "day3_sent": True, "day7_sent": True},
    ])

    downloads_module._recover_pending_followups()

    assert _to("done@example.test") == []


class FakeSheet:
    """Stands in for a real gspread Worksheet -- append_row/get_all_values
    only, matching exactly what downloads.py's own Sheets integration
    actually calls. FakeSheet.rows is a class attribute so every
    _open_sheet() call in a test returns a fresh wrapper over the same
    shared, persistent row list -- the same behavior a real Sheet has."""
    rows = []

    def append_row(self, row):
        FakeSheet.rows.append(row)

    def get_all_values(self):
        return list(FakeSheet.rows)


def _enable_sheets(monkeypatch):
    FakeSheet.rows = []
    monkeypatch.setattr(downloads_module, "_open_sheet", lambda: FakeSheet())


def _disable_sheets(monkeypatch):
    monkeypatch.setattr(downloads_module, "_open_sheet", lambda: None)


# ---------------------------------------------------------------------------
# Google Sheets durability -- the smallest solution consistent with the
# existing architecture (no new paid service, no redesign): the already-
# integrated, optional Google Sheets append becomes a real, readable
# event log a wiped local file can be reconstructed from.
# ---------------------------------------------------------------------------

def test_reconcile_is_a_no_op_when_sheets_not_configured(monkeypatch):
    _disable_sheets(monkeypatch)
    downloads_module._save_subscribers([])

    downloads_module._reconcile_subscribers_from_sheet()

    assert downloads_module._load_subscribers() == []


def test_reconcile_restores_wiped_local_state_from_sheet_events(monkeypatch):
    """The real scenario this whole mechanism exists for: a redeploy wipes
    data/subscribers.json, but the durable Sheet still has the full
    history -- including the unsubscribe, which must NOT be forgotten."""
    _enable_sheets(monkeypatch)
    signup_time = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    FakeSheet.rows = [
        ["Jane", "jane@example.test", downloads_module.SHEET_EVENT_SIGNUP, signup_time],
        ["Jane", "jane@example.test", downloads_module.SHEET_EVENT_UNSUBSCRIBED, signup_time],
        ["Jane", "jane@example.test", downloads_module.SHEET_EVENT_DAY3_SENT, signup_time],
    ]
    downloads_module._save_subscribers([])  # local file wiped, as if by a fresh redeploy

    downloads_module._reconcile_subscribers_from_sheet()

    subscribers = downloads_module._load_subscribers()
    assert len(subscribers) == 1
    sub = subscribers[0]
    assert sub["email"] == "jane@example.test"
    assert sub["source"] == "footer_signup"
    assert sub["timestamp"] == signup_time
    assert sub["unsubscribed"] is True
    assert sub["day3_sent"] is True
    assert "day7_sent" not in sub or sub["day7_sent"] is False


def test_reconcile_never_downgrades_a_true_flag(monkeypatch):
    _enable_sheets(monkeypatch)
    FakeSheet.rows = []  # sheet has nothing yet (e.g. a prior append failed)
    downloads_module._save_subscribers([
        {"email": "jane@example.test", "first_name": "Jane", "source": "footer_signup",
         "timestamp": datetime.now(timezone.utc).isoformat(), "day3_sent": True},
    ])

    downloads_module._reconcile_subscribers_from_sheet()

    sub = downloads_module._load_subscribers()[0]
    assert sub["day3_sent"] is True


def test_reconcile_end_to_end_survives_a_simulated_redeploy(monkeypatch):
    """The user's own explicit requirement: verify recovery after restart
    /redeploy, not just that the code compiles. Full cycle: sign up (via
    recover, standing in for the original signup), both follow-ups fire
    and log to the Sheet, the local file is then wiped (simulating a
    redeploy), and reconciliation + recovery together must NOT re-send
    either follow-up a second time."""
    _enable_smtp(monkeypatch)
    _enable_compliance(monkeypatch)
    _enable_sheets(monkeypatch)
    ten_days_ago = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    downloads_module._save_subscribers([
        {"email": "overdue@example.test", "first_name": "Overdue", "source": "footer_signup",
         "timestamp": ten_days_ago},
    ])

    downloads_module._recover_pending_followups()  # first process: both fire, both logged to the Sheet
    assert len(_to("overdue@example.test")) == 2
    assert any(r[2] == downloads_module.SHEET_EVENT_DAY3_SENT for r in FakeSheet.rows)
    assert any(r[2] == downloads_module.SHEET_EVENT_DAY7_SENT for r in FakeSheet.rows)

    FakeSMTP.sent = []
    downloads_module._save_subscribers([])  # simulate a redeploy wiping the local file

    downloads_module._reconcile_subscribers_from_sheet()
    downloads_module._recover_pending_followups()

    assert _to("overdue@example.test") == []  # neither follow-up is sent a second time
    sub = downloads_module._load_subscribers()[0]
    assert sub["day3_sent"] is True and sub["day7_sent"] is True


def test_unsubscribe_appends_sheet_event(client, monkeypatch):
    _enable_sheets(monkeypatch)
    _enable_compliance(monkeypatch)
    downloads_module._save_subscribers([
        {"email": "jane@example.test", "first_name": "Jane", "source": "footer_signup",
         "timestamp": datetime.now(timezone.utc).isoformat()},
    ])
    token = unsubscribe_tokens.generate_unsubscribe_token("jane@example.test")

    client.get(f"/unsubscribe/{token}")

    assert any(
        r[1] == "jane@example.test" and r[2] == downloads_module.SHEET_EVENT_UNSUBSCRIBED
        for r in FakeSheet.rows
    )


def test_day3_and_day7_success_append_sheet_events(monkeypatch):
    _enable_smtp(monkeypatch)
    _enable_compliance(monkeypatch)
    _enable_sheets(monkeypatch)
    downloads_module._save_subscribers([
        {"email": "jane@example.test", "first_name": "Jane", "source": "footer_signup",
         "timestamp": datetime.now(timezone.utc).isoformat()},
    ])

    downloads_module._send_followup_day3("jane@example.test", "Jane")
    downloads_module._send_followup_day7("jane@example.test", "Jane")

    assert any(r[2] == downloads_module.SHEET_EVENT_DAY3_SENT for r in FakeSheet.rows)
    assert any(r[2] == downloads_module.SHEET_EVENT_DAY7_SENT for r in FakeSheet.rows)


def test_recover_skips_unsubscribed_subscribers(monkeypatch):
    _enable_smtp(monkeypatch)
    _enable_compliance(monkeypatch)
    ten_days_ago = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    downloads_module._save_subscribers([
        {"email": "gone@example.test", "first_name": "Gone", "source": "footer_signup",
         "timestamp": ten_days_ago, "unsubscribed": True},
    ])

    downloads_module._recover_pending_followups()

    assert _to("gone@example.test") == []
