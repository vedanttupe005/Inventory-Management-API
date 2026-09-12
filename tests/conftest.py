import pytest

from app import create_app
from app.model.user import User
from app.config import TestingConfig
from app.extensions import db



@pytest.fixture() # used to create a test app and database
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture() # used to send request like postman
def client(app):
    return app.test_client()





@pytest.fixture
def get_access_token(client):
    def _get_access_token(role="user"):
        register_data = {
            "username": f"{role}_testuser",
            "email": f"{role}_test@test.com",
            "password": "Password123"
        }

        # Register user
        response = client.post(
            "/api/v1/auth/register",
            json=register_data
        )

        assert response.status_code == 201

        # Update user role
        user = User.query.filter_by(
            email=register_data["email"]
        ).first()

        user.role = role
        db.session.commit()

        # Login user
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": register_data["email"],
                "password": register_data["password"]
            }
        )

        assert response.status_code == 200

        return response.get_json()["access_token"]

    return _get_access_token



