import asyncio
import os
import sys

import uvicorn
from controllers.task_statuses import process_status_buffer
from fastapi import FastAPI
from routes import router

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

app = FastAPI(
    title="ServiceA",
    root_path="/",
)

app.include_router(router)


@app.on_event("startup")
async def startup_event():
    asyncio.get_event_loop().create_task(process_status_buffer())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
