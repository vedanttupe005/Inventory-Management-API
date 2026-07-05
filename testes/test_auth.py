from app.model.user import User

def test_register_success(client):
    data = {
        "username": "testuser",
        "email":"test@user.com",
        "password": "testpassword"
    }

    response = client.post("api/v1/auth/register", json=data)

    assert response.status_code == 201

    response_data = response.get_json()

    assert response_data["username"] == data["username"]
    assert response_data["email"] == data["email"]

    user = User.query.filter_by(email=data["email"]).first()

    assert user is not None

    assert user.check_password(data["password"])