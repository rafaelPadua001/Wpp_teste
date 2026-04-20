from __future__ import annotations

import quopri
import re
from collections.abc import Iterable
from io import BytesIO
from typing import Any
from xml.etree import ElementTree as ET

from fastapi import UploadFile

_NAME_KEYS = {"name", "nome", "fn", "fullname", "full_name"}
_PHONE_KEYS = {"phone", "telefone", "celular", "whatsapp", "mobile", "fone", "tel", "telefone1", "telefone2", "phone1", "phone2"}
_EMAIL_KEYS = {"email", "e-mail", "mail"}
_NOTES_KEYS = {"notes", "notas", "obs", "observacao", "observações", "observacoes"}
_XML_ROW_TAGS = {"contact", "contato", "item", "row", "record", "person"}


def _normalize_header(value: Any) -> str:
    return re.sub(r"\s+", "", str(value or "")).lower()


def _normalize_field_key(value: Any) -> str:
    normalized = _normalize_header(value).replace("_", "")
    if "}" in normalized:
        normalized = normalized.rsplit("}", 1)[-1]
    if ":" in normalized:
        normalized = normalized.rsplit(":", 1)[-1]
    return normalized


def _normalize_text(raw_value: Any) -> str | None:
    try:
        import pandas as pd
    except ModuleNotFoundError as exc:
        raise ValueError("Missing pandas dependency") from exc

    if raw_value is None or (isinstance(raw_value, float) and pd.isna(raw_value)):
        return None
    value = str(raw_value).strip()
    return value or None


def decode_upload_content(raw: bytes) -> str:
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="ignore")


def normalize_email(email: Any) -> str | None:
    if email is None:
        return None

    value = str(email).strip()
    if not value:
        return None

    if value.lower() in {"n", "na", "none", "-", "null", ""}:
        return None

    if "@" not in value:
        return None

    return value


def _normalize_phone(raw_value: Any) -> str | None:
    value = str(raw_value or "").strip()
    if not value:
        return None
    digits = re.sub(r"\D", "", value)
    return digits or None


def _first_matching_value(data: dict[str, Any], keys: Iterable[str]) -> str | None:
    for key, value in data.items():
        normalized = _normalize_field_key(key)
        if normalized in keys:
            text = _normalize_text(value)
            if text:
                return text
    return None


def _collect_matching_values(data: dict[str, Any], keys: Iterable[str]) -> list[str]:
    values: list[str] = []
    for key, value in data.items():
        normalized = _normalize_field_key(key)
        if normalized in keys:
            if isinstance(value, (list, tuple, set)):
                for item in value:
                    text = _normalize_text(item)
                    if text:
                        values.append(text)
                continue
            text = _normalize_text(value)
            if text:
                values.append(text)
    return values


def _strip_ignored_vcard_fields(content: str) -> str:
    ignored_prefixes = ("PHOTO", "LOGO", "SOUND", "KEY", "AGENT")
    filtered_lines: list[str] = []
    skipping_block = False

    for line in content.splitlines():
        if skipping_block:
            if line.startswith((" ", "\t")):
                continue
            skipping_block = False

        normalized = line.lstrip().upper()
        if any(normalized.startswith(prefix) for prefix in ignored_prefixes):
            skipping_block = True
            continue

        filtered_lines.append(line)

    return "\n".join(filtered_lines)


def _unfold_vcard_lines(content: str) -> list[str]:
    unfolded_lines: list[str] = []
    for raw_line in content.splitlines():
        if raw_line.startswith((" ", "\t")) and unfolded_lines:
            unfolded_lines[-1] += raw_line[1:]
        else:
            unfolded_lines.append(raw_line.rstrip("\r"))
    return unfolded_lines


def _decode_vcard_value(raw_key: str, raw_value: str) -> str:
    key_upper = raw_key.upper()
    value = raw_value.strip()
    if "ENCODING=QUOTED-PRINTABLE" in key_upper:
        value = quopri.decodestring(value).decode("utf-8", errors="ignore").strip()
    value = value.replace("=3D", "=")
    return value

