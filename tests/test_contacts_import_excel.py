from io import BytesIO

import pandas as pd

from tests.conftest import register_and_login


def build_xlsx(rows):
    df = pd.DataFrame(rows)
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer


def test_import_contacts_xlsx_success(client):
    _, tokens = register_and_login(client, "Tenant Excel", "excel@demo.com")
    file_buffer = build_xlsx(
        [
            {"Nome": "Ana", "Telefone": "(11) 99999-1111", "Email": "ana@demo.com"},
            {"Nome": "Bruno", "Telefone": "11988887777"},
        ]
    )
    response = client.post(
        "/api/contacts/import",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        files={
            "file": (
                "contacts.xlsx",
                file_buffer.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["imported"] == 2
    assert payload["skipped"] == 0

    list_response = client.get(
        "/api/contacts",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2


def test_import_contacts_xlsx_skips_missing_phone(client):
    _, tokens = register_and_login(client, "Tenant Skip", "skip@demo.com")
    file_buffer = build_xlsx(
        [
            {"Nome": "Sem telefone", "Telefone": ""},
            {"Nome": "Com telefone", "Telefone": "21999998888"},
        ]
    )
    response = client.post(
        "/api/contacts/import",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        files={
            "file": (
                "contacts.xlsx",
                file_buffer.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["imported"] == 1
    assert payload["skipped"] == 1


def test_import_contacts_rejects_invalid_file(client):
    _, tokens = register_and_login(client, "Tenant Invalid", "invalid@demo.com")
    response = client.post(
        "/api/contacts/import",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        files={"file": ("contacts.txt", b"invalid", "text/plain")},
    )
    assert response.status_code == 400
