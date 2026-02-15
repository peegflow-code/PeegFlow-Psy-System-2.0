from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

AppointmentStatus = Literal["available", "booked", "done", "canceled", "no_show"]


class AppointmentOut(BaseModel):
    id: int
    start_at: datetime
    end_at: datetime
    status: AppointmentStatus
    price: float
    patient_user_id: Optional[int] = None

    # para o admin ver quem marcou
    patient_name: Optional[str] = None
    patient_email: Optional[str] = None

    class Config:
        from_attributes = True


class BookIn(BaseModel):
    appointment_id: int


class CancelIn(BaseModel):
    appointment_id: int


class SetStatusIn(BaseModel):
    appointment_id: int
    status: AppointmentStatus  # admin: done | no_show | canceled (e booked/available se quiser)


class BulkGenerateIn(BaseModel):
    date: str  # YYYY-MM-DD
    start_time: str  # HH:MM
    end_time: str  # HH:MM
    duration_minutes: int
    price: float