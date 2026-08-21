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