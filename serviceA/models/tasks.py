from uuid import uuid4

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class Tasks(Base):
    """Таблица задач"""

    __tablename__: str = "tasks"

    task_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, comment="id задачи"
    )
    name = Column(String, comment="имя задачи")
    processing_time = Column(Integer, comment="время выполнения задачи")
    status = Column(SmallInteger, comment="статус задачи")
