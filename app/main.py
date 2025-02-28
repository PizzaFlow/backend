import logging
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from app.api.routes import router
from app.core.database import init_db

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_db()

app.include_router(router)
