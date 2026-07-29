"""Background-style retention and scale utilities exposed as admin/internal routes."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.deps.auth import require_internal
from app.services.repository import Repository

router = APIRouter(prefix="/internal/jobs", tags=["jobs"], dependencies=[Depends(require_internal)])


@router.post("/retention/recordings")
def purge_old_recordings(settings: Settings = Depends(get_settings)):
    repo = Repository()
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.recording_retention_days)
    purged = 0
    # Scan all restaurants via orgs
    for org in repo.list_orgs():
        for restaurant in repo.list_restaurants(org["id"]):
            for call in repo.list_calls(restaurant["id"]):
                started = call.get("started_at")
                if not started:
                    continue
                try:
                    ts = datetime.fromisoformat(str(started).replace("Z", "+00:00"))
                except ValueError:
                    continue
                if ts < cutoff and call.get("recording_storage_path"):
                    repo.update_call(
                        call["id"],
                        {"recording_url": None, "recording_storage_path": None, "recording_purged_at": datetime.now(timezone.utc).isoformat()},
                    )
                    purged += 1
    return {"purged": purged, "retention_days": settings.recording_retention_days}


@router.post("/embeddings/backfill")
def backfill_embeddings():
    """Scale: attach simple bag-of-words embedding vectors to FAQs for retrieval boost."""
    repo = Repository()
    updated = 0
    for org in repo.list_orgs():
        for restaurant in repo.list_restaurants(org["id"]):
            for faq in repo.list_faqs(restaurant["id"]):
                text = f"{faq.get('question', '')} {faq.get('answer', '')}".lower()
                # 32-dim hashed bag-of-words
                vec = [0.0] * 32
                for token in text.split():
                    vec[hash(token) % 32] += 1.0
                repo.sb.table("faqs").update({"embedding": vec}).eq("id", faq["id"]).execute()
                updated += 1
    return {"updated": updated}
