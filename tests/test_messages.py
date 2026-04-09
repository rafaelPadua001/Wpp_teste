from unittest.mock import Mock, patch

from backend.services.whatsapp_service import WhatsAppService
from tests.conftest import register_and_login


def make_response(status_code: int, payload: dict):
    response = Mock()
    response.status_code = status_code
    response.json.return_value = payload
    return response


@patch("backend.services.whatsapp_service.requests.post")
def test_whatsapp_service_sends_template_in_test_mode(mock_post):
    mock_post.return_value = make_response(200, {"messages": [{"id": "wamid.123"}]})

    service = WhatsAppService()
    result = service.send("+5511999999999", "Oferta da semana")

    assert result["status"] == "sent"
    assert result["provider_message_id"] == "wamid.123"
    payload = mock_post.call_args.kwargs["json"]
    assert payload["type"] == "template"
    assert payload["template"]["name"] == "hello_world"


@patch("backend.services.whatsapp_service.requests.post")
def test_whatsapp_service_handles_api_error(mock_post):
    mock_post.return_value = make_response(
        400,
        {"error": {"message": "Unsupported post request", "code": 100}},
    )

    service = WhatsAppService()
    result = service.send("+5511999999999", "Oferta da semana")

    assert result["status"] == "failed"
    assert result["provider_message_id"] is None
    assert result["error"] == "Invalid WhatsApp destination number"


@patch("backend.services.whatsapp_service.requests.post")
def test_contacts_crud_and_bulk_messages(mock_post, client):
    mock_post.return_value = make_response(200, {"messages": [{"id": "wamid.bulk"}]})

    _, tokens = register_and_login(client, "Contacts Tenant", "contacts@example.com")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    first = client.post("/api/contacts", headers=headers, json={"name": "Ana", "phone": "+5511988881111"})
    second = client.post("/api/contacts", headers=headers, json={"name": "Bia", "phone": "+5511977772222"})
    assert first.status_code == 201
    assert second.status_code == 201

    list_response = client.get("/api/contacts", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2

    bulk_response = client.post(
        "/api/messages/bulk",
        headers=headers,
        json={
            "contact_ids": [first.json()["id"], second.json()["id"]],
            "content": "Oferta da semana",
            "delay_seconds": 0,
        },
    )
    assert bulk_response.status_code == 200
    assert len(bulk_response.json()) == 2
    assert bulk_response.json()[0]["provider_message_id"] == "wamid.bulk"

    dashboard = client.get("/api/dashboard", headers=headers)
    assert dashboard.status_code == 200
    assert dashboard.json()["total_contacts"] == 2
    assert dashboard.json()["total_messages"] == 2
    assert dashboard.json()["tenant_name"] == "Contacts Tenant"


@patch("backend.services.whatsapp_service.requests.post")
def test_clear_history_only_archives_logged_user_messages(mock_post, client):
    mock_post.return_value = make_response(200, {"messages": [{"id": "wamid.clear"}]})

    _, admin_tokens = register_and_login(client, "History Tenant", "history-admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_tokens['access_token']}"}

    user_response = client.post(
        "/api/users",
        headers=admin_headers,
        json={"name": "Operator", "email": "history-user@example.com", "password": "123456"},
    )
    assert user_response.status_code == 201

    login_user = client.post(
        "/api/auth/login",
        json={"email": "history-user@example.com", "password": "123456"},
    )
    user_headers = {"Authorization": f"Bearer {login_user.json()['access_token']}"}

    admin_contact = client.post("/api/contacts", headers=admin_headers, json={"name": "Admin Contact", "phone": "+5511911111111"})
    user_contact = client.post("/api/contacts", headers=user_headers, json={"name": "User Contact", "phone": "+5511922222222"})
    assert admin_contact.status_code == 201
    assert user_contact.status_code == 201

    admin_send = client.post(
        "/api/messages/bulk",
        headers=admin_headers,
        json={"contact_ids": [admin_contact.json()["id"]], "content": "Admin send", "delay_seconds": 0},
    )
    user_send = client.post(
        "/api/messages/bulk",
        headers=user_headers,
        json={"contact_ids": [user_contact.json()["id"]], "content": "User send", "delay_seconds": 0},
    )
    assert admin_send.status_code == 200
    assert user_send.status_code == 200

    clear_response = client.post("/api/messages/clear", headers=user_headers)
    assert clear_response.status_code == 200
    assert clear_response.json()["archived_count"] == 1

    user_messages = client.get("/api/messages", headers=user_headers)
    admin_messages = client.get("/api/messages", headers=admin_headers)
    assert user_messages.status_code == 200
    assert admin_messages.status_code == 200
    assert user_messages.json() == []
    assert len(admin_messages.json()) == 1
