"""
File: /opt/futureex/exon/core/meta_cognition.py
Author: Ashish Pal
Purpose: Confidence estimation – called only for complex messages now (brain guards it).
Refactored v3:
  - Added structured DEBUG logging with timing
  - Raised keyword boost cap
  - Lowered defer threshold to 0.2 (was 0.3) to reduce false deferrals
  - Simple-message guard returns early (no Ollama call)
"""

import re
import logging
import time
from typing import Tuple
import redis.asyncio as redis
from exon.connectors.ollama_bridge import OllamaBridge

logger = logging.getLogger(__name__)

CONFIDENCE_PROMPT = (
    "How confident are you that you can accurately answer this query?\n"
    "Reply with ONLY a single number between 0 and 1. No explanation.\n\n"
    'Query: "{query}"\nConfidence:'
)

SIMPLE_GREETINGS = {
    "hello", "hi", "hey", "yo", "sup", "hola",
    "good morning", "good afternoon", "good evening",
}
SIMPLE_RESPONSES = {
    "ok", "okay", "thanks", "thank you", "bye", "goodbye",
    "see you", "yes", "no", "sure", "fine", "cool", "nice", "great",
}
COMMON_TOPICS = {
    "weather", "time", "date", "day", "name", "age", "how are you",
    "what's up", "who are you", "what are you", "tell me about yourself",
    "help", "what can you do", "capital", "president", "prime minister",
    "population", "color", "food", "music", "movie", "book", "sport",
    "animal", "country", "city", "language", "computer", "phone",
    "car", "house", "job", "school", "university", "family", "friend",
}


class MetaCognition:
    def __init__(self, exon_id: str, redis_client: redis.Redis, ollama: OllamaBridge):
        self.exon_id = exon_id
        self.redis = redis_client
        self.ollama = ollama

    def _is_simple_message(self, user_message: str) -> bool:
        msg_lower = user_message.strip().lower().rstrip("?!.")
        if len(msg_lower.split()) <= 2:
            logger.debug(f"[meta_cog] simple (word count ≤2): '{msg_lower}'")
            return True
        if msg_lower in SIMPLE_GREETINGS or msg_lower in SIMPLE_RESPONSES:
            logger.debug(f"[meta_cog] simple (exact match greeting/response): '{msg_lower}'")
            return True
        for simple in SIMPLE_GREETINGS | SIMPLE_RESPONSES:
            if msg_lower.startswith(simple):
                logger.debug(f"[meta_cog] simple (starts with greeting): '{msg_lower}'")
                return True
        return False

    def _get_keyword_boost(self, user_message: str) -> float:
        msg_lower = user_message.lower()
        boost = 0.0
        for topic in COMMON_TOPICS:
            if topic in msg_lower:
                boost += 0.05
        question_words = {"what", "who", "where", "when", "how", "why", "which"}
        for qw in question_words:
            if qw in msg_lower:
                boost += 0.03
        if "?" in user_message and len(msg_lower.split()) > 3:
            boost += 0.05
        capped = min(0.35, boost)
        if capped > 0:
            logger.debug(f"[meta_cog] keyword boost: {capped:.2f}")
        return capped

    async def estimate_confidence(self, user_message: str) -> float:
        if self._is_simple_message(user_message):
            logger.debug("[meta_cog] simple message → confidence=0.9 (no LLM call)")
            return 0.9

        t0 = time.perf_counter()
        try:
            prompt = CONFIDENCE_PROMPT.format(query=user_message[:400])
            logger.debug(f"[meta_cog] calling Ollama for confidence…")
            response = await self.ollama.generate(prompt, temperature=0.1)
            elapsed = (time.perf_counter() - t0) * 1000
            logger.debug(f"[meta_cog] Ollama confidence raw='{response.strip()[:30]}' "
                         f"in {elapsed:.0f}ms")

            match = re.search(r"[-+]?\d*\.\d+|\d+", response.strip())
            if match:
                confidence = float(match.group())
                confidence = min(1.0, max(0.0, confidence))
            else:
                logger.warning(f"[meta_cog] no numeric confidence found: '{response[:60]}'")
                confidence = 0.5

            boost = self._get_keyword_boost(user_message)
            final = min(1.0, confidence + boost)
            logger.debug(f"[meta_cog] confidence={confidence:.2f} + boost={boost:.2f} "
                         f"→ final={final:.2f}")
            return final

        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            logger.warning(f"[meta_cog] confidence estimation failed after {elapsed:.0f}ms: {e}")
            if self._is_simple_message(user_message):
                return 0.8
            return 0.5

    async def should_defer(
        self, user_message: str, threshold: float = 0.2
    ) -> Tuple[bool, float]:
        """
        Threshold lowered to 0.2 (was 0.3) to reduce false deferrals.
        Called only for complex messages from brain.py.
        """
        conf = await self.estimate_confidence(user_message)
        defer = conf < threshold
        logger.debug(f"[meta_cog] should_defer={defer} conf={conf:.2f} threshold={threshold}")
        return defer, conf

    async def generate_uncertain_response(
        self, user_message: str, confidence: float
    ) -> str:
        logger.debug(f"[meta_cog] generating uncertain response (conf={confidence:.2f})")
        if confidence < 0.1:
            return ("I'm not sure I understand that. "
                    "Could you rephrase or provide more context?")
        elif confidence < 0.15:
            return ("I have very limited knowledge about that. "
                    "Could you try asking differently?")
        else:
            return ("I'm not entirely confident here – I'd rather be honest. "
                    "Could you give me more context?")