import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-only-secret-change-me-in-production'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/'
    MONGO_DB = os.environ.get('MONGO_DB') or 'minishop'
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS') or 'http://localhost:5173'
    TOKEN_HOURS = 24
    PRODUCTS_PER_PAGE = 8
