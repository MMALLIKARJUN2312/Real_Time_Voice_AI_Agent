from models.database import engine, SessionLocal
from models.models import Base, DoctorSchedule
import json
Base.metadata.create_all(bind=engine)
db = SessionLocal()
doc = DoctorSchedule(doctor_id="dr_mamatha", date="2026-03-10", available_slots=json.dumps(["10:00", "14:00", "16:30"]))
db.add(doc)
db.commit()