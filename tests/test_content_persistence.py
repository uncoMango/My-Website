# tests/test_content_persistence.py
# =========================================================
# Regression tests for the admin-content persistence fix (2026-09-27).
#
# Root cause: content.py's load_content() always returned the hardcoded
# DEFAULT_PAGES dict, and save_content() was a no-op (`pass`). An admin
# edit through /kahu appeared to work within the same running process
# (Python dicts are mutable, so the in-memory object was actually changed
# in place) but vanished on any restart or redeploy, because nothing was
# ever written to disk and nothing was ever read back from it. See
# CLAUDE.md, Change Log, "2026-09-27 (Handoff Follow-Up...)".
#
# content.DATA_FILE (admin_content_overrides.json) is isolated to a
# per-test tmp_path by the autouse _isolate_admin_content fixture in
# tests/conftest.py, the same convention already used there for
# STRIPE_FULFILLED_SESSIONS_FILE and SUBSCRIBERS_FILE -- so these tests
# never read or write the real file, and never touch the pre-existing
# legacy website_content.json at all.
# =========================================================

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import auth  # noqa: E402
import config  # noqa: E402
import content as content_module  # noqa: E402
import app as app_module  # noqa: E402

TEST_PASSWORD = "test-only-password-not-real"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(auth, "ADMIN_PASSWORD", TEST_PASSWORD)
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


def _login(client, password=TEST_PASSWORD):
    return client.post("/kahu/login", data={"password": password}, follow_redirects=False)


# ---------------------------------------------------------------------------
# save_content() actually writes to disk; load_content() actually reads it
# back -- neither was true before this fix. content_module.DATA_FILE is
# already isolated to a tmp path by conftest.py's autouse fixture.
# ---------------------------------------------------------------------------

def test_save_content_persists_to_disk():
    assert not content_module.DATA_FILE.exists()
    content_module.save_content({"pages": {"home": {"title": "Saved Title"}}})
    assert content_module.DATA_FILE.exists()
    on_disk = json.loads(content_module.DATA_FILE.read_text(encoding="utf-8"))
    assert on_disk["pages"]["home"]["title"] == "Saved Title"


def test_load_content_reads_back_a_fresh_save():
    # No shared in-memory state between these two calls -- this is the
    # same shape of check as "does it survive a restart."
    content_module.save_content({"pages": {"home": {"title": "Survived A Restart"}}})
    reloaded = content_module.load_content()
    assert reloaded["pages"]["home"]["title"] == "Survived A Restart"


def test_load_content_merges_saved_edits_over_defaults_not_replacing_them():
    # A saved edit to one field of one page must not blow away every other
    # page/field that was never touched.
    content_module.save_content({"pages": {"home": {"title": "Only Title Changed"}}})
    reloaded = content_module.load_content()
    assert reloaded["pages"]["home"]["title"] == "Only Title Changed"
    assert reloaded["pages"]["home"]["hero_image"] == content_module.DEFAULT_PAGES["pages"]["home"]["hero_image"]
    assert "aloha_wellness" in reloaded["pages"]
    assert reloaded["pages"]["aloha_wellness"] == content_module.DEFAULT_PAGES["pages"]["aloha_wellness"]


def test_load_content_falls_back_to_defaults_when_nothing_saved_yet():
    assert not content_module.DATA_FILE.exists()
    assert content_module.load_content() == content_module.DEFAULT_PAGES


def test_load_content_falls_back_to_defaults_on_corrupt_saved_file():
    content_module.DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    content_module.DATA_FILE.write_text("not valid json{{{", encoding="utf-8")
    assert content_module.load_content() == content_module.DEFAULT_PAGES


def test_editing_one_page_never_mutates_default_pages_in_memory():
    # Regression guard for an aliasing bug in _deep_merge: it only rebuilds
    # keys present in BOTH the base and the override, so a page nobody has
    # edited yet stays a direct reference into DEFAULT_PAGES unless
    # load_content() first deep-copies. Simulates exactly what admin.py's
    # edit routes do: load, mutate the returned dict in place, save.
    original_title = copy.deepcopy(content_module.DEFAULT_PAGES["pages"]["home"]["title"])
    data = content_module.load_content()
    data["pages"]["home"]["title"] = "Mutated By A Different Page's Edit"
    content_module.save_content(data)

    assert content_module.DEFAULT_PAGES["pages"]["home"]["title"] == original_title, (
        "Editing a page must never mutate the module-level DEFAULT_PAGES dict in memory"
    )


# ---------------------------------------------------------------------------
# config._resolve_persistent_dir: picks the Render disk mount when it
# exists, falls back to BASE (local dev, or a Render service with no disk
# attached) when it doesn't -- so nothing here requires a disk to run.
# ---------------------------------------------------------------------------

def test_resolve_persistent_dir_uses_candidate_when_it_exists(tmp_path):
    candidate = tmp_path / "mounted_disk"
    candidate.mkdir()
    base = tmp_path / "base"
    base.mkdir()
    assert config._resolve_persistent_dir(candidate, base) == candidate


def test_resolve_persistent_dir_falls_back_to_base_when_candidate_missing(tmp_path):
    candidate = tmp_path / "no_disk_here"
    base = tmp_path / "base"
    base.mkdir()
    assert config._resolve_persistent_dir(candidate, base) == base


def test_admin_content_file_is_never_the_stale_legacy_file():
    # Regression guard: config.DATA_FILE must never be repointed at the
    # pre-existing website_content.json left over from the old monolith
    # (ke_aupuni_website.py) -- verified 2026-09-27 to hold stale,
    # superseded page copy. Wiring real load/save onto that exact file
    # would silently resurrect it the moment the app started reading it.
    assert config.DATA_FILE.name != "website_content.json"


# ---------------------------------------------------------------------------
# End-to-end: a real admin edit through /admin/edit/<page_id> shows up on
# the real public page, proven by reading the saved file independently of
# any in-memory object the app is holding.
# ---------------------------------------------------------------------------

def test_admin_edit_persists_and_appears_on_public_page(client):
    # kingdom_wealth (unlike home/partner/aloha_wellness/etc.) has no
    # dedicated route -- it's served by the generic /<page_id> catch-all,
    # driven by load_content(), so it actually proves the content pipeline.
    _login(client)
    resp = client.post(
        "/admin/edit/kingdom_wealth",
        data={"title": "Persistence Round-Trip Test Title", "hero_image": "", "body_md": "round trip body"},
        follow_redirects=False,
    )
    assert resp.status_code == 302

    on_disk = json.loads(content_module.DATA_FILE.read_text(encoding="utf-8"))
    assert on_disk["pages"]["kingdom_wealth"]["title"] == "Persistence Round-Trip Test Title"

    public_resp = client.get("/kingdom_wealth")
    assert public_resp.status_code == 200
    assert b"Persistence Round-Trip Test Title" in public_resp.data
