from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.settings import settings
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = int(payload.get("sub"))
        tenant_id = int(payload.get("tenant_id"))
    except (JWTError, TypeError, ValueError):
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

    return user


def require_admin(user: User):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Apenas admin")
    return True


def require_patient(user: User):
    if user.role != "patient":
        raise HTTPException(status_code=403, detail="Apenas paciente")
    return True