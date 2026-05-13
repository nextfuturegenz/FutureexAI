"""
File: /opt/futureex/exon/core/dream_simulator.py
Author: Ashish Pal
Purpose: Replay memory fragments in random combinations to generate creative insights (sleep-like processing).
"""

import json
import logging
import random
from datetime import datetime
import redis.asyncio as redis
import psycopg2
from exon.connectors.ollama_bridge import OllamaBridge

logger = logging.getLogger(__name__)

DREAM_PROMPT = """I will give you two memory fragments. Combine and reinterpret them to produce a new, creative insight.

Fragment A: {fragment_a}
Fragment B: {fragment_b}

Produce one original sentence (not just a summary)."""

class DreamSimulator:
    def __init__(self, exon_id: str, redis_client: redis.Redis, pg_conn, ollama: OllamaBridge):
        self.exon_id = exon_id
        self.redis = redis_client
        self.pg_conn = pg_conn
        self.ollama = ollama

    async def dream(self, exon_db_id: int):
        """Select two random memories, combine them via Ollama, store insight."""
        try:
            # Get working memories
            memories = await self.redis.lrange(f"{self.exon_id}:memory:recent", 0, -1)
            if len(memories) < 2:
                return
            # Pick two random distinct memories
            a, b = random.sample(memories, 2)
            mem_a = json.loads(a)
            mem_b = json.loads(b)

            prompt = DREAM_PROMPT.format(
                fragment_a=mem_a["user"][:200],
                fragment_b=mem_b["user"][:200]
            )
            insight = await self.ollama.generate(prompt, temperature=0.9)
            if insight:
                # Store as a special memory type
                with self.pg_conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO exon_memories (exon_id, memory_type, content, importance_score, created_at)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (exon_db_id, "dream_insight", json.dumps({"insight": insight}), 0.6, datetime.now()))
                    self.pg_conn.commit()
                logger.info(f"Dream insight generated for {self.exon_id}")
        except Exception as e:
            logger.error(f"Dream simulation failed: {e}")

    async def run_dream_cycle(self, exon_db_id: int):
        """Run dreaming periodically (e.g., every 30 min)."""
        await self.dream(exon_db_id)