from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime, date


class FinanceSummaryOut(BaseModel):
    period: str
    income_total: float
    expense_total: float
    cash_total: float

    # contagens por status
    status_counts: dict[str, int]

    # série diária (somente no modo mês)
    daily_income: list[dict[str, Any]]


class ExpenseIn(BaseModel):
    title: str
    amount: float
    spent_at: date | datetime
    notes: Optional[str] = None


class ExpenseOut(BaseModel):
    id: int
    title: str
    amount: float
    spent_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True