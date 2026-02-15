from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from app.database import Base, engine, get_db
from app.core.security import decode_token, hash_password
from app.models.user import User
from app.routes import auth, patients, appointments, session_notes, admin

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código executado no STARTUP
    Base.metadata.create_all(bind=engine)
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        email = "admin@teste.com"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Só cria e define a senha se o usuário NÃO existir
            user = User(
                email=email, 
                role="admin", 
                is_active=True,
                password_hash=hash_password("123456")
            )
            db.add(user)
            db.commit()
            print("SEED ADMIN OK:", email)
    finally:
        db.close()
    yield
    # Código executado no SHUTDOWN (se necessário)

app = FastAPI(title="PeegFlow - Psy System API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(User).filter(User.id == int(user_id), User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user

def dep_current_user():
    return Depends(get_current_user)

app.include_router(auth.router)
app.include_router(patients.router, dependencies=[dep_current_user()])
app.include_router(appointments.router, dependencies=[dep_current_user()])
app.include_router(session_notes.router, dependencies=[dep_current_user()])
app.include_router(admin.router, dependencies=[dep_current_user()])

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/auth/me")
def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "role": current_user.role}

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

    from app.database import SessionLocal
    db = SessionLocal()
    try:
        email = "admin@teste.com"
        password = "123456"

        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, role="admin", is_active=True)
            db.add(user)

        # Sempre força a senha correta
        user.password_hash = hash_password(password)
        user.role = "admin"
        user.is_active = True

        db.commit()
        print("SEED ADMIN OK:", email)
    finally:
        db.close()