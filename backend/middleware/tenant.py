from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.tenant import current_role, current_tenant_id, current_user_id


class TenantContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        token_tenant = current_tenant_id.set(None)
        token_user = current_user_id.set(None)
        token_role = current_role.set(None)
        context = getattr(request.state, "tenant_context", None)
        if context:
            current_tenant_id.set(context.tenant_id)
            current_user_id.set(context.user_id)
            current_role.set(context.role)
        response = await call_next(request)
        current_tenant_id.reset(token_tenant)
        current_user_id.reset(token_user)
        current_role.reset(token_role)
        return response
