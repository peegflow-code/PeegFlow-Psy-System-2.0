from pydantic import BaseModel, EmailStr

class PlatformLoginIn(BaseModel):
    email: EmailStr
    password: str

class PlatformTokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"