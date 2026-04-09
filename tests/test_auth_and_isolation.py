from tests.conftest import register_and_login
from backend.core.security import decode_token


def test_auth_register_login_and_refresh(client):
    tenant_id, tokens = register_and_login(client, "Tenant Auth", "auth@example.com")
    assert tenant_id > 0
    assert "access_token" in tokens
    payload = decode_token(tokens["access_token"])
    assert payload["tenant_id"] == tenant_id
    assert payload["user_id"] > 0
    assert payload["role"] == "admin"
    refresh = client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh.status_code == 200
    assert "access_token" in refresh.json()


def test_login_without_tenant_id_and_invalid_password(client):
    tenant_id, _ = register_and_login(client, "Tenant Login", "login@example.com")
    assert tenant_id > 0

    valid_login = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "123456"},
    )
    assert valid_login.status_code == 200
    assert "tenant_id" not in valid_login.request.content.decode("utf-8")

    invalid_login = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "wrong-pass"},
    )
    assert invalid_login.status_code == 401
    assert invalid_login.json()["detail"] == "Invalid credentials"


def test_tenant_isolation_between_contacts(client):
    _, tenant_a = register_and_login(client, "Tenant A", "a@example.com")
    _, tenant_b = register_and_login(client, "Tenant B", "b@example.com")

    create_contact = client.post(
        "/api/contacts",
        headers={"Authorization": f"Bearer {tenant_a['access_token']}"},
        json={"name": "Alice", "phone": "+5511999999999"},
    )
    assert create_contact.status_code == 201
    contact_id = create_contact.json()["id"]

    forbidden = client.put(
        f"/api/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {tenant_b['access_token']}"},
        json={"name": "Hack"},
    )
    assert forbidden.status_code == 404
