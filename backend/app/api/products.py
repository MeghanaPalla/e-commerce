import re

from flask import request, jsonify, current_app

from app import db
from app.api import bp
from app.utils import product_json, to_oid, error

SORTS = {
    'newest': [('created', -1), ('_id', -1)],
    'price_asc': [('price_cents', 1), ('_id', 1)],
    'price_desc': [('price_cents', -1), ('_id', 1)],
    'name': [('name', 1), ('_id', 1)],
}


@bp.route('/products')
def list_products():
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    sort = request.args.get('sort', 'newest')
    page = max(request.args.get('page', 1, type=int), 1)
    per_page = request.args.get('per_page', current_app.config['PRODUCTS_PER_PAGE'], type=int)
    per_page = min(max(per_page, 1), 50)

    query = {}
    if q:
        pattern = {'$regex': re.escape(q), '$options': 'i'}
        query['$or'] = [{'name': pattern}, {'description': pattern}]
    if category:
        query['category'] = category

    total = db.products.count_documents(query)
    cursor = db.products.find(query).sort(SORTS.get(sort, SORTS['newest'])) \
        .skip((page - 1) * per_page).limit(per_page)
    pages = max((total + per_page - 1) // per_page, 1)
    return jsonify(items=[product_json(p) for p in cursor],
                   page=page, pages=pages, total=total)


@bp.route('/products/<id>')
def get_product(id):
    product = db.products.find_one({'_id': to_oid(id)})
    if product is None:
        return error('Product not found', 404)
    return jsonify(product_json(product))


@bp.route('/categories')
def categories():
    return jsonify(sorted(db.products.distinct('category')))
