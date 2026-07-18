# WEBSITE OPERATIONS MANUAL

This is the plain-English operating guide for Kahu Phil and any future maintainer of this website. It is based on the verified, current state of the repository, and on `docs/WEBSITE_TECHNICAL_BLUEPRINT.md`. It does not describe an ideal system — only what is actually here today. Anything unverified or not yet built is labeled clearly.

## Purpose

This manual's priorities, in order:

1. Protect the live website.
2. Avoid losing content, subscriber data, or sales records.
3. Preserve working checkout and downloads.
4. Make changes safely.
5. Provide simple recovery steps when something goes wrong.

Nothing in this manual should ever be worth risking the live site over. When in doubt, stop and check rather than push forward.

---

## Website Location and Deployment

| Item | Value |
|---|---|
| Local repository path (this checkout) | `D:\Keaupuni Website\My-Website-2026` |
| Correct Git branch | `main` |
| Real application entry point | `app.py` (confirmed by `render.yaml`, `Procfile`, and `CLAUDE.md` all agreeing — see Technical Blueprint §1) |
| GitHub repository | `github.com/uncoMango/My-Website` |
| Deployment method | Render.com, service `ke-aupuni-website-2` (Hobby/legacy tier), deploys automatically from pushes to `main` |
| Live domain | `keaupuniakeakua.faith` |

No secret values (passwords, API keys, tokens) are recorded in this document, or in any documentation file. Secrets live only in Render's environment variable settings.

**A note on `ke_aupuni_website.py` and `wsgi.py`:** these files exist in the repository but are not what's actually deployed (see Technical Blueprint §1). Do not assume they reflect the live site.

---

## Before Any Work

1. Open the correct repository — `D:\Keaupuni Website\My-Website-2026`. (This repository has been confused with a different, stale checkout in the past. Always confirm the path.)
2. Confirm the branch — run `git branch --show-current` and make sure it says `main`.
3. Run `git status` and read the output.
4. Identify any existing uncommitted work before touching anything. If something unexpected is there, stop and figure out what it is before proceeding — do not discard it.
5. Read the relevant blueprint document(s) for the kind of work being done — the Technical Blueprint for code changes, the Visitor Blueprint and Content Guide for anything touching what visitors see or read.
6. Do not modify files unrelated to the task at hand.
7. Run the existing test suite and record the result before making any change (see Testing, below).

---

## Working With Claude Code

A safe standard workflow for any change made with Claude Code's help:

1. Explain the goal clearly.
2. Require inspection of the relevant code before any editing begins.
3. Keep the scope of the change limited to what was actually asked for.
4. Require a baseline test run before changes are made.
5. Require a final test run after changes are made.
6. Require a plain diff summary of exactly what changed.
7. When the change affects anything visual, review it locally in a browser before approving.
8. Commit only after explicit approval.
9. Push only after separate, explicit approval — commit and push/deploy are not the same approval.
10. Verify the live deployment actually worked, once it's out.

Claude must not create a new git branch or a new git worktree unless there is a genuine, explained reason it's required — not as a default or a convenience.

---

## Local Review

The verified, documented way to run this website locally is `python app.py` (also documented in `CLAUDE.md`; `flask run` is mentioned there as an alternative but was not the method actually used or verified in this session).

Running `python app.py` directly starts the app with Flask's debug/auto-reload mode on (this is written into `app.py` itself — `debug=True`). That's normally fine for local editing, but it means the process can spawn a second, reloader-managed child process — worth knowing if the server seems to keep running after you thought you stopped it.

- **Local browser address:** `http://127.0.0.1:5000/` by default (`python app.py` listens on the `PORT` environment variable if set, defaulting to `5000`). During this session's testing, a different port (`5099`) was sometimes used specifically to avoid clashing with anything already running on `5000` — either works, as long as you open the address that matches what the server actually printed when it started.
- **How to stop it:** if you started it in a normal terminal window, pressing `Ctrl+C` in that window stops it. If it was started in the background (as Claude Code did during this session's reviews), stopping it means finding and ending the process bound to that port — during this session that was done directly through Windows (via PowerShell's `Get-NetTCPConnection` / `Stop-Process`), not through the application itself.
- **Local review never touches the live website.** It runs entirely on your own machine, against your own local copy of the code and local data files. It does not read from or write to Render, GitHub, or `keaupuniakeakua.faith` in any way.

---

## Testing

