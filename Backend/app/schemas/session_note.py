from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class SessionNoteCreateIn(BaseModel):
    patient_id: int
    appointment_id: Optional[int] = None
    content: Optional[str] = None
    is_locked: bool = False
    session_date: Optional[date] = None  # NOVO


class SessionNoteUpdateIn(BaseModel):
    content: Optional[str] = None
    is_locked: Optional[bool] = None
    session_date: Optional[date] = None  # NOVO


class SessionNoteOut(BaseModel):
    id: int
    patient_id: int
    appointment_id: Optional[int] = None
    content: Optional[str] = None
    is_locked: bool
    session_date: Optional[date] = None  # NOVO
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True