from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TenantCreateIn(BaseModel):
    name: str
    slug: str
    is_active: bool = True
    license_expires_at: Optional[datetime] = None

class TenantUpdateIn(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    license_expires_at: Optional[datetime] = None

class TenantOut(BaseModel):
    id: int
    name: str
    slug: str
    is_active: bool
    license_expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True