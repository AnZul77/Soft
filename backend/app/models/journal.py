import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database import Base

class InvestmentJournalEntry(Base):
    __tablename__ = "investment_journal_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    portfolio_id = Column(String(36), ForeignKey("portfolios.id", ondelete="SET NULL"), nullable=True)
    ticker = Column(String(10), nullable=False, index=True)
    thesis_title = Column(String(255), nullable=False)
    thesis_content = Column(Text, nullable=False)
    rationale = Column(Text, nullable=True)
    target_price = Column(Float, nullable=True)
    confidence_rating = Column(Integer, default=3) # 1 to 5
    review_date = Column(DateTime, nullable=True)
    ai_reflection = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="journal_entries")
