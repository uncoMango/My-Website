# blueprints/pages.py
import markdown
from flask import Blueprint, abort, render_template, Response, send_from_directory, request
from content import load_content, get_nav_items, get_product_by_id, get_campaign_by_id, get_hub_featured_campaigns
from config import LOGO_PATH, LOGO_HEIGHT, FOOTER_TEXT, PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, STRIPE_ENABLED, STRIPE_PUBLISHABLE_KEY
from schema import SITE_URL, build_webpage_schema, build_article_schema, build_breadcrumb_schema, build_collection_itemlist_schema, build_product_schema

pages_bp = Blueprint("pages", __name__)

def md_to_html(md_text):
    return markdown.markdown(md_text or "", extensions=["extra", "nl2br"])

def _abs_image(hero_image):
    return request.url_root.rstrip("/") + hero_image if hero_image else None

def render_page(page_id, data):
    pages = data.get("pages", {})
    if page_id not in pages:
        abort(404)
    page = pages[page_id]
    nav_items = get_nav_items(data)
    page_url = SITE_URL + request.path
    page_schema = build_webpage_schema(
        name=page.get("title"),
        description=page.get("meta_description"),
        url=page_url,
        image_url=_abs_image(page.get("hero_image")),
    )
    return render_template(
        "page.html",
        page=page,
        nav_items=nav_items,
        body_html=md_to_html(page.get("body_md", "")),
        current_page=page_id,
        logo_path=LOGO_PATH,
        logo_height=LOGO_HEIGHT,
        footer_text=FOOTER_TEXT,
        founding_reader_remaining=data.get("founding_reader_remaining", 100),
        page_schema=page_schema,
    )

@pages_bp.route("/")
def home():
    data = load_content()
    return render_page("home", data)

@pages_bp.route("/rotten-fencepost")
def rotten_fencepost():
    data = load_content()
    nav_items = get_nav_items(data)
    page_url = SITE_URL + request.path
    # Work Order V001-002: the page now leads with the Rotten Fencepost
    # Principle itself, not the Field Guide product -- a WebPage entity
    # describing that is more accurate than relying on Product schema
    # alone to say what this page is about.
    page_schema = build_webpage_schema(
        name="The Rotten Fencepost Principle",
        description="Recurring problems aren't solved by treating symptoms again and again -- they're solved by finding the cause.",
        url=page_url,
        image_url=_abs_image("/static/images/diana-sanders-c24miY2R0FI-unsplash.jpg"),
    )
    product_schema = None
    product = get_product_by_id("rotten_fencepost_field_guide")
    if product:
        # This product has no cover_image in the catalog (digital_products.json).
        # Use this page's own hero photo rather than borrowing another
        # product's cover art -- accurate to what's actually on this page.
        product_schema = build_product_schema(
            product,
            url=page_url,
            image_url=_abs_image("/static/images/diana-sanders-c24miY2R0FI-unsplash.jpg"),
        )
    # Work Order P-003: surface a curated, bounded set of campaign videos
    # directly on this hub page (HUB_FEATURED_CAMPAIGN_IDS in content.py),
    # sourced from the same CAMPAIGNS data /campaign/<id> renders from, so
    # video/title/copy stay in sync between the hub and each campaign's
    # own page by construction. This does NOT loop over every campaign --
    # the ecosystem is expected to grow past 60, and the featured list is
    # what keeps this page from growing unbounded as that happens.
    hub_campaigns = get_hub_featured_campaigns()
    return render_template(
        "rotten_fencepost.html",
        nav_items=nav_items,
        logo_path=LOGO_PATH,
        logo_height=LOGO_HEIGHT,
        footer_text=FOOTER_TEXT,
        page_schema=page_schema,
        product_schema=product_schema,
        hub_campaigns=hub_campaigns,
    )

@pages_bp.route("/campaign/<campaign_id>")
def campaign_page(campaign_id):
    """Generic evergreen page for a published Discovery Operations campaign
    video (Work Order P-001). Campaign 002, 003, etc. need only a new entry
    in content.py's CAMPAIGNS dict -- this route and its template are
    already generic over campaign_id."""
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        abort(404)
    data = load_content()
    nav_items = get_nav_items(data)
    page_url = SITE_URL + request.path
    page_schema = build_webpage_schema(
        name=campaign.get("title"),
        description=campaign.get("meta_description"),
        url=page_url,
        image_url=_abs_image(campaign.get("hero_image")),
    )
    breadcrumb_schema = build_breadcrumb_schema([
        ("Home", SITE_URL + "/"),
        ("Rotten Fencepost", SITE_URL + "/rotten-fencepost"),
        (campaign.get("title"), page_url),
    ])
    return render_template(
        "campaign_page.html",
        campaign=campaign,
        nav_items=nav_items,
        logo_path=LOGO_PATH,
        logo_height=LOGO_HEIGHT,
        footer_text=FOOTER_TEXT,
        page_schema=page_schema,
        breadcrumb_schema=breadcrumb_schema,
    )

@pages_bp.route("/rotten-fencepost/success")
def rotten_fencepost_success():
    data = load_content()
    nav_items = get_nav_items(data)
    return render_template(
        "rotten_fencepost_success.html",
        nav_items=nav_items,
        logo_path=LOGO_PATH,
        logo_height=LOGO_HEIGHT,
        footer_text=FOOTER_TEXT,
    )

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
    page_schema = build_webpage_schema(
        name="Partner With Us - Ke Aupuni O Ke Akua",
        description="Partner with Ke Aupuni O Ke Akua to support Kingdom teaching from Molokai - monthly giving tiers, free booklets, and direct ministry impact.",
        url=SITE_URL + request.path,
        image_url=_abs_image("/static/images/helping_hands.jpg"),
    )
    return render_template(
        "partner.html",
        nav_items=nav_items,
        logo_path=LOGO_PATH,
        logo_height=LOGO_HEIGHT,
        footer_text=FOOTER_TEXT,
        paypal_client_id=PAYPAL_CLIENT_ID,
        paypal_enabled=bool(PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET),
        stripe_enabled=STRIPE_ENABLED,
        stripe_publishable_key=STRIPE_PUBLISHABLE_KEY if STRIPE_ENABLED else "",
        page_schema=page_schema,
    )

@pages_bp.route("/kingdom-study")
def kingdom_study():
    return render_template("kingdom_study.html")

@pages_bp.route("/aloha-wellness")
def aloha_wellness_funnel():
    data = load_content()
    youtube_embed_url = data.get("funnel_youtube_url", "https://www.youtube.com/embed/O_-J8t0NHLc")
    return render_template("aloha_wellness_funnel.html", youtube_embed_url=youtube_embed_url)

_ECOSYSTEM_PAGE = {
    "title": "Ke Aupuni O Ke Akua | Wellness, Scripture Insight, and Kingdom Living",
    "meta_description": "Explore the Ke Aupuni O Ke Akua ecosystem: wellness teaching, Scripture language insight tools, and Kingdom-centered living frameworks that connect body, understanding, and purpose.",
    "body_md": (
        "## The Ke Aupuni O Ke Akua Ecosystem\n\n"
        "### A Connected Platform Under One Foundation\n\n"
        "Ke Aupuni O Ke Akua is not a collection of separate topics. It is a connected ecosystem of understanding — built around one core principle: that clarity in language shapes understanding, and understanding shapes life decisions.\n\n"
        "Each section of this platform addresses a different dimension of that principle. Together, they form a framework for how to live with stability, clarity, and purpose.\n\n"
        "---\n\n"
        "### Three Core Pillars\n\n"
        "---\n\n"
        "#### Wellness — Rhythm and Stewardship of the Body\n\n"
        "Most approaches to health focus on control: restrict intake, force outcomes, follow a temporary system until it collapses.\n\n"
        "The wellness teaching at Ke Aupuni O Ke Akua takes a different approach. It draws from Hawaiian ancestral eating patterns and Scripture-based stewardship principles to help people understand how the body was actually designed to function — through rhythm, awareness, and alignment rather than restriction.\n\n"
        "Health is not something imposed on the body. It is something restored to it.\n\n"
        "[**Why Diets Fail Long-Term →**](/wellness/why-diets-fail)\n\n"
        "[**Is Three Meals a Day Necessary? →**](/wellness/three-meals-a-day-necessary)\n\n"
        "[**What Actually Works Instead of Dieting →**](/wellness/lose-weight-without-dieting)\n\n"
        "---\n\n"
        "#### Scripture Language Insight Tool — Meaning and Original Language Clarity\n\n"
        "Most readers of Scripture encounter a translation — a carefully rendered text that makes the original accessible. But translation by necessity compresses meaning. Words in Hebrew and Greek carry layers of nuance that a single English word cannot always hold.\n\n"
        "The Scripture Language Insight Tool was built to make original Hebrew and Greek word meaning accessible without requiring seminary training. Input a word or verse. See the original term. Understand the meaning, usage, and relational context that the source language carried.\n\n"
        "This does not change Scripture. It opens it.\n\n"
        "[**Use the Scripture Language Insight Tool →**](/scripture-tools/hebrew-greek-meaning-tool)\n\n"
        "[**Why Translations Create Gaps →**](/scripture-tools/translation-gap-in-scripture)\n\n"
        "[**What Changes With Original Language Understanding →**](/scripture-tools/original-language-meaning)\n\n"
        "---\n\n"
        "#### Kingdom — Identity, Purpose, and Alignment\n\n"
        "Kingdom teaching at Ke Aupuni O Ke Akua is not abstract theology. It is a practical framework for how to live — how to understand identity, steward resources, apply biblical wisdom, and align daily decisions with purpose.\n\n"
        "This section draws from original language Scripture study, Hawaiian cultural wisdom, and decades of pastoral experience on Molokaʻi.\n\n"
        "[**Kingdom Teaching →**](/call_to_repentance)\n\n"
        "---\n\n"
        "### How Everything Connects\n\n"
        "These three pillars are not separate categories. They are expressions of the same principle applied to different areas of life.\n\n"
        "**Wellness** addresses how you relate to the body — your physical rhythms, food, rest, and the habits that either support or undermine health over time.\n\n"
        "**Scripture Language Insight** addresses how you understand language — specifically the gap between what was written in the original text and what most readers encounter in translation. Clarity here affects how Scripture is interpreted and applied.\n\n"
        "**Kingdom** addresses how you understand life direction — your identity, purpose, and the framework through which you make decisions.\n\n"
        "The core principle that ties all three together:\n\n"
        "> Clarity in language shapes understanding, and understanding shapes life decisions.\n\n"
        "When you understand your body more clearly, you make better decisions about health.\n"
        "When you understand Scripture's original language more clearly, you understand intent more accurately.\n"
        "When you understand Kingdom principles more clearly, you move through life with more alignment and less confusion.\n\n"
        "---\n\n"
        "### Where to Begin\n\n"
        "**If you are struggling with health or physical patterns:**\n\n"
        "The Wellness section is the starting point. Begin with why most diet approaches fail structurally — not because of personal weakness, but because of system design.\n\n"
        "[**Start with Wellness →**](/wellness/why-diets-fail)\n\n"
        "---\n\n"
        "**If you are struggling with Scripture understanding or translation confusion:**\n\n"
        "The Scripture Tools section is where to begin. Start with why translations create meaning gaps, then use the insight tool to explore original language words.\n\n"
        "[**Start with Scripture Tools →**](/scripture-tools/translation-gap-in-scripture)\n\n"
        "---\n\n"
        "**If you are searching for meaning, direction, or life purpose:**\n\n"
        "The Kingdom section addresses those questions from a biblical and ancestral framework — without abstraction or pressure.\n\n"
        "[**Start with Kingdom Teaching →**](/call_to_repentance)\n\n"
        "---\n\n"
        "### Why This Ecosystem Exists\n\n"
        "Ke Aupuni O Ke Akua is a Kingdom ministry based on Molokaʻi, Hawaii, led by Kahu Phil Stephens — a Native Hawaiian pastor, Paniolo, and lifelong student of Scripture.\n\n"
        "This platform exists to unify the teaching across all three areas under one coherent framework:\n\n"
        "- Wellness teaching grounded in ancestral patterns and biblical stewardship\n"
        "- Scripture language tools that restore access to original meaning\n"
        "- Kingdom principles that give life direction and purpose\n\n"
        "Each section supports the others. A person who understands their body better is more present for learning. A person who understands Scripture more clearly is better equipped to apply Kingdom principles. A person living in alignment with Kingdom identity has a stable foundation for all other decisions.\n\n"
        "This is not a content library. It is a structured framework for understanding — built for long-term clarity, not short-term motivation.\n\n"
        "---\n\n"
        "### Begin Where You Are\n\n"
        "There is no required starting point. Begin with the section that addresses the question you are carrying right now.\n\n"
        "The framework will hold regardless of where you enter.\n\n"
        "[**Wellness: Body Rhythm and Stewardship →**](/wellness/why-diets-fail)\n\n"
        "[**Scripture Tools: Original Language Meaning →**](/scripture-tools/hebrew-greek-meaning-tool)\n\n"
        "[**Kingdom: Identity and Life Direction →**](/call_to_repentance)"
    ),
}

