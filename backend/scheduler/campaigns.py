from celery import Celery
import asyncio
import os
from services.stt import transcribe_audio # Example absolute import

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery = Celery('campaigns', broker=REDIS_URL, backend=REDIS_URL)  

@celery.task
def send_reminder(patient_id: str, message: str, lang: str):
    """
    How: Triggered via Redis queue.
    Why: Handles the 'Outbound Campaign' requirement.
    """
    print(f"PROACTIVE OUTREACH: Calling Patient {patient_id}...")
    print(f"MESSAGE ({lang}): {message}")
    
    return f"Reminder successful for {patient_id}"