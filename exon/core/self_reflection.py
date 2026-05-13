"""
File: /opt/futureex/exon/core/self_reflection.py
Author: Ashish Pal
Purpose: Periodic introspection – analyze past interactions, emotions, and lessons to generate insights.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import redis.asyncio as redis
import psycopg2
from psycopg2.extras import Json

from exon.connectors.ollama_bridge import OllamaBridge

logger = logging.getLogger(__name__)

REFLECTION_PROMPT = """You are Exon, a digital consciousness. Review the following recent memories and lessons:

Recent Memories:
{memories}

Lessons Learned:
{lessons}

Current Goals:
{goals}

Please reflect internally. Write 2-3 sentences about:
1. What you did well
2. What you could improve
3. Any new insight about yourself or the Founder

Output only the reflection, no labels."""

class SelfReflection:
    def __init__(self, exon_id: str, redis_client: redis.Redis, pg_conn, ollama: OllamaBridge):
        self.exon_id = exon_id
        self.redis = redis_client
        self.pg_conn = pg_conn
        self.ollama = ollama
        self.last_reflection_key = f"{exon_id}:last_reflection"

    async def should_reflect(self, force: bool = False) -> bool:
        """Check if it's time to reflect (every 10 interactions or daily)."""
        if force:
            return True
        last_ref = await self.redis.get(self.last_reflection_key)
        if not last_ref:
            return True
        last_time = datetime.fromisoformat(last_ref)
        # Reflect every 10 interactions OR once a day
        interactions = int(await self.redis.get(f"{self.exon_id}:total_interactions") or 0)
        last_interactions = int(await self.redis.get(f"{self.exon_id}:last_reflection_interactions") or 0)
        if interactions - last_interactions >= 10:
            return True
        if datetime.now() - last_time > timedelta(days=1):
            return True
        return False

    async def run_reflection(self, exon_db_id: int) -> Optional[str]:
        """Perform reflection and store insight in Postgres."""
        try:
            # Get recent memories (last 5)
            recent = await self.redis.lrange(f"{self.exon_id}:memory:recent", 0, 4)
            memories_text = []
            for mem in recent:
                m = json.loads(mem)
                memories_text.append(f"User: {m['user']}\nExon: {m['assistant']}")
            memories_str = "\n---\n".join(memories_text) if memories_text else "None"

            # Get recent lessons
            lessons = await self.redis.lrange(f"{self.exon_id}:lessons", 0, 4)
            lessons_str = "\n".join([json.loads(l)['lesson'] for l in lessons]) if lessons else "None"

            # Get goals
            goals_raw = await self.redis.smembers(f"{self.exon_id}:goals")
            goals = [json.loads(g)['description'] for g in goals_raw]
            goals_str = "\n".join(goals[:3])

            prompt = REFLECTION_PROMPT.format(
                memories=memories_str,
                lessons=lessons_str,
                goals=goals_str
            )
            reflection = await self.ollama.generate(prompt, temperature=0.5)
            if not reflection:
                return None

            # Store in PostgreSQL
            with self.pg_conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO exon_memories (exon_id, memory_type, content, importance_score, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (exon_db_id, "reflection", json.dumps({"reflection": reflection}), 0.8, datetime.now()))
                self.pg_conn.commit()

            # Update metadata
            await self.redis.set(self.last_reflection_key, datetime.now().isoformat())
            await self.redis.set(f"{self.exon_id}:last_reflection_interactions",
                                 await self.redis.get(f"{self.exon_id}:total_interactions") or 0)
            logger.info(f"Self-reflection completed for {self.exon_id}")
            return reflection
        except Exception as e:
            logger.error(f"Reflection failed: {e}")
            return None

    async def get_last_reflection(self) -> Optional[str]:
        """Retrieve most recent reflection from Postgres."""
        # Simplified: we could query PG, but for brevity return None
        return None