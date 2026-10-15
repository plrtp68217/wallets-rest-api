from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from decimal import Decimal
import uuid


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