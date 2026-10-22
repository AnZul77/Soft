from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.portfolio import PortfolioType

class PortfolioCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: PortfolioType = PortfolioType.VIRTUAL_TRADING
    initial_cash: Optional[float] = Field(default=100000.0, ge=0.0)

class PortfolioResponse(BaseModel):
    id: str
    user_id: str
    name: str
    type: PortfolioType
    base_currency: str
    virtual_cash_balance: float
    reserved_cash: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HoldingCreate(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    quantity: float = Field(..., gt=0.0)
    cost_basis: float = Field(..., ge=0.0)

class HoldingUpdate(BaseModel):
    quantity: Optional[float] = Field(None, gt=0.0)
    cost_basis: Optional[float] = Field(None, ge=0.0)

class HoldingResponse(BaseModel):
    id: str
    portfolio_id: str
    ticker: str
    quantity: float
    cost_basis: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ValuationHolding(BaseModel):
    holding_id: str
    ticker: str
    quantity: float
    cost_basis: float
    current_price: float
    market_value: float
    unrealized_pl: float
    unrealized_pl_pct: float
    weight_pct: float
    is_stale: bool
    price_source: str # 'LIVE', 'CACHE', 'COST_BASIS_FALLBACK'

class PortfolioValuation(BaseModel):
    portfolio_id: str
    portfolio_name: str
    portfolio_type: PortfolioType
    base_currency: str
    total_equity: float # holdings_value + virtual_cash_balance + reserved_cash
    holdings_value: float
    virtual_cash_balance: float
    reserved_cash: float
    total_unrealized_pl: float
    total_unrealized_pl_pct: float
    holdings: List[ValuationHolding]
    valuation_time: datetime
