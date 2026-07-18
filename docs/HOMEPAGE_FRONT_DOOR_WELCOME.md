# Homepage Front-Door Welcome — Report

**Status: NOT deployed.** All changes are unstaged in the working tree. Nothing has been committed, pushed, or deployed. Waiting on Kahu Phil's review and explicit approval.

## Files inspected (Phase 1)

`blueprints/pages.py`, `templates/page.html`, `templates/base.html`, `templates/partials/styles.css`, `content.py`, `config.py`, `website_content.json`, `tests/test_security.py`, and the live route table (`grep @pages_bp.route`).

Findings reported at the time (before any edit):
- Homepage route: `GET /` → `blueprints/pages.py::home()` → `templates/page.html` (extends `templates/base.html`).
- One CSS file, inlined: `templates/partials/styles.css`.
- Home-only blocks (founding-reader offer, free-guide bar, Kingdom Study Tools band, Ecosystem band) are hardcoded in `page.html`, gated by `current_page == 'home'` — not JSON-driven.
- Best existing routes for the four visitor choices: `/call_to_repentance` (Kingdom/Bible Truth), `/aloha_wellness` (Health), `/kingdom_wealth` (Wealth), `/kingdom_keys` (free booklets) — all already used by both the nav and the home page's own body copy.
- Mobile nav: hamburger toggle JS and `.nav-menu.active` CSS present and structurally standard; not visually confirmed in a real browser (see Testing section below for why).
- Working tree was clean before this task started.

## A mid-task discovery that changed the plan

While consolidating the homepage copy, I found that **`website_content.json` is not actually the live content source**. `content.py`'s `load_content()` is hardcoded to `return DEFAULT_PAGES` — a Python dict literal in the same file — and never reads the JSON file at all, despite `config.py` defining a `DATA_FILE` path for it. The JSON file is written by `/kahu` edits' `save_content()` call but never read back.

This means:
- My first edit (removing a duplicate closing line from `website_content.json`) had **zero effect** on the live site, because that file isn't read.
- The actual home page content that visitors see lives in `content.py`'s `DEFAULT_PAGES["pages"]["home"]["body_md"]`, which is a longer, slightly different, and more current version of the same copy — I applied the equivalent fix there instead (see Files changed below).
- **This is a separate, likely serious problem I did not attempt to fix**, per your Phase 7 instruction to document and stop rather than silently repair unrelated files. If admin edits made through `/kahu` only mutate the in-memory `DEFAULT_PAGES` dict for the lifetime of the running process, they would appear to work immediately but be silently lost on the next Render restart or redeploy, since a fresh process re-reads the hardcoded literal in `content.py`, not the JSON file. I have not verified this theory against the live server — it's based on reading the code only. **This needs your attention separately from the homepage work in this report**, and probably needs live confirmation (edit a page via `/kahu`, restart the Render service, check whether the edit survived) before deciding how urgent it is.

## Files changed

| File | What changed |
|---|---|
| `templates/page.html` | Reordered the home-only blocks and added the new welcome section. See exact content below. |
| `content.py` | Removed the now-redundant trailing line `*Aloha. You are in the right place.*` from `DEFAULT_PAGES["pages"]["home"]["body_md"]` (this is the actual live content — see discovery above). Nothing else in this file touched. |
| `website_content.json` | Same single-line removal, for consistency, even though this file isn't currently read by the live app. Harmless either way. |
| `tests/test_homepage.py` (new) | 17 new tests for the welcome section, described below. |

No other files were touched. `config.py`, `blueprints/admin.py`, `blueprints/payments.py`, `blueprints/products.py`, `auth.py`, environment-variable handling, and the nav markup in `base.html` are all untouched.

## Exact homepage content added, moved, or removed

**Added** (new block in `templates/page.html`, home-only, placed immediately after the hero):

- Heading (h2): "Aloha. You are in the right place."
- Two short intro sentences, close to your suggested copy, adapted slightly to avoid duplicating the fuller version that already exists further down the page:
  > "I'm Kahu Phil Stephens — a pastor, Paniolo, and lifelong student of Scripture, writing from Molokaʻi, Hawaiʻi."
  > "Ke Aupuni O Ke Akua exists to help people rediscover the Kingdom of God and live its truth through Scripture, wellness, and faithful stewardship."
- Subheading (h3): "Where would you like to begin?"
- Four choice cards (each a single clickable link/card, exact copy as you specified):

