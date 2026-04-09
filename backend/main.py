from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.core.config import settings
from backend.middleware.tenant import TenantContextMiddleware
from backend.routers.routes import router_auth, router_contacts, router_dashboard, router_messages, router_users

app = FastAPI(title=settings.app_name)
app.add_middleware(TenantContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

app.include_router(router_auth, prefix="/api")
app.include_router(router_users, prefix="/api")
app.include_router(router_contacts, prefix="/api")
app.include_router(router_messages, prefix="/api")
app.include_router(router_dashboard, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
