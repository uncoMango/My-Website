# blueprints/admin.py
# =========================================================
# Admin panel: view all pages, edit content.
# Access at /kahu
# =========================================================

import re
from flask import Blueprint, abort, redirect, render_template, request
from content import load_content, save_content, get_nav_items
from config import ORDER

admin_bp = Blueprint("admin", __name__)


def _youtube_to_embed(url):
    """Convert any YouTube share/watch URL to an embed URL."""
    url = url.strip()
    # youtu.be/ID
    m = re.search(r'youtu\.be/([A-Za-z0-9_-]{11})', url)
    if m:
        return f"https://www.youtube.com/embed/{m.group(1)}"
    # youtube.com/watch?v=ID
    m = re.search(r'[?&]v=([A-Za-z0-9_-]{11})', url)
    if m:
        return f"https://www.youtube.com/embed/{m.group(1)}"
    # already an embed URL — return as-is
    m = re.search(r'youtube\.com/embed/([A-Za-z0-9_-]{11})', url)
    if m:
        return url
    return url


@admin_bp.route("/kahu", methods=["GET", "POST"])
def admin_panel():
    data = load_content()
    if request.method == "POST":
        raw_url = request.form.get("funnel_youtube_url", "").strip()
        if raw_url:
            data["funnel_youtube_url"] = _youtube_to_embed(raw_url)
        elif "funnel_youtube_url" in data:
            del data["funnel_youtube_url"]
        save_content(data)
        return redirect("/kahu")
    pages = data.get("pages", {})
    return render_template(
        "admin/panel.html",
        pages=pages,
        funnel_youtube_url=data.get("funnel_youtube_url", "https://www.youtube.com/embed/O_-J8t0NHLc"),
    )


@admin_bp.route("/admin/edit/<page_id>", methods=["GET", "POST"])
def edit_page(page_id):
    data = load_content()
    pages = data.get("pages", {})

    if page_id not in pages:
        abort(404)

    if request.method == "POST":
        page = pages[page_id]

        page["title"] = request.form.get("title", "")
        page["hero_image"] = request.form.get("hero_image", "")
        page["body_md"] = request.form.get("body_md", "")

        # Optional URL fields — remove key if empty
        for field in ("direct_buy_url", "product_url", "gumroad_url", "podcast_embed"):
            value = request.form.get(field, "").strip()
            if value:
                page[field] = value
            elif field in page:
                del page[field]

        # Product images (one URL per line)
        product_images_raw = request.form.get("product_images", "").strip()
        page["product_images"] = (
            [line.strip() for line in product_images_raw.splitlines() if line.strip()]
            if product_images_raw
            else []
        )

        # Gallery images (one URL per line)
        gallery_raw = request.form.get("gallery_images", "").strip()
        if gallery_raw:
            page["gallery_images"] = [
                img.strip() for img in gallery_raw.splitlines() if img.strip()
            ]
        elif "gallery_images" in page:
            del page["gallery_images"]

        # Music/product links (format: Name|URL|Icon, one per line)
        links_raw = request.form.get("product_links", "").strip()
        if links_raw:
            links = []
            for line in links_raw.splitlines():
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        links.append({
                            "name": parts[0].strip(),
                            "url": parts[1].strip(),
                            "icon": parts[2].strip(),
                        })
            if links:
                page["product_links"] = links
        elif "product_links" in page:
            del page["product_links"]

        data["pages"] = pages
        save_content(data)
        return redirect("/kahu")

    page = pages[page_id]
    gallery_str = "\n".join(page.get("gallery_images", []))
    product_images_str = "\n".join(page.get("product_images", []))
    links_str = "\n".join(
        f"{link['name']}|{link['url']}|{link['icon']}"
        for link in page.get("product_links", [])
    )

    return render_template(
        "admin/edit_page.html",
        page=page,
        page_id=page_id,
        gallery_str=gallery_str,
        product_images_str=product_images_str,
        links_str=links_str,
    )
