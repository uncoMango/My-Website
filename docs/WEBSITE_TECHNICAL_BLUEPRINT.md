# WEBSITE TECHNICAL BLUEPRINT

This document describes the Ke Aupuni O Ke Akua website **as it actually exists today**, in this repository, on the `main` branch. It is not a description of an ideal or planned architecture. Anything not yet built is explicitly labeled **"Future Work."** If something isn't mentioned here, assume it doesn't exist in the codebase.

Repository: `github.com/uncoMango/My-Website` · Local path (this checkout): `D:\Keaupuni Website\My-Website-2026` · Branch: `main` · Deployed service: Render.com, `ke-aupuni-website-2` (Hobby/legacy tier).

Two unrelated sibling folders live alongside this project on disk (`Scripture App/`, `STEPBible-Data/`) — they are separate projects, not part of this website, and are not covered by this document.

---

## Guiding Principle

The Technical Blueprint documents the website as it actually exists today. It is descriptive, not prescriptive. Future enhancements should be recorded in the Future Work section until they are implemented and verified.

---

## 1. Architecture Overview

This is a **Flask** (Python) web application, structured as a set of **Blueprints** — Flask's mechanism for splitting routes into separate modules that all register onto one app.

**Real entry point:** `app.py`. It creates the Flask app, sets the session secret key and cookie security settings, initializes rate limiting, and registers five blueprints:

```
app.py
├── blueprints/pages.py      (public content pages, sitemap, robots.txt)
├── blueprints/downloads.py  (free PDF downloads, email signup)
├── blueprints/products.py   (digital product pages + admin product CRUD)
├── blueprints/payments.py   (PayPal + Stripe checkout)
└── blueprints/admin.py      (/kahu admin panel, login/logout)
```

Confirmed as the real entry point by three independent sources agreeing: `render.yaml` (`startCommand: gunicorn --bind 0.0.0.0:$PORT app:app`), `Procfile` (`web: gunicorn app:app`), and `CLAUDE.md`'s own architecture notes.

**A second, unused file exists:** `ke_aupuni_website.py` — a large single-file (monolithic) version of the whole site, roughly 3,100 lines, containing its own copies of routes, templates-as-strings, and page content. It is **not** the deployed application. It is still present in the repository and still imported by `wsgi.py` (`from ke_aupuni_website import app`), but `wsgi.py` is not what Render actually runs — `render.yaml` and `Procfile` both point directly at `app:app`. Because this file is still tracked in git and still technically importable, it was cleaned of hardcoded secrets in an earlier pass of work on this repo, but no other code in it should be considered live.

`vercel.json` also exists and is out of date — it still references the old monolith file and does not reflect the current blueprint structure. It is not currently used for deployment (Render is the live host).

---

## 2. Technology Stack

