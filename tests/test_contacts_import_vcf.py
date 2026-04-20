from tests.conftest import register_and_login


def test_import_contacts_vcf_success(client):
    _, tokens = register_and_login(client, "Tenant VCF", "vcf@demo.com")

    vcf_content = (
        "BEGIN:VCARD\r\n"
        "VERSION:3.0\r\n"
        "FN:Ana Demo\r\n"
        "TEL;TYPE=CELL:+55 (11) 99999-1111\r\n"
        "TEL;TYPE=HOME:(11) 98888-2222\r\n"
        "PHOTO;ENCODING=b;TYPE=PNG:iVBORw0KGgoAAAANSUhEUgAAAAUA\r\n"
        "END:VCARD\r\n"
        "BEGIN:VCARD\r\n"
        "VERSION:3.0\r\n"
        "FN:Bruno Demo\r\n"
        "TEL;TYPE=CELL:11 98888-7777\r\n"
        "END:VCARD\r\n"
    ).encode("utf-8")

    response = client.post(
        "/api/contacts/import",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        files={"file": ("contacts.vcf", vcf_content, "text/vcard")},
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
