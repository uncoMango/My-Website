# blueprints/downloads.py
import json
import smtplib
import threading
from datetime import datetime, timezone
from email.mime.text import MIMEText
from flask import Blueprint, send_file, abort, request, redirect, render_template, render_template_string
from config import BASE, EMAILS_FILE, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, NOTIFY_EMAIL

downloads_bp = Blueprint("downloads", __name__)

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

@downloads_bp.route("/download/aloha_wellness_freebie", methods=["GET", "POST"])
def aloha_wellness_freebie():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if email:
            subscribers = []
            if EMAILS_FILE.exists():
                subscribers = json.loads(EMAILS_FILE.read_text())
            if not any(s["email"] == email for s in subscribers):
                subscribers.append({
                    "email": email,
                    "source": "aloha_wellness",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                EMAILS_FILE.write_text(json.dumps(subscribers, indent=2))
                threading.Thread(target=_notify_new_subscriber, args=(email,)).start()
    return _send(BASE / "static" / "Aloha_Wellness_Free_Guide.pdf")


def _notify_new_subscriber(email, name=""):
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS]):
        print(
            f"[subscribe] SMTP not configured — skipping notification for {email}. "
            "Set SMTP_HOST, SMTP_USER, SMTP_PASS in Render environment.",
            flush=True,
        )
        return
    try:
        name_line = f"Name:  {name}\n" if name else ""
        msg = MIMEText(
            f"New subscriber:\n\n"
            f"{name_line}"
            f"Email: {email}\n"
            f"Time:  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
        )
        msg["Subject"] = f"New Subscriber: {name + ' — ' if name else ''}{email}"
        msg["From"] = SMTP_USER
        msg["To"] = NOTIFY_EMAIL
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
    except Exception as e:
        print(f"[subscribe] Email notification failed for {email}: {e}", flush=True)


@downloads_bp.route("/thank-you")
def thank_you():
    name = request.args.get("name", "").strip()
    return render_template("thank_you.html", name=name)


@downloads_bp.route("/subscribe", methods=["POST"])
def subscribe():
    first_name = request.form.get("first_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    if not email:
        return redirect(request.referrer or "/")

    subscribers = []
    if EMAILS_FILE.exists():
        try:
            subscribers = json.loads(EMAILS_FILE.read_text())
        except Exception:
            pass
    if not any(s["email"] == email for s in subscribers):
        subscribers.append({
            "first_name": first_name,
            "email": email,
            "source": "footer_signup",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        EMAILS_FILE.write_text(json.dumps(subscribers, indent=2))
        threading.Thread(target=_notify_new_subscriber, args=(email, first_name)).start()

    from urllib.parse import quote
    return redirect(f"/thank-you?name={quote(first_name)}")

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
