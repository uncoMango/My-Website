# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Emoji Policy

**NO emoji characters anywhere in this project** — not in templates, not in Python files, not in HTML, not in content. Never add emoji unless explicitly instructed by Kahu Phil.

## Project Overview

Flask web application for Ke Aupuni O Ke Akua, a Hawaiian Kingdom ministry website. Deployed on Render.com at `keaupuniakeakua.faith`.

## Commands

- **Run locally:** `flask run` or `python app.py`
- **Install dependencies:** `pip install -r requirements.txt`
- **Production start:** `gunicorn --bind 0.0.0.0:$PORT app:app`
- No test suite or linter configured.

## Architecture

**Blueprint-based Flask app** refactored from a legacy monolith (`ke_aupuni_website.py`, still present but unused).

### Entry Points
- `app.py` — App factory, registers all blueprints
- `config.py` — Centralized settings (page nav order, paths). All secrets loaded from environment variables (no hardcoded fallbacks).
- `content.py` — JSON data layer: reads/writes `website_content.json` and `digital_products.json`

### Blueprints (`blueprints/`)
| Blueprint | Route prefix | Purpose |
|-----------|-------------|---------|
| `pages.py` | `/<page_id>` | Public content pages |
| `downloads.py` | `/download/` | Free PDF downloads |
| `products.py` | `/product/`, `/admin/products` | Digital product CRUD + public pages |
| `payments.py` | `/checkout/`, `/paypal/`, `/stripe/` | PayPal (active) + Stripe (ready to activate) |
| `admin.py` | `/kahu` | Admin panel (password: see `config.py`) |

### Data Storage
Content is stored as JSON files, **not a database**:
- `website_content.json` — Page content (Markdown rendered to HTML via `markdown` library with `extra` and `nl2br` extensions). **Do not delete.**
- `digital_products.json` — Product catalog. **Do not delete.**
- `digital_products/` — Uploaded product files

### Templates
Jinja2 templates in `templates/` extend `base.html`. CSS is inline via `{% include 'partials/styles.css' %}`. No CSS framework is used — all custom responsive styles.

### Deployment
- Primary: Render.com (`render.yaml`)
- `Procfile` for Heroku-compatible hosts
- `vercel.json` exists but is outdated (references old monolith)

### Page Navigation Order
Defined in `config.py` as `ORDER` list. Controls nav bar ordering.

### Sales Funnels
- `templates/aloha_wellness_funnel.html` — Standalone landing page for Aloha Wellness book. Routes to `/checkout/prod_aloha_wellness` (uses existing PayPal/Stripe payment system). Includes free booklet email capture via `/download/aloha_wellness_freebie`.

## Environment Variables (Required on Render)

All secrets are loaded via `os.environ[]` with **no fallback defaults** — the app will crash on startup if any are missing. Set these in Render Dashboard > Environment:

| Variable | Description |
|----------|-------------|
| `ADMIN_PASSWORD` | Password for `/kahu` admin panel |
| `PAYPAL_CLIENT_ID` | PayPal live API client ID |
| `PAYPAL_CLIENT_SECRET` | PayPal live API secret |
| `SMTP_HOST` | SMTP server hostname (e.g. `mail.privateemail.com`) |
| `SMTP_PORT` | SMTP port (e.g. `587`) |
| `SMTP_USER` | SMTP login email address |
| `SMTP_PASS` | SMTP login password |

**Optional** (safe empty-string defaults):
- `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` — Set when activating Stripe
- `STRIPE_ENABLED` — Set to `true` to show Stripe button on checkout

## Change Log

