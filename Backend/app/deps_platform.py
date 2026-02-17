from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.platform_admin import PlatformAdmin
from app.core.security import decode_platform_token

bearer = HTTPBearer(auto_error=True)

def get_current_platform_admin(
    cred: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> PlatformAdmin:
    token = cred.credentials
    admin_id = decode_platform_token(token)
    if not admin_id:
        raise HTTPException(status_code=401, detail="Token inválido")

    admin = (
        db.query(PlatformAdmin)
        .filter(PlatformAdmin.id == admin_id, PlatformAdmin.is_active == True)
        .first()
    )
    if not admin:
        raise HTTPException(status_code=401, detail="Token inválido")

    return admin