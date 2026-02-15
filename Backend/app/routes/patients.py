from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.patient import Patient
from app.models.user import User
from app.schemas.patient import PatientCreateIn, PatientUpdateIn, PatientOut, PatientAccessIn
from app.deps import get_current_user, require_admin
from app.core.security import hash_password

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("", response_model=list[PatientOut])
def list_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    return db.query(Patient).order_by(Patient.full_name.asc()).all()


@router.post("", response_model=PatientOut)
def create_patient(
    data: PatientCreateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    if data.create_user and data.email:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Já existe um usuário com esse email")

    p = Patient(
        full_name=data.full_name,
        phone=data.phone,
        email=data.email,
        birth_date=data.birth_date,
        sex=data.sex,
        marital_status=data.marital_status,
        address=data.address,
        occupation=data.occupation,
        emergency_name=data.emergency_name,
        emergency_phone=data.emergency_phone,
        document_id=data.document_id,
    )

    if data.create_user:
        if not data.email:
            raise HTTPException(status_code=400, detail="Para criar acesso, o paciente precisa ter email")

        u = User(
            email=data.email,
            role="patient",
            is_active=True,
            password_hash=hash_password(data.user_password),
        )
        db.add(u)
        db.flush()
        p.user_id = u.id

    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.patch("/{patient_id}", response_model=PatientOut)
def update_patient(
    patient_id: int,
    data: PatientUpdateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(p, field, value)

    db.commit()
    db.refresh(p)
    return p


@router.delete("/{patient_id}/access")
def remove_patient_access(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    # ✅ Melhoria: desativa o user também (mantém histórico, mas remove acesso)
    if p.user_id:
        u = db.query(User).filter(User.id == p.user_id).first()
        if u and u.role == "patient":
            u.is_active = False

    p.user_id = None
    db.commit()
    return {"ok": True}


# ✅ NOVO: reativar/criar acesso do paciente
@router.post("/{patient_id}/access", response_model=PatientOut)
def create_or_restore_access(
    patient_id: int,
    data: PatientAccessIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    if not p.email:
        raise HTTPException(status_code=400, detail="Paciente precisa ter email para criar/reativar acesso")

    # tenta por user_id primeiro
    user = None
    if p.user_id:
        user = db.query(User).filter(User.id == p.user_id).first()

    # se não tiver, tenta pelo email
    if not user:
        user = db.query(User).filter(User.email == p.email).first()

    if user:
        user.role = "patient"
        user.is_active = True
        user.password_hash = hash_password(data.password)
    else:
        user = User(
            email=p.email,
            role="patient",
            is_active=True,
            password_hash=hash_password(data.password),
        )
        db.add(user)
        db.flush()

    p.user_id = user.id
    db.commit()
    db.refresh(p)
    return p


# ✅ NOVO: excluir paciente
@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    # opcional: desativa o usuário vinculado (mantém histórico, evita login futuro)
    if p.user_id:
        u = db.query(User).filter(User.id == p.user_id).first()
        if u and u.role == "patient":
            u.is_active = False

    db.delete(p)
    db.commit()
    return {"ok": True}