### 2026-07-24
- **Sitewide Shared-Layout Correction** (Work Orders 004-B investigation + 004-C implementation). 004-B found that the exact hero/body overlap defect fixed on the homepage in Correction 003-A (`.container`'s `position: absolute; top: 0; height: 100vh`, layering page content on top of the hero instead of after it) was still present, unmodified, on **26 other pages** — every page rendered through `page.html` except home (the 7 primary content pages, `/ecosystem`, and all 18 wellness/kingdom/wealth/scripture-tools article pages). Desktop-only; an existing mobile override already made `.container` safe below 768px, likely why it went unnoticed. Full investigation and page-by-page inventory in `SITE_LAYOUT_AUDIT.md`.
  - **004-C fix** (`templates/partials/styles.css`): removed `.container`'s absolute positioning and `.content-card`'s `margin-top: 25vh` peek-through offset, replacing both with the same plain normal-flow layout `.home-container`/`.home-content-card` already used successfully. Deviated from the original investigation's suggested approach (duplicate the homepage's classes under new names) once it was confirmed *every* use of `.container`/`.content-card` needed the fix — editing them directly was simpler and covers all 26 pages with one change instead of 26 template rewrites. `page.html`'s existing home/non-home conditional needed no changes at all, since both branches are now safe. `.home-hero`/`.home-container`/`.home-content-card` and all 11 independently-safe templates (`rotten_fencepost.html`, `partner.html`, `product_page.html`, `checkout.html`, `products.html`, `thank_you.html`, and the 5 standalone funnel/success templates) were left untouched, confirmed via diff.
  - Added `tests/test_shared_layout.py` (59 tests): every one of the 26 affected pages returns 200 and renders via the shared classes; a direct regression guard asserting `.container` never contains `position: absolute` again; confirms the homepage still uses its own `.home-container`/`.home-content-card`; spot-checks the independently-safe templates. Full suite: 170/170 pass (111 existing + 59 new). Full 35-page/49-link crawl: zero broken links. Verified representative pages (`/kingdom_wealth`, `/ecosystem`, and `/kingdom/understanding-scripture-through-original-words` — the longest article page on the site, chosen to stress-test long-content flow) render in correct hero→container→article→footer document order with no absolute positioning in their inlined CSS. Product, checkout, PayPal/Stripe, and download-token behavior all unaffected.
