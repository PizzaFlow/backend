from fastapi import FastAPI

from app.api.router import router
from app.core.database import init_db

app = FastAPI()


@app.on_event("startup")
async def startup():
    await init_db()


app.include_router(router)
