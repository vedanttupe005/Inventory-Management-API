#====================== inventory log test ======================
#====================== inventory log test ======================
import pytest
from app.extensions import db
from app.model import InventoryLog


def test_get_inventory_logs(client, get_access_token):
    access_token = get_access_token(role="admin")

    response = client.get(
        "/api/v1/inventory/logs",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "page" in data
    assert "per_page" in data
    assert "total" in data
    assert "pages" in data
    assert "items" in data


def test_get_inventory_logs_unauthorized(client):
    response = client.get("/api/v1/inventory/logs")

    assert response.status_code == 401


@pytest.mark.parametrize("role", ["admin", "staff", "manager", "user"])
def test_get_inventory_logs_allowed_roles(client, get_access_token, role):
    access_token = get_access_token(role=role)

    response = client.get(
        "/api/v1/inventory/logs",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200



def test_get_inventory_logs_filter_by_product(client,get_access_token,inventory_logs):
    access_token = get_access_token(role="admin")

    product = inventory_logs["product1_id"]

    response = client.get(
        f"/api/v1/inventory/logs?product_id={product}",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["total"] == 2
    assert len(data["items"]) == 2

    for item in data["items"]:
        assert item["product_id"] == product


def test_get_inventory_logs_nonexistent_product(
    client,
    get_access_token
):
    access_token = get_access_token(role="admin")

    response = client.get(
        "/api/v1/inventory/logs?product_id=99999",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["total"] == 0
    assert data["items"] == []


def test_get_inventory_logs_without_product_filter(
    client,
    get_access_token,
    inventory_logs
):
    access_token = get_access_token(role="admin")

    response = client.get(
        "/api/v1/inventory/logs",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["total"] == 3
    assert len(data["items"]) == 3

def test_get_inventory_logs_pagination(
    client,
    get_access_token,
    inventory_logs
):
    access_token = get_access_token(role="admin")

    response = client.get(
        "/api/v1/inventory/logs?page=1&limit=2",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["page"] == 1
    assert data["per_page"] == 2
    assert data["total"] == 3
    assert data["pages"] == 2
    assert len(data["items"]) == 2


def test_get_inventory_logs_second_page(
    client,
    get_access_token,
    inventory_logs
):
    access_token = get_access_token(role="admin")

    response = client.get(
        "/api/v1/inventory/logs?page=2&limit=2",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["page"] == 2
    assert data["per_page"] == 2
    assert data["total"] == 3
    assert data["pages"] == 2
    assert len(data["items"]) == 1


def test_get_inventory_logs_page_out_of_range(
    client,
    get_access_token,
    inventory_logs
):
    access_token = get_access_token(role="admin")

    response = client.get(
        "/api/v1/inventory/logs?page=100&limit=10",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["items"] == []
    assert data["total"] == 3


def test_get_inventory_logs_default_pagination(
    client,
    get_access_token,
    inventory_logs
):
    access_token = get_access_token(role="admin")

    response = client.get(
        "/api/v1/inventory/logs",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["page"] == 1
    assert data["per_page"] == 10


from datetime import datetime, timedelta


def test_get_inventory_logs_ordered_by_latest_first(
    client,
    get_access_token,
    inventory_logs,
    app
):
    with app.app_context():
        # getting the newest log entry based on timestamp
        logs = InventoryLog.query.order_by(InventoryLog.timestamp.desc()).first()

        log_id = logs.id

        db.session.commit()




    access_token = get_access_token(role="admin")

    response = client.get(
        "/api/v1/inventory/logs",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["items"][0]["id"] == log_id