- **Sitemap Completion** (Work Order 005) — `blueprints/pages.py`'s `sitemap()` route. Scoped strictly to the sitemap; no metadata, structured data, or other visibility work touched, per instruction.
  - **Added 7 pages** identified as missing in the Work Order 004 audit: `/ecosystem` (0.9, weekly), `/partner` (0.8, monthly), `/rotten-fencepost` (0.9, weekly — now the homepage's primary CTA), `/aloha-wellness` (0.8, weekly — the hyphenated funnel page, distinct from `/aloha_wellness`), and the 3 missing `/scripture-tools/*` pages (`hebrew-greek-meaning-tool` at weekly since it's the flagship page referenced by name from `/ecosystem`; `translation-gap-in-scripture` and `original-language-meaning` at monthly, matching the site's existing pattern for less-actively-cross-linked reference articles). Sitemap is now 34 URLs (was 27).
  - **`<lastmod>` removed entirely**, not fixed to a "better" value. Investigated whether an accurate per-page value was achievable: this app has no CMS or timestamp layer anywhere in its data model (page content lives in hardcoded Python dicts in `content.py` and `_SEO_PAGES` in `blueprints/pages.py`, with no "last modified" field on any page). The only way to get a *real* date would be either adding a genuine content-timestamp system (well beyond this work order's scope) or shelling out to `git log` per file at request time (fragile — depends on `.git` being present and readable in the Render deploy, adds a subprocess call to a hot request path, and still only gives file-level granularity, not per-page, since multiple pages share one file). Both fail the work order's own "without introducing unnecessary complexity" bar. The previous behavior (`datetime.now()` stamped on every URL, every request) wasn't accurate either — it just always said "today," which is arguably a mild form of the "invented modification date" the work order explicitly prohibited. `<lastmod>` is optional per the sitemap protocol, so removing it entirely was the only honest option left; also removed the now-unused `from datetime import datetime` import.
  - **Validation**: sitemap re-confirmed well-formed XML, 34 URLs, **zero duplicates**, every URL resolves 200 (both locally and live), every `<loc>` matches that page's own `<link rel="canonical">` tag (the 3 pages with no canonical tag at all — `/myron-golden`, `/aloha-wellness`, `/kingdom-study` — are a pre-existing, already-documented metadata gap from the Work Order 004 audit, correctly left untouched here). `robots.txt` still correctly references the sitemap. Full 111-test suite passes. Full 35-page/49-link crawl: zero regressions.
  - Also updated `GOOGLE_VISIBILITY_READINESS_AUDIT.md` to mark the sitemap-omissions and `<lastmod>` recommendations complete/resolved, with a status column added to the recommendation table.
- **Google Visibility Readiness Audit** (Work Order 004) — understanding-only, no code changed. Full findings in `GOOGLE_VISIBILITY_READINESS_AUDIT.md`. Files inspected: `templates/base.html`, `templates/page.html`, all 5 standalone templates (`aloha_wellness_funnel.html`, `kingdom_study.html`, `myron_golden_funnel.html`, `partner_success.html`, `payment_success.html`), `blueprints/pages.py` (sitemap/robots/`_SEO_PAGES`), `content.py` (`DEFAULT_PAGES` meta_description coverage), `products.py`. Major findings: (1) Search Console + Bing verification already present via meta tags, no code needed, but GSC/Bing property-claim status can't be confirmed from code — manual check required. (2) `sitemap.xml` is well-formed and every listed URL resolves, but omits 6 real pages (`/ecosystem`, `/partner`, `/rotten-fencepost`, 3 of 6 `/scripture-tools/*` pages) and its `<lastmod>` is always "today" regardless of actual changes. (3) `robots.txt` correctly allows all real content and blocks only `/kahu`/`/admin` — nothing accidentally blocked. (4) 8 of 9 primary content pages share one identical generic meta description (`templates/page.html:4`'s fallback); Open Graph/Twitter Card tags exist only on `product_page.html`, nowhere else sitewide. (5) Structured data is limited to `Person` + `Organization` JSON-LD (both valid); no `Product`, `Article`, `WebSite`, or `BreadcrumbList` schema anywhere. (6) Found genuinely orphaned pages with zero inbound internal links from any public page: `/aloha-wellness` (the hyphenated funnel — distinct from `/aloha_wellness`) and `/product/rotten_fencepost_field_guide`, plus the 4 partner-tier product pages (likely intentional, since `/partner` has its own dedicated checkout UI). Full prioritized 10-item engineering sequence with effort estimates and code-only vs. Google-account-access flags is in the audit doc's closing table. **No implementation begun — awaiting approval for Work Order 005.**
- **Repaired the 5 Critical findings from `WEBSITE_VISIBILITY_AUDIT_001.md`** (Work Order 002). Approved by Kahu Phil, committed (`31827a4`), pushed, and deployed to Render. **Live-verified via HTTP against `keaupuniakeakua.faith`**: all 12 nav destinations return 200 and the new grouped/dropdown markup is live; hero H1s render with real content on both short and long titles; product/checkout pages carry site nav, footer, and working back-links (no purchase was attempted); all 14 repaired internal links resolve and a full 35-page/49-link live crawl found zero 404s; `/rotten-fencepost/success` renders with its new dark card styling and both return links work. See `WEBSITE_VISIBILITY_AUDIT_001.md` for full before/after detail on each item. Pixel-level visual checks (exact nav wrapping/spacing across viewport widths, dropdown open/close feel, mobile presentation) still need a human look in a real browser — the Claude-in-Chrome extension was unavailable all session.
  - **Nav overflow** (`templates/base.html`, `templates/partials/styles.css`): grouped the 6 least-critical of 12 nav items behind a "More" dropdown, reusing `.nav-dropdown`/`.dropdown-menu` CSS and click-outside JS that already existed in the codebase but was never wired to any markup. Added a `toggleDropdown()` click handler. Added `flex-wrap` to `.nav-menu` as a safety net. Moved the hamburger breakpoint from 768px to 1100px (the horizontal bar can't reliably fit even the grouped nav at 1024px next to the existing 180px-tall logo) and trimmed nav link font-size from 1.3rem to 1.1rem for extra margin at 1101px+. All 12 original destinations remain reachable.
  - **Hidden page titles** (`templates/partials/styles.css`): removed `.hero h1 { display: none; }`, replaced with visible, responsive (`clamp()`-sized), text-shadowed styling. Affects all ~28 `page.html`-driven pages. Verified all `page.title` values in `website_content.json` and the `_SEO_PAGES` dict render cleanly (no odd whitespace).
  - **Off-brand product/checkout pages** (`templates/product_page.html`, `templates/checkout.html`): both now `{% extends "base.html" %}` instead of being standalone documents, so they carry the site nav, footer, and branding. Added an `extra_head` block to `base.html` so `product_page.html` can still inject its OG/Twitter meta tags. Renamed each page's own `.container` class to avoid colliding with the shared `.container` rule from `page.html`'s hero layout. Added explicit "Back to All Products" / "Return to Homepage" links (product page) and "Back to product page" / "Return to Homepage" links (checkout). All existing Stripe form actions, the PayPal SDK script/JS, and the `#paypal-button-container` id were carried over unchanged. Incidentally fixed raw (non-2-decimal) price display on the product page (`$23.5` → `$23.50`) while rewriting that block.
  - **Broken internal links** (`blueprints/pages.py`): repointed every instance of `/support` → `/partner`, bare `/scripture-tools` → `/scripture-tools/hebrew-greek-meaning-tool`, bare `/kingdom` → `/call_to_repentance`, and `/wellness/what-actually-works-instead-of-dieting` → `/wellness/lose-weight-without-dieting`. No redirects added: these were never valid routes (not renamed/moved pages), so nothing could have indexed or bookmarked them as working URLs.
  - **White-on-white success page** (`templates/rotten_fencepost_success.html`): wrapped content in a new `.success-card` block (explicit dark background/text color, kept separate from `.content-card` to avoid a specificity collision with `.content-card a` that would have recolored the buttons). Added "Back to Rotten Fencepost" and "Return to Ke Aupuni O Ke Akua" links. Confirmed via repo-wide search that no payment success/redirect flow currently links to this route — it appears to be orphaned from an earlier version of the funnel — but it now renders correctly if reached directly.
  - **Testing:** full existing suite (`tests/`, 111 tests) passes. Manually exercised every changed/affected route via the Flask test client (including checkout with PayPal/Stripe credentials monkeypatched present), crawled all internal links across all 35 public pages (46 non-checkout links, zero 404s), and confirmed no protected file paths leak from the rewritten product/checkout pages. Nav width fix is code-reviewed and measured against the actual 180px logo height and container max-width, but **not yet visually verified in a live browser** at the requested viewport widths (1920/1440/1366/1024/768/390) — the Claude-in-Chrome extension was unavailable both this session and the prior audit session. Flagged for live human review before/at deploy verification.
- **Added Product 001: "Find the Cause, Not the Symptoms"** (`prod_find_the_cause_not_the_symptoms` in `digital_products.json`, $9.99, category `ebook`). Uses the existing generic `/product/<id>` + `product_page.html` flow — no bespoke funnel page. `product_page.html` gained optional `subtitle`/`author`/`publisher`/`series`/`seo_title`/`meta_description` fields (backward compatible, unused fields are simply ignored by older entries).
- **New public `/products` listing page** (`blueprints/products.py` + `templates/products.html`) — lists all `active` non-`partnership` catalog products as cards. Added to nav in `base.html` and to `sitemap.xml`.
- Approved cover (`static/covers/find_the_cause_not_the_symptoms_cover.jpg`, full KDP wraparound print spread) and finalized PDF (`digital_products/find_the_cause_not_the_symptoms.pdf`) received from Kahu Phil and installed. Generated `find_the_cause_not_the_symptoms_cover_web.jpg` — a front-cover-only crop — for on-site display (`cover_image`); the untouched wraparound file is kept as `print_cover_image` for reference and is not itself displayed anywhere on the site. Product 001 is now `"active": true`.
- Added a homepage promo band (`content.py`, `home` page `body_md`) linking to the new product page.
- Added `og:title`/`og:description`/`og:image`/`twitter:card` meta tags to `product_page.html` (none existed anywhere on the site before) so product links share correctly.
- **Bugfix:** `serve_cover()` in `blueprints/downloads.py` (a leftover route from before the blueprint refactor) resolved `/static/covers/<filename>` against the repo root instead of `static/covers/`, so it shadowed Flask's default static handler and 404'd on every file in that folder — including the pre-existing `cover1.jpg`/`cover2.jpg`/`cover3.jpg`, not just the new cover. Fixed the path join; confirmed all four now serve correctly.
- All changes tested locally via `flask run` (nav, homepage band, `/products`, `/product/prod_find_the_cause_not_the_symptoms`, cover image, `/download/product/...`, checkout route, sitemap.xml). Not yet committed, pushed, or deployed — awaiting Kahu Phil's explicit go-ahead.

### 2026-03-03
- **Dynamic YouTube embed on `/aloha-wellness` funnel** — `funnel_youtube_url` stored in `website_content.json` (top-level key). Admin can paste any YouTube URL format into the `/kahu` panel "Weekly YouTube Video" field to update the embed without code changes. `_youtube_to_embed()` in `admin.py` converts share/watch/embed URLs to embed format.
- **Fixed `edit_page` save** — now preserves all top-level JSON keys (was previously stripping unknown keys like `funnel_youtube_url`).

### 2026-02-26
- **Removed all hardcoded secrets from `config.py`** — admin password, PayPal credentials, and SMTP credentials now require environment variables with no fallback defaults. Stripe vars kept optional with empty defaults since Stripe is not yet active.
- **Audited `aloha_wellness_funnel.html`** — confirmed all CTA buttons already route to internal `/checkout/prod_aloha_wellness` (no external Amazon/Gumroad links present).
