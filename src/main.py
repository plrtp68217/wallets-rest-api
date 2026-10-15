from fastapi import FastAPI, APIRouter, Depends, HTTPException

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from contextlib import asynccontextmanager
from pydantic import BaseModel, Field

from src.database import AsyncSessionLocal, engine, Base
from src.models import Wallet


class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"

class OperationRequest(BaseModel):
    operation_type: OperationType
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)

class WalletResponse(BaseModel):
    id: uuid.UUID
    balance: Decimal
    created_at: datetime
    updated_at: datetime

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
router = APIRouter(prefix="/api/v1")

@router.post("/wallets", response_model=WalletResponse)
async def create_wallet(session: AsyncSession = Depends(get_session)):
    new_wallet = Wallet()
    session.add(new_wallet)
    await session.commit()
    await session.refresh(new_wallet)
    return new_wallet

@router.get("/wallets", response_model=list[WalletResponse])
async def get_wallets(session: AsyncSession = Depends(get_session)):
    wallets = (await session.execute(select(Wallet))).scalars().all()
    return wallets

@router.post("/wallets/{wallet_uuid}/operation", response_model=WalletResponse)
async def wallet_operation(
    wallet_uuid: uuid.UUID, 
    data: OperationRequest,
    session: AsyncSession = Depends(get_session)
):
    statement = select(Wallet).where(Wallet.id == wallet_uuid).with_for_update()
    wallet = (await session.execute(statement)).scalar_one_or_none()

    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if data.operation_type == OperationType.DEPOSIT:
        wallet.balance += data.amount
    elif data.operation_type == OperationType.WITHDRAW:
        if wallet.balance < data.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        wallet.balance -= data.amount

    await session.commit()
    await session.refresh(wallet)

    return wallet

app.include_router(router)