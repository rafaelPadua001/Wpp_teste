from datetime import datetime, timedelta, timezone

from tests.conftest import register_and_login
from backend.models.contact import Contact


def create_contact(client, token, name="Contato", phone="5511999999999"):
    response = client.post(
        "/api/contacts",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": name, "phone": phone, "email": None, "notes": "Obs"},
    )
    assert response.status_code == 201
    return response.json()


def test_clear_and_recover_contacts(client):
    _, tokens = register_and_login(client, "Tenant Clear", "clear@demo.com")
    token = tokens["access_token"]

    contact_1 = create_contact(client, token, name="Contato 1", phone="5511990000001")
    create_contact(client, token, name="Contato 2", phone="5511990000002")

    clear_response = client.post(
        "/api/contacts/clear",
        headers={"Authorization": f"Bearer {token}"},
        json={"contact_ids": [contact_1["id"]]},
    )
    assert clear_response.status_code == 200

    list_response = client.get(
        "/api/contacts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    recover_response = client.post(
        "/api/contacts/recover",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert recover_response.status_code == 200

    recovered_list = client.get(
        "/api/contacts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert recovered_list.status_code == 200
    assert len(recovered_list.json()) == 2


def test_clear_contacts_no_ids_is_noop(client):
    _, tokens = register_and_login(client, "Tenant Clear Noop", "clear-noop@demo.com")
    token = tokens["access_token"]

    create_contact(client, token, name="Contato 1", phone="5511990000101")

    clear_response = client.post(
        "/api/contacts/clear",
        headers={"Authorization": f"Bearer {token}"},
        json={"contact_ids": []},
    )
    assert clear_response.status_code == 200

    list_response = client.get(
        "/api/contacts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_recover_skips_expired_contacts(client, db_session):
    _, tokens = register_and_login(client, "Tenant Expired", "expired@demo.com")
    token = tokens["access_token"]

    contact_payload = create_contact(client, token, name="Contato Expirado", phone="5511990000003")

    db_contact = (
        db_session.query(Contact)
        .filter(Contact.id == contact_payload["id"])
        .first()
    )
    db_contact.is_deleted = True
    db_contact.deleted_at = datetime.now(timezone.utc) - timedelta(hours=49)
    db_session.commit()

    recover_response = client.post(
        "/api/contacts/recover",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert recover_response.status_code == 200

    list_response = client.get(
        "/api/contacts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    assert list_response.json() == []
