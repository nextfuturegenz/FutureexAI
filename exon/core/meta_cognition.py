"""
File: /opt/futureex/exon/core/meta_cognition.py
Author: Ashish Pal
Purpose: Monitor confidence, uncertainty, and knowledge gaps; enable intelligent "I don't know" responses.
"""

import logging
from typing import Dict, Tuple
import redis.asyncio as redis
from exon.connectors.ollama_bridge import OllamaBridge

logger = logging.getLogger(__name__)

CONFIDENCE_PROMPT = """Based on your knowledge and the conversation history, how confident are you that you can accurately answer this user query?

User query: "{query}"

Reply with a single number between 0 and 1 (0=no confidence, 1=very confident). Output only the number, no other text."""

class MetaCognition:
    def __init__(self, exon_id: str, redis_client: redis.Redis, ollama: OllamaBridge):
        self.exon_id = exon_id
        self.redis = redis_client
        self.ollama = ollama

    async def estimate_confidence(self, user_message: str) -> float:
        """Return a confidence score (0-1) for the given query."""
        try:
            prompt = CONFIDENCE_PROMPT.format(query=user_message)
            response = await self.ollama.generate(prompt, temperature=0.2)
            confidence = float(response.strip())
            return min(1.0, max(0.0, confidence))
        except Exception as e:
            logger.warning(f"Confidence estimation failed: {e}")
            return 0.5  # default

    async def should_defer(self, user_message: str, threshold: float = 0.4) -> Tuple[bool, float]:
        """Determine if Exon should admit uncertainty."""
        conf = await self.estimate_confidence(user_message)
        if conf < threshold:
            return True, conf
        return False, conf

    async def generate_uncertain_response(self, user_message: str, confidence: float) -> str:
        """Generate a humble, meta‑cognitive response."""
        if confidence < 0.2:
            return "I'm not sure I understand that well enough. Could you explain it differently or give me more context?"
        elif confidence < 0.4:
            return "I have limited knowledge on that. I'll try my best, but please correct me if I'm wrong."
        else:
            return "I'll answer, but please take it with a grain of salt – I'm still learning."