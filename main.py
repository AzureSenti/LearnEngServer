
from fastapi import FastAPI
from api.routes import auth
from core.config import settings

app = FastAPI()

app.include_router(auth.router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to the API!"}