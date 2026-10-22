import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base

class AlertStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    DELIVERED = "DELIVERED"
    READ = "READ"

class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ticker = Column(String(10), nullable=True) # None means applies to any holding in user portfolio
    threshold_pct = Column(Float, nullable=False, default=0.08) # 8% move
    window_minutes = Column(Float, nullable=False, default=15.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AlertNotification(Base):
    __tablename__ = "alert_notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    portfolio_id = Column(String(36), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=True)
    ticker = Column(String(10), nullable=False)
    event_type = Column(String(50), nullable=False) # 'PRICE_DROP', 'PRICE_SPIKE', 'SUPPLY_CHAIN_SHOCK'
    price_change_pct = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    portfolio_exposure_pct = Column(Float, nullable=False, default=0.0)
    status = Column(SQLEnum(AlertStatus), nullable=False, default=AlertStatus.DELIVERED)
    message = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="alerts")
