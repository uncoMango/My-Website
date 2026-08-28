# blueprints/downloads.py
import json
import os
import smtplib
from datetime import datetime, timezone
from threading import Timer
from urllib.parse import quote
from email.mime.text import MIMEText
from flask import Blueprint, send_file, abort, request, redirect, render_template
from config import BASE, EMAILS_FILE, SUBSCRIBERS_FILE, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, NOTIFY_EMAIL, LOGO_PATH, LOGO_HEIGHT, FOOTER_TEXT, PHYSICAL_MAILING_ADDRESS
from limiter import limiter
import unsubscribe_tokens

DAY3_SECONDS = 3 * 24 * 3600
DAY7_SECONDS = 7 * 24 * 3600

downloads_bp = Blueprint("downloads", __name__)

_DISPOSABLE_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "tempmail.com", "throwaway.email",
    "fakeinbox.com", "trashmail.com", "yopmail.com", "sharklasers.com",
    "spam4.me", "boun.cr",
}


def _valid_email(email):
    if len(email) < 6:
        return False
    if "@" not in email:
        return False
    local, domain = email.split("@", 1)
    if "." not in domain or domain.endswith("."):
        return False
    if domain.lower() in _DISPOSABLE_DOMAINS:
        return False
    if local.isdigit():
        return False
    if len(local) >= 6 and not any(c in "aeiou" for c in local.lower()):
        return False
    return True


# ---------------------------------------------------------------------------
# Subscriber storage helpers
# ---------------------------------------------------------------------------

def _load_subscribers():
    if not SUBSCRIBERS_FILE.exists():
        SUBSCRIBERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        SUBSCRIBERS_FILE.write_text("[]")
        print("[subscribers] data/subscribers.json did not exist — created empty file.", flush=True)
        return []
    try:
        return json.loads(SUBSCRIBERS_FILE.read_text())
    except Exception as e:
        print(f"[subscribers] Failed to load {SUBSCRIBERS_FILE}: {e}", flush=True)
        return []


def _save_subscribers(subscribers):
    SUBSCRIBERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUBSCRIBERS_FILE.write_text(json.dumps(subscribers, indent=2))


def _find_subscriber(subscribers, email):
    for s in subscribers:
        if s.get("email") == email:
            return s
    return None


def _is_unsubscribed(email):
    """Real-time check, reloaded from disk -- a day-3/day-7 send must
    never rely on the in-memory state captured at signup time, since the
    subscriber may have unsubscribed at any point since then."""
    sub = _find_subscriber(_load_subscribers(), email)
    return bool(sub and sub.get("unsubscribed"))


def _mark_subscriber_fields(email, **fields):
    """Updates one subscriber's own record in place (unsubscribed flag,
    day3_sent/day7_sent markers) -- never a second, parallel store."""
    subscribers = _load_subscribers()
    sub = _find_subscriber(subscribers, email)
    if sub is None:
        return False
    sub.update(fields)
    _save_subscribers(subscribers)
    return True


# Print stored subscribers on startup so we can verify data is persisting.
_startup_subs = _load_subscribers()
print(f"[subscribers] {len(_startup_subs)} subscriber(s) on startup:", flush=True)
for _s in _startup_subs:
    print(f"  - {_s.get('email', '?')}  name={_s.get('first_name', '')}", flush=True)
if not _startup_subs:
    print("[subscribers] (none stored yet)", flush=True)

# Remove any subscribers that fail current email validation.
_before_clean = len(_startup_subs)
_startup_subs = [s for s in _startup_subs if _valid_email(s.get("email", ""))]
if len(_startup_subs) < _before_clean:
    _save_subscribers(_startup_subs)
    print(f"[subscribers] Cleaned {_before_clean - len(_startup_subs)} invalid subscriber(s). {len(_startup_subs)} remain.", flush=True)

# Check for Google credentials at startup so misconfiguration is visible immediately.
_gc = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")
if _gc:
    print(f"[sheets] GOOGLE_CREDENTIALS_JSON found at startup ({len(_gc)} chars)", flush=True)
