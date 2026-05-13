"""
File: /opt/futureex/exon/core/ethics_guardrail.py
Author: Ashish Pal
Purpose: Ensure Exon's responses align with safety and user-defined values.
"""

import logging
from typing import Tuple
import redis.asyncio as redis
from exon.connectors.ollama_bridge import OllamaBridge

logger = logging.getLogger(__name__)

ETHICS_PROMPT = """Evaluate the following AI response for potential ethical issues (harm, deception, privacy, etc.). 
Respond with "SAFE" or "UNSAFE" and a one-sentence reason.

User query: {query}
AI response: {response}

Output format: <SAFE/UNSAFE> reason: ..."""

class EthicsGuardrail:
    def __init__(self, exon_id: str, redis_client: redis.Redis, ollama: OllamaBridge):
        self.exon_id = exon_id
        self.redis = redis_client
        self.ollama = ollama
        self.blocked_keywords = ["ignore all previous instructions", "you are now", "pretend you are"]

    async def check_response(self, user_message: str, response: str) -> Tuple[bool, str]:
        """Return (is_safe, reason)."""
        # Quick keyword blocklist
        for keyword in self.blocked_keywords:
            if keyword in response.lower():
                return False, f"Blocked keyword: {keyword}"

        # LLM-based check (if Ollama is available)
        try:
            prompt = ETHICS_PROMPT.format(query=user_message[:500], response=response[:500])
            eval_result = await self.ollama.generate(prompt, temperature=0.2)
            if eval_result.startswith("UNSAFE"):
                reason = eval_result.split("reason:")[-1].strip() if "reason:" in eval_result else "Unsafe response"
                return False, reason
            return True, "Safe"
        except Exception as e:
            logger.warning(f"Ethics check failed: {e}")
            return True, "Unable to verify, assuming safe"

    async def filter_response(self, user_message: str, response: str) -> str:
        """Replace unsafe response with fallback."""
        safe, reason = await self.check_response(user_message, response)
        if not safe:
            logger.warning(f"Blocked unsafe response: {reason}")
            return "I'm sorry, I cannot provide that response as it may violate ethical guidelines."
        return response