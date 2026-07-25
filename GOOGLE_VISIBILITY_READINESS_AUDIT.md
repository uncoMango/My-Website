# Google Visibility Readiness Audit

**Date:** 2026-07-24
**Scope:** `keaupuniakeakua.faith` — full codebase inspection (`templates/`, `blueprints/`, `content.py`, `config.py`) plus live verification against the deployed site.
**Method:** Code inspection and local/live HTTP validation only. No content was created, no code was changed. Every finding below is traced to a specific file/line or a live HTTP response — nothing here is a guess.

**The question this audit answers:** *If Google were evaluating this website today, what would prevent it from being discovered?*

**Short answer:** Nothing is broken or blocking indexing. The technical floor (robots.txt, sitemap validity, canonical tags, Search Console verification) is in place. The gap is **completeness and depth** — several real, good pages aren't in the sitemap or have zero inbound links, most page-specific metadata falls back to one generic description, and structured data covers only 2 of the schema types that would help this specific site (products, articles, breadcrumbs).

---

## 1. Search Console Readiness

**Verification: already present, both Google and Bing.**

- `templates/base.html:11` — `<meta name="google-site-verification" content="ba5d8e311152a3a0" />`
- `templates/base.html:12` — `<meta name="msvalidate.01" content="2728FA73D4512593659D170D39E32016" />` (Bing)
- `static/BingSiteAuth.xml` — Bing's alternate file-based verification, served at `/BingSiteAuth.xml`
- Confirmed live: the Google verification meta tag renders on `keaupuniakeakua.faith` today.
- Google Analytics 4 is also installed sitewide (`base.html:17-23`, measurement ID `G-V2NY3MEWKB`) — not a search-visibility factor itself, but confirms a Google product is already connected to this property.

**No code changes required.** The meta-tag method means verification lives in the page itself — it doesn't need a file upload or DNS record, and it won't break on redeploy.

**What I cannot verify from code:** whether someone has actually completed the verification *click* inside Google Search Console using this tag (the tag being present and the property being *claimed* in GSC are two different steps). That's a manual check — see Section 9.

---

## 2. Sitemap

