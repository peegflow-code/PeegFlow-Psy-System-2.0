from datetime import datetime, date
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.database import get_db
from app.models.session_note import SessionNote
from app.models.patient import Patient
from app.models.user import User
from app.schemas.session_note import (
    SessionNoteCreateIn,
    SessionNoteUpdateIn,
    SessionNoteOut,
)
from app.deps import get_current_user, require_admin

router = APIRouter(prefix="/session-notes", tags=["Session Notes"])


def _normalize_session_date(value):
    if value is None:
        return None

    if isinstance(value, date) and not isinstance(value, datetime):
        return value

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, str):
        v = value.strip()
        if not v:
            return None
        try:
            return datetime.strptime(v, "%Y-%m-%d").date()
        except Exception:
            pass
        try:
            return datetime.strptime(v, "%d/%m/%Y").date()
        except Exception:
            pass
        try:
            return datetime.fromisoformat(v).date()
        except Exception:
            pass

    return None


@router.post("", response_model=SessionNoteOut)
def create_note(
    data: SessionNoteCreateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    patient = (
        db.query(Patient)
        .filter(
            Patient.id == data.patient_id,
            Patient.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    parsed_date = _normalize_session_date(getattr(data, "session_date", None))
    session_date = parsed_date or datetime.utcnow().date()

    note = SessionNote(
        tenant_id=current_user.tenant_id,
        patient_id=data.patient_id,
        appointment_id=data.appointment_id,
        content=data.content,
        is_locked=data.is_locked or False,
        session_date=session_date,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.patch("/{note_id}", response_model=SessionNoteOut)
def update_note(
    note_id: int,
    data: SessionNoteUpdateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    note = (
        db.query(SessionNote)
        .filter(
            SessionNote.id == note_id,
            SessionNote.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Prontuário não encontrado")

    if note.is_locked:
        raise HTTPException(status_code=400, detail="Prontuário bloqueado")

    if data.content is not None:
        note.content = data.content

    if data.is_locked is not None:
        note.is_locked = data.is_locked

    parsed_date = _normalize_session_date(getattr(data, "session_date", None))
    if parsed_date is not None:
        note.session_date = parsed_date

    note.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(note)
    return note


@router.get("/patient/{patient_id}", response_model=list[SessionNoteOut])
def list_by_patient_month(
    patient_id: int,
    month: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    # garante que o paciente é do tenant
    patient = (
        db.query(Patient)
        .filter(
            Patient.id == patient_id,
            Patient.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    try:
        start = datetime.strptime(month + "-01", "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="month deve ser YYYY-MM")

    if start.month == 12:
        end = date(start.year + 1, 1, 1)
    else:
        end = date(start.year, start.month + 1, 1)

    notes = (
        db.query(SessionNote)
        .filter(
            SessionNote.tenant_id == current_user.tenant_id,
            SessionNote.patient_id == patient_id,
            SessionNote.session_date >= start,
            SessionNote.session_date < end,
        )
        .order_by(SessionNote.session_date.desc(), SessionNote.id.desc())
        .all()
    )
    return notes


def _pdf_for_note(note: SessionNote, patient_name: str) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 60
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "PeegFlow • Prontuário")
    y -= 30

    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Paciente: {patient_name}")
    y -= 18
    c.drawString(50, y, f"Data da sessão: {note.session_date.strftime('%d/%m/%Y') if note.session_date else '-'}")
    y -= 18
    c.drawString(50, y, f"Registrado em: {note.created_at.strftime('%d/%m/%Y %H:%M')}")
    y -= 18
    c.drawString(50, y, f"Bloqueado: {'Sim' if note.is_locked else 'Não'}")
    y -= 30

    c.setFont("Helvetica", 11)
    text = c.beginText(50, y)
    text.setLeading(14)

    content = note.content or ""
    for line in content.splitlines() or [""]:
        while len(line) > 110:
            text.textLine(line[:110])
            line = line[110:]
        text.textLine(line)

    c.drawText(text)
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.read()


@router.get("/{note_id}/pdf")
def download_pdf(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    note = (
        db.query(SessionNote)
        .filter(
            SessionNote.id == note_id,
            SessionNote.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Prontuário não encontrado")

    patient = (
        db.query(Patient)
        .filter(
            Patient.id == note.patient_id,
            Patient.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    patient_name = patient.full_name if patient else "Paciente"

    pdf_bytes = _pdf_for_note(note, patient_name)

    filename = f"prontuario_{note.id}.pdf"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers=headers,
    )