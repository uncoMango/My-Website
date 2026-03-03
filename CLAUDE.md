# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

### 2026-03-03
- **Dynamic YouTube embed on `/aloha-wellness` funnel** — `funnel_youtube_url` stored in `website_content.json` (top-level key). Admin can paste any YouTube URL format into the `/kahu` panel "Weekly YouTube Video" field to update the embed without code changes. `_youtube_to_embed()` in `admin.py` converts share/watch/embed URLs to embed format.
- **Fixed `edit_page` save** — now preserves all top-level JSON keys (was previously stripping unknown keys like `funnel_youtube_url`).

### 2026-02-26
- **Removed all hardcoded secrets from `config.py`** — admin password, PayPal credentials, and SMTP credentials now require environment variables with no fallback defaults. Stripe vars kept optional with empty defaults since Stripe is not yet active.
- **Audited `aloha_wellness_funnel.html`** — confirmed all CTA buttons already route to internal `/checkout/prod_aloha_wellness` (no external Amazon/Gumroad links present).
