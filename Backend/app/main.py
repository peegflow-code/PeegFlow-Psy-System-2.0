from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from datetime import datetime

from app.database import Base, engine, SessionLocal

# IMPORTA MODELS para o create_all enxergar tudo
from app.models import (
    user, tenant, patient, appointment, session_note, expense, platform_admin
)
from app.models.user import User
from app.models.tenant import Tenant
from app.models.platform_admin import PlatformAdmin

from app.core.security import hash_password

# ROUTERS
from app.routes import auth, patients, appointments, session_notes, admin
# ✅ NOVO: rota da dona do sistema (SuperAdmin)
from app.routes import platform


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ----------------------------
    # STARTUP
    # ----------------------------
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # ============================
        # 1) SEED: PLATFORM OWNER (VOCÊ)
        # ============================
        # Configure no Render/ENV:
        # PLATFORM_ADMIN_EMAIL=PeegFlow@gmail.com
        # PLATFORM_ADMIN_PASSWORD=... (não commitar)
        owner_email = os.getenv("PLATFORM_ADMIN_EMAIL")
        owner_password = os.getenv("PLATFORM_ADMIN_PASSWORD")

        if owner_email and owner_password:
            existing_owner = db.query(PlatformAdmin).filter(PlatformAdmin.email == owner_email).first()
            if not existing_owner:
                db.add(
                    PlatformAdmin(
                        email=owner_email,
                        password_hash=hash_password(owner_password),
                        is_active=True,
                    )
                )
                db.commit()
                print("✅ PLATFORM OWNER seeded:", owner_email)

        # ============================
        # 2) SEED: TENANT DEFAULT (1o psicólogo/cliente)
        # ============================
        # Configure no Render/ENV (exemplo):
        # DEFAULT_TENANT_NAME=Cliente Demo
        # DEFAULT_TENANT_SLUG=demo
        tenant_name = os.getenv("DEFAULT_TENANT_NAME", "Cliente Demo")
        tenant_slug = os.getenv("DEFAULT_TENANT_SLUG", "demo")

        t = db.query(Tenant).filter(Tenant.slug == tenant_slug).first()
        if not t:
            t = Tenant(
                name=tenant_name,
                slug=tenant_slug,
                is_active=True,
                license_expires_at=None,  # você controla depois via plataforma
            )
            db.add(t)
            db.commit()
            db.refresh(t)
            print("✅ DEFAULT TENANT seeded:", tenant_slug)

        # ============================
        # 3) SEED: ADMIN DO TENANT
        # ============================
        # Configure no Render/ENV (exemplo):
        # DEFAULT_ADMIN_EMAIL=admin@teste.com
        # DEFAULT_ADMIN_PASSWORD=123456
        admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@teste.com")
        admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "123456")

        # ⚠️ IMPORTANTE: email pode repetir em outro tenant no futuro,
        # então o ideal é (tenant_id + email) ser único.
        # Por agora vamos buscar por tenant + email.
        tenant_admin = (
            db.query(User)
            .filter(User.email == admin_email)
            .filter(User.tenant_id == t.id)
            .first()
        )

        if not tenant_admin:
            tenant_admin = User(
                email=admin_email,
                role="admin",
                is_active=True,
                tenant_id=t.id,
                password_hash=hash_password(admin_password),
            )
            db.add(tenant_admin)
            db.commit()
            print("✅ TENANT ADMIN seeded:", admin_email, "tenant:", tenant_slug)

    finally:
        db.close()

    yield

    # ----------------------------
    # SHUTDOWN (opcional)
    # ----------------------------


app = FastAPI(title="PeegFlow - Psy System API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # depois você restringe pro domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Rotas normais
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(session_notes.router)
app.include_router(admin.router)

# ✅ Rotas da dona do sistema (SuperAdmin / Platform)
app.include_router(platform.router)


@app.get("/health")
def health():
    return {"status": "ok", "ts": datetime.utcnow().isoformat()}