> **COMPLETED — Work Order 005 (2026-07-24).** All 7 omissions below were added, `<lastmod>` was removed (see the updated note at the end of this section for why), and the sitemap was re-validated: 34 URLs, zero duplicates, every URL resolves 200, every `<loc>` matches that page's own canonical tag. Deployed and live-verified. This section is left in its original (pre-fix) form below as the historical record of what the audit found; the fix itself is documented in `CLAUDE.md`.
>
> **FOLLOW-UP — Work Order 009 (2026-07-24).** Re-audited product-page coverage specifically (line 50 below). Added the 4 remaining active, non-partnership product pages that were still missing (`prod_aloha_wellness`, `prod_kingdom_booklet1`, `prod_kingdom_booklet2`, `prod_nahenahe_cd`) — sitemap is now 38 URLs. `/product/rotten_fencepost_field_guide` remains deliberately excluded (near-duplicate of the already-indexed `/rotten-fencepost`), as do the 4 `partner_tierN` product pages (see Section 6's existing note — still an open, non-clear-cut call, not resolved). Full record in `CLAUDE.md`.

**File:** `blueprints/pages.py:1075-1119` (`/sitemap.xml`) — a hardcoded Python list, not auto-generated from routes.

**Validated:** Well-formed XML (parsed successfully with `xml.etree.ElementTree`), 27 URLs, every single one returns HTTP 200 both locally and live. No broken entries.

**Omissions — real, live pages not in the sitemap:**

| Missing page | In nav? | Notes |
|---|---|---|
| `/ecosystem` | Yes | The site's own hub/framework page — should be one of the *first* URLs listed |
| `/partner` | Yes | Donation/partnership page |
| `/rotten-fencepost` | Yes | The $9 field guide sales page — a primary commercial page and now the homepage's primary CTA destination |
| `/scripture-tools/translation-gap-in-scripture` | No | Real `_SEO_PAGES` entry (`blueprints/pages.py`) |
| `/scripture-tools/original-language-meaning` | No | Real `_SEO_PAGES` entry |
| `/scripture-tools/hebrew-greek-meaning-tool` | No | Real `_SEO_PAGES` entry — the specific page `/ecosystem`'s own copy calls out by name as "the Scripture Language Insight Tool" |
| `/aloha-wellness` (hyphen) | No | A *different* page from `/aloha_wellness` (underscore) — see Section 6, this one has zero inbound links from anywhere |

**Answering the scope checklist directly:**
- Product pages: only 1 of 6 non-partnership products is listed (`prod_find_the_cause_not_the_symptoms`). `/products` itself is listed. The others are not (see Section 6 for why this may be partly intentional).
- Rotten Fencepost pages: `/rotten-fencepost` is **not** in the sitemap (the field guide's own `/product/rotten_fencepost_field_guide` page isn't either).
- Scripture Tools: 3 of 6 `scripture-tools/*` pages are missing (listed above).
- Wellness pages: all 6 wellness-topic `_SEO_PAGES` entries present in the checked set (`why-diets-fail`, `lose-weight-without-dieting`, `three-meals-a-day-necessary`, `ancestral-eating-patterns`, `why-modern-health-advice-feels-confusing`, `why-your-body-resists-diets`) plus 3 more (`eating-when-hungry`, `the-rotten-fencepost-principle`, `kupuna-wisdom-and-modern-health`) — **all 9 wellness sub-pages are present.**
- Kingdom pages: `what-is-the-kingdom-of-god`, `jesus-kingdom-message`, `understanding-scripture-through-original-words`, `stewardship-in-the-kingdom-of-god` — **all 4 present.**

**Secondary issue — `<lastmod>` is always "today."** `blueprints/pages.py:1108`: `today = datetime.now().strftime("%Y-%m-%d")` is computed once per request and applied to *every* URL in the sitemap, regardless of whether that page's content actually changed. This isn't broken (Google tolerates it), but it's a weak signal — it tells crawlers "everything changed today" on every single fetch, which doesn't help Google prioritize genuinely new content over unchanged pages.

**Not changed in this audit**, per instructions — this is a findings list, not a fix.

---

## 3. Robots.txt

**File:** `blueprints/pages.py:1122-1133`

```
User-agent: *
Allow: /
Disallow: /kahu
Disallow: /admin

Sitemap: https://keaupuniakeakua.faith/sitemap.xml
```

**Nothing important is blocked.** `Disallow` is scoped only to `/kahu` (the admin login/panel) and `/admin` (admin CRUD routes) — both correctly excluded, since neither should ever be indexed. Every content page, product page, and article is allowed. The `Sitemap:` directive correctly points to the live sitemap URL. Confirmed identical between local code and the live response.

**No accidental blocking found.** Searched the full codebase for `noindex` meta tags and `X-Robots-Tag` headers — zero instances anywhere, in either direction (nothing wrongly blocking real content, and nothing appropriately excluding pages that shouldn't be indexed either — see Section 7 for where that would help).

---

## 4. Metadata

> **RESOLVED (Titles + Meta Descriptions) — Work Order 005 "Unique Metadata Implementation" (2026-07-24, second work order to carry that number this session — see `CLAUDE.md`).** All 8 pages sharing the fallback description, plus `rotten_fencepost.html`, now have unique meta descriptions; the 7 `page.html`-driven pages among them also gained a dedicated `seo_title` field for the `<title>` tag, decoupled from the visible on-page heading so no content was changed. Full implementation record in `CLAUDE.md`. Open Graph, Twitter Cards, and structured data (the rest of this section and Section 5) are unchanged and still open — this work order was scoped to titles/descriptions only.

### Titles
Present on every page checked (16 sampled). Lengths range from 13 characters (`/free_booklets` — "FREE Booklets") to 70 (product page). No missing `<title>` tags found anywhere, including the 5 standalone templates that don't extend `base.html`.

### Meta descriptions — the biggest, most concrete gap found in this audit
**8 of 9 primary content pages share one identical, generic fallback description**, defined in `templates/page.html:4`:

> "Ke Aupuni O Ke Akua - Kingdom ministry from Molokai, Hawaii by Native Hawaiian Pastor Kahu Phil Stephens."

Affected pages (verified via `content.py` — none of these define their own `meta_description`): `/kingdom_wealth`, `/aloha_wellness`, `/call_to_repentance`, `/pastor_planners`, `/nahenahe_voice`, `/free_booklets`, `/kingdom_keys`, `/partner`. (`/` and `/ecosystem` and all 18 SEO sub-pages *do* have their own unique descriptions — that part of the site is done correctly.)

This means 8 distinct, substantively different pages would show **the exact same snippet** in Google search results — a duplicate-metadata pattern that gives Google no page-specific signal and makes results indistinguishable to a searcher.

Additionally, two commercially important standalone pages have **no meta description at all**:
- `templates/rotten_fencepost.html` — the $9 field guide sales page and the homepage's primary CTA target. No `{% block meta_description %}` override, so it also falls back to the same generic line.
- `templates/aloha_wellness_funnel.html` (`/aloha-wellness`) — has a custom `<title>` but zero `<meta name="description">` tag (not even a fallback — the tag is simply absent, since this template doesn't extend `base.html`).

### Canonical URLs

> **RESOLVED — Work Order 008 "Canonical Tags & Internal Link Architecture" (2026-07-24).** Added a self-referencing, absolute-HTTPS canonical tag to the 3 public standalone templates that lacked one (`aloha_wellness_funnel.html`, `kingdom_study.html`, `myron_golden_funnel.html`). `partner_success.html` and `payment_success.html` remain without one — correctly, since they're transactional confirmation pages explicitly out of scope for canonical tags. Full crawl of all 34 sitemap URLs confirmed: exactly one canonical per page, zero duplicates, zero mismatches. Full implementation record in `CLAUDE.md`.

Present sitewide on every template extending `base.html` (`templates/base.html:13`, dynamic per `request.path`, confirmed correct format live: `https://keaupuniakeakua.faith/`). **Absent on the 5 standalone templates**: `aloha_wellness_funnel.html`, `kingdom_study.html`, `myron_golden_funnel.html`, `partner_success.html`, `payment_success.html` — none of these have a `<link rel="canonical">` at all. (Historical record, left as originally written — see the resolution note above.)

### Open Graph / Twitter Cards

> **RESOLVED — Work Order 006 "Open Graph & Social Sharing Metadata Implementation" (2026-07-24).** All 10 required fields (`og:title`, `og:description`, `og:type`, `og:url`, `og:image`, `og:site_name`, `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`) now render on every one of the 36 public pages checked, sourced from each page's own already-established title/description rather than duplicated by hand. Full implementation record in `CLAUDE.md`. Canonical tags (mentioned in the paragraph below, on the 5 standalone templates) and structured data (Section 5) remain open — out of scope for this work order.

**Previously exist on exactly one template: `product_page.html`** (`og:type`, `og:title`, `og:description`, `og:image`, `og:url`, `twitter:card`). Every other page on the site — the homepage, `/rotten-fencepost`, `/kingdom-study`, `/ecosystem`, all 18 article pages, `/products`, `/partner` — had **no Open Graph or Twitter Card tags whatsoever**. Sharing any of these links on Facebook, X, iMessage, Slack, or Discord produced a bare link with no title, description, or preview image. (Historical record, left as originally written — see the resolution note above.)

### Summary table (sampled pages)

> This table is the original audit snapshot, left unedited as the historical record. Title/meta description gaps were resolved in Work Order 005; OG tags in Work Order 006 (now present on every row below, including the standalone-template rows that still show "missing" canonical — canonical tags remain unresolved, see the note above). Don't read this table as current status — see the resolution banners above each subsection instead.

| Page | Title | Meta desc. | Canonical | OG tags |
|---|---|---|---|---|
| `/` | ✓ (54 char) | ✓ (own) | ✓ | ✗ |
| `/kingdom_wealth` | ✓ | fallback | ✓ | ✗ |
| `/rotten-fencepost` | ✓ | fallback | ✓ | ✗ |
| `/aloha-wellness` | ✓ | **missing** | ✓ (WO008) | ✗ |
| `/kingdom-study` | ✓ | ✓ (own) | ✓ (WO008) | ✗ |
| `/myron-golden` | ✓ | ✓ (own) | ✓ (WO008) | ✗ |
| `/ecosystem` | ✓ | ✓ (own) | ✓ | ✗ |
| `/product/<id>` | ✓ | ✓ (own) | ✓ | ✓ |

---

## 5. Structured Data

> **RESOLVED — Work Order 007 "Structured Data / Schema.org Implementation" (2026-07-24).** `WebSite`, `Article`, `Product`, `CollectionPage`, and `BreadcrumbList` schema all implemented, sourced entirely from real site data via a new `schema.py` module. `FAQPage` remains not-applicable (no FAQ content exists to justify it — unchanged from the original finding below). Full implementation record in `CLAUDE.md`.

**Previously existed (historical record):** exactly two JSON-LD blocks, both in `templates/base.html:29-57`, both present on every page that extends `base.html`:
- `Person` (Kahu Phil Stephens)
- `Organization` (Ke Aupuni O Ke Akua Press)

Both validated as syntactically correct JSON via a live parse test.

**What's missing, specific to this site's actual content:**
- **`WebSite`** schema (with a `SearchAction`) — the baseline schema Google uses to potentially show a sitelinks search box; not present anywhere.
- **`Product`** schema (JSON-LD, not just the `og:type="product"` Open Graph tag, which is a different, Facebook-specific convention) — none of the 6 sellable products have real `Product`/`Offer` structured data, which is what would make them eligible for Google's price/availability rich results.
- **`Article`** schema — the 18 wellness/kingdom/scripture-tools pages are genuinely article-shaped content (headline, author, body, publish context) and are the site's best candidates for this, but none is marked up.
- **`BreadcrumbList`** — no page has breadcrumb markup; relevant given the `/wellness/*`, `/kingdom/*`, `/scripture-tools/*`, `/wealth/*` URL structure already implies a natural hierarchy.
- **`FAQPage`** — no FAQ-formatted content currently exists on the site to justify this; not a real gap today, just not applicable yet.

**What's incomplete:** nothing currently implemented is broken or malformed — the gap here is coverage, not correctness.

---

## 6. Internal Linking

> **PARTIALLY ADDRESSED — Work Order 008 "Canonical Tags & Internal Link Architecture" (2026-07-24).** Added 4 natural, contextual internal links between pages that already share subject matter: `/wellness/the-rotten-fencepost-principle` ↔ `/rotten-fencepost`, and `/kingdom/understanding-scripture-through-original-words` → `/kingdom-study`, `/scripture-tools/hebrew-greek-meaning-tool` → `/kingdom-study`. This does not resolve the orphan pages listed below (none of those 4 links target an orphan — the orphans found in the original audit were deliberately left alone rather than forcing an unnatural link just to close them; see `CLAUDE.md` for the reasoning) or add coverage to `/aloha-wellness`, `/myron-golden`, or the still-orphaned product pages. Full implementation record in `CLAUDE.md`.

### Navigation
12 destinations, all working (verified in the Work Order 002 audit and reconfirmed here). Nav does not cover: `/free_booklets`, `/myron-golden`, `/aloha-wellness`, any of the 18 SEO sub-pages, or any individual `/product/<id>` page — all reachable only through body-content links or direct URL.

### Contextual (body-content) links
The 18 SEO sub-pages are well cross-linked to each other and to `/ecosystem` — this part of the site has real link density. `/free_booklets` and `/myron-golden` each have at least one inbound contextual link from another real page (`/free_booklets` from the homepage and `/kingdom_wealth`; `/myron-golden` from `/kingdom_wealth`'s "Myron Golden Kingdom Business Training" link).

### Orphan pages — zero inbound public links found
Searched the entire codebase (templates, `content.py`, `blueprints/pages.py`) for any `href`/markdown link pointing at each of these. Found none, in either direction:

| Orphaned page | Only reference found | Why it matters |
|---|---|---|
| `/aloha-wellness` (hyphen funnel) | `templates/admin/panel.html` (admin-only, not public) | A real, complete, well-built landing page for the Aloha Wellness book. Google has no path to it unless someone links to it externally or it's added to the sitemap directly. |
| `/product/rotten_fencepost_field_guide` | none | The $9 field guide *product page* specifically — `/rotten-fencepost` and `/partner` both link straight to `/checkout/rotten_fencepost_field_guide`, skipping this page entirely. |
| `/product/prod_nahenahe_cd` | none | Music CD product page |
| `/product/prod_kingdom_booklet1`, `/product/prod_kingdom_booklet2` | none | Free booklet product pages (these are `$0` items — see the existing Work Order 001 audit finding on that flow) |
| `/product/partner_tier1` through `partner_tier4` | none | Likely intentional — `/partner` has its own dedicated tier cards and checkout buttons, so a generic `/product/partner_tier1` page may not be meant as a real destination at all. Flagging for confirmation, not as a clear-cut gap. |

None of the above (except the partner tiers) are in the sitemap either, compounding the discovery gap — no nav link, no body link, no sitemap entry.

---

## 7. Indexing Priorities

### Highest Priority (should be indexed immediately)
- `/` — homepage, brand + Rotten Fencepost + Kingdom identity
- `/rotten-fencepost` — primary commercial entrance page, now the homepage's #1 CTA
- `/ecosystem` — the site's own explainer of how everything connects; a strong candidate for ranking on branded + "what is Ke Aupuni O Ke Akua" queries
- `/products` and `/product/prod_find_the_cause_not_the_symptoms` — active commercial pages
- `/call_to_repentance` — the established Kingdom Series entry point, now also the homepage's #2 CTA
- All 18 `wellness/`, `kingdom/`, `wealth/`, `scripture-tools/` article pages — see Section 8, these are the strongest organic-search candidates on the whole site
- `/aloha_wellness`, `/kingdom_wealth` — core content pillars, linked from nav

**Why:** these are the pages a first-time Google visitor is most likely to land on and that most directly represent what the site does and sells.

### Lower Priority (useful, not essential)
- `/pastor_planners`, `/nahenahe_voice` — real content, but niche audiences (pastors needing planners; a specific music recording) with limited organic search volume potential
- `/myron-golden`, `/aloha-wellness` (funnel) — these are **intentionally** built as landing pages for *paid/referral traffic* (their design deliberately omits site navigation to avoid distracting from one conversion goal — noted in the Work Order 001 audit). They don't need strong organic SEO the way article content does; if anything, ranking for broad terms and pulling in cold organic traffic could hurt their conversion-focused design intent. Recommend leaving these as lower-priority rather than "fixing."
- `/partner` — important to the ministry, but donation pages generally aren't strong organic-search targets
- `/kingdom-study` — a $97 upsell page; valuable but more suited to being reached via the site's own funnel (homepage → Study Tools band) than cold search traffic

**Should probably be excluded from indexing entirely** (not just deprioritized): `/checkout/<id>`, `/rotten-fencepost/success`, `/paypal/success`, `/paypal/cancel`, `partner_success.html`/`payment_success.html` pages, and `/thank-you`. These are transactional/confirmation pages with no unique value to a search visitor and no reason to compete for index space. None currently have `noindex` — see Section 9/Recommendations.

---

## 8. Discovery Opportunities

**Not creating content — identifying what's already well-positioned.**

The 18 `_SEO_PAGES` articles (`blueprints/pages.py`) are, structurally, the site's strongest evergreen-search asset:
- Each has a unique title, meta description, and hero image already
- Each targets a specific, real search intent (e.g. "Is Three Meals a Day Necessary?", "Why Diets Fail Long-Term", "What Is the Kingdom of God?")
- They're already organized into three natural clusters that map directly to URL structure:
  - **Wellness cluster** (9 pages under `/wellness/*`) — ancestral eating, fasting/hunger, diet psychology. Strong evergreen health-search potential.
  - **Kingdom cluster** (4 pages under `/kingdom/*`, plus `/call_to_repentance`) — Kingdom theology, repentance, original-language Scripture study. Strong potential for a distinctive, less-crowded theological search niche (most competing content is generic devotional writing, not original-language study).
  - **Scripture Tools cluster** (3 pages under `/scripture-tools/*`) — Hebrew/Greek word study, translation gaps. Narrow but high-intent audience (serious Bible students), likely lower competition.
- `/wealth/biblical-stewardship-principles` stands somewhat alone — a natural candidate for 2-3 more pages to become its own fourth cluster, mirroring the other three.

This clustering is already good information architecture; it just isn't fully connected to the sitemap or cross-promoted as a set (e.g., no "Wellness Hub" or "Kingdom Hub" landing page separate from `/ecosystem`'s brief overview).

---

## 9. Manual Google Tasks (cannot be done in code — requires Kahu Phil's Google account access)

> **NEW — Work Order 009 (2026-07-24).** Found a genuine technical defect that requires Cloudflare/Render dashboard access, not a Google account, added here as the same category of "can't be fixed in this codebase" item — see the checklist item below.

- [ ] **Fix or remove the `www` subdomain.** `www.keaupuniakeakua.faith` resolves in DNS (Cloudflare-proxied, pointing at the same Render origin as the apex domain) but has no working TLS certificate or redirect rule: HTTPS requests fail with a TLS handshake failure, and plain HTTP requests return a bare `409 Conflict` from Cloudflare instead of a redirect to `https://keaupuniakeakua.faith`. Confirmed via `openssl s_client` and raw HTTP requests — not a browser/client quirk. If anyone or anything (a backlink, a typed-in URL, a search engine) ever tries the `www` form, they hit a broken connection instead of landing on the site. Fix requires either removing the `www` DNS record entirely, or configuring it as a proper custom domain alias in Render with a 301 redirect to the apex domain — both are dashboard actions, not code changes.
- [ ] **Confirm Search Console ownership is actually claimed.** The verification meta tag is live on the site (Section 1), but that only proves the tag exists — someone needs to log into [Google Search Console](https://search.google.com/search-console) with the account tied to this property and confirm it shows as verified.
- [ ] **Submit `https://keaupuniakeakua.faith/sitemap.xml` in Search Console** (Sitemaps section), once the sitemap omissions in Section 2 are addressed.
- [ ] **Same for Bing Webmaster Tools** (verification already present via `msvalidate.01` + `BingSiteAuth.xml` — confirm the property is claimed there too).
- [ ] **Request indexing** for the highest-priority pages listed in Section 7 directly via Search Console's URL Inspection tool, once metadata gaps are fixed — this can speed up initial discovery rather than waiting for organic crawl.
- [ ] **Review Google Analytics 4** (already installed, `G-V2NY3MEWKB`) to confirm it's actually receiving traffic and connected to the same Google account as Search Console — useful for measuring whether any of this work is moving the needle.
- [ ] **Decide on Google Merchant Center / Rich Results** if `Product` structured data is added later (Section 5) — that's a separate Google product/account with its own setup, only relevant once the code-side schema work exists.

None of these require code changes and none were attempted in this audit, per instructions.

---

## Recommended Engineering Sequence (for a future work order)

Ordered by priority, with effort and whether Google account access is needed:

| # | Recommendation | Priority | Effort | Type | Status |
|---|---|---|---|---|---|
| 1 | Add the missing real pages to `sitemap.xml` (`/ecosystem`, `/partner`, `/rotten-fencepost`, `/aloha-wellness`, 3 `scripture-tools/*` pages) | High | Low | Code-only | **DONE — Work Order 005** |
| 2 | Write unique meta descriptions for the 8 pages sharing the generic fallback, plus `rotten_fencepost.html` and `aloha_wellness_funnel.html` | High | Medium | Code-only | **DONE for 8 + `rotten_fencepost.html` — Work Order 005 (2nd).** `aloha_wellness_funnel.html` (a standalone template, not part of the original 8) still open. |
| 3 | Add sitewide Open Graph + Twitter Card tags to `base.html` (dynamic per-page, using existing `page.title`/`hero_image`) so every page — not just products — gets a real social preview | High | Low–Medium | Code-only | **DONE — Work Order 006.** |
| 4 | Add `noindex` to transactional pages (`/checkout/*`, success/thank-you pages) | Medium | Low | Code-only | Not started |
| 5 | Add canonical + OG tags to the 5 standalone templates (`aloha_wellness_funnel.html`, `kingdom_study.html`, `myron_golden_funnel.html`, `partner_success.html`, `payment_success.html`) | Medium | Low | Code-only | **OG tags DONE — Work Order 006. Canonical DONE for the 3 public templates — Work Order 008.** `partner_success.html`/`payment_success.html` correctly remain without canonical (transactional, out of scope). |
| 6 | Resolve orphan pages — link `/product/rotten_fencepost_field_guide` from somewhere public, or confirm intentional and leave as-is (`/aloha-wellness` is now in the sitemap as of Work Order 005, which helps discovery but doesn't add an internal link to it) | Medium | Low | Code-only | Partially addressed. **Work Order 008** added 4 natural contextual links elsewhere on the site (see Section 6) but did not target this specific orphan list — `/product/rotten_fencepost_field_guide`, the other orphaned product pages, and `/aloha-wellness`/`/myron-golden` still have no inbound body-content link; still open. |
| 7 | Add `Product` JSON-LD to product pages, `Article` JSON-LD to the 18 content pages, `WebSite` schema to `base.html` | Medium | Medium–High | Code-only | **DONE — Work Order 007.** (No `SearchAction`: the site has no genuine site-search feature, and the work order explicitly said not to add one merely for appearance.) |
| 8 | `sitemap.xml`'s `<lastmod>` | Low | Low–Medium | Code-only | **RESOLVED — Work Order 005.** Determined a reliably accurate per-page value isn't achievable without either a real CMS/timestamp layer (out of scope) or fragile runtime `git log` calls (introduces the "unnecessary complexity" the work order explicitly said to avoid). Removed `<lastmod>` entirely rather than continue fabricating "today" on every request — see `CLAUDE.md` for full reasoning. |
| 9 | Confirm/complete the manual Google Search Console + Bing Webmaster Tools setup (Section 9) | High | — | Google account access | Not started |
| 10 | Add `BreadcrumbList` schema | Low | Medium | Code-only | **DONE for the 18 SEO articles (Home → Article) and product pages (Home → Products → Product) — Work Order 007.** A 3-level breadcrumb for articles (Home → Category → Article) was considered and deliberately not done — no real `/wellness`, `/kingdom`, etc. index page exists to link the middle level to, and inventing one just for the breadcrumb would be exactly the fabrication the work order prohibited. Building real category hub pages first (see Section 8's cluster discussion) would unlock this. |

Items 1 and 8 are complete as of Work Order 005 (2026-07-24) — see `CLAUDE.md` Change Log for the deployed commit and live verification. All other items are unchanged from the original audit and awaiting a future work order.