| Choice | Description | Links to |
|---|---|---|
| Understand the Kingdom | Explore what Jesus taught about the Kingdom of God through Scripture and original-language study. | `/call_to_repentance` |
| Strengthen Your Health | Discover practical wellness principles rooted in Scripture and lived experience. | `/aloha_wellness` |
| Practice Faithful Stewardship | Learn Kingdom principles for managing what God has placed in your hands. | `/kingdom_wealth` |
| Start With Something Free | Begin with short Kingdom booklets created to make these teachings understandable and useful. | `/kingdom_keys` |

All four are existing, already-live routes — nothing new was created, no URL was invented.

**Moved** (not deleted): the founding-reader offer banner and the free health-guide email bar. Both were `position: fixed` overlays sitting directly under the nav, meaning they visually competed with everything else for a first-time visitor's attention immediately. I converted both to normal in-page blocks (removed `position: fixed`, `top`, `z-index` — kept every word of copy, every link, and the email form's `action`/fields exactly as they were) and moved them to appear right after the new welcome/choices section, ahead of the Kingdom Study Tools and Ecosystem bands. They still work exactly as before; they're just no longer the first thing overlaying the screen.

**Removed**: one line, `*Aloha. You are in the right place.*`, from the end of the home page body copy (in both `content.py` and `website_content.json`) — because that exact phrase now opens the page instead of closing it. This is the only text removed. The "three pillars," "Start Here – FREE," and everything else in the body copy is untouched.

**Unchanged**: the hero (title, image), the Kingdom Study Tools band, the Ecosystem band, the entire body_md content (three pillars, personal story, free-resources callout), the footer signup form in `base.html`, and the top navigation.

## Final homepage order (top to bottom)

1. Header / nav (`base.html`, unchanged)
2. Hero (title + background image, unchanged)
3. **New:** welcome heading + two-sentence identity statement
4. **New:** "Where would you like to begin?" — 4 choice cards
5. Founding-reader offer banner (moved, same content)
6. Free Kingdom Health Guide email bar (moved, same content)
7. Kingdom Study Tools band (unchanged)
8. Ecosystem band (unchanged)
9. Main body: longer personal story, three pillars, "Start Here – FREE" (unchanged, minus the one relocated closing line)
10. Footer signup strip + copyright (`base.html`, unchanged)

## Navigation recommendation (Phase 4) — not implemented

The top nav currently has 11 flat items in one row (Home, Keaupuni Health, Keaupuni Wealth, Bible Truth, Music, Keaupuni Planners, Free Booklets, Ministry Support, Rotten Fencepost, Ecosystem, Study Tools) with no grouping. On mobile this collapses to a single 11-item scrolling list behind the hamburger icon.

I did not change this. Reordering or grouping it (e.g., moving less-common destinations like Music/Rotten Fencepost/Ministry Support under a secondary "More" dropdown, or reordering by likely visitor priority) would improve scannability, but it touches something that's currently live and working, and doing it well is a real design decision (what counts as "primary" vs "secondary," how a dropdown should look and behave on mobile) rather than a mechanical fix. Per your instruction, I'm documenting this as a recommendation for you to decide on rather than implementing it now.

