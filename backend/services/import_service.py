from __future__ import annotations

import re
from io import BytesIO
from typing import Any

from fastapi import UploadFile


def _normalize_header(value: Any) -> str:
    return re.sub(r"\s+", "", str(value or "")).lower()


def _normalize_text(raw_value: Any) -> str | None:
    try:
        import pandas as pd
    except ModuleNotFoundError as exc:
        raise ValueError("Missing pandas dependency") from exc

    if raw_value is None or (isinstance(raw_value, float) and pd.isna(raw_value)):
        return None
    value = str(raw_value).strip()
    return value or None


def read_contacts_spreadsheet(file: UploadFile):
    try:
        import pandas as pd
    except ModuleNotFoundError as exc:
        raise ValueError("Missing pandas dependency") from exc

    try:
        content = file.file.read()
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

    return df
