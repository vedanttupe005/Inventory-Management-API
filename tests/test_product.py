#================== Get products with searching,sorting,pagination, filtering ==================
#================== Get products with searching,sorting,pagination, filtering ==================
import pytest
from app.model import Product


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


