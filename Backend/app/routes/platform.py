from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.platform_admin import PlatformAdmin
from app.models.tenant import Tenant
from app.schemas.platform import PlatformLoginOut, TenantCreateIn, TenantOut
from app.core.security import verify_password, create_platform_token
from app.deps_platform import get_current_platform_admin

router = APIRouter(prefix="/platform", tags=["Platform"])

@router.post("/login", response_model=PlatformLoginOut)
def platform_login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = form.username
    password = form.password

    admin = db.query(PlatformAdmin).filter(
        PlatformAdmin.email == email,
        PlatformAdmin.is_active == True
    ).first()

    if not admin or not verify_password(password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = create_platform_token(subject=str(admin.id))
    return {"access_token": token, "token_type": "bearer"}

@router.post("/tenants", response_model=TenantOut)
def create_tenant(
    data: TenantCreateIn,
    db: Session = Depends(get_db),
    _: PlatformAdmin = Depends(get_current_platform_admin),
):
    exists = db.query(Tenant).filter(Tenant.slug == data.slug).first()
    if exists:
        raise HTTPException(status_code=400, detail="Slug já existe")

    t = Tenant(
        name=data.name,
        slug=data.slug,
        is_active=data.is_active,
        license_expires_at=data.license_expires_at,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t

@router.get("/tenants", response_model=list[TenantOut])
def list_tenants(
    db: Session = Depends(get_db),
    _: PlatformAdmin = Depends(get_current_platform_admin),
):
    return db.query(Tenant).order_by(Tenant.created_at.desc()).all()