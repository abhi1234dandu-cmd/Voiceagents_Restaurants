from uuid import UUID

from fastapi import APIRouter, Depends

from app.deps.auth import AuthContext, require_admin
from app.services.repository import Repository

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/orgs")
def list_orgs(_: AuthContext = Depends(require_admin)):
    repo = Repository()
    orgs = repo.list_orgs()
    enriched = []
    for o in orgs:
        usage = repo.list_usage(o["id"])
        minutes = sum(float(u.get("quantity", 0)) for u in usage if u.get("metric") == "voice_minutes")
        enriched.append({**o, "voice_minutes": minutes})
    return enriched


@router.post("/orgs/{org_id}/suspend")
def suspend_org(org_id: UUID, _: AuthContext = Depends(require_admin)):
    return Repository().update_org(org_id, {"status": "suspended"})


@router.get("/usage")
def platform_usage(_: AuthContext = Depends(require_admin)):
    repo = Repository()
    return {"orgs": len(repo.list_orgs()), "note": "Aggregate usage available per org via /admin/orgs"}


@router.get("/health")
def admin_health(_: AuthContext = Depends(require_admin)):
    return {"status": "ok", "services": ["api", "voice-worker", "supabase", "twilio", "stripe"]}
