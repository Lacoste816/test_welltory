import logging

from aioredis import Redis
from controllers.tasks import create_task
from controllers.tasks import get_tasks
from controllers.tasks import process_task_status
from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from utils import get_redis_dep
from utils import session_manager

from . import router
from .schemas import CreateTaskRequest
from .schemas import Task
from .schemas import TaskID
from .schemas import TaskStatusRequest


@router.get("/tasks", tags=["general"], response_model=list[Task])
async def _get_tasks(async_session: AsyncSession = Depends(session_manager)):
    """Просмотр списка задач"""
    try:
        return await get_tasks(async_session)
    except BaseException as e:
        logging.error(f"Произошла ошибка при списка задач: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}", tags=["general"], response_model=Task)
async def _get_task_by_id(
    task_id, async_session: AsyncSession = Depends(session_manager)
):
    """Просмотр статуса задачи по ее id"""
    try:
        result = await get_tasks(async_session, task_id)
        if len(result) == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        return result[0]
    except BaseException as e:
        logging.error(
            f"Произошла ошибка при получении задачи с id {task_id} : {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/tasks", tags=["general"], response_model=TaskID, response_description="Task id"
)
async def _create_task(
    request: CreateTaskRequest,
    async_session: AsyncSession = Depends(session_manager),
    async_redis: Redis = Depends(get_redis_dep),
):
    """Создание задачи"""
    params = request.dict()
    try:
        task_id = await create_task(params, async_session, async_redis)
        return {"task_id": task_id}
    except BaseException as e:
        logging.error(
            f"Произошла ошибка при попытке создать задачу с параметрами {params}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/task_status", tags=["system"], response_model=bool)
async def _task_status(
    request: TaskStatusRequest, async_redis: Redis = Depends(get_redis_dep)
):
    """Обновление статуса задачи"""
    params = request.dict()
    params["task_id"] = str(params["task_id"])
    try:
        await process_task_status(params, async_redis)
        return True
    except BaseException as e:
        logging.error(
            f"Произошла ошибка при попытке обновить статус с параметрами: {params}"
        )
        raise e
        raise HTTPException(status_code=500, detail=str(e))
