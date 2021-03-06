from http import HTTPStatus
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic.validators import UUID
from starlette.requests import Request

from app.core.fastapi.auth.decorators import login_required
from app.models.response import ResponseModel
from app.models.room import RoomModel, RoomUserModel, RoomUserTypeModel
from app.services.room import RoomService, get_room_service

room_router = APIRouter()


@room_router.get("/", response_model=RoomModel)
@login_required()
async def get_owner_room(
        request: Request,
        service: RoomService = Depends(get_room_service),
) -> Optional[RoomModel]:
    room = await service.get_owner_room(user=request.user)
    if not room:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User room not found!")
    return room


@room_router.post("/", response_model=ResponseModel)
@login_required()
async def create_room(
        request: Request,
        service: RoomService = Depends(get_room_service),
) -> ResponseModel:
    error = await service.create_user_room(user_id=request.user.pk)
    if error:
        return ResponseModel(success=False, errors=[error])
    return ResponseModel(success=True)


@room_router.get("/{room_id}/users/", response_model=List[RoomUserModel])
@login_required()
async def get_room_users(
        request: Request,
        room_id: UUID,
        service: RoomService = Depends(get_room_service),
) -> List[RoomUserModel]:
    return await service.get_room_users(room_id=str(room_id))


@room_router.patch("/{room_id}/{user_id}/", response_model=ResponseModel)
@login_required()
async def update_room_user_permission(
        request: Request,
        room_id: UUID,
        user_id: UUID,
        user_type: RoomUserTypeModel,
        service: RoomService = Depends(get_room_service),
) -> ResponseModel:
    error = await service.update_room_user_permission(
        owner_id=request.user.pk,
        user_id=str(user_id),
        room_id=str(room_id),
        user_type=user_type.user_type.value,
    )
    if error:
        return ResponseModel(success=False, errors=[error])
    return ResponseModel(success=True)


@room_router.post("/{room_id}/join", response_model=ResponseModel)
@login_required()
async def join(
        room_id: UUID,
        request: Request,
        service: RoomService = Depends(get_room_service),
) -> ResponseModel:
    error = await service.join(user=request.user, room_id=str(room_id))
    if error:
        return ResponseModel(success=False, errors=[error])
    return ResponseModel(success=True)


@room_router.get("/{room_id}", response_model=RoomModel)
@login_required()
async def get_room(
        room_id: UUID,
        request: Request,
        service: RoomService = Depends(get_room_service),
) -> RoomModel:
    room = await service.get_room(user=request.user, room_id=room_id)
    if not room:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Permission denied!")
    return room
