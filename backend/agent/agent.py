import os
import json
import logging
from typing import Dict, Any
from google import genai
from google.genai import types
from dotenv import load_dotenv

from services.scheduling import (
    check_availability as service_check_availability, 
    book_appointment as service_book_appointment, 
    cancel_appointment as service_cancel_appointment, 
    reschedule_appointment as service_reschedule_appointment
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def check_clinic_availability(date: str) -> str:
    """Checks for available appointment slots on a given date (YYYY-MM-DD)."""
    result = service_check_availability(date)
    return json.dumps(result)

def book_clinic_appointment(patient_id: str, date: str, slot: str) -> str:
    """Books an appointment for a patient (YYYY-MM-DD, e.g., '10:00 AM')."""
    result = service_book_appointment(patient_id, date, slot)
    return json.dumps(result)

def cancel_clinic_appointment(appointment_id: str) -> str:
    """Cancels an existing appointment using its ID."""
    result = service_cancel_appointment(appointment_id)
    return json.dumps(result)

def reschedule_clinic_appointment(appointment_id: str, new_date: str, new_slot: str) -> str:
    """Moves an appointment to a new date and time."""
    result = service_reschedule_appointment(appointment_id, new_date, new_slot)
    return json.dumps(result)

clinical_tools = [
    check_clinic_availability, 
    book_clinic_appointment, 
    cancel_clinic_appointment, 
    reschedule_clinic_appointment
]

SYSTEM_INSTRUCTION = """
You are a multilingual clinical AI agent for 'Apollo Clinics'. 
Languages: English, Hindi, Tamil.
Behavior: Respond in the user's language. Suggest alternatives if slots are full.
"""

config = types.GenerateContentConfig(
    system_instruction=SYSTEM_INSTRUCTION,
    tools=clinical_tools,
)

async def process_intent(user_text: str, context: Dict[str, Any], lang: str) -> Dict[str, Any]:
    """
    Handles the interaction using the new generate_content unified method.
    """
    full_prompt = f"Patient Context: {json.dumps(context)} | User Message: {user_text}"
    
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=full_prompt,
            config=config
        )

        if response.candidates[0].grounding_metadata:
            logger.info("Tool use or grounding occurred.")

        return {
            "response": response.text,
            "intent": "processed",
        }
    except Exception as e:
        logger.error(f"Agent Error: {e}")
        return {
            "response": "I'm having trouble with the connection. Please try again.",
            "intent": "error"
        }