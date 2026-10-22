import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Text, UniqueConstraint
from app.database import Base

class CompanyRelationship(Base):
    __tablename__ = "company_relationships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_ticker = Column(String(10), nullable=False, index=True)
    target_ticker = Column(String(10), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False) # 'SUPPLIER', 'CUSTOMER', 'COMPETITOR', 'SUBSIDIARY'
    description = Column(Text, nullable=True)
    confidence_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint('source_ticker', 'target_ticker', 'relationship_type', name='uq_source_target_rel'),
    )
