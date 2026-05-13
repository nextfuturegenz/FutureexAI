# exon/api/routes/chat.py
# Author: Ashish Pal
# Purpose: Chat endpoints (REST and SSE streaming).

import json
import logging
from typing import AsyncGenerator
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from exon.api.models.schemas import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Will be set by app.py
exon_brain = None

def init(brain):
    global exon_brain
    exon_brain = brain

# SSE Streaming generator
async def stream_generator(message: str, persona: str, session_id: str) -> AsyncGenerator[str, None]:
    """Generates SSE events from ExonBrain.process_message_stream."""
    try:
        async for token in exon_brain.process_message_stream(
            message, persona=persona, session_id=session_id
        ):
            yield f"data: {json.dumps({'token': token})}\n\n"
    except Exception as e:
        logger.exception("Stream error")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
    yield "data: [DONE]\n\n"

@router.post("/chat", response_model=ChatResponse)
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

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """SSE endpoint that streams tokens word by word."""
    return StreamingResponse(
        stream_generator(request.message, request.persona, request.session_id or "web"),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )