# blueprints/downloads.py
import json
import os
import smtplib
from datetime import datetime, timezone
from urllib.parse import quote
from email.mime.text import MIMEText
from flask import Blueprint, send_file, abort, request, redirect, render_template
from config import BASE, EMAILS_FILE, SUBSCRIBERS_FILE, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, NOTIFY_EMAIL

downloads_bp = Blueprint("downloads", __name__)

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
    print(f"[notify] Attempting notification email → {NOTIFY_EMAIL}  (subscriber: {email})", flush=True)
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS]):
        print("[notify] SMTP not configured — set SMTP_HOST, SMTP_USER, SMTP_PASS in Render environment.", flush=True)
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
        print(f"[notify] Connecting to SMTP {SMTP_HOST}:{SMTP_PORT}", flush=True)
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            print("[notify] SMTP login success", flush=True)
            server.send_message(msg)
            print(f"[notify] Notification sent to {NOTIFY_EMAIL}", flush=True)
    except Exception as e:
        print(f"[notify] FAILED for {email}: {e}", flush=True)


def _send_welcome_email(email, name=""):
    print(f"[welcome] Attempting welcome email → {email}", flush=True)
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS]):
        print("[welcome] SMTP not configured — skipping welcome email.", flush=True)
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
        print(f"[welcome] Connecting to SMTP {SMTP_HOST}:{SMTP_PORT}", flush=True)
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            print("[welcome] SMTP login success", flush=True)
            server.send_message(msg)
            print(f"[welcome] Welcome email sent to {email}", flush=True)
    except Exception as e:
        print(f"[welcome] FAILED for {email}: {e}", flush=True)


# ---------------------------------------------------------------------------
# Google Sheets integration
# ---------------------------------------------------------------------------

def _append_to_sheet(name, email, timestamp):
    print(f"[sheets] >>> _append_to_sheet called for {email}", flush=True)
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")
    if not creds_json:
        print("[sheets] GOOGLE_CREDENTIALS_JSON is empty/missing — skipping.", flush=True)
        return
    print(f"[sheets] Credentials string found ({len(creds_json)} chars) — parsing JSON", flush=True)
    try:
        creds_dict = json.loads(creds_json)
        print(f"[sheets] Credentials parsed OK, project={creds_dict.get('project_id', '?')}", flush=True)
    except Exception as e:
        print(f"[sheets] FAILED to parse GOOGLE_CREDENTIALS_JSON: {e}", flush=True)
        return
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        print("[sheets] Credentials object created — authorizing gspread client", flush=True)
        client = gspread.authorize(creds)
        print("[sheets] gspread authorized — opening sheet 'Ke Aupuni Leads'", flush=True)
        sheet = client.open("Ke Aupuni Leads").sheet1
        print("[sheets] Sheet opened — appending row", flush=True)
        row = [name, email, "Website Signup", timestamp]
        sheet.append_row(row)
        print(f"[sheets] SUCCESS — row appended: {row}", flush=True)
    except Exception as e:
        print(f"[sheets] FAILED for {email}: {type(e).__name__}: {e}", flush=True)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@downloads_bp.route("/subscribe", methods=["POST"])
def subscribe():
    first_name = request.form.get("first_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    if not email:
        return redirect(request.referrer or "/")

    print(f"[subscribe] New signup attempt — email={email} name={first_name}", flush=True)

    subscribers = _load_subscribers()
    if any(s["email"] == email for s in subscribers):
        print(f"[subscribe] Duplicate — {email} already in subscribers.json", flush=True)
    else:
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

    return redirect(f"/thank-you?name={quote(first_name)}")


@downloads_bp.route("/thank-you")
def thank_you():
    name = request.args.get("name", "").strip()
    return render_template("thank_you.html", name=name)


@downloads_bp.route("/download/aloha_wellness_freebie", methods=["GET", "POST"])
def aloha_wellness_freebie():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
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
