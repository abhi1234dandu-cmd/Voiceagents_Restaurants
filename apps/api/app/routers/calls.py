from uuid import UUID

from fastapi import APIRouter, Depends

from app.deps.auth import AuthContext, assert_restaurant_org, get_current_user
from app.models.schemas import Call, CallTurn
from app.services.repository import Repository

router = APIRouter(tags=["calls"])


@router.get("/v1/restaurants/{restaurant_id}/calls", response_model=list[Call])
def list_calls(restaurant_id: UUID, auth: AuthContext = Depends(get_current_user)):
    repo = Repository()
    assert_restaurant_org(repo.get_restaurant(restaurant_id), auth.org_id)
    return repo.list_calls(restaurant_id)


@router.get("/v1/calls/{call_id}", response_model=Call)
def get_call(call_id: UUID, auth: AuthContext = Depends(get_current_user)):
    repo = Repository()
    call = repo.get_call(call_id)
    assert_restaurant_org(repo.get_restaurant(call["restaurant_id"]), auth.org_id)
    return call


@router.get("/v1/calls/{call_id}/turns", response_model=list[CallTurn])
def get_turns(call_id: UUID, auth: AuthContext = Depends(get_current_user)):
    repo = Repository()
    call = repo.get_call(call_id)
    assert_restaurant_org(repo.get_restaurant(call["restaurant_id"]), auth.org_id)
    return repo.list_turns(call_id)