def parse_vcf(content: str) -> list[dict[str, str | None]]:
    contacts: list[dict[str, str | None]] = []
    current: dict[str, str | list[str] | None] = {}

    for line in _unfold_vcard_lines(_strip_ignored_vcard_fields(content)):
        line = line.strip()
        if not line:
            continue

        upper_line = line.upper()
        if upper_line.startswith("BEGIN:VCARD"):
            current = {}
            continue

        if upper_line.startswith("END:VCARD"):
            for phone_value in current.get("phones", []) or []:
                normalized_phone = _normalize_phone(phone_value)
                if normalized_phone:
                    contacts.append(
                        {
                            "name": current.get("name") or "Sem nome",
                            "phone": normalized_phone,
                            "email": current.get("email"),
                            "notes": None,
                        }
                    )
            current = {}
            continue

        if ":" not in line:
            continue

        raw_key, raw_value = line.split(":", 1)
        decoded_value = _decode_vcard_value(raw_key, raw_value)
        key_name = raw_key.split(";", 1)[0].strip().upper()

        if key_name == "FN":
            current["name"] = decoded_value or "Sem nome"
            continue

        if key_name == "TEL":
            phone = _normalize_phone(decoded_value)
            if phone:
                phones = current.setdefault("phones", [])
                if isinstance(phones, list):
                    phones.append(phone)
            continue

        if key_name == "EMAIL":
            current["email"] = normalize_email(decoded_value)
            continue

    return contacts


def _records_from_mapping(data: dict[str, Any]) -> list[dict[str, str | None]]:
    name = _first_matching_value(data, _NAME_KEYS) or "Sem nome"
    phones = _collect_matching_values(data, _PHONE_KEYS)
    email = normalize_email(_first_matching_value(data, _EMAIL_KEYS))
    notes = _first_matching_value(data, _NOTES_KEYS)

    records: list[dict[str, str | None]] = []
    for phone in phones:
        normalized_phone = _normalize_phone(phone)
        if not normalized_phone:
            continue
        records.append(
            {
                "name": name,
                "phone": normalized_phone,
                "email": email,
                "notes": notes,
            }
        )
    return records


def parse_spreadsheet_content(content: bytes):
    try:
        import pandas as pd
    except ModuleNotFoundError as exc:
        raise ValueError("Missing pandas dependency") from exc

    try:
        df = pd.read_excel(BytesIO(content))
    except Exception as exc:
        raise ValueError("Unable to parse spreadsheet") from exc

    header_map = {
        "nome": "name",
        "name": "name",
        "telefone": "phone",
        "phone": "phone",
        "celular": "phone",
        "whatsapp": "phone",
        "email": "email",
        "e-mail": "email",
        "mail": "email",
        "observacao": "notes",
        "observações": "notes",
        "obs": "notes",
        "notas": "notes",
        "notes": "notes",
    }
    column_rename = {}
    for column in df.columns:
        normalized = _normalize_header(column)
        if normalized in header_map:
            column_rename[column] = header_map[normalized]
    df = df.rename(columns=column_rename)

    for field in ("name", "email", "notes"):
        if field in df.columns:
            df[field] = df[field].apply(_normalize_text)

    if "email" in df.columns:
        df["email"] = df["email"].apply(normalize_email)

    return df


def read_contacts_spreadsheet(file: UploadFile):
    content = file.file.read()
    return parse_spreadsheet_content(content)


def parse_xml(content: str) -> list[dict[str, str | None]]:
    content = content.strip()
    if not content:
        return []

    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        raise ValueError("Unable to parse XML file") from exc

    row_nodes: list[ET.Element] = []
    for element in root.iter():
        if element is root:
            continue
        if _normalize_field_key(element.tag) in _XML_ROW_TAGS:
            row_nodes.append(element)

    if not row_nodes:
        for element in root.iter():
            if element is root or not list(element):
                continue
            if any(list(child) for child in element):
                continue
            row_nodes.append(element)
        if not row_nodes:
            row_nodes = [root]

    contacts: list[dict[str, str | None]] = []
    for node in row_nodes:
        flat: dict[str, Any] = {}
        for descendant in node.iter():
            if descendant is node or list(descendant):
                continue
            text = _normalize_text(descendant.text)
            if not text:
                continue
            key = descendant.tag
            current = flat.get(key)
            if current is None:
                flat[key] = text
            elif isinstance(current, list):
                current.append(text)
            else:
                flat[key] = [current, text]
        records = _records_from_mapping(flat)
        contacts.extend(records)

    return contacts
