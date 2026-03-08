from celery import Celery
import asyncio
from ..main import app 

celery = Celery('campaigns', broker='redis://localhost:6379', backend='redis://localhost:6379')  

@celery.task
def send_reminder(patient_id: str, message: str, lang: str):
    """
    Outbound: Init WS call, send TTS message, handle response.
    Why: Background for scale; simulate full Twilio integration.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print(f"Outbound to {patient_id}: {message} in {lang}")  
    loop.close()
    return "Sent"

