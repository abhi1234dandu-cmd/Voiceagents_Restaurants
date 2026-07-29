"""Plan limits derived from Hostline pricing."""

from typing import Any, Optional

PLAN_LIMITS: dict[str, dict[str, Any]] = {
    "free": {"minutes": 50, "locations": 1, "sms": False, "multilingual": False, "pos": False},
    "starter": {"minutes": 500, "locations": 1, "sms": False, "multilingual": False, "pos": False},
    "professional": {"minutes": 2000, "locations": 1, "sms": True, "multilingual": True, "pos": False},
    "premium": {"minutes": None, "locations": 20, "sms": True, "multilingual": True, "pos": True},
    "enterprise": {"minutes": None, "locations": None, "sms": True, "multilingual": True, "pos": True},
    "pro": {"minutes": 2000, "locations": 1, "sms": True, "multilingual": True, "pos": False},  # legacy alias
}


def limits_for(plan: Optional[str]) -> dict[str, Any]:
    return PLAN_LIMITS.get((plan or "free").lower(), PLAN_LIMITS["free"])


def minutes_remaining(plan: Optional[str], used: float) -> Optional[float]:
    lim = limits_for(plan)["minutes"]
    if lim is None:
        return None
    return max(0.0, float(lim) - float(used))


def can_activate_agent(org: dict[str, Any], used_minutes: float) -> tuple[bool, str]:
    if org.get("status") == "suspended":
        return False, "Organization is suspended"
    if org.get("status") == "past_due":
        return False, "Payment past due"
    remaining = minutes_remaining(org.get("plan"), used_minutes)
    if remaining is not None and remaining <= 0:
        return False, "AI minute allowance exhausted for this plan"
    return True, "ok"


def can_add_location(org: dict[str, Any], current_count: int) -> tuple[bool, str]:
    lim = limits_for(org.get("plan"))["locations"]
    if lim is None:
        return True, "ok"
    if current_count >= lim:
        return False, f"Plan allows up to {lim} location(s). Upgrade for more."
    return True, "ok"
