# Website Visibility Audit — 001

**Date:** 2026-07-24
**Scope:** All publicly reachable pages on `keaupuniakeakua.faith` (main site) reviewed as a first-time visitor would encounter them.
**Method:** Code-based audit — Jinja templates, shared CSS (`templates/partials/styles.css`, `base.html`), route definitions (`blueprints/*.py`), and content data (`website_content.json`, `digital_products.json`) were read directly rather than rendered live in a browser (the Claude-in-Chrome extension was not connected this session). Findings below are derived from what the code will actually produce, not a visual screenshot pass. Anything that specifically needs eyeballing in a real browser (exact pixel wrapping, animation feel, real font rendering) is called out as unverified rather than asserted.

**Pages reviewed (35):**
- Primary nav pages (9): `/`, `/kingdom_wealth`, `/free_booklets`, `/kingdom_keys`, `/call_to_repentance`, `/aloha-wellness`, `/pastor_planners`, `/nahenahe_voice`, `/partner`
- Unique-template pages (8): `/rotten-fencepost`, `/rotten-fencepost/success`, `/myron-golden`, `/kingdom-study`, `/ecosystem`, `/products`, `/product/prod_find_the_cause_not_the_symptoms`, `/checkout/<product_id>`
- SEO sub-pages (18): all `/wellness/*`, `/kingdom/*`, `/wealth/*`, `/scripture-tools/*` pages defined in `blueprints/pages.py`

---

## Critical

> **IMPLEMENTED — awaiting live verification** (Work Order 002, 2026-07-24). See `CLAUDE.md` Change Log for the full before/after detail on each item below.

### 1. Desktop nav will overflow or become unreadable on almost every real screen width
**Page:** Sitewide (`templates/base.html`, `templates/partials/styles.css`) — every single page uses this same hardcoded nav.
**Issue:** The nav bar has 12 items (Home, Keaupuni Health, Keaupuni Wealth, Bible Truth, Music, Keaupuni Planners, Free Booklets, Ministry Support, Rotten Fencepost, Products, Ecosystem, Study Tools) at `font-size: 1.3rem`, bold, with no `flex-wrap` set on `.nav-menu` (`display:flex` defaults to `nowrap`) and no overflow handling on `.nav-container`. Rough width math on the item text alone puts total nav width at roughly 2000–2200px. The only responsive fallback is the hamburger menu, which only activates below `768px`. Between 769px and roughly 2200px — i.e., virtually every laptop (1280–1440px) and most desktop monitors (1920px) — the nav has nowhere to go: items will overflow the container, likely spilling past the edge of the screen or overlapping the logo, since nothing constrains or wraps them in that range.
**Why it matters:** This is the very first thing every visitor sees, on every page, on the majority of devices used to browse the web. A broken or unreadable nav directly undermines "clarity of purpose" and "navigation clarity" — arguably the single biggest issue on the site.
**Recommended implementation:** Add an intermediate breakpoint (e.g. below ~1400–1500px) that either shrinks nav font-size/padding significantly, drops to the hamburger menu earlier, or reduces visible top-level items (move some into a dropdown). Verify visually across 1280px, 1366px, 1440px, and 1920px widths.
**Priority:** Critical

> **IMPLEMENTED — awaiting live verification**

### 2. Every content page's real title is invisible for the entire first screen
**Page:** All `page.html`-driven pages — the 9 primary nav pages, `/ecosystem`, and all 18 SEO sub-pages (28 pages total).
**Issue:** `templates/page.html` renders `<h1>{{ page.title }}</h1>` inside the hero, but `styles.css` has `.hero h1 { display: none; }`. The hero is a full-viewport-height (`100vh`, min 600px) background photo with a dark gradient overlay — and, because of that rule, literally no text on top of it. A visitor landing on `/kingdom_wealth` from a search result or shared link sees a full-screen photo and nothing telling them what the page is, until they scroll down past the entire hero into the content card below.
**Why it matters:** Directly hurts "clarity of purpose" and "first impression" for every content page on the site — a full screen with no identifying text is the definition of visitor confusion.
**Recommended implementation:** Remove or override `.hero h1 { display: none; }` for `page.html`'s hero (it appears to have been added for one specific page that had its own redundant title text, and then applied globally). Style the H1 to match the existing hero text-shadow treatment used elsewhere (e.g. `rotten_fencepost.html`'s hero, which does show its H1 correctly).
**Priority:** Critical