| Layer | What's actually used |
|---|---|
| Language | Python |
| Web framework | Flask |
| Templating | Jinja2 (Flask's built-in templating), server-rendered HTML |
| Content formatting | The `markdown` Python library converts page body text from Markdown to HTML at request time |
| CSS | One plain CSS file (`templates/partials/styles.css`), included inline into every page's `<style>` block via `{% include %}`. No CSS framework (no Bootstrap, Tailwind, etc.) |
| JavaScript | A small amount of vanilla JS inline in `base.html` — only for toggling the mobile nav menu open/closed. No JS framework, no build step, no bundler |
| Rate limiting | `flask-limiter` (`limiter.py`), applied to a handful of specific routes |
| Payments | PayPal REST API (live), called directly via Python's built-in `urllib.request` — no PayPal SDK library is installed server-side. Stripe's official `stripe` Python library is installed and code exists for it, but it is inactive unless explicitly turned on (see §7) |
| Email | Python's built-in `smtplib`, direct SMTP — no third-party email service/API |
| Spreadsheet integration | `gspread` + `google-auth`, optional, only runs if a service-account credential is present (see §8) |
| Web server (production) | `gunicorn` |
| Data storage | JSON files on local disk — **no database of any kind** |
| Testing | `pytest` (not listed in `requirements.txt` — see §11) |

Full contents of `requirements.txt`:
```
flask
markdown
werkzeug
gunicorn
gspread
google-auth
flask-limiter
stripe
```

---

## 3. Directory Structure (relevant to the live app)

```
app.py                  — real entry point
wsgi.py                 — imports the OLD monolith; not what's actually deployed
config.py               — all settings, all secrets read from environment variables
content.py               — reads/writes page + product JSON data (see §6 for an important caveat)
limiter.py               — flask-limiter instance, shared across blueprints
auth.py                  — admin login/session helpers, shared by admin.py and products.py
ke_aupuni_website.py     — old monolithic version of the site; not deployed
blueprints/
  pages.py               — public content pages, ecosystem page, SEO subpages, sitemap/robots
  downloads.py            — free PDF downloads, email capture, subscriber storage
  products.py             — public product pages + admin product management
  payments.py              — PayPal checkout/capture, Stripe (dormant by default)
  admin.py                — /kahu panel, login/logout, page editing
templates/                — Jinja2 templates (see §5)
templates/partials/styles.css — the site's one CSS file
website_content.json      — page content in JSON form (see §6 — currently NOT read by the live app)
digital_products.json     — the digital product catalog (this one IS actively read/written)
digital_products/         — uploaded product files land here
static/                   — images and other static assets
data/subscribers.json     — created at runtime by downloads.py; stores email signups (gitignored: no — see §12)
tests/                    — pytest test files
docs/                     — documentation, including this file
```

---

## 4. Full Route Inventory

Every route currently registered in the live application, grouped by blueprint. (44 total.)

**`pages.py`** — `/`, `/rotten-fencepost`, `/rotten-fencepost/success`, `/myron-golden`, `/partner`, `/kingdom-study`, `/aloha-wellness`, `/ecosystem`, `/<parent>/<slug>` (SEO sub-pages, e.g. `/wellness/why-diets-fail`), `/sitemap.xml`, `/robots.txt`, `/BingSiteAuth.xml`, `/<page_id>` (generic catch-all for any page stored in the content dictionary — see §6)

**`downloads.py`** — `/subscribe` (POST), `/thank-you`, `/download/aloha_wellness_freebie` (GET+POST), `/download/pamphlet1`–`/download/pamphlet4`, `/download/booklet1`–`/download/booklet6`, `/download/kingdom_is_here`, `/download/kingdom_wealth_booklet`, `/download/product/<product_id>`, `/static/covers/<filename>`

**`products.py`** — `/product/<product_id>` (public), `/download/product/<product_id>` (public — note this exists in both `products.py` and `downloads.py`, see §12), `/admin/products`, `/admin/products/add` (POST), `/admin/products/edit/<product_id>`, `/admin/products/delete/<product_id>` (POST)

**`payments.py`** — `/checkout/<product_id>`, `/paypal/success`, `/paypal/cancel`, `/stripe/create-session/<product_id>` (POST, dormant), `/stripe/success` (dormant), `/stripe/webhook` (POST, dormant)

**`admin.py`** — `/kahu/login` (GET+POST), `/kahu/logout` (POST), `/kahu` (GET+POST), `/admin/delete-page/<page_id>` (POST), `/admin/edit/<page_id>` (GET+POST)

**Templates that exist but are not currently referenced by any route:** `templates/myron_golden.html` (the live `/myron-golden` route renders `myron_golden_funnel.html` instead).

---

## 5. Page Rendering

Most public content pages share one template, `templates/page.html`, which extends the shared layout `templates/base.html`. The page's title, hero image, and body text (written in Markdown) are pulled from the content dictionary described in §6 and rendered into that shared template. A handful of pages have their own dedicated templates instead of using the generic one — `partner.html`, `kingdom_study.html`, `checkout.html`, `product_page.html`, `payment_success.html`, `thank_you.html`, `rotten_fencepost.html`, `rotten_fencepost_success.html`, `myron_golden_funnel.html`, `aloha_wellness_funnel.html`, and the `admin/` templates.

`base.html` contains: the `<head>` (meta description, canonical link, Google/Bing site-verification tags, Google Fonts, Google Analytics `gtag.js`, and JSON-LD structured data for the ministry and for Kahu Phil as a Person), the top navigation bar (hardcoded list of links, not generated from any data file), the footer (an email-signup form posting to `/subscribe`, plus a copyright line), and the mobile nav-toggle script.

The homepage (`/`) has several additional home-only sections hardcoded directly into `page.html`, controlled by `{% if current_page == 'home' %}` checks rather than being data-driven: a welcome/four-choice-cards section, a founding-reader offer banner, a free health-guide email bar, a "Kingdom Study Tools" promotional band, and an "Ecosystem" promotional band.

---

## 6. Content & Data Storage — no database

There is no database. All content and product data live in JSON files read and written directly from disk.

**Important, verified fact about page content:** `config.py` defines `DATA_FILE = BASE / "website_content.json"`, and `content.py` contains `save_content()`, which does write to that file. However, `content.py`'s `load_content()` function currently does **not** read that file — it is hardcoded to `return DEFAULT_PAGES`, a Python dictionary literal defined directly inside `content.py`. This means:

- The actual page content served to visitors today comes from the `DEFAULT_PAGES` dictionary in `content.py`, not from `website_content.json`.
- `website_content.json` exists on disk, appears to be kept roughly in sync by hand, but has no effect on what the live site shows.
- Editing a page through `/kahu` calls `save_content()`, which writes to `website_content.json` — but since `load_content()` doesn't read it back, those edits do not appear to change what's served on the next page load within the same process in the way a JSON-backed system normally would. (Whether an edit persists at all, and for how long, depends on Python's normal in-memory object mutation behavior within a single running process — this has not been verified against the live server, and is flagged here as a fact about the code, not a claim about live behavior.)

This is documented as a factual observation about the current code, not something this document recommends fixing — any decision about whether or how to address it belongs to a separate, deliberate piece of work.

**Digital products** (`digital_products.json`) work differently and normally: `load_digital_products()` and `save_digital_products()` in `content.py` both actually read and write this file, and the admin product-management pages (`/admin/products/*`) function as expected against it.

**Free PDF downloads** are static files, not content-managed — each is a specific file on disk, served directly by a dedicated route (see §4).

**Uploaded product files** land in the `digital_products/` folder when added through `/admin/products/add`.

**Email subscribers** are stored in `data/subscribers.json`, created automatically the first time the app starts if it doesn't already exist.

---

## 7. Payments

**PayPal is the live, active payment method.** `blueprints/payments.py` calls PayPal's REST API directly using `PAYPAL_CLIENT_ID` / `PAYPAL_CLIENT_SECRET` (read from environment variables, no hardcoded fallback — see §10). The checkout page (`/checkout/<product_id>`) embeds PayPal's JS SDK client-side; the backend exchanges the client ID/secret for an access token, retrieves order/payer details after approval, updates the product's sale count in `digital_products.json`, and optionally sends a sale-notification email.

If `PAYPAL_CLIENT_ID` or `PAYPAL_CLIENT_SECRET` is missing at request time, `/checkout/<product_id>` returns an HTTP 503 with a clear configuration-error message rather than rendering a broken checkout page — this fail-safe behavior was added deliberately in an earlier pass of work on this repo.

**Stripe exists in code but is dormant by default.** The `stripe` library is installed, and `blueprints/payments.py` contains full routes for creating a Stripe Checkout session, handling success, and handling webhooks. All three routes immediately `abort(404)` unless `STRIPE_ENABLED` is explicitly set to `"true"` in the environment — which it is not, by default. This is not "Future Work" in the sense of code that doesn't exist yet; it is written and present, but switched off.

---

## 8. Email Capture & Notifications

Two routes collect email addresses: `/subscribe` (the footer signup form on every page) and `/download/aloha_wellness_freebie` (a dedicated free-guide funnel). Both:
- Run a lightweight honeypot/User-Agent check to filter obvious bots.
- Validate the email address with a hand-written check in `downloads.py` (not a third-party validation library).
- Save the subscriber to `data/subscribers.json`.
- Optionally append a row to a Google Sheet, **only if** a `GOOGLE_CREDENTIALS_JSON` environment variable is set (via `gspread`); otherwise this step is silently skipped and logged.
- Optionally send an admin notification email and a subscriber welcome email over SMTP, **only if** `SMTP_HOST`/`SMTP_USER`/`SMTP_PASS` are all set; otherwise skipped and logged.
- Schedule two follow-up emails (day 3 and day 7) using Python's `threading.Timer`. **This is an in-process timer, not a persistent job queue** — if the server restarts or redeploys before a scheduled timer fires, that follow-up email is lost and will not be resent. This is a real, current limitation of how follow-up emails work today.

---

## 9. Analytics

Google Analytics (GA4, `gtag.js`) is installed directly in `templates/base.html`, on every page that extends the shared layout, using a hardcoded measurement ID (`G-V2NY3MEWKB` — this is a public, client-side identifier, not a secret). This was verified present in the actual template code and confirmed live on the production site. No other analytics or tag-manager tooling is present in the codebase.

---

## 10. Authentication & Admin

The `/kahu` admin panel and every content-editing/product-management route require a logged-in session. This is implemented in `auth.py`:

- `ADMIN_PASSWORD` is read from an environment variable with no hardcoded fallback. If it is unset or empty, `admin_configured()` returns false and login is refused outright (not silently allowed).
- Password comparison uses `secrets.compare_digest` (constant-time comparison).
- A successful login sets a signed session cookie (`session[SESSION_KEY] = True`); the `require_admin` decorator checks this on every protected route and redirects to `/kahu/login` if it isn't present.
- The session cookie is signed using `app.secret_key`, set from a `FLASK_SECRET_KEY` environment variable if present. If that variable is not set, the app falls back to a random key generated once at process startup — sessions still work, but every admin gets logged out whenever the process restarts (a redeploy, a crash, a scale event). This is a known, accepted trade-off, not a bug: it fails toward "admins get logged out" rather than toward "the site becomes insecure."
- The login route is rate-limited (10 attempts per hour).
- `/kahu/login` also renders a "not configured" message instead of a working form if `ADMIN_PASSWORD` isn't set, rather than pretending login is available.

Protected routes: `/kahu`, `/admin/edit/<page_id>`, `/admin/delete-page/<page_id>`, `/admin/products`, `/admin/products/add`, `/admin/products/edit/<product_id>`, `/admin/products/delete/<product_id>`.

This authentication system did not exist in an earlier version of this codebase — these routes were previously reachable by anyone with no login at all. Adding this authentication was a deliberate, separate piece of work completed before this document was written.

---

## 11. Testing

Two test files exist under `tests/`, run with `pytest` against Flask's built-in test client (no live network calls, no real PayPal/SMTP/Google Sheets calls are made during tests):

- `tests/test_security.py` — 26 tests covering admin authentication (unauthenticated access denied, correct/incorrect login, logout, unauthorized writes rejected and verified not to touch real content files), JSON validity of `website_content.json`, missing-secret fail-safe behavior (both for admin login and PayPal checkout), and that public pages still load.
- `tests/test_homepage.py` — 17 tests covering the homepage welcome section: presence and correct link targets for all four visitor-choice cards, correct ordering relative to the pre-existing promotional bands, confirmation that existing content (three pillars, founding-reader offer, free-guide form) was not deleted, and that other public/admin routes were unaffected.

Total: **56 tests, currently passing.**

`pytest` is **not listed in `requirements.txt`** — it was installed separately into an isolated virtual environment to run these tests, and is not part of what gets installed on the production server. There is **no continuous integration configured** — no `.github/workflows` directory or equivalent exists in this repository. Tests are currently run manually, by a developer, before changes are pushed.

---

## 12. Known Inconsistencies (documented, not fixed here)

These are facts about the current code, noted so future developers aren't confused by them. None of these were altered as part of writing this document.

- **`website_content.json` is not read by the live app** (§6) — the most significant of these.
- **`config.py` defines `EMAILS_FILE`** (`email_subscribers.json`) and it is imported into `downloads.py`, but the code actually uses a different path, `SUBSCRIBERS_FILE` (`data/subscribers.json`), for all subscriber storage. `EMAILS_FILE` appears to be unused.
- **`/download/product/<product_id>` is defined in both `products.py` and `downloads.py`**, with slightly different implementations (the `products.py` version increments a download counter and saves it back to `digital_products.json`; the `downloads.py` version does not track downloads at all). Both routes register successfully — Werkzeug allows duplicate URL rules under different endpoint names — but only one is ever reached. Verified directly against the app's URL map: because `downloads_bp` is registered before `products_bp` in `app.py`, **`downloads.download_product` is the one that actually runs**, and `products.download_product` (the version that tracks download counts) is unreachable dead code.
- **`.gitignore` excludes `email_subscribers.json` but not `data/subscribers.json`** — the file that's actually used for subscriber storage today is not excluded from version control by name, though the whole `data/` directory has not been committed as of this writing.
- **`templates/myron_golden.html` is an orphaned template** — not referenced by any current route.
- **`ke_aupuni_website.py` and `wsgi.py` do not reflect the live application** and could mislead a future developer into thinking they're the entry point (§1).
- **`vercel.json` is stale** and references the old monolith file.

---

## 13. Deployment

- **Host:** Render.com, service `ke-aupuni-website-2` (Hobby/legacy tier).
- **Build command:** `pip install -r requirements.txt` (from `render.yaml`).
- **Start command:** `gunicorn --bind 0.0.0.0:$PORT app:app` (from `render.yaml`).
- **`Procfile`** provides the same start command in Heroku's format, as a fallback/alternative host option — not currently the live host.
- **Persistent disk:** `render.yaml` does not request a Render persistent disk. Whether the live service has one attached some other way (configured directly in the Render dashboard rather than in this file) has not been verified from the code — this matters because it determines whether files written at runtime (subscriber list, admin content edits, uploaded product files) survive a redeploy or restart. **This needs to be checked directly in the Render dashboard; it cannot be determined from this repository.**
- **Deployment trigger:** pushing to `main` on GitHub. There is no separate staging environment or preview-deploy step configured in this repository.
- **No CI:** as noted in §11, nothing runs tests automatically before or after a deploy. A push to `main` deploys directly.

---

## 14. Environment Variables

Read from the environment, with no hardcoded fallback (the app will not silently substitute a working-but-insecure default for these):

| Variable | Used for |
|---|---|
| `ADMIN_PASSWORD` | `/kahu` login |
| `FLASK_SECRET_KEY` | Signs the admin session cookie |
| `PAYPAL_CLIENT_ID` | PayPal checkout |
| `PAYPAL_CLIENT_SECRET` | PayPal checkout |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` | Sale/subscriber notification and welcome/follow-up emails |

Optional, with safe empty/disabled defaults if unset:

| Variable | Used for |
|---|---|
| `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | Stripe checkout (only relevant if `STRIPE_ENABLED` is also set) |
| `STRIPE_ENABLED` | Turns on the (otherwise dormant) Stripe routes |
| `GOOGLE_CREDENTIALS_JSON` | Optional Google Sheets logging of new subscribers |
| `PORT` | Set automatically by Render; used for local `python app.py` runs too, defaulting to `5000` |

---

## 15. Maintenance & Backups

There is currently no documented or automated backup process for `digital_products.json`, `data/subscribers.json`, or uploaded files in `digital_products/` beyond whatever Render's own infrastructure provides. No backup script, export job, or scheduled task exists in this repository.

---

## Future Work

Items below do not exist in the codebase today. They are listed here only because they were mentioned or implied elsewhere as things that may be wanted later — nothing in this section should be read as already built.

- **Fixing or intentionally resolving the `website_content.json` / `content.py` disconnect** (§6), so that admin content edits persist in a well-understood, durable way.
- **A persistent, durable follow-up email system** to replace the current in-process `threading.Timer` approach (§8), which does not survive a restart.
- **Continuous integration** to run the existing test suite automatically on push (§11).
- **A documented, automated backup process** for the JSON data files and uploaded product files (§15).
- **Activating Stripe** as a second live payment option (the code exists and is dormant — see §7 — but turning it on, testing it, and deciding whether to actually offer it to visitors has not been done).
- **Verifying and, if needed, provisioning a persistent disk** on the Render service (§13).
