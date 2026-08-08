# tests/test_publishing_media.py
# =========================================================
# Tests for the Discovery Workforce publishing-media bridge:
# publish_media.py (register/mark-verified/cleanup) and the
# GET /publishing-media/<asset_id>/<token> route.
#
# Covers:
#   - register() copies the file, mints a valid signed URL, and is
#     idempotent for an unchanged source file (no duplicate copy)
#   - a changed source file for the same asset_id re-copies (new content
#     hash) rather than silently reusing the stale file
#   - the route serves a registered asset for a valid token, and rejects
#     (403/404/503, never a file) every other case: wrong asset, tampered
#     token, unregistered asset_id, and a missing DOWNLOAD_TOKEN_SECRET
#   - the route never accepts a raw filename/path, only an asset_id
#     resolved through the manifest, and refuses to serve outside
#     PUBLISHING_MEDIA_DIR even if a manifest entry were corrupted
#   - cleanup() removes only verified + expired entries, never an
#     unverified one no matter how old
# =========================================================

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import config as config_module  # noqa: E402
import publish_media  # noqa: E402
import publishing_media_tokens  # noqa: E402
import app as app_module  # noqa: E402

TEST_SECRET = "test-only-publishing-media-secret-not-real"


@pytest.fixture
def media_env(tmp_path, monkeypatch):
    media_dir = tmp_path / "publishing_media"
    manifest_file = media_dir / "manifest.json"
    monkeypatch.setattr(config_module, "PUBLISHING_MEDIA_DIR", media_dir)
    monkeypatch.setattr(config_module, "PUBLISHING_MEDIA_MANIFEST_FILE", manifest_file)
    monkeypatch.setattr(publish_media, "PUBLISHING_MEDIA_DIR", media_dir)
    monkeypatch.setattr(publish_media, "PUBLISHING_MEDIA_MANIFEST_FILE", manifest_file)

    from blueprints import publishing_media as pm_blueprint
    monkeypatch.setattr(pm_blueprint, "PUBLISHING_MEDIA_DIR", media_dir)
    monkeypatch.setattr(pm_blueprint, "PUBLISHING_MEDIA_MANIFEST_FILE", manifest_file)

    monkeypatch.setattr(publishing_media_tokens, "DOWNLOAD_TOKEN_SECRET", TEST_SECRET)

    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    return {"media_dir": media_dir, "client": app_module.app.test_client()}


def _make_source(tmp_path, name="short_01.mp4", content=b"fake-mp4-bytes"):
    path = tmp_path / name
    path.write_bytes(content)
    return path


def test_register_copies_file_and_returns_valid_signed_url(tmp_path, media_env):
    source = _make_source(tmp_path)
    url = publish_media.register("campaign_001:short_01:v2", source, "video/mp4", "campaign_001")

    # ':' is unsafe in a Windows filename and awkward in a URL path segment —
    # register() maps it through safe_id() consistently everywhere.
    assert url == f"https://keaupuniakeakua.faith/publishing-media/campaign_001_short_01_v2/{url.rsplit('/', 1)[1]}"
    stored = media_env["media_dir"] / "campaign_001_short_01_v2.mp4"
    assert stored.exists()
    assert stored.read_bytes() == b"fake-mp4-bytes"


def test_register_is_idempotent_for_unchanged_source(tmp_path, media_env):
    source = _make_source(tmp_path)
    publish_media.register("short_01", source, "video/mp4")
    stored = media_env["media_dir"] / "short_01.mp4"
    first_mtime = stored.stat().st_mtime_ns

    publish_media.register("short_01", source, "video/mp4")
    assert stored.stat().st_mtime_ns == first_mtime  # never re-copied


def test_register_recopies_when_source_content_changes(tmp_path, media_env):
    source = _make_source(tmp_path, content=b"version-one")
    publish_media.register("short_01", source, "video/mp4")

    source.write_bytes(b"version-two-different-content")
    publish_media.register("short_01", source, "video/mp4")

    stored = media_env["media_dir"] / "short_01.mp4"
    assert stored.read_bytes() == b"version-two-different-content"


def test_register_raises_without_secret(tmp_path, media_env, monkeypatch):
    monkeypatch.setattr(publishing_media_tokens, "DOWNLOAD_TOKEN_SECRET", "")
    source = _make_source(tmp_path)
    with pytest.raises(ValueError):
        publish_media.register("short_01", source, "video/mp4")