- **Test command:** `pytest tests/` (run from the repository root).
- **What the tests cover, as of this writing:** 56 tests across two files — `tests/test_security.py` (26 tests: admin login/logout, unauthorized access and writes being rejected, JSON validity, missing-secret fail-safe behavior, public pages loading) and `tests/test_homepage.py` (17 tests: the homepage welcome section's content, link targets, and ordering, plus confirmation that other routes weren't affected).
- **Current limitations:** `pytest` is not listed in `requirements.txt` — it must be installed separately (into a virtual environment is recommended) to run these tests; it is not part of what Render installs on deploy. There is no automated test runner (no CI) — tests only run when a person runs them by hand.
- **Always record both a baseline result (before changes) and a final result (after changes)** when making any code change, so a regression can be traced to the specific change that caused it.

**Manual checks** — things the automated tests do not fully replace, and that should be checked by a human, especially after any change that touches these areas:
- Homepage loads and looks right.
- `/kahu` requires login (does not open directly).
- Admin login works with the real password, then logs out cleanly.
- Checkout actually completes (or at minimum, loads the PayPal button correctly) for a real product.
- A free download actually downloads.
- Email signup actually stores a subscriber (or at minimum submits without error).
- Navigation links all go where they say they go.
- The site looks correct on a phone-width screen, not just desktop.

Do not assume the automated test suite covers anything not explicitly listed above — it does not test payments against real PayPal, does not send real emails, and does not check visual appearance at all.

---

## Commit and Push Workflow

Plain-language versions of the commands used:

- `git status` — shows what's changed and what's untracked. Always look at this before doing anything else.
- `git diff <file>` — shows the exact line-by-line changes in a file, so you can read exactly what would be committed.
- `git add <file>` — stages a specific file to be included in the next commit. Prefer naming files explicitly over adding everything at once, so nothing unexpected gets swept in.
- `git commit -m "..."` — records the staged changes as a new commit, with a message explaining what changed and why.
- `git push origin main` — sends the commit up to GitHub. **This is the step that actually triggers Render to deploy**, since Render is set to deploy automatically from pushes to `main` (see Technical Blueprint §13). There is no separate "deploy" button or step in this setup — pushing to `main` *is* deploying.

Because push and deploy are the same action here, never push to `main` casually. Commit can be a checkpoint you're not fully sure about yet; push cannot.

---

## Post-Deployment Verification

After any push to `main`, check:

- [ ] The Render deployment actually succeeded (checked in the Render dashboard — this cannot be confirmed from the repository or from this manual).
- [ ] The homepage opens.
- [ ] Navigation works.
- [ ] `/kahu` requires login (not open to anyone).
- [ ] Admin login actually works.
- [ ] PayPal checkout works.
- [ ] Downloads work.
- [ ] Email capture works.
- [ ] Google Analytics is still present (view page source, look for `gtag`).
- [ ] No visual damage is evident on desktop or mobile.

---

## Content Updates — Important: Content Persistence Risk

This is the single most important operational fact documented in this manual.

As verified and documented in the Technical Blueprint (§6): **`content.py` currently provides the live page content, not `website_content.json`.** The function that loads page content (`load_content()`) is hardwired to return a fixed set of content written directly into `content.py`, and does not read `website_content.json` at all — even though a separate function does write to that file.

**In plain language:** editing a page through `/kahu` may appear to work in the moment, but there is a real, documented risk that those edits do not survive a server restart or a new deployment, because the content the site actually shows comes from a file that isn't updated by those edits. This has not been confirmed against the live server one way or the other — it is a fact about the code, flagged here so it can be tested and taken seriously, not something this manual claims to have proven happens live.

**Do not fix this as a side effect of other work.** This is a real, separate issue that deserves its own deliberate, tested fix — not a quick patch made in passing. Until it is fixed and verified, treat any content edit made through `/kahu` as *not guaranteed to survive a redeploy*, and correspondingly consider making significant content changes directly in `content.py` (as a proper code change, tested and committed) rather than relying on the admin panel for anything you can't afford to lose.

---

## Payments and Secrets

- Never place secret values (passwords, API keys, tokens) in any documentation file, commit message, or code comment.
- Use environment variables for every secret — this is already how `config.py` is written for `ADMIN_PASSWORD`, `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`, `FLASK_SECRET_KEY`, and the SMTP credentials (see Technical Blueprint §14). Keep it that way — never hardcode a secret value into the code as a "temporary" fix.
- If a credential is ever exposed (accidentally committed, shared, or otherwise compromised), rotate it — generate a new value with the provider (PayPal, email provider, etc.) and update it in Render's environment. Removing an exposed value from a file does not undo the exposure; the old value must be treated as compromised and replaced.
- Test checkout after any change that touches payment code, even a small one.
- Never edit payment logic casually. Payment code should get the same care as anything that handles real money, because it does.

