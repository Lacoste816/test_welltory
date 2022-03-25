import json
import uuid
from enum import IntEnum

from aioredis import Redis
from models import Tasks
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class TaskStatuses(IntEnum):
    NEW = 1
    PROCESSING = 2
    COMPLETED = 3
    ERROR = 4


async def create_task(params: dict, session: AsyncSession, redis: Redis) -> str:
    task_id = uuid.uuid4()
    task = {
        "task_id": str(task_id),
        "name": params.get("name"),
        "processing_time": params.get("processing_time"),
        "status": TaskStatuses.NEW.value,
    }
    query = insert(Tasks).values(task)
    await session.execute(query)
    await redis.lpush("tasks", json.dumps(task))
    return task_id


async def get_tasks(session: AsyncSession, task_id: int = None) -> list:
    query = select([Tasks.task_id, Tasks.name, Tasks.processing_time, Tasks.status])
    if task_id is not None:
        query = query.where(Tasks.task_id == task_id)
    rows = await session.execute(query)
    result = [dict(row) for row in rows]
    return result


async def process_task_status(params: dict, redis: Redis):
    await redis.lpush("task_status_buffer", json.dumps(params))
