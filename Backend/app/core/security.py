from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.settings import settings

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 dias

def _tenant_secret() -> str:
    # ✅ recomendado: setar TENANT_SECRET_KEY no Render
    return getattr(settings, "TENANT_SECRET_KEY", None) or settings.SECRET_KEY

def _platform_secret() -> str:
    # ✅ recomendado: setar PLATFORM_SECRET_KEY no Render
    return getattr(settings, "PLATFORM_SECRET_KEY", None) or settings.SECRET_KEY

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# ✅ token do tenant (admin/patient)
def create_access_token(*, subject: str, tenant_id: int, role: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "tenant_id": tenant_id,
        "role": role,           # ✅ crucial
        "type": "tenant",       # ✅ crucial
        "iat": int(now.timestamp()),
        "exp": exp,
    }
    return jwt.encode(payload, _tenant_secret(), algorithm=ALGORITHM)

# ✅ token da plataforma (dona do SaaS)
def create_platform_token(*, subject: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "type": "platform_admin",
        "iat": int(now.timestamp()),
        "exp": exp,
    }
    return jwt.encode(payload, _platform_secret(), algorithm=ALGORITHM)

def decode_tenant_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, _tenant_secret(), algorithms=[ALGORITHM])
        if payload.get("type") != "tenant":
            return None
        return payload
    except Exception:
        return None

def decode_platform_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, _platform_secret(), algorithms=[ALGORITHM])
        if payload.get("type") != "platform_admin":
            return None
        return int(payload.get("sub"))
    except Exception:
        return None