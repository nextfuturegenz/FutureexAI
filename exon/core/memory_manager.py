"""
File: /opt/futureex/exon/core/memory_manager.py
Author: Ashish Pal
Purpose: Coordinate working memory (Redis) and long-term memory (PostgreSQL).
Refactored v3:
  - Added DEBUG logging with timing on every operation
  - Logs Redis key, length after push, and PG insert result
"""

import json
import logging
import time
from typing import List, Dict, Optional
from datetime import datetime
import redis.asyncio as redis
import psycopg2
from psycopg2.extras import Json

logger = logging.getLogger(__name__)


class MemoryManager:
    def __init__(self, exon_id: str, redis_client: redis.Redis, pg_conn):
        self.exon_id = exon_id
        self.redis = redis_client
        self.pg_conn = pg_conn

    async def store(
        self,
        user_message: str,
        ai_response: str,
        session_id: Optional[str],
        emotion: dict,
        exon_db_id: int,
    ):
        t0 = time.perf_counter()
        memory_entry = {
            "user": user_message,
            "assistant": ai_response,
            "emotion": emotion.get("primary", "neutral"),
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
        }

        # Redis working memory
        redis_key = f"{self.exon_id}:memory:recent"
        await self.redis.lpush(redis_key, json.dumps(memory_entry))
        await self.redis.ltrim(redis_key, 0, 49)
        redis_len = await self.redis.llen(redis_key)
        logger.debug(f"[memory] stored to Redis (key={redis_key} len={redis_len}) "
                     f"emotion={emotion.get('primary')}")

        # PostgreSQL long-term
        try:
            with self.pg_conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO exon_memories
                        (exon_id, memory_type, content, emotion_at_time, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (exon_db_id, "conversation", Json(memory_entry),
                     emotion.get("primary"), datetime.now()),
                )
                self.pg_conn.commit()
            elapsed = (time.perf_counter() - t0) * 1000
            logger.debug(f"[memory] stored to PostgreSQL in {elapsed:.0f}ms "
                         f"(exon_db_id={exon_db_id})")
        except Exception as e:
            self.pg_conn.rollback()
            logger.error(f"[memory] PostgreSQL store failed: {e}")

    async def recall(
        self, keyword: str, limit: int = 5, exon_db_id: Optional[int] = None
    ) -> List[Dict]:
        t0 = time.perf_counter()
        memories: List[Dict] = []

        # Redis first
        redis_memories = await self.redis.lrange(
            f"{self.exon_id}:memory:recent", 0, limit - 1
        )
        for mem in redis_memories:
            try:
                memories.append(json.loads(mem))
            except Exception:
                pass
        logger.debug(f"[memory] recall Redis: {len(memories)} entries for '{keyword}'")

        # Fallback to PostgreSQL
        if len(memories) < limit and exon_db_id is not None:
            try:
                with self.pg_conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT content FROM exon_memories
                        WHERE exon_id = %s AND content::text ILIKE %s
                        ORDER BY created_at DESC LIMIT %s
                        """,
                        (exon_db_id, f"%{keyword}%", limit - len(memories)),
                    )
                    for row in cur.fetchall():
                        memories.append(row[0])
                logger.debug(f"[memory] recall PG: now {len(memories)} total")
            except Exception as e:
                logger.error(f"[memory] recall PG failed: {e}")

        elapsed = (time.perf_counter() - t0) * 1000
        logger.debug(f"[memory] recall done in {elapsed:.0f}ms – {len(memories)} results")
        return memories

    async def get_recent_memories(self, limit: int = 10) -> List[Dict]:
        t0 = time.perf_counter()
        memories: List[Dict] = []
        redis_memories = await self.redis.lrange(
            f"{self.exon_id}:memory:recent", 0, limit - 1
        )
        for mem in redis_memories:
            try:
                memories.append(json.loads(mem))
            except Exception:
                pass
        elapsed = (time.perf_counter() - t0) * 1000
        logger.debug(f"[memory] get_recent_memories: {len(memories)} in {elapsed:.0f}ms")
        return memories

    async def get_memory_count(self) -> int:
        count = await self.redis.llen(f"{self.exon_id}:memory:recent")
        logger.debug(f"[memory] working memory count: {count}")
        return count

    async def clear_working_memory(self):
        await self.redis.delete(f"{self.exon_id}:memory:recent")
        logger.info("[memory] working memory cleared")