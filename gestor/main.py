import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from gestor import manager
from gestor.routers import api, webhooks

logging.basicConfig(level=logging.DEBUG)

app = FastAPI(title="Gestor", description="Gestor")
app.include_router(api.router, prefix="/api")
app.include_router(webhooks.router, prefix="/webhooks")

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"msg": "Hello World"}


@app.on_event("startup")
async def startup_event():
    await manager.manager.start()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await manager.manager.stop()