else:
    print("[sheets] GOOGLE_CREDENTIALS_JSON NOT SET at startup — sheet append will be skipped", flush=True)


# ---------------------------------------------------------------------------
# Email helpers — run synchronously so every step appears in Render logs
# ---------------------------------------------------------------------------

def _notify_new_subscriber(email, name=""):
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS]):
        return
    try:
        name_line = f"Name:  {name}\n" if name else ""
        body = (
            f"New subscriber:\n\n"
            f"{name_line}"
            f"Email: {email}\n"
            f"Time:  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
        )
        msg = MIMEText(body)
        msg["Subject"] = f"New Subscriber: {name + ' — ' if name else ''}{email}"
        msg["From"] = "kahuphil@keaupuni.faith"
        msg["To"] = NOTIFY_EMAIL
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"[notify] Notification sent to {NOTIFY_EMAIL}", flush=True)
    except Exception as e:
        print(f"[notify] FAILED for {email}: {e}", flush=True)


def _unsubscribe_footer_html(email):
    token = unsubscribe_tokens.generate_unsubscribe_token(email)
    link = f"https://keaupuniakeakua.faith/unsubscribe/{token}" if token else None
    parts = [f'<p style="color:rgba(255,255,255,0.5);font-size:0.8rem;">{PHYSICAL_MAILING_ADDRESS}</p>']
    if link:
        parts.append(f'<p style="color:rgba(255,255,255,0.5);font-size:0.8rem;"><a href="{link}" style="color:rgba(255,255,255,0.6);">Unsubscribe</a></p>')
    return "\n".join(parts)


def _unsubscribe_footer_plain(email):
    token = unsubscribe_tokens.generate_unsubscribe_token(email)
    lines = [PHYSICAL_MAILING_ADDRESS]
    if token:
        lines.append(f"Unsubscribe: https://keaupuniakeakua.faith/unsubscribe/{token}")
    return "\n".join(lines)


def _compliance_ready():
    """CAN-SPAM's real floor (working unsubscribe link + physical address)
    can only be met once Kahu Phil has supplied his own real mailing
    address -- never fabricated here. While unset, every automated
    marketing send below fails closed, the same convention already used
    for a missing SMTP credential; subscriber storage and the admin
    new-subscriber notification are unaffected either way."""
    return bool(PHYSICAL_MAILING_ADDRESS)


def _send_welcome_email(email, name=""):
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS]) or not _compliance_ready():
        return
    try:
        greeting = name if name else "friend"
        body = f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#1a1a1a;font-family:Georgia,serif;color:#f0ece3;">
