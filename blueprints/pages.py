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
        founding_reader_remaining=data.get("founding_reader_remaining", 100),
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

@pages_bp.route("/kingdom-study")
def kingdom_study():
    return render_template("kingdom_study.html")

@pages_bp.route("/aloha-wellness")
def aloha_wellness_funnel():
    data = load_content()
    youtube_embed_url = data.get("funnel_youtube_url", "https://www.youtube.com/embed/O_-J8t0NHLc")
    return render_template("aloha_wellness_funnel.html", youtube_embed_url=youtube_embed_url)

# ===== SEO ENTRY SUB-PAGES =====

_SEO_PAGES = {
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
        "title": "Lose Weight Without Dieting — Kingdom Wellness Principles",
        "meta_description": "Learn how Kahu Phil Stephens lost 54 pounds without dieting by following Kingdom wellness principles rooted in Scripture and ancestral Hawaiian wisdom.",
        "hero_image": "/static/images/food_basket.jpg",
        "body_md": (
            "## Lose Weight Without Dieting — The Kingdom Approach\n\n"
            "Kahu Phil Stephens is 67 years old. He has lived on Molokaʻi for over eight years. He lost 54 pounds — and he never went on a diet.\n\n"
            "What he did instead is documented in the **Aloha Wellness** book — and it starts with a question: *What did God actually design your body to do?*\n\n"
            "---\n\n"
            "### Why \"Going on a Diet\" Does Not Work\n\n"
            "A diet has a beginning and an end. That is the first problem.\n\n"
            "The moment you frame health as a temporary program, your body and mind begin counting the days until it is over. Every craving becomes a countdown. Every setback feels like failure. And when the diet ends — as it always does — the weight returns.\n\n"
            "Kingdom health does not work that way. The Kingdom is not a program. It is a **way of life** — a covenant rhythm that becomes natural over time.\n\n"
            "---\n\n"
            "### What Happened When a Hawaiian Pastor Stopped Dieting\n\n"
            "Living as a Paniolo (Hawaiian cowboy) on Molokaʻi, Kahu Phil was active. He worked the land. He rode horses. He pastored his community.\n\n"
            "But weight accumulated anyway — as it does for many men over 60 — until he encountered a set of Kingdom principles about eating that he had never heard taught in church.\n\n"
            "These principles were not complicated. They were **ancient**. They were embedded in Scripture, confirmed by the ancestral Hawaiian way of eating, and validated by what science is only now beginning to understand about meal timing, appetite, and metabolism.\n\n"
            "When Kahu Phil applied them, the weight came off — without counting calories, without eliminating food groups, without white-knuckling through hunger.\n\n"
            "---\n\n"
            "### The Principles Behind Effortless Change\n\n"
            "**Eat in alignment with your body's design, not against it.**\n"
            "Your body has natural rhythms — for hunger, for fullness, for digestion, for rest. When you eat with those rhythms instead of overriding them, your body stops storing excess and starts releasing it.\n\n"
            "**Let hunger be your signal, not the clock.**\n"
            "Modern eating culture ignores hunger signals. Three meals a day at fixed times — regardless of whether you are hungry — trains your body to eat by schedule rather than need. The Kingdom approach restores your body's natural intelligence.\n\n"
            "**Slow down the experience of eating.**\n"
            "How you eat matters as much as what you eat. Eating slowly, gratefully, and without distraction transforms the body's response to food. This is not mysticism — it is how God designed the digestive system.\n\n"
            "---\n\n"
            "### Ready to Begin?\n\n"
            "The full framework — including the practical daily system Kahu Phil uses — is in **Aloha Wellness: The Sacred Art of How You Eat**.\n\n"
            "---\n\n"
            "[**Get the Aloha Wellness Book →**](/aloha-wellness)"
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
            "[**Read Aloha Wellness — The Kingdom Approach to Health →**](/aloha-wellness)"
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
            "[**Read Aloha Wellness — The Kingdom Approach to Health →**](/aloha-wellness)"
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
}


@pages_bp.route("/<parent>/<slug>")
def seo_subpage(parent, slug):
    page = _SEO_PAGES.get((parent, slug))
    if not page:
        abort(404)
    data = load_content()
    nav_items = get_nav_items(data)
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
    )


# ===== SITEMAP AND ROBOTS.TXT FOR GOOGLE/BING INDEXING =====

@pages_bp.route("/sitemap.xml")
def sitemap():
    """XML sitemap so Google and Bing can find and index all pages."""
    pages = [
        ("/",                   "1.0", "weekly"),
        ("/kingdom_wealth",     "0.9", "weekly"),
        ("/free_booklets",      "0.9", "weekly"),
        ("/kingdom_keys",       "0.9", "weekly"),
        ("/call_to_repentance", "0.9", "weekly"),
        ("/aloha-wellness",     "0.9", "weekly"),
        ("/pastor_planners",    "0.8", "monthly"),
        ("/nahenahe_voice",     "0.8", "monthly"),
        ("/myron-golden",       "0.8", "weekly"),
        ("/kingdom-study",                          "0.9", "weekly"),
        ("/wellness/why-diets-fail",               "0.8", "monthly"),
        ("/wellness/lose-weight-without-dieting",  "0.8", "monthly"),
        ("/wellness/three-meals-a-day-necessary",  "0.8", "monthly"),
        ("/wellness/ancestral-eating-patterns",    "0.8", "monthly"),
        ("/kingdom/what-is-the-kingdom-of-god",    "0.8", "monthly"),
        ("/kingdom/jesus-kingdom-message",         "0.8", "monthly"),
        ("/wealth/biblical-stewardship-principles","0.8", "monthly"),
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
