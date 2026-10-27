from bson import ObjectId
from flask_login import UserMixin
from werkzeug.security import check_password_hash

from app import login
from db import users_collection


class User(UserMixin):
    def __init__(self, doc):
        self.doc = doc
        self.id = str(doc["_id"])

    @property
    def name(self):
        return self.doc["name"]

    @property
    def email(self):
        return self.doc["email"]

    @property
    def role(self):
        return self.doc.get("role", "customer")

    def check_password(self, password):
        return check_password_hash(self.doc["password_hash"], password)

    def to_dict(self):
        return {"_id": self.id, "name": self.name, "email": self.email, "role": self.role}


@login.user_loader
def load_user(user_id):
    if not ObjectId.is_valid(user_id):
        return None
    doc = users_collection.find_one({"_id": ObjectId(user_id)})
    return User(doc) if doc else None