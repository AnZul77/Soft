from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.models.order import OrderSide, OrderType, OrderStatus

class OrderCreate(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    side: OrderSide
    type: OrderType
    quantity: float = Field(..., gt=0.0)
    limit_price: Optional[float] = Field(None, gt=0.0)

    @model_validator(mode="after")
    def validate_limit_price(self):
        if self.type == OrderType.LIMIT and (self.limit_price is None or self.limit_price <= 0):
            raise ValueError("limit_price is strictly required for LIMIT orders and must be > 0")
        return self

class OrderResponse(BaseModel):
    id: str
    portfolio_id: str
    ticker: str
    side: OrderSide
    type: OrderType
    quantity: float
    limit_price: Optional[float] = None
    execution_price: Optional[float] = None
    status: OrderStatus
    idempotency_key: Optional[str] = None
    error_reason: Optional[str] = None
    executed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CashTransactionResponse(BaseModel):
    id: str
    portfolio_id: str
    order_id: Optional[str] = None
    amount: float
    balance_after: float
    transaction_type: str
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
