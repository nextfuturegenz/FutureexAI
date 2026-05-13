# exon/api/models/schemas.py
# Author: Ashish Pal
# Purpose: Request/Response Pydantic models.

from pydantic import BaseModel
from typing import Optional

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