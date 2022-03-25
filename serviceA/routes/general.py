from fastapi import Response

from . import router


@router.get("/healthcheck", tags=["general"])
async def healthcheck():
    """Проверка доступности сервиса"""
    return Response(status_code=200)