@pages_bp.route("/ecosystem")
def ecosystem():
    data = load_content()
    nav_items = get_nav_items(data)
    page = dict(_ECOSYSTEM_PAGE)
    page["hero_image"] = data.get("pages", {}).get("home", {}).get("hero_image", "/static/images/taro_root.jpg")
    page_url = SITE_URL + request.path
    # CollectionPage: this page genuinely functions as a hub linking out to
    # the site's three real content pillars, via the same links its own
    # "Begin Where You Are" section already uses.
    page_schema = build_collection_itemlist_schema(
        name=page.get("title"),
        description=page.get("meta_description"),
        url=page_url,
        items=[
            ("Wellness: Body Rhythm and Stewardship", SITE_URL + "/wellness/why-diets-fail"),
            ("Scripture Tools: Original Language Meaning", SITE_URL + "/scripture-tools/hebrew-greek-meaning-tool"),
            ("Kingdom: Identity and Life Direction", SITE_URL + "/call_to_repentance"),
        ],
    )
    return render_template(
        "page.html",
        page=page,
        nav_items=nav_items,
        body_html=md_to_html(page["body_md"]),
        current_page="ecosystem",
        logo_path=LOGO_PATH,
        logo_height=LOGO_HEIGHT,
        footer_text=FOOTER_TEXT,
        founding_reader_remaining=data.get("founding_reader_remaining", 100),
        page_schema=page_schema,
    )

# ===== SEO ENTRY SUB-PAGES =====

