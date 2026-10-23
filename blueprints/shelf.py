# blueprints/shelf.py
# =========================================================
# The buyer's shelf page, its protected file downloads, and the locked door the Foreman uses to add things
# to every shelf. The rules for what is on a shelf live in shelf.py (top of that file).
# =========================================================

import hmac
import json

from flask import Blueprint, abort, jsonify, make_response, render_template, request, send_file

import config
import shelf
from config import FOOTER_TEXT, LOGO_HEIGHT, LOGO_PATH
from content import get_product_by_id
from download_tokens import validate_and_consume_token_ex
from limiter import limiter

shelf_bp = Blueprint("shelf", __name__)


def _private(response):
    """A shelf address is a private address: never indexed, never cached, never passed on in a Referer header."""
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@shelf_bp.route("/shelf/<token>")
def shelf_page(token):
    order_id, reason = shelf.order_from_token(token)
    if order_id is None:
        abort(503 if reason == "not_configured" else 404)
    product = get_product_by_id(shelf.PRODUCT_ID) or {}
    return _private(make_response(render_template(
        "shelf.html",
        shelf=shelf.build_shelf(order_id),
        product=product,
        logo_path=LOGO_PATH,
        logo_height=LOGO_HEIGHT,
        footer_text=FOOTER_TEXT,
    )))


@shelf_bp.route("/shelf/file/<item_id>/<token>")
def shelf_file(item_id, token):
    ok, reason, _order_id, _uses = validate_and_consume_token_ex("shelf:" + item_id, token)
    if not ok:
        abort(503 if reason == "not_configured" else 403)
    item = shelf.find_item(item_id)
    found = shelf.item_file(item) if item else None
    if not found or not found[0].is_file() or found[0].stat().st_size == 0:
        return ("We are sorry: that file could not be sent just now. Please try again in a little while.", 503)
    path, name, mimetype = found
    return _private(send_file(path, as_attachment=True, download_name=name, mimetype=mimetype))


# ---------------------------------------------------------------- the Foreman's door
def _authorised():
    if not config.SHELF_ADMIN_KEY:
        abort(503, "The shelf password is not set on the website (SHELF_ADMIN_KEY).")
    header = request.headers.get("Authorization", "")
    given = header[7:] if header.lower().startswith("bearer ") else ""
    if not hmac.compare_digest(given.encode(), config.SHELF_ADMIN_KEY.encode()):
        abort(401)


def _meta_from_request():
    """Fields come from a JSON body, or from a multipart form with a `meta` JSON field plus an optional `file`."""
    if request.files or request.form:
        try:
            meta = json.loads(request.form.get("meta", "{}"))
        except ValueError:
            raise shelf.ShelfError("meta must be valid JSON")
        return meta, request.files.get("file")
    return (request.get_json(silent=True) or {}), None


@shelf_bp.route("/api/shelf/items", methods=["GET"])
@limiter.limit("120 per minute")
def api_list_items():
    _authorised()
    return jsonify({"items": [{k: v for k, v in i.items() if not k.startswith("_")} for i in shelf.merged_items()]})


@shelf_bp.route("/api/shelf/items/<item_id>", methods=["PUT"])
@limiter.limit("60 per minute")
def api_put_item(item_id):
    _authorised()
    if request.content_length and request.content_length > shelf.MAX_UPLOAD_BYTES + 1024 * 1024:
        return jsonify({"error": "request is larger than 25 MB"}), 413
    try:
        meta, upload = _meta_from_request()
        stored = shelf.put_item(item_id, meta, upload)
    except shelf.ShelfError as exc:
        return jsonify({"error": str(exc)}), 400
    except OSError as exc:
        return jsonify({"error": "could not save: " + type(exc).__name__}), 500
    return jsonify({"ok": True, "item": stored})


@shelf_bp.route("/api/shelf/items/<item_id>", methods=["DELETE"])
@limiter.limit("60 per minute")
def api_delete_item(item_id):
    _authorised()
    if not shelf.remove_item(item_id):
        return jsonify({"error": "no such item"}), 404
    return jsonify({"ok": True})


@shelf_bp.route("/api/shelf/buyers", methods=["GET"])
@limiter.limit("60 per minute")
def api_buyers():
    """Every buyer, with the private shelf address to put in the 'new chapter is on your shelf' email."""
    _authorised()
    rows = []
    for order_id, row in shelf.buyers().items():
        path = shelf.shelf_path(order_id)
        rows.append({"order_id": order_id, "email": row.get("email", ""), "name": row.get("name", ""),
                     "bought_at": row.get("bought_at", ""), "shelf_url": (config.SITE_DOMAIN + path) if path else ""})
    return jsonify({"buyers": rows})


@shelf_bp.route("/api/shelf/revoke", methods=["POST"])
@limiter.limit("30 per minute")
def api_revoke():
    _authorised()
    order_id = str((request.get_json(silent=True) or {}).get("order_id", "")).strip()
    if not order_id:
        return jsonify({"error": "order_id is required"}), 400
    shelf.revoke(order_id)
    return jsonify({"ok": True})
