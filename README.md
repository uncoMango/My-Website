# Ke Aupuni O Ke Akua - Website

## Project Structure

```
ke_aupuni/
├── app.py                      ← Start here. Wires everything together.
├── config.py                   ← ALL settings: passwords, API keys, URLs
├── content.py                  ← Reads/writes JSON data files
├── styles.py                   ← Shared CSS (kept for reference)
├── requirements.txt            ← Python packages needed
│
├── blueprints/                 ← Each file handles one area of the site
│   ├── pages.py                ← Public pages (home, aloha wellness, etc.)
│   ├── downloads.py            ← Free PDF download routes
│   ├── products.py             ← Digital product sales + admin
│   ├── payments.py             ← PayPal (active) + Stripe (ready to activate)
│   └── admin.py                ← Admin panel at /kahu
│
├── templates/                  ← HTML files (no more HTML inside Python!)
│   ├── base.html               ← Shared nav + footer used by all pages
│   ├── page.html               ← Any page from website_content.json
│   ├── myron_golden.html       ← Myron Golden affiliate page
│   ├── checkout.html           ← Payment page (PayPal + Stripe)
│   ├── payment_success.html    ← Thank you / download page
│   ├── product_page.html       ← Public product sales page
│   ├── partials/
│   │   └── styles.css          ← Shared CSS loaded inline
│   └── admin/
│       ├── panel.html          ← Admin dashboard at /kahu
│       ├── edit_page.html      ← Edit any page
│       ├── products_list.html  ← Manage digital products
│       └── product_edit.html   ← Edit a product
│
├── website_content.json        ← Your page content (DO NOT DELETE)
├── digital_products.json       ← Your products (DO NOT DELETE)
└── digital_products/           ← Uploaded product files folder
```

---

## Deploying to GitHub (one-time setup)

1. **Delete** the old `ke_aupuni_website.py` from your repo
2. **Upload all these new files**, keeping the folder structure exactly as shown above
3. **Keep** your existing `website_content.json`, `digital_products.json`, and all your PDF files
4. Push to GitHub — Render will redeploy automatically

---

## Activating Stripe (when ready)

1. Sign up at [stripe.com](https://stripe.com)
2. Go to Stripe Dashboard → Developers → API Keys
3. Open `config.py`
4. Paste your Publishable Key and Secret Key into the STRIPE fields
5. Change `STRIPE_ENABLED = False` to `STRIPE_ENABLED = True`
6. Uncomment the `# stripe` line in `requirements.txt`
7. Push to GitHub

The Stripe button will appear automatically on your checkout page.

---

## Making Changes

- **Change a password or API key?** → Edit `config.py`
- **Change how a page looks?** → Edit the template in `templates/`
- **Add a new page route?** → Edit `blueprints/pages.py`
- **Add a new PDF download?** → Edit `blueprints/downloads.py`
- **Change payment settings?** → Edit `blueprints/payments.py`

---

*Made with aloha for Kahu Phil Stephens, Molokaʻi*
