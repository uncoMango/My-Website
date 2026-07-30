# Product Discovery Distribution Kit

**Discovery Operations — Work Order 002**
**Deliverable type:** Finished, ready-to-use operational asset (not a strategy document)
**Date produced:** 2026-07-25
**Current subject:** Product 001 — "Find the Cause, Not the Symptoms"
**Companion tracker:** `discovery_distribution_tracker.csv`

---

## 1. Why This Work Order Was Selected

Per `DISCOVERY_OPERATIONS_BASELINE.md` (Discovery Operations — Work Order 001), the technical foundation is complete and verified, but three concrete numbers in that baseline are all zero:

- **0 confirmed organic visibility** (Section 5) — no search results for the domain observed.
- **0 subscribers** (Section 7) — the site's own email capture has never converted a visitor.
- **0 sales** (Section 6).

The same baseline's Section 10 ("Current Bottlenecks") states plainly: *"No backlink data exists in this environment. The only confirmed outbound social presence is one YouTube channel; whether it (or anything else) sends referral traffic is unverifiable here."* And Section 11 ("Remaining Manual Tasks") shows that the other candidate levers — GSC indexing requests, Bing Webmaster Tools, GA4 traffic review, the `www` DNS fix — all require Kahu Phil's own account logins and cannot be completed inside this environment.

That leaves one clear, evidence-grounded, *completable* highest-leverage lever: **the site currently has no external links pointing to it, and no presence anywhere off-site.** A new site with strong on-page SEO but zero inbound links and zero off-site presence has no path into a search engine's crawl graph and no way for a person to encounter it who isn't already looking for it by exact name. Establishing a small number of real, legitimate, free off-site listings does three things at once: gives crawlers new paths to discover and index the site, gives the domain its first real backlinks, and creates direct referral-traffic entry points — the same three zeros in the baseline.

This is a distribution/citation problem, not an engineering problem or a content problem — it requires no code change and no change to Product 001's existing content, satisfying the operating constraints for this work order.

## 2. The Deliverable

Two finished artifacts, both usable today with no further work:

1. **This kit** — a complete, copy-paste-ready listing package for Product 001, plus a vetted list of legitimate, free, real off-site channels with exact submission steps for each.
2. **`discovery_distribution_tracker.csv`** — a pre-populated tracking spreadsheet (Channel, Status, Date, Live URL, Notes) that turns each submission into a measurable, checkable event. This is the actual measurement instrument going forward — open it in any spreadsheet tool.

Everything in Section 4 below is copied verbatim from data already verified to exist in the live codebase (`digital_products.json`, `config.py`) — nothing here is new or invented content about Product 001.

## 3. Selection Criteria for Channels

Every channel listed below was checked against three requirements before inclusion:

- **Real and verifiable.** Each URL below was fetched or searched during this session and confirmed to be the platform's actual, current entry point — not guessed.
- **Free.** No paid submissions are included.
- **Legitimate and durable.** Established platforms (Google, Microsoft/Bing, Goodreads) with real editorial/verification processes — not link farms or "SEO directory" spam sites, which risk doing more harm than good to a brand-new domain's trust signals.

Anything requiring information this session doesn't have (e.g., a business mailing address for Google Business Profile verification) is marked accordingly — the copy is ready, but Kahu Phil must supply that one missing field and complete the identity verification himself, since that step cannot be done by anyone other than the account owner.

## 4. Ready-to-Use Listing Package — Product 001

Copy these fields directly into any submission form below. Source: `digital_products.json` (`prod_find_the_cause_not_the_symptoms`) and `config.py`, verified in the live codebase.

| Field | Value |
|---|---|
| **Title** | Find the Cause, Not the Symptoms |
| **Subtitle** | A Rotten Fencepost Foundational Guide |
| **Author** | Kahu Phil Stephens |
| **Publisher** | Rotten Fencepost Publishing |
| **Series** | Rotten Fencepost |
| **Format / Price** | Digital ebook (PDF), $9.99 |
| **Short description** (155 chars, for fields with tight limits) | Discover why recurring problems continue to return and learn a practical framework for identifying root causes instead of repeatedly treating symptoms. |
| **Long description** (for fields with more room) | Most people spend their lives treating symptoms instead of discovering what caused the problem in the first place. Using the simple illustration of a rotten fencepost, Kahu Phil Stephens presents a practical framework that helps readers identify hidden causes behind recurring problems in health, finances, relationships, leadership, work, and everyday life. Instead of asking, "How do I fix this?" — learn to ask, "What caused this problem to appear?" That one question can change everything. |
| **Link to send people to** | `https://keaupuniakeakua.faith/rotten-fencepost` |
| **Website / organization** | Ke Aupuni O Ke Akua — `https://keaupuniakeakua.faith` |
| **Contact email** | kahuphil@keaupuni.faith |
| **YouTube channel (existing, owned asset)** | `https://www.youtube.com/@keaupuniokeakua` |