> **IMPLEMENTED — awaiting live verification**

### 3. Clicking into any product strands the visitor outside the site, with no way back except browser-back
**Page:** `/product/<product_id>` (`templates/product_page.html`) and `/checkout/<product_id>` (`templates/checkout.html`)
**Issue:** Both templates are fully standalone HTML documents that do **not** extend `base.html`. They have their own generic purple-gradient design (`#667eea`/`#764ba2`, system-ui font) that shares nothing visually with the rest of the site (dark Hawaiian/Kingdom theme, Noto Sans, teal/gold accents). Neither template includes the site nav, logo, or footer, and neither has a link back to the homepage anywhere on the page. A visitor who reaches `/products` → clicks a product → is on the checkout page has no way to get back into the site except the browser back button.
**Why it matters:** This is the exact purchase path (`/products` → `/product/<id>` → `/checkout/<id>`) — the site's actual monetization funnel — and at every step past the products listing the visitor is visually and navigationally cut off from the brand they were just trusting. It also looks like a different, less trustworthy site right at the moment they're asked to pay.
**Recommended implementation:** At minimum, add a small "← Back to Ke Aupuni O Ke Akua" link/logo to both templates. Longer-term, consider having these extend `base.html` (or a lightweight variant) so nav/footer/branding stay consistent through checkout — a common, well-tested pattern is to keep checkout distraction-free but still branded.
**Priority:** Critical

> **IMPLEMENTED — awaiting live verification**

### 4. Several prominent "learn more" links are dead — they 404
**Page:** `/ecosystem`, and the SEO sub-pages `/wellness/eating-when-hungry`, `/wellness/the-rotten-fencepost-principle`, `/wellness/kupuna-wisdom-and-modern-health`, `/kingdom/understanding-scripture-through-original-words`, `/wellness/god-never-told-adam-when-to-eat`, `/kingdom/stewardship-in-the-kingdom-of-god`
**Issue:** Verified against the actual page-ID list in `website_content.json` and the route table in `blueprints/pages.py`:
- `/support` — linked 6 times across the pages above (e.g. "Support the Ministry →") — no such route or page exists → 404.
- `/scripture-tools` (bare, no slug) — linked 4 times (e.g. "Scripture Study Tools →") — the real route requires a slug (`/scripture-tools/<slug>`); the bare path 404s.
- `/kingdom` (bare) — linked 3 times on `/ecosystem` (e.g. "Kingdom Teaching →", "Start with Kingdom Teaching →") — no `kingdom` page-ID exists → 404.
- `/wellness/what-actually-works-instead-of-dieting` — linked once on `/ecosystem` — this slug isn't in the `_SEO_PAGES` dict at all → 404.
**Why it matters:** These aren't buried footnotes — several are the primary "continue reading" CTA at the end of an article, exactly where a first-time visitor who's engaged enough to click is most likely to leave frustrated and bounce.
**Recommended implementation:** Either build the missing `/support`, `/kingdom`, and `/wellness/what-actually-works-instead-of-dieting` pages, or repoint each broken link to the nearest real equivalent (`/partner` for support, `/ecosystem` or `/kingdom_wealth`+`/call_to_repentance` for `/kingdom`, `/wellness/why-diets-fail` for the dieting link). For `/scripture-tools`, either point to `/scripture-tools/hebrew-greek-meaning-tool` directly or build a real index page at that path.
**Priority:** Critical

> **IMPLEMENTED — awaiting live verification**

