import logging
import time
from datetime import datetime, timezone
from typing import Any

import requests

from backend.core.config import settings
from backend.models.contact import Contact
from backend.models.tenant import Tenant

logger = logging.getLogger(__name__)


class WhatsAppService:
    def __init__(self) -> None:
        self.base_url = (
            f"{settings.whatsapp_base_url}/"
            f"{settings.whatsapp_api_version}/"
            f"{settings.whatsapp_phone_number_id}/messages"
        )

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {settings.whatsapp_access_token}",
            "Content-Type": "application/json",
        }

    def _parse_response(self, response: requests.Response) -> dict[str, Any]:
        try:
            data = response.json()
        except ValueError:
            logger.exception("whatsapp.invalid_response")
            return {
                "status": "failed",
                "provider_message_id": None,
                "error": "Invalid response from WhatsApp API",
            }

        logger.info(
            "whatsapp.api_response",
            extra={"status_code": response.status_code, "response": data},
        )

        if response.status_code != 200:
            error_payload = data.get("error", data)
            error_message = self._extract_error_message(error_payload)
            logger.warning(
                "whatsapp.send_failed",
                extra={"status_code": response.status_code, "error": error_payload},
            )
            return {
                "status": "failed",
                "provider_message_id": None,
                "error": error_message,
                "details": error_payload,
            }

        provider_message_id = data.get("messages", [{}])[0].get("id")
        logger.info("whatsapp.send_success", extra={"provider_message_id": provider_message_id})
        return {
            "status": "sent",
            "provider_message_id": provider_message_id,
            "error": None,
            "details": data,
        }

    def _extract_error_message(self, error_payload: Any) -> str:
        if isinstance(error_payload, dict):
            code = error_payload.get("code")
            message = error_payload.get("message")
            if code == 190:
                return "WhatsApp authentication failed"
            if code in {100, 131009}:
                return "Invalid WhatsApp destination number"
            if code in {4, 80007, 130429}:
                return "WhatsApp rate limit reached"
            if message:
                return str(message)
        return "WhatsApp API request failed"

    def send_message(self, phone: str, content: str) -> dict[str, Any]:
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"body": content},
        }
        try:
            response = requests.post(self.base_url, json=payload, headers=self._headers(), timeout=30)
        except requests.RequestException as exc:
            logger.exception("whatsapp.request_exception")
            return {
                "status": "failed",
                "provider_message_id": None,
                "error": str(exc),
            }
        return self._parse_response(response)

    def send_template_message(self, phone: str) -> dict[str, Any]:
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": "hello_world",
                "language": {"code": "en_US"},
            },
        }
        try:
            response = requests.post(self.base_url, json=payload, headers=self._headers(), timeout=30)
        except requests.RequestException as exc:
            logger.exception("whatsapp.template_request_exception")
            return {
                "status": "failed",
                "provider_message_id": None,
                "error": str(exc),
            }
        return self._parse_response(response)

    def send(self, phone: str, message: str) -> dict[str, Any]:
        if settings.whatsapp_test_mode:
            return self.send_template_message(phone)
        return self.send_message(phone, message)

    def send_bulk(self, tenant: Tenant, contacts: list[Contact], content: str, delay_seconds: float = 0) -> list[dict]:
        results = []
        for contact in contacts:
            if delay_seconds:
                time.sleep(delay_seconds)
            response = self.send(contact.phone, content)
            results.append(
                {
                    "contact_id": contact.id,
                    "phone": contact.phone,
                    "content": content,
                    "status": response["status"],
                    "provider_message_id": response.get("provider_message_id"),
                    "error_message": response.get("error"),
                    "sent_at": datetime.now(timezone.utc) if response["status"] == "sent" else None,
                }
            )
        tenant.messages_used += sum(1 for result in results if result["status"] == "sent")
        return results
