# shelf.py
# =========================================================
# The buyer's shelf (2026-10-23): one private page per buyer of the Rotten Fencepost Package that holds
# everything the package includes, and grows as the Foreman adds chapters, workbooks and videos.
#
# Two sources of shelf items, merged on every page view:
#   * shelf_seed/manifest.json   -- what ships with the website (day one). Part of the git checkout.
#   * <persistent disk>/shelf_live/manifest.json -- what the Foreman adds later through /api/shelf/...,
#     so a new chapter reaches every buyer (old and new) WITHOUT a website code change or redeploy.
#     Files the Foreman uploads live next to it in shelf_live/files/.
# A live item with the same id replaces the seed item; a live item {"id": ..., "hidden": true} hides one.
#
# The shelf link itself is a signed token that never expires (it carries only the order id), so a buyer
# keeps one address for good. Revoking one buyer is a line in shelf_live/revoked.json. Every file INSIDE
# the shelf is still served through the same short-lived, use-limited download token as every other
# paid download (download_tokens.py), minted fresh each time the shelf page is opened.
# =========================================================

import json
import os
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

from itsdangerous import BadSignature, URLSafeSerializer

import config
from download_tokens import generate_download_token

SEED_DIR = config.BASE / "shelf_seed"
LIVE_DIR = config.PERSISTENT_DIR / "shelf_live"

PRODUCT_ID = "prod_wyk_package"
_SALT = "buyer-shelf"
_LOCK = threading.Lock()

KINDS = ("chapter", "guide", "workbook", "video", "intro", "other")
ALLOWED_EXTENSIONS = {".pdf", ".epub", ".docx", ".mp3", ".m4a", ".png", ".jpg", ".jpeg"}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_MIMETYPES = {
    ".pdf": "application/pdf", ".epub": "application/epub+zip",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".mp3": "audio/mpeg", ".m4a": "audio/mp4", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
}


