from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    user_id, tenant_id = decode_token(token)

    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.tenant_id == tenant_id,
            User.is_active == True
        )
        .first()
    )
    if not user:
        raise HTTPException(status_code=401, detail="Sessão inválida")

    return user


def require_admin(user: User):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Apenas admin")


def require_platform_admin(user: User):
    if user.role != "platform_admin":
        raise HTTPException(status_code=403, detail="Apenas dona do sistema (platform_admin)")