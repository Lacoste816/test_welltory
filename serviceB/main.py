import json
import logging
import os
import time
from enum import Enum

import requests
from redis import Redis

REDIS_URL = (
    f'redis://:{os.getenv("REDIS_PWD")}@{os.getenv("REDIS_HOST")}:'
    f'{os.getenv("REDIS_PORT")}/{os.getenv("REDIS_DB")}'
)
STATUS_URL = os.getenv("STATUS_URL")


class TaskStatuses(Enum):
    NEW = 1
    PROCESSING = 2
    COMPLETED = 3
    ERROR = 4


def get_redis():
    return Redis.from_url(
        url=REDIS_URL,
        socket_keepalive=True,
        socket_timeout=1,
    )


def change_task_status(task_id, status):
    r = requests.post(STATUS_URL, json={"task_id": task_id, "status": status})
    if r.status_code != 200:
        logging.error(
            f"ошибка при отправке статуса для задачи {task_id}: {str(r.reason)}"
        )


def process_tasks():
    r = get_redis()
    try:
        while True:
            task = r.rpop("tasks")
            if task:
                task = json.loads(task)
                change_task_status(task.get("task_id"), TaskStatuses.PROCESSING.value)
                time.sleep(task.get("processing_time"))
                if task.get("processing_time") == 13:
                    change_task_status(task.get("task_id"), TaskStatuses.ERROR.value)
                else:
                    change_task_status(
                        task.get("task_id"), TaskStatuses.COMPLETED.value
                    )
            else:
                time.sleep(1)
    finally:
        r.close()


if __name__ == "__main__":
    process_tasks()
