import pytest

from app import create_app, db
from app.config import TestConfig


@pytest.fixture
def app():
    application = create_app(TestConfig)

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    from app import db
    from app.models.user import User

    with app.app_context():
        user = User(username="test-admin", role="admin")
        user.set_password("test-password-123")
        db.session.add(user)
        db.session.commit()
    client = app.test_client()
    client.post("/login", data={"username": "test-admin", "password": "test-password-123"})
    return client
