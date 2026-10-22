"""Kahu Phil's standing font rule (2026-10-22): the website uses Noto Sans and the right Noto font for each
language, served from this site itself. Never Helvetica, Arial, DejaVu or Georgia, and never Google Fonts."""
import re
from pathlib import Path

import pytest

import app as app_module

@pytest.fixture
def client():
    app_module.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    with app_module.app.test_client() as c:
        yield c


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://keaupuniakeakua.faith"

# Code and pages the live site is built from (not tests, not the unused legacy monolith, not vendored files).
SOURCES = [p for p in (
    list((ROOT / "templates").rglob("*.html")) + list((ROOT / "templates").rglob("*.css"))
    + list((ROOT / "blueprints").glob("*.py")) + [ROOT / "styles.py", ROOT / "content.py", ROOT / "app.py"]
    + list((ROOT / "static" / "fonts").glob("*.css"))
) if p.is_file()]

FORBIDDEN = re.compile(r"helvetica|arial|dejavu|georgia|system-ui|-apple-system|segoe|times new roman|fonts\.googleapis|fonts\.gstatic", re.I)

REQUIRED_FILES = (
    "NotoSans-Regular.ttf", "NotoSans-Bold.ttf", "NotoSans-Italic.ttf", "NotoSans-BoldItalic.ttf",
    "NotoSansHebrew-Regular.ttf", "NotoSansHebrew-Bold.ttf", "NotoSansJP-Regular.ttf", "NotoSansJP-Bold.ttf",
)


@pytest.mark.parametrize("path", SOURCES, ids=lambda p: str(p.relative_to(ROOT)))
def test_no_forbidden_font_names_anywhere(path):
    hits = FORBIDDEN.findall(path.read_text(encoding="utf-8", errors="replace"))
    assert not hits, f"{path.relative_to(ROOT)} names a forbidden font or Google Fonts: {sorted(set(h.lower() for h in hits))}"


def test_every_font_family_declaration_is_noto():
    bad = []
    for path in SOURCES:
        for m in re.finditer(r"font-family:\s*([^;}\"\n]*)", path.read_text(encoding="utf-8", errors="replace")):
            value = m.group(1).strip()
            if value.lower() in ("inherit", "initial", "unset"):
                continue
            if not value.replace('"', "'").lstrip("'").lower().startswith("noto sans"):
                bad.append((str(path.relative_to(ROOT)), value))
    assert not bad, f"font-family that is not Noto Sans first: {bad}"


def test_the_noto_files_are_on_the_site_and_real():
    for name in REQUIRED_FILES:
        f = ROOT / "static" / "fonts" / name
        assert f.is_file() and f.stat().st_size > 20_000, f"missing or empty font file {name}"
        assert f.read_bytes()[:4] in (b"\x00\x01\x00\x00", b"true", b"OTTO"), f"{name} is not a font file"


def test_noto_css_points_only_at_files_that_exist():
    css = (ROOT / "static" / "fonts" / "noto.css").read_text(encoding="utf-8")
    urls = re.findall(r"url\('(/static/fonts/[^']+)'\)", css)
    assert len(urls) == len(REQUIRED_FILES)
    for u in urls:
        assert (ROOT / u.lstrip("/")).is_file(), u


def test_the_site_actually_serves_the_fonts(client):
    css = client.get("/static/fonts/noto.css", base_url=BASE)
    assert css.status_code == 200
    for name in REQUIRED_FILES:
        resp = client.get(f"/static/fonts/{name}", base_url=BASE)
        assert resp.status_code == 200, name
        assert len(resp.data) > 20_000, name


def test_pages_load_the_local_font_css_not_google(client):
    for path in ("/", "/campaign/002", "/rotten-fencepost"):
        html = client.get(path, base_url=BASE).get_data(as_text=True)
        assert "/static/fonts/noto.css" in html, path
        assert "googleapis" not in html and "gstatic" not in html, path
