from typing import Sequence

from sqlalchemy.orm import Session

from backend.models.contact import Contact
from backend.models.message import Message
from backend.models.refresh_token import RefreshToken
from backend.models.tenant import Tenant
from backend.models.user import User


class TenantRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> Tenant:
        tenant = Tenant(**kwargs)
        self.db.add(tenant)
        self.db.flush()
        return tenant

    def get(self, tenant_id: int) -> Tenant | None:
        return self.db.query(Tenant).filter(Tenant.id == tenant_id).first()


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, tenant_id: int, email: str) -> User | None:
        return self.db.query(User).filter(User.tenant_id == tenant_id, User.email == email).first()

    def get_by_email_global(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def list(self, tenant_id: int) -> Sequence[User]:
        return self.db.query(User).filter(User.tenant_id == tenant_id).order_by(User.id.desc()).all()

    def get(self, tenant_id: int, user_id: int) -> User | None:
        return self.db.query(User).filter(User.tenant_id == tenant_id, User.id == user_id).first()

    def create(self, **kwargs) -> User:
        user = User(**kwargs)
        self.db.add(user)
        self.db.flush()
        return user


class ContactRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, tenant_id: int, owner_user_id: int | None = None) -> Sequence[Contact]:
        query = self.db.query(Contact).filter(Contact.tenant_id == tenant_id)
        if owner_user_id is not None:
            query = query.filter(Contact.owner_user_id == owner_user_id)
        return query.order_by(Contact.id.desc()).all()

    def get(self, tenant_id: int, contact_id: int) -> Contact | None:
        return self.db.query(Contact).filter(Contact.tenant_id == tenant_id, Contact.id == contact_id).first()

    def create(self, **kwargs) -> Contact:
        contact = Contact(**kwargs)
        self.db.add(contact)
        self.db.flush()
        return contact


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, tenant_id: int, user_id: int | None = None) -> Sequence[Message]:
        query = self.db.query(Message).filter(Message.tenant_id == tenant_id)
        if user_id is not None:
            query = query.filter(Message.user_id == user_id)
        return query.order_by(Message.id.desc()).all()

    def create(self, **kwargs) -> Message:
        message = Message(**kwargs)
        self.db.add(message)
        self.db.flush()
        return message


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> RefreshToken:
        token = RefreshToken(**kwargs)
        self.db.add(token)
        self.db.flush()
        return token

    def get_valid(self, raw_token: str) -> RefreshToken | None:
        return (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token == raw_token, RefreshToken.revoked_at.is_(None))
            .first()
        )
