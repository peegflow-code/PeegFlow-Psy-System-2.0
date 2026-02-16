from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# -------------------------
# Auth (Platform Admin)
# -------------------------

class PlatformLoginIn(BaseModel):
    email: str
    password: str


class PlatformLoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PlatformMeOut(BaseModel):
    id: int
    email: str
    is_active: bool

    class Config:
        from_attributes = True


# -------------------------
# Tenants (Clientes)
# -------------------------

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