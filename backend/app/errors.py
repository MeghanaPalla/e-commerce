from flask import jsonify
from app import app


@app.errorhandler(404)
def not_found(e):
    return jsonify(error='Not found'), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify(error='Method not allowed'), 405


@app.errorhandler(500)
def server_error(e):
    return jsonify(error='Something went wrong on our side'), 500
