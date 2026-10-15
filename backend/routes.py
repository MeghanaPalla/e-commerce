from flask import jsonify, request
from app import app

product_list = [
    {
        "id": 1,
        "name": "Wireless Mouse",
        "price": 599,
        "category": "Electronics",
        "in_stock": True
    },
    {
        "id": 2,
        "name": "Mechanical Keyboard",
        "price": 2499,
        "category": "Electronics",
        "in_stock": True
    },
    {
        "id": 3,
        "name": "USB-C Cable",
        "price": 299,
        "category": "Accessories",
        "in_stock": False
    }
]


@app.route("/")
def home():
    return "Welcome to our E-Commerce website!"


@app.route("/products")
def products():
    search_query = request.args.get("search", "").lower()
    category_query = request.args.get("category","").lower()
    filtered_products = []

    for product in product_list:
        name_matches = search_query in product["name"].lower()
        category_matches = category_query in product["category"].lower()
        if name_matches and category_matches:
            filtered_products.append(product)

    return jsonify(filtered_products)


@app.route("/products/<int:product_id>")
def get_product(product_id):
    for product in product_list:
        if product["id"] == product_id:
            return jsonify(product)

    return jsonify({"error": "Product not found"}), 404


@app.route("/cart")
def cart():
    return "Your shopping cart"