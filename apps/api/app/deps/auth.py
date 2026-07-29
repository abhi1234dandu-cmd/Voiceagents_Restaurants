from typing import Any, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from app.config import Settings, get_settings
from app.services.supabase_client import get_supabase

bearer = HTTPBearer(auto_error=False)


class AuthContext:
    def __init__(self, user_id: UUID, org_id: UUID, role: str, email: Optional[str] = None):
        self.user_id = user_id
        self.org_id = org_id
        self.role = role
        self.email = email


def decode_jwt(token: str, settings: Settings) -> dict[str, Any]:
    # Local/dev opaque tokens always win in development
    if token.startswith("dev:"):
        parts = token.split(":")
        if len(parts) >= 4:
            return {
                "sub": parts[1],
                "org_id": parts[2],
                "role": parts[3],
                "email": "dev@example.com",
            }
        raise HTTPException(status_code=401, detail="Malformed dev token")
    if not settings.supabase_jwt_secret or settings.supabase_jwt_secret.startswith("your-"):
        raise HTTPException(status_code=401, detail="JWT secret not configured")
    try:
        return jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
    settings: Settings = Depends(get_settings),
) -> AuthContext:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing auth")
    payload = decode_jwt(credentials.credentials, settings)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid subject")

    # Dev token shortcut — org comes from token, not membership lookup
    if credentials.credentials.startswith("dev:"):
        return AuthContext(
            user_id=UUID(payload["sub"]),
            org_id=UUID(payload["org_id"]),
            role=payload.get("role", "owner"),
            email=payload.get("email"),
        )

    sb = get_supabase()
    memberships = (
        sb.table("memberships")
        .select("org_id, role")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if not memberships.data:
        raise HTTPException(status_code=403, detail="No organization membership")
    m = memberships.data[0]
    return AuthContext(
        user_id=UUID(user_id),
        org_id=UUID(m["org_id"]),
        role=m["role"],
        email=payload.get("email"),
    )


async def require_internal(
    x_internal_secret: Optional[str] = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    if x_internal_secret != settings.internal_api_secret:
        raise HTTPException(status_code=401, detail="Invalid internal secret")


async def require_admin(auth: AuthContext = Depends(get_current_user), settings: Settings = Depends(get_settings)) -> AuthContext:
    if str(auth.user_id) not in settings.admin_ids and auth.role != "owner":
        # Platform admins must be listed; owners can access their own admin-lite later
        if str(auth.user_id) not in settings.admin_ids:
            raise HTTPException(status_code=403, detail="Platform admin required")
    if str(auth.user_id) not in settings.admin_ids:
        raise HTTPException(status_code=403, detail="Platform admin required")
    return auth


def assert_restaurant_org(restaurant: dict[str, Any], org_id: UUID) -> None:
    if UUID(restaurant["org_id"]) != org_id:
        raise HTTPException(status_code=404, detail="Restaurant not found")
