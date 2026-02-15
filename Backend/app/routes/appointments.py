from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.appointment import Appointment
from app.models.user import User
from app.models.patient import Patient
from app.schemas.appointment import AppointmentOut, BookIn, CancelIn, BulkGenerateIn, SetStatusIn
from app.deps import get_current_user, require_admin

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def _as_out(appt: Appointment, patient: Patient | None):
    out = AppointmentOut.model_validate(appt)
    if patient:
        out.patient_name = patient.full_name
        out.patient_email = patient.email
    return out


@router.get("/range", response_model=list[AppointmentOut])
def range_list(
    date_from: str,
    date_to: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Admin: vê todos os horários no range (available/booked/done/canceled/no_show)
    Patient: vê apenas os próprios agendamentos
    """
    try:
        d1 = datetime.strptime(date_from, "%Y-%m-%d")
        d2 = datetime.strptime(date_to, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Use date_from/date_to como YYYY-MM-DD")

    start = datetime(d1.year, d1.month, d1.day, 0, 0, 0)
    end = datetime(d2.year, d2.month, d2.day, 23, 59, 59)

    q = db.query(Appointment).filter(Appointment.start_at >= start, Appointment.start_at <= end)

    if current_user.role == "patient":
        q = q.filter(Appointment.patient_user_id == current_user.id)

    appts = q.order_by(Appointment.start_at.asc()).all()

    # pega pacientes relacionados (por user_id)
    user_ids = [a.patient_user_id for a in appts if a.patient_user_id]
    patients_map = {}
    if user_ids:
        pts = db.query(Patient).filter(Patient.user_id.in_(user_ids)).all()
        patients_map = {p.user_id: p for p in pts}

    return [_as_out(a, patients_map.get(a.patient_user_id)) for a in appts]


@router.get("/available", response_model=list[AppointmentOut])
def available(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    appts = (
        db.query(Appointment)
        .filter(Appointment.status == "available")
        .order_by(Appointment.start_at.asc())
        .all()
    )
    return [AppointmentOut.model_validate(a) for a in appts]


@router.get("/mine", response_model=list[AppointmentOut])
def mine(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Apenas paciente")

    appts = (
        db.query(Appointment)
        .filter(Appointment.patient_user_id == current_user.id)
        .order_by(Appointment.start_at.desc())
        .all()
    )
    return [AppointmentOut.model_validate(a) for a in appts]


@router.post("/book", response_model=AppointmentOut)
def book(data: BookIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Apenas paciente")

    appt = db.query(Appointment).filter(Appointment.id == data.appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    if appt.status != "available":
        raise HTTPException(status_code=400, detail="Horário indisponível")

    appt.status = "booked"
    appt.patient_user_id = current_user.id
    db.commit()
    db.refresh(appt)

    # para o paciente não precisa de nome, mas não atrapalha
    patient = db.query(Patient).filter(Patient.user_id == appt.patient_user_id).first()
    return _as_out(appt, patient)


@router.post("/cancel", response_model=AppointmentOut)
def cancel(data: CancelIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    appt = db.query(Appointment).filter(Appointment.id == data.appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")

    if current_user.role == "patient":
        if appt.patient_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Não é sua consulta")
        if appt.status != "booked":
            raise HTTPException(status_code=400, detail="Só booked pode ser cancelada pelo paciente")

    if current_user.role == "admin":
        # admin pode cancelar booked (e até available se quiser “bloquear”)
        if appt.status not in ("booked", "available"):
            raise HTTPException(status_code=400, detail="Status inválido para cancelamento")

    appt.status = "canceled"
    db.commit()
    db.refresh(appt)
    patient = db.query(Patient).filter(Patient.user_id == appt.patient_user_id).first() if appt.patient_user_id else None
    return _as_out(appt, patient)


@router.post("/set-status", response_model=AppointmentOut)
def set_status(data: SetStatusIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Admin marca: done (compareceu), no_show (faltou), canceled (cancelada).
    """
    require_admin(current_user)

    appt = db.query(Appointment).filter(Appointment.id == data.appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")

    # regra simples: só faz sentido alterar se já existe horário
    # booked -> done/no_show/canceled
    # available -> (não mexe normalmente)
    if appt.status == "available" and data.status in ("done", "no_show"):
        raise HTTPException(status_code=400, detail="Não dá pra marcar done/no_show em horário disponível (sem paciente)")

    appt.status = data.status
    db.commit()
    db.refresh(appt)

    patient = db.query(Patient).filter(Patient.user_id == appt.patient_user_id).first() if appt.patient_user_id else None
    return _as_out(appt, patient)


@router.post("/bulk")
def bulk_generate(data: BulkGenerateIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_admin(current_user)

    try:
        day = datetime.strptime(data.date, "%Y-%m-%d").date()
        start_t = datetime.strptime(data.start_time, "%H:%M").time()
        end_t = datetime.strptime(data.end_time, "%H:%M").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato inválido. Use date=YYYY-MM-DD e time=HH:MM")

    start_dt = datetime.combine(day, start_t)
    end_dt = datetime.combine(day, end_t)

    if end_dt <= start_dt:
        raise HTTPException(status_code=400, detail="end_time deve ser maior que start_time")

    created = 0
    cur = start_dt
    dur = timedelta(minutes=data.duration_minutes)

    while cur + dur <= end_dt:
        exists = (
            db.query(Appointment)
            .filter(Appointment.start_at == cur, Appointment.end_at == cur + dur)
            .first()
        )
        if not exists:
            db.add(
                Appointment(
                    start_at=cur,
                    end_at=cur + dur,
                    status="available",
                    price=float(data.price),
                    patient_user_id=None,
                )
            )
            created += 1
        cur += dur

    db.commit()
    return {"created": created}