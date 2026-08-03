# publish_media.py
# =========================================================
# CLI bridge the Discovery Workforce's Publishing Department uses to move
# an already-approved, already-produced campaign asset (a Short's .mp4,
# a campaign image) from the Discovery Engine workspace into this
# repository's dedicated publishing_media/ directory, so
# blueprints/publishing_media.py can serve it to Buffer over a stable,
# signed HTTPS URL.
#
# Must be run in an environment where DOWNLOAD_TOKEN_SECRET is set to the
# same value the deployed app uses — the token this prints is only valid
# against that real, live secret. Never invoked with any other secret.
#
# This app has no persistent disk or object storage — the git repo itself
# is the deploy artifact (same as digital_products/). `register` therefore
# runs locally, during the same authorized engineering session that
# commits/pushes/deploys the rest of a campaign's changes — never as a
# separate post-deploy step. Its output (the copied file plus the updated
# manifest.json) must be committed like any other real content change.
#
# Retention/cleanup policy (requirement: never delete before verification):
#   - `register` copies a file in and mints its token. Nothing is ever
#     deleted by `register`.
#   - `mark-verified` records that Publication Verification independently
#     confirmed the asset is genuinely live on its destination platform.
#   - `cleanup` removes only entries already marked verified, and only
#     once at least CLEANUP_GRACE_DAYS have passed since verification —
#     giving the destination platform (and any retry) ample time to have
#     already fetched the file. An unverified entry is never removed by
#     `cleanup`, no matter how old. Like `register`, its result (deleted
#     file, updated manifest) only takes effect live once committed,
#     pushed, and deployed — same as removing any other tracked file.
#
# Usage:
#   python publish_media.py register <asset_id> <source_path> <mimetype> [campaign_id]
#   python publish_media.py build-url <asset_id>     # re-mint a URL for an
#                                                     # already-registered asset;
#                                                     # needs DOWNLOAD_TOKEN_SECRET
#   python publish_media.py mark-verified <asset_id>
#   python publish_media.py cleanup
# =========================================================

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from config import PUBLISHING_MEDIA_DIR, PUBLISHING_MEDIA_MANIFEST_FILE, SITE_DOMAIN
from publishing_media_tokens import generate_publishing_media_token

CLEANUP_GRACE_DAYS = 7