# ---------------------------------------------------------------- small file helpers
def _read_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _write_json(path, data):
    """Write to a temp file then swap it in, so a crash can never leave half a file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


# ---------------------------------------------------------------- the shelf link (never expires)
def _serializer():
    return URLSafeSerializer(config.DOWNLOAD_TOKEN_SECRET, salt=_SALT)


def make_shelf_token(order_id):
    """None when DOWNLOAD_TOKEN_SECRET is not set (fail closed, like every other download)."""
    if not config.DOWNLOAD_TOKEN_SECRET:
        return None
    return _serializer().dumps({"oid": str(order_id)})


def shelf_path(order_id):
    token = make_shelf_token(order_id)
    return f"/shelf/{token}" if token else None


def order_from_token(token):
    """(order_id, reason). reason: "" | "not_configured" | "invalid" | "revoked"."""
    if not config.DOWNLOAD_TOKEN_SECRET:
        return None, "not_configured"
    try:
        payload = _serializer().loads(token)
    except BadSignature:
        return None, "invalid"
    order_id = str(payload.get("oid", "")) if isinstance(payload, dict) else ""
    if not order_id:
        return None, "invalid"
    if order_id in set(_read_json(LIVE_DIR / "revoked.json", [])):
        return None, "revoked"
    return order_id, ""


def revoke(order_id):
    with _LOCK:
        revoked = _read_json(LIVE_DIR / "revoked.json", [])
        if str(order_id) not in revoked:
            revoked.append(str(order_id))
            _write_json(LIVE_DIR / "revoked.json", revoked)


# ---------------------------------------------------------------- who bought (so the Foreman can tell them)
def record_buyer(order_id, email="", name="", product_id=PRODUCT_ID):
    """Idempotent on order_id. A later call can fill in an email that was missing the first time."""
    if not order_id:
        return
    try:
        with _LOCK:
            buyers = _read_json(LIVE_DIR / "buyers.json", {})
            row = buyers.get(str(order_id))
            if row is None:
                buyers[str(order_id)] = {"email": (email or "").strip().lower(), "name": name or "", "product_id": product_id,
                                         "bought_at": datetime.now(timezone.utc).isoformat()}
            elif email and not row.get("email"):
                row["email"] = email.strip().lower()
                row["name"] = row.get("name") or name or ""
            else:
                return
            _write_json(LIVE_DIR / "buyers.json", buyers)
    except OSError:
        pass  # never fail the payment flow over a bookkeeping write


def buyers():
    return _read_json(LIVE_DIR / "buyers.json", {})


# ---------------------------------------------------------------- the items
def _seed_items():
    return _read_json(SEED_DIR / "manifest.json", {}).get("items", [])


def _live_items():
    return _read_json(LIVE_DIR / "manifest.json", {}).get("items", [])


def merged_items():
    """Seed items, overridden / hidden / extended by live items. Order of first appearance is kept."""
    by_id, order = {}, []
    for origin, items in (("seed", _seed_items()), ("live", _live_items())):
        for item in items:
            item_id = item.get("id")
            if not item_id:
                continue
            if item_id not in by_id:
                order.append(item_id)
            by_id[item_id] = dict(item, _origin=origin)
    return [by_id[i] for i in order if not by_id[i].get("hidden")]


def item_count():
    return len(merged_items())


def find_item(item_id):
    return next((i for i in merged_items() if i.get("id") == item_id), None)


def item_file(item):
    """(Path, download_name, mimetype) for an item that is a file, else None."""
    from content import get_product_by_id
    if item.get("product"):
        product = get_product_by_id(item["product"])
        if product and product.get("file_path"):
            path = config.BASE / product["file_path"]
            return path, product.get("filename") or path.name, _MIMETYPES.get(path.suffix.lower(), "application/octet-stream")
        return None
    if item.get("file"):
        from_live = item["_origin"] == "live" and item.get("store") != "seed"
        root = (LIVE_DIR if from_live else SEED_DIR) / "files"
        path = (root / item["file"]).resolve()
        if root.resolve() not in path.parents:
            return None   # a manifest line can never point outside its own folder
        return path, path.name, _MIMETYPES.get(path.suffix.lower(), "application/octet-stream")
    return None


def _num(value, default=1000.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _campaigns_of(item):
    value = item.get("campaign")
    if not value:
        return []
    return [str(v) for v in value] if isinstance(value, list) else [str(value)]


def build_shelf(order_id):
    """What the shelf page shows for this buyer: sections of items, each with a link already
    signed for this buyer. Nothing here is a public address."""
    from content import get_campaign_by_id
    items = sorted(merged_items(), key=lambda i: (_num(i.get("order")), str(i.get("title", ""))))

    def view(item):
        link = None
        if item.get("url"):
            link = item["url"]
        elif item_file(item):
            token = generate_download_token("shelf:" + item["id"], order_id)
            link = f"/shelf/file/{item['id']}/{token}" if token else None
        return {"id": item["id"], "kind": item.get("kind", "other"), "title": item.get("title", ""),
                "subtitle": item.get("subtitle", ""), "label": item.get("label") or _default_label(item),
                "link": link, "external": bool(item.get("url")) and not str(item["url"]).startswith("/")}

    views = [(i, view(i)) for i in items]
    book = [v for i, v in views if i.get("kind") == "chapter"]
    guides = [v for i, v in views if i.get("kind") == "guide"]
    campaign_ids = sorted({c for i in items for c in _campaigns_of(i)})
    groups = []
    for cid in campaign_ids:
        campaign = get_campaign_by_id(cid) or {}
        members = [v for i, v in views if cid in _campaigns_of(i)]
        video = next((v for v in members if v["kind"] == "video"), None)
        rest = [v for v in members if v["kind"] != "video"]
        title = (campaign.get("title") or (video or {}).get("title") or "")
        groups.append({"id": cid, "title": title, "video": video, "rows": rest,
                       "page": f"/campaign/{cid}" if campaign else (video or {}).get("link")})
    placed = {v["id"] for g in groups for v in ([g["video"]] if g["video"] else []) + g["rows"]} | {v["id"] for v in book + guides}
    more = [v for i, v in views if v["id"] not in placed]
    return {"book": book, "guides": guides, "groups": groups, "more": more}


def _default_label(item):
    return {"chapter": "Download the chapter (PDF)", "workbook": "Download the workbook (PDF)", "video": "Watch the video",
            "intro": "Download the Introduction (PDF)", "guide": "Download the guide (PDF)"}.get(item.get("kind"), "Open")


# ---------------------------------------------------------------- changes by the Foreman
class ShelfError(ValueError):
    pass


def validate_meta(item_id, meta):
    if not _ID_RE.match(item_id or ""):
        raise ShelfError("item id must be lowercase letters, numbers, - or _ (1 to 64 characters)")
    kind = meta.get("kind")
    if kind not in KINDS:
        raise ShelfError("kind must be one of: " + ", ".join(KINDS))
    if not str(meta.get("title", "")).strip():
        raise ShelfError("title is required")
    clean = {"id": item_id, "kind": kind, "title": str(meta["title"]).strip()}
    for key in ("subtitle", "label"):
        if meta.get(key):
            clean[key] = str(meta[key]).strip()
    if meta.get("order") is not None:
        clean["order"] = _num(meta["order"], None)
        if clean["order"] is None:
            raise ShelfError("order must be a number")
    if meta.get("campaign"):
        value = meta["campaign"]
        values = value if isinstance(value, list) else [value]
        if not all(re.match(r"^\d{3}$", str(v)) for v in values):
            raise ShelfError("campaign must be a three-digit id like 005 (or a list of them)")
        clean["campaign"] = [str(v) for v in values] if isinstance(value, list) else str(value)
    if meta.get("url"):
        url = str(meta["url"])
        if not (url.startswith("/") and not url.startswith("//")) and not url.startswith("https://"):
            raise ShelfError("url must start with / (a page on this site) or https://")
        clean["url"] = url
    if meta.get("product"):
        from content import get_product_by_id
        if not get_product_by_id(str(meta["product"])):
            raise ShelfError("unknown product id")
        clean["product"] = str(meta["product"])
    if meta.get("added"):
        clean["added"] = str(meta["added"])[:40]
    return clean


def put_item(item_id, meta, upload=None):
    """Add or replace one live item. `upload` is a werkzeug FileStorage (or None). Returns the stored item."""
    clean = validate_meta(item_id, meta)
    with _LOCK:
        manifest = _read_json(LIVE_DIR / "manifest.json", {"items": []})
        items = manifest.setdefault("items", [])
        existing = next((i for i in items if i.get("id") == item_id), None)
        if upload is not None and upload.filename:
            ext = Path(upload.filename).suffix.lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise ShelfError("file type not allowed: " + ext)
            data = upload.read(MAX_UPLOAD_BYTES + 1)
            if len(data) > MAX_UPLOAD_BYTES:
                raise ShelfError("file is larger than 25 MB")
            if not data:
                raise ShelfError("file is empty")
            name = f"{item_id}{ext}"
            target = LIVE_DIR / "files" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_name(target.name + ".tmp")
            tmp.write_bytes(data)
            os.replace(tmp, target)
            clean["file"] = name
        elif existing and existing.get("file") and not (clean.get("url") or clean.get("product")):
            clean["file"] = existing["file"]
            if existing.get("store"):
                clean["store"] = existing["store"]
        sources = [k for k in ("file", "url", "product") if clean.get(k)]
        if not sources:
            # Changing only the words / order / campaign of a built-in item (for example adding campaign "005"
            # to Chapter 1): keep the built-in item's own file, url or product.
            seed = next((i for i in _seed_items() if i.get("id") == item_id), None)
            if seed:
                for k in ("file", "url", "product"):
                    if seed.get(k):
                        clean[k] = seed[k]
                        sources = [k]
                        if k == "file":
                            clean["store"] = "seed"
        if len(sources) != 1:
            raise ShelfError("give exactly one of: a file upload, url, or product")
        clean.setdefault("added", datetime.now(timezone.utc).date().isoformat())
        items[:]= [i for i in items if i.get("id") != item_id] + [clean]
        _write_json(LIVE_DIR / "manifest.json", manifest)
    return clean


def remove_item(item_id):
    """Take an item off every shelf. Live items are deleted; built-in items are hidden. Returns True if anything changed."""
    with _LOCK:
        manifest = _read_json(LIVE_DIR / "manifest.json", {"items": []})
        items = manifest.setdefault("items", [])
        live = next((i for i in items if i.get("id") == item_id), None)
        in_seed = any(i.get("id") == item_id for i in _seed_items())
        if not live and not in_seed:
            return False
        items[:] = [i for i in items if i.get("id") != item_id]
        if in_seed:
            items.append({"id": item_id, "hidden": True})
        _write_json(LIVE_DIR / "manifest.json", manifest)
        if live and live.get("file"):
            try:
                (LIVE_DIR / "files" / live["file"]).unlink()
            except OSError:
                pass
    return True
