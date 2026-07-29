from fastapi import APIRouter, Depends

from app.deps.auth import AuthContext, get_current_user
from app.models.schemas import AnalyticsSummary
from app.services.analytics import compute_analytics
from app.services.repository import Repository

router = APIRouter(prefix="/v1/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def summary(auth: AuthContext = Depends(get_current_user)):
    repo = Repository()
    restaurants = repo.list_restaurants(auth.org_id)
    data = compute_analytics(repo, str(auth.org_id), [r["id"] for r in restaurants])
    return data
