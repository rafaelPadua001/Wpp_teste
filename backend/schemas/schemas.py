from datetime import datetime

from backend.services.import_service import normalize_email

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TenantRegister(BaseModel):
    company_name: str = Field(min_length=2, max_length=150)
    plan: str = "basic"
    admin_name: str = Field(min_length=2, max_length=120)
    admin_email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    whatsapp: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserBase(BaseModel):
    name: str
    email: EmailStr
    whatsapp: str | None = None


class UserCreateRequest(UserBase):
    password: str = Field(min_length=6)


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    whatsapp: str | None = None
    password: str | None = Field(default=None, min_length=6)
    role: str | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tenant_id: int
    created_by: int | None
    role: str
    is_active: bool
    created_at: datetime


class ContactBase(BaseModel):
    name: str
    phone: str
    email: str | None = None
    notes: str | None = None

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, value):
        return normalize_email(value)


class ContactCreate(ContactBase):
    owner_user_id: int | None = None


class ContactUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    notes: str | None = None

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, value):
        return normalize_email(value)


class ContactResponse(ContactBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tenant_id: int
    owner_user_id: int
    created_at: datetime


class ContactClearRequest(BaseModel):
    contact_ids: list[int] = Field(default_factory=list)


class BulkMessageRequest(BaseModel):
    content: str = Field(min_length=1)
    contact_ids: list[int] = Field(default_factory=list)
    delay_seconds: float = Field(default=0, ge=0, le=5)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tenant_id: int
    user_id: int | None
    contact_id: int | None
    phone: str
    content: str
    status: str
    error_message: str | None
    provider_message_id: str | None
    created_at: datetime
    sent_at: datetime | None


class DashboardResponse(BaseModel):
    tenant_name: str | None = None
    total_users: int
    total_contacts: int
    total_messages: int
    messages_used: int
    message_limit: int
