# Sitewide Layout Root-Cause Investigation

> **RESOLVED — Work Order 004-C (2026-07-24).** All 26 pages listed below were corrected. See "Implementation (Work Order 004-C)" near the end of this document for what was done and how it was verified. The investigation content below (Work Order 004-B) is left as-written — it's the record of what was found and why the fix was scoped the way it was.

**Date:** 2026-07-24
**Scope:** Work Order 004-B — investigation only. No code was changed, nothing was committed.
**Method:** Full inspection of `templates/base.html`, `templates/page.html`, every other template in `templates/`, and `templates/partials/styles.css`. Every page/template was individually checked for actual class usage (not assumed) via a direct grep sweep across all templates for `container`, `content-card`, and `hero` class references. No live browser was available this session, so final pixel-level severity is not confirmed — the mechanism and which pages are structurally affected are confirmed from CSS/template source, which is unambiguous.

## Answer to the objective

**Yes — the overlapping-content issue is caused by the shared site layout, not the homepage.** Correction 003-A fixed exactly one page (the homepage) by giving it its own non-overlapping layout classes. The underlying mechanism that caused the original bug — `.container`'s `position: absolute; top: 0; height: 100vh` layering page content on top of the hero — is still in use, unmodified, on **26 other pages**. It was never the source of the bug; it's still there, doing the same thing it always did.

---

## Root Cause

`templates/partials/styles.css`:

```css
.hero {
    height: 100vh; min-height: 600px;
    position: relative; display: flex; align-items: flex-end; overflow: hidden;
}
.container {
    max-width: 1500px; margin: 0 auto; padding: 2rem;
    position: absolute; top: 0; left: 50%; transform: translateX(-50%);
    width: 100%; height: 100vh; overflow-y: auto; z-index: 3;
}
.content-card {
    background: rgba(0,0,0,0.25); border: none;
    padding: 3rem 5rem; box-shadow: none;
    margin-top: 25vh; padding-top: 4rem; color: white; text-align: center;
}
```

`templates/page.html` renders, for every page except home:
```html
<header class="hero">
    <div class="hero-overlay"></div>
    <div class="hero-content"><h1>{{ page.title }}</h1></div>
</header>
...
<main class="container">
    <article class="content-card">{{ body_html|safe }}</article>
</main>
```

**The mechanism, precisely:**

1. `<header class="hero">` is a normal-flow element, `position: relative`, occupying document space `y: 0` to `y: 100vh` (desktop).
2. `<main class="container">` is `position: absolute; top: 0`. Since neither `<body>` nor `<html>` sets `position`, its containing block is the page's initial containing block — so `top: 0` anchors it to the very top of the *document*, not wherever it falls in source order. It ends up occupying the exact same `y: 0` to `y: 100vh` region as the hero, not the region *after* it.
3. `.container` has `z-index: 3`; `.hero` has no explicit `z-index` (stacks below any sibling with a positive value). So `.container`'s content — the article body, starting with `.content-card`'s `margin-top: 25vh` peeking through the top quarter of the hero photo — renders **on top of** the hero, for that entire first screen.
4. Because `.container` is taken out of normal flow, it contributes **zero height** to the page's own scrollable flow. The footer (a normal-flow sibling after `<main>`) sits immediately after the hero's `100vh` in document flow — so the browser's own page-scroll only spans "hero height + footer height," largely bypassing the article body entirely.
5. `.container { height: 100vh; overflow-y: auto }` gives the article body its own **separate, nested scroll region** confined to that first screen. The actual article text is reachable, but only by scrolling *inside* that region — a second, independent scroll gesture layered on top of the page's normal one, not a single continuous scroll a visitor would expect. (Standard browser scroll-chaining means a mouse wheel over that region will scroll it first, then fall through to the outer page once it's exhausted — so nothing is a hard dead end, but the experience is a confusing double-scroll rather than one predictable page.)

**This is exactly the same mechanism the homepage had**, just less visually obvious there before Work Order 003, because the pre-003 hero either had no visible title at all (`.hero h1 { display: none }`, before Work Order 002) or just one bottom-anchored title line (after 002) — not enough content for the overlap to register as "broken" the way the new multi-element hero/CTA stack did. **On the 26 pages below, the exact same single-title-line hero is still overlapping with that page's own scrolling article body in the same way** — just quieter, because there's less hero content to notice colliding with it.

