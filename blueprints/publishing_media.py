# blueprints/publishing_media.py
# =========================================================
# Serves approved Discovery Workforce campaign media (Shorts, campaign
# images) to Buffer/YouTube/Facebook over a stable HTTPS URL, gated by a
# signed, asset-bound, time-limited token (publishing_media_tokens.py) —
# never by a guessable filename or bare listing.
#
# This is a publishing-media bridge, not a public file library:
#   - Only files publish_media.py has copied in and recorded in
#     PUBLISHING_MEDIA_MANIFEST_FILE are ever served.
#   - The URL path takes an asset_id, never a filename or path — the real
#     on-disk filename is looked up server-side from the manifest, so a
#     request can never name an arbitrary path.
#   - The resolved path is re-verified to stay inside PUBLISHING_MEDIA_DIR
#     before being served (defense in depth against a corrupted manifest
#     entry), and there is no route that lists the directory's contents.
# =========================================================

import json

from flask import Blueprint, abort, redirect, send_file

from config import PUBLISHING_MEDIA_DIR, PUBLISHING_MEDIA_MANIFEST_FILE
from publishing_media_tokens import generate_publishing_media_token, validate_publishing_media_token

publishing_media_bp = Blueprint("publishing_media", __name__)


def _load_manifest():
    if not PUBLISHING_MEDIA_MANIFEST_FILE.exists():
        return {}
    try:
        return json.loads(PUBLISHING_MEDIA_MANIFEST_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


@publishing_media_bp.route("/publishing-media/<asset_id>/<token>")
def serve_publishing_media(asset_id, token):
    ok, reason = validate_publishing_media_token(asset_id, token)
    if not ok:
        # Same fail-closed convention as /download/product/<id>/<token>:
        # "not_configured" is a server misconfiguration (missing
        # DOWNLOAD_TOKEN_SECRET) -> 503; everything else (expired,
        # invalid, wrong asset) -> 403, and deliberately not distinguished
        # further so a forged-token attempt can't be fingerprinted.
        abort(503 if reason == "not_configured" else 403)

    manifest = _load_manifest()
    entry = manifest.get(asset_id)
    if not entry:
        abort(404)

    file_path = (PUBLISHING_MEDIA_DIR / entry["filename"]).resolve()
    real_dir = PUBLISHING_MEDIA_DIR.resolve()
    if real_dir != file_path.parent:
        # The manifest should never point outside its own directory —
        # if it somehow does, refuse rather than serve it.
        abort(404)
    if not file_path.is_file():
        abort(404)

    return send_file(file_path, mimetype=entry.get("mimetype", "application/octet-stream"))


@publishing_media_bp.route("/media/<safe_asset_id>")
def evergreen_media_link(safe_asset_id):
    """A permanent public link for an already-approved, freely-released
    asset (e.g. a free campaign workbook) -- mints a fresh
    publishing-media token on every request and redirects to the
    existing signed route above, so a link embedded in a public page
    never goes stale even though each individual signed URL expires
    after TOKEN_MAX_AGE_SECONDS (14 days). Buffer/platform fetches keep
    using the directly-minted, short-lived URL from publish_media.py --
    this route exists only for assets meant to stay public indefinitely."""
    manifest = _load_manifest()
    if safe_asset_id not in manifest:
        abort(404)
    token = generate_publishing_media_token(safe_asset_id)
    if token is None:
        abort(503)
    return redirect(f"/publishing-media/{safe_asset_id}/{token}")