**Why `/rotten-fencepost` and not `/product/prod_find_the_cause_not_the_symptoms`:** both URLs are live, indexable pages for the same product (confirmed in the codebase — this is an existing, pre-Discovery-Operations characteristic of the site, not something this work order changes). `/rotten-fencepost` is the one the site's own sitemap already weights higher (priority 0.9, weekly, vs. 0.8, monthly) and is described in the engineering record as "the homepage's primary CTA." Sending every new external link to the same one URL, rather than splitting them across two pages for the same product, concentrates whatever backlink value these listings create instead of diluting it. This is a distribution choice for where new external links point, not a change to the site itself.

## 5. Channels — Exact Steps

### 5.1 YouTube channel "About" link (do this first — zero signup required)

The site already has one confirmed, owned channel: `https://www.youtube.com/@keaupuniokeakua`. Whether its channel description/"About" section currently links back to the site is unverifiable from this environment (no channel-management access here). This is the fastest possible win because no new account or verification is needed:

1. Go to the channel's YouTube Studio → Customization → Basic Info.
2. Confirm (or add) the site link in the channel description and the "Links" section, pointing to `https://keaupuniakeakua.faith/rotten-fencepost`.
3. On the next video uploaded (or by editing an existing video's description), add the same link.

### 5.2 Google Business Profile (highest general-purpose leverage)

Official entry point: `https://business.google.com` (redirects through Google's own account flow — this is the correct, official URL, not a third party).

Confirmed via Google's own support documentation: a business with no public storefront can register as a **Service Area Business (SAB)**. Google still requires one real address for identity verification, but that address is never made public — only the service area (e.g., "Hawaiʻi" or specific islands) is shown.

Missing input this session cannot supply: **a real mailing address for verification.** Everything else in Section 4 is ready to paste in. Kahu Phil must provide the address and complete phone/postcard verification himself — this is an identity-verification step no one else can complete on his behalf.

### 5.3 Bing Places for Business

Official entry point: `https://www.bing.com/forbusiness/` (confirmed live during this session). Free, same category as Google Business Profile but for Microsoft's Bing/Yahoo search and Bing Maps — directly relevant since this site's `msvalidate.01` Bing verification tag is already installed in the codebase. Same Service-Area-Business option and the same missing-address caveat as 5.2.

### 5.4 Goodreads

Confirmed via Goodreads' own Author Program page (`https://www.goodreads.com/author/program`) during this session. Two steps, since this book is self-published and not already in Goodreads' catalog:

1. **Add the book.** Because it has no ISBN/ASIN and isn't yet in Goodreads' database, it must first be added manually through Goodreads' book-request process (search the title on Goodreads; if it doesn't appear, use the "Add a new book" / Librarian request flow, using the fields from Section 4 — cover image can use the site's existing `find_the_cause_not_the_symptoms_cover_web.jpg`).
2. **Claim authorship.** Once the book exists in Goodreads' database, go to `https://www.goodreads.com/author/program`, find the book, click "Is this you? Let us know!" on the author page, and submit the application. Goodreads states approval typically takes about 2 business days.

This is the one channel here likely to take more than a few minutes, since it depends on Goodreads' review queue — everything on Kahu Phil's side (the copy, the cover image) is already prepared above.

## 6. Reusing This Kit for Future Products

This kit is deliberately structured so it is not Product-001-specific:

- Section 4's table maps 1:1 to fields that already exist on every entry in `digital_products.json` (`name`, `subtitle`, `author`, `publisher`, `series`, `price`, `meta_description`, `description`) plus the two fixed site-level fields in `config.py` (`CONTACT_EMAIL`, `SITE_DOMAIN`). Producing this same table for any future product is a data pull, not new writing.
- Section 5's channel list and steps are entirely product-agnostic — the same four channels and the same process apply to any product this ministry publishes next, with no changes needed to the instructions themselves.
- `discovery_distribution_tracker.csv` uses a `Product` column specifically so future products' rows can be added to the same file rather than creating a new tracker each time.

No engineering or template work is required to extend this to Product 002 or beyond when that phase begins.

## 7. What This Does Not Do

- Does not touch any code, template, or Product 001 content — no files under `templates/`, `content.py`, `digital_products.json`, `blueprints/`, or `schema.py` were modified.
- Does not itself submit anything to any external platform. Account creation, identity verification, and form submission on Google, Bing, YouTube, and Goodreads all require Kahu Phil's own logins and, in two cases, physical-address verification only he can complete. This kit exists so that work takes minutes instead of research time, not to bypass account ownership.
- Does not modify the roadmap or reopen any Discovery Engineering work order.

## 8. Verification That Work Order 002 Is Complete

- [x] Single highest-priority lever identified, with evidence traced directly to `DISCOVERY_OPERATIONS_BASELINE.md` Sections 5, 7, and 10 (Section 1 above).
- [x] Finished, immediately usable asset produced — not a recommendation or strategy document (Sections 4–5: real, fetched-and-confirmed URLs; copy-paste-ready content, sourced verbatim from verified existing data).
- [x] Companion tracker produced as the measurement instrument (`discovery_distribution_tracker.csv`).
- [x] No engineering changes made; no files under application code touched.
- [x] No Product 001 content changed.
- [x] No Product 002 work begun.
- [x] Explicitly reusable for future products without redesign (Section 6).