### Important nuance: desktop-only

`templates/partials/styles.css`, inside the existing `@media (max-width: 768px)` block:
```css
.container { position: relative; height: auto; margin-top: 0; padding: 0 1rem 2rem; transform: none; left: 0; }
```
At 768px and below, `.container` is already safe — plain normal flow, no absolute positioning, no nested scroll. **The bug only exists above 768px** (tablet-landscape and desktop widths). This is presumably why it wasn't caught earlier: most casual review — and most real traffic — skews mobile, where this has never been broken.

---

## Every Public Page

| Page | Route | Template | Layout classes used | Overlap risk |
|---|---|---|---|---|
| Home | `/` | `page.html` | `.home-hero` / `.home-container` / `.home-content-card` | **Fixed (003-A)** |
| Kingdom Wealth | `/kingdom_wealth` | `page.html` | `.hero` / `.container` / `.content-card` | **Yes** |
| Aloha Wellness | `/aloha_wellness` | `page.html` | `.hero` / `.container` / `.content-card` | **Yes** |
| Call to Repentance | `/call_to_repentance` | `page.html` | `.hero` / `.container` / `.content-card` | **Yes** |
| Pastor Planners | `/pastor_planners` | `page.html` | `.hero` / `.container` / `.content-card` | **Yes** |
| Nahenahe Voice | `/nahenahe_voice` | `page.html` | `.hero` / `.container` / `.content-card` | **Yes** |
| Free Booklets | `/free_booklets` | `page.html` | `.hero` / `.container` / `.content-card` | **Yes** |
| Kingdom Keys | `/kingdom_keys` | `page.html` | `.hero` / `.container` / `.content-card` | **Yes** |
| Ecosystem | `/ecosystem` | `page.html` (via bespoke view fn) | `.hero` / `.container` / `.content-card` | **Yes** |
| 6 `wellness/*` pages (why-diets-fail, lose-weight-without-dieting, three-meals-a-day-necessary, ancestral-eating-patterns, why-modern-health-advice-feels-confusing, why-your-body-resists-diets) | `/wellness/*` | `page.html` | `.hero` / `.container` / `.content-card` | **Yes** (all 6) |
| 4 more `wellness/*` pages (eating-when-hungry, the-rotten-fencepost-principle, kupuna-wisdom-and-modern-health, god-never-told-adam-when-to-eat) | `/wellness/*` | `page.html` | `.hero` / `.container` / `.content-card` | **Yes** (all 4) |
| 4 `kingdom/*` pages (what-is-the-kingdom-of-god, jesus-kingdom-message, understanding-scripture-through-original-words, stewardship-in-the-kingdom-of-god) | `/kingdom/*` | `page.html` | `.hero` / `.container` / `.content-card` | **Yes** (all 4) |
| Biblical Stewardship Principles | `/wealth/biblical-stewardship-principles` | `page.html` | `.hero` / `.container` / `.content-card` | **Yes** |
| 3 `scripture-tools/*` pages | `/scripture-tools/*` | `page.html` | `.hero` / `.container` / `.content-card` | **Yes** (all 3) |
| Rotten Fencepost | `/rotten-fencepost` | `rotten_fencepost.html` | `.hero`/`.hero-content`/`.hero-overlay` only — own normal-flow body divs, never uses `.container`/`.content-card` | No |
| Rotten Fencepost Success | `/rotten-fencepost/success` | `rotten_fencepost_success.html` | `.success-card` (own class, normal flow, added in Work Order 002) | No |
| Partner | `/partner` | `partner.html` | `.partner-hero`/`.partner-container` (own classes, normal flow — never used the shared pattern at all) | No |
| Product detail | `/product/<id>` | `product_page.html` | `.product-page-wrap` (own class, normal flow, added in Work Order 002) | No |
| Checkout | `/checkout/<id>` | `checkout.html` | `.checkout-container` (own class, normal flow, added in Work Order 002) | No |
| Products listing | `/products` | `products.html` | `.hero`/`.hero-content`/`.hero-overlay` only — own normal-flow body div, never uses `.container`/`.content-card` | No |
| Thank You | `/thank-you` | `thank_you.html` | `.content-card` class only, **not** wrapped in `.container` (no `position:absolute` ancestor), and the page has no hero at all — safe | No |
| Kingdom Study | `/kingdom-study` | `kingdom_study.html` (standalone) | Own embedded `<style>`, defines its own unrelated `.container`/`.hero` classes scoped to this one document — no relation to the shared site CSS | No |
| Myron Golden | `/myron-golden` | `myron_golden_funnel.html` (standalone) | Own embedded styles, no shared classes | No |
| Aloha Wellness Funnel | `/aloha-wellness` | `aloha_wellness_funnel.html` (standalone) | Own embedded styles, no shared classes | No |
| PayPal/Stripe success | `/paypal/success`, `/stripe/success` | `payment_success.html` (standalone) | Own embedded `.container` (unrelated, simple white card) | No |
| Partnership success | (partnership payment flow) | `partner_success.html` (standalone) | Own embedded `.container` (unrelated, simple white card) | No |