_EXTENSION_BY_MIMETYPE = {
    "video/mp4": ".mp4",
    "image/jpeg": ".jpg",
    "image/png": ".png",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_id(asset_id: str) -> str:
    """Discovery Engine asset IDs (e.g.
    'campaign_001:planning_document:short_01:v2') contain ':', which
    Windows forbids in filenames and which is needlessly awkward in a
    URL path segment. This is the one place that mapping happens — the
    same safe form is used as the manifest key, the stored filename, and
    the public URL's asset_id segment, so there is never a second,
    diverging id to keep in sync."""
    return asset_id.replace(":", "_")


def load_manifest() -> dict:
    if not PUBLISHING_MEDIA_MANIFEST_FILE.exists():
        return {}
    try:
        return json.loads(PUBLISHING_MEDIA_MANIFEST_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_manifest(manifest: dict) -> None:
    PUBLISHING_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    PUBLISHING_MEDIA_MANIFEST_FILE.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def copy_asset_into_media_dir(
    asset_id: str, source_path: Path, mimetype: str, campaign_id: str | None = None,
) -> str:
    """Copies source_path in (skipping the copy if an identical-hash file
    is already registered under this asset_id — never duplicates
    unnecessarily) and records it in the manifest. Returns the safe_id
    used as the manifest key/filename stem. Needs no secret — this is
    the part of publishing that is pure file/manifest bookkeeping and can
    run in any local engineering session, well before deploy."""
    if not source_path.is_file():
        raise FileNotFoundError(f"source file does not exist: {source_path}")

    sid = safe_id(asset_id)
    content_hash = _hash_file(source_path)
    manifest = load_manifest()
    existing = manifest.get(sid)

    extension = _EXTENSION_BY_MIMETYPE.get(mimetype, source_path.suffix or "")
    filename = f"{sid}{extension}"

    if not (existing and existing.get("content_hash") == content_hash):
        PUBLISHING_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, PUBLISHING_MEDIA_DIR / filename)
        manifest[sid] = {
            "asset_id": asset_id,
            "filename": filename,
            "campaign_id": campaign_id,
            "mimetype": mimetype,
            "content_hash": content_hash,
            "added_at": _now_iso(),
            "verified": False,
            "verified_at": None,
        }
        save_manifest(manifest)

    return sid


def build_public_url(asset_id: str) -> str:
    """Mints the full signed public URL for an already-registered
    asset_id. Requires DOWNLOAD_TOKEN_SECRET to match the real, deployed
    app's secret — this is the one step that genuinely needs to run
    wherever that secret is available (a local shell with it exported,
    or Render's own console), and can be re-run at any time to get a
    fresh, valid URL for an asset registered at any earlier time (the
    token is a pure function of the secret + asset id, not stored
    state). Raises ValueError if the secret isn't configured — never
    returns an unsigned or fabricated URL."""
    sid = safe_id(asset_id)
    token = generate_publishing_media_token(sid)
    if token is None:
        raise ValueError(
            "DOWNLOAD_TOKEN_SECRET is not set in this environment — refusing to "
            "produce an unsigned URL. Run this with the same DOWNLOAD_TOKEN_SECRET "
            "the deployed app uses."
        )
    return f"{SITE_DOMAIN}/publishing-media/{sid}/{token}"


def register(asset_id: str, source_path: Path, mimetype: str, campaign_id: str | None = None) -> str:
    """Convenience wrapper: copy_asset_into_media_dir() + build_public_url()
    in one call, kept for the CLI. Raises ValueError if
    DOWNLOAD_TOKEN_SECRET isn't configured — the copy/manifest write
    still happens (and is still committable) even when the URL can't
    yet be minted in this environment."""
    copy_asset_into_media_dir(asset_id, source_path, mimetype, campaign_id)
    return build_public_url(asset_id)


def mark_verified(asset_id: str) -> None:
    sid = safe_id(asset_id)
    manifest = load_manifest()
    if sid not in manifest:
        raise KeyError(f"no registered asset: {asset_id}")
    manifest[sid]["verified"] = True
    manifest[sid]["verified_at"] = _now_iso()
    save_manifest(manifest)


def cleanup() -> list[str]:
    """Removes only verified assets older than CLEANUP_GRACE_DAYS.
    Returns the list of asset_ids removed. Never touches an unverified
    entry, regardless of age."""
    manifest = load_manifest()
    cutoff = datetime.now(timezone.utc) - timedelta(days=CLEANUP_GRACE_DAYS)
    removed = []
    for asset_id, entry in list(manifest.items()):
        if not entry.get("verified"):
            continue
        verified_at = entry.get("verified_at")
        if not verified_at:
            continue
        if datetime.fromisoformat(verified_at) > cutoff:
            continue
        file_path = PUBLISHING_MEDIA_DIR / entry["filename"]
        file_path.unlink(missing_ok=True)
        del manifest[asset_id]
        removed.append(asset_id)
    if removed:
        save_manifest(manifest)
    return removed


def _main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    command = argv[0]
    if command == "register":
        asset_id, source_path, mimetype = argv[1], argv[2], argv[3]
        campaign_id = argv[4] if len(argv) > 4 else None
        url = register(asset_id, Path(source_path), mimetype, campaign_id)
        print(url)
        return 0
    if command == "build-url":
        print(build_public_url(argv[1]))
        return 0
    if command == "mark-verified":
        mark_verified(argv[1])
        print(f"marked verified: {argv[1]}")
        return 0
    if command == "cleanup":
        removed = cleanup()
        print(f"removed {len(removed)} verified, expired asset(s): {removed}")
        return 0
    print(f"unknown command: {command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
