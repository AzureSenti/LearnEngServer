from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import auth
from api.routes import sync
from api.routes import user
from core.config import settings
from core.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: runs init_db on startup to ensure tables exist."""
    init_db()
    yield


app = FastAPI(
    title="LearnEng API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(sync.router, prefix=settings.API_V1_STR)
app.include_router(user.router, prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    return {"message": "Welcome to the API!"}