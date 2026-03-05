# blueprints/pages.py
import markdown
from datetime import datetime
from flask import Blueprint, abort, render_template, Response
from content import load_content, get_nav_items
from config import LOGO_PATH, LOGO_HEIGHT, FOOTER_TEXT, PAYPAL_CLIENT_ID, STRIPE_ENABLED, STRIPE_PUBLISHABLE_KEY

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
def myron_golden():
    data = load_content()
    return render_template(
        "myron_golden_funnel.html",
        mg_hero_headline=data.get("mg_hero_headline", "How to Fund Your Mission Without a 9-to-5"),
        mg_hero_sub=data.get("mg_hero_sub", "Stop struggling to resource your calling. The man who taught me — Myron Golden — built a system rooted in Scripture and proven in the marketplace. Here is where to start."),
        mg_story_headline=data.get("mg_story_headline", "A Pastor on Molokai Needed a War Chest. Here Is What I Found."),
        mg_story_body=data.get("mg_story_body", "I am 67 years old. I have been a pastor on Molokai for eight years, serving a community of about 7,000 people. I have 54 volumes of Kingdom theology to publish, a wellness mission to fund, and a ranch that does not pay ministry bills. I knew the vision was from God. I did not know how to fund it. That is when I found Myron Golden."),
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
        paypal_client_id=PAYPAL_CLIENT_ID,
        stripe_enabled=STRIPE_ENABLED,
        stripe_publishable_key=STRIPE_PUBLISHABLE_KEY if STRIPE_ENABLED else "",
    )

@pages_bp.route("/aloha-wellness")
def aloha_wellness_funnel():
    data = load_content()
    youtube_embed_url = data.get("funnel_youtube_url", "https://www.youtube.com/embed/O_-J8t0NHLc")
    return render_template("aloha_wellness_funnel.html", youtube_embed_url=youtube_embed_url)

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
