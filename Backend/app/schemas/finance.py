from pydantic import BaseModel

class StatusCount(BaseModel):
    status: str
    count: int

class PatientTotal(BaseModel):
    patient_id: int
    patient_name: str
    total: float

class FinanceSummaryOut(BaseModel):
    month: str  # YYYY-MM
    total_month: float
    by_status: list[StatusCount]
    total_by_patient: list[PatientTotal]