from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class PlatformLoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TenantCreateIn(BaseModel):
    name: str
    slug: str
    license_expires_at: Optional[datetime] = None
    is_active: bool = True

class TenantOut(BaseModel):
    id: int
    name: str
    slug: str
    is_active: bool
    license_expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True