**Total structurally affected: 26 pages**, all sharing the identical `page.html` template and the identical `.hero` + `.container`/`.content-card` combination. **0 false negatives found** — every other template was individually verified to either not use these classes at all, or (in 3 cases — `kingdom_study.html`, `partner_success.html`, `payment_success.html`) to define its own same-named-but-unrelated local class inside its own standalone `<style>` block, which shares no CSS with `templates/partials/styles.css` and poses no risk.

One footnote unrelated to layout: `content.py`'s `DEFAULT_PAGES` still contains a `"partner"` entry, but the dedicated `/partner` route (matched by Flask before the generic `/<page_id>` catch-all, since static routes always win over dynamic ones) renders `partner.html` instead — so that data entry is dead, never actually reaches `page.html`. Not a layout bug, just worth knowing if that data is ever edited expecting it to take effect.

---

## Why Correction 003-A Didn't Catch This

003-A's fix (`.home-container`/`.home-content-card`, applied via a template conditional scoped to `current_page == 'home'`) was scoped correctly to the reported problem — the homepage was the only page anyone had visually inspected and flagged. The fix pattern itself (normal-flow classes instead of the absolute overlay) is directly reusable for the other 26 pages; it just wasn't extended to them because the work order that produced it was explicitly scoped to the homepage only ("Scope this correction only to the homepage... Preserve the existing overlay behavior on all non-home `page.html` pages").

---

## Recommendation (original plan, from Work Order 004-B — see below for what was actually done)

**Safest migration strategy, if approved:** extend the exact same pattern already proven on the homepage — normal-flow `.home-container`/`.home-content-card`-equivalent classes — to all 26 remaining `page.html`-driven pages, via the same `current_page`-based template conditional already in `page.html`, rather than modifying the shared `.container`/`.content-card` rules in place.

Why this order of operations minimizes regression risk:
1. **One shared template, one shared fix.** All 26 pages render through the exact same `page.html` file with the exact same structure — there's no per-page template variation to account for. A single CSS/template change covers all 26 at once, the same way the homepage fix did.
2. **The `.container`/`.content-card` classes themselves should not be edited in place.** Doing so would need to simultaneously handle every page currently depending on their current behavior — better to keep them exactly as they are (as `.home-container`/`.home-content-card` already do, coexisting with the originals) and simply point every page at the safe versions.
3. **Lowest-risk sequencing:** verify the fix against 2–3 representative pages first (e.g., one short page like `/kingdom_keys`, one long article like `/wellness/why-diets-fail`, and the hub page `/ecosystem`) before rolling it out to all 26, since they're all driven by the same template change simultaneously — a mistake would affect all of them at once, so confirming correctness on a few first is worth the extra step even though the code change itself is a single edit.
4. **Do not touch** `rotten_fencepost.html`, `partner.html`, `product_page.html`, `checkout.html`, `products.html`, `thank_you.html`, or any of the 6 standalone templates — confirmed above that none of them are affected, and touching them would be unrelated scope.

No effort estimate is given here since implementation was explicitly out of scope for this work order.

---

## Implementation (Work Order 004-C)

