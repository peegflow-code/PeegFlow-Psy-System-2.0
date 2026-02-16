from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.settings import settings
from app.models.user import User

# Swagger /docs usa isso para "Authorize"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Lê o JWT e garante:
    - sub (user_id) existe
    - tenant_id existe
    - user existe nesse tenant e está ativo
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        sub = payload.get("sub")
        tenant_id = payload.get("tenant_id")

        if sub is None or tenant_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")

        user_id = int(sub)
        tenant_id = int(tenant_id)

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


def get_tenant_id_or_401(current_user: User = Depends(get_current_user)) -> int:
    """
    Helper: devolve tenant_id do usuário autenticado.
    """
    if not current_user.tenant_id:
        raise HTTPException(status_code=401, detail="Tenant inválido")
    return current_user.tenant_id


def require_admin(user: User) -> None:
    """
    Protege rotas admin. Use assim:
      current_user: User = Depends(get_current_user)
      require_admin(current_user)
    """
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")


def require_patient(user: User) -> None:
    """
    Protege rotas de paciente.
    """
    if not user or user.role != "patient":
        raise HTTPException(status_code=403, detail="Apenas paciente")