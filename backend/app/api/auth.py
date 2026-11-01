import re
from datetime import datetime, timezone

from flask import request, jsonify, g
from pymongo.errors import DuplicateKeyError
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.api import bp
from app.utils import make_token, login_required, error

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def user_json(u):
    return {'id': str(u['_id']), 'username': u['username'], 'email': u['email']}


@bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    username = str(data.get('username', '')).strip()
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))

    if not 3 <= len(username) <= 64:
        return error('Username must be 3 to 64 characters', 400)
    if not EMAIL_RE.match(email):
        return error('Please enter a valid email address', 400)
    if len(password) < 6:
        return error('Password must be at least 6 characters', 400)
    if db.users.find_one({'$or': [{'username': username}, {'email': email}]}):
        return error('Username or email is already registered', 409)

    user = {'username': username, 'email': email,
            'password_hash': generate_password_hash(password),
            'created': datetime.now(timezone.utc)}
    try:
        user['_id'] = db.users.insert_one(user).inserted_id
    except DuplicateKeyError:
        return error('Username or email is already registered', 409)
    return jsonify(token=make_token(user['_id']), user=user_json(user)), 201


@bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    who = str(data.get('username', '')).strip()
    password = str(data.get('password', ''))
    user = db.users.find_one({'$or': [{'username': who}, {'email': who.lower()}]})
    if user is None or not check_password_hash(user['password_hash'], password):
        return error('Invalid username or password', 401)
    return jsonify(token=make_token(user['_id']), user=user_json(user))


@bp.route('/auth/me')
@login_required
def me():
    return jsonify(user=user_json(g.user))