### 5. Purchase-confirmation page text is white-on-white — effectively invisible
**Page:** `/rotten-fencepost/success` (`templates/rotten_fencepost_success.html`)
**Issue:** This template extends `base.html` but wraps its content in a plain inline-styled `<div>` with no background color, instead of the site's `.content-card` (which the other confirmation page, `thank_you.html`, correctly uses with `background: rgba(0,0,0,0.55)`). `base.html`'s `body` sets `color: white` but has no solid background — just a near-white page with two very faint (5% opacity) radial gradients. The result: white "You are in. Mahalo." heading and body text sit directly on an effectively white page background.
**Why it matters:** If a visitor ever reaches this page, the entire confirmation message is unreadable. Note: while auditing the code path, this route does not appear to be linked from the actual PayPal/Stripe success flow (`payments.py` renders `payment_success.html` instead) or from anywhere else in the codebase — it looks orphaned/left over from an earlier version of the funnel. It's still a real, publicly reachable URL, so it's in scope, but its practical exposure may currently be low.
**Recommended implementation:** Wrap the content in `.content-card` (matching `thank_you.html`) or set an explicit dark background/text color. Separately, confirm with Kahu Phil whether this route is still meant to be part of any flow — if not, it can be removed rather than fixed.
**Priority:** Critical

---

## High

### 6. Garbled/mojibake characters visible in live product copy
**Page:** `/product/prod_find_the_cause_not_the_symptoms`, `/product/rotten_fencepost_field_guide`
**Issue:** In `digital_products.json`, `prod_find_the_cause_not_the_symptoms.series` reads `"Rotten Fencepost�"` and `rotten_fencepost_field_guide.description` reads `"Why everything keeps falling apart � and what God actually designed instead."` — both contain a raw replacement/mojibake character (almost certainly a corrupted em dash or apostrophe from an encoding mismatch when the JSON was saved). Both fields render directly and unescaped into `product_page.html` (the series line right under the product title; the description in the main body).
**Why it matters:** A visibly broken character on a product's sales page — right next to the price and buy button — reads as sloppy/untrustworthy at the exact moment a visitor is deciding whether to pay.
**Recommended implementation:** Fix the two strings directly in `digital_products.json` (replace `�` with the intended `—` or `'`), and re-save the file with UTF-8 encoding to prevent recurrence. Worth a quick scan of the rest of `digital_products.json` and `website_content.json` for the same character in case it appears elsewhere.
**Priority:** High

