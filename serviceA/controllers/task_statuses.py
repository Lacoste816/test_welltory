import asyncio
import json
import logging

from models import Tasks
from sqlalchemy.dialects.postgresql import insert
from utils import get_redis
from utils import SessionMaker


async def process_status_buffer():
    while True:
        r = None
        try:
            r = await get_redis()
            status_entry = True
            statuses = {}
            while status_entry is not None:
                status_entry = await r.rpop("task_status_buffer")
                if status_entry is None:
                    continue
                status_entry = json.loads(status_entry)
                statuses[status_entry.get("task_id")] = status_entry.get("status")
            if statuses:
                values = [{"task_id": key, "status": statuses[key]} for key in statuses]
                query = insert(Tasks).values(values)
                query = query.on_conflict_do_update(
                    index_elements=[Tasks.task_id],
                    set_=dict(status=query.excluded.status),
                )
                session = SessionMaker()
                await session.execute(query)
                await session.commit()
                await session.close()
            await asyncio.sleep(1)
        except asyncio.exceptions.CancelledError:
            # graceful shutdown
            return
        except BaseException as e:
            logging.error(f"Произошла ошибка при обработке статусов задач: {str(e)}")
        finally:
            if r:
                await r.close()
