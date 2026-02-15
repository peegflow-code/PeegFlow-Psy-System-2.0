from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


class PatientBase(BaseModel):
    full_name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

    # ficha completa
    birth_date: Optional[date] = None
    sex: Optional[str] = None
    marital_status: Optional[str] = None
    address: Optional[str] = None
    occupation: Optional[str] = None
    emergency_name: Optional[str] = None
    emergency_phone: Optional[str] = None
    document_id: Optional[str] = None


class PatientCreateIn(PatientBase):
    create_user: bool = True
    user_password: str = "123456"


class PatientUpdateIn(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

    # ficha completa
    birth_date: Optional[date] = None
    sex: Optional[str] = None
    marital_status: Optional[str] = None
    address: Optional[str] = None
    occupation: Optional[str] = None
    emergency_name: Optional[str] = None
    emergency_phone: Optional[str] = None
    document_id: Optional[str] = None


class PatientOut(PatientBase):
    id: int
    user_id: Optional[int] = None

    class Config:
        from_attributes = True


class PatientAccessIn(BaseModel):
    password: str = "123456"