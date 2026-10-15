from fastapi import APIRouter, HTTPException
from sqlalchemy import select
import uuid

from src.api.v1.dependencies import SessionDep
from src.models.wallets import Wallet
from src.schemas.wallets import WalletResponse, OperationRequest, OperationType

router = APIRouter()

@router.get("/wallets", response_model=list[WalletResponse])
async def get_wallets(session: SessionDep):
    wallets = (await session.execute(select(Wallet))).scalars().all()
    return wallets

@router.post("/wallets", response_model=WalletResponse)
async def create_wallet(session: SessionDep):
    new_wallet = Wallet()
    session.add(new_wallet)
    await session.commit()
    await session.refresh(new_wallet)
    return new_wallet

@router.post("/wallets/{wallet_uuid}/operation", response_model=WalletResponse)
async def wallet_operation(
    wallet_uuid: uuid.UUID, 
    data: OperationRequest,
    session: SessionDep
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