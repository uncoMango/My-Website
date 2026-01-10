@app.route("/kahu/edit/<page_id>", methods=["GET", "POST"])
def edit_page(page_id):
    data = load_content()
    pages = data.get("pages", data)
    
    if page_id not in pages:
        abort(404)
    
    if request.method == "POST":
        pages[page_id]["title"] = request.form.get("title", "")
        pages[page_id]["hero_image"] = request.form.get("hero_image", "")
        pages[page_id]["body_md"] = request.form.get("body_md", "")
        
        product_url = request.form.get("product_url", "").strip()
        if product_url:
            pages[page_id]["product_url"] = product_url
        elif "product_url" in pages[page_id]:
            del pages[page_id]["product_url"]
        
        gumroad_url = request.form.get("gumroad_url", "").strip()
        if gumroad_url:
            pages[page_id]["gumroad_url"] = gumroad_url
        elif "gumroad_url" in pages[page_id]:
            del pages[page_id]["gumroad_url"]
        
        podcast_embed = request.form.get("podcast_embed", "").strip()
        if podcast_embed:
            pages[page_id]["podcast_embed"] = podcast_embed
        elif "podcast_embed" in pages[page_id]:
            del pages[page_id]["podcast_embed"]

        products_text = request.form.get("products_json", "").strip()
        if products_text:
            products = []
            for line in products_text.split("\n"):
                line = line.strip()
                if not line or "|" not in line:
                    continue
                parts = [p.strip() for p in line.split("|")]
                if parts[0]:
                    product = {
                        "title": parts[0],
                        "cover": parts[1] if len(parts) > 1 and parts[1] else "",
                        "amazon": parts[2] if len(parts) > 2 and parts[2] else "",
                        "gumroad": parts[3] if len(parts) > 3 and parts[3] else ""
                    }
                    if product["amazon"] or product["gumroad"]:
                        products.append(product)
            if products:
                pages[page_id]["products"] = products
            elif "products" in pages[page_id]:
                del pages[page_id]["products"]
        elif "products" in pages[page_id]:
            del pages[page_id]["products"]
        
        product_images_raw = request.form.get("product_images", "")
        if product_images_raw:
            pages[page_id]["product_images"] = [line.strip() for line in product_images_raw.split("\n") if line.strip()]
        else:
            pages[page_id]["product_images"] = []
        
        gallery_str = request.form.get("gallery_images", "").strip()
        if gallery_str:
            gallery_images = [img.strip() for img in gallery_str.split("\n") if img.strip()]
            pages[page_id]["gallery_images"] = gallery_images
        elif "gallery_images" in pages[page_id]:
            del pages[page_id]["gallery_images"]
        
        links_str = request.form.get("product_links", "").strip()
        if links_str:
            links = []
            for line in links_str.split("\n"):
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        links.append({
                            "name": parts[0].strip(),
                            "url": parts[1].strip(),
                            "icon": parts[2].strip()
                        })
            if links:
                pages[page_id]["product_links"] = links
        elif "product_links" in pages[page_id]:
            del pages[page_id]["product_links"]
        
        save_content({"pages": pages, "order": data.get("order", ORDER)})
        return redirect("/kahu")
    
    page = pages[page_id]
    gallery_str = "\n".join(page.get("gallery_images", []))
    products_text_lines = []
    if page.get("products"):
        for p in page["products"]:
            line = f"{p.get('title', '')} | {p.get('cover', '')} | {p.get('amazon', '')} | {p.get('gumroad', '')}"
            products_text_lines.append(line)
    products_json = "\n".join(products_text_lines)
    
    product_images_str = ""
    if page.get("product_images"):
        product_images_str = "\n".join(page["product_images"])
    
    links_str = ""
    if "product_links" in page:
        links_str = "\n".join([
            f"{link['name']}|{link['url']}|{link['icon']}"
            for link in page["product_links"]
        ])
    
    edit_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit {page.get('title', 'Page')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{ color: #2c3e50; margin-bottom: 0.5rem; }}
        .subtitle {{ color: #7f8c8d; margin-bottom: 2rem; }}
        .form-group {{ margin-bottom: 1.5rem; }}
        label {{
            display: block;
            color: #2c3e50;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        input[type="text"],
        textarea {{
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1rem;
            font-family: inherit;
            transition: border-color 0.3s ease;
        }}
        input[type="text"]:focus,
        textarea:focus {{
            outline: none;
            border-color: #667eea;
        }}
        textarea {{ min-height: 200px; resize: vertical; }}
        .help-text {{ font-size: 0.85rem; color: #6c757d; margin-top: 0.25rem; }}
        .btn-group {{ display: flex; gap: 1rem; margin-top: 2rem; }}
        .btn {{
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-block;
        }}
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }}
        .btn-secondary {{ background: #6c757d; color: white; }}
        .btn-secondary:hover {{ background: #5a6268; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>✏️ Edit Page</h1>
        <p class="subtitle">{page.get('title', '')}</p>
        
        <form method="POST">
            <div class="form-group">
                <label for="title">Page Title</label>
                <input type="text" id="title" name="title" value="{page.get('title', '')}" required>
            </div>
            
            <div class="form-group">
                <label for="hero_image">Hero Image URL</label>
                <input type="text" id="hero_image" name="hero_image" value="{page.get('hero_image', '')}" required>
            </div>
            
            <div class="form-group">
                <label for="body_md">Content (Markdown)</label>
                <textarea id="body_md" name="body_md" required>{page.get('body_md', '')}</textarea>
            </div>
            
            <div class="form-group">
                <label for="product_url">Product URL</label>
                <input type="text" id="product_url" name="product_url" value="{page.get('product_url', '')}">
            </div>
            
            <div class="form-group">
                <label for="gumroad_url">Gumroad URL</label>
                <input type="text" id="gumroad_url" name="gumroad_url" value="{page.get('gumroad_url', '')}">
            </div>
            
            <div class="form-group">
                <label for="podcast_embed">Podcast Embed</label>
                <textarea id="podcast_embed" name="podcast_embed" style="min-height: 100px;">{page.get('podcast_embed', '')}</textarea>
            </div>
            
            <div class="form-group">
                <label for="product_images">Product Images (One URL per line)</label>
                <textarea id="product_images" name="product_images" style="min-height: 120px;">{product_images_str}</textarea>
            </div>
            
            <div class="form-group">
                <label for="products_json">Products</label>
                <textarea id="products_json" name="products_json" style="min-height: 180px; font-family: 'Courier New', monospace;">{products_json}</textarea>
                <div class="help-text">Format: Title | Cover URL | Amazon URL | Gumroad URL</div>
            </div>

            <div class="form-group">
                <label for="gallery_images">Gallery Images</label>
                <textarea id="gallery_images" name="gallery_images" style="min-height: 100px;">{gallery_str}</textarea>
            </div>
            
            <div class="form-group">
                <label for="product_links">Music Links</label>
                <textarea id="product_links" name="product_links" style="min-height: 100px;">{links_str}</textarea>
                <div class="help-text">Format: Name|URL|Icon</div>
            </div>
            
            <div class="btn-group">
                <button type="submit" class="btn btn-primary">💾 Save</button>
                <a href="/kahu" class="btn btn-secondary">← Cancel</a>
            </div>
        </form>
    </div>
</body>
</html>"""
    
    return render_template_string(edit_html)

if __name__ == "__main__":
    if not DATA_FILE.exists():
        save_content(DEFAULT_PAGES)
    
    # Railway environment check
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
