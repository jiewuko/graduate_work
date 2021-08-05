import logging
from functools import lru_cache
from typing import Optional, List
from uuid import UUID

from aioredis import Redis
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, insert, exists, and_, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.fastapi.auth.models import CustomUser
from app.db.postgres.postgres import get_pg_engine
from app.db.redis.redis import get_redis_client
from app.models.db.room import Room, RoomUser
from app.models.room import RoomModel, RoomUserTypeEnum, RoomUserModel, RoomUserMessage, RoomUserMessageTypeEnum
from app.services.base import BaseService

__all__ = ('get_room_service', 'RoomService')

logger = logging.getLogger(__name__)


class RoomService(BaseService):

    async def get_owner_room(self, user: CustomUser) -> Optional[RoomModel]:
        async with self.db_connection.begin() as conn:
            room = await conn.execute(
                select(Room).where(Room.owner_uuid == str(user.pk)))
            existed_room = room.mappings().fetchone()
            return RoomModel(**existed_room) if existed_room else None

    async def create_user_room(self, user_id: str):
        async with self.get_session() as session:
            try:
                async with session.begin():
                    session.add(Room(
                        owner_uuid=user_id,
                        room_users=[RoomUser(user_uuid=user_id, user_type=RoomUserTypeEnum.owner.value)])
                    )
            except IntegrityError as exc:
                logger.error(exc)
                return f'Room for user "{user_id}" already exist!'

    async def get_room(self, room_id: UUID, user: CustomUser) -> Optional[RoomModel]:
        async with self.db_connection.begin() as conn:
            room_user_type = await conn.execute(
                select(RoomUser.user_type).where(
                    RoomUser.room_uuid == str(room_id),
                    RoomUser.user_uuid == str(user.pk),
                ))
            existed_room_user_type = room_user_type.scalars().first()
            if not existed_room_user_type or existed_room_user_type == RoomUserTypeEnum.pending.value:
                return None

            room = await conn.execute(select(Room).where(RoomUser.room_uuid == str(room_id)))
            existed_room = room.mappings().fetchone()
            return RoomModel(**existed_room) if existed_room else None

    async def join(self, user: CustomUser, room_id: str) -> Optional[str]:
        async with self.db_connection.begin() as conn:
            room = await conn.execute(select(Room.owner_uuid).where(Room.id == room_id))
            room_owner = room.scalars().first()

            if not room_owner:
                return f'Room "{room_id}" does not exist!'

            if user.pk == room_owner:
                return f'You are the owner of the room "{room_id}"!'

            try:
                await conn.execute(
                    insert(RoomUser, {
                        RoomUser.room_uuid.key: room_id,
                        RoomUser.user_uuid.key: user.pk,
                        RoomUser.user_type: RoomUserTypeEnum.pending.value,
                    })
                )
            except IntegrityError as exc:
                logger.error(exc)
                return f'Room user "{user.pk}" already exist!'

            message = RoomUserMessage(
                text='New user is waiting to approve!',
                msg_type=RoomUserMessageTypeEnum.service.value,
                user_id=user.pk,
                first_name=user.first_name,
                last_name=user.last_name,
            )
            await self.redis.xadd(
                room_id,
                fields=jsonable_encoder(message),
            )

    async def update_room_user_permission(
            self,
            owner_id: str,
            room_id: str,
            user_id: str,
            user_type: str,
    ) -> Optional[str]:
        async with self.db_connection.begin() as conn:
            if user_id == owner_id:
                return "Cannot change the owner of the room!"

            room_owner = await conn.execute(
                select(exists(Room).where(and_(Room.id == room_id, Room.owner_uuid == owner_id))))
            is_owner = room_owner.scalars().first()

            if not is_owner:
                return "Permission denied!"

            await conn.execute(
                update(RoomUser).where(
                    and_(
                        RoomUser.room_uuid == room_id,
                        RoomUser.user_uuid == user_id
                    )
                ).values(user_type=user_type))

    async def get_room_users(self, room_id: str) -> List[RoomUserModel]:
        async with self.db_connection.begin() as conn:
            results = await conn.execute(select(RoomUser).where(RoomUser.room_uuid == room_id))
            room_users = results.mappings().fetchall()
            return [RoomUserModel(**room_user) for room_user in room_users] if room_users else []


@lru_cache()
def get_room_service(
        db_connection: AsyncEngine = Depends(get_pg_engine),
        redis: Redis = Depends(get_redis_client),
) -> RoomService:
    return RoomService(db_connection, redis)
