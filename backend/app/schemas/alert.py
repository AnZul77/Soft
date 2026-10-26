from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.alert import AlertStatus

class AlertRuleCreate(BaseModel):
    ticker: Optional[str] = None
    threshold_pct: float = 0.08
    window_minutes: float = 15.0

class AlertRuleUpdate(BaseModel):
    ticker: Optional[str] = None
    threshold_pct: Optional[float] = None
    window_minutes: Optional[float] = None
    is_active: Optional[bool] = None

class AlertRuleResponse(BaseModel):
    id: str
    user_id: str
    ticker: Optional[str] = None
    threshold_pct: float
    window_minutes: float
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AlertNotificationResponse(BaseModel):
    id: str
    user_id: str
    portfolio_id: Optional[str] = None
    ticker: str
    event_type: str
    price_change_pct: float
    current_price: float
    portfolio_exposure_pct: float
    status: AlertStatus
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RiskMetricsResponse(BaseModel):
    portfolio_id: str
    concentration_hhi: float
    top_3_concentration_pct: float
    is_high_concentration: bool
    annualized_volatility: float
    portfolio_beta: float
    value_at_risk_95_1d: float
    benchmark_ticker: str = "SPY"
    calculated_at: datetime
