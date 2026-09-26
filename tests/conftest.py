import pytest

from app import create_app
from app.model.user import User
from app.config import TestingConfig
from app.extensions import db
from app.model import Catogary, Product, InventoryLog, Order, OrderItems



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


@pytest.fixture
def low_stock_inventory_logs(app):
    with app.app_context():

        category = Catogary(
            name="Electronics"
        )

        db.session.add(category)
        db.session.commit()

        product1 = Product(
            name="Laptop",
            description="Gaming laptop",
            price=50000,
            quantity=5,
            category_id=category.id
        )

        product2 = Product(
            name="Keyboard",
            description="Mechanical keyboard",
            price=3000,
            quantity=10,
            category_id=category.id
        )

        product3 = Product(
            name="Mouse",
            description="Wireless mouse",
            price=1000,
            quantity=20,
            category_id=category.id
        )

        db.session.add_all([
            product1,
            product2,
            product3
        ])
        db.session.commit()

        user = User(
            username="inventoryuser",
            email="inventory@example.com",
            role="admin"
        )

        user.set_password("password123")

        db.session.add(user)
        db.session.commit()

        log1 = InventoryLog(
            user_id=user.id,
            product_id=product1.id,
            change_type="addition",
            quantity_changed=5
        )

        log2 = InventoryLog(
            user_id=user.id,
            product_id=product2.id,
            change_type="addition",
            quantity_changed=10
        )

        log3 = InventoryLog(
            user_id=user.id,
            product_id=product3.id,
            change_type="addition",
            quantity_changed=20
        )

        db.session.add_all([
            log1,
            log2,
            log3
        ])
        db.session.commit()

        return {
            "products": [product1, product2, product3],
            "product_ids": [product1.id, product2.id, product3.id],
            "logs": [log1, log2, log3]
        }


@pytest.fixture
def category(app):
    with app.app_context():
        electronics = Catogary(name="Electronics")
        furniture = Catogary(name="Furniture")
        db.session.add_all([electronics, furniture])
        db.session.commit()
        return [[electronics.id, furniture.id], [electronics.name, furniture.name]]  # Return both IDs and objects for flexibility


@pytest.fixture
def products(app, category):
    with app.app_context():



        products = [
            Product(
                name="Laptop",
                description="Business laptop",

                price=50000,
                quantity=10,
                category_id=category[0][0]
            ),
            Product(
                name="Mouse",
                description="Wireless mouse",

                price=500,
                quantity=25,
                category_id=category[0][0]
            ),
            Product(
                name="Keyboard",
                description="Mechanical keyboard",

                price=2500,
                quantity=15,
                category_id=category[0][0]
            ),
            Product(
                name="Office Chair",
                description="Ergonomic office chair",

                price=8000,
                quantity=5,
                category_id=category[0][1]
            ),
            Product(
                name="Desk",
                description="Office desk",

                price=12000,
                quantity=8,
                category_id=category[0][1]
            )
        ]

        db.session.add_all(products)
        db.session.commit()

        return products



@pytest.fixture
def order(app, products):
    def _create_order(user_role="user"):
        with app.app_context():

            product = Product.query.filter_by(
                name="Laptop"
            ).first()

            user = User.query.filter_by(
                email=f"{user_role}_test@test.com"
            ).first()

            if not user:
                user = User(
                    username=f"{user_role}_testuser",
                    email=f"{user_role}_test@test.com",

                    role=user_role
                )
                user.set_password("Password123")
                db.session.add(user)
                db.session.flush()

            order = Order(
                user_id=user.id,
                total_amount=product.price * 2
            )

            db.session.add(order)
            db.session.flush()

            order_item = OrderItems(
                order_id=order.id,
                product_id=product.id,
                quantity=2,
                price=product.price
            )

            db.session.add(order_item)
            db.session.commit()

            order_id = order.id

            return order_id

    return _create_order

