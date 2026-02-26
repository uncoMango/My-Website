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
- `config.py` — Centralized settings (passwords, API keys, page nav order, paths)
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
