# blueprints/package.py
# =========================================================
# The Rotten Fencepost Package (2026-10-23): the free Introduction page "Smoke Is Not the Fire" and the $47 package
# page "What Your Body Forgot". The words come from Kahu Phil's own files, stored unchanged in content_text/:
#   smoke_is_not_the_fire.json  -- the Introduction, one entry per paragraph, from the master manuscript
#   what_your_body_forgot.md    -- Part 1 of Rotten_Fencepost_Package.md (his notes in [square brackets] removed)
# =========================================================

import json
from functools import lru_cache

import markdown
from flask import Blueprint, abort, redirect, render_template, request, send_file

from config import BASE, FOOTER_TEXT, LOGO_HEIGHT, LOGO_PATH
from content import get_nav_items, get_product_by_id, load_content
from limiter import limiter
from schema import SITE_URL, build_breadcrumb_schema, build_product_schema, build_webpage_schema
from blueprints.downloads import _valid_email, save_introduction_signup

package_bp = Blueprint("package", __name__)

TEXT_DIR = BASE / "content_text"
INTRO_PDF = TEXT_DIR / "Smoke_Is_Not_the_Fire.pdf"
PACKAGE_PRODUCT_ID = "prod_wyk_package"
HERO_IMAGE = "/static/images/diana-sanders-c24miY2R0FI-unsplash.jpg"

BUY_BUTTON_HTML = (
    '<p class="wyk-buy"><a href="/checkout/' + PACKAGE_PRODUCT_ID + '" class="buy-button" '
    'style="background: linear-gradient(135deg, #c9a842, #9a7a1a); font-size: 1.3rem; padding: 1rem 2.5rem;">'
    "Get the Package, $47</a></p>"
)


def _md(text):
    return markdown.markdown(text, extensions=["extra", "nl2br"])


@lru_cache(maxsize=1)
def _introduction():
    return json.loads((TEXT_DIR / "smoke_is_not_the_fire.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _package_text():
    """(title, subtitle, tagline, body_html) from the stored page wording."""
    lines = (TEXT_DIR / "what_your_body_forgot.md").read_text(encoding="utf-8").split("\n")
    title = lines[0].lstrip("# ").strip()
    subtitle = lines[1].lstrip("# ").strip()
    rest = "\n".join(lines[2:]).strip("\n")
    tagline, _, body = rest.partition("\n\n")
    body_html = _md(body).replace("<p>@@BUY_BUTTON@@</p>", BUY_BUTTON_HTML)
    return title, subtitle, tagline.strip(), body_html


def _nav():
    return get_nav_items(load_content())


# ---------------------------------------------------------------- the free Introduction
@package_bp.route("/smoke-is-not-the-fire")
def introduction_page():
    intro = _introduction()
    url = SITE_URL + request.path
    return render_template(
        "introduction.html",
        paragraphs=intro["paragraphs"],
        saved=request.args.get("saved") == "1",
        nav_items=_nav(),
        logo_path=LOGO_PATH,
        logo_height=LOGO_HEIGHT,
        footer_text=FOOTER_TEXT,
        page_schema=build_webpage_schema(
            name="Smoke Is Not the Fire",
            description="Read the whole Introduction here, free. No sign-up needed.",
            url=url,
            image_url=request.url_root.rstrip("/") + HERO_IMAGE,
        ),
        breadcrumb_schema=build_breadcrumb_schema([
            ("Home", SITE_URL + "/"),
            ("Rotten Fencepost", SITE_URL + "/rotten-fencepost"),
            ("Smoke Is Not the Fire", url),
        ]),
    )


@package_bp.route("/smoke-is-not-the-fire/download")
def introduction_pdf():
    if not INTRO_PDF.is_file():
        abort(404)
    return send_file(INTRO_PDF, as_attachment=True, download_name="Smoke_Is_Not_the_Fire.pdf", mimetype="application/pdf")


@package_bp.route("/smoke-is-not-the-fire/keep-me-posted", methods=["POST"])
@limiter.limit("3 per hour")
def keep_me_posted():
    """Same guards as the site's other forms (a browser User-Agent, an empty hidden trap field, a real-looking address,
    3 tries an hour). Saves the address to the lead list. Sends nothing to the person."""
    back = "/smoke-is-not-the-fire"
    if not request.headers.get("User-Agent", "").strip():
        return redirect(back)
    if request.form.get("website"):
        return redirect(back)
    email = request.form.get("email", "").strip().lower()
    if not email or not _valid_email(email):
        return redirect(back + "#keep-me-posted")
    save_introduction_signup(email)
    return redirect(back + "?saved=1#keep-me-posted")


# ---------------------------------------------------------------- the package page
@package_bp.route("/what-your-body-forgot")
def package_page():
    product = get_product_by_id(PACKAGE_PRODUCT_ID)
    if not product or not product.get("active", True):
        abort(404)
    title, subtitle, tagline, body_html = _package_text()
    url = SITE_URL + request.path
    image = request.url_root.rstrip("/") + HERO_IMAGE
    return render_template(
        "package.html",
        title=title,
        subtitle=subtitle,
        tagline=tagline,
        body_html=body_html,
        nav_items=_nav(),
        logo_path=LOGO_PATH,
        logo_height=LOGO_HEIGHT,
        footer_text=FOOTER_TEXT,
        page_schema=build_webpage_schema(name=title + ": " + subtitle, description=tagline, url=url, image_url=image),
        product_schema=build_product_schema(product, url=url, image_url=image),
        breadcrumb_schema=build_breadcrumb_schema([
            ("Home", SITE_URL + "/"),
            ("Rotten Fencepost", SITE_URL + "/rotten-fencepost"),
            (title, url),
        ]),
    )
