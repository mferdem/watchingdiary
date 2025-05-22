import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app, db

@pytest.fixture(scope='session')
def app():
    app = create_app(testing=True)
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def _db(app):
    db.create_all()
    yield db
    db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
