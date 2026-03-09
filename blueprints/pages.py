# blueprints/pages.py
import markdown
from datetime import datetime
from flask import Blueprint, abort, render_template, Response, send_from_directory
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
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://keaupuniakeakua.faith/</loc><priority>1.0</priority></url>
  <url><loc>https://keaupuniakeakua.faith/aloha-wellness</loc><priority>0.9</priority></url>
  <url><loc>https://keaupuniakeakua.faith/kingdom_wealth</loc><priority>0.8</priority></url>
  <url><loc>https://keaupuniakeakua.faith/call_to_repentance</loc><priority>0.8</priority></url>
  <url><loc>https://keaupuniakeakua.faith/pastor_planners</loc><priority>0.7</priority></url>
  <url><loc>https://keaupuniakeakua.faith/nahenahe_voice</loc><priority>0.7</priority></url>
  <url><loc>https://keaupuniakeakua.faith/free_booklets</loc><priority>0.7</priority></url>
  <url><loc>https://keaupuniakeakua.faith/kingdom_keys</loc><priority>0.7</priority></url>
  <url><loc>https://keaupuniakeakua.faith/partner</loc><priority>0.6</priority></url>
  <url><loc>https://keaupuniakeakua.faith/myron-golden</loc><priority>0.6</priority></url>
</urlset>'''
    return Response(xml, mimetype='application/xml', headers={'Content-Type': 'application/xml; charset=utf-8'})

@pages_bp.route("/robots.txt")
def robots():
    return send_from_directory('static', 'robots.txt', mimetype='text/plain')

@pages_bp.route("/<page_id>")
def page(page_id):
    if page_id in ("admin", "product", "checkout", "download", "paypal", "stripe", "kahu"):
        abort(404)
    data = load_content()
    pages = data.get("pages", {})
    if page_id not in pages:
        abort(404)
    return render_page(page_id, data)
