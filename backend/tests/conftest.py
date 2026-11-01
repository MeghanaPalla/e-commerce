import os
import sys

import mongomock
import pymongo
import pytest

# use an in-memory fake instead of a real MongoDB for tests
pymongo.MongoClient = mongomock.MongoClient
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app as flask_app, db  # noqa: E402
import shop  # noqa: E402,F401


@pytest.fixture
def client():
    for name in db.list_collection_names():
        db.drop_collection(name)
    flask_app.test_cli_runner().invoke(args=['seed'])
    return flask_app.test_client()
