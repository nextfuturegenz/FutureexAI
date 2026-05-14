"""
File: /opt/futureex/exon/core/learning_loop.py
Author: Ashish Pal
Purpose: Extract lessons from conversations using Ollama, store in Redis.
Refactored v3:
  - Added DEBUG logging with timing
  - Logs lesson extraction result or failure clearly
  - extract_lesson is called from background queue only (not hot path)
"""

import json
import logging
import time
from typing import Optional, List, Dict
from datetime import datetime
import redis.asyncio as redis
from exon.connectors.ollama_bridge import OllamaBridge

logger = logging.getLogger(__name__)

LESSON_PROMPT = (
    "You had this conversation:\n\n"
    "User: {user_message}\n"
    "You: {ai_response}\n\n"
    "Extract one specific lesson in a single sentence starting with 'I learned that...'\n"
    "Output ONLY the lesson sentence, nothing else."
)


class LearningLoop:
    def __init__(self, exon_id: str, redis_client: redis.Redis, ollama: OllamaBridge):
        self.exon_id = exon_id
        self.redis = redis_client
        self.ollama = ollama

    async def extract_lesson(
        self, user_message: str, response: str
    ) -> Optional[str]:
        t0 = time.perf_counter()
        logger.debug(f"[learning] extracting lesson from exchange "
                     f"(user={len(user_message)}c response={len(response)}c)")
        try:
            prompt = LESSON_PROMPT.format(
                user_message=user_message[:300],
                ai_response=response[:300],
            )
            lesson = await self.ollama.generate(prompt, temperature=0.3)
            elapsed = (time.perf_counter() - t0) * 1000
            if lesson and lesson.startswith("I learned that"):
                logger.debug(f"[learning] lesson extracted in {elapsed:.0f}ms: "
                             f"'{lesson[:80]}'")
                return lesson
            else:
                logger.debug(f"[learning] no valid lesson (raw='{lesson[:60]}') "
                             f"in {elapsed:.0f}ms")
                return None
        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            logger.warning(f"[learning] lesson extraction failed after "
                           f"{elapsed:.0f}ms: {e}")
            return None

    async def store_lesson(self, lesson: str):
        entry = {
            "lesson": lesson,
            "timestamp": datetime.now().isoformat(),
            "reinforcement_count": 1,
        }
        key = f"{self.exon_id}:lessons"
        await self.redis.lpush(key, json.dumps(entry))
        await self.redis.ltrim(key, 0, 99)  # keep last 100 lessons
        count = await self.redis.llen(key)
        logger.debug(f"[learning] lesson stored (total in Redis: {count})")

    async def get_relevant_lessons(
        self, context: str, limit: int = 3
    ) -> List[Dict]:
        t0 = time.perf_counter()
        lessons: List[Dict] = []
        all_lessons = await self.redis.lrange(f"{self.exon_id}:lessons", 0, -1)
        for ls in all_lessons:
            try:
                l = json.loads(ls)
                lesson_text = l.get("lesson", "").lower()
                context_words = context.lower().split()[:5]
                if any(w in lesson_text for w in context_words):
                    lessons.append(l)
            except Exception:
                pass
            if len(lessons) >= limit:
                break
        elapsed = (time.perf_counter() - t0) * 1000
        logger.debug(f"[learning] get_relevant_lessons: {len(lessons)} matched "
                     f"from {len(all_lessons)} total in {elapsed:.0f}ms")
        return lessons