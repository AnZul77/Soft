import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base

class OrderSide(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, enum.Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"

class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class TradeOrder(Base):
    __tablename__ = "trade_orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String(36), ForeignKey("portfolios.id", ondelete="SET NULL"), nullable=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    side = Column(SQLEnum(OrderSide), nullable=False)
    type = Column(SQLEnum(OrderType), nullable=False)
    quantity = Column(Float, nullable=False)
    limit_price = Column(Float, nullable=True)
    execution_price = Column(Float, nullable=True)
    status = Column(SQLEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    idempotency_key = Column(String(64), unique=True, nullable=True, index=True)
    error_reason = Column(String(255), nullable=True)
    executed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    portfolio = relationship("Portfolio", back_populates="orders")