<div style="max-width:560px;margin:40px auto;padding:40px;background:#2a2a2a;border-radius:8px;">
<h1 style="font-size:1.6rem;color:#d4a853;margin-bottom:0.5rem;">Ke Aupuni O Ke Akua Press</h1>
<hr style="border:none;border-top:1px solid rgba(255,255,255,0.15);margin:1.5rem 0;">
<p style="font-size:1.1rem;">Aloha {greeting},</p>
<p style="line-height:1.8;">You are now connected to Ke Aupuni O Ke Akua Press.</p>
<p style="line-height:1.8;">Watch your inbox. What is coming is not just information — it is invitation.</p>
<hr style="border:none;border-top:1px solid rgba(255,255,255,0.15);margin:1.5rem 0;">
<p style="color:rgba(255,255,255,0.6);font-size:0.9rem;">Kahu Phil Stephens<br>keaupuniakeakua.faith</p>
{_unsubscribe_footer_html(email)}
</div>
</body>
</html>"""
        msg = MIMEText(body, "html")
        msg["Subject"] = "You are connected — Ke Aupuni O Ke Akua"
        msg["From"] = "kahuphil@keaupuni.faith"
        msg["To"] = email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"[welcome] Welcome email sent to {email}", flush=True)
    except Exception as e:
        print(f"[welcome] FAILED for {email}: {e}", flush=True)


def _send_followup_day3(email, name=""):
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS]) or not _compliance_ready():
        return
    if _is_unsubscribed(email):
        print(f"[followup-day3] Skipped {email} -- unsubscribed", flush=True)
        return
    try:
        greeting = name if name else "friend"
        body = (
            f"Aloha {greeting},\n\n"
            "I have been thinking about you since you joined our community.\n\n"
            "The Kingdom of God is not a distant destination — it is the present reality "
            "you were created to walk in. Every step you take in faith is already Kingdom ground.\n\n"
            "Keep going. You are not alone in this.\n\n"
            "Mahalo for being here.\n\n"
            "Kahu Phil Stephens\n"
            "keaupuniakeakua.faith\n\n"
            "--\n"
            f"{_unsubscribe_footer_plain(email)}"
        )
        msg = MIMEText(body, "plain")
        msg["Subject"] = "A word for you — Ke Aupuni O Ke Akua"
        msg["From"] = "kahuphil@keaupuni.faith"
        msg["To"] = email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"[followup-day3] Day-3 email sent to {email}", flush=True)
        _mark_subscriber_fields(email, day3_sent=True)
        _append_sheet_event(name, email, SHEET_EVENT_DAY3_SENT, datetime.now(timezone.utc).isoformat())
    except Exception as e:
        print(f"[followup-day3] FAILED for {email}: {e}", flush=True)


def _send_followup_day7(email, name=""):
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS]) or not _compliance_ready():
        return
    if _is_unsubscribed(email):
        print(f"[followup-day7] Skipped {email} -- unsubscribed", flush=True)
        return
    try:
        greeting = name if name else "friend"
        body = (
            f"Aloha {greeting},\n\n"
            "A week ago you connected with Ke Aupuni O Ke Akua — and I want to share "
            "something that has been close to my heart.\n\n"
            "I wrote Aloha Wellness because I believe the body, the spirit, and the Kingdom "
            "are not separate things. True wellness flows from living under the reign of God — "
            "eating, resting, and moving in covenant rhythm rather than the world's anxious pace.\n\n"
            "If that resonates with you, I would love for you to take a look:\n\n"
            "https://keaupuniakeakua.faith/aloha-wellness\n\n"
            "No pressure. Just an invitation.\n\n"
            "Mahalo for walking this road with us.\n\n"
            "Kahu Phil Stephens\n"
            "keaupuniakeakua.faith\n\n"
            "--\n"
            f"{_unsubscribe_footer_plain(email)}"
        )
        msg = MIMEText(body, "plain")
        msg["Subject"] = "Wellness from the inside out — Aloha Wellness"
        msg["From"] = "kahuphil@keaupuni.faith"
        msg["To"] = email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"[followup-day7] Day-7 email sent to {email}", flush=True)
        _mark_subscriber_fields(email, day7_sent=True)
        _append_sheet_event(name, email, SHEET_EVENT_DAY7_SENT, datetime.now(timezone.utc).isoformat())
    except Exception as e:
        print(f"[followup-day7] FAILED for {email}: {e}", flush=True)


# ---------------------------------------------------------------------------
# Follow-up scheduling -- also re-run once at process startup (bottom of
# this file) so an in-memory threading.Timer lost to a restart is
# recomputed from the persisted subscriber record instead of silently
# dropped forever. Never re-sends a follow-up already marked sent, and
# never sends to an unsubscribed address (checked again, fresh, inside
# _send_followup_day3/_send_followup_day7 themselves).
# ---------------------------------------------------------------------------

def _schedule_followups(email, name, signup_time):
    subscribers = _load_subscribers()
    sub = _find_subscriber(subscribers, email) or {}
    if sub.get("unsubscribed"):
        return
    elapsed = (datetime.now(timezone.utc) - signup_time).total_seconds()
    for delay_seconds, sent_field, sender in (
        (DAY3_SECONDS, "day3_sent", _send_followup_day3),
        (DAY7_SECONDS, "day7_sent", _send_followup_day7),
    ):
        if sub.get(sent_field):
            continue
        remaining = delay_seconds - elapsed
        if remaining <= 0:
            sender(email, name)
        else:
            Timer(remaining, sender, args=[email, name]).start()


# ---------------------------------------------------------------------------
# Google Sheets integration -- the one durable, cross-redeploy record
# ---------------------------------------------------------------------------
#
# data/subscribers.json lives on Render's ephemeral filesystem (no `disk:`
# section in render.yaml) -- it is not guaranteed to survive a fresh
# deploy. Google Sheets, already integrated here (optional, only runs if
# GOOGLE_CREDENTIALS_JSON is set), is the one existing, no-new-cost
# capability that does. Extended from a write-only signup log into a real,
# append-only EVENT log -- same column shape, the "Website Signup" label
# generalized into an event_type column that now also carries
# "Unsubscribed"/"Day3 Sent"/"Day7 Sent" -- so a wiped local file can be
# fully reconstructed. This matters beyond convenience: recovering only
# the original signup fact and forgetting a real unsubscribe would resume
# mailing someone who opted out, a real compliance regression this must
# not introduce. Entirely inert (identical to the prior behavior) when
# GOOGLE_CREDENTIALS_JSON is unset.

SHEET_EVENT_SIGNUP = "Website Signup"
SHEET_EVENT_UNSUBSCRIBED = "Unsubscribed"
SHEET_EVENT_DAY3_SENT = "Day3 Sent"
SHEET_EVENT_DAY7_SENT = "Day7 Sent"


def _open_sheet():
    """Returns the real gspread Worksheet, or None if not configured or
    unreachable. Never raises -- every caller already treats a Sheets
    outage as non-fatal, the same discipline this file already applies
    to an SMTP outage."""
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")
    if not creds_json:
        return None
    try:
        from google.oauth2.service_account import Credentials
        import gspread

        creds = Credentials.from_service_account_info(
            json.loads(creds_json),
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        client = gspread.authorize(creds)
        return client.open("Ke Aupuni Leads").sheet1
    except Exception as e:
        print(f"[sheets] Could not open sheet: {type(e).__name__}: {e}", flush=True)
        return None


def _append_sheet_event(name, email, event_type, timestamp):
    sheet = _open_sheet()
    if sheet is None:
        return
    try:
        sheet.append_row([name, email, event_type, timestamp])
        print(f"[sheets] {event_type} row appended for {email}", flush=True)
    except Exception as e:
        print(f"[sheets] FAILED to append {event_type} for {email}: {type(e).__name__}: {e}", flush=True)


def _append_to_sheet(name, email, timestamp):
    """Preserved name/signature -- the original signup-time call site."""
    _append_sheet_event(name, email, SHEET_EVENT_SIGNUP, timestamp)


def _read_sheet_state():
    """Reconstructs one record per email from the full event log. Returns
    {} if Sheets isn't configured or unreachable -- callers must treat
    that exactly like "nothing to reconcile", never like "everyone
    unsubscribed"."""
    sheet = _open_sheet()
    if sheet is None:
        return {}
    try:
        rows = sheet.get_all_values()
    except Exception as e:
        print(f"[sheets] FAILED to read sheet: {type(e).__name__}: {e}", flush=True)
        return {}
    state = {}
    for row in rows:
        if len(row) < 4:
            continue
        name, raw_email, event_type, timestamp = row[0], row[1], row[2], row[3]
        email = raw_email.strip().lower()
        if not email or "@" not in email:
            continue
        rec = state.setdefault(email, {"email": email, "first_name": name, "source": "footer_signup"})
        if event_type == SHEET_EVENT_SIGNUP and "timestamp" not in rec:
            rec["timestamp"] = timestamp
        elif event_type == SHEET_EVENT_UNSUBSCRIBED:
            rec["unsubscribed"] = True
        elif event_type == SHEET_EVENT_DAY3_SENT:
            rec["day3_sent"] = True
        elif event_type == SHEET_EVENT_DAY7_SENT:
            rec["day7_sent"] = True
    return state