_SEO_PAGES = {
    ("rotten-fencepost", "why-do-i-keep-starting-over"): {
        "title": "Why Do I Keep Starting Over? — A Rotten Fencepost Look at Repeated Failure",
        "meta_description": "Maybe the problem isn't discipline. Maybe you're fixing the wrong thing. A Rotten Fencepost look at why the same problems keep coming back.",
        "hero_image": "/static/images/paniolo_phil.jpg",
        "body_md": (
            "## This time will be different\n\n"
            "Have you ever found yourself saying those words? Maybe it was about your health, your finances, your relationship, or your walk with the Lord. You made a decision. You had every intention to follow through — for a little while, you did. Then one day you woke up and realized you were right back where you started.\n\n"
            "If that's ever happened to you, here's something worth considering: maybe the problem isn't that you don't care. Maybe it isn't that you're lazy. Maybe it isn't even that you lack discipline. Maybe, just maybe, you're fixing the wrong thing.\n\n"
            "---\n\n"
            "## What is this fence attached to?\n\n"
            "For many years, I've been blessed to live and work as a paniolo here in Hawaii. One lesson the land teaches me over and over is this: a fence doesn't usually fail all at once. You might first notice a loose wire, then a leaning section, then an animal gets through. Most people look at the wire, because that's what they can see. But an experienced paniolo learns to ask another question: what is this fence attached to? Because if the post underneath has begun rotting, it doesn't matter how tight you pull that wire. Sooner or later, the fence is coming down.\n\n"
            "People are not much different. We spend so much of our lives repairing the wire in our lives — we buy another planner, start another diet, make another budget, promise ourselves that tomorrow will be different. There's nothing wrong with those things. The problem comes when we expect them to fix something they were never designed to fix. If the fence post is rotten, new wire is not the answer.\n\n"
            "---\n\n"
            "## A very different question\n\n"
            "I've seen this happen in ministry, again and again: \"I've asked God to forgive me a hundred times.\" \"I keep making the same mistake.\" \"I don't understand why I can't seem to change.\" Those are honest questions — and also, often, the wrong ones. Instead of asking \"why can't I stay consistent,\" what if the question became: \"what keeps bringing me back here?\" That's a very different question. And sometimes, just sometimes, it's the beginning of freedom.\n\n"
            "Symptoms are often loud. Causes are usually quiet. Symptoms demand attention today; causes patiently wait on the ground. That is true in relationships, in finances, in health, and in our spiritual lives. If all we ever do is respond to what we can see, we may spend our entire lives repairing the same fence.\n\n"
            "---\n\n"
            "## Begin with curiosity, not guilt\n\n"
            "The next time you catch yourself starting over, don't begin with guilt. Don't begin with shame. Begin with curiosity. Ask yourself: what happened before I quit? What happened before I became discouraged? What happened before I made that decision? Better yet — what is feeding this? Those questions may just lead you to the fence post that is rotting. And once you find it, you finally have something you can repair.\n\n"
            "The subjects change, but the principles do not. Whether we're talking about families, health, money, leadership, or faith, the principle remains the same: if you find the cause, if you fix the cause, you can change the future.\n\n"
            "---\n\n"
            "### Going Deeper\n\n"
            "This article accompanies the video [Why Do I Keep Starting Over?](/campaign/002). For the broader teaching this builds on, see [Find the Cause, Not the Symptoms](/rotten-fencepost/find-the-cause-not-the-symptoms). For the full teaching library, visit the [Rotten Fencepost hub](/rotten-fencepost).\n\n"
            "---\n\n"
            "[**Watch the video →**](/campaign/002)\n\n"
            "<div style=\"background: #eef2f0; border: 2px solid #5f9ea0; border-radius: 12px; padding: 2rem; margin: 2rem 0; text-align: center;\">"
            "<div style=\"font-size: 0.8rem; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; color: #3d7a7c; margin-bottom: 0.5rem;\">Free Companion Workbook</div>"
            "<h3 style=\"margin: 0 0 0.75rem 0; color: #2c3e50;\">Why Do I Keep Starting Over?</h3>"
            "<p style=\"margin: 0 0 1.5rem 0; color: #2c3e50;\">A short workbook to help you apply this teaching to your own life — find the fence post that's actually rotting, not just the wire.</p>"
            "<a href=\"/media/campaign_002_planning_document_workbook_pdf_v5\" style=\"display: inline-block; padding: 0.9rem 2.5rem; background: linear-gradient(135deg, #d4af37, #b8960c); color: #1a1a1a; text-decoration: none; border-radius: 8px; font-weight: 900;\">Download the Free Workbook</a>"
            "</div>\n\n"
            "[**Explore the Rotten Fencepost Principle →**](/rotten-fencepost)"
        ),
    },
    ("wellness", "why-diets-fail"): {
        "title": "Why Diets Fail Long-Term (And What Actually Works Instead)",
        "meta_description": "Most diets fail because they are structurally unsustainable and conflict with how the human body is designed. This page explores ancestral, biblical, and lifestyle-based principles that explain why dieting breaks down and what actually creates lasting health.",
        "hero_image": "/static/images/ulu_kalo_mango.jpg",
        "body_md": (
            "## Why Diets Fail — And What Your Body Was Designed to Do Instead\n\n"
            "### The Cycle That Repeats\n\n"
            "Most diets follow a predictable cycle:\n\n"
            "- Strict rules and restriction\n"
            "- Short-term compliance\n"
            "- Increasing physical and emotional stress\n"
            "- Eventual breakdown\n"
            "- Rebound eating\n"
            "- Frustration and restart\n\n"
            "This cycle is not caused by lack of discipline. It is caused by structural unsustainability.\n\n"
            "---\n\n"
            "### Ancient Eating Patterns\n\n"
            "Across many Indigenous and ancestral cultures, including Hawaiian and Polynesian traditions, eating was not structured around constant restriction or rigid scheduling.\n\n"
            "Food patterns were shaped by:\n\n"
            "- Physical activity\n"
            "- Land availability\n"
            "- Natural daily rhythms\n"
            "- Respect for food as nourishment rather than constant consumption\n\n"
            "This created balance without formal dieting systems.\n\n"
            "---\n\n"
            "### Biblical Perspective on the Body\n\n"
            "Scripture consistently presents the body as something to steward rather than control through harsh restriction.\n\n"
            "Stewardship implies:\n\n"
            "- Awareness instead of excess control\n"
            "- Balance instead of extremes\n"
            "- Wisdom instead of rigid systems\n\n"
            "The goal is alignment, not domination.\n\n"
            "---\n\n"
            "### Why Diets Break Down\n\n"
            "Diets fail long-term because they:\n\n"
            "- Rely on external control instead of internal awareness\n"
            "- Ignore emotional and cultural eating behavior\n"
            "- Create stress around food decisions\n"
            "- Are not designed for lifelong sustainability\n\n"
            "Eventually, the system collapses under its own pressure.\n\n"
            "---\n\n"
            "### What Actually Works Long-Term\n\n"
            "Sustainable health is built on:\n\n"
            "- Consistent but flexible habits\n"
            "- Awareness of hunger and fullness\n"
            "- Reducing metabolic and emotional stress\n"
            "- Aligning eating patterns with lifestyle\n\n"
            "This is not a diet system. It is a lifestyle recalibration.\n\n"
            "---\n\n"
            "### The Aloha Wellness Approach\n\n"
            "Aloha Wellness is built on:\n\n"
            "- Scripture-based stewardship principles\n"
            "- Hawaiian cultural wisdom and lived experience\n"
            "- Sustainable, real-world application\n\n"
            "It is not a diet.\n\n"
            "It is a return to alignment between body, land, and lifestyle.\n\n"
            "---\n\n"
            "### Invitation\n\n"
            "If diets have not worked long-term, the issue is not effort — it is structure.\n\n"
            "There is another way forward.\n\n"
            "[**Free Aloha Wellness Guide →**](/download/aloha_wellness_freebie)\n\n"
            "[**Aloha Wellness Book →**](/aloha_wellness)\n\n"
            "---\n\n"
            "[**Continue Reading: Lose Weight Without Dieting →**](/wellness/lose-weight-without-dieting)"
        ),
    },
    ("wellness", "lose-weight-without-dieting"): {
        "title": "How to Lose Weight Without Dieting, Calorie Counting, or Restriction",
        "meta_description": "Learn how to lose weight without dieting, restriction, or calorie counting. A sustainable approach based on ancestral patterns, lifestyle alignment, and body awareness rooted in real-world experience and biblical stewardship principles.",
        "hero_image": "/static/images/food_basket.jpg",
        "body_md": (
            "## How to Lose Weight Without Dieting\n\n"
            "### The Question Most People Are Asking\n\n"
            "Most people think the answer is:\n\n"
            "\"How do I find the right diet?\"\n\n"
            "But the real question is:\n\n"
            "\"How do I stop needing diets at all?\"\n\n"
            "Because if a system only works temporarily, it is not a solution — it is a cycle.\n\n"
            "---\n\n"
            "### Why Dieting Keeps People Stuck\n\n"
            "Dieting creates a loop:\n\n"
            "- Control food intake\n"
            "- Rely on discipline\n"
            "- Suppress natural signals\n"
            "- Build stress over time\n"
            "- Eventually break\n"
            "- Restart again\n\n"
            "This is why most people never maintain long-term results, even after success.\n\n"
            "The issue is not effort.\n\n"
            "The issue is structure.\n\n"
            "---\n\n"
            "### Your Body Was Not Designed for Constant Restriction\n\n"
            "The human body responds more to:\n\n"
            "- Stress load\n"
            "- Consistency of habits\n"
            "- Sleep and recovery\n"
            "- Environment and rhythm\n\n"
            "Than to short-term food control.\n\n"
            "This is why restriction-based systems fail long term.\n\n"
            "---\n\n"
            "### What Ancient Eating Patterns Reveal\n\n"
            "Across Hawaiian and Polynesian traditions, eating was not based on constant intake or rigid schedules.\n\n"
            "It was shaped by:\n\n"
            "- Physical work and energy needs\n"
            "- Availability of food\n"
            "- Natural daily rhythms\n"
            "- Respect for food as nourishment, not habit\n\n"
            "This created balance without formal dieting systems.\n\n"
            "---\n\n"
            "### The Real Shift: From Control to Awareness\n\n"
            "Sustainable change happens when you stop trying to control everything and start rebuilding awareness:\n\n"
            "- Recognizing true hunger\n"
            "- Reducing habitual eating\n"
            "- Simplifying food decisions\n"
            "- Aligning intake with real energy needs\n\n"
            "This is not restriction.\n\n"
            "It is recalibration.\n\n"
            "---\n\n"
            "### Why This Works When Diets Do Not\n\n"
            "This approach works because it removes the failure points:\n\n"
            "- No extreme rules\n"
            "- No short-term systems\n"
            "- No rebound cycles\n"
            "- No dependence on motivation\n\n"
            "Instead, it builds stability through consistency and awareness.\n\n"
            "---\n\n"
            "### The Aloha Wellness Foundation\n\n"
            "Aloha Wellness is built on three foundations:\n\n"
            "- Scripture-based stewardship principles\n"
            "- Hawaiian cultural wisdom from lived experience\n"
            "- Practical, sustainable lifestyle alignment\n\n"
            "It is not a diet replacement.\n\n"
            "It is a return to a stable relationship with food, body, and discipline.\n\n"
            "---\n\n"
            "### The Invitation\n\n"
            "If diets have not worked for you long-term, it is not because you failed.\n\n"
            "It is because the system was never designed for sustainability.\n\n"
            "There is another way.\n\n"
            "One built on awareness, rhythm, and alignment instead of restriction.\n\n"
            "[**Free Aloha Wellness Guide →**](/download/aloha_wellness_freebie)\n\n"
            "[**Aloha Wellness Book →**](/aloha_wellness)\n\n"
            "---\n\n"
            "[**Related: Why Diets Fail Long-Term →**](/wellness/why-diets-fail)"
        ),
    },
    ("wellness", "three-meals-a-day-necessary"): {
        "title": "Is Three Meals a Day Necessary? What Scripture and Ancestral Wisdom Reveal",
        "meta_description": "Is eating three meals a day really necessary? Kahu Phil explores what the Bible and ancestral Hawaiian eating patterns reveal about meal frequency and health.",
        "hero_image": "/static/images/taro_root.jpg",
        "body_md": (
            "## Is Three Meals a Day Necessary? What Scripture and Ancestral Wisdom Reveal\n\n"
            "Three meals a day. Breakfast, lunch, dinner. It seems obvious — almost sacred.\n\n"
            "But is it actually how God designed your body to eat?\n\n"
            "---\n\n"
            "### Where \"Three Meals a Day\" Came From\n\n"
            "The three-meal-a-day structure did not come from Scripture. It did not come from ancestral Hawaiian wisdom. It came from **industrialization**.\n\n"
            "When factory work replaced agricultural life, workers needed to eat on a fixed schedule tied to shift breaks. Breakfast before work. Lunch at midday. Dinner after the shift. Three meals. Scheduled. Clock-driven.\n\n"
            "Before that, human beings — including the ancient Hawaiians of Molokaʻi — ate differently. They ate when they were hungry, in amounts that matched their activity, from foods available in season. There was no fixed schedule. There was **rhythm**.\n\n"
            "---\n\n"
            "### What Scripture Reveals About Eating\n\n"
            "The Bible does not prescribe a meal schedule. But it does speak to how Israel ate in the wilderness, how Jesus ate during his ministry, and what the earliest communities understood about food and the body.\n\n"
            "What emerges from careful study is not a diet plan — it is a set of **principles**. Eat what is given. Eat with gratitude. Do not be governed by appetite, but by wisdom.\n\n"
            "The Kingdom approach to eating is not about rules. It is about **stewardship of the temple** — honoring the body God gave you by feeding it in alignment with its design.\n\n"
            "---\n\n"
            "### What the Ancient Hawaiians Knew\n\n"
            "Native Hawaiians were renowned for physical strength, endurance, and health. Anthropological accounts consistently describe a lean, powerful people — not because they had a meal plan, but because they had **covenant alignment** with the land.\n\n"
            "They ate primarily taro (kalo), breadfruit (ulu), fish, and seasonal produce. They did not eat three meals a day on a clock. They ate in response to hunger, in relationship with nature's rhythms, and with communal gratitude.\n\n"
            "The result was health that lasted.\n\n"
            "---\n\n"
            "### The Practical Question\n\n"
            "If three meals a day is not required, what is?\n\n"
            "The answer is simpler than most diets would have you believe:\n\n"
            "- Eat when you are genuinely hungry\n"
            "- Eat food that nourishes rather than stimulates\n"
            "- Stop when you are satisfied, not when the plate is clean\n"
            "- Create space between eating and sleeping\n\n"
            "This is not a calorie count. It is not a macro split. It is **wisdom** — the kind that has sustained human health across thousands of years and is now being confirmed by modern research on meal timing, intermittent fasting, and metabolic health.\n\n"
            "---\n\n"
            "### Go Deeper with Aloha Wellness\n\n"
            "Kahu Phil Stephens explores these principles in full in the **Aloha Wellness** book — including the practical framework he uses daily on Molokaʻi.\n\n"
            "---\n\n"
            "[**Read Aloha Wellness — The Kingdom Approach to Health →**](/aloha_wellness)"
        ),
    },
    ("wellness", "ancestral-eating-patterns"): {
        "title": "Ancestral Eating Patterns — The Hawaiian Kingdom Health Model",
        "meta_description": "Explore the ancestral eating patterns of Native Hawaiians and how they align with Kingdom wellness principles taught by Pastor Kahu Phil Stephens from Molokai, Hawaii.",
        "hero_image": "/static/images/breadfruit.jpg",
        "body_md": (
            "## Ancestral Eating Patterns — The Hawaiian Kingdom Health Model\n\n"
            "For thousands of years, the people of Hawaiʻi ate from the land in a way that produced extraordinary health.\n\n"
            "No modern diet. No calorie counting. No macros. Just deep alignment between the people, the land, and the Creator who made both.\n\n"
            "That alignment is what Kahu Phil Stephens calls **Kingdom wellness** — and it is the foundation of the Aloha Wellness approach.\n\n"
            "---\n\n"
            "### What the Ancestral Hawaiian Diet Actually Looked Like\n\n"
            "The traditional Hawaiian diet was built on a few core foods:\n\n"
            "**Kalo (Taro)** — The sacred foundation of Hawaiian life. Kalo was not just food — it was family. In Hawaiian tradition, the taro plant is the elder sibling of humanity, a sign of the deep relationship between people, land, and the divine. Nutritionally, it is a complex carbohydrate that digests slowly, sustains energy, and causes none of the blood sugar spikes of modern processed grains.\n\n"
            "**Iʻa (Fish and seafood)** — Fresh from the ocean that surrounds the islands. High in omega-3 fatty acids, rich in protein, and eaten with the reverence of something given by the sea.\n\n"
            "**ʻUlu (Breadfruit)** — Calorie-dense, nourishing, and extraordinarily versatile. A single breadfruit tree can feed a family for generations.\n\n"
            "**Seasonal fruits and vegetables** — Eaten in rhythm with what the land produced, not imported or stored out of season.\n\n"
            "What was absent: processed sugar, refined flour, industrial seed oils, and the constant snacking that defines modern eating culture.\n\n"
            "---\n\n"
            "### Why Ancestral Eating Works — The Kingdom Framework\n\n"
            "From a Kingdom theology perspective, ancestral Hawaiian eating was an expression of **covenant stewardship**.\n\n"
            "The people did not own the land. The land was entrusted to them by the Creator. They ate what the land gave, in the season it gave it, with gratitude for the gift. The body, in turn, was treated as a temple — not a machine to be optimized, but a sacred gift to be honored.\n\n"
            "This is the same framework that undergirds the Aloha Wellness teaching: your body is not the enemy. It is a gift. How you steward it reflects your theology.\n\n"
            "---\n\n"
            "### What Changed — And Why It Matters\n\n"
            "When Western contact brought sugar plantations, canned goods, white rice, and eventually fast food, the health of the Hawaiian people collapsed with devastating speed.\n\n"
            "Rates of obesity, diabetes, and cardiovascular disease — rare in traditional Hawaiian life — became epidemic within two generations.\n\n"
            "This is not a racial vulnerability. It is a **covenant disruption**. A people who ate in alignment with God's design for their land and their body lost that alignment — and their health followed.\n\n"
            "The path back is not a diet. It is a **return** — to ancestral wisdom, Kingdom principles, and the deep understanding that how you eat is a spiritual act.\n\n"
            "---\n\n"
            "### Begin the Return\n\n"
            "The **Aloha Wellness** book is Kahu Phil's invitation to make that return — rooted in Scripture, informed by Hawaiian ancestral wisdom, and practical for life today.\n\n"
            "---\n\n"
            "[**Read Aloha Wellness — The Kingdom Approach to Health →**](/aloha_wellness)"
        ),
    },
    ("wellness", "why-modern-health-advice-feels-confusing"): {
        "title": "Why Modern Health Advice Feels So Confusing",
        "meta_description": "Modern health advice often contradicts itself, leaving people frustrated and uncertain. This page explores why modern health systems feel confusing and what a simpler, more grounded understanding of wellness looks like.",
        "hero_image": "/static/images/taro_root.jpg",
        "body_md": (
            "## Why Modern Health Advice Feels So Confusing\n\n"
            "### The Experience Most People Have Today\n\n"
            "Most people trying to improve their health eventually hit the same wall.\n\n"
            "They start with one system. They hear conflicting advice from another. They read studies that say opposite things. They try multiple approaches and end up more uncertain than when they started.\n\n"
            "This is not a personal failure. It is a structural one.\n\n"
            "---\n\n"
            "### Why the Advice Keeps Changing\n\n"
            "Health advice does not change because the body changes. It changes because:\n\n"
            "- Different studies measure different outcomes over different time periods\n"
            "- Commercial interests fund and shape research priorities\n"
            "- Short-term findings get treated as long-term conclusions\n"
            "- Institutions compete for authority over what counts as healthy\n\n"
            "The result is a system that produces contradictions faster than it produces clarity.\n\n"
            "---\n\n"
            "### The Missing Foundation\n\n"
            "Modern health systems tend to focus on isolated factors:\n\n"
            "- Calories in and out\n"
            "- Macronutrient ratios\n"
            "- Specific supplements or food categories\n\n"
            "What they often leave out:\n\n"
            "- Lifestyle and daily rhythm\n"
            "- Stress and recovery\n"
            "- Consistency over time\n"
            "- The relationship between eating and living\n\n"
            "The body is not a machine that responds only to inputs. It is a living system that responds to patterns.\n\n"
            "---\n\n"
            "### What Traditional and Ancestral Systems Show\n\n"
            "Hawaiian and Polynesian cultures built health into the fabric of daily life — not as a separate project, but as a natural result of how people worked, ate, and rested.\n\n"
            "Food was tied to:\n\n"
            "- Physical labor and energy needs\n"
            "- What the land and sea provided in season\n"
            "- Natural rhythms of day and activity\n\n"
            "There were no conflicting systems to navigate. There was simply alignment between the body, the land, and the life being lived.\n\n"
            "---\n\n"
            "### Why This Creates Confusion\n\n"
            "When there is no stable foundation, people cycle through systems:\n\n"
            "- Try one approach\n"
            "- It works briefly or not at all\n"
            "- Switch to the next promising method\n"
            "- Repeat\n\n"
            "Each cycle reinforces the belief that the problem is personal — that the right system just has not been found yet.\n\n"
            "But the problem is not the person. It is the absence of a unified framework for understanding the body in the first place.\n\n"
            "---\n\n"
            "### The Aloha Wellness Perspective\n\n"
            "Aloha Wellness does not offer another system to follow. It offers a different way of understanding health altogether.\n\n"
            "Built on four principles:\n\n"
            "- **Awareness** over control\n"
            "- **Rhythm** over rigidity\n"
            "- **Stewardship** over restriction\n"
            "- **Simplicity** over complexity\n\n"
            "These principles do not change with the next study. They are grounded in Scripture, confirmed by ancestral Hawaiian wisdom, and sustainable in real everyday life.\n\n"
            "---\n\n"
            "### The Invitation\n\n"
            "If health advice has felt confusing, the answer is not to find better advice.\n\n"
            "It is to build a foundation that does not depend on constantly changing advice in the first place.\n\n"
            "That foundation exists. It is simpler than most systems suggest.\n\n"
            "[**Free Aloha Wellness Guide →**](/download/aloha_wellness_freebie)\n\n"
            "[**Aloha Wellness Book →**](/aloha_wellness)\n\n"
            "---\n\n"
            "[**Related: Why Diets Fail Long-Term →**](/wellness/why-diets-fail)\n\n"
            "[**Related: Is Three Meals a Day Necessary? →**](/wellness/three-meals-a-day-necessary)"
        ),
    },
    ("wellness", "why-your-body-resists-diets"): {
        "title": "Why Your Body Resists Diets and Restrictive Eating",
        "meta_description": "Many people struggle because their body resists restrictive diets. This page explains why this happens and introduces a more natural, sustainable approach to eating and wellness.",
        "hero_image": "/static/images/food_basket.jpg",
        "body_md": (
            "## Why Your Body Resists Diets and Restrictive Eating\n\n"
            "### The Common Experience\n\n"
            "Most people begin a diet with real motivation and discipline. For a while it holds.\n\n"
            "Then something shifts:\n\n"
            "- Cravings intensify instead of fading\n"
            "- Energy drops and focus becomes harder to sustain\n"
            "- Consistency breaks down despite genuine effort\n\n"
            "This pattern repeats across different diets and different attempts. The frustration is real. So is the question: why does this keep happening?\n\n"
            "---\n\n"
            "### Why Willpower Alone Fails\n\n"
            "Willpower is a mental resource. It is not a biological long-term strategy.\n\n"
            "The body does not respond to intention. It responds to signals — stress, restriction, perceived scarcity. When those signals are present, the body activates protective responses regardless of what the mind has decided.\n\n"
            "This is not a character flaw. It is how the body is designed to function.\n\n"
            "---\n\n"
            "### The Body's Protective Response\n\n"
            "When caloric intake drops significantly or food is restricted, the body reads this as a threat:\n\n"
            "- Hunger signals increase to drive food-seeking behavior\n"
            "- Metabolism slows to conserve energy\n"
            "- Cravings intensify, particularly for calorie-dense foods\n\n"
            "These responses are not failure. They are biology working exactly as it was designed — protecting the body against scarcity.\n\n"
            "Restriction-based diets activate this system. The harder the restriction, the stronger the response.\n\n"
            "---\n\n"
            "### Why Diet Systems Miss This\n\n"
            "Most diet systems are built around control:\n\n"
            "- Control what you eat\n"
            "- Control how much\n"
            "- Control when\n\n"
            "They focus on compliance rather than on how the body actually adapts over time. Short-term results are mistaken for sustainable solutions. When the body's protective response eventually overcomes the control system, it looks like personal failure — but the design of the system itself was the problem.\n\n"
            "---\n\n"
            "### A More Natural Pattern\n\n"
            "Traditional eating patterns — including those of Hawaiian and Polynesian cultures — were not built around rigid control.\n\n"
            "They were shaped by:\n\n"
            "- Natural hunger and satiety rhythms\n"
            "- Physical activity and real energy demands\n"
            "- Food availability tied to land, season, and community\n\n"
            "There was no system to comply with. There was alignment — between the body, the food, and the life being lived. That alignment is what produced sustained health across generations.\n\n"
            "---\n\n"
            "### The Aloha Wellness Perspective\n\n"
            "Aloha Wellness is not a new control system. It is a return to a different relationship with the body altogether.\n\n"
            "Built on four shifts:\n\n"
            "- **Listening** to the body instead of overriding it\n"
            "- **Rhythm** over rules\n"
            "- **Consistency** over restriction\n"
            "- **Stewardship** over control\n\n"
            "These are not tactics. They are principles rooted in Scripture and confirmed by the lived experience of cultures that maintained health without modern diet systems.\n\n"
            "---\n\n"
            "### The Transition\n\n"
            "The goal is not to find a diet that works well enough to endure.\n\n"
            "The goal is to stop needing the diet framework at all — by understanding how the body actually functions and learning to work with it instead of against it.\n\n"
            "That shift is available. And it is simpler than most systems suggest.\n\n"
            "[**Free Aloha Wellness Guide →**](/download/aloha_wellness_freebie)\n\n"
            "[**Aloha Wellness Book →**](/aloha_wellness)\n\n"
            "---\n\n"
            "[**Related: Why Diets Fail Long-Term →**](/wellness/why-diets-fail)\n\n"
            "[**Related: Is Three Meals a Day Necessary? →**](/wellness/three-meals-a-day-necessary)\n\n"
            "[**Related: Why Modern Health Advice Feels So Confusing →**](/wellness/why-modern-health-advice-feels-confusing)"
        ),
    },
    ("kingdom", "what-is-the-kingdom-of-god"): {
        "title": "What Is the Kingdom of God? — Kingdom Theology Explained",
        "meta_description": "What is the Kingdom of God? Kahu Phil Stephens explains Kingdom theology from original Greek and Hebrew Scripture. Jesus preached the Kingdom 53 times — here's why that matters.",
        "hero_image": "/static/images/sunlight_bursting.jpg",
        "body_md": (
            "## What Is the Kingdom of God?\n\n"
            "Jesus mentioned the Kingdom of God **53 times** in the Gospels.\n\n"
            "He mentioned \"church\" twice.\n\n"
            "That ratio is not an accident. And understanding it changes everything.\n\n"
            "---\n\n"
            "### Not a Religion. A Kingdom.\n\n"
            "Most of what passes for Christianity today is built around church — attending services, following rituals, maintaining membership in a religious institution.\n\n"
            "That is not what Jesus preached. What Jesus preached was **the Kingdom of God** — a complete system of governance, identity, economy, health, and purpose that covers every dimension of human life.\n\n"
            "**Kahu Phil Stephens** — a Native Hawaiian pastor, Paniolo, and 30-year student of Scripture in the original Greek and Hebrew — has spent his ministry unpacking what Jesus actually meant when he said *the Kingdom of God is at hand*.\n\n"
            "The answer is more revolutionary than most churches have taught.\n\n"
            "---\n\n"
            "### What \"Kingdom\" Means in the Original Language\n\n"
            "The Greek word translated \"Kingdom\" is *basileia* (βασιλεία). It does not primarily mean a geographic territory. It means **the reign and rule of a king** — the active exercise of royal authority over every domain of life.\n\n"
            "When Jesus said \"the Kingdom of God is at hand,\" he was not announcing a future heavenly destination. He was announcing the arrival of God's active reign — breaking into history, available now, transforming everything it touches.\n\n"
            "This changes the entire framework of the Christian life. You are not waiting to go to heaven. You are living as a citizen of God's Kingdom **now** — and Kingdom citizens carry Kingdom authority, Kingdom identity, and Kingdom responsibility.\n\n"
            "---\n\n"
            "### The Three Dimensions of the Kingdom\n\n"
            "Through 30 years of studying Scripture in the original languages, Kahu Phil has identified three primary dimensions of Kingdom life:\n\n"
            "**Kingdom Identity** — Who you are in the Kingdom. Citizens of the Kingdom of God are not religious consumers. They are sons and daughters of the King, with royal inheritance, Kingdom purpose, and divine assignment.\n\n"
            "**Kingdom Wealth** — How the Kingdom views resources. The Kingdom operates on stewardship, not ownership. God is your Source, not your employer. Understanding this transforms how you approach money, giving, and increase.\n\n"
            "**Kingdom Wellness** — How the Kingdom views the body. Your body is a temple of the Holy Spirit — a gift to be stewarded, not a burden to be managed. Kingdom wellness is built on Scripture and confirmed by ancestral Hawaiian wisdom about food, rhythm, and covenant health.\n\n"
            "---\n\n"
            "### Begin Here\n\n"
            "The call to repentance is not a call to self-improvement. It is a call to *metanoia* — a complete change of mind and framework — from a church-centered worldview to a Kingdom-centered one.\n\n"
            "Kahu Phil's **Kingdom Series** is the place to begin.\n\n"
            "---\n\n"
            "[**Start the Kingdom Series →**](/call_to_repentance)\n\n"
            "[**Get FREE Kingdom Booklets →**](/free_booklets)"
        ),
    },
    ("kingdom", "jesus-kingdom-message"): {
        "title": "The Kingdom Message of Jesus — What He Actually Preached",
        "meta_description": "Jesus preached the Kingdom of God, not a religion. Kahu Phil Stephens unpacks the revolutionary Kingdom message of Jesus from original Greek and Hebrew Scripture.",
        "hero_image": "/static/images/bible_scroll.jpg",
        "body_md": (
            "## The Kingdom Message of Jesus — What He Actually Preached\n\n"
            "Before Jesus healed anyone. Before he performed a single miracle. Before he chose his disciples.\n\n"
            "He preached.\n\n"
            "And what he preached was not what most churches preach today.\n\n"
            "---\n\n"
            "### The First Words of Jesus' Ministry\n\n"
            "In Mark 1:14-15, the very first recorded words of Jesus' public ministry are:\n\n"
            "*\"The time is fulfilled, and the Kingdom of God is at hand. Repent and believe in the gospel.\"*\n\n"
            "Not: \"Accept me as your personal Savior.\"\n"
            "Not: \"Attend your local church.\"\n"
            "Not: \"Follow these religious rules.\"\n\n"
            "**The Kingdom of God is at hand.**\n\n"
            "This was the core message. Everything else — the healings, the teachings, the parables, the miracles — was in service of this announcement. Jesus came to establish a Kingdom, and he wanted everyone to know it had arrived.\n\n"
            "---\n\n"
            "### What \"Repent\" Actually Means\n\n"
            "The Greek word translated \"repent\" is *metanoia* (μετάνοια). It literally means **to change your mind** — to adopt a completely new framework for thinking about reality.\n\n"
            "Jesus was not asking people to feel guilty. He was asking them to **change their operating system** — to stop thinking like subjects of Rome or members of a religious institution, and start thinking like citizens of the Kingdom of God.\n\n"
            "That is a total transformation. And it is available to anyone willing to change their mind.\n\n"
            "---\n\n"
            "### The Kingdom Message in the Parables\n\n"
            "The majority of Jesus' parables begin with \"The Kingdom of God is like...\" He used stories about:\n\n"
            "- A farmer planting seed\n"
            "- A woman searching for a lost coin\n"
            "- A merchant finding a pearl of great price\n"
            "- A father welcoming home a son\n"
            "- A king preparing a wedding feast\n\n"
            "Every parable was designed to reveal how the Kingdom operates — how it grows, how it values people, how it distributes resources, how it deals with those who accept or reject it.\n\n"
            "The Kingdom is not a future event. It is a present reality. Jesus was teaching people how to *see* it, *enter* it, and *operate within* it.\n\n"
            "---\n\n"
            "### Why This Changes Everything\n\n"
            "If Christianity is primarily about going to heaven when you die, then the focus is on the afterlife.\n\n"
            "If Christianity is primarily about the Kingdom of God — **present, active, transforming every domain of life** — then the focus is on *now*. On how you steward your resources, your health, your relationships, your calling. On what it means to live as a citizen of an eternal Kingdom in a temporary world.\n\n"
            "That shift changes everything. And it is the shift that **Kahu Phil Stephens** has been teaching from Molokaʻi, Hawaiʻi for over 30 years.\n\n"
            "---\n\n"
            "### Go Deeper\n\n"
            "The Kingdom Series is where Kahu Phil unpacks the Kingdom message of Jesus in full — beginning with the call to repentance (metanoia) and moving through Kingdom identity, Kingdom wealth, and Kingdom wellness.\n\n"
            "Start with the free booklets. Go deeper with the full series.\n\n"
            "---\n\n"
            "[**Explore the Kingdom Series →**](/call_to_repentance)\n\n"
            "[**Get FREE Kingdom Booklets →**](/free_booklets)"
        ),
    },
    ("wealth", "biblical-stewardship-principles"): {
        "title": "Biblical Stewardship Principles — Kingdom Wealth Teaching",
        "meta_description": "Discover the biblical stewardship principles that most churches never teach. Kahu Phil Stephens reveals the Kingdom model of wealth rooted in original Hebrew and Greek Scripture.",
        "hero_image": "/static/images/kingdom-wealth-hero.jpg",
        "body_md": (
            "## Biblical Stewardship Principles — The Kingdom Approach to Wealth\n\n"
            "Most churches teach tithing. Few teach stewardship.\n\n"
            "There is a significant difference — and understanding it changes your relationship with money forever.\n\n"
            "---\n\n"
            "### The Foundational Principle: God Is Your Source\n\n"
            "Modern financial culture teaches that your employer, your clients, or your investments are your source of income. The Kingdom of God teaches something entirely different:\n\n"
            "**God is your Source. Money is a resource, not the source.**\n\n"
            "This is not a semantic distinction. It is a complete transformation of how you relate to money, work, and provision.\n\n"
            "When your employer is your source, losing your job is catastrophic. When God is your Source, a closed door is simply a redirect. The Source does not change. Only the channel does.\n\n"
            "---\n\n"
            "### The Parable of the Talents — Reread Through Kingdom Eyes\n\n"
            "In Matthew 25, Jesus tells a parable of a master who entrusts different amounts of money to his servants before a journey.\n\n"
            "Two servants invest and multiply what they were given. One buries his share out of fear.\n\n"
            "The master's response to the first two: *\"Well done, good and faithful servant. You have been faithful over little; I will set you over much.\"*\n\n"
            "The lesson is not about financial strategy. It is about **faithfulness to a trust**. The servants did not own what they were given — they were stewards. And faithful stewardship of small things leads to greater responsibility in the Kingdom.\n\n"
            "Every resource you have — money, time, skill, health — is a trust from the King. Faithfulness with what you have positions you for increase.\n\n"
            "---\n\n"
            "### Three Kingdom Stewardship Principles\n\n"
            "**1. Stewardship Before Ownership**\n"
            "In the Kingdom, you own nothing. You steward everything. The land, the money, the family, the ministry — all of it is the King's, entrusted to you for faithful management. This releases you from the anxiety of ownership and roots you in the peace of trusting stewardship.\n\n"
            "**2. Seed and Harvest**\n"
            "The Kingdom operates on a seed-and-harvest economy. What you give — generously, faithfully, in faith — comes back multiplied. This is not a prosperity-gospel transaction formula. It is a Kingdom principle woven into the fabric of creation itself. Farmers understand it. Kingdom citizens must understand it too.\n\n"
            "**3. Honor God First**\n"
            "The principle of *bikkurim* — firstfruits — runs throughout Scripture. Bringing the first and best of what you have to God is not a tax. It is a declaration of who your Source is. It realigns your trust and opens the channels of Kingdom provision.\n\n"
            "---\n\n"
            "### Beyond Tithing — Kingdom Wealth as a Way of Life\n\n"
            "Tithing is a starting point. Kingdom stewardship is a way of life.\n\n"
            "It governs how you earn (with integrity and purpose), how you spend (with wisdom and alignment), how you give (with generosity and faith), and how you invest (with long-term Kingdom fruitfulness in view).\n\n"
            "**Kahu Phil Stephens** has spent 30 years studying these principles in the original Greek and Hebrew of Scripture — and applying them in the context of a ministry that must resource itself from the margins of the economic system.\n\n"
            "---\n\n"
            "[**Explore Kingdom Wealth Teaching →**](/kingdom_wealth)\n\n"
            "[**Get FREE Kingdom Wealth Booklets →**](/free_booklets)"
        ),
    },
    ("scripture-tools", "translation-gap-in-scripture"): {
        "title": "Why Many People Misunderstand Scripture When Reading Translations Alone",
        "meta_description": "Many misunderstandings in Scripture come from translation gaps between original Hebrew, Greek, and modern language usage. Discover why meaning often shifts.",
        "hero_image": "/static/images/taro_root.jpg",
        "body_md": (
            "## Why Many People Misunderstand Scripture When Reading Translations Alone\n\n"
            "### Most Readers Start With a Translation\n\n"
            "For most people, the only version of Scripture they ever read is a translated one.\n\n"
            "That is not a problem in itself. Translations make Scripture accessible. They have carried the text across centuries and cultures.\n\n"
            "But translation is not the same as the original.\n\n"
            "And when readers treat a translation as if it were identical to the source, gaps begin to appear — gaps that accumulate into confusion, misapplication, and sometimes serious misunderstanding.\n\n"
            "---\n\n"
            "### Language Shifts Over Time\n\n"
            "English is not a fixed language. Words that meant one thing in the 1600s carry different weight today.\n\n"
            "Words like \"charity,\" \"conversation,\" \"ghost,\" and \"prevent\" all appear in older translations with meanings that modern readers would not recognize without a footnote.\n\n"
            "This creates a quiet problem: readers assume they understand what a passage says because the words are familiar — but the meaning behind those words has drifted.\n\n"
            "This happens even more dramatically when moving from the original Hebrew and Greek into any English rendering.\n\n"
            "---\n\n"
            "### Hebrew and Greek Carry Layered Meaning\n\n"
            "Both Hebrew and Greek are languages with a depth of structure that English does not replicate cleanly.\n\n"
            "In Hebrew, a single root word can carry relational, physical, and spiritual dimensions simultaneously. The word used for \"know,\" for example, is not merely intellectual. It describes intimate relationship, direct experience, and covenant connection — all in one term.\n\n"
            "In Greek, words for love, time, word, and spirit each carry specific distinctions that single English words flatten.\n\n"
            "When a translator chooses one English word for a layered original term, something is always compressed.\n\n"
            "---\n\n"
            "### Translation Simplifies to Communicate\n\n"
            "Translators face an unavoidable tension.\n\n"
            "They must render a text legible in the target language while preserving meaning from the source language. These goals sometimes conflict.\n\n"
            "A word-for-word rendering can be accurate but unreadable. A meaning-for-meaning rendering can be readable but interpretive.\n\n"
            "Every translation makes thousands of small choices. Each choice reflects both scholarship and perspective. And across different translation teams, those choices produce meaningfully different texts — which is why comparing translations sometimes reveals more questions than answers.\n\n"
            "---\n\n"
            "### The Need for Original Language Understanding\n\n"
            "This is not an argument against translations. It is a case for going deeper.\n\n"
            "Readers who want to understand what was actually written — not just what was rendered — benefit from access to original language meaning.\n\n"
            "Not to rewrite the text. Not to create new doctrine. But to see the fuller picture behind the word that was chosen.\n\n"
            "That kind of understanding changes how a passage lands. It opens layers that translation, by necessity, had to close.\n\n"
            "---\n\n"
            "### A Tool Built for This Purpose\n\n"
            "The Scripture Language Insight Tool was built to make original Hebrew and Greek meaning accessible — without requiring years of seminary training.\n\n"
            "Input a word or verse. See the original term. Understand its meaning, usage, and context in the language it was written in.\n\n"
            "[**Use the Scripture Language Tool →**](/scripture-tools/hebrew-greek-meaning-tool)\n\n"
            "[**What Changes When You Understand Original Language →**](/scripture-tools/original-language-meaning)\n\n"
            "---\n\n"
            "[**Free Aloha Wellness Guide →**](/download/aloha_wellness_freebie)"
        ),
    },
    ("scripture-tools", "original-language-meaning"): {
        "title": "What Changes When You Understand the Original Hebrew and Greek Meaning",
        "meta_description": "Understanding original Hebrew and Greek words reveals deeper context and meaning often lost in translation.",
        "hero_image": "/static/images/taro_root.jpg",
        "body_md": (
            "## What Changes When You Understand the Original Hebrew and Greek Meaning\n\n"
            "### Reading Is Not the Same as Understanding\n\n"
            "Most people who read Scripture regularly are reading a translation.\n\n"
            "That translation was produced by scholars who made careful choices — but choices nonetheless. Every English word selected to represent a Hebrew or Greek original carried a range of possible meanings, and the one chosen reflects a particular interpretation of context.\n\n"
            "Reading gives you the rendered text.\n\n"
            "Understanding the original language gives you the source.\n\n"
            "---\n\n"
            "### Why Original Words Matter\n\n"
            "Words in Hebrew and Greek were not interchangeable the way English words sometimes are.\n\n"
            "Hebrew is a concrete, relational language. Its words are grounded in physical experience and covenant relationship. Abstract concepts are expressed through tangible imagery.\n\n"
            "Greek, particularly the Koine Greek of the New Testament era, was precise and structured. It distinguished between concepts that English collapses into a single term.\n\n"
            "When you know what word was actually used — and what that word meant in its original context — the passage opens.\n\n"
            "---\n\n"
            "### Where Meaning Deepens\n\n"
            "Consider words that appear simple in translation but carry significant depth in the original:\n\n"
            "- Words for \"love\" in Greek describe different relational qualities — familial, unconditional, friendship, and romantic — each distinct, each used intentionally in different passages\n"
            "- Words for \"peace\" in Hebrew often carry the meaning of wholeness, completion, and covenant alignment — not merely the absence of conflict\n"
            "- Words for \"righteousness\" in both languages often describe relational right-standing rather than moral performance\n\n"
            "None of these are doctrinal claims. They are language observations — the kind that change how a reader sits with a passage.\n\n"
            "---\n\n"
            "### How Translation Compresses Meaning\n\n"
            "Translators work under real constraints.\n\n"
            "They must produce text that reads naturally in the target language. They must make choices quickly across thousands of words. And they must balance faithfulness to the source with readability for the audience.\n\n"
            "The result is that layered words get reduced to single English equivalents. Nuance that was present in the original is not always recoverable from the translation alone.\n\n"
            "This is not a failure of translators. It is the nature of translation.\n\n"
            "---\n\n"
            "### The Value of Word Study\n\n"
            "Original language word study does not require fluency in Hebrew or Greek.\n\n"
            "It requires access to the original terms and their documented meanings — the kind of information that scholars have preserved in lexicons, concordances, and reference tools for centuries.\n\n"
            "What changes when you do this kind of study:\n\n"
            "- Passages that felt flat gain dimension\n"
            "- Phrases that seemed contradictory become coherent\n"
            "- Concepts that felt abstract become grounded\n"
            "- Understanding becomes more personal and less dependent on secondhand interpretation\n\n"
            "---\n\n"
            "### A Tool That Makes This Accessible\n\n"
            "The Scripture Language Insight Tool was built to bring original Hebrew and Greek meaning into reach for everyday readers.\n\n"
            "No seminary training required. No original language fluency needed.\n\n"
            "Input a word or passage. Receive the original term, its meaning, and its usage context.\n\n"
            "[**Use the Scripture Language Tool →**](/scripture-tools/hebrew-greek-meaning-tool)\n\n"
            "[**Why Translations Create Gaps →**](/scripture-tools/translation-gap-in-scripture)\n\n"
            "---\n\n"
            "[**Aloha Wellness Book →**](/aloha_wellness)"
        ),
    },
    ("scripture-tools", "hebrew-greek-meaning-tool"): {
        "title": "How the Scripture Language Insight Tool Helps You Understand What Was Actually Written",
        "meta_description": "A simple tool that reveals original Hebrew and Greek meanings behind Scripture words so readers can understand deeper context and intent.",
        "hero_image": "/static/images/taro_root.jpg",
        "body_md": (
            "## How the Scripture Language Insight Tool Helps You Understand What Was Actually Written\n\n"
            "### Scripture Contains Original Language Depth\n\n"
            "The text most readers encounter is a translation — a careful, scholarly rendering of words first written in Hebrew, Aramaic, and Greek.\n\n"
            "Those original languages carry meaning that translation does not always fully transfer. Words that appear simple in English often represent layered concepts in the source language. Understanding what was actually written requires access to what those original words meant.\n\n"
            "The Scripture Language Insight Tool was built for that purpose.\n\n"
            "---\n\n"
            "### What the Tool Does\n\n"
            "The tool is straightforward in design and purpose:\n\n"
            "**1. Input a verse or word**\n\n"
            "Enter the passage, verse reference, or specific word you want to explore.\n\n"
            "**2. See the original Hebrew or Greek term**\n\n"
            "The tool surfaces the original language word behind the English rendering — drawn from documented lexical sources.\n\n"
            "**3. Understand the original meaning and usage context**\n\n"
            "See what that word meant in its original context: its range of meaning, how it was commonly used, and what dimension of understanding it carries that translation may have compressed.\n\n"
            "---\n\n"
            "### What This Tool Does NOT Do\n\n"
            "This is important to state clearly.\n\n"
            "This tool does not rewrite Scripture.\n\n"
            "It does not generate new doctrine, alter the text, or replace any translation. It reveals what the original language source actually says — which is the foundation that all translations rest on.\n\n"
            "The goal is clarity, not revision.\n\n"
            "---\n\n"
            "### An Example of How This Works\n\n"
            "A reader encounters the word \"love\" in a familiar New Testament passage.\n\n"
            "In English, \"love\" is a single word used across many contexts. In the original Greek, that same passage may use a specific term — one of several distinct Greek words for love — each carrying a different quality of relationship or intention.\n\n"
            "Knowing which word was used, and what that word specifically means, does not change the text. It opens it. The reader now understands not just that love was described, but what kind of love, in what relational context, with what weight of meaning.\n\n"
            "That is the difference original language understanding makes.\n\n"
            "---\n\n"
            "### Why This Matters\n\n"
            "Readers who engage with original language meaning consistently report:\n\n"
            "- **Clearer understanding** — passages that were opaque become legible\n"
            "- **Reduced misinterpretation** — meaning becomes anchored to source rather than tradition or assumption\n"
            "- **Deeper insight into intent** — the writer's purpose becomes more visible when the words used are understood on their own terms\n\n"
            "This is not an academic exercise. It is a practical one — the kind that changes how a person reads, reflects, and applies what they find in the text.\n\n"
            "---\n\n"
            "### Begin with the Tool\n\n"
            "If you want to understand what was actually written — not just what was translated — this tool gives you a starting point.\n\n"
            "No prior language knowledge required.\n\n"
            "[**Use the Scripture Language Tool →**](/scripture-tools/hebrew-greek-meaning-tool)\n\n"
            "[**Why Translations Create Gaps →**](/scripture-tools/translation-gap-in-scripture)\n\n"
            "[**What Changes With Original Language Understanding →**](/scripture-tools/original-language-meaning)\n\n"
            "Want to go further than a single word or verse at a time? [**Kingdom Study Tools →**](/kingdom-study) walks through 73 original Hebrew and Greek word studies built for sustained Kingdom theology study.\n\n"
            "---\n\n"
            "[**Free Aloha Wellness Guide →**](/download/aloha_wellness_freebie)\n\n"
            "[**Aloha Wellness Book →**](/aloha_wellness)"
        ),
    },
    ("wellness", "eating-when-hungry"): {
        "title": "Eating When Hungry Instead of Eating by Schedule | Ke Aupuni O Ke Akua",
        "meta_description": "Discover the difference between eating by true hunger and eating by artificial schedule. Explore wellness rhythm, stewardship, and ancestral patterns.",
        "hero_image": "/static/images/ulu_kalo_mango.jpg",
        "body_md": (
            "## Eating When Hungry — Returning to the Body's Natural Rhythm\n\n"
            "### A Question Worth Asking\n\n"
            "When did you last eat because you were genuinely hungry — not because the clock said it was time, not because food was available, not because habit called it a meal hour?\n\n"
            "For most people in modern culture, the distinction barely registers. Eating has been organized around schedule, convenience, and social convention rather than around the body's actual signals. Breakfast arrives because it is breakfast time. Lunch follows the workday break. Dinner comes with the evening hour. True hunger — the body's own signal that nourishment is needed — often plays a smaller role than the calendar does.\n\n"
            "---\n\n"
            "### What Creation Reveals\n\n"
            "Observe any animal living outside a human-imposed feeding routine. It eats when its body signals hunger, stops when satisfied, and rests between meals. It does not eat at fixed intervals because the clock demands it. It does not consume beyond what its energy requires.\n\n"
            "This pattern is not primitive. It is extraordinarily functional. Creatures maintained this rhythm long before modern agriculture organized human life around scheduled mealtimes. Creation itself demonstrates that hunger is a reliable signal — and that trusting it may be more intelligent than overriding it with a schedule.\n\n"
            "---\n\n"
            "### How Ancestral Cultures Lived Differently\n\n"
            "The people of Molokaʻi and across the Hawaiian Islands did not organize their eating around a corporate meal schedule. Their eating was shaped by physical labor, by what the land and sea provided in season, and by the rhythm of the day and the demands of the work being done.\n\n"
            "They were not counting meals. They were responding to hunger — real hunger, earned through activity, satisfied through nourishment, and allowed to return naturally before eating again.\n\n"
            "The result was a lean and capable people. Not because they followed a wellness system, but because they lived in alignment with how the body was designed to function. That alignment produced health without programs, without tracking, without the anxiety that most modern eating culture creates.\n\n"
            "---\n\n"
            "### The Confusion Constant Eating Can Create\n\n"
            "When food is available at every hour and eating is tied to schedule rather than hunger, the body's natural signaling can become harder to read. The signals that once communicated true need become difficult to distinguish from habit, boredom, stress, or simple availability.\n\n"
            "Kahu Phil Stephens began observing this in his own life on Molokaʻi — noticing that eating by schedule often meant eating before genuine hunger arrived. The shift came not from a diet program but from a simple question: am I actually hungry, or is it simply time?\n\n"
            "That question, asked consistently and honestly, began to restore a different relationship with food. One built on awareness rather than routine.\n\n"
            "---\n\n"
            "### This Is Not About Restriction\n\n"
            "Eating when hungry is not starvation. It is not extreme fasting. It is not a system requiring tracking or measuring. It is not a diet at all in the modern sense.\n\n"
            "It is the opposite of restriction — it is trust. Trust that the body will signal when it needs nourishment. Trust that waiting for real hunger is not dangerous but natural. Trust that stopping when satisfied rather than when the plate is empty is sufficient.\n\n"
            "Rhythm and awareness guide this approach. Rules do not.\n\n"
            "---\n\n"
            "### Stewardship of the Temple\n\n"
            "From a Kingdom perspective, how you eat is a stewardship question. The body is a gift entrusted to your care. Stewarding that gift faithfully means paying attention to what it actually needs — not simply feeding it according to cultural convention or commercial habit.\n\n"
            "Stewardship requires discernment. In this case, discernment begins with learning to distinguish genuine hunger from the noise of modern food culture. That distinction, once recovered, opens a quieter and more sustainable path to physical wellbeing.\n\n"
            "---\n\n"
            "[**Explore the Wellness Ecosystem →**](/ecosystem)\n\n"
            "[**Ancestral Eating Patterns →**](/wellness/ancestral-eating-patterns)\n\n"
            "[**Is Three Meals a Day Necessary? →**](/wellness/three-meals-a-day-necessary)\n\n"
            "[**Scripture Study Tools →**](/scripture-tools/hebrew-greek-meaning-tool)\n\n"
            "---\n\n"
            "If this teaching is helping you, consider supporting the mission.\n\n"
            "[**Support the Ministry →**](/partner)"
        ),
    },
    ("wellness", "the-rotten-fencepost-principle"): {
        "title": "The Rotten Fencepost Principle: When the Foundation Is Off | Ke Aupuni O Ke Akua",
        "meta_description": "The Rotten Fencepost Principle: why problems keep repeating until the real foundation is fixed. This piece applies that principle to wellness -- one application of a larger framework.",
        "hero_image": "/static/images/molokai_ranch.jpg",
        "body_md": (
            "## The Rotten Fencepost Principle — When the Foundation Is Off\n\n"
            "*This article applies the [Rotten Fencepost Principle](/rotten-fencepost) to one specific area of life: wellness. "
            "The principle itself isn't a wellness program — it's a way of finding hidden causes behind recurring problems in "
            "health, finances, relationships, leadership, faith, and everyday life. Wellness is simply where this article applies it.*\n\n"
            "### The Principle\n\n"
            "On a ranch, a fencepost set crooked does not stay crooked alone. Every wire, every rail, every post attached to it inherits the lean. By the time you have run a hundred yards of fence, the whole line is off — and finding the source of the problem requires going back, past all the later posts, to the one that started the drift.\n\n"
            "A rotten fencepost does the same thing. It looks stable. The wire holds. The fence seems to stand. But the foundation is compromised, and eventually everything it supports will lean with it.\n\n"
            "I learned this lesson working cattle on the land of Molokaʻi. And it applies directly to how modern wellness culture has been built.\n\n"
            "---\n\n"
            "### How Small Misunderstandings Create Widespread Confusion\n\n"
            "When the foundational assumptions of a system are flawed, every conclusion built on those assumptions inherits the error. This is not visible immediately. The system may appear to function for years before the drift becomes obvious.\n\n"
            "Modern wellness has built many structures on foundations that were never fully examined. The three-meals-a-day model was not developed from observation of the body's natural rhythms. The calorie-counting framework was built on mechanical assumptions about human metabolism that later research has repeatedly complicated. The diet industry runs on the premise that willpower and the right system are all that separate people from health — an assumption that decades of failure rates have not dislodged.\n\n"
            "The posts look stable. But something in the foundation has never been right.\n\n"
            "---\n\n"
            "### When Marketing Replaces Wisdom\n\n"
            "Part of what makes the fencepost problem persistent is that modern culture rewards new systems rather than examined foundations. A new diet, a new program, a new framework — each one offers a fresh start without requiring a return to the original misalignment.\n\n"
            "Marketing accelerates this. The next system is always more sophisticated, more targeted, more scientifically branded than the last. But if the foundational assumptions remain unexamined, the new post leans in the same direction as the old one.\n\n"
            "Wisdom, by contrast, is patient. It does not chase novelty. It goes back to the fence line and asks where the first post was set — and whether it was set correctly.\n\n"
            "---\n\n"
            "### What Creation and Simplicity Teach\n\n"
            "The natural world does not overcomplicate wellness. Animals maintain health through rhythm, movement, rest, and eating in alignment with genuine need. The complexity comes not from the body's design but from the systems humans impose on top of it.\n\n"
            "Hawaiian ancestral life was not simple because it lacked sophistication. It was grounded because it was rooted in the actual requirements of life on the land — physical work, food from the soil and sea, rest aligned with the rhythms of the day. Those foundations held for generations precisely because they were not built on assumptions that needed to be revised every decade.\n\n"
            "---\n\n"
            "### Stewardship Requires Questioning Foundations\n\n"
            "Kingdom stewardship is not passive. It does not accept inherited systems without examination. It asks whether the foundation is sound — whether the first post was set correctly — before extending the fence line further.\n\n"
            "Applied to wellness, this means asking not only which diet or program to follow, but whether the framework that produces diets and programs is itself trustworthy. And if it is not, where to go instead.\n\n"
            "The path back is not more complexity. It is return — to simpler foundations, older wisdom, and the kind of alignment that does not require constant revision.\n\n"
            "---\n\n"
            "[**Explore the Wellness Ecosystem →**](/ecosystem)\n\n"
            "[**Why Modern Health Advice Feels Confusing →**](/wellness/why-modern-health-advice-feels-confusing)\n\n"
            "[**Eating When Hungry →**](/wellness/eating-when-hungry)\n\n"
            "[**What Is the Kingdom of God? →**](/kingdom/what-is-the-kingdom-of-god)\n\n"
            "Want to apply this principle beyond wellness? [**The Rotten Fencepost Field Guide →**](/rotten-fencepost) walks through the same 3-question method for finding hidden causes in any area of life.\n\n"
            "---\n\n"
            "Continue learning through the wellness and Kingdom ecosystem.\n\n"
            "[**Support the Ministry →**](/partner)"
        ),
    },
    ("rotten-fencepost", "find-the-cause-not-the-symptoms"): {
        "title": "Find the Cause, Not the Symptoms — The Rotten Fencepost Principle | Ke Aupuni O Ke Akua",
        "meta_description": "Why do the same problems keep coming back? The Rotten Fencepost Principle explains why treating symptoms instead of causes guarantees they'll return — in health, finances, relationships, and leadership.",
        "hero_image": "/static/covers/find_the_cause_not_the_symptoms_cover_web.jpg",
        "body_md": (
            "## Find the Cause, Not the Symptoms\n\n"
            "If you've ever fixed the same problem twice, you already know something is wrong — not with the problem, but with the fix.\n\n"
            "Maybe it's a disagreement that keeps resurfacing with someone you love, no matter how many times you've \"resolved\" it. Maybe it's a budget that balances for a month and then quietly falls apart again. Maybe it's a project at work that keeps stalling in the same place, or a health complaint that fades and returns like clockwork.\n\n"
            "In each case, there's a natural instinct: fix what's visible. Smooth over the argument. Cover the shortfall. Push the deadline. Treat the symptom. And that instinct isn't wrong — sometimes the visible problem genuinely needs attention right now. But if that's the only thing that happens, the problem hasn't been solved. It's been postponed.\n\n"
            "---\n\n"
            "### The Rotten Fencepost\n\n"
            "I teach this idea through a simple, physical picture: a fencepost on a working ranch. From above the ground, a rotten post can look completely fine — the wire is taut, the post is upright, the fence appears sound. But below the soil line, where nothing is visible, the wood has been quietly rotting for months, sometimes years. The post holds — until, without warning, it doesn't. And when it fails, it often takes a stretch of fence line down with it, because everything attached to that post inherited its hidden weakness.\n\n"
            "That's the whole principle in one image: what looks fine on the surface can still be failing underneath, and the surface will eventually show it.\n\n"
            "---\n\n"
            "### Why This Shows Up Everywhere\n\n"
            "The rotten fencepost isn't just a metaphor for one kind of problem — it's a pattern that shows up almost anywhere something keeps failing in the same way:\n\n"
            "- **In health**, a symptom treated in isolation — pain, fatigue, a recurring flare-up — often returns because whatever is actually producing it was never addressed.\n"
            "- **In finances**, a budget \"fix\" that only rearranges numbers for one month doesn't survive the month after, because the underlying spending pattern or income gap is still there.\n"
            "- **In relationships**, the same argument keeps happening because the actual disagreement underneath it was smoothed over instead of resolved.\n"
            "- **In leadership and work**, the same project keeps stalling at the same stage because a structural or communication problem — not the individual failure everyone blames — was never fixed.\n\n"
            "Different surfaces. Same underlying pattern.\n\n"
            "---\n\n"
            "### A Simple Way to Find the Cause\n\n"
            "You don't need a framework or a consultant to start applying this. The exercise I teach is short enough to use on almost anything:\n\n"
            "1. Name the problem in one sentence — the thing that keeps recurring.\n"
            "2. Ask \"why did this happen?\" and write down the honest answer.\n"
            "3. Take that answer and ask \"why\" again. Keep going — usually four or five layers is enough — until you reach something that feels less like a circumstance and more like a real cause: a habit, a decision, an unspoken assumption, a structural gap.\n"
            "4. Choose one action this week that addresses that answer, not the original symptom.\n\n"
            "This is deliberately small. The goal isn't to solve everything at once — it's to stop patching the same rotten post and start dealing with what's actually underneath it.\n\n"
            "---\n\n"
            "### Going Deeper\n\n"
            "This article is a general introduction to the principle across everyday life. If you're specifically working through wellness and health patterns, the companion piece — [The Rotten Fencepost Principle: When the Foundation Is Off](/wellness/the-rotten-fencepost-principle) — applies the same idea directly to diet culture and modern health advice.\n\n"
            "For the full teaching — including the video this article accompanies and a growing library of Rotten Fencepost content — visit the [Rotten Fencepost hub](/rotten-fencepost). And if you want a structured way to work through this exercise for your own recurring problem, the companion guide, [*Find the Cause, Not the Symptoms: A Rotten Fencepost Foundational Guide*](/product/prod_find_the_cause_not_the_symptoms), walks through the method in full, with a workbook you can use on a real situation in your own life.\n\n"
            "The next time you find yourself fixing the same problem for the second or third time, pause before you patch it again. Ask what's actually rotting underneath — and go find the cause, not just the symptom.\n\n"
            "---\n\n"
            "[**Get the Rotten Fencepost Field Guide →**](/rotten-fencepost)\n\n"
            "[**Support the Ministry →**](/partner)"
        ),
    },
    ("wellness", "kupuna-wisdom-and-modern-health"): {
        "title": "Kupuna Wisdom and Modern Health | Ke Aupuni O Ke Akua",
        "meta_description": "Explore how Hawaiian kupuna wisdom, stewardship, simplicity, and rhythm can help modern people rethink wellness and health.",
        "hero_image": "/static/images/breadfruit.jpg",
        "body_md": (
            "## Kupuna Wisdom and Modern Health\n\n"
            "### What the Elders Knew\n\n"
            "Kupuna — the Hawaiian word for elders, grandparents, and those who carry ancestral knowledge — were not wellness experts in the modern sense. They had no degrees in nutrition or fitness science. They did not publish protocols or sell programs.\n\n"
            "What they had was something that modern wellness culture consistently struggles to replicate: a way of living that kept people healthy across generations, not through intervention but through alignment.\n\n"
            "Their wisdom was practical and grounded. It emerged from a deep relationship with the land, the sea, and the rhythms of creation. And it included principles that modern health research is only now beginning to rediscover.\n\n"
            "---\n\n"
            "### Living in Rhythm With Life\n\n"
            "The foundation of kupuna wisdom was not a set of rules. It was a relationship — with the land, with the seasons, with the body's natural cycles, and with the community that sustained daily life.\n\n"
            "Eating followed the rhythms of what the land and sea provided. Movement was not separate from life — it was life, built into the labor of farming, fishing, and building. Rest came with the darkness. Work came with the light. The body was not managed. It was lived in.\n\n"
            "This is not nostalgia. It is a recognition that the body was designed to function within rhythms — and that health tends to follow when those rhythms are honored rather than overridden.\n\n"
            "---\n\n"
            "### When Modern Systems Disconnect People From Stewardship\n\n"
            "Modern wellness culture, despite its sophistication, often moves people further from natural stewardship rather than closer to it. Programs create dependency on external structure. Tracking systems replace internal awareness. The focus on isolated variables can crowd out the simpler, more durable question of how to live in alignment with how the body was made.\n\n"
            "Kupuna wisdom did not fragment wellness into components. It understood health as a result of how life was lived as a whole — the food, the work, the rest, the relationships, the spiritual grounding, and the relationship with the land.\n\n"
            "When one piece of that whole is addressed in isolation, the results tend to be partial and temporary. When the whole is addressed, something more lasting becomes possible.\n\n"
            "---\n\n"
            "### Wellness Includes More Than the Physical\n\n"
            "The elders understood that the body does not exist in isolation from the soul, the mind, and the community. Wellness that addresses only the physical while ignoring the emotional and spiritual dimensions of a person will always be incomplete.\n\n"
            "Hawaiian tradition held that mana — spiritual strength and vitality — was connected to how a person lived in relationship: with the Creator, with the land, with their family, and with their own kuleana, their responsibility and purpose. A person disconnected from those relationships was understood to be vulnerable in ways that no amount of physical attention could fully address.\n\n"
            "True wellness, in the kupuna understanding, was never only about the body. It was about the whole person living in right relationship with life.\n\n"
            "---\n\n"
            "### Simplicity and Sustainability\n\n"
            "The most durable health practices are the ones simple enough to continue indefinitely. Kupuna wisdom was sustainable across generations not because it was unchanging, but because it was built on foundations that do not require constant revision — the body's natural hunger rhythms, physical work, rest, whole food from the land, and spiritual grounding.\n\n"
            "Modern wellness culture tends to move in the opposite direction: more complexity, more tracking, more interventions. Each new system promises more than the last. Most cannot be sustained for a year, let alone a generation.\n\n"
            "The path toward lasting wellness may not be forward into greater complexity. It may be back — toward the simpler, more grounded understanding of health that the kupuna carried and practiced.\n\n"
            "---\n\n"
            "[**Explore the Wellness Ecosystem →**](/ecosystem)\n\n"
            "[**Ancestral Eating Patterns →**](/wellness/ancestral-eating-patterns)\n\n"
            "[**The Rotten Fencepost Principle →**](/wellness/the-rotten-fencepost-principle)\n\n"
            "[**Scripture Study Tools →**](/scripture-tools/hebrew-greek-meaning-tool)\n\n"
            "---\n\n"
            "Explore the broader ecosystem and teachings.\n\n"
            "[**Support the Ministry →**](/partner)"
        ),
    },
    ("kingdom", "understanding-scripture-through-original-words"): {
        "title": "Understanding Scripture Through Original Hebrew and Greek Words | Ke Aupuni O Ke Akua",
        "meta_description": "Learn why understanding original Hebrew and Greek words can deepen Scripture study without changing the Bible itself.",
        "hero_image": "/static/images/bible_scroll.jpg",
        "body_md": (
            "## Understanding Scripture Through Original Hebrew and Greek Words\n\n"
            "### Reading Is Not the Same as Understanding\n\n"
            "There is a difference between reading a text and understanding what it actually says. That difference becomes most significant when the text was written in a language other than the one you are reading.\n\n"
            "Scripture was written in Hebrew, Aramaic, and Greek. What most readers encounter today is a translation — a careful, scholarly rendering produced centuries after the original, in a language whose relationship to the source text is never fully transparent.\n\n"
            "A translation gives access to the text. It does not give direct access to the words themselves.\n\n"
            "---\n\n"
            "### What Ancient Language Carried\n\n"
            "Words in ancient Hebrew and Greek were not thin containers for simple ideas. They carried layered meaning rooted in culture, history, covenant relationship, and the structure of the language itself.\n\n"
            "The Hebrew word most often translated as \"know\" does not describe intellectual awareness alone. It describes intimate relationship, direct experience, and the kind of understanding that comes from covenant connection. When Scripture says that God knew a person, or that a person knew God, the depth of that word in the original language far exceeds what the English rendering conveys.\n\n"
            "The Greek vocabulary of the New Testament carried similar precision. Words for love, time, peace, righteousness, and power each had specific ranges of meaning that the Greek-speaking world understood — ranges that a single English translation word often cannot fully hold.\n\n"
            "When those words are flattened into single English equivalents, something is compressed. The text remains. The depth is reduced.\n\n"
            "---\n\n"
            "### Cultural and Governmental Context\n\n"
            "Ancient Hebrew developed within a culture shaped by covenant relationship — between a people and their God, between families and the land, between generations and the promises made to them. That covenantal framework colors every word. Law, justice, righteousness, and blessing all carry dimensions of covenant meaning that a reader unfamiliar with that world will miss.\n\n"
            "Greek, particularly the Koine Greek of the New Testament era, was shaped by the governmental and philosophical world of the first century. Words like *basileia* (kingdom), *ekklesia* (assembly), and *kurios* (lord) carried specific governmental weight that Greek-speaking listeners understood immediately — weight that modern translations often reduce to religious language stripped of its original force.\n\n"
            "Understanding what those words meant in their original context is not an academic exercise. It changes how the text is heard.\n\n"
            "---\n\n"
            "### The Goal Is Clarity, Not Revision\n\n"
            "Studying original language meaning is not about rewriting Scripture or producing new doctrine. The text is not being changed. The original words are not being replaced.\n\n"
            "The goal is to see more clearly what is already there — to recover the dimension of meaning that translation, by necessity, had to compress. Faithful translation is a gift. Original language study is a companion to that gift, not a rejection of it.\n\n"
            "Approaching the text with humility is essential. The purpose is deeper understanding of what was written, not the construction of alternative readings. The original words are the foundation. Understanding them more fully serves the text.\n\n"
            "---\n\n"
            "### Language Shapes Understanding\n\n"
            "Every language frames reality in a particular way. The categories available in Hebrew are not the same categories available in modern English. Concepts that ancient Israelites held in a single word sometimes require paragraphs to unpack in Western thought — and those paragraphs can still miss something.\n\n"
            "When readers understand which original word is behind the English rendering they are reading, they gain access to the frame. They begin to see not just what the translation chose to say, but what the original writer actually expressed.\n\n"
            "That shift in understanding does not diminish the translated text. It adds light to it.\n\n"
            "---\n\n"
            "[**Scripture Study Tools →**](/scripture-tools/hebrew-greek-meaning-tool)\n\n"
            "[**Explore the Kingdom Ecosystem →**](/ecosystem)\n\n"
            "[**What Is the Kingdom of God? →**](/kingdom/what-is-the-kingdom-of-god)\n\n"
            "[**The Kingdom Message of Jesus →**](/kingdom/jesus-kingdom-message)\n\n"
            "For a deeper, guided study across 73 original Hebrew and Greek words, explore [**Kingdom Study Tools →**](/kingdom-study).\n\n"
            "---\n\n"
            "Explore the Scripture study tools and Kingdom ecosystem.\n\n"
            "[**Support the Ministry →**](/partner)"
        ),
    },
    ("wellness", "god-never-told-adam-when-to-eat"): {
        "title": "God Never Told Adam When to Eat — And That Changes Everything",
        "meta_description": "In Genesis, God gave mankind everything to eat — but never a schedule. Explore what creation itself teaches us about hunger, rhythm, and wellness stewardship.",
        "hero_image": "/static/images/taro_root.jpg",
        "body_md": (
            "## God Never Told Adam When to Eat — And That Changes Everything\n\n"
            "### Abundance Without a Schedule\n\n"
            "In the opening chapters of Genesis, God provided abundantly. Every tree, every fruit, every living thing was given for nourishment. But something is missing from that provision — and that missing piece may be one of the most important wellness insights in all of Scripture.\n\n"
            "God never told Adam and Eve when to eat. He never told them how much.\n\n"
            "There is no schedule in the garden. No breakfast, lunch, and dinner. No portioned plate. No clock on the wall telling them it was time. Just abundance, awareness, and the freedom to live in rhythm with their own bodies and with creation.\n\n"
            "---\n\n"
            "### What Creation Itself Teaches\n\n"
            "Look at the rest of creation and you will see the same pattern. Animals do not eat by schedule. Birds do not set alarms. Fish do not count calories. Every living thing — from the largest animal to the smallest insect, from the tallest tree to the smallest plant — consumes only what it needs, when it needs it. Creation itself is the teacher.\n\n"
            "This is not a minor detail. It is a consistent pattern written into the fabric of how life was designed to function. The body's hunger signals are not obstacles to manage. They are a form of wisdom — the same wisdom that guides every other living creature toward nourishment without needing a program to follow.\n\n"
            "---\n\n"
            "### What Changed When Modern Life Arrived\n\n"
            "Something changed when modern life arrived. Schedules were built around work shifts, industrial routines, and marketing systems that told people when to be hungry. Three meals a day became a cultural rule rather than a natural rhythm. And quietly, over generations, people stopped listening to their bodies and started listening to the clock.\n\n"
            "The three-meal structure did not emerge from Scripture. It did not come from ancestral Hawaiian wisdom or from any ancient understanding of how the body functions. It came from industrialization — factory workers needing to eat on a fixed schedule tied to shift breaks.\n\n"
            "Before that structure was imposed, human beings ate differently. They ate when genuinely hungry, in amounts that matched their activity, from food available in the season. There was rhythm — not schedule.\n\n"
            "---\n\n"
            "### Returning to Simplicity\n\n"
            "This is not about extreme dieting or skipping meals to suffer. This is about returning to something simpler — the awareness that your body was designed with wisdom, and that wisdom does not need a schedule to function.\n\n"
            "Eating when hungry rather than eating by clock is not deprivation. It is trust. Trust that the body will signal genuine need. Trust that waiting for real hunger is natural rather than dangerous. Trust that stopping when satisfied is sufficient.\n\n"
            "Creation modeled this from the beginning. The garden demonstrated it. The ancestral peoples who lived closest to the land understood it in practice across generations.\n\n"
            "---\n\n"
            "### Kingdom Stewardship Begins With Listening\n\n"
            "Kingdom health begins with stewardship. And stewardship begins with listening — to creation, to your body, and to the One who designed both.\n\n"
            "The body is not the enemy. It is a gift entrusted to your care. Stewarding that gift faithfully means paying attention to what it actually needs — not simply feeding it according to a schedule someone else designed for a different era and a different way of life.\n\n"
            "What God placed in the garden was not just food. It was a demonstration of how life was meant to be lived — with awareness, with rhythm, and with the freedom to respond to real need rather than artificial demand.\n\n"
            "---\n\n"
            "[**Is Three Meals a Day Necessary? →**](/wellness/three-meals-a-day-necessary)\n\n"
            "[**Ancestral Eating Patterns →**](/wellness/ancestral-eating-patterns)\n\n"
            "[**Eating When Hungry →**](/wellness/eating-when-hungry)\n\n"
            "[**What Is the Kingdom of God? →**](/kingdom/what-is-the-kingdom-of-god)\n\n"
            "[**Explore the Ke Aupuni Ecosystem →**](/ecosystem)\n\n"
            "---\n\n"
            "If this teaching is helping you see wellness differently, explore the full Aloha Wellness teaching or support this ministry so these resources can keep reaching people who need them.\n\n"
            "[**Aloha Wellness Book →**](/aloha_wellness)\n\n"
            "[**Support the Ministry →**](/partner)"
        ),
    },
    ("kingdom", "stewardship-in-the-kingdom-of-god"): {
        "title": "Stewardship in the Kingdom of God | Ke Aupuni O Ke Akua",
        "meta_description": "Discover how stewardship, responsibility, and service connect to the message of the Kingdom of God.",
        "hero_image": "/static/images/sunlight_bursting.jpg",
        "body_md": (
            "## Stewardship in the Kingdom of God\n\n"
            "### A Practical Kingdom\n\n"
            "Much of what passes for Kingdom theology is theoretical — a framework for understanding church structure or doctrinal categories. The Kingdom is discussed as a concept and preached as a future destination.\n\n"
            "But the Kingdom message of Jesus was radically practical. It was concerned with how people lived now — how they related to one another, how they used their resources, how they treated those in need, how they stewarded what had been entrusted to them. Stewardship was not a footnote to the Kingdom message. It was central to it.\n\n"
            "---\n\n"
            "### What Stewardship Actually Means\n\n"
            "Stewardship is not ownership. It is the faithful management of something entrusted to you by another.\n\n"
            "In the Kingdom of God, this principle applies to everything. The earth belongs to God — human beings are stewards of it. Resources belong to the King — citizens of the Kingdom are managers of what has been placed in their care. The body is a gift from the Creator — the one who receives it is responsible for its care.\n\n"
            "This reframes the question from what do I have to how well am I managing what has been given to me. The shift is not subtle. It changes the entire orientation of life — from accumulation and control to faithfulness and fruitfulness.\n\n"
            "---\n\n"
            "### Stewardship Extends Across All of Life\n\n"
            "The scope of stewardship in the Kingdom is not limited to money or material resources. Jesus addressed the stewardship of time, of talent, of relationships, of truth, of physical health, and of calling.\n\n"
            "The Parable of the Talents was not a lesson in investment strategy. It was a statement about what faithfulness looks like across every domain of life entrusted to Kingdom citizens. The servants who multiplied what they were given were commended not for their technique but for their faithfulness to the trust. The servant who buried his gift out of fear was not rebuked for failure to produce — he was rebuked for failure to steward.\n\n"
            "Fear produces inaction. Faithful stewardship produces fruitfulness. And fruitfulness, in the Kingdom economy, is the measure of faithfulness.\n\n"
            "---\n\n"
            "### The Kingdom Is Not Merely Theoretical\n\n"
            "The message of stewardship lands differently when it is understood as a Kingdom principle rather than a religious obligation. Religious obligation produces compliance — doing the minimum required to satisfy the requirement. Kingdom stewardship produces engagement — the genuine desire to manage well what the King has entrusted, because the relationship with the King makes faithfulness worthwhile.\n\n"
            "Service and responsibility matter in the Kingdom because citizens carry the King's authority and represent the King's character. Stewardship is therefore not merely personal management. It is a form of service — to the King, to the community, and to the generation that will receive what is built or neglected.\n\n"
            "Wisdom in this context does not elevate the one who possesses it. It serves those who need it.\n\n"
            "---\n\n"
            "### The Body as a Stewardship Priority\n\n"
            "Stewardship includes the physical body — something the Kingdom message addresses directly and something that wellness teachings rooted in Scripture take seriously.\n\n"
            "The body is not incidental to Kingdom life. It is the vessel through which Kingdom citizens work, serve, build, and love. Neglecting the body is a stewardship failure in the same way that neglecting a resource or a talent is. Caring for it wisely is an act of faithfulness.\n\n"
            "This is why the wellness dimension of Kingdom teaching is not separate from the theological dimension. They arise from the same root: the understanding that everything entrusted to you is the King's, and that faithful management of all of it — resources, relationships, body, mind, and community — is what Kingdom citizenship looks like in practice.\n\n"
            "---\n\n"
            "[**Explore the Kingdom Ecosystem →**](/ecosystem)\n\n"
            "[**What Is the Kingdom of God? →**](/kingdom/what-is-the-kingdom-of-god)\n\n"
            "[**Biblical Stewardship Principles →**](/wealth/biblical-stewardship-principles)\n\n"
            "[**Scripture Study Tools →**](/scripture-tools/hebrew-greek-meaning-tool)\n\n"
            "---\n\n"
            "Continue exploring the Kingdom ecosystem and teachings.\n\n"
            "[**Support the Ministry →**](/partner)"
        ),
    },
}


