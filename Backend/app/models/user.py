from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id"), index=True, nullable=False)
    tenant = relationship("Tenant", back_populates="users")

    email: Mapped[str] = mapped_column(String, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, default="patient")  # admin | patient
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    patient = relationship("Patient", back_populates="user", uselist=False)

    # IMPORTANTE:
    # Para multi-tenant, o "unique" do email não pode ser global.
    # Depois: criar UNIQUE(tenant_id, email) via SQL.