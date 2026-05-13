"""
File: /opt/futureex/exon/core/meta_cognition.py
Author: Ashish Pal
Purpose: Monitor confidence, extract numeric score from LLM response.
Refactored: Smarter confidence estimation with keyword boosting, lower default threshold.
"""

import re
import logging
from typing import Tuple
import redis.asyncio as redis
from exon.connectors.ollama_bridge import OllamaBridge

logger = logging.getLogger(__name__)

CONFIDENCE_PROMPT = """Based on your knowledge and the conversation history, how confident are you that you can accurately answer this user query?  
Reply with a single number between 0 and 1 (0=no confidence, 1=very confident). Output ONLY the number, nothing else.

User query: "{query}"
Confidence (0-1):"""

# Keywords that suggest the message is simple and doesn't need high confidence
SIMPLE_GREETINGS = {"hello", "hi", "hey", "yo", "sup", "hola", "good morning", "good afternoon", "good evening"}
SIMPLE_RESPONSES = {"ok", "okay", "thanks", "thank you", "bye", "goodbye", "see you", "yes", "no", "sure", "fine", "cool", "nice", "great"}
COMMON_TOPICS = {
    "weather", "time", "date", "day", "name", "age", "how are you", "what's up",
    "who are you", "what are you", "tell me about yourself", "help", "what can you do",
    "capital", "president", "prime minister", "population", "color", "food", "music",
    "movie", "book", "sport", "animal", "country", "city", "language", "computer",
    "phone", "car", "house", "job", "school", "university", "family", "friend"
}

class MetaCognition:
    def __init__(self, exon_id: str, redis_client: redis.Redis, ollama: OllamaBridge):
        self.exon_id = exon_id
        self.redis = redis_client
        self.ollama = ollama

    def _is_simple_message(self, user_message: str) -> bool:
        """Check if the message is a simple greeting or short response."""
        msg_lower = user_message.strip().lower().rstrip('?!.')
        
        # Very short messages (1-2 words) are usually simple
        word_count = len(msg_lower.split())
        if word_count <= 2:
            return True
        
        # Check against known simple greetings/responses
        if msg_lower in SIMPLE_GREETINGS or msg_lower in SIMPLE_RESPONSES:
            return True
        
        # Check if message starts with a simple phrase
        for simple in SIMPLE_GREETINGS | SIMPLE_RESPONSES:
            if msg_lower.startswith(simple):
                return True
        
        return False

    def _get_keyword_boost(self, user_message: str) -> float:
        """Boost confidence if message contains common topics."""
        msg_lower = user_message.lower()
        boost = 0.0
        
        # Check for common easy topics
        for topic in COMMON_TOPICS:
            if topic in msg_lower:
                boost += 0.05
        
        # Check for question words (suggests factual query)
        question_words = {"what", "who", "where", "when", "how", "why", "which", "whose", "whom"}
        for qw in question_words:
            if qw in msg_lower:
                boost += 0.03
        
        # Longer, well-formed questions get more boost
        if "?" in user_message and len(msg_lower.split()) > 3:
            boost += 0.05
        
        return min(0.3, boost)  # Cap the boost

    async def estimate_confidence(self, user_message: str) -> float:
        """Return confidence score (0-1) with keyword boosting."""
        
        # Simple messages get high confidence without LLM call
        if self._is_simple_message(user_message):
            logger.debug(f"Simple message detected, skipping LLM confidence check: {user_message[:50]}")
            return 0.9
        
        try:
            prompt = CONFIDENCE_PROMPT.format(query=user_message[:500])
            response = await self.ollama.generate(prompt, temperature=0.2)
            # Extract first floating point number from response
            match = re.search(r"[-+]?\d*\.\d+|\d+", response.strip())
            if match:
                confidence = float(match.group())
                confidence = min(1.0, max(0.0, confidence))
            else:
                logger.warning(f"No numeric confidence found in: {response[:100]}")
                confidence = 0.5
            
            # Apply keyword boost
            boost = self._get_keyword_boost(user_message)
            confidence = min(1.0, confidence + boost)
            
            logger.debug(f"Confidence for '{user_message[:50]}': {confidence:.2f} (boost: {boost:.2f})")
            return confidence
            
        except Exception as e:
            logger.warning(f"Confidence estimation failed: {e}")
            # If LLM fails, check if it's a simple message
            if self._is_simple_message(user_message):
                return 0.8
            return 0.5

    async def should_defer(self, user_message: str, threshold: float = 0.3) -> Tuple[bool, float]:
        """Check if we should defer (low confidence). Threshold lowered to 0.3."""
        conf = await self.estimate_confidence(user_message)
        return (conf < threshold, conf)

    async def generate_uncertain_response(self, user_message: str, confidence: float) -> str:
        """Generate contextual uncertain response based on confidence level."""
        if confidence < 0.1:
            return "I'm not sure I understand that. Could you rephrase or provide more context?"
        elif confidence < 0.2:
            return "I have very limited knowledge about that. Could you try asking differently?"
        elif confidence < 0.3:
            return "I'm not entirely confident, but let me try... Actually, I'd rather be honest and say I'm not sure about this one. Could you ask something else?"
        else:
            return "I'll try my best to answer, though I'm still learning. Take my response with a pinch of salt."