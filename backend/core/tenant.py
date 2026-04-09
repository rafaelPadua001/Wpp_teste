from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional

current_tenant_id: ContextVar[Optional[int]] = ContextVar("current_tenant_id", default=None)
current_user_id: ContextVar[Optional[int]] = ContextVar("current_user_id", default=None)
current_role: ContextVar[Optional[str]] = ContextVar("current_role", default=None)


@dataclass
class TenantContext:
    tenant_id: int
    user_id: int
    role: str
