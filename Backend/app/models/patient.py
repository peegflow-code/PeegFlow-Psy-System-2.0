from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)

    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)

    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="patient", lazy="joined")

    birth_date = Column(Date, nullable=True)
    sex = Column(String(20), nullable=True)
    marital_status = Column(String(30), nullable=True)
    address = Column(Text, nullable=True)
    occupation = Column(String(120), nullable=True)

    emergency_name = Column(String(120), nullable=True)
    emergency_phone = Column(String(40), nullable=True)

    document_id = Column(String(60), nullable=True)