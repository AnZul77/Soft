from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class JournalEntryCreate(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    thesis_title: str = Field(..., min_length=1, max_length=255)
    thesis_content: str
    rationale: Optional[str] = None
    target_price: Optional[float] = None
    confidence_rating: int = Field(default=3, ge=1, le=5)
    review_date: Optional[datetime] = None
    portfolio_id: Optional[str] = None

class JournalEntryUpdate(BaseModel):
    thesis_title: Optional[str] = None
    thesis_content: Optional[str] = None
    rationale: Optional[str] = None
    target_price: Optional[float] = None
    confidence_rating: Optional[int] = Field(None, ge=1, le=5)
    review_date: Optional[datetime] = None

class JournalEntryResponse(BaseModel):
    id: str
    user_id: str
    portfolio_id: Optional[str] = None
    ticker: str
    thesis_title: str
    thesis_content: str
    rationale: Optional[str] = None
    target_price: Optional[float] = None
    confidence_rating: int
    review_date: Optional[datetime] = None
    ai_reflection: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ThesisReflectionRequest(BaseModel):
    entry_id: str
