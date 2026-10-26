import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    items = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan")
    user = relationship("User", backref="watchlists")

class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    __table_args__ = (
        UniqueConstraint("watchlist_id", "ticker", name="uq_watchlist_items_watchlist_ticker"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    watchlist_id = Column(String(36), ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    notes = Column(String(255), nullable=True)
    target_price = Column(Float, nullable=True)
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    watchlist = relationship("Watchlist", back_populates="items")
