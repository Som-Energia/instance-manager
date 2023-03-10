import logging

import uvicorn
from fastapi import FastAPI

from gestor import manager
from gestor.routers import api, webhooks

logging.basicConfig(level=logging.DEBUG)

app = FastAPI(title="Gestor", description="Gestor")
app.include_router(api.router, prefix="/api")
app.include_router(webhooks.router, prefix="/webhooks")


@app.get("/")
async def root():
    return {"msg": "Hello World"}


@app.on_event("startup")
async def startup_event():
    await manager.manager.start()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