### 7. Free ($0) items are funneled through the same "Buy Now" payment flow as paid products
**Page:** `/product/prod_kingdom_booklet1`, `/product/prod_kingdom_booklet2` (reachable from `/products`)
**Issue:** Both booklets have `price: 0.0` and are `active: true` with no special handling. `product_page.html` renders the same button for every product: `<a href="/checkout/{{ product.id }}" class="buy-button">Buy Now – ${{ product.price }}</a>` — so these show "Buy Now – $0.0" and route into the full PayPal/Stripe checkout. PayPal does not support $0.00 orders, so this button is likely to fail outright for these two items (unverified without live testing, since a browser session wasn't available).
**Why it matters:** Confusing at best (asking someone to "buy" something free), broken at worst (a payment provider rejecting a $0 order). Either way it's a dead-end CTA for exactly the kind of low-friction, top-of-funnel free resource that's supposed to bring people in.
**Recommended implementation:** Give `$0` products a direct "Free Download" link (the site already has this exact pattern working elsewhere — the `/download/*` routes in `blueprints/downloads.py`) instead of routing them through checkout.
**Priority:** High

### 8. Sitemap.xml is missing several real, linked pages
**Page:** `/sitemap.xml`
**Issue:** Comparing the hardcoded page list in `sitemap()` (`blueprints/pages.py`) against the actual route table: `/ecosystem`, `/partner`, and `/rotten-fencepost` are all live, nav-linked or content-linked pages that are absent from the sitemap. Of the 18 SEO sub-pages, 3 are also missing: `/scripture-tools/translation-gap-in-scripture`, `/scripture-tools/original-language-meaning`, and `/scripture-tools/hebrew-greek-meaning-tool` (the last of these is the page the `/ecosystem` copy calls out by name as "the Scripture Language Insight Tool").
**Why it matters:** Not a direct visitor-confusion issue, but it undercuts how visitors find these pages in the first place via Google/Bing — some of the site's most-referenced content (the Scripture tool pages) is invisible to the sitemap that's supposed to help search engines index it.
**Recommended implementation:** Add the 6 missing paths to the `pages` list in `sitemap()`.
**Priority:** High

### 9. Kingdom Study Tools' only purchase button sends visitors to a bare `.onrender.com` URL
**Page:** `/kingdom-study` (`templates/kingdom_study.html`)
**Issue:** Both "Unlock the Full Collection — $97" buttons link to `https://scripture-app.onrender.com/unlock` — a different app on a different, unbranded Render subdomain, not `keaupuniakeakua.faith`. Unlike this repo's own checkout, this is a separate application entirely; its current state/uptime wasn't verifiable this session.
**Why it matters:** This is the single highest-priced offer on the entire site ($97), and the only way to buy it takes the visitor off-brand to a raw platform subdomain right at the moment of payment — the kind of URL a cautious buyer (rightly) hesitates at.
**Recommended implementation:** At minimum, put that app behind a custom subdomain (e.g. `study.keaupuniakeakua.faith`) so the URL doesn't read as an unfinished dev deployment. Confirm the app is actually live and the purchase flow works end-to-end.
**Priority:** High

---

## Medium

### 10. `/products` listing looks inconsistent — some cards have cover art, others are bare text
**Page:** `/products`
**Issue:** `products.html` only renders a cover image `{% if product.cover_image %}`. Of the 6 non-partnership products, only `prod_aloha_wellness` and `prod_find_the_cause_not_the_symptoms` have a `cover_image` set; `prod_kingdom_booklet1`, `prod_kingdom_booklet2`, `rotten_fencepost_field_guide`, and `prod_nahenahe_cd` have none, so they render as plain text-only cards in the same grid.
**Why it matters:** A product grid with two polished cards next to four bare ones reads as unfinished/inconsistent on a page whose entire job is to make the catalog look credible.
**Recommended implementation:** Add cover images for the remaining 4 products, or design a consistent placeholder/fallback graphic so every card looks intentional.
**Priority:** Medium

### 11. Inconsistent price formatting between product listing and product page
**Page:** `/product/<product_id>` vs `/products`
**Issue:** `products.html` formats price with `"%.2f"|format(product.price)` (e.g. "$23.50"). `product_page.html` prints the raw value: `${{ product.price }}` and `Buy Now – ${{ product.price }}` — for `prod_aloha_wellness` (`price: 23.5`) this renders as `$23.5`, not `$23.50`.
**Why it matters:** Small, but a visibly inconsistent price format between the two pages in the exact same purchase flow looks unpolished.
**Recommended implementation:** Apply the same `"%.2f"` formatting in `product_page.html`.
**Priority:** Medium

### 12. Same hero photo reused across many unrelated pages
**Page:** Multiple SEO sub-pages — `taro_root.jpg` is used as the hero image on 7 different pages (`three-meals-a-day-necessary`, `why-modern-health-advice-feels-confusing`, `translation-gap-in-scripture`, `original-language-meaning`, `hebrew-greek-meaning-tool`, `the-rotten-fencepost-principle`, `god-never-told-adam-when-to-eat`), and it's also the fallback hero for `/ecosystem`.
**Why it matters:** Since each hero occupies the entire first screen (see finding #2), landing on 7+ different articles that all open with the identical photo makes pages feel undifferentiated and can make a visitor moving between tabs/links wonder if they're on the same page they already read.
**Recommended implementation:** Spread the existing image variety (`ulu_kalo_mango.jpg`, `breadfruit.jpg`, `food_basket.jpg`, `bible_scroll.jpg`, `sunlight_bursting.jpg`, `molokai_coast.jpg`, `molokai_ranch.jpg` are all already in `static/images/` but underused) more evenly across the SEO sub-pages.
**Priority:** Medium

### 13. Hero background images are large, unoptimized files loaded on every content page
**Page:** Sitewide (all `page.html` pages)
**Issue:** Several hero images referenced in `blueprints/pages.py` are multi-megabyte files served at full size via CSS `background-size: cover` with no compression or responsive variants: `ulu_kalo_mango.jpg` (2.0MB), `molokai_coast.jpg` (1.2MB), `taro_root.jpg` (1.0MB). These load on a full-viewport-height hero on every single content page.
**Why it matters:** Slow-loading, multi-megabyte images on the very first thing every visitor sees — especially on mobile networks — directly risks the "would cause a visitor to leave" criterion, on top of Core Web Vitals/SEO impact.
**Recommended implementation:** Compress and resize all hero images (a 1920px-wide JPEG at reasonable quality should be well under 300KB for photos like these) and consider `loading="lazy"` equivalents or a responsive `srcset` approach for below-the-fold heroes.
**Priority:** Medium

### 14. Partner page's Rotten Fencepost callout box visually clashes with the page's own theme
**Page:** `/partner`
**Issue:** The rest of `/partner` uses a consistent dark theme (`rgba(0,0,0,0.25–0.55)` panels, gold/teal accents, `Georgia` serif headings). One inline-styled box — "If you are just discovering this teaching, start here: Get the Rotten Fencepost Field Guide — $9" — uses a light cream background (`#f9f5ef`) with a brown button (`#8B6914`), styled like it was copy-pasted from a completely different (light-theme) page.
**Why it matters:** Minor but noticeable — a bright cream box in the middle of an otherwise dark, cohesive page reads as a mistake rather than a deliberate callout.
**Recommended implementation:** Restyle that box to match the page's existing dark-panel treatment (e.g. reuse `.tier-card` or `.cd-section` styling).
**Priority:** Medium

### 15. Several SEO sub-page titles are long enough to be truncated in search results
**Page:** `/wellness/lose-weight-without-dieting` ("How to Lose Weight Without Dieting, Calorie Counting, or Restriction" — 70 chars), `/wellness/three-meals-a-day-necessary` ("Is Three Meals a Day Necessary? What Scripture and Ancestral Wisdom Reveal" — 76 chars), `/wellness/ancestral-eating-patterns` ("Ancestral Eating Patterns — The Hawaiian Kingdom Health Model" — 63 chars), and a few others in the same range.
**Why it matters:** Google typically truncates title tags around ~60 characters; anything longer gets cut off with "…" in search results, which can make the page look less relevant or less polished before a visitor even clicks.
**Recommended implementation:** Tighten these titles to under ~60 characters where practical (this doesn't need to match the on-page `<h1>`, only the `<title>`/meta title).
**Priority:** Medium

---

## Low

### 16. Empty "success icon" div leaves an unexplained gap on the payment-success page
**Page:** `payment_success.html` (rendered after a successful PayPal/Stripe purchase)
**Issue:** `<div class="success-icon"></div>` has `font-size: 4rem` styling but no content — it was very likely an emoji (✅/🎉) that was removed to comply with this project's no-emoji policy, leaving an empty, sized element.
**Why it matters:** Minor, but it leaves an odd blank gap directly above "Mahalo! Payment Received" on the one page every paying customer sees.
**Recommended implementation:** Remove the empty div, or replace it with a simple text/SVG checkmark that fits the no-emoji rule.
**Priority:** Low

---

## Summary

| Metric | Count |
|---|---|
| Total pages reviewed | 35 |
| Total issues found | 16 |
| Critical | 5 |
| High | 4 |
| Medium | 6 |
| Low | 1 |

**Note on method:** This pass was code-based, not a live visual walkthrough (browser extension wasn't connected this session). Findings above are all traced to specific, verifiable source (CSS rules, route tables, JSON content, template logic) rather than visual impression — but a live pass would likely surface additional pixel-level issues (real font rendering, exact wrapping, animation/hover feel, actual mobile viewport behavior) that static reading can't catch. Recommend a follow-up live-browser pass once the extension is connected, particularly to confirm finding #1 (nav overflow) at real screen widths.

This audit makes no code changes. Awaiting the next engineering work order to begin fixes.
