from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from ..dependencies import get_db
from ..services.scheduling import (
    check_availability,
    book_appointment,
    cancel_appointment,
    reschedule_appointment,
)

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

# Input schemas 

class AvailabilityRequest(BaseModel):
    doctor_id: str
    date: str  


class BookRequest(BaseModel):
    patient_id: str
    doctor_id: str
    date: str  
    time: str  

class CancelRequest(BaseModel):
    appointment_id: int


class RescheduleRequest(BaseModel):
    appointment_id: int
    new_date: str
    new_time: str


# Response schemas

class AvailabilityResponse(BaseModel):
    available_slots: List[str]
    doctor_id: str
    date: str


class BookingResponse(BaseModel):
    success: bool
    message: str
    appointment_id: Optional[int] = None
    alternatives: Optional[List[str]] = None


class SimpleResponse(BaseModel):
    success: bool
    message: str


# Endpoints

@router.post("/availability", response_model=AvailabilityResponse)
def get_availability(
    req: AvailabilityRequest,
    db: Session = Depends(get_db)
):
    """Check available time slots for a doctor on a specific date"""
    slots = check_availability(db, req.doctor_id, req.date)
    if not slots:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No available slots or invalid doctor/date"
        )
    return {
        "available_slots": slots,
        "doctor_id": req.doctor_id,
        "date": req.date
    }


@router.post("/book", response_model=BookingResponse)
def book_appointment_api(
    req: BookRequest,
    db: Session = Depends(get_db)
):
    """Create a new appointment"""
    result = book_appointment(
        db,
        patient_id=req.patient_id,
        doctor_id=req.doctor_id,
        date=req.date,
        time=req.time
    )

    if result["success"]:
        # In real app you'd return the created appointment ID
        # For simplicity we return just success + message
        return {
            "success": True,
            "message": result["message"],
            "appointment_id": None  # can be improved later
        }
    else:
        return {
            "success": False,
            "message": result.get("error", "Booking failed"),
            "alternatives": result.get("alternatives")
        }


@router.post("/cancel", response_model=SimpleResponse)
def cancel_appointment_api(
    req: CancelRequest,
    db: Session = Depends(get_db)
):
    """Cancel an existing appointment by ID"""
    result = cancel_appointment(db, req.appointment_id)
    if result["success"]:
        return {"success": True, "message": "Appointment cancelled successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("error", "Appointment not found")
        )


@router.post("/reschedule", response_model=BookingResponse)
def reschedule_appointment_api(
    req: RescheduleRequest,
    db: Session = Depends(get_db)
):
    """Change date/time of an existing appointment"""
    result = reschedule_appointment(
        db,
        appt_id=req.appointment_id,
        new_date=req.new_date,
        new_time=req.new_time
    )

    if result["success"]:
        return {
            "success": True,
            "message": result["message"],
            "appointment_id": req.appointment_id
        }
    else:
        return {
            "success": False,
            "message": result.get("error", "Reschedule failed"),
            "alternatives": result.get("alternatives")
        }