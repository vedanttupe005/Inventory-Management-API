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


def test_register_duplicate_email(client):

    data = {
        "username": "testuser",
        "email": "test@user.com",
        "password": "testpassword"
    }

    response = client.post("api/v1/auth/register", json=data)

    assert response.status_code == 201

    response = client.post("api/v1/auth/register", json=data)

    assert response.status_code == 409

    response_data = response.get_json()

    print(response_data)
    assert response_data["message"] == "Email already registered"


    user = User.query.filter_by(email=data["email"]).all()

    assert len(user) == 1






def test_register_missing_username(client):
    data = {
        "email": "vedant@test.com",
        "password": "Password123"
    }

    response = client.post(
        "/api/v1/auth/register",
        json=data
    )

    assert response.status_code == 422

    response_data = response.get_json()

    assert "username" in response_data["errors"]["json"]

    user = User.query.filter_by(email=data["email"]).first()

    assert user is None






def test_register_missing_email(client):
    data = {
        "username": "Vedant",
        "password": "Password123"
    }

    response = client.post(
        "/api/v1/auth/register",
        json=data
    )

    assert response.status_code == 422

    response_data = response.get_json()

    assert "email" in response_data["errors"]["json"]

    user = User.query.filter_by(username=data["username"]).first()

    assert user is None





def test_register_missing_password(client):
    data = {
        "username": "Vedant",
        "email": "vedant@test.com"
    }

    response = client.post(
        "/api/v1/auth/register",
        json=data
    )

    assert response.status_code == 422

    response_data = response.get_json()

    assert "password" in response_data["errors"]["json"]

    user = User.query.filter_by(email=data["email"]).first()

    assert user is None






def test_register_invalid_email(client):
    data = {
        "username": "Vedant",
        "email": "invalid-email",
        "password": "Password123"
    }

    response = client.post(
        "/api/v1/auth/register",
        json=data
    )

    assert response.status_code == 422

    response_data = response.get_json()

    assert "email" in response_data["errors"]["json"]

    user = User.query.filter_by(username=data["username"]).first()

    assert user is None




#---------------------Login Tests---------------------
#---------------------Login Tests---------------------


def test_login_success(client):
    register_data = {
        "username": "Vedant",
        "email": "vedant@test.com",
        "password": "Password123"
    }

    # Register a user first
    response = client.post(
        "/api/v1/auth/register",
        json=register_data
    )

    assert response.status_code == 201

    # Login with the same credentials
    login_data = {
        "email": "vedant@test.com",
        "password": "Password123"
    }

    response = client.post(
        "/api/v1/auth/login",
        json=login_data
    )

    assert response.status_code == 200

    response_data = response.get_json()

    assert "access_token" in response_data
    assert response_data["access_token"]

    assert "refresh_token" in response_data
    assert response_data["refresh_token"]

    assert response_data["user"]["username"] == register_data["username"]
    assert response_data["user"]["email"] == register_data["email"]
    assert response_data["user"]["role"] == "user"

def test_login_user_not_found(client):
    data = {
        "email": "vedant@test.com",
        "password": "Password123"
    }

    response = client.post(
        "/api/v1/auth/login",
        json=data
    )

    assert response.status_code == 401

    response_data = response.get_json()

    assert response_data["message"] == "Invalid credentials: user not found"


def test_login_incorrect_password(client):
    register_data = {
        "username": "Vedant",
        "email": "vedant@test.com",
        "password": "Password123"
    }

    # Register the user
    response = client.post(
        "/api/v1/auth/register",
        json=register_data
    )

    assert response.status_code == 201

    # Login with an incorrect password
    login_data = {
        "email": "vedant@test.com",
        "password": "WrongPassword123"
    }

    response = client.post(
        "/api/v1/auth/login",
        json=login_data
    )

    assert response.status_code == 401

    response_data = response.get_json()

    assert response_data["message"] == "Invalid credentials: incorrect password"


def test_login_missing_email(client):
    data = {
        "password": "Password123"
    }

    response = client.post(
        "/api/v1/auth/login",
        json=data
    )

    assert response.status_code == 422

    response_data = response.get_json()

    assert "email" in response_data["errors"]["json"]



def test_login_missing_password(client):
    data = {
        "email": "vedant@test.com"
    }

    response = client.post(
        "/api/v1/auth/login",
        json=data
    )

    assert response.status_code == 422

    response_data = response.get_json()

    assert "password" in response_data["errors"]["json"]

def test_login_invalid_email(client):
    data = {
        "email": "invalid-email",
        "password": "Password123"
    }

    response = client.post(
        "/api/v1/auth/login",
        json=data
    )

    assert response.status_code == 422

    response_data = response.get_json()

    assert "email" in response_data["errors"]["json"]