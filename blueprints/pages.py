# blueprints/pages.py
import markdown
from datetime import datetime
from flask import Blueprint, abort, render_template, Response
from content import load_content, get_nav_items
from config import LOGO_PATH, LOGO_HEIGHT, FOOTER_TEXT

pages_bp = Blueprint("pages", __name__)

def md_to_html(md_text):
    return markdown.markdown(md_text or "", extensions=["extra", "nl2br"])

def render_page(page_id, data):
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

@pages_bp.route("/partner")
def partner_page():
    data = load_content()
    nav_items = get_nav_items(data)
    return render_template(
        "partner.html",
        nav_items=nav_items,
        logo_path=LOGO_PATH,
        logo_height=LOGO_HEIGHT,
        footer_text=FOOTER_TEXT,
    )

@pages_bp.route("/aloha-wellness")
def aloha_wellness_funnel():
    return render_template("aloha_wellness_funnel.html")

@pages_bp.route("/sitemap.xml")
def sitemap():
    pages = [
        ("/",                       "1.0", "weekly"),
        ("/kingdom_wealth",         "0.9", "weekly"),
        ("/free_booklets",          "0.9", "weekly"),
        ("/kingdom_keys",           "0.9", "weekly"),
        ("/call_to_repentance",     "0.9", "weekly"),
        ("/aloha_wellness",         "0.9", "weekly"),
        ("/pastor_planners",        "0.8", "monthly"),
        ("/nahenahe_voice",         "0.8", "monthly"),
        ("/aloha-wellness-funnel",  "0.9", "weekly"),
        ("/aloha-wellness-buy",     "0.7", "monthly"),
        ("/myron-golden",           "0.8", "weekly"),
        ("/partner",                "0.9", "monthly"),
    ]
    base_url = "https://keaupuniakeakua.faith"
    today = datetime.now().strftime("%Y-%m-%d")
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for path, priority, freq in pages:
        xml.append("  <url>")
        xml.append(f"    <loc>{base_url}{path}</loc>")
        xml.append(f"    <lastmod>{today}</lastmod>")
        xml.append(f"    <changefreq>{freq}</changefreq>")
        xml.append(f"    <priority>{priority}</priority>")
        xml.append("  </url>")
    xml.append("</urlset>")
    return Response("\n".join(xml), mimetype="application/xml")

@pages_bp.route("/robots.txt")
def robots():
    content = "User-agent: *\nAllow: /\nDisallow: /kahu\nDisallow: /admin\n\nSitemap: https://keaupuniakeakua.faith/sitemap.xml\n"
    return Response(content, mimetype="text/plain")

@pages_bp.route("/<page_id>")
def page(page_id):
    if page_id in ("admin", "product", "checkout", "download", "paypal", "stripe", "kahu"):
        abort(404)
    data = load_content()
    pages = data.get("pages", {})
    if page_id not in pages:
        abort(404)
    return render_page(page_id, data)
