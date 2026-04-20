from tests.conftest import register_and_login


def test_import_contacts_xml_success(client):
    _, tokens = register_and_login(client, "Tenant XML", "xml@demo.com")

    xml_content = """
    <contacts>
      <contact>
        <name>Ana Demo</name>
        <phone>(11) 99999-1111</phone>
      </contact>
      <contact>
        <name>Bruno Demo</name>
        <phone>+55 (11) 98888-2222</phone>
        <phone>11 97777-3333</phone>
      </contact>
    </contacts>
    """.strip().encode("utf-8")

    response = client.post(
        "/api/contacts/import",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        files={"file": ("contacts.xml", xml_content, "application/xml")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["imported"] == 3
    assert payload["skipped"] == 0

    list_response = client.get(
        "/api/contacts",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert list_response.status_code == 200
    assert len(list_response.json()) == 3
