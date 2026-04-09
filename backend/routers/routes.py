import csv
from io import StringIO

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_context, get_current_user, get_db, require_admin
from backend.core.security import hash_password
from backend.core.tenant import TenantContext
from backend.models.contact import Contact
from backend.models.message import Message
from backend.models.tenant import Tenant
from backend.models.user import User
from backend.repositories.repositories import ContactRepository, MessageRepository, TenantRepository, UserRepository
from backend.schemas.schemas import (
    BulkMessageRequest,
    ContactCreate,
    ContactResponse,
    ContactUpdate,
    DashboardResponse,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    TenantRegister,
    UserCreateRequest,
    UserResponse,
    UserUpdate,
)
from backend.services.auth_service import AuthService
from backend.services.whatsapp_service import WhatsAppService

router_auth = APIRouter(prefix="/auth", tags=["auth"])
router_users = APIRouter(prefix="/users", tags=["users"])
router_contacts = APIRouter(prefix="/contacts", tags=["contacts"])
router_messages = APIRouter(prefix="/messages", tags=["messages"])
router_dashboard = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router_auth.post("/register")
def register(payload: TenantRegister, db: Session = Depends(get_db)):
    return AuthService(db).register_tenant(payload)


@router_auth.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return AuthService(db).login(payload)


@router_auth.post("/refresh")
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    return AuthService(db).refresh(payload.refresh_token)


@router_users.get("", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
    _: User = Depends(require_admin),
):
    return UserRepository(db).list(context.tenant_id)


@router_users.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreateRequest,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
    current_user: User = Depends(require_admin),
):
    repo = UserRepository(db)
    if repo.get_by_email(context.tenant_id, payload.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    user = repo.create(
        tenant_id=context.tenant_id,
        created_by=current_user.id,
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role="user",
        whatsapp=payload.whatsapp,
        is_active=True,
    )
    db.commit()
    db.refresh(user)
    return user


@router_users.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
    current_user: User = Depends(get_current_user),
):
    repo = UserRepository(db)
    user = repo.get(context.tenant_id, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.role != "admin" and current_user.id != user.id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    update_data = payload.model_dump(exclude_unset=True)
    if current_user.role != "admin":
        update_data.pop("role", None)
        update_data.pop("is_active", None)
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router_users.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
    _: User = Depends(require_admin),
):
    repo = UserRepository(db)
    user = repo.get(context.tenant_id, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()


@router_contacts.get("", response_model=list[ContactResponse])
def list_contacts(
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
    current_user: User = Depends(get_current_user),
):
    owner_filter = None if current_user.role == "admin" else current_user.id
    return ContactRepository(db).list(context.tenant_id, owner_filter)


@router_contacts.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    payload: ContactCreate,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
    current_user: User = Depends(get_current_user),
):
    owner_user_id = payload.owner_user_id if current_user.role == "admin" and payload.owner_user_id else current_user.id
    user = UserRepository(db).get(context.tenant_id, owner_user_id)
    if not user:
        raise HTTPException(status_code=400, detail="Owner user not found")
    contact = ContactRepository(db).create(
        tenant_id=context.tenant_id,
        owner_user_id=owner_user_id,
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        notes=payload.notes,
    )
    db.commit()
    db.refresh(contact)
    return contact


@router_contacts.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    payload: ContactUpdate,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
    current_user: User = Depends(get_current_user),
):
    repo = ContactRepository(db)
    contact = repo.get(context.tenant_id, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    if current_user.role != "admin" and contact.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    return contact


@router_contacts.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
    current_user: User = Depends(get_current_user),
):
    repo = ContactRepository(db)
    contact = repo.get(context.tenant_id, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    if current_user.role != "admin" and contact.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db.delete(contact)
    db.commit()


@router_contacts.post("/import-csv", response_model=list[ContactResponse])
def import_contacts_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
    current_user: User = Depends(get_current_user),
):
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(StringIO(content))
    repo = ContactRepository(db)
    created = []
    for row in reader:
        if not row.get("name") or not row.get("phone"):
            continue
        created.append(
            repo.create(
                tenant_id=context.tenant_id,
                owner_user_id=current_user.id,
                name=row["name"],
                phone=row["phone"],
                email=row.get("email"),
                notes=row.get("notes"),
            )
        )
    db.commit()
    for item in created:
        db.refresh(item)
    return created


@router_messages.get("", response_model=list[MessageResponse])
def list_messages(
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
    current_user: User = Depends(get_current_user),
    include_archived: bool = Query(default=False),
):
    user_filter = None if current_user.role == "admin" else current_user.id
    messages = MessageRepository(db).list(context.tenant_id, user_filter)
    if not include_archived:
        messages = [message for message in messages if message.status != "archived"]
    return messages


@router_messages.post("/clear", status_code=status.HTTP_200_OK)
def clear_message_history(
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Message).filter(
        Message.tenant_id == context.tenant_id,
        Message.user_id == current_user.id,
        Message.status != "archived",
    )
    updated = 0
    for message in query.all():
        message.status = "archived"
        updated += 1
    db.commit()
    return {"archived_count": updated}


@router_messages.post("/bulk", response_model=list[MessageResponse])
def send_bulk_messages(
    payload: BulkMessageRequest,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
    current_user: User = Depends(get_current_user),
):
    tenant = TenantRepository(db).get(context.tenant_id)
    if not tenant or not tenant.is_active:
        raise HTTPException(status_code=403, detail="Inactive tenant")
    if tenant.messages_used + len(payload.contact_ids) > tenant.message_limit:
        raise HTTPException(status_code=403, detail="Message limit exceeded")
    contacts = []
    for contact_id in payload.contact_ids:
        contact = ContactRepository(db).get(context.tenant_id, contact_id)
        if not contact:
            raise HTTPException(status_code=404, detail=f"Contact {contact_id} not found")
        if current_user.role != "admin" and contact.owner_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Cannot message this contact")
        contacts.append(contact)
    results = WhatsAppService().send_bulk(tenant, contacts, payload.content, payload.delay_seconds)
    repo = MessageRepository(db)
    saved = [
        repo.create(
            tenant_id=context.tenant_id,
            user_id=current_user.id,
            contact_id=result["contact_id"],
            phone=result["phone"],
            content=result["content"],
            status=result["status"],
            provider_message_id=result["provider_message_id"],
            error_message=result.get("error_message"),
            sent_at=result["sent_at"],
        )
        for result in results
    ]
    db.commit()
    for message in saved:
        db.refresh(message)
    return saved


@router_dashboard.get("", response_model=DashboardResponse)
def dashboard(
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
    current_user: User = Depends(get_current_user),
):
    tenant = TenantRepository(db).get(context.tenant_id)
    user_count = db.query(User).filter(User.tenant_id == context.tenant_id).count()
    contact_query = db.query(Contact).filter(Contact.tenant_id == context.tenant_id)
    message_query = db.query(Message).filter(Message.tenant_id == context.tenant_id)
    if current_user.role != "admin":
        contact_query = contact_query.filter(Contact.owner_user_id == current_user.id)
        message_query = message_query.filter(Message.user_id == current_user.id)
    return DashboardResponse(
        tenant_name=tenant.name if tenant else None,
        total_users=user_count if current_user.role == "admin" else 1,
        total_contacts=contact_query.count(),
        total_messages=message_query.count(),
        messages_used=tenant.messages_used if tenant else 0,
        message_limit=tenant.message_limit if tenant else 0,
    )
