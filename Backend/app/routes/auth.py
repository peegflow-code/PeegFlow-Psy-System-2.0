from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import TokenOut, LoginTenantIn, RegisterTenantIn
from app.core.security import verify_password, create_access_token, hash_password
from app.models.user import User
from app.models.tenant import Tenant

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register-tenant", response_model=TokenOut)
def register_tenant(payload: RegisterTenantIn, db: Session = Depends(get_db)):
    slug = payload.tenant_slug.strip().lower()

    exists = db.query(Tenant).filter(Tenant.slug == slug).first()
    if exists:
        raise HTTPException(status_code=400, detail="Slug já existe")

    tenant = Tenant(name=payload.tenant_name.strip(), slug=slug)
    db.add(tenant)
    db.flush()  # pega tenant.id sem commit ainda

    # admin do tenant
    admin = User(
        tenant_id=tenant.id,
        email=payload.admin_email.lower().strip(),
        password_hash=hash_password(payload.admin_password),
        role="admin",
        is_active=True,
    )
    db.add(admin)
    db.commit()

    token = create_access_token(subject=str(user.id), tenant_id=tenant.id, role=user.role)
    return TokenOut(access_token=token, token_type="bearer")


@router.post("/login-tenant", response_model=TokenOut)
def login_tenant(payload: LoginTenantIn, db: Session = Depends(get_db)):
    slug = payload.tenant_slug.strip().lower()

    tenant = db.query(Tenant).filter(Tenant.slug == slug).first()
    if not tenant:
        raise HTTPException(status_code=401, detail="Consultório não encontrado")

    user = db.query(User).filter(
        User.tenant_id == tenant.id,
        User.email == payload.email.lower().strip(),
        User.is_active == True
    ).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = create_access_token(subject=str(admin.id), tenant_id=tenant.id, role=admin.role)
    return TokenOut(access_token=token, token_type="bearer")


# mantém /login para Swagger não “quebrar” (opcional)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends as _Depends

@router.post("/login", response_model=TokenOut, include_in_schema=False)
def login_swagger(form_data: OAuth2PasswordRequestForm = _Depends(), db: Session = Depends(get_db)):
    # fallback: espera username no formato slug|email
    raw = form_data.username.strip()
    if "|" not in raw:
        raise HTTPException(status_code=400, detail="Use username como: slug|email")

    slug, email = raw.split("|", 1)
    payload = LoginTenantIn(tenant_slug=slug, email=email, password=form_data.password)
    return login_tenant(payload, db)