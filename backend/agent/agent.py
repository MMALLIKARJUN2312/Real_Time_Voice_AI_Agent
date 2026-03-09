import os
import json
import logging
from typing import Dict, Any
from services.scheduling import (
    check_availability, 
    book_appointment, 
    cancel_appointment, 
    reschedule_appointment
)
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

clinical_tools = [
    check_availability, 
    book_appointment, 
    cancel_appointment, 
    reschedule_appointment
]

SYSTEM_INSTRUCTION = """
You are a multilingual clinical AI agent for 'Apollo Clinics'. 
Languages: English, Hindi, Tamil.
Capabilities: Book, cancel, reschedule, and check availability.
Behavior:
1. Always identify the user's language and respond in the same.
2. If a conflict occurs, suggest the next two available slots.
3. Be concise for voice interaction.
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    tools=clinical_tools,
    system_instruction=SYSTEM_INSTRUCTION
)

async def process_intent(user_text: str, context: Dict[str, Any], lang: str) -> Dict[str, Any]:
    """
    How: Uses Gemini's chat session with automatic function calling.
    Why: Handles 'Real-world messiness' (conflicts/changes of mind) natively.
    """
    chat = model.start_chat(enable_automatic_function_calling=True)
    
    full_prompt = f"Patient Context: {json.dumps(context)} | User Message: {user_text}"
    
    try:
        response = chat.send_message(full_prompt)
        
        logger.info(f"Agent reasoning for lang [{lang}]: {response.candidates[0].grounding_metadata}")

        return {
            "response": response.text,
            "intent": "processed",
            "reasoning_trace": "Grounding successful"
        }
    except Exception as e:
        logger.error(f"Agent Error: {e}")
        return {
            "response": "I encountered an error. How can I help you differently?",
            "intent": "error"
        }