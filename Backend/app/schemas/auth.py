from pydantic import BaseModel, EmailStr, Field

class LoginTenantIn(BaseModel):
    tenant_slug: str = Field(..., min_length=2)
    email: EmailStr
    password: str

class RegisterTenantIn(BaseModel):
    tenant_name: str = Field(..., min_length=2)
    tenant_slug: str = Field(..., min_length=2)
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=6)

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    tenant_id: int

    class Config:
        from_attributes = True