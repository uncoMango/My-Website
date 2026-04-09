# content.py
import json
from datetime import datetime
from config import DATA_FILE, PRODUCTS_FILE, ORDER

DEFAULT_PAGES = {
    "funnel_youtube_url": "https://www.youtube.com/embed/O_-J8t0NHLc",
    "order": ORDER,
    "pages": {
        "home": {
            "title": "Ke Aupuni O Ke Akua - The Kingdom of God",
            "hero_image": "/static/images/molokai_coast.jpg",
            "body_md": "## What If Everything You Were Taught About Christianity Was Missing the Most Important Part?\r\n\r\nJesus mentioned the Kingdom of God **53 times**. He mentioned \"church\" **twice**.\r\n\r\nThere's a reason for that - and it changes everything.\r\n\r\n---\r\n\r\nI'm **Kahu Phil Stephens** - a pastor, Paniolo, and lifelong student of Scripture — studying the scriptures for almost 30 years and spending the last 5 years in the ancient Hebrew and Greek languages, writing to you from Moloka'i, Hawai'i.\r\n\r\nAfter three decades of study, I made a discovery that turned my faith upside down - in the best way. Jesus didn't come to start a religion. He came to establish a **Kingdom**. And that Kingdom has three dimensions that touch every part of your life.\r\n\r\n---\r\n\r\n### The Three Pillars of Ke Aupuni O Ke Akua\r\n\r\n**The Kingdom of God** - Rediscover what Jesus actually preached. Not church. Not religion. The revolutionary Kingdom message that transforms your mind, your identity, and your purpose.\r\n\r\n**[Explore the Kingdom Series](/call_to_repentance)**\r\n\r\n---\r\n\r\n**Kingdom Wellness** - Your body is not a burden. It is a temple - and the Kingdom has a design for it. Discover how a Paniolo pastor from Moloka'i lost 54 pounds without dieting, through a revelation rooted in Scripture and confirmed by a life on horseback.\r\n\r\n**[Discover Aloha Wellness](/aloha_wellness)**\r\n\r\n---\r\n\r\n**Kingdom Wealth** - The Kingdom operates on stewardship, not ownership. Learn the biblical principles of increase that most churches never teach.\r\n\r\n**[Learn Kingdom Wealth](/kingdom_wealth)**\r\n\r\n---\r\n\r\n### Start Here - FREE\r\n\r\nNot sure where to begin? Start with our **FREE Kingdom Keys** - short, powerful booklets drawn from almost 30 years of studying Scripture, including the last 5 years in the ancient Hebrew and Greek languages.\r\n\r\n**[Get Your FREE Kingdom Keys](/kingdom_keys)**\r\n\r\n*Aloha. You are in the right place.*",
            "product_url": "",
            "gumroad_url": "https://keaupuni.gumroad.com",
        },
        "kingdom_wealth": {
            "title": "Kingdom Wealth",
            "hero_image": "/static/images/scottsdale-mint-ATq9BSFebRE-unsplash.jpg",
            "body_md": "## Biblical Stewardship & Economic Increase\r\n\r\nMost churches teach you to tithe and wait. The Kingdom teaches something far more powerful - that you are a **steward** of God's resources, called to multiply what He has placed in your hands.\r\n\r\nI'm **Kahu Phil Stephens** - a pastor and Paniolo from Moloka'i, Hawai'i. After 30 years of studying Scripture in the original Greek and Hebrew, I discovered that the Bible has more to say about wealth, stewardship, and economic increase than most believers ever hear on Sunday morning.\r\n\r\n---\r\n\r\n### The Kingdom Wealth Difference\r\n\r\n**God is your Source - not your job, not your business, not the economy.** Understanding this one principle will change how you approach every financial decision you make.\r\n\r\nThe Kingdom operates on seedtime and harvest. On giving and receiving. On stewardship that multiplies rather than hoarding that stagnates.\r\n\r\n---\r\n\r\n### What You Will Discover\r\n\r\n**Source vs. Resource** - Why looking to your job or business as your source is the #1 mistake believers make - and what to do instead.\r\n\r\n**Kingdom Value** - How to create so much value for others that wealth flows naturally into your life as a byproduct of Kingdom service.\r\n\r\n**Stewardship Principles** - The biblical framework for managing money, time, and talent that produces generational increase.\r\n\r\n**The Offer** - How Kingdom people think about what they bring to the marketplace - and why it matters eternally.\r\n\r\n---\r\n\r\n### Start Your Kingdom Wealth Journey\r\n\r\n**[FREE Kingdom Keys Booklets](/kingdom_keys)** - Start here. Short, powerful, life-changing.\r\n\r\n**[FREE Kingdom Booklets](/free_booklets)** - Go deeper with our complete collection.\r\n\r\n**[The Complete Kingdom Series](/call_to_repentance)** - The full theological foundation.\r\n\r\n**[Myron Golden Kingdom Business Training](/myron-golden)** - Advanced Kingdom wealth principles for marketplace leaders.\r\n\r\n---\r\n\r\n*The Kingdom is not just about eternity. It is about how you live, work, and prosper today - for the glory of God and the blessing of your 'ohana.*",
            "product_url": "",
        },
        "aloha_wellness": {
            "title": "Aloha Wellness - Island Health & Healing",
            "hero_image": "/static/images/ulu_kalo_mango.jpg",
            "body_md": "## What If the Key to Your Health Was Never About What You Eat - But How?\r\n\r\nI lost **54 pounds** without dieting. No counting calories. No programs. No willpower battles.\r\n\r\nWhat changed? I discovered the **sacred art of how you eat** - a principle hidden in plain sight in Scripture, confirmed by 30 years of living as a Paniolo on the land of Moloka'i.\r\n\r\n---\r\n\r\nI'm **Kahu Phil Stephens** - a Native Hawaiian pastor, Paniolo, and 30-year student of Scripture. I've spent my life on horseback, on the land, connected to the rhythms God built into creation. And that connection taught me something the diet industry will never tell you.\r\n\r\n**Your body was designed by God. It already knows what to do. Your job is to stop fighting it.**\r\n\r\n---\r\n\r\n### The Aloha Wellness Book\r\n\r\nIn this book, I share the complete revelation that transformed my health - rooted in Hawaiian cultural wisdom, confirmed by Scripture, and proven by my own 54-pound transformation.\r\n\r\n**What you will discover:**\r\n\r\n- The Paniolo principle of eating that your great-grandparents knew - and modern culture forgot\r\n- Why the *how* of eating matters more than the *what*\r\n- The biblical design for your body that most health books completely miss\r\n- How Hawaiian cultural values like **aloha**, **pono**, and **mana** connect directly to physical wellness\r\n- Simple, sustainable practices that work with your body instead of against it\r\n\r\n---\r\n\r\n### This Is For You If...\r\n\r\n- You have tried every diet and nothing sticks\r\n- You feel like your body is fighting you\r\n- You want a health approach rooted in wisdom, not willpower\r\n- You are ready for a transformation that goes deeper than the scale\r\n\r\n---\r\n\r\n*Available now on Amazon and direct from Ke Aupuni O Ke Akua Press.*",
            "product_url": "https://a.co/d/6YrcnQp",
            "gumroad_url": "https://keaupuni.gumroad.com/l/aloha-wellness",
            "direct_buy_url": "/checkout/prod_aloha_wellness",
        },
        "call_to_repentance": {
            "title": "The Call to Repentance - The Kingdom Series",
            "hero_image": "/static/images/sunlight_bursting.jpg",
            "body_md": "## The Message Jesus Actually Preached\r\n\r\nWhen Jesus began His ministry, His first recorded words were: *'Repent, for the Kingdom of Heaven is at hand.'*\r\n\r\nNot 'join a church.' Not 'follow a religion.' Not 'say a prayer.'\r\n\r\n**The Kingdom of Heaven is at hand.**\r\n\r\nAnd yet - how many believers have ever been taught what the Kingdom actually is?\r\n\r\n---\r\n\r\nI'm **Kahu Phil Stephens** - a Native Hawaiian pastor and 30-year student of Scripture in the original Greek and Hebrew. This series is the fruit of three decades of digging into what Jesus actually said - not what religion translated it to mean.\r\n\r\n---\r\n\r\n### The Call to Repentance - Volume 1\r\n\r\nThe word *repentance* in Greek is **metanoia** - a complete transformation of the mind. Not sorrow. Not regret. A **total renovation of how you think**.\r\n\r\nWhen Jesus called people to repent, He was calling them to think differently about everything - about God, about themselves, about their purpose on this earth.\r\n\r\n**This book will challenge everything you thought you knew about:**\r\n\r\n- What repentance actually means in the original Greek\r\n- Why the Kingdom message is fundamentally different from church religion\r\n- How Jesus defined the Kingdom - and what that means for your life today\r\n- The three dimensions of Kingdom life: Spiritual, Physical, and Economic\r\n- Why Jesus mentioned Kingdom 53 times and church only twice\r\n\r\n---\r\n\r\n### The Kingdom Series\r\n\r\nThis is Volume 1 of a 54-volume theological series exploring every dimension of the Kingdom of God - drawn from 30 years of study in the original Greek and Hebrew scriptures.\r\n\r\n**The most comprehensive Kingdom theology series written from a Native Hawaiian perspective.**\r\n\r\n---\r\n\r\n*Published by Ke Aupuni O Ke Akua Press, Moloka'i, Hawai'i.*",
            "product_url": "https://a.co/d/fgbAVMs",
            "gumroad_url": "https://keaupuni.gumroad.com/l/call-to-repentance",
        },
        "pastor_planners": {
            "title": "Pastor Planners - Tools for Ministry Excellence",
            "hero_image": "/static/images/bible_scroll.jpg",
            "body_md": "## Organize Your Ministry with Purpose and Prayer\r\n\r\nBuilt for pastors who serve Pacific Islander and multilingual communities - these planners combine daily prayer, sermon preparation, pastoral care tracking, and ministry administration into one beautifully designed tool.\r\n\r\nCreated by **Kahu Phil Stephens** - pastor, teacher, and 30-year student of Scripture - these planners reflect the values of Kingdom ministry: intentionality, prayer, and faithful stewardship of the calling God has placed on your life.\r\n\r\n---\r\n\r\n### Available Editions\r\n\r\n**Ke Kauoha La Haku - Hawaiian Edition 2026**\r\nThe first pastoral planner designed specifically for Hawaiian-speaking ministers. Bilingual Hawaiian/English format with Hawaiian cultural values woven throughout.\r\n\r\n[Get on Amazon](https://a.co/d/gatnNET) | [Get on Gumroad](https://uncomango.gumroad.com/l/ulrmu)\r\n\r\n---\r\n\r\n**Tusi Fuataiaga a le Faifeau - Samoan Enhanced Edition 2026**\r\nDesigned for Samoan-speaking pastors and ministry leaders. Enhanced format with expanded planning sections and Samoan language throughout.\r\n\r\n[Get on Amazon](https://a.co/d/gs0WRPh) | [Get on Gumroad](https://uncomango.gumroad.com/l/ubzevn)\r\n\r\n---\r\n\r\n### What Makes These Planners Different\r\n\r\n- Designed by a working pastor who understands the daily demands of ministry\r\n- Native language editions that honor cultural identity\r\n- Integrates prayer, planning, and pastoral care in one place\r\n- Kingdom-centered framework - not just time management, but stewardship of calling\r\n- Professional quality suitable for gift-giving and ministry partnerships\r\n\r\n---\r\n\r\n*More language editions coming: Tongan, Fijian, Filipino, Japanese, and more.*\r\n\r\n*Published by Ke Aupuni O Ke Akua Press, Moloka'i, Hawai'i.*",
        },
        "nahenahe_voice": {
            "title": "The Nahenahe Voice of Nahono'opi'ilani - Musical Legacy",
            "hero_image": "/static/images/molokai_ranch.jpg",
            "body_md": "## Live from the Molokai Ranch Lodge - A Musical Legacy\r\n\r\nIn the year 2000, at the historic **Molokai Ranch Lodge**, something sacred was captured on recording.\r\n\r\nThe Nahenahe Voice of **Nahono'opi'ilani** - authentic Hawaiian music performed with the soul, spirit, and aloha that can only come from someone who has lived it.\r\n\r\n---\r\n\r\nThis is not a studio production polished for commercial appeal. This is the real voice of Hawai'i - intimate, powerful, and deeply rooted in the 'aina of Moloka'i.\r\n\r\n**Nahenahe** - the Hawaiian word for soft, gentle, and melodious. Music that moves not just the ears but the soul.\r\n\r\n---\r\n\r\n### The Recording\r\n\r\nRecorded live at the Molokai Ranch Lodge in 2000 - a venue that no longer exists in its original form, making this recording a true piece of living Hawaiian history.\r\n\r\nThese songs carry the mana of the land, the aloha of the people, and the spirit of a musical tradition that has been passed down through generations of Hawaiian families.\r\n\r\n---\r\n\r\n### Listen Now\r\n\r\nThe Nahenahe Voice is available on all major streaming platforms. Listen, share, and let the music of Moloka'i touch your heart.\r\n\r\n*E mau ana ka 'oia'i'o* - The truth endures forever.",
            "gallery_images": [
                "/static/images/legacy-album/LeAnne_cover.jpg",
                "/static/images/legacy-album/Phil_ukulele-cover.jpg",
                "/static/images/legacy-album/arena_cover.jpg",
            ],
            "product_links": [
                {"name": "Amazon Music", "url": "https://music.amazon.com/search/nahenahe%20voice", "icon": ""},
                {"name": "Apple Music", "url": "https://music.apple.com/us/search?term=nahenahe%20voice", "icon": ""},
                {"name": "Spotify", "url": "https://open.spotify.com/search/nahenahe%20voice", "icon": ""},
            ],
        },
        "free_booklets": {
            "title": "FREE Booklets",
            "hero_image": "/static/images/taro_field_1.jpg",
            "body_md": "## FREE Kingdom Booklets - Yours as a Gift\r\n\r\nThese booklets are drawn from **30 years of biblical study** in the original Greek and Hebrew - and they are completely free.\r\n\r\nKahu Phil Stephens has spent three decades studying the Kingdom of God as Jesus actually taught it - not through the lens of religious tradition, but through the original language of Scripture. These booklets represent the distilled essence of that study. Practical. Powerful. Grounded in the Word.\r\n\r\n**Download all 6 booklets below** - no email required, no strings attached. This is Kingdom generosity in action.\r\n\r\n---\r\n\r\n### What Is Kingdom Theology?\r\n\r\nJesus used the phrase \"Kingdom of God\" 53 times in the Gospels. He used the word \"church\" twice. That ratio is not an accident. Jesus came to establish a Kingdom - a complete system of governance, identity, wealth, wellness, and purpose that covers every dimension of human life.\r\n\r\nMost believers have been taught a church-centered gospel. These booklets introduce you to the Kingdom-centered gospel that Jesus actually preached. The difference will change how you read Scripture, how you approach money, how you steward your body, and how you understand your purpose on earth.\r\n\r\n---\r\n\r\n### The Six Booklets\r\n\r\n**Kingdom Wealth Principles** - The biblical foundations of increase, stewardship, and generosity. What the Kingdom says about money that most churches never teach.\r\n\r\n[FREE Download](https://keaupuniakeakua.faith/download/booklet1)\r\n\r\n---\r\n\r\n**Kingdom Wealth for Couples** - How husbands and wives can align around Kingdom financial principles. Unity in stewardship as a spiritual discipline.\r\n\r\n[FREE Download](https://keaupuniakeakua.faith/download/booklet2)\r\n\r\n---\r\n\r\n**Kingdom Wellness Principles** - Your body is a temple, not a burden. The Kingdom framework for health, eating, and physical stewardship rooted in Scripture.\r\n\r\n[FREE Download](https://keaupuniakeakua.faith/download/booklet3)\r\n\r\n---\r\n\r\n**Kingdom Wellness for Couples** - How couples can pursue health together as an act of Kingdom faithfulness. Practical and Scripture-grounded.\r\n\r\n[FREE Download](https://keaupuniakeakua.faith/download/booklet4)\r\n\r\n---\r\n\r\n**Kingdom Living Principles** - Identity, purpose, and daily life as a Kingdom citizen. Who you are in the Kingdom determines how you live in the world.\r\n\r\n[FREE Download](https://keaupuniakeakua.faith/download/booklet5)\r\n\r\n---\r\n\r\n**Kingdom Living for Couples** - Marriage as a Kingdom institution. How two people can build a household that reflects the values and purposes of the Kingdom of God.\r\n\r\n[FREE Download](https://keaupuniakeakua.faith/download/booklet6)\r\n\r\n---\r\n\r\n### Why Free?\r\n\r\nThe Kingdom of God operates on a principle of seed and harvest. These booklets are seed. Kahu Phil offers them freely because he believes that what God has given him belongs to the Body of Christ - not to a publishing program.\r\n\r\nIf these booklets change your life, you are welcome to give. But there is no obligation. The Kingdom does not put a price on truth.\r\n\r\n*Written and published from Moloka'i, Hawai'i by Ke Aupuni O Ke Akua Press.*",
            "products": [
                {"title": "Kingdom Wealth Principles", "download": "/download/booklet1"},
                {"title": "Kingdom Wealth for Couples", "download": "/download/booklet2"},
                {"title": "Kingdom Wellness Principles", "download": "/download/booklet3"},
                {"title": "Kingdom Wellness for Couples", "download": "/download/booklet4"},
                {"title": "Kingdom Living Principles", "download": "/download/booklet5"},
                {"title": "Kingdom Living for Couples", "download": "/download/booklet6"},
            ],
        },
        "kingdom_keys": {
            "title": "FREE Kingdom Keys Booklets",
            "hero_image": "/static/images/taro_field_2.jpg",
            "body_md": "## Unlock the Kingdom - FREE\r\n\r\nAfter **30 years of biblical study** in the original Greek and Hebrew, Kahu Phil Stephens has distilled the most powerful Kingdom principles into short, focused booklets that you can read in minutes - and apply for a lifetime.\r\n\r\nThese are not devotionals. These are **keys** - specific, actionable Kingdom truths that will unlock new dimensions of your spiritual life, your health, and your prosperity.\r\n\r\n**Download your FREE Kingdom Keys below.**\r\n\r\n---\r\n\r\n### Your FREE Kingdom Keys\r\n\r\n*Want to go deeper? Explore the [Complete Kingdom Series](/call_to_repentance) - the full theological foundation for Kingdom living.*",
            "products": [
                {"title": "7 Scriptures Kingdom Inside You", "download": "/download/pamphlet1"},
                {"title": "Kingdom Healing in 10 Minutes", "download": "/download/pamphlet2"},
                {"title": "5 Kingdom Prayers", "download": "/download/pamphlet3"},
                {"title": "Kingdom Wealth Verses", "download": "/download/pamphlet4"},
            ],
        },
        "partner": {
            "title": "Partner With Us",
            "hero_image": "/static/images/helping_hands.jpg",
            "body_md": "",
        },
    },
}

def _deep_merge(base, override):
    result = dict(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result

def load_content():
    return DEFAULT_PAGES

def save_content(data):
    pass

def get_nav_items(data):
    pages = data.get("pages", {})
    page_order = data.get("order", ORDER)
    nav = []
    for slug in page_order:
        if slug in pages:
            nav.append({
                "slug": slug,
                "title": pages[slug].get("title", slug.replace("_", " ").title()),
                "url": "/" if slug == "home" else f"/{slug}",
            })
    return nav

def load_digital_products():
    if PRODUCTS_FILE.exists():
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"products": []}

def save_digital_products(products_data):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products_data, f, indent=2, ensure_ascii=False)

def generate_product_id():
    return f"prod_{datetime.now().strftime('%Y%m%d%H%M%S')}"

def get_product_by_id(product_id):
    products_data = load_digital_products()
    return next(
        (p for p in products_data["products"] if p["id"] == product_id), None
    )
