"""
File: /opt/futureex/exon/core/memory_consolidator.py
Author: Ashish Pal
Purpose: Promote important memories to long-term PostgreSQL, forget trivial ones, and create summaries.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import redis.asyncio as redis
import psycopg2
from psycopg2.extras import Json

logger = logging.getLogger(__name__)

class MemoryConsolidator:
    def __init__(self, exon_id: str, redis_client: redis.Redis, pg_conn):
        self.exon_id = exon_id
        self.redis = redis_client
        self.pg_conn = pg_conn

    async def consolidate(self, exon_db_id: int):
        """Scan working memory, compute importance, and promote to PG."""
        try:
            # Get all working memories
            working_memories = await self.redis.lrange(f"{self.exon_id}:memory:recent", 0, -1)
            if len(working_memories) < 50:  # Only consolidate when near limit
                return

            # For each memory, compute importance (simple heuristic)
            important_memories = []
            for mem_json in working_memories:
                mem = json.loads(mem_json)
                importance = self._compute_importance(mem)
                if importance > 0.7:
                    important_memories.append((mem, importance))

            # Store important ones in PostgreSQL
            with self.pg_conn.cursor() as cur:
                for mem, imp in important_memories:
                    cur.execute("""
                        INSERT INTO exon_memories (exon_id, memory_type, content, importance_score, created_at)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (exon_db_id, "conversation", Json(mem), imp, datetime.fromisoformat(mem['timestamp'])))
                self.pg_conn.commit()

            # Optionally truncate working memory after consolidation
            await self.redis.ltrim(f"{self.exon_id}:memory:recent", 0, 19)  # keep 20 most recent
            logger.info(f"Consolidated {len(important_memories)} memories for {self.exon_id}")
        except Exception as e:
            logger.error(f"Memory consolidation failed: {e}")

    def _compute_importance(self, memory: dict) -> float:
        """Rule-based importance scoring."""
        score = 0.5  # base
        user_msg = memory.get('user', '')
        # Longer messages more important
        if len(user_msg) > 100:
            score += 0.2
        # Questions indicate engagement
        if '?' in user_msg:
            score += 0.1
        # Keywords
        important_words = ['purpose', 'goal', 'learn', 'remember', 'important', 'future']
        for word in important_words:
            if word in user_msg.lower():
                score += 0.1
        # Emotion intensity
        if memory.get('emotion') in ['curious', 'excited']:
            score += 0.05
        return min(1.0, score)