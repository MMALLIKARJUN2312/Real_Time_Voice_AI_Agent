from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .database import Base
from datetime import datetime

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, index=True) 
    doctor_id = Column(String, index=True)
    date = Column(String)  
    time = Column(String)  
    status = Column(String, default="booked") 
    created_at = Column(DateTime, default=datetime.utcnow)

class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(String, index=True)
    date = Column(String)
    available_slots = Column(String) 
    updated_at = Column(DateTime, default=datetime.utcnow)