# blueprints/downloads.py
import json
import os
import smtplib
import threading
from datetime import datetime, timezone
from urllib.parse import quote
from email.mime.text import MIMEText
from flask import Blueprint, send_file, abort, request, redirect, render_template
from config import BASE, EMAILS_FILE, SUBSCRIBERS_FILE, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, NOTIFY_EMAIL
from limiter import limiter

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


def _send_welcome_email(email, name=""):
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS]):
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
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS]):
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
            "keaupuniakeakua.faith"
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
    except Exception as e:
        print(f"[followup-day3] FAILED for {email}: {e}", flush=True)


def _send_followup_day7(email, name=""):
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS]):
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
            "keaupuniakeakua.faith"
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
    except Exception as e:
        print(f"[followup-day7] FAILED for {email}: {e}", flush=True)


# ---------------------------------------------------------------------------
# Google Sheets integration
# ---------------------------------------------------------------------------

def _append_to_sheet(name, email, timestamp):
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")
    if not creds_json:
        return
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
        sheet = client.open("Ke Aupuni Leads").sheet1
        row = [name, email, "Website Signup", timestamp]
        sheet.append_row(row)
        print(f"[sheets] Row appended for {email}", flush=True)
    except Exception as e:
        print(f"[sheets] FAILED for {email}: {type(e).__name__}: {e}", flush=True)


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
        subscribers.append({
            "first_name": first_name,
            "email": email,
            "source": "footer_signup",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        _save_subscribers(subscribers)
        print(f"[subscribe] Saved — {len(subscribers)} total subscriber(s)", flush=True)
        _append_to_sheet(first_name, email, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
        _notify_new_subscriber(email, first_name)
        _send_welcome_email(email, first_name)
        threading.Timer(3 * 24 * 3600, _send_followup_day3, args=[email, first_name]).start()
        threading.Timer(7 * 24 * 3600, _send_followup_day7, args=[email, first_name]).start()
        print(f"[followup] Scheduled day-3 and day-7 emails for {email}", flush=True)

    return redirect(f"/thank-you?name={quote(first_name)}")


@downloads_bp.route("/thank-you")
def thank_you():
    name = request.args.get("name", "").strip()
    return render_template("thank_you.html", name=name)


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
    cover_path = BASE / filename
    if cover_path.exists():
        return send_file(cover_path, mimetype="image/jpeg")
    abort(404)


def _send(path):
    if not path.exists():
        abort(404)
    return send_file(path, mimetype="application/pdf", as_attachment=True)
