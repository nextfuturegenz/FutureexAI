"""Chat routing endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    persona: str = "Maya"
    session_id: Optional[str] = None

@router.post("/chat")
async def chat_endpoint(msg: ChatMessage):
    # This will be connected to ExonBrain in app.py
    return {"status": "received", "message": msg.message}