@pages_bp.route("/<parent>/<slug>")
def seo_subpage(parent, slug):
    page = _SEO_PAGES.get((parent, slug))
    if not page:
        abort(404)
    data = load_content()
    nav_items = get_nav_items(data)
    page_url = SITE_URL + request.path
    # Article, not WebPage: these 18 pages are genuinely article-shaped
    # (headline, body, single author). No datePublished/dateModified --
    # no reliable dates exist anywhere in this site's data.
    page_schema = build_article_schema(
        headline=page.get("title"),
        description=page.get("meta_description"),
        url=page_url,
        image_url=_abs_image(page.get("hero_image")),
    )
    # 2-level breadcrumb only (Home -> Article). A 3-level "Home -> Wellness
    # -> Article" would require a real /wellness index page to link the
    # middle level to -- none exists, and inventing one just for the
    # breadcrumb would be exactly the fabrication the work order prohibits.
    breadcrumb_schema = build_breadcrumb_schema([
        ("Home", SITE_URL + "/"),
        (page.get("title"), page_url),
    ])
    return render_template(
        "page.html",
        page=page,
        nav_items=nav_items,
        body_html=md_to_html(page.get("body_md", "")),
        current_page=f"{parent}/{slug}",
        logo_path=LOGO_PATH,
        logo_height=LOGO_HEIGHT,
        footer_text=FOOTER_TEXT,
        founding_reader_remaining=data.get("founding_reader_remaining", 100),
        page_schema=page_schema,
        breadcrumb_schema=breadcrumb_schema,
    )