def _reconcile_subscribers_from_sheet():
    """Merges the Sheet's durable event history into the local (possibly
    just-wiped-by-a-redeploy) subscriber file. Boolean flags are OR-merged
    -- once true anywhere, true everywhere -- so a redeploy can never
    silently resurrect an unsubscribed contact. A correct no-op whenever
    Sheets isn't configured (_read_sheet_state() returns {})."""
    sheet_state = _read_sheet_state()
    if not sheet_state:
        return
    subscribers = _load_subscribers()
    by_email = {s["email"]: s for s in subscribers if s.get("email")}
    changed = False
    for email, sheet_rec in sheet_state.items():
        local = by_email.get(email)
        if local is None:
            subscribers.append(sheet_rec)
            by_email[email] = sheet_rec
            changed = True
            continue
        for flag in ("unsubscribed", "day3_sent", "day7_sent"):
            if sheet_rec.get(flag) and not local.get(flag):
                local[flag] = True
                changed = True
        if not local.get("timestamp") and sheet_rec.get("timestamp"):
            local["timestamp"] = sheet_rec["timestamp"]
            changed = True
    if changed:
        _save_subscribers(subscribers)
        print("[sheets] Reconciled local subscriber state from the durable event log", flush=True)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@downloads_bp.app_errorhandler(429)
