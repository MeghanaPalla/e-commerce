import re
from datetime import datetime, timezone

from flask import jsonify, request
from flask_login import current_user, login_required, login_user, logout_user
from pymongo.errors import DuplicateKeyError
from werkzeug.security import generate_password_hash

from app import app
from db import users_collection
from models import User
@app.route("/auth/login", methods=["POST"])
def login_route():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    email = data.get("email")
    password = data.get("password")
    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({"error": "Email and password are required."}), 400

    doc = users_collection.find_one({"email": email.strip().lower()})
    user = User(doc) if doc else None
    if user is None or not user.check_password(password):
        return jsonify({"error": "Invalid email or password."}), 401

    login_user(user)
    return jsonify(user.to_dict())


@app.route("/auth/logout", methods=["POST"])
@login_required
def logout_route():
    logout_user()
    return jsonify({"message": "Logged out."})


@app.route("/auth/me")
@login_required
def me():
    return jsonify(current_user.to_dict())