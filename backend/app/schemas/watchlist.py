from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class WatchlistItemCreate(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    notes: Optional[str] = None
    target_price: Optional[float] = None

class WatchlistItemResponse(BaseModel):
    id: str
    watchlist_id: str
    ticker: str
    notes: Optional[str] = None
    target_price: Optional[float] = None
    added_at: datetime
    current_price: Optional[float] = None
    change_percent: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class WatchlistCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class WatchlistUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None

class WatchlistResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    items: List[WatchlistItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
