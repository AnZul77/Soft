from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    risk_tolerance: Optional[str] = "MODERATE"
    investment_horizon: Optional[str] = "MEDIUM_TERM"
    bio: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    risk_tolerance: Optional[str] = None
    investment_horizon: Optional[str] = None
    bio: Optional[str] = None

class UserProfileResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    risk_tolerance: Optional[str] = "MODERATE"
    investment_horizon: Optional[str] = "MEDIUM_TERM"
    bio: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[str] = None
