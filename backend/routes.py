import re
from bson import ObjectId
from flask import jsonify, request
from app import app
from db import products_collection


def serialize(product):
    """Convert MongoDB's ObjectId to a string so it can be sent as JSON."""
    product["_id"] = str(product["_id"])
    return product


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


@app.route("/products/<product_id>")
def get_product(product_id):
    if not ObjectId.is_valid(product_id):
        return jsonify({"error": "Invalid product id"}), 400

    product = products_collection.find_one({"_id": ObjectId(product_id)})
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(serialize(product))


@app.route("/categories")
def categories():
    return jsonify(sorted(products_collection.distinct("category")))


@app.route("/cart")
def cart():
    return "Your shopping cart"