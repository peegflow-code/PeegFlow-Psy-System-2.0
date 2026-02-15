from datetime import datetime, date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.appointment import Appointment
from app.models.expense import Expense
from app.schemas.admin import FinanceSummaryOut, ExpenseIn, ExpenseOut
from app.deps import get_current_user, require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


def _parse_month(month: str) -> tuple[datetime, datetime]:
    try:
        start = datetime.strptime(month + "-01", "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="month deve ser YYYY-MM")
    if start.month == 12:
        end = datetime(start.year + 1, 1, 1)
    else:
        end = datetime(start.year, start.month + 1, 1)
    return start, end


def _parse_day(day: str) -> tuple[datetime, datetime]:
    try:
        d = datetime.strptime(day, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="day deve ser YYYY-MM-DD")
    start = datetime.combine(d, datetime.min.time())
    end = start + timedelta(days=1)
    return start, end


def _parse_range(date_from: str, date_to: str) -> tuple[datetime, datetime]:
    """
    date_from/date_to: YYYY-MM-DD
    range inclusivo (até 23:59:59 do date_to)
    """
    try:
        d1 = datetime.strptime(date_from, "%Y-%m-%d").date()
        d2 = datetime.strptime(date_to, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="date_from/date_to deve ser YYYY-MM-DD")

    start = datetime.combine(d1, datetime.min.time())
    end = datetime.combine(d2, datetime.max.time())  # 23:59:59.999999
    return start, end


@router.get("/finance/summary", response_model=FinanceSummaryOut)
def finance_summary(
    # ✅ NOVO: período custom (preferência máxima)
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,

    # antigos (mantidos pra compatibilidade)
    month: Optional[str] = None,
    day: Optional[str] = None,

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    # 1) Se vier date_from/date_to: usa isso
    if date_from and date_to:
        start, end = _parse_range(date_from, date_to)
        period = f"{date_from} → {date_to}"

    # 2) Se vier day: usa day
    elif day:
        start, end = _parse_day(day)
        period = day

    # 3) Senão usa month (ou mês atual)
    else:
        month = month or datetime.utcnow().strftime("%Y-%m")
        start, end = _parse_month(month)
        period = month

    # Entradas: consultas concluídas (done)
    done_appts = (
        db.query(Appointment)
        .filter(Appointment.status == "done")
        .filter(Appointment.start_at >= start, Appointment.start_at <= end)
        .all()
    )
    income = float(sum((a.price or 0) for a in done_appts))

    # Despesas
    expenses = (
        db.query(Expense)
        .filter(Expense.spent_at >= start, Expense.spent_at <= end)
        .order_by(Expense.spent_at.desc())
        .all()
    )
    expense_total = float(sum((e.amount or 0) for e in expenses))

    cash = income - expense_total

    # Série diária (para gráfico em linha)
    daily_income = []
    # só faz daily se o período for maior que 1 dia
    days_span = (end.date() - start.date()).days
    if days_span >= 1:
        cur = datetime.combine(start.date(), datetime.min.time())
        last = datetime.combine(end.date(), datetime.min.time()) + timedelta(days=1)

        while cur < last:
            nxt = cur + timedelta(days=1)
            day_sum = 0.0
            for a in done_appts:
                if a.start_at >= cur and a.start_at < nxt:
                    day_sum += float(a.price or 0)
            daily_income.append({"day": cur.strftime("%Y-%m-%d"), "income": round(day_sum, 2)})
            cur = nxt

    # Contagens por status
    status_counts = {"available": 0, "booked": 0, "done": 0, "canceled": 0}
    appts_all = (
        db.query(Appointment)
        .filter(Appointment.start_at >= start, Appointment.start_at <= end)
        .all()
    )
    for a in appts_all:
        if a.status in status_counts:
            status_counts[a.status] += 1

    return {
        "period": period,
        "income_total": round(income, 2),
        "expense_total": round(expense_total, 2),
        "cash_total": round(cash, 2),
        "status_counts": status_counts,
        "daily_income": daily_income,
    }


@router.get("/expenses", response_model=list[ExpenseOut])
def list_expenses(
    # ✅ pode listar por month (mantém)
    month: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    start, end = _parse_month(month)
    return (
        db.query(Expense)
        .filter(Expense.spent_at >= start, Expense.spent_at < end)
        .order_by(Expense.spent_at.desc())
        .all()
    )


@router.post("/expenses", response_model=ExpenseOut)
def create_expense(
    data: ExpenseIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    spent_at = data.spent_at
    if isinstance(spent_at, date):
        spent_at = datetime.combine(spent_at, datetime.min.time())

    e = Expense(
        title=data.title,
        amount=float(data.amount),
        spent_at=spent_at,
        notes=data.notes,
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


@router.delete("/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    e = db.query(Expense).filter(Expense.id == expense_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    db.delete(e)
    db.commit()
    return {"ok": True}