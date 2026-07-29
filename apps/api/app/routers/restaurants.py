from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.deps.auth import AuthContext, assert_restaurant_org, get_current_user
from app.models.schemas import Restaurant, RestaurantCreate, RestaurantUpdate
from app.services.repository import Repository

router = APIRouter(prefix="/v1/restaurants", tags=["restaurants"])


@router.get("", response_model=list[Restaurant])
def list_restaurants(auth: AuthContext = Depends(get_current_user)):
    return Repository().list_restaurants(auth.org_id)


@router.post("", response_model=Restaurant)
def create_restaurant(body: RestaurantCreate, auth: AuthContext = Depends(get_current_user)):
    return Repository().create_restaurant(auth.org_id, body.model_dump())


@router.get("/{restaurant_id}", response_model=Restaurant)
def get_restaurant(restaurant_id: UUID, auth: AuthContext = Depends(get_current_user)):
    repo = Repository()
    r = repo.get_restaurant(restaurant_id)
    assert_restaurant_org(r, auth.org_id)
    return r


@router.patch("/{restaurant_id}", response_model=Restaurant)
def update_restaurant(
    restaurant_id: UUID, body: RestaurantUpdate, auth: AuthContext = Depends(get_current_user)
):
    repo = Repository()
    r = repo.get_restaurant(restaurant_id)
    assert_restaurant_org(r, auth.org_id)
    return repo.update_restaurant(restaurant_id, body.model_dump(exclude_unset=True))


@router.delete("/{restaurant_id}")
def delete_restaurant(restaurant_id: UUID, auth: AuthContext = Depends(get_current_user)):
    repo = Repository()
    r = repo.get_restaurant(restaurant_id)
    assert_restaurant_org(r, auth.org_id)
    repo.update_restaurant(restaurant_id, {"status": "archived"})
    return {"ok": True}
