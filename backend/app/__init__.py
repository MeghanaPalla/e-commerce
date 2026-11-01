from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r'/api/*': {'origins': app.config['CORS_ORIGINS'].split(',')}})

client = MongoClient(app.config['MONGO_URI'])
db = client[app.config['MONGO_DB']]

from app.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')

from app import errors
