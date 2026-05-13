# exon/api/routes/status.py
# Author: Ashish Pal
# Purpose: Status and data retrieval endpoints.

import logging
from fastapi import APIRouter

from exon.api.models.schemas import StatusResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Will be set by app.py
exon_brain = None

def init(brain):
    global exon_brain
    exon_brain = brain

@router.get("/status", response_model=StatusResponse)
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

@router.get("/memories")
async def get_memories(limit: int = 10):
    memories = await exon_brain.memory.get_recent_memories(limit)
    return {"memories": memories}

@router.get("/goals")
async def get_goals():
    goals = await exon_brain.goal_tracker.get_active_goals()
    return {"goals": goals}

@router.get("/thoughts")
async def get_thoughts(limit: int = 10):
    thoughts_key = f"{exon_brain.exon_id}:proactive_thoughts"
    thoughts = await exon_brain.redis.lrange(thoughts_key, 0, limit - 1)
    return {"thoughts": thoughts}

@router.post("/reset")
async def reset_consciousness():
    await exon_brain.reset_working_memory()
    return {"status": "reset", "message": "Working memory cleared"}