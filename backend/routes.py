import re
from bson import ObjectId
from flask import jsonify, request
from app import app
from db import products_collection
from datetime import datetime, timezone
from pymongo import ReturnDocument  #to update route

def serialize(product):
    product["_id"] = str(product["_id"])
    for key in ("created_at", "updated_at"):
        value = product.get(key)
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            product[key] = value.isoformat().replace("+00:00", "Z")
    return product

def is_number(value):

    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_product(data, partial=False):
    """Return (clean_data, errors). partial=True is for updates, where fields are optional."""
    clean, errors = {}, {}

    if not partial or "name" in data:
        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            errors["name"] = "Name is required and must be text."
        elif len(name) > 300:
            errors["name"] = "Name must be 300 characters or fewer."
        else:
            clean["name"] = name.strip()

    if not partial or "price" in data:
        price = data.get("price")
        if not is_number(price) or price <= 0:
            errors["price"] = "Price is required and must be a number greater than 0."
        else:
            clean["price"] = float(price)

    if not partial or "category" in data:
        category = data.get("category")
        if not isinstance(category, str) or not category.strip():
            errors["category"] = "Category is required and must be text."
        else:
            clean["category"] = category.strip()

    if "stock" in data:
        stock = data["stock"]
        if not isinstance(stock, int) or isinstance(stock, bool) or stock < 0:
            errors["stock"] = "Stock must be a whole number, 0 or more."
        else:
            clean["stock"] = stock
    elif not partial:
        clean["stock"] = 0

    if "original_price" in data:
        original = data["original_price"]
        if not is_number(original) or original <= 0:
            errors["original_price"] = "Original price must be a number greater than 0."
        else:
            clean["original_price"] = float(original)

    if "image" in data:
        if not isinstance(data["image"], str):
            errors["image"] = "Image must be a URL string."
        else:
            clean["image"] = data["image"].strip()

    if "description" in data:
        desc = data["description"]
        if isinstance(desc, str):
            desc = [desc]
        if not isinstance(desc, list) or not all(isinstance(d, str) for d in desc):
            errors["description"] = "Description must be text or a list of text."
        else:
            clean["description"] = [d.strip() for d in desc if d.strip()]

    return clean, errors

@app.route("/")
def home():
    return "Welcome to our E-Commerce website!"


@app.route("/products")
def products():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    sort = request.args.get("sort", "")
    page = max(request.args.get("page", 1, type=int), 1)
    limit = min(max(request.args.get("limit", 12, type=int), 1), 50)

    query = {}

    if search:
        # re.escape stops users from sending regex characters that break the search
        query["name"] = {"$regex": re.escape(search), "$options": "i"}

    if category:
        query["category"] = {"$regex": f"^{re.escape(category)}$", "$options": "i"}

    price_filter = {}
    if min_price is not None:
        price_filter["$gte"] = min_price
    if max_price is not None:
        price_filter["$lte"] = max_price
    if price_filter:
        query["price"] = price_filter

    sort_options = {
        "price_asc": [("price", 1)],
        "price_desc": [("price", -1)],
        "rating": [("rating", -1)],
        "popular": [("rating_count", -1)],
    }
    sort_spec = sort_options.get(sort, [("name", 1)]) + [("_id", 1)]  # _id keeps paging stable

    total = products_collection.count_documents(query)
    cursor = (
        products_collection.find(query)
        .sort(sort_spec)
        .skip((page - 1) * limit)
        .limit(limit)
    )

    return jsonify({
        "products": [serialize(p) for p in cursor],
        "page": page,
        "limit": limit,
        "total": total,
        "pages": (total + limit - 1) // limit,
    })

@app.route("/products", methods=["POST"])
def create_product():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    clean, errors = validate_product(data)
    if errors:
        return jsonify({"errors": errors}), 400

    now = datetime.now(timezone.utc)
    clean["created_at"] = now
    clean["updated_at"] = now

    result = products_collection.insert_one(clean)
    clean["_id"] = result.inserted_id
    return jsonify(serialize(clean)), 201


@app.route("/products/<product_id>")
def get_product(product_id):
    if not ObjectId.is_valid(product_id):
        return jsonify({"error": "Invalid product id"}), 400

    product = products_collection.find_one({"_id": ObjectId(product_id)})
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(serialize(product))

@app.route("/products/<product_id>", methods=["PATCH"])
def update_product(product_id):
    if not ObjectId.is_valid(product_id):
        return jsonify({"error": "Invalid product id"}), 400

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    clean, errors = validate_product(data, partial=True)
    if errors:
        return jsonify({"errors": errors}), 400
    if not clean:
        return jsonify({"error": "No valid fields to update."}), 400

    clean["updated_at"] = datetime.now(timezone.utc)

    updated = products_collection.find_one_and_update(
        {"_id": ObjectId(product_id)},
        {"$set": clean},
        return_document=ReturnDocument.AFTER,
    )
    if updated is None:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(serialize(updated))

@app.route("/products/<product_id>", methods=["DELETE"])
def delete_product(product_id):
    if not ObjectId.is_valid(product_id):
        return jsonify({"error": "Invalid product id"}), 400

    result = products_collection.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({"message": "Product deleted"})

@app.route("/categories")
def categories():
    return jsonify(sorted(products_collection.distinct("category")))


@app.route("/cart")
def cart():
    return "Your shopping cart"