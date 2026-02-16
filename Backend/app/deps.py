from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.core.security import decode_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
        tenant_id = int(payload.get("tenant_id"))
    except (JWTError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(User).filter(
        User.id == user_id,
        User.tenant_id == tenant_id,
        User.is_active == True
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Sessão inválida")

    # ✅ kill switch / licença
    if not user.tenant.is_active:
        raise HTTPException(status_code=403, detail="Conta desativada")

    if user.tenant.license_expires_at and user.tenant.license_expires_at < datetime.utcnow():
        raise HTTPException(status_code=403, detail="Licença expirada")

    return user

def require_admin(user: User):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Apenas admin")