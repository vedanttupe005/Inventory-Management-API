#================== Test Create Order ==================
#================== Test Create Order ==================
import pytest
from app.model import Product, Order, OrderItems, InventoryLog

def test_create_order_success(
    app,
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="user")

    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()

        product_id = product.id
        original_quantity = product.quantity
        price = product.price

    response = client.post(
        "/api/v1/orders/",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2
                }
            ]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 201

    data = response.json

    assert data["total_amount"] == price * 2


def test_create_order_saved_to_database(
    app,
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="user")

    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()

        product_id = product.id

    response = client.post(
        "/api/v1/orders/",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2
                }
            ]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 201

    order_id = response.json["id"]

    with app.app_context():
        order = Order.query.get(order_id)

        assert order is not None
        assert order.total_amount == 100000


def test_create_order_creates_order_item(
    app,
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="user")

    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()

        product_id = product.id
        price = product.price

    response = client.post(
        "/api/v1/orders/",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2
                }
            ]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 201

    order_id = response.json["id"]

    with app.app_context():
        order_item = OrderItems.query.filter_by(
            order_id=order_id,
            product_id=product_id
        ).first()

        assert order_item is not None
        assert order_item.quantity == 2
        assert order_item.price == price


def test_create_order_updates_inventory(
    app,
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="user")

    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()

        product_id = product.id
        original_quantity = product.quantity

    response = client.post(
        "/api/v1/orders/",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2
                }
            ]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 201

    with app.app_context():
        product = Product.query.get(product_id)

        assert product.quantity == original_quantity - 2


def test_create_order_creates_inventory_log(
    app,
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="user")

    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()

        product_id = product.id

    response = client.post(
        "/api/v1/orders/",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2
                }
            ]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 201

    with app.app_context():
        log = InventoryLog.query.filter_by(
            product_id=product_id,
            change_type="order"
        ).first()

        assert log is not None
        assert log.quantity_changed == -2


def test_create_order_multiple_products(
    app,
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="user")

    with app.app_context():
        laptop = Product.query.filter_by(
            name="Laptop"
        ).first()

        mouse = Product.query.filter_by(
            name="Mouse"
        ).first()

        laptop_id = laptop.id
        mouse_id = mouse.id

        laptop_quantity = laptop.quantity
        mouse_quantity = mouse.quantity

    response = client.post(
        "/api/v1/orders/",
        json={
            "items": [
                {
                    "product_id": laptop_id,
                    "quantity": 2
                },
                {
                    "product_id": mouse_id,
                    "quantity": 3
                }
            ]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 201

    data = response.json

    assert data["total_amount"] == 101500

    with app.app_context():
        laptop = Product.query.get(laptop_id)
        mouse = Product.query.get(mouse_id)

        assert laptop.quantity == laptop_quantity - 2
        assert mouse.quantity == mouse_quantity - 3


def test_create_order_duplicate_product(
    app,
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="user")

    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()

        product_id = product.id

    response = client.post(
        "/api/v1/orders/",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2
                },
                {
                    "product_id": product_id,
                    "quantity": 1
                }
            ]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 400

    assert response.json["message"] == (
        f"Duplicate product_id {product_id} in order items"
    )


def test_create_order_product_not_found(
    client,
    get_access_token
):
    access_token = get_access_token(role="user")

    product_id = 99999

    response = client.post(
        "/api/v1/orders/",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1
                }
            ]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 400

    assert response.json["message"] == (
        f"Product with id {product_id} does not exist"
    )


def test_create_order_zero_quantity(
    app,
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="user")

    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()

        product_id = product.id

    response = client.post(
        "/api/v1/orders/",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 0
                }
            ]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    print("STATUS:", response.status_code)
    print("JSON:", response.json)
    print("DATA:", response.get_data(as_text=True))
    assert response.status_code == 422

    assert response.json["errors"] == (
        {'json': {'items': {'0': {'quantity': ['Must be greater than or equal to '
                                       '1.']}}}}#because of the validation in the schema, it will return 422 instead of 400
    )


def test_create_order_negative_quantity(
    app,
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="user")

    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()

        product_id = product.id

    response = client.post(
        "/api/v1/orders/",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": -2
                }
            ]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422

    assert response.json["errors"] == (
        {'json': {'items': {'0': {'quantity': ['Must be greater than or equal to '
                                       '1.']}}}}#because of the validation in the schema, it will return 422 instead of 400
    )


def test_create_order_insufficient_stock(
    app,
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="user")

    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()
        available_quantity = product.quantity
        product_id = product.id

    response = client.post(
        "/api/v1/orders/",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 11
                }
            ]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 400

    assert response.json["message"] == (
        f"Insufficient stock for product Laptop. Available: {available_quantity}, Requested: {11}"
    )


def test_create_order_no_token(
    client,
    products
):
    # We only need the fixture to populate the database.
    response = client.post(
        "/api/v1/orders/",
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1
                }
            ]
        }
    )

    assert response.status_code == 401
    assert response.json["msg"] == "Missing Authorization Header"


def test_create_order_invalid_token(
    client,
    products
):
    response = client.post(
        "/api/v1/orders/",
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1
                }
            ]
        },
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 422



@pytest.mark.parametrize(
    "role",
    ["admin", "manager", "staff", "user"]
)
def test_create_order_allowed_roles(
    app,
    client,
    get_access_token,
    products,
    role
):
    access_token = get_access_token(role=role)

    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()

        product_id = product.id

    response = client.post(
        "/api/v1/orders/",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1
                }
            ]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 201



def test_create_order_empty_items(
    client,
    get_access_token
):
    access_token = get_access_token(role="user")

    response = client.post(
        "/api/v1/orders/",
        json={
            "items": []
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422





#================== Test Create Order ==================
#================== Test Create Order ==================






