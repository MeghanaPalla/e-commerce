import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_login import LoginManager

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise ValueError("SECRET_KEY is missing. Check your .env file.")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

login = LoginManager(app)


@login.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Login required."}), 401


import routes
import auth