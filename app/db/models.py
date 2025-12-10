from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    mrn = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    person = relationship("Person", back_populates="patient", uselist=False, primaryjoin="Patient.id == foreign(Person.id)")
    visits = relationship("Visit", back_populates="patient")

class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    birth_date = Column(Date)

    patient = relationship("Patient", back_populates="person", primaryjoin="Patient.id == foreign(Person.id)")

class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True)
    visit_account_number = Column(String, unique=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    visit_date = Column(Date)
    reason = Column(String)

    patient = relationship("Patient", back_populates="visits")
