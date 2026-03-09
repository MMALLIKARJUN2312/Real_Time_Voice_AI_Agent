from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware  
from dotenv import load_dotenv
import os
import time
import asyncio
from services.stt import transcribe_audio
from services.language_detection import detect_language
from memory.memory import MemoryManager
from agent.agent import process_intent
from services.tts import synthesize_speech
from models.database import SessionLocal
from scheduler.campaigns import send_reminder
from api.endpoints import router as appointment_router
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from agent.agent import process_intent

load_dotenv()
mm = MemoryManager()

logger = logging.getLogger(__name__)

app = FastAPI(title="Voice AI Agent", description="Real-time multilingual appointment booking")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "running", "message": "Voice AI Agent Backend Ready"}

@app.websocket("/ws/voice")
async def websocket_voice(websocket: WebSocket, patient_id: str = "default_patient"):  
    await websocket.accept()
    session_id = str(time.time())
    db = SessionLocal()
    is_responding = False 
    try:
        while True:
            data = await websocket.receive_bytes()  
            start_time = time.perf_counter() 

            # Speech to Text
            stt_start = time.perf_counter()
            text, stt_lang = await transcribe_audio(data)
            stt_time = (time.perf_counter() - stt_start) * 1000
            if not text: await websocket.send_text("STT error"); continue

            # Detect language
            detect_start = time.perf_counter()
            lang = detect_language(text, stt_lang)
            context = await mm.get_context(session_id, patient_id) 
            lang = context.get("preferred_lang", lang)  
            await mm.set_persistent(patient_id, {"preferred_lang": lang}) 
            detect_time = (time.perf_counter() - detect_start) * 1000

            # Agent
            agent_start = time.perf_counter()
            intent_output = await process_intent(text, context, lang, db)
            response_text = intent_output.get("response", "Understood.")
            agent_time = (time.perf_counter() - agent_start) * 1000

            # Text to Speech
            if not is_responding:
                tts_start = time.perf_counter()
                audio_bytes = await synthesize_speech(response_text, lang)
                tts_time = (time.perf_counter() - tts_start) * 1000
                await websocket.send_bytes(audio_bytes)  
            else:
                is_responding = False  

            # Latency log
            total_time = (time.perf_counter() - start_time) * 1000
            logger.info(f"Latency: Total={total_time:.0f}ms | STT={stt_time:.0f} | Detect={detect_time:.0f} | Agent={agent_time:.0f} | TTS={tts_time:.0f}")
            if total_time > 450: logger.warning("Latency exceeded target!")

            # Update memory
            await mm.set_session(session_id, "last_input", text)
            await mm.set_session(session_id, "intent", intent_output["intent"])

    except WebSocketDisconnect:
        try:
            await websocket.send_text(
            "Sorry, something went wrong on our side. "
            "Please try speaking again or call back later."
        )
        except:
            db.close()
            print("Disconnected")
        
@app.post("/campaign/reminder")
async def schedule_reminder(patient_id: str, message: str, lang: str):
    send_reminder.delay(patient_id, message, lang)
    return {"status": "Scheduled"}

app.include_router(appointment_router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error – please try again later"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)