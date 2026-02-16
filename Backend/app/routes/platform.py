from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.platform_admin import PlatformAdmin
from app.models.tenant import Tenant
from app.schemas.platform_auth import PlatformLoginIn, PlatformTokenOut
from app.schemas.tenant import TenantCreateIn, TenantOut
from app.core.security import verify_password, hash_password
from jose import jwt
from app.settings import settings

router = APIRouter(prefix="/platform", tags=["Platform"])

PLATFORM_ALG = "HS256"

def create_platform_token(admin_id: int) -> str:
    payload = {"sub": str(admin_id), "iat": int(datetime.utcnow().timestamp())}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=PLATFORM_ALG)

def get_platform_admin(token: str = Depends(lambda: None), db: Session = Depends(get_db)) -> PlatformAdmin:
    """
    Para simplificar sem mexer no OAuth2 agora:
    - Você chama com header: Authorization: Bearer <token>
    - E a gente valida aqui.
    """
    # pega header manualmente via fastapi (jeito simples sem OAuth2PasswordBearer)
    # se quiser, eu te mando a versão com OAuth2 certinha depois.
    raise HTTPException(status_code=501, detail="Implemente via deps (vou te passar abaixo)")

@router.post("/seed-admin")
def seed_platform_admin(db: Session = Depends(get_db)):
    """
    Só para começar. Depois você remove essa rota.
    """
    email = "owner@peegflow.com"
    pwd = "123456"
    exists = db.query(PlatformAdmin).filter(PlatformAdmin.email == email).first()
    if exists:
        return {"ok": True, "message": "Já existe"}

    a = PlatformAdmin(email=email, password_hash=hash_password(pwd), is_active=True)
    db.add(a)
    db.commit()
    return {"ok": True, "email": email, "password": pwd}

@router.post("/login", response_model=PlatformTokenOut)
def platform_login(data: PlatformLoginIn, db: Session = Depends(get_db)):
    admin = db.query(PlatformAdmin).filter(
        PlatformAdmin.email == data.email,
        PlatformAdmin.is_active == True
    ).first()
    if not admin or not verify_password(data.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = create_platform_token(admin.id)
    return PlatformTokenOut(access_token=token, token_type="bearer")

@router.post("/tenants", response_model=TenantOut)
def create_tenant(data: TenantCreateIn, db: Session = Depends(get_db)):
    # (Depois a gente protege com auth de platform)
    exists = db.query(Tenant).filter(Tenant.slug == data.slug).first()
    if exists:
        raise HTTPException(status_code=400, detail="Slug já existe")

    t = Tenant(
        name=data.name,
        slug=data.slug,
        is_active=data.is_active,
        license_expires_at=data.license_expires_at
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t

@router.get("/tenants", response_model=list[TenantOut])
def list_tenants(db: Session = Depends(get_db)):
    return db.query(Tenant).order_by(Tenant.created_at.desc()).all()

@router.patch("/tenants/{tenant_id}", response_model=TenantOut)
def update_tenant(
    tenant_id: int,
    is_active: bool | None = None,
    license_expires_at: datetime | None = None,
    db: Session = Depends(get_db),
):
    t = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    if is_active is not None:
        t.is_active = is_active
    if license_expires_at is not None:
        t.license_expires_at = license_expires_at

    db.commit()
    db.refresh(t)
    return t