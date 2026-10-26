import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    risk_tolerance = Column(String(50), nullable=True, default="MODERATE")
    investment_horizon = Column(String(50), nullable=True, default="MEDIUM_TERM")
    bio = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    journal_entries = relationship("InvestmentJournalEntry", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("AlertNotification", back_populates="user", cascade="all, delete-orphan")
    alert_rules = relationship("AlertRule", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
