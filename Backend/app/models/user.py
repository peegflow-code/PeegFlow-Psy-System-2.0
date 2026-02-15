from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, default="patient")  # "admin" | "patient"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

     # 🔽 RELAÇÃO 1:1 COM PATIENT
    patient = relationship(
        "Patient",
        back_populates="user",
        uselist=False
    )