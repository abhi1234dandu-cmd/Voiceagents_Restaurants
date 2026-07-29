from typing import Any

from app.services.repository import Repository


def compute_analytics(repo: Repository, org_id: str, restaurant_ids: list[str]) -> dict[str, Any]:
    calls: list[dict[str, Any]] = []
    reservations: list[dict[str, Any]] = []
    for rid in restaurant_ids:
        calls.extend(repo.list_calls(rid))  # type: ignore[arg-type]
        reservations.extend(repo.list_reservations(rid))  # type: ignore[arg-type]

    usage = [u for u in repo.list_usage(org_id) if u.get("metric") == "voice_minutes"]  # type: ignore[arg-type]
    voice_minutes = sum(float(u.get("quantity", 0)) for u in usage)

    by_day: dict[str, dict[str, Any]] = {}
    for c in calls:
        day = str(c.get("started_at", ""))[:10]
        bucket = by_day.setdefault(day, {"date": day, "calls": 0, "transfers": 0, "reservations": 0})
        bucket["calls"] += 1
        if c.get("outcome") == "transferred":
            bucket["transfers"] += 1

    for r in reservations:
        if r.get("status") == "confirmed" and r.get("source") == "voice":
            day = str(r.get("starts_at", ""))[:10]
            bucket = by_day.setdefault(day, {"date": day, "calls": 0, "transfers": 0, "reservations": 0})
            bucket["reservations"] += 1

    return {
        "total_calls": len(calls),
        "answered_calls": len([c for c in calls if c.get("outcome") not in (None, "failed")]),
        "reservations_booked": len([r for r in reservations if r.get("status") == "confirmed"]),
        "transfers": len([c for c in calls if c.get("outcome") == "transferred"]),
        "voice_minutes": voice_minutes,
        "by_day": sorted(by_day.values(), key=lambda x: x["date"]),
    }
