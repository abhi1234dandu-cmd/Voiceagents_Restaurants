"""POS adapter interface (scale phase) — pluggable ordering adapters."""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends

from app.deps.auth import AuthContext, assert_restaurant_org, get_current_user
from app.services.repository import Repository

router = APIRouter(prefix="/v1/restaurants/{restaurant_id}/pos", tags=["pos"])


class POSAdapter(ABC):
    @abstractmethod
    def list_menu(self, restaurant_id: str) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def create_order(self, restaurant_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class StubPOSAdapter(POSAdapter):
    """Pilot stub POS — mirrors internal menu; orders logged to audit."""

    def list_menu(self, restaurant_id: str) -> list[dict[str, Any]]:
        return Repository().list_menu_items(restaurant_id)  # type: ignore[arg-type]

    def create_order(self, restaurant_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        repo = Repository()
        restaurant = repo.get_restaurant(restaurant_id)  # type: ignore[arg-type]
        order_id = __import__("uuid").uuid4().hex
        repo.audit(
            restaurant["org_id"],
            None,
            "pos_create_order",
            "order",
            order_id,
            payload,
        )
        return {"order_id": order_id, "status": "accepted", "adapter": "stub"}


ADAPTERS: dict[str, POSAdapter] = {"stub": StubPOSAdapter()}


@router.get("/menu")
def pos_menu(restaurant_id: UUID, auth: AuthContext = Depends(get_current_user)):
    repo = Repository()
    assert_restaurant_org(repo.get_restaurant(restaurant_id), auth.org_id)
    return ADAPTERS["stub"].list_menu(str(restaurant_id))


@router.post("/orders")
def pos_order(restaurant_id: UUID, body: dict, auth: AuthContext = Depends(get_current_user)):
    repo = Repository()
    assert_restaurant_org(repo.get_restaurant(restaurant_id), auth.org_id)
    return ADAPTERS["stub"].create_order(str(restaurant_id), body)
