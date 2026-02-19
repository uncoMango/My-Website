# blueprints/pages.py
# =========================================================
# All public-facing page routes.
# Each page in website_content.json gets rendered here.
# =========================================================

import markdown
from flask import Blueprint, abort, render_template
from content import load_content, get_nav_items
from config import LOGO_PATH, LOGO_HEIGHT, FOOTER_TEXT

pages_bp = Blueprint("pages", __name__)


def md_to_html(md_text):
    """Convert Markdown text to HTML."""
    return markdown.markdown(md_text or "", extensions=["extra", "nl2br"])


def render_page(page_id, data):
    """Render any page from website_content.json by its ID."""
    pages = data.get("pages", {})
    if page_id not in pages:
        abort(404)
    page = pages[page_id]
    nav_items = get_nav_items(data)
    return render_template(
        "page.html",
        page=page,
        nav_items=nav_items,
        body_html=md_to_html(page.get("body_md", "")),
        current_page=page_id,
        logo_path=LOGO_PATH,
        logo_height=LOGO_HEIGHT,
        footer_text=FOOTER_TEXT,
    )


@pages_bp.route("/")
def home():
    data = load_content()
    return render_page("home", data)


@pages_bp.route("/myron-golden")
def myron_golden_page():
    data = load_content()
    nav_items = get_nav_items(data)
    return render_template(
        "myron_golden.html",
        nav_items=nav_items,
        logo_path=LOGO_PATH,
        logo_height=LOGO_HEIGHT,
        footer_text=FOOTER_TEXT,
    )


@pages_bp.route("/<page_id>")
def page(page_id):
    # Skip reserved prefixes so other blueprints handle them.
    if page_id in ("admin", "product", "checkout", "download", "paypal", "stripe", "kahu"):
        abort(404)
    data = load_content()
    pages = data.get("pages", {})
    if page_id not in pages:
        abort(404)
    return render_page(page_id, data)
