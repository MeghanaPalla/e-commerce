from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from bson import ObjectId
from bson.errors import InvalidId
from flask import request, g, jsonify, current_app

from app import db


def error(message, status):
    return jsonify(error=message), status


def to_oid(value):
    """Turn a string into an ObjectId, or None if it isn't a valid one."""
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None


def parse_int(value, minimum=1, maximum=1000):
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value if minimum <= value <= maximum else None


def iso(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def make_token(user_id):
    expires = datetime.now(timezone.utc) + timedelta(hours=current_app.config['TOKEN_HOURS'])
    return jwt.encode({'sub': str(user_id), 'exp': expires},
                      current_app.config['SECRET_KEY'], algorithm='HS256')


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        header = request.headers.get('Authorization', '')
        if not header.startswith('Bearer '):
            return error('Please log in first', 401)
        try:
            data = jwt.decode(header[7:], current_app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except jwt.PyJWTError:
            return error('Session expired, please log in again', 401)
        user = db.users.find_one({'_id': to_oid(data.get('sub'))})
        if user is None:
            return error('Account not found', 401)
        g.user = user
        return f(*args, **kwargs)
    return wrapper


def product_json(p):
    return {'id': str(p['_id']), 'name': p['name'], 'description': p['description'],
            'category': p['category'], 'price_cents': p['price_cents'],
            'stock': p['stock']}
