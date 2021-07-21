import uuid

from sqlalchemy import Column, String, DateTime, func, ForeignKey, Float, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Room(Base):
    __tablename__ = "cinema_together_room"

    created_at = Column(DateTime, server_default=func.now())
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    owner_uuid = Column(UUID, nullable=False, unique=True)

    film_work_uuid = Column(UUID(as_uuid=True))
    film_work_time = Column(Float)
    film_work_state = Column(String)

    room_users = relationship("RoomUser")

    # required in order to access columns with server defaults
    # or SQL expression defaults, subsequent to a flush, without
    # triggering an expired load
    __mapper_args__ = {"eager_defaults": True}


class RoomUser(Base):
    __tablename__ = "cinema_together_room_user"

    created_at = Column(DateTime, server_default=func.now())

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_uuid = Column(UUID(as_uuid=True))
    user_type = Column(String)

    room_uuid = Column(ForeignKey("cinema_together_room.id"))

    __table_args__ = (UniqueConstraint('user_uuid', 'room_uuid', name='unique_room_user'),)