def test_copy_asset_succeeds_without_secret_even_though_url_minting_needs_it(tmp_path, media_env, monkeypatch):
    """The file-copy/manifest step is pure bookkeeping and must work in
    any local engineering session — only building the actual signed URL
    requires the real, deployed DOWNLOAD_TOKEN_SECRET."""
    monkeypatch.setattr(publishing_media_tokens, "DOWNLOAD_TOKEN_SECRET", "")
    source = _make_source(tmp_path)

    sid = publish_media.copy_asset_into_media_dir("short_01", source, "video/mp4", "campaign_001")
    assert sid == "short_01"
    assert (media_env["media_dir"] / "short_01.mp4").exists()

    with pytest.raises(ValueError):
        publish_media.build_public_url("short_01")

    monkeypatch.setattr(publishing_media_tokens, "DOWNLOAD_TOKEN_SECRET", TEST_SECRET)
    url = publish_media.build_public_url("short_01")
    assert url.startswith("https://keaupuniakeakua.faith/publishing-media/short_01/")


def test_route_serves_registered_asset_with_valid_token(tmp_path, media_env):
    source = _make_source(tmp_path)
    url = publish_media.register("short_01", source, "video/mp4")
    path = url.replace("https://keaupuniakeakua.faith", "")

    resp = media_env["client"].get(path)
    assert resp.status_code == 200
    assert resp.data == b"fake-mp4-bytes"


def test_route_rejects_tampered_token(tmp_path, media_env):
    source = _make_source(tmp_path)
    url = publish_media.register("short_01", source, "video/mp4")
    path = url.replace("https://keaupuniakeakua.faith", "") + "tampered"

    resp = media_env["client"].get(path)
    assert resp.status_code == 403


def test_route_rejects_token_for_wrong_asset(tmp_path, media_env):
    source = _make_source(tmp_path)
    publish_media.register("short_01", source, "video/mp4")
    publish_media.register("short_02", source, "video/mp4")
    url_01 = f"https://keaupuniakeakua.faith/publishing-media/short_01/{publishing_media_tokens.generate_publishing_media_token('short_01')}"
    path_for_short_02 = url_01.replace("short_01", "short_02", 1).replace("https://keaupuniakeakua.faith", "")

    resp = media_env["client"].get(path_for_short_02)
    assert resp.status_code == 403


def test_route_404s_for_never_registered_asset(media_env):
    token = publishing_media_tokens.generate_publishing_media_token("never_registered")
    resp = media_env["client"].get(f"/publishing-media/never_registered/{token}")
    assert resp.status_code == 404


def test_route_503s_when_secret_not_configured(tmp_path, media_env, monkeypatch):
    source = _make_source(tmp_path)
    url = publish_media.register("short_01", source, "video/mp4")
    path = url.replace("https://keaupuniakeakua.faith", "")

    monkeypatch.setattr(publishing_media_tokens, "DOWNLOAD_TOKEN_SECRET", "")
    resp = media_env["client"].get(path)
    assert resp.status_code == 503


def test_route_refuses_manifest_entry_pointing_outside_media_dir(tmp_path, media_env):
    source = _make_source(tmp_path)
    publish_media.register("short_01", source, "video/mp4")

    manifest = publish_media.load_manifest()
    manifest["short_01"]["filename"] = "../../etc/passwd"
    publish_media.save_manifest(manifest)

    token = publishing_media_tokens.generate_publishing_media_token("short_01")
    resp = media_env["client"].get(f"/publishing-media/short_01/{token}")
    assert resp.status_code == 404


def test_cleanup_never_removes_unverified_entry_regardless_of_age(tmp_path, media_env):
    source = _make_source(tmp_path)
    publish_media.register("short_01", source, "video/mp4")
    manifest = publish_media.load_manifest()
    manifest["short_01"]["added_at"] = (datetime.now(timezone.utc) - timedelta(days=365)).isoformat()
    publish_media.save_manifest(manifest)

    removed = publish_media.cleanup()
    assert removed == []
    assert (media_env["media_dir"] / "short_01.mp4").exists()


def test_cleanup_removes_verified_entries_past_grace_period(tmp_path, media_env):
    source = _make_source(tmp_path)
    publish_media.register("short_01", source, "video/mp4")
    publish_media.mark_verified("short_01")
    manifest = publish_media.load_manifest()
    manifest["short_01"]["verified_at"] = (
        datetime.now(timezone.utc) - timedelta(days=publish_media.CLEANUP_GRACE_DAYS + 1)
    ).isoformat()
    publish_media.save_manifest(manifest)

    removed = publish_media.cleanup()
    assert removed == ["short_01"]
    assert not (media_env["media_dir"] / "short_01.mp4").exists()


