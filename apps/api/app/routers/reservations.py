from uuid import UUID

from fastapi import APIRouter, Depends

from app.deps.auth import AuthContext, assert_restaurant_org, get_current_user
from app.models.schemas import Reservation, ReservationCreate
from app.services.repository import Repository

router = APIRouter(tags=["reservations"])


@router.get("/v1/restaurants/{restaurant_id}/reservations", response_model=list[Reservation])
def list_reservations(restaurant_id: UUID, auth: AuthContext = Depends(get_current_user)):
    repo = Repository()
    assert_restaurant_org(repo.get_restaurant(restaurant_id), auth.org_id)
    return repo.list_reservations(restaurant_id)


@router.post("/v1/restaurants/{restaurant_id}/reservations", response_model=Reservation)
def create_reservation(
    restaurant_id: UUID, body: ReservationCreate, auth: AuthContext = Depends(get_current_user)
):
    repo = Repository()
    assert_restaurant_org(repo.get_restaurant(restaurant_id), auth.org_id)
    return repo.create_reservation(restaurant_id, body.model_dump())


@router.post("/v1/reservations/{reservation_id}/cancel", response_model=Reservation)
def cancel_reservation(reservation_id: UUID, auth: AuthContext = Depends(get_current_user)):
    repo = Repository()
    row = repo.cancel_reservation(reservation_id)
    restaurant = repo.get_restaurant(row["restaurant_id"])
    assert_restaurant_org(restaurant, auth.org_id)
    return row
