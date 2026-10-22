from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class QuoteResponse(BaseModel):
    ticker: str
    price: float
    change: float
    change_percent: float
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    volume: Optional[float] = None
    previous_close: Optional[float] = None
    last_updated: datetime
    is_stale: bool = False
    source: str = "CACHE"

    model_config = ConfigDict(from_attributes=True)

class SecurityResponse(BaseModel):
    id: str
    ticker: str
    company_name: str
    sector: Optional[str] = None
    industry: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class NewsArticleResponse(BaseModel):
    id: str
    title: str
    source: str
    url: str
    published_at: datetime
    content_raw: str
    ai_summary: Optional[str] = None
    sentiment_label: Optional[str] = None
    sentiment_score: Optional[float] = None
    ticker_tags: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AnomalyInjectionRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    price_change_pct: float = Field(..., description="E.g. -0.08 for -8% drop, or +0.10 for +10% spike")
    headline: Optional[str] = Field(None, description="Optional news headline triggering the anomaly")
    content: Optional[str] = Field(None, description="Optional news article body")