**One deviation from the plan above, made deliberately:** the original plan (point 2) said not to edit `.container`/`.content-card` in place. Once implementation started, it became clear that *every single page* using those two classes was on the affected list — there was no page anywhere in the codebase that still needed the old `position: absolute` behavior. With that confirmed, editing `.container`/`.content-card` directly was simpler and lower-risk than duplicating `.home-container`/`.home-content-card` under new names and rewiring 26 pages' worth of template conditionals to point at them: one CSS change covers all 26 pages, `page.html`'s existing `{% if current_page == 'home' %}...{% else %}container...{% endif %}` conditional needed **zero changes** (both branches already produce a normal-flow layout now), and there is nothing left anywhere depending on the old absolute-positioned behavior to break.

**What changed**, in `templates/partials/styles.css`:
- `.container` — removed `position: absolute; top: 0; left: 50%; transform: translateX(-50%); height: 100vh; overflow-y: auto; z-index: 3`. What remains: `max-width: 1500px; margin: 0 auto; padding: 2rem; width: 100%` — a plain, normal-flow block, matching `.home-container` exactly.
- `.content-card` — removed `margin-top: 25vh` (the "peek through the hero" offset that only made sense when this box was layered on top of the hero) and `padding-top: 4rem`, replaced with `padding-top: 3rem` — matching `.home-content-card`.
- The mobile (`≤768px`) override block was simplified: it used to re-declare `position: relative; height: auto; margin-top: 0; transform: none; left: 0` on `.container` to undo the desktop absolute-positioning — all of that is now a no-op since desktop no longer sets those properties, so it was removed, keeping only the mobile-specific padding value it still legitimately needs. `.content-card`'s mobile padding was aligned with `.home-content-card`'s equivalent for consistency.
- `.home-hero`, `.home-container`, `.home-content-card`, and the homepage-specific hero content in `page.html` — **untouched**, exactly as Correction 003-A left them, per this work order's explicit instruction.
- `page.html` itself — **no changes**. Its existing conditional already routes home to `.home-container`/`.home-content-card` and everything else to `.container`/`.content-card`; both are now safe.

**Templates confirmed untouched** (verified via diff, not just by not editing them): `rotten_fencepost.html`, `partner.html`, `product_page.html`, `checkout.html`, `products.html`, `thank_you.html`, `aloha_wellness_funnel.html`, `kingdom_study.html`, `myron_golden_funnel.html`, `partner_success.html`, `payment_success.html`.

### Representative verification (before treating the full 26 as done)

Checked `/kingdom_wealth` (primary content page), `/ecosystem` (hub page), and `/kingdom/understanding-scripture-through-original-words` (the longest article page on the site by rendered size, 24.6KB of HTML — chosen specifically to stress-test whether long content still flows correctly). On all three, confirmed via the Flask test client:
- Document order is `<header class="hero">` → `<main class="container">` → `<article class="content-card">` → `<footer>`, in that exact sequence.
- Each page's own inlined `.container` CSS rule contains no `position` property at all (i.e., no absolute positioning survived).
- Nav and the "More" dropdown render normally.

### Full rollout verification (all 26 pages)

- Added `tests/test_shared_layout.py` (59 new test cases): every one of the 26 affected pages returns 200 and renders through `class="container"`/`class="content-card"`; a direct regression guard asserting `.container`'s CSS rule never contains `position: absolute` again; confirmation the homepage still renders its own `.home-container`/`.home-content-card` (and *not* the shared `.container`); and spot checks that `/rotten-fencepost`, `/partner`, `/product/<id>`, and `/products` (representative "independently safe" templates) still render normally.
- **Full test suite: 170/170 pass** (111 pre-existing + 59 new).
- **Full 35-page/49-link crawl: zero broken links.**
- **Commerce/download regression check:** `/product/<id>`, `/checkout/<id>` both 200; PayPal button container and Stripe form both still present on checkout (verified with credentials monkeypatched present, matching prior work orders' verification method); the download-token endpoint returns the identical response to an invalid token as it did before this change (503, an unrelated pre-existing local-environment behavior, not a regression — `download_tokens.py` was not touched).

### Mobile

Mobile (`≤768px`) was never affected by the original bug — a pre-existing override already made `.container` normal-flow at that width. That override is simplified (redundant declarations removed) but not functionally changed, so mobile behavior is preserved exactly as it was.

---

## Stop Point

Work Order 004-B: no code was changed, nothing was committed — investigation only.
Work Order 004-C: implementation complete, locally verified. See `CLAUDE.md` for commit/deploy/live-verification record.
