from fastapi import FastAPI

from gestor.routers import webhooks, api

app = FastAPI(title="Gestor", description="Gestor")

app.include_router(api.router, prefix="/api")
app.include_router(webhooks.router, prefix="/webhooks")
