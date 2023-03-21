import logging

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


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await manager.manager.stop()
