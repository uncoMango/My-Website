# sale_alerts.py
# =========================================================
# Phone messages (ntfy) for the owner about real sales and about delivery problems (2026-10-21).
#
# Turn on by setting ONE environment variable on Render: SALE_ALERT_NTFY_TOPIC (the topic name the owner already
# subscribes to in the ntfy app). Optional: SALE_ALERT_NTFY_SERVER (default https://ntfy.sh).
# With no topic set, nothing is sent and /health/sales says so (so the gap is seen, not silent).
#
# Rules: never raises, never delays the buyer more than a few seconds, never puts a key or the buyer's email in a message.
# =========================================================
import json
import os
import urllib.request
from datetime import datetime, timezone

from config import PERSISTENT_DIR

SENT_FILE = PERSISTENT_DIR / "sale_alerts_sent.json"


def _topic():
    return os.environ.get("SALE_ALERT_NTFY_TOPIC", "").strip()


def _server():
    return os.environ.get("SALE_ALERT_NTFY_SERVER", "https://ntfy.sh").strip().rstrip("/")


def configured():
    return bool(_topic())


def _ascii(text):
    return text.encode("ascii", "ignore").decode("ascii")[:120]


def send(title, body, urgent=False, *, post=None):
    """Send one phone message. Returns True if it was handed to the alert service. Never raises."""
    topic = _topic()
    if not topic:
        print(f"[sale-alert] NOT SENT (no SALE_ALERT_NTFY_TOPIC set): {_ascii(title)}", flush=True)
        return False
    try:
        headers = {
            "Title": _ascii(title),
            "Priority": "urgent" if urgent else "default",
            "Tags": "rotating_light" if urgent else "moneybag",
        }
        if post is None:
            request = urllib.request.Request(f"{_server()}/{topic}", data=body.encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(request, timeout=5) as response:
                return 200 <= response.status < 300
        return bool(post(f"{_server()}/{topic}", body, headers))
    except Exception as exc:  # noqa: BLE001 - an alert problem must never touch the payment flow
        print(f"[sale-alert] send failed: {type(exc).__name__}", flush=True)
        return False


def once(key):
    """True the first time this key is seen (and remembers it); False afterwards. Fails open: if the record cannot be read or
    written, the answer is True, so a real sale is never silenced."""
    try:
        try:
            seen = json.loads(SENT_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            seen = {}
        if key in seen:
            return False
        seen[key] = datetime.now(timezone.utc).isoformat()
        SENT_FILE.write_text(json.dumps(seen), encoding="utf-8")
        return True
    except Exception:  # noqa: BLE001
        return True


def sale(product_name, amount, method, order_id, ready, reason=""):
    """One message for a verified payment, saying whether the buyer can get the file."""
    short = str(order_id)[-8:]
    if ready:
        return send(f"SALE: {product_name} ${amount:.2f}",
                    f"Paid by {method}. Buyer's download link: READY. Order ...{short}. Buyer details are in your sale email and {method}.")
    return send(f"FIX NOW: paid but NO file for {product_name}",
                f"A buyer paid ${amount:.2f} by {method} but the download is NOT ready ({reason}). Order ...{short}. "
                f"Look up the buyer in {method} and send them the file by hand.", urgent=True)


def delivered(product_name, order_id):
    return send(f"DELIVERED: {product_name}", f"The buyer opened their download. Order ...{str(order_id)[-8:]}.")


def delivery_failed(product_name, order_id, reason):
    return send(f"FIX NOW: download failed ({product_name})",
                f"A buyer tried to download but it failed ({reason}). Order ...{str(order_id)[-8:]}. Send them the file by hand.",
                urgent=True)