**Verified in the Technical Blueprint:** PayPal is the live, active payment method. Stripe is present in the code but dormant — it is switched off by default and only activates if `STRIPE_ENABLED` is explicitly turned on in the environment (Technical Blueprint §7).

---

## Admin Access

- `/kahu` requires a login. The password is set as the `ADMIN_PASSWORD` environment variable in Render — it is not stored anywhere in this repository or its documentation.
- **To test it:** open `/kahu` while logged out and confirm you're asked for a password, not shown the panel directly. Log in with the real password and confirm you reach the panel.
- **Password safety:** treat the admin password like any other sensitive credential — don't share it over insecure channels, and rotate it if you suspect it's been seen by anyone who shouldn't have it.
- **Logout:** a "Log Out" option exists in the admin panel and clears the login session.
- **If login fails unexpectedly:** first confirm the password is actually correct. If it is and login still fails, the most likely cause (per the Technical Blueprint) is that `ADMIN_PASSWORD` isn't set correctly in Render's environment — login is designed to refuse access outright rather than fail open, so a misconfiguration shows up as "login doesn't work," not as a security gap.

---

## Downloads

- **To verify a product download**, use the actual "download" link or button for that product on the live site and confirm a real file comes down, rather than just checking that the button exists.
- **The duplicate route finding** (documented in Technical Blueprint §12): `/download/product/<product_id>` is defined twice, once in `products.py` and once in `downloads.py`. Only one of them ever actually runs — the one in `downloads.py`, because that blueprint is registered first in `app.py`. The other copy, in `products.py`, is dead code that never executes.
- **Do not remove the dead route without focused, dedicated testing.** Even though it doesn't currently run, removing code that looks unused always carries some risk of an assumption being wrong — this should be its own small, tested piece of work, not something done in passing while working on something else.

---

## Email Subscribers

Subscribers are stored in `data/subscribers.json`, created automatically the first time the app runs if the file doesn't already exist (Technical Blueprint §6, §8).

**A known mismatch, noted but not changed:** `config.py` defines a separate path, `EMAILS_FILE` (pointing at `email_subscribers.json`), which is imported into `downloads.py` but does not actually appear to be used anywhere — the real subscriber storage is `SUBSCRIBERS_FILE` (`data/subscribers.json`). Don't be misled by the existence of `EMAILS_FILE` into thinking subscriber data lives there; it doesn't, as far as has been verified.

---

## Backups

### What Exists Now

No backup script, export job, or scheduled task exists anywhere in this repository. Whatever backup protection exists today is entirely whatever Render's own infrastructure provides by default for the service — which has not been independently verified as part of this documentation effort.

### What Is Missing

- No formal, documented backup process for `digital_products.json`, `data/subscribers.json`, or files uploaded into `digital_products/`.
- No confirmation of whether the Render service has a persistent disk attached (see Technical Blueprint §13) — this matters directly for backups, because if the disk is not persistent, files written at runtime could be lost on a redeploy or restart regardless of any backup plan.

### Minimum Manual Backup Procedure

Until an automated system exists, a simple manual approach using only what's already verified to be here:

1. Periodically download a copy of `digital_products.json` and `data/subscribers.json` from the live server (via whatever file access Render provides — this has not been set up or tested as part of this documentation) and store the copies somewhere safe, outside of Render.
2. Before any deployment that could plausibly affect these files, take a fresh copy first.
3. Keep dated copies rather than overwriting the same backup file each time, so a mistake can be traced back to a specific point.

This is a starting point, not a real backup system — it depends on someone remembering to do it. A proper automated backup process is listed under Future Operations Improvements below.

---

## Troubleshooting

**Render deployment failure**
- *Likely cause:* a code error introduced by the last push, or a missing dependency in `requirements.txt`.
- *First safe check:* look at the build/deploy logs in the Render dashboard.
- *What not to do:* don't push another "fix" blindly without reading the actual error first.
- *When to stop and ask for help:* if the error isn't about a specific, obvious line of code you just changed.

**Website opens with an error**
- *Likely cause:* an unhandled exception in a route, or a missing environment variable a route depends on.
- *First safe check:* check Render's runtime logs for the actual error message.
- *What not to do:* don't restart the service repeatedly hoping it resolves itself without knowing why it broke.
- *When to stop and ask for help:* if the error message doesn't clearly point to something recent.

**`/kahu` login fails**
- *Likely cause:* wrong password, or `ADMIN_PASSWORD` not set/misconfigured in Render's environment.
- *First safe check:* confirm the password is correct; confirm `ADMIN_PASSWORD` is actually set in Render.
- *What not to do:* don't add a hardcoded password into the code as a workaround.
- *When to stop and ask for help:* if the environment variable is confirmed set correctly and login still fails.

