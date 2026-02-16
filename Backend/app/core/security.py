from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.settings import settings

# ✅ Argon2 primeiro (padrão). Bcrypt só como fallback (se tiver hash antigo)
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 dias

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(*, subject: str, tenant_id: int) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "tenant_id": tenant_id,
        "iat": int(now.timestamp()),
        "exp": exp,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)

def create_platform_token(*, subject: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=PLATFORM_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "type": "platform_admin",
        "iat": int(now.timestamp()),
        "exp": exp,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=PLATFORM_ALGORITHM)

def decode_platform_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[PLATFORM_ALGORITHM])
        if payload.get("type") != "platform_admin":
            return None
        return int(payload.get("sub"))
    except Exception:
        return None