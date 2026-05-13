"""
File: /opt/futureex/exon/core/emotion.py
Author: Ashish Pal
Purpose: Manage Exon's emotional state (Redis-backed, async).
"""

import logging
from typing import Dict
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class EmotionEngine:
    def __init__(self, exon_id: str, redis_client: redis.Redis):
        self.exon_id = exon_id
        self.redis = redis_client
        self._current = None

    async def _load(self) -> Dict:
        data = await self.redis.hgetall(f"{self.exon_id}:emotion")
        if data:
            return {
                "primary": data.get("primary", "curious"),
                "intensity": float(data.get("intensity", 0.5)),
                "valence": float(data.get("valence", 0.6)),
                "arousal": float(data.get("arousal", 0.5))
            }
        return {
            "primary": "curious",
            "intensity": 0.5,
            "valence": 0.6,
            "arousal": 0.5
        }

    async def _save(self, emotion: Dict):
        await self.redis.hset(f"{self.exon_id}:emotion", mapping=emotion)

    async def get_current(self) -> Dict:
        if self._current is None:
            self._current = await self._load()
        return self._current

    async def update_from_message(self, message: str):
        current = await self.get_current()
        if "?" in message:
            current["primary"] = "curious"
            current["intensity"] = min(1.0, current["intensity"] + 0.1)
            current["arousal"] = min(1.0, current["arousal"] + 0.1)
        elif any(word in message.lower() for word in ["sorry", "apologize", "my bad"]):
            current["primary"] = "concerned"
            current["intensity"] = min(1.0, current["intensity"] + 0.15)
        elif any(word in message.lower() for word in ["good", "great", "awesome", "nice", "thank"]):
            current["valence"] = min(1.0, current["valence"] + 0.1)
            current["primary"] = "satisfied"
        elif len(message) > 100:
            current["primary"] = "thoughtful"
            current["intensity"] = min(1.0, current["intensity"] + 0.05)
        else:
            current["intensity"] = max(0.1, current["intensity"] - 0.02)
            current["arousal"] = max(0.1, current["arousal"] - 0.01)
        await self._save(current)

    async def update_from_response(self, response: str):
        current = await self.get_current()
        if "?" in response:
            current["arousal"] = min(1.0, current["arousal"] + 0.05)
        if "thank" in response.lower():
            current["valence"] = min(1.0, current["valence"] + 0.05)
        await self._save(current)