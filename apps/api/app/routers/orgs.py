from uuid import UUID

from fastapi import APIRouter, Depends

from app.deps.auth import AuthContext, get_current_user
from app.models.schemas import Organization, OrganizationCreate
from app.services.repository import Repository

router = APIRouter(prefix="/v1/orgs", tags=["orgs"])


@router.post("", response_model=Organization)
def create_org(body: OrganizationCreate, auth: AuthContext = Depends(get_current_user)):
    repo = Repository()
    # If already has org, return it
    try:
        return repo.get_org(auth.org_id)
    except Exception:
        pass
    return repo.create_org_for_user(auth.user_id, body.name)


@router.get("/me", response_model=Organization)
def get_my_org(auth: AuthContext = Depends(get_current_user)):
    return Repository().get_org(auth.org_id)


@router.post("/bootstrap", response_model=Organization)
def bootstrap_org(body: OrganizationCreate, auth: AuthContext = Depends(get_current_user)):
    """Create org if membership missing (first login)."""
    repo = Repository()
    try:
        return repo.get_org(auth.org_id)
    except Exception:
        return repo.create_org_for_user(auth.user_id, body.name)


@router.get("/me/members")
def list_members(auth: AuthContext = Depends(get_current_user)):
    return Repository().list_memberships(auth.org_id)


@router.get("/me/subscription")
def get_subscription(auth: AuthContext = Depends(get_current_user)):
    sub = Repository().get_billing_subscription(auth.org_id)
    return sub or {"status": "none", "plan": "free"}
