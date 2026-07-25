# schema.py
# =========================================================
# Centralized Schema.org / JSON-LD builders (Work Order 007).
#
# Every function here returns a plain dict; templates render it with the
# `tojson` filter (Flask/Jinja's built-in, script-safe JSON serializer) so
# the resulting JSON is always syntactically valid regardless of which
# optional fields are present -- no hand-assembled JSON text with
# conditional commas.
#
# Nothing in this file invents data. Every value a caller passes in must
# already exist in the site's real content (page titles/descriptions,
# the digital product catalog, hero images, the site's own logo/YouTube
# link). No dates, ratings, reviews, addresses, or identifiers are
# fabricated -- callers simply don't pass fields that don't exist, and the
# builders below omit them rather than emit empty placeholders.
# =========================================================

SITE_URL = "https://keaupuniakeakua.faith"
ORG_ID = SITE_URL + "/#organization"
PERSON_ID = SITE_URL + "/#person"
WEBSITE_ID = SITE_URL + "/#website"


def org_ref():
    return {"@id": ORG_ID}


def person_ref():
    return {"@id": PERSON_ID}


def website_ref():
    return {"@id": WEBSITE_ID}


def build_webpage_schema(name, description, url, image_url=None, page_type="WebPage"):
    """WebPage (or a more specific subtype like CollectionPage) for a
    standard content page. page_type must be a page-level schema.org type
    -- callers decide (e.g. "CollectionPage" for /ecosystem and /products)
    since only the caller knows whether the page genuinely meets that
    type's definition."""
    schema = {
        "@context": "https://schema.org",
        "@type": page_type,
        "name": name,
        "url": url,
        "isPartOf": website_ref(),
        "publisher": org_ref(),
    }
    if description:
        schema["description"] = description
    if image_url:
        schema["primaryImageOfPage"] = {"@type": "ImageObject", "url": image_url}
    return schema


def build_article_schema(headline, description, url, image_url=None):
    """Article for the 18 SEO wellness/kingdom/wealth/scripture-tools pages.
    Deliberately omits datePublished/dateModified -- no reliable dates
    exist anywhere in this site's content or data model, and the work
    order explicitly prohibits inventing them."""
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": headline,
        "author": person_ref(),
        "publisher": org_ref(),
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "url": url,
    }
    if description:
        schema["description"] = description
    if image_url:
        schema["image"] = image_url
    return schema


def build_breadcrumb_schema(items):
    """items: ordered list of (name, url) tuples starting from Home. Every
    entry must be a real, navigable page -- callers should not invent
    intermediate category levels that don't correspond to an actual page."""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": url}
            for i, (name, url) in enumerate(items)
        ],
    }


def build_product_schema(product, url, image_url=None):
    """Product + Offer for an individual product page, sourced entirely
    from the real digital_products.json catalog entry passed in. No
    ratings, reviews, SKU/GTIN/ISBN, or shipping claims are added --
    none of that data exists in the catalog. Availability reflects the
    product's actual `active` flag."""
    availability = (
        "https://schema.org/InStock"
        if product.get("active", True)
        else "https://schema.org/OutOfStock"
    )
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.get("name"),
        "url": url,
        "brand": org_ref(),
        "offers": {
            "@type": "Offer",
            "url": url,
            "priceCurrency": "USD",
            "price": "%.2f" % float(product.get("price") or 0),
            "availability": availability,
        },
    }
    if product.get("description"):
        schema["description"] = product["description"]
    if image_url:
        schema["image"] = image_url
    return schema


def build_collection_itemlist_schema(name, description, url, items):
    """CollectionPage with a lightweight ItemList (name/url per entry only
    -- no price/image/description duplicated here, since that would be
    Product schema on a listing page, which the work order says not to do
    unless justified). items: list of (name, url) tuples."""
    schema = build_webpage_schema(name, description, url, page_type="CollectionPage")
    schema["mainEntity"] = {
        "@type": "ItemList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": item_name,
                "url": item_url,
            }
            for i, (item_name, item_url) in enumerate(items)
        ],
    }
    return schema
