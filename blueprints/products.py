# blueprints/products.py
# =========================================================
# Digital products management.
# Public product pages + admin CRUD (add / edit / delete).
# =========================================================

from flask import Blueprint, abort, redirect, render_template, request
from flask import jsonify, send_file
from werkzeug.utils import secure_filename
from pathlib import Path

from content import (
    load_digital_products,
    save_digital_products,
    generate_product_id,
    get_product_by_id,
)
from config import PRODUCTS_FOLDER, LOGO_PATH, LOGO_HEIGHT, FOOTER_TEXT, CONTACT_EMAIL
from auth import require_admin
from download_tokens import validate_and_consume_token

products_bp = Blueprint("products", __name__)


# =========================================================
# PUBLIC: Products listing page
# =========================================================

@products_bp.route("/products")
def products_list():
    products_data = load_digital_products()
    products = [
        p for p in products_data.get("products", [])
        if p.get("active", True) and p.get("category") != "partnership"
    ]
    return render_template(
        "products.html",
        products=products,
        logo_path=LOGO_PATH,
        logo_height=LOGO_HEIGHT,
        footer_text=FOOTER_TEXT,
        contact_email=CONTACT_EMAIL,
    )


# =========================================================
# PUBLIC: Product sales page
# =========================================================

@products_bp.route("/product/<product_id>")
def product_page(product_id):
    product = get_product_by_id(product_id)
    if not product or not product.get("active", True):
        abort(404)
    return render_template(
        "product_page.html",
        product=product,
        logo_path=LOGO_PATH,
        logo_height=LOGO_HEIGHT,
        footer_text=FOOTER_TEXT,
        contact_email=CONTACT_EMAIL,
    )


# =========================================================
# PUBLIC: Download product file (after payment)
# Requires a signed, product-bound, time-limited token minted by
# _render_payment_success() in blueprints/payments.py right after a
# verified PayPal/Stripe payment. See download_tokens.py.
# =========================================================

@products_bp.route("/download/product/<product_id>/<token>")
def download_product(product_id, token):
    product = get_product_by_id(product_id)
    if not product:
        abort(404)
    ok, reason = validate_and_consume_token(product_id, token)
    if not ok:
        # "not_configured" is a server misconfiguration (missing
        # DOWNLOAD_TOKEN_SECRET) -> 503, matching how this app already
        # signals missing ADMIN_PASSWORD/PayPal secrets elsewhere.
        # Everything else is a bad/expired/reused/mismatched token from
        # the requester -> 403, and deliberately not distinguished further
        # in the response so a forged-token attempt can't be fingerprinted.
        abort(503 if reason == "not_configured" else 403)
    products_data = load_digital_products()
    for p in products_data["products"]:
        if p["id"] == product_id:
            p["downloads"] = p.get("downloads", 0) + 1
    save_digital_products(products_data)
    file_path = Path(product["file_path"])
    return send_file(file_path, as_attachment=True, download_name=product["filename"])


# =========================================================
# ADMIN: Products list
# =========================================================

@products_bp.route("/admin/products")
@require_admin
def admin_products():
    products_data = load_digital_products()
    return render_template(
        "admin/products_list.html",
        products=products_data.get("products", []),
    )


# =========================================================
# ADMIN: Add product
# =========================================================

@products_bp.route("/admin/products/add", methods=["POST"])
@require_admin
def add_product():
    name = request.form.get("name")
    description = request.form.get("description")
    price = float(request.form.get("price", 0))
    category = request.form.get("category", "ebook")
    cover_image = request.form.get("cover_image", "")

    file = request.files.get("file")
    if not file:
        return "No file uploaded", 400

    filename = secure_filename(file.filename)
    product_id = generate_product_id()
    PRODUCTS_FOLDER.mkdir(exist_ok=True)
    file_path = PRODUCTS_FOLDER / f"{product_id}_{filename}"
    file.save(file_path)

    products_data = load_digital_products()
    products_data["products"].append({
        "id": product_id,
        "name": name,
        "description": description,
        "price": price,
        "category": category,
        "filename": filename,
        "file_path": str(file_path),
        "cover_image": cover_image,
        "active": True,
        "downloads": 0,
        "total_sales": 0,
    })
    save_digital_products(products_data)
    return redirect("/admin/products")


# =========================================================
# ADMIN: Edit product
# =========================================================

@products_bp.route("/admin/products/edit/<product_id>", methods=["GET", "POST"])
@require_admin
def edit_product(product_id):
    products_data = load_digital_products()
    product = next(
        (p for p in products_data["products"] if p["id"] == product_id), None
    )
    if not product:
        abort(404)

    if request.method == "POST":
        product["name"] = request.form.get("name")
        product["description"] = request.form.get("description")
        product["price"] = float(request.form.get("price", 0))
        product["category"] = request.form.get("category", "ebook")
        product["cover_image"] = request.form.get("cover_image", "")
        product["active"] = request.form.get("active") == "on"
        save_digital_products(products_data)
        return redirect("/admin/products")

    return render_template("admin/product_edit.html", product=product)


# =========================================================
# ADMIN: Delete product
# =========================================================

@products_bp.route("/admin/products/delete/<product_id>", methods=["POST"])
@require_admin
def delete_product(product_id):
    products_data = load_digital_products()
    product = next(
        (p for p in products_data["products"] if p["id"] == product_id), None
    )
    if product:
        file_path = Path(product["file_path"])
        if file_path.exists():
            file_path.unlink()
        products_data["products"] = [
            p for p in products_data["products"] if p["id"] != product_id
        ]
        save_digital_products(products_data)
    return jsonify({"success": True})