**Checkout fails**
- *Likely cause:* `PAYPAL_CLIENT_ID` / `PAYPAL_CLIENT_SECRET` missing or incorrect in Render's environment (the checkout page is designed to fail with a clear 503 message in this case, rather than silently breaking).
- *First safe check:* confirm both PayPal environment variables are set correctly in Render.
- *What not to do:* don't touch payment code as a first response — check configuration first.
- *When to stop and ask for help:* if the credentials are confirmed correct and checkout still fails — this may mean something has changed on PayPal's side.

**Download fails**
- *Likely cause:* the underlying file is missing from the server, or the file path stored for that product is wrong.
- *First safe check:* confirm the file actually exists at the expected location.
- *What not to do:* don't assume it's a code problem before confirming the file itself is present.
- *When to stop and ask for help:* if the file exists and the download still fails.

**Content changes disappear**
- *Likely cause:* the Content Persistence Risk described above — an edit made through `/kahu` may not have survived a restart or redeploy.
- *First safe check:* re-check whether the edit is present in `content.py` itself, not just in `website_content.json`.
- *What not to do:* don't assume `/kahu` edits are permanent until the persistence issue is actually resolved and verified.
- *When to stop and ask for help:* this is a known, documented risk — if it happens, it confirms something worth prioritizing a real fix for, not something to keep working around indefinitely.

**Tests fail**
- *Likely cause:* a recent code change broke something the tests check for.
- *First safe check:* read the specific failing test's name and assertion — it should say plainly what it expected versus what happened.
- *What not to do:* don't skip or delete a failing test to make the suite pass.
- *When to stop and ask for help:* if the failure doesn't make sense relative to what was actually changed.

**Wrong repository or branch**
- *Likely cause:* working in a stale or duplicate local copy of the site instead of `D:\Keaupuni Website\My-Website-2026` on `main`.
- *First safe check:* run `pwd`, `git branch --show-current`, and `git log -1 --oneline`, and compare against the values recorded at the top of this manual.
- *What not to do:* don't assume any local folder is the right one without checking — this exact confusion has happened before during work on this site.
- *When to stop and ask for help:* if the branch or repository doesn't match what's documented here and it isn't immediately obvious why.

**Uncommitted changes already exist**
- *Likely cause:* work in progress from an earlier session that was never committed.
- *First safe check:* run `git status` and `git diff` to see exactly what's there before doing anything else.
- *What not to do:* never run a command that discards changes (like `git checkout .` or `git reset --hard`) without first understanding what would be lost.
- *When to stop and ask for help:* if it's unclear whether the existing changes are safe to keep, discard, or build on top of.

---

## Monthly Maintenance Checklist

- [ ] Open the live site and browse it as a visitor would.
- [ ] Test one checkout, if it can be done safely (e.g. a real small purchase, or whatever safe test method is available).
- [ ] Test one download.
- [ ] Test admin login.
- [ ] Review Render's logs for anything unusual.
- [ ] Review subscriber storage — confirm new signups are actually being recorded.
- [ ] Check for broken links, especially on frequently-linked pages.
- [ ] Confirm backups (per the manual procedure above, until an automated one exists).
- [ ] Review the unresolved items in the Technical Blueprint's Future Work section and this manual's Future Operations Improvements section, and decide if any should be prioritized.

---

## Emergency Rule

**If the live website is working and the cause of a problem is uncertain, do not make broad changes.**

Inspect first. Protect payments, downloads, subscriber data, and content above all else. A narrow, well-understood fix is always better than a broad change made under pressure while the cause is still unclear.

---

## Future Operations Improvements

Verified as missing, and listed here separately from anything already built:

- Continuous integration, to run the existing test suite automatically before or after a deploy.
- A real, automated backup process for the JSON data files and uploaded product files.
- Verification (and, if needed, provisioning) of a persistent disk on the Render service.
- A real fix for the `website_content.json` / `content.py` content-persistence issue described above.
- Cleanup of the duplicate `/download/product/<product_id>` route once it can be done with focused, dedicated testing.
- Cleanup of the unused `EMAILS_FILE` reference in `config.py`/`downloads.py`.

(These match the Future Work items already documented in `docs/WEBSITE_TECHNICAL_BLUEPRINT.md` — listed here again because they're directly relevant to safe day-to-day operations, not to duplicate ownership of tracking them.)

---

## Change History

**2026-07-17** — Initial version of this manual created, based on the verified current state of the repository and `docs/WEBSITE_TECHNICAL_BLUEPRINT.md`.

*Space reserved below for future revisions.*