def test_register_handles_real_discovery_engine_asset_id_format(tmp_path, media_env):
    """Real Discovery Engine asset_ids look like
    'campaign_001:planning_document:short_01:v2' — this must round-trip
    through register(), the manifest, and the live route without ever
    hitting an invalid-Windows-filename error."""
    source = _make_source(tmp_path)
    real_asset_id = "campaign_001:planning_document:short_01:v2"
    url = publish_media.register(real_asset_id, source, "video/mp4", "campaign_001")
    path = url.replace("https://keaupuniakeakua.faith", "")

    resp = media_env["client"].get(path)
    assert resp.status_code == 200
    assert resp.data == b"fake-mp4-bytes"

    manifest = publish_media.load_manifest()
    stored_entry = manifest[publish_media.safe_id(real_asset_id)]
    assert stored_entry["asset_id"] == real_asset_id  # original id preserved for Records/Verification


def test_resolve_all_urls_mints_one_url_per_manifest_entry_in_one_call(tmp_path, media_env):
    source1 = _make_source(tmp_path, name="a.mp4", content=b"content-a")
    source2 = _make_source(tmp_path, name="b.mp4", content=b"content-b")
    publish_media.copy_asset_into_media_dir("campaign_001:planning_document:short_01:v2", source1, "video/mp4", "campaign_001")
    publish_media.copy_asset_into_media_dir("campaign_001:planning_document:short_02:v2", source2, "video/mp4", "campaign_001")

    urls = publish_media.resolve_all_urls()

    assert set(urls.keys()) == {
        "campaign_001:planning_document:short_01:v2",
        "campaign_001:planning_document:short_02:v2",
    }
    for asset_id, url in urls.items():
        path = url.replace("https://keaupuniakeakua.faith", "")
        resp = media_env["client"].get(path)
        assert resp.status_code == 200


def test_resolve_all_urls_raises_without_secret(tmp_path, media_env, monkeypatch):
    source = _make_source(tmp_path)
    publish_media.copy_asset_into_media_dir("short_01", source, "video/mp4")
    monkeypatch.setattr(publishing_media_tokens, "DOWNLOAD_TOKEN_SECRET", "")
    with pytest.raises(ValueError):
        publish_media.resolve_all_urls()


# --- Evergreen public link (2026-08-07) -----------------------------------
# A signed /publishing-media/<id>/<token> URL expires after
# TOKEN_MAX_AGE_SECONDS (14 days) — fine for a Buffer/platform fetch, wrong
# for a link embedded permanently in a public page (e.g. a free workbook
# download). /media/<safe_asset_id> mints a fresh token per request and
# redirects, so the embedded link itself never goes stale.


def test_evergreen_link_redirects_to_a_working_signed_url(tmp_path, media_env):
    source = _make_source(tmp_path, name="workbook.pdf", content=b"fake-pdf-bytes")
    publish_media.copy_asset_into_media_dir("campaign_002:planning_document:workbook_pdf:v5", source, "application/pdf", "campaign_002")
    safe_id = publish_media.safe_id("campaign_002:planning_document:workbook_pdf:v5")

    resp = media_env["client"].get(f"/media/{safe_id}", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.location.startswith(f"/publishing-media/{safe_id}/")

    followed = media_env["client"].get(f"/media/{safe_id}", follow_redirects=True)
    assert followed.status_code == 200
    assert followed.data == b"fake-pdf-bytes"


def test_evergreen_link_mints_a_fresh_token_each_time(tmp_path, media_env):
    source = _make_source(tmp_path, name="workbook.pdf", content=b"fake-pdf-bytes")
    publish_media.copy_asset_into_media_dir("workbook_v5", source, "application/pdf")

    first = media_env["client"].get("/media/workbook_v5", follow_redirects=False)
    second = media_env["client"].get("/media/workbook_v5", follow_redirects=False)
    # Both work independently even though the token in the redirect differs
    # run to run (itsdangerous timestamps the payload) — the point is every
    # visit gets a currently-valid token, not a single baked-in one.
    for resp in (first, second):
        assert resp.status_code == 302
        followed = media_env["client"].get(resp.location)
        assert followed.status_code == 200


def test_evergreen_link_404s_for_unregistered_asset(media_env):
    resp = media_env["client"].get("/media/never_registered")
    assert resp.status_code == 404


def test_evergreen_link_503s_when_secret_not_configured(tmp_path, media_env, monkeypatch):
    source = _make_source(tmp_path, name="workbook.pdf", content=b"fake-pdf-bytes")
    publish_media.copy_asset_into_media_dir("workbook_v5", source, "application/pdf")
    monkeypatch.setattr(publishing_media_tokens, "DOWNLOAD_TOKEN_SECRET", "")

    resp = media_env["client"].get("/media/workbook_v5")
    assert resp.status_code == 503


def test_cleanup_keeps_verified_entries_still_within_grace_period(tmp_path, media_env):
    source = _make_source(tmp_path)
    publish_media.register("short_01", source, "video/mp4")
    publish_media.mark_verified("short_01")

    removed = publish_media.cleanup()
    assert removed == []
    assert (media_env["media_dir"] / "short_01.mp4").exists()
