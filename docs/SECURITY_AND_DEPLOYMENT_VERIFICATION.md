# Security and Deployment Verification

**Scope:** `D:\Keaupuni Website\My-Website-2026` — the confirmed clean, in-sync local checkout of `origin/main` (commit `fa592ff`), which is what Render's `ke-aupuni-website-2` service actually deploys. No commits, pushes, or deploys were made. All changes are unstaged in the working tree.

## How the correct repository was confirmed

An earlier pass of this audit worked in the wrong local repo (`D:\Keaupuni Website\My-Website`, a stale `development` branch, 195 commits behind `main` and never merged into it). That mistake was caught before any code was changed, by fingerprinting the actual live site (`robots.txt`, `sitemap.xml`, and nav items unique to newer commits all matched `origin/main` exactly, not `development`).

This repository was then verified directly:
- `git branch --show-current` → `main`
- `git status --short` → clean, no pre-existing uncommitted changes
- `git worktree list` → one worktree only, this directory
- `git fetch origin` + comparison → local `main` and `origin/main` are identical (`fa592ff`, 0 ahead / 0 behind)

This satisfied the "safe to use as-is" condition, so all Phase 2 work proceeded here.

---

## Confirmed findings

1. **`/kahu` and every content-write/product-upload route had no authentication.** `blueprints/admin.py` and `blueprints/products.py` defined `ADMIN_PASSWORD` in `config.py` but never referenced it anywhere in the route logic. Verified two ways: reading the code, and (in the earlier, since-superseded pass of this audit) fetching the live `/kahu` URL directly, which returned the full admin dashboard with no login prompt.
2. **Live PayPal credential values were hardcoded in plaintext in `ke_aupuni_website.py`** — four separate occurrences (`ADMIN_PASSWORD`, `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`, and a duplicate `PAYPAL_CLIENT_ID` embedded directly inside an HTML `<script>` string). This file is not the active entry point (`app.py` is, confirmed via `render.yaml`, `Procfile`, and `CLAUDE.md`), but `wsgi.py` still does `from ke_aupuni_website import app`, and the file is tracked in git regardless, so the exposure was real.
3. **`config.py` itself already had no hardcoded secrets** — `ADMIN_PASSWORD`, `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`, and the SMTP variables were already `os.environ.get(...)` with no fallback default, per this repo's own `CLAUDE.md` changelog (dated 2026-02-26). This was a false alarm carried over from auditing the wrong repo earlier — no fix was needed here.
4. **`website_content.json` is valid JSON** in this repo. The syntax error found earlier (a duplicated `"hero_image"` key) exists only in the stale `development` branch's copy of the file and does not affect this repo or production. No repair was needed; confirmed with Python's `json` module and with a dedicated test.
5. **Google Analytics is installed and working** — `templates/base.html` has a correct GA4 `gtag.js` snippet (measurement ID `G-V2NY3MEWKB`, which is a public client-side identifier, not a secret) on every page that extends the shared base template. This is also a false alarm carried over from the wrong repo — no analytics tag was added, per your instruction not to duplicate existing tracking.
6. **The PayPal checkout flow had no fail-safe for missing credentials.** If `PAYPAL_CLIENT_ID`/`PAYPAL_CLIENT_SECRET` were ever unset, `/checkout/<product_id>` would have rendered a checkout page with a broken PayPal button and no clear error, rather than failing safely.

## Fixed

All changes are unstaged in the working tree — nothing has been committed.

