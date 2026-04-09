from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from backend.models.refresh_token import RefreshToken
from backend.models.user import User
from backend.repositories.repositories import RefreshTokenRepository, TenantRepository, UserRepository
from backend.schemas.schemas import LoginRequest, TenantRegister, TokenResponse


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.tenants = TenantRepository(db)
        self.users = UserRepository(db)
        self.refresh_tokens = RefreshTokenRepository(db)

    def register_tenant(self, payload: TenantRegister) -> dict:
        tenant = self.tenants.create(
            name=payload.company_name,
            plan=payload.plan,
            message_limit=settings.default_message_limit,
            messages_used=0,
            is_active=True,
        )
        user = self.users.create(
            tenant_id=tenant.id,
            created_by=None,
            name=payload.admin_name,
            email=payload.admin_email,
            password_hash=hash_password(payload.password),
            role="admin",
            whatsapp=payload.whatsapp,
            is_active=True,
        )
        self.db.commit()
        self.db.refresh(tenant)
        self.db.refresh(user)
        return {"tenant_id": tenant.id, "admin_user_id": user.id}

    def login(self, payload: LoginRequest) -> TokenResponse:
        # Future improvement: if a single email can belong to multiple tenants,
        # this login flow should add an explicit tenant discovery/selection step.
        user = self.users.get_by_email_global(payload.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        now = datetime.now(timezone.utc)
        blocked_until = user.blocked_until
        if blocked_until and blocked_until.tzinfo is None:
            blocked_until = blocked_until.replace(tzinfo=timezone.utc)
        if blocked_until and blocked_until > now:
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="User temporarily blocked")
        if not verify_password(payload.password, user.password_hash):
            user.login_attempts += 1
            if user.login_attempts >= 5:
                user.blocked_until = now + timedelta(seconds=5)
                user.login_attempts = 0
            self.db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        user.login_attempts = 0
        user.blocked_until = None
        refresh_raw = create_refresh_token()
        self.refresh_tokens.create(
            tenant_id=user.tenant_id,
            user_id=user.id,
            token=refresh_raw,
            expires_at=now + timedelta(days=settings.refresh_token_expire_days),
        )
        access = create_access_token({"user_id": user.id, "tenant_id": user.tenant_id, "role": user.role})
        self.db.commit()
        return TokenResponse(access_token=access, refresh_token=refresh_raw)

    def refresh(self, raw_token: str) -> TokenResponse:
        token = self.refresh_tokens.get_valid(raw_token)
        now = datetime.now(timezone.utc)
        expires_at = token.expires_at if token else None
        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if not token or not expires_at or expires_at < now:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        user = self.db.query(User).filter(User.id == token.user_id, User.tenant_id == token.tenant_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        token.revoked_at = now
        new_refresh = create_refresh_token()
        self.refresh_tokens.create(
            tenant_id=user.tenant_id,
            user_id=user.id,
            token=new_refresh,
            expires_at=now + timedelta(days=settings.refresh_token_expire_days),
        )
        access = create_access_token({"user_id": user.id, "tenant_id": user.tenant_id, "role": user.role})
        self.db.commit()
        return TokenResponse(access_token=access, refresh_token=new_refresh)
