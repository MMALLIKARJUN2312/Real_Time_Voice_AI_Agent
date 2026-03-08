import google.generativeai as genai
import json
import logging
from typing import Dict, Any
from ..services.scheduling import check_availability, book_appointment, cancel_appointment, reschedule_appointment
from ..models.database import SessionLocal
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOOLS = {
    "check_availability": check_availability,
    "book_appointment": book_appointment,
    "cancel_appointment": cancel_appointment,
    "reschedule_appointment": reschedule_appointment
}

PROMPT_TEMPLATE = """
You are a multilingual healthcare agent for appointment booking. Languages: English, Hindi, Tamil.
User: {user_input} | Context: {context} | Lang: {lang}

Reason step-by-step, then call tools if needed. Output JSON: {{"reasoning": "trace", "intent": "book/cancel/etc", "tool": "name", "params": {{"key":"val"}}, "response": "natural lang reply"}}

Available tools: {tools}
"""

async def process_intent(user_text: str, context: Dict[str, Any], lang: str, db) -> Dict[str, Any]:
    prompt = PROMPT_TEMPLATE.format(user_input=user_text, context=json.dumps(context), lang=lang, tools=list(TOOLS.keys()))
    response = model.generate_content(prompt)
    try:
        output = json.loads(response.text)  
        logger.info(f"Reasoning trace: {output['reasoning']}")  
        if output['tool'] in TOOLS:
            tool_func = TOOLS[output['tool']]
            params = output['params']
            result = tool_func(db, **params) 
            output['tool_result'] = result
        return output
    except json.JSONDecodeError:
        return {"response": "Sorry, I didn't understand. Please repeat.", "intent": "error"}