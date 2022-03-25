from uuid import UUID
from uuid import uuid4

from controllers.tasks import TaskStatuses
from pydantic import BaseModel
from pydantic import Field


class CreateTaskRequest(BaseModel):
    name: str = Field(title="Название задачи")
    processing_time: int = Field(title="Время выполнения в секундах", ge=0)


class TaskID(BaseModel):
    task_id: UUID = Field(default_factory=uuid4, title="id задачи")


class TaskStatusRequest(TaskID):
    status: TaskStatuses = Field(title="Статус задачи")


class Task(CreateTaskRequest, TaskStatusRequest):
    pass
