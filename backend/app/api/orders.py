from datetime import datetime, timezone

from flask import request, jsonify, g

from app import db
from app.api import bp
from app.api.cart import cart_lines
from app.utils import login_required, to_oid, iso, error


def order_json(o):
    return {'id': str(o['_id']), 'created': iso(o['created']), 'status': o['status'],
            'full_name': o['full_name'], 'address': o['address'],
            'total_cents': o['total_cents'],
            'items': [{'name': i['name'], 'price_cents': i['price_cents'],
                       'quantity': i['quantity'],
                       'subtotal_cents': i['price_cents'] * i['quantity']}
                      for i in o['items']]}


@bp.route('/orders', methods=['POST'])
@login_required
def place_order():
    data = request.get_json(silent=True) or {}
    full_name = str(data.get('full_name', '')).strip()
    address = str(data.get('address', '')).strip()
    if not 1 <= len(full_name) <= 120:
        return error('Please enter your full name', 400)
    if not 1 <= len(address) <= 300:
        return error('Please enter a delivery address (max 300 characters)', 400)

    lines = cart_lines()
    if not lines:
        return error('Your cart is empty', 400)

    # take stock one product at a time; undo everything if any product runs out
    taken = []
    for line in lines:
        pid = to_oid(line['product_id'])
        result = db.products.update_one(
            {'_id': pid, 'stock': {'$gte': line['quantity']}},
            {'$inc': {'stock': -line['quantity']}})
        if result.modified_count == 0:
            for done_id, done_qty in taken:
                db.products.update_one({'_id': done_id}, {'$inc': {'stock': done_qty}})
            return error('Sorry, {} no longer has enough stock'.format(line['name']), 409)
        taken.append((pid, line['quantity']))

    order = {'user_id': g.user['_id'], 'created': datetime.now(timezone.utc),
             'status': 'Placed', 'full_name': full_name, 'address': address,
             'total_cents': sum(l['subtotal_cents'] for l in lines),
             'items': [{'name': l['name'], 'price_cents': l['price_cents'],
                        'quantity': l['quantity']} for l in lines]}
    order['_id'] = db.orders.insert_one(order).inserted_id
    db.carts.update_one({'user_id': g.user['_id']}, {'$set': {'items': []}})
    return jsonify(order_json(order)), 201


@bp.route('/orders')
@login_required
def list_orders():
    orders = db.orders.find({'user_id': g.user['_id']}).sort('created', -1)
    return jsonify([order_json(o) for o in orders])


@bp.route('/orders/<id>')
@login_required
def get_order(id):
    order = db.orders.find_one({'_id': to_oid(id), 'user_id': g.user['_id']})
    if order is None:
        return error('Order not found', 404)
    return jsonify(order_json(order))
