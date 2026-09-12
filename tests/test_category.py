import pytest

#================Create Category Test================#
#================Create Category Test================#
def test_create_category_success(client, get_access_token):

    access_token = get_access_token(role="admin")

    response = client.post(
        "/api/v1/categories/",
        json={
            "name": "Electronics"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 201


def test_create_category_unauthorized(client, get_access_token):

    access_token = get_access_token(role="user")

    response = client.post(
        "/api/v1/categories/",
        json={
            "name": "Electronics"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 403


def test_create_category_missing_name(client, get_access_token):

    access_token = get_access_token(role="admin")

    response = client.post(
        "/api/v1/categories/",
        json={},
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422


def test_create_category_duplicate_name(client, get_access_token):

    access_token = get_access_token(role="admin")

    # First creation
    response1 = client.post(
        "/api/v1/categories/",
        json={
            "name": "Electronics"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response1.status_code == 201

    # Duplicate creation
    response2 = client.post(
        "/api/v1/categories/",
        json={
            "name": "Electronics"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response2.status_code == 409


def test_create_category_no_token(client):

    response = client.post(
        "/api/v1/categories/",
        json={
            "name": "Electronics"
        }
    )

    assert response.status_code == 401

def test_create_category_invalid_token(client):

    response = client.post(
        "/api/v1/categories/",
        json={
            "name": "Electronics"
        },
        headers={
            "Authorization": f"Bearer invalidtoken"
        }
    )

    assert response.status_code == 422




#================Get Category Test================#
#================Get Category Test================#

def test_get_categories_success(client, get_access_token):
    access_token = get_access_token(role="admin")

    # Create categories
    client.post(
        "/api/v1/categories/",
        json={"name": "Electronics"},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    client.post(
        "/api/v1/categories/",
        json={"name": "Clothing"},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    response = client.get(
        "/api/v1/categories/",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2
    assert data[0]["name"] == "Electronics"
    assert data[1]["name"] == "Clothing"


def test_get_categories_empty(client, get_access_token):
    access_token = get_access_token(role="admin")

    response = client.get(
        "/api/v1/categories/",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data == []


def test_get_categories_no_token(client):
    response = client.get("/api/v1/categories/")

    assert response.status_code == 401

    data = response.get_json()

    assert data["msg"] == "Missing Authorization Header"


def test_get_categories_invalid_token(client):
    response = client.get(
        "/api/v1/categories/",
        headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 422

    data = response.get_json()

    assert "msg" in data




@pytest.mark.parametrize(
    "role",
    ["admin", "user", "staff", "manager"]
)
def test_get_categories_allowed_roles(client, get_access_token, role):
    access_token = get_access_token(role=role)

    response = client.get(
        "/api/v1/categories/",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200


#================Get Category By ID Test================#
#================Get Category By ID Test================#


def test_get_category_success(client, get_access_token):
    access_token = get_access_token(role="admin")

    # Create category
    create_response = client.post(
        "/api/v1/categories/",
        json={"name": "Electronics"},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert create_response.status_code == 201

    category = create_response.get_json()
    category_id = category["id"]

    # Get category
    response = client.get(
        f"/api/v1/categories/{category_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == category_id
    assert data["name"] == "Electronics"


def test_get_category_not_found(client, get_access_token):
    access_token = get_access_token(role="admin")

    response = client.get(
        "/api/v1/categories/9",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 404

    data = response.get_json()
    print(data)
    assert data["message"] == "Category not found"



def test_get_category_no_token(client):
    response = client.get("/api/v1/categories/1")

    assert response.status_code == 401

    data = response.get_json()

    assert data["msg"] == "Missing Authorization Header"

def test_get_category_invalid_token(client):
    response = client.get(
        "/api/v1/categories/1",
        headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 422

    data = response.get_json()

    assert "msg" in data


@pytest.mark.parametrize(
    "role",
    ["admin", "user", "staff", "manager"]
)
def test_get_category_allowed_roles(client, get_access_token, role):

    admin_access = get_access_token(role="admin")

    # Create category
    create_response = client.post(
        "/api/v1/categories/",
        json={"name": "Electronics"},
        headers={"Authorization": f"Bearer {admin_access}"}
    )

    assert create_response.status_code == 201

    if role == "admin":
        access_token = admin_access
    else:
        access_token = get_access_token(role=role)
    category_id = create_response.get_json()["id"]

    # Get category
    response = client.get(
        f"/api/v1/categories/{category_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
