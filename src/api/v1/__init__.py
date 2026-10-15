from fastapi import APIRouter

from src.api.v1.wallets import router as wallets_router

router_v1 = APIRouter()

router_v1.include_router(wallets_router)