One small, separate observation while I was in the nav code: the nav's "Free Booklets" link and the home page's own "Start Here – FREE" link both point to `/kingdom_keys`, not `/free_booklets` (a separate, similarly-named page that exists but isn't linked from the nav or the home page). That's pre-existing, not something I introduced or changed — flagging it only because you may want to know it's there.

## Testing (Phase 8)

**Baseline (before any homepage change):** `tests/test_security.py`, run in isolation — **26 passed, 0 failed.**

**After changes:** `tests/test_security.py` + new `tests/test_homepage.py` — **56 passed, 0 failed.**

The 17 new homepage tests check, against a real Flask test client (no network calls):
- `/` returns 200
- The welcome heading and "Where would you like to begin?" text are present
- Each of the 4 choice cards' title text is present, paired with the correct `href`
- Each of the 4 link targets (`/call_to_repentance`, `/aloha_wellness`, `/kingdom_wealth`, `/kingdom_keys`) independently returns 200 — i.e., every link in the new section actually resolves
- The welcome heading appears in the HTML *before* the founding-reader offer and before the Kingdom Study Tools/Ecosystem bands (verifies the reorder actually took effect, not just that the text exists somewhere)
- The founding-reader offer and free-guide email form are still present with their original link/action
- The "three pillars" content is still present (nothing was deleted)
- The phrase "Aloha. You are in the right place." appears **exactly once** on the rendered page (catches the duplicate-content bug I found and fixed)
- 12 other public pages (including `/product/prod_aloha_wellness`, `/ecosystem`, `/kingdom-study`) still return 200
- `/kahu` still requires login (302, not 200) — confirms the homepage work didn't touch auth

**Manual route checks**, against a locally running instance with no PayPal/admin env vars set (worst case): `/checkout/prod_aloha_wellness` → 503 (unchanged fail-safe behavior from the earlier security work, not a regression), `/kahu` → 302, `/download/pamphlet1` → 200, all 10 other content pages → 200, `/product/prod_aloha_wellness` → 200.

**HTML structure check:** parsed the actual rendered `/` response with Python's `html.parser` and walked the tag stack — 0 unclosed tags, 0 mismatched tags, in 23,405 characters of output.

**What I could not verify:** actual visual rendering in a browser. The Claude-in-Chrome browser extension is not connected in this environment (`tabs_context_mcp` returned "Browser extension is not connected"), so I have no screenshot and cannot confirm layout, spacing, or the mobile breakpoint by sight. I'm not claiming the visual result looks right — only that the HTML is well-formed, the tests pass, and the new grid section uses the exact same responsive CSS Grid technique (`grid-template-columns: repeat(auto-fit, minmax(..., 1fr))`) already used elsewhere on this same page for the product/gallery grids, which is the strongest evidence I have that it won't cause horizontal scrolling on narrow screens — but that's inference from consistent code, not an observed result. **I'd recommend you open the homepage yourself on desktop and phone before approving deployment.**

## Remaining risks

1. **Unverified visual layout** (above) — the biggest open item. Please look at it yourself before approving.
2. **The `website_content.json` / `content.py` disconnect** (see "mid-task discovery") — a real, separate issue that may mean `/kahu` content edits don't survive a restart. Not fixed here, flagged for your attention.
3. The new welcome section's card styling is close to, but not pixel-identical to, the existing Kingdom Study Tools/Ecosystem bands (I used a warm-brown/gold palette distinct from the existing gold and teal bands, so the three don't blur together visually) — a judgment call on my part, not something you specifically asked for or against.
4. I have not tested with a screen reader or automated accessibility scanner — only confirmed logical heading order (h2 → h3) and that every link is a real `<a href>` (keyboard-reachable by default, no `onclick`-only interactions).

## `git status`

```
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
	modified:   content.py
	modified:   templates/page.html
	modified:   website_content.json

Untracked files:
	tests/test_homepage.py
```

## Diff summary

```
 content.py           |  2 +-   (1 line: removed duplicate closing "Aloha" sentence)
 templates/page.html  | 44 ++++++++++++++++++++++++++++++++++----------
 website_content.json |  2 +-   (same 1-line removal, for consistency; not currently read live)
 3 files changed, 36 insertions(+), 12 deletions(-)
```

## Manual testing instructions for Kahu Phil

1. Pull this branch locally (or review the diff directly) — nothing is deployed yet.
2. Run `python app.py` (or `flask run`) and open `http://127.0.0.1:5000/`.
3. Confirm you see, in order: the hero image, then "Aloha. You are in the right place." with the two intro sentences, then "Where would you like to begin?" with 4 clickable cards, then the founding-reader offer banner, then the free health-guide bar, then Kingdom Study Tools, then Ecosystem, then the rest of the page as before.
4. Click each of the 4 new cards and confirm they land on the right page: Understand the Kingdom → Call to Repentance page, Strengthen Your Health → Aloha Wellness page, Practice Faithful Stewardship → Kingdom Wealth page, Start With Something Free → Kingdom Keys page.
5. Resize your browser window narrow (or open on your phone) and confirm the 4 cards stack into a single column without any horizontal scrollbar, and that the hamburger menu still opens/closes the nav normally.
6. Confirm the founding-reader "Claim Offer" link and the free-guide email form still work as they did before.
7. Confirm `/kahu` still asks for your password, and that checkout/downloads still work as before (these weren't touched, but worth a quick check).
8. If it all looks right, let me know and I'll commit — I will not push or deploy without your separate go-ahead on that, per your instructions.
