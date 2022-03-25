import logging
import os
import time

from aioredis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

REDIS_URL = (
    f'redis://:{os.getenv("REDIS_PWD")}@{os.getenv("REDIS_HOST")}:'
    f'{os.getenv("REDIS_PORT")}/{os.getenv("REDIS_DB")}'
)
POSTGRES_URL = (
    f'postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@'
    f'{os.getenv("DB_IP")}:{int(os.getenv("DB_PORT", 5432))}/{os.getenv("DB_DATABASE")}'
)
engine = create_async_engine(POSTGRES_URL)
SessionMaker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def session_manager():
    session = SessionMaker()
    try:
        yield session
    except Exception as e:
        logging.error(f"Произошла ошибка. {str(e)}. Откат транзакции")
        await session.rollback()
    finally:
        await session.commit()
        await session.close()


async def get_redis() -> Redis:
    return Redis.from_url(
        url=REDIS_URL,
        socket_keepalive=True,
        socket_timeout=3,
    )


async def get_redis_dep():
    redis = await get_redis()
    try:
        yield redis
    finally:
        await redis.close()


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if "log_time" in kw:
            name = kw.get("log_name", method.__name__.upper())
            kw["log_time"][name] = int((te - ts) * 1000)
        else:
            logging.info(
                f"Выполнение функции {method.__name__} заняло {round((te - ts) * 1000, 2)}"
            )
        return result

    return timed
