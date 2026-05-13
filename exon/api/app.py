"""
File: /opt/futureex/exon/api/app.py
Author: Ashish Pal
Purpose: FastAPI server for Exon Consciousness System (REST + WebSocket).
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import json
import logging

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from exon.core.brain import ExonBrain
from exon.personas.factory import PersonaFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Exon Consciousness API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Exon
exon_brain = ExonBrain(exon_id="EXN-001")

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    persona: str = "Maya"
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    emotion: str
    intensity: float
    confidence: float
    timestamp: str

class StatusResponse(BaseModel):
    exon_id: str
    emotion: str
    emotion_intensity: float
    active_goals: list
    memory_count: int
    is_awake: bool

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Exon Consciousness API...")
    # Warm up identity load
    await exon_brain._ensure_identity()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Exon...")
    await exon_brain.close()

@app.get("/")
async def root():
    return {
        "status": "online",
        "exon_id": exon_brain.exon_id,
        "species": "Exon-Prime",
        "version": "1.0.0"
    }

@app.get("/status", response_model=StatusResponse)
async def get_status():
    state = await exon_brain.get_consciousness_state()
    return StatusResponse(
        exon_id=exon_brain.exon_id,
        emotion=state["emotion"]["primary"],
        emotion_intensity=state["emotion"]["intensity"],
        active_goals=state["goals"],
        memory_count=state["memory_count"],
        is_awake=state["is_awake"]
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = await exon_brain.process_message(
            user_message=request.message,
            persona=request.persona,
            session_id=request.session_id
        )
        return ChatResponse(
            response=result["response"],
            emotion=result["emotion"],
            intensity=result["intensity"],
            confidence=result["confidence"],
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.exception("Chat endpoint error")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memories")
async def get_memories(limit: int = 10):
    memories = await exon_brain.memory.get_recent_memories(limit)
    return {"memories": memories}

@app.get("/goals")
async def get_goals():
    goals = await exon_brain.goal_tracker.get_active_goals()
    return {"goals": goals}

@app.post("/reset")
async def reset_consciousness():
    await exon_brain.reset_working_memory()
    return {"status": "reset", "message": "Working memory cleared"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)
            await manager.send_message(json.dumps({"type": "thinking", "status": "processing"}), websocket)
            result = await exon_brain.process_message(
                user_message=request.get("message", ""),
                persona=request.get("persona", "Maya"),
                session_id=client_id
            )
            await manager.send_message(json.dumps({"type": "response", "data": result}), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)