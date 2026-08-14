from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, primary_key=False, index=False, unique=True, nullable=False)
    # Relationship to cases claimed by this employee
    cases = relationship("Case", back_populates="claimed_by_employee")

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    patientName = Column(String, nullable=False)
    modality = Column(String, nullable=False)
    studyDate = Column(Date, nullable=False)
    status = Column(String, default="PENDING", nullable=False)  # PENDING, IN_PROGRESS, COMPLETED
    report = Column(Text, nullable=True)
    claimedAt = Column(DateTime, nullable=True)
    claimedBy = Column(Integer, ForeignKey("employees.id"), nullable=True)

    claimed_by_employee = relationship("Employee", back_populates="cases")