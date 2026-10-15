from fastapi import FastAPI
from src.api.v1 import router_v1

app = FastAPI()

app.include_router(router_v1, prefix="/api/v1", tags=["v1"])