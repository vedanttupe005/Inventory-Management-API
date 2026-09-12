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



