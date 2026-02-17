from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import decode_tenant_token

bearer = HTTPBearer(auto_error=True)

def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
    x_tenant_slug: str | None = Header(default=None, alias="X-Tenant-Slug"),
) -> User:
    token = cred.credentials
    payload = decode_tenant_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")

    try:
        user_id = int(payload.get("sub"))
        tenant_id = int(payload.get("tenant_id"))
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.tenant_id == tenant_id,
            User.is_active == True,
        )
        .first()
    )
    if not user:
        raise HTTPException(status_code=401, detail="Sessão inválida")

    # ✅ Kill switch/licença (recomendado)
    t = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not t or not t.is_active:
        raise HTTPException(status_code=403, detail="Tenant desativado")

    # (opcional) valida header X-Tenant-Slug
    if x_tenant_slug and t.slug != x_tenant_slug:
        raise HTTPException(status_code=401, detail="Tenant inválido")

    # (opcional) licença
    if t.license_expires_at is not None:
        from datetime import datetime
        if t.license_expires_at <= datetime.utcnow():
            raise HTTPException(status_code=403, detail="Licença expirada")

    return user

def require_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Apenas admin")
    return user

def require_patient(user: User = Depends(get_current_user)):
    if user.role != "patient":
        raise HTTPException(status_code=403, detail="Apenas paciente")
    return user