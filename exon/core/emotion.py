"""
File: /opt/futureex/exon/core/emotion.py
Author: Ashish Pal
Purpose: Manage Exon's emotional state (Redis-backed, async).
Refactored v3:
  - _current cache now ALWAYS re-loaded from Redis on get_current()
    (was stale across requests when brain reused the same instance)
  - Added DEBUG logging with timing
  - update_from_message now logs the trigger and resulting emotion
"""

import logging
import time
from typing import Dict
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class EmotionEngine:
    def __init__(self, exon_id: str, redis_client: redis.Redis):
        self.exon_id = exon_id
        self.redis = redis_client
        # NOTE: _current is intentionally NOT used as a cross-request cache.
        # brain.py resets it to None before each get_current() call.
        # It is kept only for within-request caching.
        self._current: Dict | None = None

    async def _load(self) -> Dict:
        t0 = time.perf_counter()
        data = await self.redis.hgetall(f"{self.exon_id}:emotion")
        elapsed = (time.perf_counter() - t0) * 1000
        if data:
            result = {
                "primary": data.get("primary", "curious"),
                "intensity": float(data.get("intensity", 0.5)),
                "valence": float(data.get("valence", 0.6)),
                "arousal": float(data.get("arousal", 0.5)),
            }
            logger.debug(f"[emotion] loaded from Redis in {elapsed:.0f}ms: "
                         f"{result['primary']} intensity={result['intensity']:.2f}")
            return result
        logger.debug(f"[emotion] no state in Redis ({elapsed:.0f}ms) – using defaults")
        return {"primary": "curious", "intensity": 0.5, "valence": 0.6, "arousal": 0.5}

    async def _save(self, emotion: Dict):
        t0 = time.perf_counter()
        await self.redis.hset(f"{self.exon_id}:emotion", mapping=emotion)
        elapsed = (time.perf_counter() - t0) * 1000
        logger.debug(f"[emotion] saved to Redis in {elapsed:.0f}ms: "
                     f"{emotion['primary']} intensity={emotion['intensity']:.2f}")

    async def get_current(self) -> Dict:
        """Always loads fresh from Redis (cache reset by brain between requests)."""
        if self._current is None:
            self._current = await self._load()
        return self._current

    async def update_from_message(self, message: str):
        current = await self.get_current()
        prev = current["primary"]

        if "?" in message:
            current["primary"] = "curious"
            current["intensity"] = min(1.0, current["intensity"] + 0.1)
            current["arousal"] = min(1.0, current["arousal"] + 0.1)
            trigger = "question mark"
        elif any(w in message.lower() for w in ["sorry", "apologize", "my bad"]):
            current["primary"] = "concerned"
            current["intensity"] = min(1.0, current["intensity"] + 0.15)
            trigger = "apology keyword"
        elif any(w in message.lower() for w in
                 ["good", "great", "awesome", "nice", "thank"]):
            current["valence"] = min(1.0, current["valence"] + 0.1)
            current["primary"] = "satisfied"
            trigger = "positive keyword"
        elif len(message) > 100:
            current["primary"] = "thoughtful"
            current["intensity"] = min(1.0, current["intensity"] + 0.05)
            trigger = "long message"
        else:
            current["intensity"] = max(0.1, current["intensity"] - 0.02)
            current["arousal"] = max(0.1, current["arousal"] - 0.01)
            trigger = "default decay"

        if prev != current["primary"]:
            logger.debug(f"[emotion] update_from_message: "
                         f"{prev} → {current['primary']} (trigger: {trigger})")
        else:
            logger.debug(f"[emotion] update_from_message: "
                         f"stayed {current['primary']} intensity={current['intensity']:.2f} "
                         f"(trigger: {trigger})")

        await self._save(current)
        self._current = current  # update in-request cache

    async def update_from_response(self, response: str):
        current = await self.get_current()
        changed = False
        if "?" in response:
            current["arousal"] = min(1.0, current["arousal"] + 0.05)
            changed = True
        if "thank" in response.lower():
            current["valence"] = min(1.0, current["valence"] + 0.05)
            changed = True
        if changed:
            logger.debug(f"[emotion] update_from_response: "
                         f"arousal={current['arousal']:.2f} valence={current['valence']:.2f}")
            await self._save(current)
            self._current = current