from sqlalchemy.orm import Session
from ..models.models import Appointment, DoctorSchedule
from datetime import datetime
import json

def check_availability(db: Session, doctor_id: str, date: str) -> list[str]:
    """
    Return available slots for doctor/date.
    Why: Prevents past/invalid bookings.
    """
    now = datetime.now()
    if datetime.strptime(f"{date} 00:00", "%Y-%m-%d %H:%M") < now: 
        return []
    sched = db.query(DoctorSchedule).filter(DoctorSchedule.doctor_id == doctor_id, DoctorSchedule.date == date).first()
    if not sched:
        return []  
    slots = json.loads(sched.available_slots)  
    booked = [a.time for a in db.query(Appointment).filter(Appointment.doctor_id == doctor_id, Appointment.date == date, Appointment.status == "booked").all()]
    available = [s for s in slots if s not in booked]  
    return available

def book_appointment(db: Session, patient_id: str, doctor_id: str, date: str, time: str) -> dict:
    avail = check_availability(db, doctor_id, date)
    if time not in avail:
        return {"success": False, "error": "Slot unavailable", "alternatives": avail[:3]}  
    appt = Appointment(patient_id=patient_id, doctor_id=doctor_id, date=date, time=time)
    db.add(appt)
    db.commit()
    return {"success": True, "message": f"Booked for {time} on {date}"}

def cancel_appointment(db: Session, appt_id: int) -> dict:
    appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if appt:
        appt.status = "cancelled"
        db.commit()
        return {"success": True}
    return {"success": False, "error": "Not found"}

def reschedule_appointment(db: Session, appt_id: int, new_date: str, new_time: str) -> dict:
    appt = db.query(Appointment).filter(Appointment.id == appt_id).first()
    if not appt:
        return {"success": False, "error": "Not found"}
    avail = check_availability(db, appt.doctor_id, new_date)
    if new_time not in avail:
        return {"success": False, "error": "Slot unavailable", "alternatives": avail[:3]}
    appt.date, appt.time = new_date, new_time
    db.commit()
    return {"success": True, "message": f"Rescheduled to {new_time} on {new_date}"}