# ===== SITEMAP AND ROBOTS.TXT FOR GOOGLE/BING INDEXING =====

@pages_bp.route("/sitemap.xml")
def sitemap():
    """XML sitemap so Google and Bing can find and index all pages.

    No <lastmod> is emitted (see Work Order 005 / GOOGLE_VISIBILITY_READINESS_AUDIT.md):
    this app has no per-page modification timestamp anywhere in its data model
    (content lives in hardcoded dicts in content.py and this file, with no
    "last updated" field), so there is no real date to report. The prior
    implementation stamped every URL with today's date on every request,
    which is not a modification date at all -- it just always said "today."
    <lastmod> is optional per the sitemap protocol; omitting it is honest,
    omitting it is safer than fabricating one, and it costs nothing indexing-wise.

    Deliberately excluded product ids (Work Order 009 audit): `rotten_fencepost_field_guide`
    is not listed under /product/<id> because /rotten-fencepost is already its
    canonical, indexed sales page -- listing both would be near-duplicate content
    for the same item. `partner_tier1`-`partner_tier4` are not listed because
    /partner is the canonical entry point for donation tiers; the individual
    /product/partner_tierN pages exist for checkout plumbing, not as distinct
    content, matching the same call already made in GOOGLE_VISIBILITY_READINESS_AUDIT.md.

    Discovery Operations campaign pages (Work Order P-001, generic
    /campaign/<id> route sourced from content.py's CAMPAIGNS dict) are
    listed manually here too, same as every other section of this list --
    add one line per new campaign (e.g. "/campaign/002") when it publishes.
    """
    pages = [
        ("/",                   "1.0", "weekly"),
        ("/kingdom_wealth",     "0.9", "weekly"),
        ("/free_booklets",      "0.9", "weekly"),
        ("/kingdom_keys",       "0.9", "weekly"),
        ("/call_to_repentance", "0.9", "weekly"),
        ("/aloha_wellness",     "0.9", "weekly"),
        ("/pastor_planners",    "0.8", "monthly"),
        ("/nahenahe_voice",     "0.8", "monthly"),
        ("/partner",            "0.8", "monthly"),
        ("/ecosystem",          "0.9", "weekly"),
        ("/author",             "0.6", "monthly"),
        ("/rotten-fencepost",   "0.9", "weekly"),
        ("/campaign/001",       "0.7", "monthly"),
        ("/campaign/002",       "0.7", "monthly"),
        ("/myron-golden",       "0.8", "weekly"),
        ("/aloha-wellness",     "0.8", "weekly"),
        ("/kingdom-study",                          "0.9", "weekly"),
        ("/products",                                "0.9", "weekly"),
        ("/product/prod_find_the_cause_not_the_symptoms", "0.8", "monthly"),
        ("/product/prod_aloha_wellness",             "0.8", "monthly"),
        ("/product/prod_kingdom_booklet1",           "0.8", "monthly"),
        ("/product/prod_kingdom_booklet2",           "0.8", "monthly"),
        ("/product/prod_nahenahe_cd",                "0.8", "monthly"),
        ("/wellness/why-diets-fail",               "0.8", "monthly"),
        ("/wellness/lose-weight-without-dieting",  "0.8", "monthly"),
        ("/wellness/three-meals-a-day-necessary",  "0.8", "monthly"),
        ("/wellness/ancestral-eating-patterns",              "0.8", "monthly"),
        ("/wellness/why-modern-health-advice-feels-confusing", "0.8", "monthly"),
        ("/wellness/why-your-body-resists-diets",            "0.8", "monthly"),
        ("/kingdom/what-is-the-kingdom-of-god",              "0.8", "monthly"),
        ("/kingdom/jesus-kingdom-message",         "0.8", "monthly"),
        ("/wealth/biblical-stewardship-principles","0.8", "monthly"),
        ("/scripture-tools/hebrew-greek-meaning-tool",       "0.8", "weekly"),
        ("/scripture-tools/translation-gap-in-scripture",    "0.8", "monthly"),
        ("/scripture-tools/original-language-meaning",       "0.8", "monthly"),
        ("/wellness/eating-when-hungry",                              "0.8", "weekly"),
        ("/wellness/the-rotten-fencepost-principle",                  "0.8", "weekly"),
        ("/wellness/kupuna-wisdom-and-modern-health",                 "0.8", "weekly"),
        ("/kingdom/understanding-scripture-through-original-words",   "0.8", "weekly"),
        ("/kingdom/stewardship-in-the-kingdom-of-god",               "0.8", "weekly"),
        ("/wellness/god-never-told-adam-when-to-eat",                 "0.8", "weekly"),
        ("/rotten-fencepost/find-the-cause-not-the-symptoms",         "0.8", "weekly"),
        ("/rotten-fencepost/why-do-i-keep-starting-over",             "0.8", "weekly"),
    ]
    base_url = "https://keaupuniakeakua.faith"
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for path, priority, freq in pages:
        xml.append("  <url>")
        xml.append(f"    <loc>{base_url}{path}</loc>")
        xml.append(f"    <changefreq>{freq}</changefreq>")
        xml.append(f"    <priority>{priority}</priority>")
        xml.append("  </url>")
    xml.append("</urlset>")
    return Response("\n".join(xml), mimetype="application/xml")


@pages_bp.route("/robots.txt")
def robots():
    """Robots.txt tells search engines how to crawl the site."""
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /kahu\n"
        "Disallow: /admin\n"
        "\n"
        "Sitemap: https://keaupuniakeakua.faith/sitemap.xml\n"
    )
    return Response(content, mimetype="text/plain")


# ===== END SITEMAP SECTION =====

@pages_bp.route("/BingSiteAuth.xml")
def bing_verify():
    return send_from_directory('static', 'BingSiteAuth.xml', mimetype='application/xml')

@pages_bp.route("/<page_id>")
def page(page_id):
    if page_id in ("admin", "product", "checkout", "download", "paypal", "stripe", "kahu"):
        abort(404)
    data = load_content()
    pages = data.get("pages", {})
    if page_id not in pages:
        abort(404)
    return render_page(page_id, data)
