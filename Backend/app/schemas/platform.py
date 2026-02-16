from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TenantCreateIn(BaseModel):
    name: str
    slug: str
    license_expires_at: Optional[datetime] = None


class TenantOut(BaseModel):
    id: int
    name: str
    slug: str
    is_active: bool
    license_expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class TenantUpdateIn(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    license_expires_at: Optional[datetime] = None