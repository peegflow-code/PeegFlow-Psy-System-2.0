from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.platform_admin import PlatformAdmin
from app.core.security import decode_platform_token

oauth2_platform = OAuth2PasswordBearer(tokenUrl="/platform/login")

def get_current_platform_admin(
    token: str = Depends(oauth2_platform),
    db: Session = Depends(get_db),
) -> PlatformAdmin:
    sub = decode_platform_token(token)
    if not sub:
        raise HTTPException(status_code=401, detail="Token inválido (platform)")

    admin = db.query(PlatformAdmin).filter(
        PlatformAdmin.id == int(sub),
        PlatformAdmin.is_active == True
    ).first()

    if not admin:
        raise HTTPException(status_code=401, detail="Sessão inválida")

    return admin