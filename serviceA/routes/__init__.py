import os

from fastapi import APIRouter

prefix = os.getenv("API_PREFIX", "")
router = APIRouter(prefix=prefix)

from .general import *  # noqa
from .tasks import *  # noqa

__all__ = [
    "router",
]
