from tests.conftest import register_and_login


def test_admin_can_create_common_user_in_same_tenant(client):
    tenant_id, tokens = register_and_login(client, "Users Tenant", "users@example.com")
    admin_headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    create_response = client.post(
        "/api/users",
        headers=admin_headers,
        json={"name": "Operator", "email": "operator@example.com", "password": "123456"},
    )
    assert create_response.status_code == 201
    created_user = create_response.json()
    user_id = created_user["id"]
    assert created_user["tenant_id"] == tenant_id
    assert created_user["created_by"] is not None
    assert created_user["role"] == "user"

    list_response = client.get("/api/users", headers=admin_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2
    assert all(user["tenant_id"] == tenant_id for user in list_response.json())

    update_response = client.put(f"/api/users/{user_id}", headers=admin_headers, json={"name": "Operator 2"})
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Operator 2"

    delete_response = client.delete(f"/api/users/{user_id}", headers=admin_headers)
    assert delete_response.status_code == 204


def test_common_user_cannot_create_users(client):
    _, admin_tokens = register_and_login(client, "Tenant Operator", "admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_tokens['access_token']}"}

    created_user = client.post(
        "/api/users",
        headers=admin_headers,
        json={"name": "Operator", "email": "operator2@example.com", "password": "123456"},
    )
    assert created_user.status_code == 201

    operator_login = client.post(
        "/api/auth/login",
        json={"email": "operator2@example.com", "password": "123456"},
    )
    operator_headers = {"Authorization": f"Bearer {operator_login.json()['access_token']}"}

    forbidden = client.post(
        "/api/users",
        headers=operator_headers,
        json={"name": "Blocked", "email": "blocked@example.com", "password": "123456"},
    )
    assert forbidden.status_code == 403


def test_users_are_isolated_between_tenants(client):
    tenant_a_id, tenant_a_tokens = register_and_login(client, "Tenant A Users", "a-users@example.com")
    _, tenant_b_tokens = register_and_login(client, "Tenant B Users", "b-users@example.com")

    create_user = client.post(
        "/api/users",
        headers={"Authorization": f"Bearer {tenant_a_tokens['access_token']}"},
        json={"name": "A User", "email": "shared@example.com", "password": "123456"},
    )
    assert create_user.status_code == 201
    assert create_user.json()["tenant_id"] == tenant_a_id

    list_tenant_b = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {tenant_b_tokens['access_token']}"},
    )
    assert list_tenant_b.status_code == 200
    assert len(list_tenant_b.json()) == 1
    assert all(user["email"] != "shared@example.com" for user in list_tenant_b.json())
