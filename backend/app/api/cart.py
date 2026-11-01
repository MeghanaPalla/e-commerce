from flask import request, jsonify, g

from app import db
from app.api import bp
from app.utils import login_required, to_oid, parse_int, error


def get_items():
    doc = db.carts.find_one({'user_id': g.user['_id']})
    return doc['items'] if doc else []


def save_items(items):
    db.carts.update_one({'user_id': g.user['_id']}, {'$set': {'items': items}}, upsert=True)


def cart_lines():
    """Cart rows joined with current product data."""
    items = get_items()
    ids = [i['product_id'] for i in items]
    products = {p['_id']: p for p in db.products.find({'_id': {'$in': ids}})}
    lines = []
    for item in items:
        p = products.get(item['product_id'])
        if p is None:          # product was deleted, skip it
            continue
        lines.append({'product_id': str(p['_id']), 'name': p['name'],
                      'price_cents': p['price_cents'], 'stock': p['stock'],
                      'quantity': item['quantity'],
                      'subtotal_cents': p['price_cents'] * item['quantity']})
    return lines


def cart_response():
    lines = cart_lines()
    return jsonify(items=lines,
                   count=sum(l['quantity'] for l in lines),
                   total_cents=sum(l['subtotal_cents'] for l in lines))


@bp.route('/cart')
@login_required
def get_cart():
    return cart_response()


@bp.route('/cart', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json(silent=True) or {}
    pid = to_oid(data.get('product_id'))
    qty = parse_int(data.get('quantity', 1))
    if pid is None or qty is None:
        return error('Invalid product or quantity', 400)
    product = db.products.find_one({'_id': pid})
    if product is None:
        return error('Product not found', 404)

    items = get_items()
    for item in items:
        if item['product_id'] == pid:
            new_qty = item['quantity'] + qty
            break
    else:
        item, new_qty = None, qty
    if new_qty > product['stock']:
        return error('Only {} of {} in stock'.format(product['stock'], product['name']), 400)
    if item:
        item['quantity'] = new_qty
    else:
        items.append({'product_id': pid, 'quantity': qty})
    save_items(items)
    return cart_response()


@bp.route('/cart/<product_id>', methods=['PUT'])
@login_required
def update_cart(product_id):
    pid = to_oid(product_id)
    data = request.get_json(silent=True) or {}
    qty = parse_int(data.get('quantity'), minimum=0)
    if pid is None or qty is None:
        return error('Invalid product or quantity', 400)
    items = get_items()
    item = next((i for i in items if i['product_id'] == pid), None)
    if item is None:
        return error('That item is not in your cart', 404)
    if qty == 0:
        items.remove(item)
    else:
        product = db.products.find_one({'_id': pid})
        if product is None or qty > product['stock']:
            return error('Not enough stock', 400)
        item['quantity'] = qty
    save_items(items)
    return cart_response()


@bp.route('/cart/<product_id>', methods=['DELETE'])
@login_required
def remove_from_cart(product_id):
    pid = to_oid(product_id)
    save_items([i for i in get_items() if i['product_id'] != pid])
    return cart_response()