| File | Change |
|---|---|
| `auth.py` (new) | Shared login gate: `admin_configured()`, constant-time `check_password()` (via `secrets.compare_digest`), `require_admin` decorator. Returns `False`/denies by default if `ADMIN_PASSWORD` is unset — never falls open. |
| `config.py` | Added `FLASK_SECRET_KEY` (env-var only, no fallback default) to sign the session cookie. |
| `app.py` | Sets `app.secret_key` from `FLASK_SECRET_KEY` (or a random key at process start if unset, so a missing key degrades to "admins get logged out on restart," not "the site is wide open"). Hardened session cookie flags: `HTTPONLY`, `SAMESITE=Lax`, and `SECURE` (HTTPS-only) when running on Render. |
| `blueprints/admin.py` | Added `GET/POST /kahu/login` (rate-limited to 10/hour) and `POST /kahu/logout`. Applied `@require_admin` to `/kahu`, `/admin/delete-page/<page_id>`, and `/admin/edit/<page_id>`. Existing view logic is unchanged — the decorator only gates entry. |
| `blueprints/products.py` | Applied `@require_admin` to `/admin/products`, `/admin/products/add`, `/admin/products/edit/<product_id>`, `/admin/products/delete/<product_id>`. `/product/<id>` (public sales page) and `/download/product/<id>` were left open, since those are meant to be public. |
| `templates/admin/login.html` (new) | Plain login form, styled to match the existing admin panel. Shows a clear "not configured" state if `ADMIN_PASSWORD` is unset rather than a generic error. |
| `templates/admin/panel.html` | Added a "Log Out" button next to the existing admin actions. |
| `blueprints/payments.py` | `/checkout/<product_id>` now returns `503` with a clear message if PayPal credentials are unset, instead of silently rendering a broken checkout page. |
| `ke_aupuni_website.py` | All four hardcoded secret values replaced with `os.environ.get(...)` reads (matching `config.py`'s existing pattern). The one value that was baked directly into an HTML string (not a variable) was replaced with a placeholder token substituted at render time. This file is still unused dead code — it is not wired into any deployed route — but is no longer a plaintext credential leak. |
| `tests/test_security.py` (new) | 26 tests, see below. |

**What removing these values from the file does *not* do:** it does not rotate the PayPal credentials, and it does not remove them from git history — they remain readable in every prior commit that touched `ke_aupuni_website.py`, on GitHub, for anyone with read access to the repository.

## Tests

26 tests in `tests/test_security.py`, run against a local Flask test client (in-memory, no network calls):

- unauthenticated GET on `/kahu`, `/admin/products`, `/admin/edit/<id>` → redirected, not served
- unauthenticated POST on `/admin/edit/<id>`, `/admin/delete-page/<id>`, `/admin/products/delete/<id>`, `/admin/products/add` → rejected, **and** the real local `website_content.json`/`digital_products.json` are byte-for-byte unchanged before/after (verified by reading the files, not just checking the HTTP status)
- correct password → session established, `/kahu` returns 200 with admin content
- wrong password → rejected, session not established
- logout → session cleared, `/kahu` denied again
- `website_content.json` parses as valid JSON and contains a `home` page
- `ADMIN_PASSWORD` unset → `admin_configured()` is `False`, login POST returns `503` (not a silent bypass)
- `PAYPAL_CLIENT_ID`/`SECRET` unset → `/checkout/<id>` returns `503`; present → returns `200`
- 10 existing public pages (`/`, all 8 content pages, `/partner`, `/product/prod_aloha_wellness`) still return 200 after all the above changes

```
============================== 26 passed, 1 warning in 1.36s ==============================
```

(The one warning is Flask-Limiter's standard notice that it's using in-memory rate-limit storage — pre-existing, unrelated to this change, expected for a single-instance Hobby-tier deployment.)

## Local startup verification

Ran `app.py` locally with **no** `ADMIN_PASSWORD`, `PAYPAL_CLIENT_ID`, or `PAYPAL_CLIENT_SECRET` set (i.e. the worst case — nothing configured):

- `GET /` → `200` (public pages unaffected)
- `GET /kahu` → `302` (denied, not exposed)
- `GET /checkout/prod_aloha_wellness` → `503` (fails safely, not a broken PayPal button)
- Startup log printed only `GOOGLE_CREDENTIALS_JSON NOT SET at startup` (a boolean fact, pre-existing log line) — no secret value was printed anywhere in startup output or in these tests.

A `data/subscribers.json` file was created as a side effect of running the app locally (existing, unrelated `downloads.py` behavior — it initializes an empty subscriber list on startup if one doesn't exist). This was deleted after verification since it was a local artifact, not a deliverable.

## `git status` / diff summary

Nothing staged, committed, or pushed. Working tree only:

```
 M app.py                     |  +14/-1
 M blueprints/admin.py        |  +43/-1
 M blueprints/payments.py     |  +2
 M blueprints/products.py     |  +4
 M config.py                  |  +4
 M ke_aupuni_website.py       |  +9/-7
 M templates/admin/panel.html |  +1
?? auth.py
?? templates/admin/login.html
?? tests/test_security.py
```

---

## Items requiring Kahu Phil to act outside the code

1. **Set `FLASK_SECRET_KEY` in Render's Environment tab** (any long random string — e.g. generate one with `python -c "import secrets; print(secrets.token_hex(32))"`). Without it, admin sessions will still work but everyone gets logged out whenever Render restarts the service (a redeploy, a scale event, a crash restart).
2. **Rotate the PayPal Client ID/Secret in the PayPal developer dashboard.** These values were sitting in plaintext in a tracked file in git history (on `main`, not just the abandoned branch). Removing them from `ke_aupuni_website.py` in this change does not invalidate the old values or erase them from history — only PayPal-side rotation does that. After rotating, update `PAYPAL_CLIENT_ID`/`PAYPAL_CLIENT_SECRET` in Render's Environment tab to the new values.
3. **Rotate the admin password** (the old hardcoded value, `"Kingdom2024"`, is likewise exposed in git history) and set the new value as `ADMIN_PASSWORD` in Render's Environment tab.
4. **Confirm whether Render's `ke-aupuni-website-2` service has a persistent disk attached.** `render.yaml` doesn't request one. Content edited live through `/kahu` (page text, product uploads, subscriber list) is written to local JSON files/disk — if the filesystem is ephemeral, those edits may not survive a redeploy. This wasn't something I could verify from the repository; it needs a check in the Render dashboard.
5. **Confirm the actual git history exposure window** — if you want to know exactly which commits/dates the PayPal secret was exposed in, that requires `git log -p` review or GitHub's secret-scanning history, which is worth doing before/alongside rotation so you know if it needs reporting anywhere.

## Items still requiring live-server verification

- These fixes are unstaged in the local working tree only. **Nothing is live yet** — the actual `/kahu` on `keaupuniakeakua.faith` is still unauthenticated until this is committed, pushed, and deployed (a decision left to you, per your instruction not to commit/push/deploy automatically).
- Once deployed, confirm `/kahu` actually prompts for a password in production, and that logging in with the new `ADMIN_PASSWORD` works, before relying on it.
- Confirm `/checkout/<product_id>` still works end-to-end live (a real, low-value test purchase or PayPal sandbox pass) after this change, since the new 503 guard only activates when credentials are missing — it shouldn't change existing behavior when they're present, but this wasn't tested against real PayPal endpoints, only that the guard triggers/doesn't trigger correctly.
- Whether Render's disk is ephemeral (item 4 above) is not verifiable from code and needs a live check.