def ratelimit_exceeded(e):
    return redirect("/")


@downloads_bp.route("/subscribe", methods=["POST"])
@limiter.limit("3 per hour")
def subscribe():
    if not request.headers.get("User-Agent", "").strip():
        return redirect("/")
    if request.form.get("website"):
        return redirect("/")

    first_name = request.form.get("first_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    if not email or not _valid_email(email):
        return redirect("/")

    print(f"[subscribe] New signup attempt — email={email} name={first_name}", flush=True)

    subscribers = _load_subscribers()
    if not any(s["email"] == email for s in subscribers):
        now = datetime.now(timezone.utc)
        subscribers.append({
            "first_name": first_name,
            "email": email,
            "source": "footer_signup",
            "timestamp": now.isoformat(),
        })
        _save_subscribers(subscribers)
        print(f"[subscribe] Saved — {len(subscribers)} total subscriber(s)", flush=True)
        # ISO format, not a human-readable string -- _reconcile_subscribers_from_sheet()
        # must be able to datetime.fromisoformat() this back on recovery.
        _append_to_sheet(first_name, email, now.isoformat())
        _notify_new_subscriber(email, first_name)
        _send_welcome_email(email, first_name)
        _schedule_followups(email, first_name, now)
        print(f"[followup] Scheduled day-3 and day-7 emails for {email}", flush=True)

    return redirect(f"/thank-you?name={quote(first_name)}")


@downloads_bp.route("/unsubscribe/<token>")
def unsubscribe(token):
    email, reason = unsubscribe_tokens.resolve_unsubscribe_token(token)
    if email is None:
        return "This unsubscribe link is invalid or no longer usable.", 400
    now = datetime.now(timezone.utc)
    sub = _find_subscriber(_load_subscribers(), email)
    _mark_subscriber_fields(email, unsubscribed=True, unsubscribed_at=now.isoformat())
    _append_sheet_event((sub or {}).get("first_name", ""), email, SHEET_EVENT_UNSUBSCRIBED, now.isoformat())
    print(f"[unsubscribe] {email} unsubscribed", flush=True)
    return f"{email} has been unsubscribed. You will not receive further automated emails from this list."


@downloads_bp.route("/thank-you")
def thank_you():
    name = request.args.get("name", "").strip()
    return render_template(
        "thank_you.html",
        name=name,
        logo_path=LOGO_PATH,
        logo_height=LOGO_HEIGHT,
        footer_text=FOOTER_TEXT,
    )


@downloads_bp.route("/download/aloha_wellness_freebie", methods=["GET", "POST"])
@limiter.limit("3 per hour")
def aloha_wellness_freebie():
    if not request.headers.get("User-Agent", "").strip():
        return redirect("/")
    if request.method == "POST":
        if request.form.get("website"):
            return redirect("/")
        email = request.form.get("email", "").strip().lower()
        if email and not _valid_email(email):
            return redirect("/")
        if email:
            subscribers = _load_subscribers()
            if not any(s["email"] == email for s in subscribers):
                subscribers.append({
                    "email": email,
                    "source": "aloha_wellness",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                _save_subscribers(subscribers)
                _notify_new_subscriber(email)
    return _send(BASE / "static" / "Aloha_Wellness_Free_Guide.pdf")


@downloads_bp.route("/download/pamphlet1")
def pamphlet1():
    return _send(BASE / "Kingdom_Keys_1_Kingdom_Inside_You.pdf")

@downloads_bp.route("/download/pamphlet2")
def pamphlet2():
    return _send(BASE / "Kingdom_Keys_2_Release_Healing.pdf")

@downloads_bp.route("/download/pamphlet3")
def pamphlet3():
    return _send(BASE / "Kingdom_Keys_3_Hawaiian_Grandmas_Prayers.pdf")

@downloads_bp.route("/download/pamphlet4")
def pamphlet4():
    return _send(BASE / "Kingdom_Keys_4_Kingdom_Wealth.pdf")

@downloads_bp.route("/download/booklet1")
def booklet1():
    return _send(BASE / "Free_Booklet_1_Kingdom_Wealth.pdf")

@downloads_bp.route("/download/booklet2")
def booklet2():
    return _send(BASE / "Free_Booklet_2_Kingdom_Wealth_Couples.pdf")

@downloads_bp.route("/download/booklet3")
def booklet3():
    return _send(BASE / "Free_Booklet_3_Kingdom_Wellness.pdf")

@downloads_bp.route("/download/booklet4")
def booklet4():
    return _send(BASE / "Free_Booklet_4_Kingdom_Wellness_Couples.pdf")

@downloads_bp.route("/download/booklet5")
def booklet5():
    return _send(BASE / "Free_Booklet_5_Kingdom_Living.pdf")

@downloads_bp.route("/download/booklet6")
def booklet6():
    return _send(BASE / "Free_Booklet_6_Kingdom_Living_Couples.pdf")

@downloads_bp.route("/download/kingdom_is_here")
def kingdom_is_here():
    return _send(BASE / "Kingdom_Is_Here_Booklet1.pdf")

@downloads_bp.route("/download/kingdom_wealth_booklet")
def kingdom_wealth_booklet():
    return _send(BASE / "Kingdom_Wealth_Booklet2.pdf")

@downloads_bp.route("/static/covers/<filename>")
def serve_cover(filename):
    cover_path = BASE / "static" / "covers" / filename
    if cover_path.exists():
        return send_file(cover_path, mimetype="image/jpeg")
    abort(404)


def _send(path):
    if not path.exists():
        abort(404)
    return send_file(path, mimetype="application/pdf", as_attachment=True)


# ---------------------------------------------------------------------------
# Startup recovery -- an in-memory threading.Timer scheduled by
# _schedule_followups() above is lost on every process restart (Render's
# web dynos restart periodically even without a fresh deploy). Recompute
# each still-pending day-3/day-7 follow-up from the one persisted record
# instead of silently losing it. Scoped to source == "footer_signup" only,
# matching exactly what _schedule_followups() was already scheduling
# before this fix -- aloha_wellness_freebie signups never had a day-3/
# day-7 follow-up scheduled in the first place, and this recovery pass
# must not start sending them one now.
#
# This recovers a follow-up across an ordinary process restart using the
# local file alone. Surviving a full redeploy (render.yaml has no `disk:`
# section, so data/subscribers.json itself is not guaranteed to survive
# one) additionally requires _reconcile_subscribers_from_sheet() (above)
# to have already rebuilt the local file from the durable Google Sheets
# event log -- which only happens if GOOGLE_CREDENTIALS_JSON is
# configured. Without it, this recovers a restart only, not a redeploy;
# a real, separate, cost-bearing decision (a paid persistent disk) would
# be the only other way to close that remaining gap.
# ---------------------------------------------------------------------------

def _recover_pending_followups():
    for sub in _load_subscribers():
        if sub.get("source") != "footer_signup" or sub.get("unsubscribed"):
            continue
        try:
            signup_time = datetime.fromisoformat(sub["timestamp"])
        except (KeyError, ValueError):
            continue
        _schedule_followups(sub["email"], sub.get("first_name", ""), signup_time)


_reconcile_subscribers_from_sheet()
_recover_pending_followups()
