#================== Get products with searching,sorting,pagination, filtering ==================
#================== Get products with searching,sorting,pagination, filtering ==================
import pytest
from app.model import Product,InventoryLog



def test_get_products_no_token(client):
    response = client.get("/api/v1/products/")

    assert response.status_code == 401
    assert response.json["msg"] == "Missing Authorization Header"


def test_get_products_invalid_token(client):
    response = client.get(
        "/api/v1/products/",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 422


def test_get_products_success(client, get_access_token, products):
    access_token = get_access_token(role="user")

    response = client.get(
        "/api/v1/products/",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json

    assert "page" in data
    assert "per_page" in data
    assert "total" in data
    assert "pages" in data
    assert "items" in data

    assert data["total"] == len(products)


def test_get_products_default_pagination(
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="user")

    response = client.get(
        "/api/v1/products/",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json

    assert data["page"] == 1
    assert data["per_page"] == 10
    assert data["total"] == len(products)
    assert len(data["items"]) <= 10


def test_get_products_pagination(
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="user")

    response = client.get(
        "/api/v1/products/?page=1&limit=2",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json

    assert data["page"] == 1
    assert data["per_page"] == 2
    assert data["total"] == len(products)
    assert len(data["items"]) <= 2


def test_get_products_invalid_page(
    client,
    get_access_token
):
    access_token = get_access_token(role="user")

    response = client.get(
        "/api/v1/products/?page=0",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 400
    assert response.json["message"] == "Page and limit must be greater than 0"



def test_get_products_invalid_limit(
    client,
    get_access_token
):
    access_token = get_access_token(role="user")

    response = client.get(
        "/api/v1/products/?limit=0",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 400
    assert response.json["message"] == "Page and limit must be greater than 0"


def test_get_products_limit_exceeds_max(
    client,
    get_access_token
):
    access_token = get_access_token(role="user")

    response = client.get(
        "/api/v1/products/?limit=101",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 400
    assert response.json["message"] == "Limit must be less than or equal to 100"


def test_get_products_search_by_name(
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="user")

    response = client.get(
        "/api/v1/products/?name=laptop",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json

    assert data["total"] >= 1
    assert all(
        "laptop" in product["name"].lower()
        for product in data["items"]
    )


def test_get_products_filter_by_category_id(
    client,
    get_access_token,
    products,
    category

):
    access_token = get_access_token(role="user")

    response = client.get(
        f"/api/v1/products/?category_id={category[0][0]}",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json

    assert all(
        product["category_id"] == category[0][0]
        for product in data["items"]
    )


def test_get_products_filter_by_category_name(
    client,
    get_access_token,
    products,
    category
):
    access_token = get_access_token(role="user")

    response = client.get(
        f"/api/v1/products/?category={category[1][0]}",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json

    assert data["total"] >= 1


def test_get_products_price_lt(
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="user")

    response = client.get(
        "/api/v1/products/?price_lt=1000",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json

    assert all(
        product["price"] <= 1000
        for product in data["items"]
    )


def test_get_products_price_gt(
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="user")

    response = client.get(
        "/api/v1/products/?price_gt=1000",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json

    assert all(
        product["price"] >= 1000
        for product in data["items"]
    )


def test_get_products_quantity_lt(
    client,
    get_access_token
):
    access_token = get_access_token(role="user")

    response = client.get(
        "/api/v1/products/?quantity_lt=10",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json

    assert all(
        product["quantity"] <= 10
        for product in data["items"]
    )


def test_get_products_quantity_gt(
    client,
    get_access_token
):
    access_token = get_access_token(role="user")

    response = client.get(
        "/api/v1/products/?quantity_gt=10",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json

    assert all(
        product["quantity"] >= 10
        for product in data["items"]
    )


def test_get_products_sort_price_ascending(
    client,
    get_access_token
):
    access_token = get_access_token(role="user")

    response = client.get(
        "/api/v1/products/?sort=price",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json

    prices = [product["price"] for product in data["items"]]

    assert prices == sorted(prices)


def test_get_products_sort_price_descending(
    client,
    get_access_token
):
    access_token = get_access_token(role="user")

    response = client.get(
        "/api/v1/products/?sort=-price",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json

    prices = [product["price"] for product in data["items"]]

    assert prices == sorted(prices, reverse=True)


def test_get_products_no_matching_products(
    client,
    get_access_token
):
    access_token = get_access_token(role="user")

    response = client.get(
        "/api/v1/products/?name=product_that_does_not_exist",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json

    assert data["total"] == 0
    assert data["items"] == []
    assert data["pages"] == 0


def test_get_products_combined_filters(
    client,
    get_access_token
):
    access_token = get_access_token(role="user")

    response = client.get(
        "/api/v1/products/?"
        "price_gt=500&"
        "price_lt=5000&"
        "quantity_gt=5&"
        "sort=-price",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json

    for product in data["items"]:
        assert product["price"] >= 500
        assert product["price"] <= 5000
        assert product["quantity"] >= 5

    prices = [product["price"] for product in data["items"]]

    assert prices == sorted(prices, reverse=True)




#================== Test Get product with ID  ==================
#================== Test Get product with ID  ==================




def test_get_product_success(
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="user")

    product = Product.query.first()

    response = client.get(
        f"/api/v1/products/1",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json

    assert data["id"] == product.id
    assert data["name"] == product.name
    assert data["description"] == product.description

    assert data["price"] == product.price
    assert data["quantity"] == product.quantity
    assert data["category_id"] == product.category_id


def test_get_product_not_found(
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="user")

    response = client.get(
        "/api/v1/products/9999",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 404
    assert response.json["message"] == "Product not found"


def test_get_product_no_token(
    client,
    products
):
    product = products[0]

    response = client.get(
        f"/api/v1/products/1"
    )

    assert response.status_code == 401
    assert response.json["msg"] == "Missing Authorization Header"


def test_get_product_invalid_token(
    client,
    products
):


    response = client.get(
        f"/api/v1/products/1",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "role",
    ["admin", "user", "staff", "manager"]
)
def test_get_product_allowed_roles(
    client,
    get_access_token,
    products,
    role
):
    access_token = get_access_token(role=role)

    product = Product.query.first()

    response = client.get(
        f"/api/v1/products/1",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json

    assert data["id"] == product.id


@pytest.mark.parametrize("product_index", [0, 1, 2])
def test_get_product_by_id(
    client,
    get_access_token,
    products,
    product_index
):
    access_token = get_access_token(role="user")

    product = Product.query.offset(product_index).first()

    response = client.get(
        f"/api/v1/products/{product.id}",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200
    assert response.json["id"] == product.id
    assert response.json["name"] == product.name





#================== Test create product   ==================
#================== Test create product   ==================





@pytest.mark.parametrize("role", ["admin", "manager"])
def test_create_product_success(
    client,
    get_access_token,
    category,
    role
):
    access_token = get_access_token(role=role)

    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Monitor",
            "description": "24 inch monitor",
            "price": 15000,
            "quantity": 20,
            "category_id": category[0][0]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 201

    data = response.json

    assert data["name"] == "Monitor"
    assert data["description"] == "24 inch monitor"
    assert data["price"] == 15000
    assert data["quantity"] == 20
    assert data["category_id"] == category[0][0]



def test_create_product_no_token(
    client,
    category
):
    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Monitor",
            "description": "24 inch monitor",
            "price": 15000,
            "quantity": 20,
            "category_id": category[0][0]
        }
    )

    assert response.status_code == 401
    assert response.json["msg"] == "Missing Authorization Header"


def test_create_product_invalid_token(
    client,
    category
):
    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Monitor",
            "description": "24 inch monitor",
            "price": 15000,
            "quantity": 20,
            "category_id": category[0][0]
        },
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 422


@pytest.mark.parametrize("role",["user", "staff"])
def test_create_product_user_forbidden(
    client,
    get_access_token,
    category,
    role
):
    access_token = get_access_token(role=role)

    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Monitor",
            "description": "24 inch monitor",
            "price": 15000,
            "quantity": 20,
            "category_id": category[0][0]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 403


def test_create_product_duplicate_name(
    client,
    get_access_token,
    products,
    category
):
    access_token = get_access_token(role="admin")

    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Laptop",
            "description": "Another laptop",
            "price": 60000,
            "quantity": 5,
            "category_id": category[0][0]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 409

    assert response.json["message"] == (
        "Product with this name already exists"
    )


def test_create_product_category_not_found(
    client,
    get_access_token
):
    access_token = get_access_token(role="admin")

    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Monitor",
            "description": "24 inch monitor",
            "price": 15000,
            "quantity": 20,
            "category_id": 99999
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 404

    assert response.json["message"] == (
        "Category not found. Create the category first."
    )


def test_create_product_missing_name(
    client,
    get_access_token,
    category
):
    access_token = get_access_token(role="admin")

    response = client.post(
        "/api/v1/products/",
        json={
            "description": "24 inch monitor",
            "price": 15000,
            "quantity": 20,
            "category_id": category[0][0]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422


def test_create_product_missing_price(
    client,
    get_access_token,
    category
):
    access_token = get_access_token(role="admin")

    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Monitor",
            "description": "24 inch monitor",
            "quantity": 20,
            "category_id": category[0][0]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422


def test_create_product_missing_quantity(
    client,
    get_access_token,
    category
):
    access_token = get_access_token(role="admin")

    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Monitor",
            "description": "24 inch monitor",
            "price": 15000,
            "category_id": category[0][0]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422


def test_create_product_missing_category_id(
    client,
    get_access_token
):
    access_token = get_access_token(role="admin")

    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Monitor",
            "description": "24 inch monitor",
            "price": 15000,
            "quantity": 20
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422


def test_create_product_negative_price(
    client,
    get_access_token,
    category
):
    access_token = get_access_token(role="admin")

    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Monitor",
            "description": "24 inch monitor",
            "price": -100,
            "quantity": 20,
            "category_id": category[0][0]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422


def test_create_product_negative_quantity(
    client,
    get_access_token,
    category
):
    access_token = get_access_token(role="admin")

    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Monitor",
            "description": "24 inch monitor",
            "price": 15000,
            "quantity": -5,
            "category_id": category[0][0]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422


def test_create_product_creates_inventory_log(
    app,
    client,
    get_access_token,
    category
):
    access_token = get_access_token(role="admin")

    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Projector",
            "description": "Office projector",
            "price": 40000,
            "quantity": 5,
            "category_id": category[0][0]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 201

    product_id = response.json["id"]

    with app.app_context():
        log = InventoryLog.query.filter_by(
            product_id=product_id
        ).first()

        assert log is not None
        assert log.change_type == "product created"
        assert log.quantity_changed == 5






#================== Test Update product   ==================
#================== Test Update product   ==================






@pytest.mark.parametrize("role", ["admin", "manager"])
def test_update_product_success_admin(
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

    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={
            "name": "Gaming Laptop",
            "price": 60000
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json

    assert data["name"] == "Gaming Laptop"
    assert data["price"] == 60000


def test_update_product_no_token(
    app,
    client,
    products
):
    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()

        product_id = product.id

    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={
            "price": 55000
        }
    )

    assert response.status_code == 401
    assert response.json["msg"] == "Missing Authorization Header"


def test_update_product_invalid_token(
    app,
    client,
    products
):
    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()

        product_id = product.id

    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={
            "price": 55000
        },
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 422


@pytest.mark.parametrize("role", ["user", "staff"])
def test_update_product_user_forbidden(
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

    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={
            "price": 55000
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 403


def test_update_product_not_found(
    client,
    get_access_token
):
    access_token = get_access_token(role="admin")

    response = client.patch(
        "/api/v1/products/99999",
        json={
            "price": 55000
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 404

    assert response.json["message"] == "Product not found"


def test_update_product_category(
    app,
    client,
    get_access_token,
    products,
    category
):
    access_token = get_access_token(role="admin")

    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()

        product_id = product.id

    furniture_id = category[0][1]

    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={
            "category_id": furniture_id
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    assert response.json["category_id"] == furniture_id


def test_update_product_category_not_found(
    app,
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="admin")

    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()

        product_id = product.id

    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={
            "category_id": 99999
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 404

    assert response.json["message"] == (
        "Category not found. Create the category first."
    )


def test_update_product_quantity_increase_creates_inventory_log(
    app,
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="admin")

    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()

        product_id = product.id

    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={
            "quantity": 15
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200
    assert response.json["quantity"] == 15

    with app.app_context():
        log = InventoryLog.query.filter_by(
            product_id=product_id,
            change_type="stock adjustment"
        ).first()

        assert log is not None
        assert log.quantity_changed == 5


def test_update_product_quantity_decrease_creates_inventory_log(
    app,
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="admin")

    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()

        product_id = product.id

    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={
            "quantity": 7
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200
    assert response.json["quantity"] == 7

    with app.app_context():
        log = InventoryLog.query.filter_by(
            product_id=product_id,
            change_type="stock adjustment"
        ).first()

        assert log is not None
        assert log.quantity_changed == -3


def test_update_product_same_quantity_does_not_create_inventory_log(
    app,
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="admin")

    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()

        product_id = product.id

        existing_logs = InventoryLog.query.filter_by(
            product_id=product_id,
            change_type="stock adjustment"
        ).count()

    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={
            "quantity": 10
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200
    assert response.json["quantity"] == 10

    with app.app_context():
        new_logs = InventoryLog.query.filter_by(
            product_id=product_id,
            change_type="stock adjustment"
        ).count()

        assert new_logs == existing_logs


def test_update_product_negative_quantity(
    app,
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="admin")

    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()

        product_id = product.id

    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={
            "quantity": -5
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422


def test_update_product_negative_price(
    app,
    client,
    get_access_token,
    products
):
    access_token = get_access_token(role="admin")

    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()

        product_id = product.id

    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={
            "price": -100
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422


def test_update_product_multiple_fields(
    app,
    client,
    get_access_token,
    products,
    category
):
    access_token = get_access_token(role="admin")

    with app.app_context():
        product = Product.query.filter_by(
            name="Laptop"
        ).first()

        product_id = product.id

    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={
            "name": "Gaming Laptop",
            "description": "High performance gaming laptop",
            "price": 75000,
            "quantity": 20,
            "category_id": category[0][1]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json

    assert data["name"] == "Gaming Laptop"
    assert data["description"] == "High performance gaming laptop"
    assert data["price"] == 75000
    assert data["quantity"] == 20
    assert data["category_id"] == category[0][1]







