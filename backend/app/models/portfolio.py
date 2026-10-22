import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base

class PortfolioType(str, enum.Enum):
    MANUAL_TRACKING = "MANUAL_TRACKING"
    VIRTUAL_TRADING = "VIRTUAL_TRADING"

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(SQLEnum(PortfolioType), nullable=False, default=PortfolioType.VIRTUAL_TRADING)
    base_currency = Column(String(3), nullable=False, default="USD")
    virtual_cash_balance = Column(Float, nullable=False, default=100000.00)
    reserved_cash = Column(Float, nullable=False, default=0.00)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")
    orders = relationship("TradeOrder", back_populates="portfolio", cascade="all, delete-orphan")
    cash_transactions = relationship("CashTransaction", back_populates="portfolio", cascade="all, delete-orphan")

class Holding(Base):
    __tablename__ = "holdings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String(36), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    quantity = Column(Float, nullable=False, default=0.0)
    cost_basis = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    portfolio = relationship("Portfolio", back_populates="holdings")

class CashTransaction(Base):
    __tablename__ = "cash_transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String(36), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id = Column(String(36), ForeignKey("trade_orders.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Float, nullable=False) # Positive for deposits/sales, negative for purchases
    balance_after = Column(Float, nullable=False)
    transaction_type = Column(String(30), nullable=False) # 'INITIAL_DEPOSIT', 'BUY_ORDER', 'SELL_ORDER', 'ESCROW_RESERVE', 'ESCROW_REFUND'
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    portfolio = relationship("Portfolio", back_populates="cash_transactions")
