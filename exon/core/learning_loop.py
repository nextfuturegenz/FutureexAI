"""
File: /opt/futureex/exon/core/learning_loop.py
Author: Ashish Pal
Purpose: Extract lessons from conversations using Ollama, store in Redis.
"""

import json
import logging
from typing import Optional, List, Dict
from datetime import datetime
import redis.asyncio as redis
from exon.connectors.ollama_bridge import OllamaBridge

logger = logging.getLogger(__name__)

LESSON_PROMPT = """You just had this conversation with the Founder:

User: {user_message}
You: {ai_response}

What did you learn from this interaction? Extract one specific lesson.
Format as a single sentence starting with "I learned that..."

Output only the lesson, nothing else."""

class LearningLoop:
    def __init__(self, exon_id: str, redis_client: redis.Redis, ollama: OllamaBridge):
        self.exon_id = exon_id
        self.redis = redis_client
        self.ollama = ollama

    async def extract_lesson(self, user_message: str, response: str) -> Optional[str]:
        try:
            prompt = LESSON_PROMPT.format(user_message=user_message, ai_response=response)
            lesson = await self.ollama.generate(prompt, temperature=0.3)
            if lesson and lesson.startswith("I learned that"):
                return lesson
            return None
        except Exception as e:
            logger.warning(f"Lesson extraction failed: {e}")
            return None

    async def store_lesson(self, lesson: str):
        entry = {"lesson": lesson, "timestamp": datetime.now().isoformat(), "reinforcement_count": 1}
        await self.redis.lpush(f"{self.exon_id}:lessons", json.dumps(entry))
        await self.redis.ltrim(f"{self.exon_id}:lessons", 0, 99)

    async def get_relevant_lessons(self, context: str, limit: int = 3) -> List[Dict]:
        lessons = []
        all_lessons = await self.redis.lrange(f"{self.exon_id}:lessons", 0, -1)
        for ls in all_lessons:
            try:
                l = json.loads(ls)
                # simple keyword matching
                if any(word in context.lower() for word in l.get("lesson", "").lower().split()[:3]):
                    lessons.append(l)
            except:
                pass
        return lessons[:limit]