# Rotten Fencepost Discovery Engine — Discovery Operations Baseline

**Document type:** Permanent operational baseline (Discovery Operations — Work Order 001)
**Date established:** 2026-07-25
**Focus:** Product 001 — "Find the Cause, Not the Symptoms" (`prod_find_the_cause_not_the_symptoms`)
**Prerequisite phase:** Discovery Engineering (Work Orders 004–010) — COMPLETE. See `DISCOVERY_ENGINEERING_COMPLETION_REPORT.md`.

This document is the zero-point baseline for Discovery Operations. It records what is verifiably true about production, discoverability, and Product 001's publication state on the date above. Every future Discovery Operations work order should be measured as a delta against the numbers in this document, not against assumptions.

**Evidence key** used throughout: **[CODE]** = confirmed by reading the repository. **[LIVE]** = confirmed by fetching the live production site during this session. **[REPORTED]** = stated by Kahu Phil or a prior session, not independently re-verified here. **[UNVERIFIABLE]** = cannot be confirmed from this environment; requires dashboard/account access this session does not have.

---

## 1. Current Production Status

- Site is live and reachable at `https://keaupuniakeakua.faith` on Render.com. **[LIVE]**
- `/robots.txt` returns correct directives: allows `/`, disallows `/kahu` and `/admin`, references the sitemap. **[LIVE]**
- `/sitemap.xml` returns valid XML. **[LIVE]**
- Product 001's page (`/product/prod_find_the_cause_not_the_symptoms`) is live, returns the correct title ("Find the Cause, Not the Symptoms | Rotten Fencepost Foundational Guide"), displays the correct price ($9.99), and has a working "Buy Now" button linking to checkout. **[LIVE]**
- Last full production crawl (63 URLs, zero broken links, zero mixed content) was performed one day prior to this document, during Work Order 009-DV. Not re-run in full during this session; the three spot checks above (sitemap, robots.txt, product page) found no drift from that verification. **[REPORTED + spot-checked LIVE]**
- `www.keaupuniakeakua.faith` remains unconfigured (Cloudflare/Render DNS/TLS gap) — unchanged, not re-tested this session. **[REPORTED]**

## 2. Completed Engineering Work (Reference)

Work Orders 005–010 delivered the full technical search-visibility foundation this phase now operates on top of: sitemap completeness, unique metadata, Open Graph/Twitter Cards, Schema.org structured data, canonical tags, `noindex` on transactional pages, and internal linking to close orphan pages. Full detail is in `DISCOVERY_ENGINEERING_COMPLETION_REPORT.md` and `CLAUDE.md`'s Change Log — not restated here. That work is locked and out of scope for Discovery Operations.

## 3. Google Search Console Status

