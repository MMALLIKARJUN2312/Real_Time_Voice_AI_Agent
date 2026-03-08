from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware  
import os
from dotenv import load_dotenv

load_dotenv()

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
async def websocket_voice(websocket: WebSocket):
    await websocket.accept()  
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")  
    except WebSocketDisconnect:
        print("Client disconnected")  

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)