import pytest

from app import create_app
from app.model.user import User
from app.config import TestingConfig
from app.extensions import db
from app.model import Catogary, Product, InventoryLog



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


@pytest.fixture
def inventory_logs(app):
    with app.app_context():

        user = User(
            username="testuser",
            email="testuser@example.com",
            role="admin"
        )
        user.set_password("password123")

        category = Catogary(
            name="Electronics"
        )

        db.session.add_all([user, category])
        db.session.commit()

        product1 = Product(
            name="Laptop",
            description="Gaming laptop",
            price=50000,
            quantity=10,
            category_id=category.id
        )

        product2 = Product(
            name="Mouse",
            description="Wireless mouse",
            price=1000,
            quantity=20,
            category_id=category.id
        )

        db.session.add_all([product1, product2])
        db.session.commit()

        log1 = InventoryLog(
            user_id=user.id,
            product_id=product1.id,
            change_type="addition",
            quantity_changed=10
        )

        log2 = InventoryLog(
            user_id=user.id,
            product_id=product1.id,
            change_type="subtraction",
            quantity_changed=2
        )

        log3 = InventoryLog(
            user_id=user.id,
            product_id=product2.id,
            change_type="addition",
            quantity_changed=20
        )

        db.session.add_all([log1, log2, log3])
        db.session.commit()

        return {
            "user": user,
            "category": category,
            "product1": product1,
            "product2": product2,
            "product1_id": product1.id,
            "product2_id": product2.id,
            "logs": [log1, log2, log3]
        }