- `<meta name="google-site-verification" content="ba5d8e311152a3a0" />` and `<meta name="msvalidate.01" content="...">` (Bing) are present in `templates/base.html` and served on every page. **[CODE, confirmed live via the meta tags' presence in the deployed template]**
- Whether the GSC and Bing Webmaster Tools *properties themselves* are claimed/verified in each platform's dashboard, whether the sitemap has been submitted inside GSC, and whether indexing has been explicitly requested for Product 001's pages — **[UNVERIFIABLE from this environment]**. This session has no GSC/Bing account access. A prior session's Change Log entry (Work Order 010, `CLAUDE.md`) states the GSC property was "already configured and Google has begun validating recent indexing changes" — that is a **[REPORTED]** claim, not independently confirmed here.

## 4. Current Sitemap Status

- Live `/sitemap.xml`: **38 unique URLs**, zero duplicates, valid XML. Confirmed two ways: locally via the Flask test client, and by fetching the live URL directly. Both agree exactly. **[LIVE + CODE]**
- Includes `/product/prod_find_the_cause_not_the_symptoms` at priority 0.8, monthly changefreq. **[CODE — `blueprints/pages.py`]**
- No `<lastmod>` values (a deliberate Work Order 005 decision — no reliable per-page timestamp exists in this app's data model). **[CODE]**

## 5. Current Indexing Status

- This session ran three web searches: `site:keaupuniakeakua.faith`, the bare domain name `keaupuniakeakua.faith`, and a distinctive phrase from Product 001's own description. **All three returned zero results from the keaupuniakeakua.faith domain.** **[LIVE web-search check, this session]**
- **This is a signal, not a confirmed fact of Google's index state.** The search tool used here does not disclose which index/provider backs it, may lag behind Google's live index, and a `site:` query returning nothing is not the same as an authoritative GSC Index Coverage report (which can show "Discovered, not yet indexed" or "Crawled, not indexed" states invisible to a public search box). Treat this as "no organic visibility observed today," not "confirmed zero index coverage."
- Actual GSC Index Coverage data (pages submitted vs. indexed vs. excluded, with reasons) — **[UNVERIFIABLE from this environment]**.

## 6. Current Product 001 Publication Status

From `digital_products.json` (`prod_find_the_cause_not_the_symptoms`): **[CODE]**

| Field | Value |
|---|---|
| `active` | `true` |
| `price` | `$9.99` |
| `category` | `ebook` |
| `total_sales` | `0` |
| `downloads` | `0` |
| `author` | Kahu Phil Stephens |
| `publisher` | Rotten Fencepost Publishing |
| `series` | Rotten Fencepost |

Live checkout button confirmed functional (links to checkout page) as of this session. **[LIVE]** No purchase was attempted (would create a real transaction).

## 7. Existing Discovery Assets Already in Production

All confirmed present in the deployed codebase: **[CODE]**

- **Primary navigation**: `/products` is a top-level nav link on every page (`templates/base.html`). `/rotten-fencepost` (Product 001's dedicated sales page) is one click deeper, under the "More" dropdown.
- **Homepage promo band**: a dedicated section in `content.py`'s `home` page content links directly to `/product/prod_find_the_cause_not_the_symptoms`.
- **Dedicated bespoke sales page** at `/rotten-fencepost` (`templates/rotten_fencepost.html`) with two separate buy links into the product.
- **Generic catalog page** `/products` lists it among all active products.
- **One organic, contextual internal link** from the SEO article `/wellness/the-rotten-fencepost-principle` into `/rotten-fencepost`, and a reciprocal link back (added Work Order 008) — this is the only content page besides the sales/product pages themselves that discusses the "rotten fencepost" concept by name (confirmed by repo-wide search).
- **Structured data**: `Product` + `Offer` + `BreadcrumbList` JSON-LD on the product page (Work Order 007).
- **Metadata**: unique `<title>`, meta description, canonical tag, and Open Graph/Twitter Card tags (Work Orders 005–006, 008).
- **Sitewide Google Analytics 4** (`gtag.js`, measurement ID `G-V2NY3MEWKB`) installed in `templates/base.html` on every page, including Product 001's. Dashboard traffic data itself — **[UNVERIFIABLE from this environment]**.
- **Sitewide email capture** ("Stay Connected" footer form on every page, posts to `/subscribe`). Current stored subscriber count: **0** (`data/subscribers.json` is an empty array as of this session). **[CODE]**
- **One established outbound social profile**: a YouTube channel (`https://www.youtube.com/@keaupuniokeakua`), referenced in the site's own structured data as its only genuine `sameAs` link (confirmed during the Work Order 007 investigation — no other social profiles were found to exist). Channel activity/subscriber count — **[UNVERIFIABLE from this environment]**.

## 8. Content Inventory Relevant to Product 001

A repo-wide search for "rotten fencepost" (case-insensitive) across all content sources (`content.py`, `blueprints/pages.py`'s `_SEO_PAGES`, all templates) found exactly three pages that reference the concept or product by name: **[CODE]**

1. `/rotten-fencepost` — the bespoke sales page itself.
2. `/wellness/the-rotten-fencepost-principle` — the one SEO article explaining the concept.
3. `/` (homepage) — one promo band.

No other page in the 38-URL sitemap, and no other `_SEO_PAGES` article, mentions "rotten fencepost" or Product 001. There is currently no cluster of supporting content (no second or third article approaching the topic from a different angle, no FAQ, no case-study/testimonial page) beyond these three touchpoints.

## 9. Current Strengths

- The full technical SEO foundation (sitemap, structured data, metadata, canonical, indexing signals, internal linking) is complete, tested (298/298), and production-verified — nothing here is blocking discovery on the technical side. **[CODE + REPORTED]**
- Product 001 has three independent, cross-linked entry points (nav → `/products`, nav → `/rotten-fencepost`, homepage promo band) plus one organic content backlink from an SEO article — not a single point of failure. **[CODE]**
- Analytics (GA4) and both major search-engine verification tags are already installed sitewide, so whatever Discovery Operations does next can be measured without further engineering work. **[CODE]**
- A working, tested checkout flow (PayPal live, Stripe ready to activate) means any traffic Discovery Operations generates has a functioning path to a sale today. **[CODE + LIVE]**

## 10. Current Bottlenecks

- **Zero recorded sales and zero downloads** for Product 001 since launch (`total_sales: 0`, `downloads: 0`). **[CODE]**
- **Zero captured email subscribers** sitewide (`data/subscribers.json` is empty). **[CODE]**
- **No organic search visibility observed** for the domain in this session's web-search check (Section 5) — caveated as a signal, not a confirmed GSC fact.
- **Only one piece of supporting content** (Section 8) exists to build topical authority around the "rotten fencepost" concept — no content cluster.
- **No backlink data exists in this environment.** The only confirmed outbound social presence is one YouTube channel; whether it (or anything else) sends referral traffic is unverifiable here.
- **GSC/Bing dashboard state and GA4 traffic data are both unverifiable from this environment** — Discovery Operations work cannot be evidence-based on these fronts until dashboard access is available to whoever runs the next work order.

## 11. Remaining Manual Tasks

Carried over, unresolved, not code-only (same items the Discovery Engineering Completion Report already listed as out of that phase's scope):

| Task | Status |
|---|---|
| Confirm GSC property verification, sitemap submission, and request indexing for Product 001's URLs specifically | **[UNVERIFIABLE from this environment]** — requires Kahu Phil's GSC dashboard access |
| Confirm Bing Webmaster Tools property + sitemap submission | **[UNVERIFIABLE from this environment]** |
| Resolve `www` subdomain DNS/TLS configuration gap | **[REPORTED, unresolved]** — Cloudflare/Render dashboard access required |
| Pull actual GA4 traffic numbers for baseline comparison | **[UNVERIFIABLE from this environment]** — requires GA4 dashboard access |

## 12. Operational Metrics to Track Going Forward (Recommended — Not Yet Measured)

These are recommendations for what future Discovery Operations work orders should track. None of these have baseline values yet beyond what's stated above; they are not invented metrics, they are named data sources that already exist in the stack (GSC, GA4, the product catalog) but are unread from this environment.

- **GSC**: impressions, clicks, average position, and CTR for queries reasonably related to Product 001 and "rotten fencepost." GSC Index Coverage report (indexed vs. discovered vs. excluded).
- **GA4**: sessions/users landing on `/rotten-fencepost`, `/product/prod_find_the_cause_not_the_symptoms`, and `/products`; traffic-source breakdown (organic search vs. direct vs. referral vs. social); engagement rate on those three pages.
- **Checkout funnel**: product-page view → checkout-page view → completed purchase, using `total_sales` in `digital_products.json` as the running conversion counter already in place.
- **Email list growth**: subscriber count in `data/subscribers.json` over time (currently 0).
- **Backlinks / referring domains**: not currently tracked by any tool in this stack; would need GSC's Links report or a third-party backlink tool if this becomes a priority.

## 13. Recommended Success Measurements for Future Discovery Operations Work Orders

Framed as concrete, verifiable first-milestones against this document's zero-baseline — not speculative targets:

- **First indexed page**: a future `site:keaupuniakeakua.faith` check (or a GSC Index Coverage read) returns at least one URL, where this session's returned zero.
- **First qualified organic visit**: a GA4 session on `/rotten-fencepost` or `/product/prod_find_the_cause_not_the_symptoms` with `organic search` as the traffic source.
- **First captured subscriber**: `data/subscribers.json` moves from 0 to 1.
- **First sale**: `total_sales` on `prod_find_the_cause_not_the_symptoms` moves from 0 to 1.

Each of these is a binary, evidence-checkable event — not a percentage or projection — chosen deliberately because this baseline currently shows all four at zero, and each is directly readable from a source already confirmed to exist in this stack.

---

**This document does not authorize or propose any engineering changes.** It is a factual snapshot to be read alongside `DISCOVERY_ENGINEERING_COMPLETION_REPORT.md` before scoping Discovery Operations — Work Order 002.
