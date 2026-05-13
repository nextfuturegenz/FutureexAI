"""
File: /opt/futureex/exon/core/autonomous_loop.py
Author: Ashish Pal
Purpose: Background task to periodically run reflection, memory consolidation, and proactive messages.
"""

import asyncio
import logging
from datetime import datetime, timedelta
import redis.asyncio as redis
from exon.core.self_reflection import SelfReflection
from exon.core.memory_consolidator import MemoryConsolidator
from exon.core.goal_tracker import GoalTracker

logger = logging.getLogger(__name__)

class AutonomousLoop:
    def __init__(self, exon_id: str, redis_client: redis.Redis, pg_conn, ollama, goal_tracker, exon_db_id: int):
        self.exon_id = exon_id
        self.redis = redis_client
        self.pg_conn = pg_conn
        self.ollama = ollama
        self.goal_tracker = goal_tracker
        self.exon_db_id = exon_db_id
        self.reflection = SelfReflection(exon_id, redis_client, pg_conn, ollama)
        self.consolidator = MemoryConsolidator(exon_id, redis_client, pg_conn)
        self.running = False

    async def start(self, interval_seconds: int = 300):
        """Start background loop (every 5 minutes)."""
        self.running = True
        while self.running:
            try:
                await self._run_tasks()
            except Exception as e:
                logger.error(f"Autonomous loop error: {e}")
            await asyncio.sleep(interval_seconds)

    async def _run_tasks(self):
        # 1. Memory consolidation if needed
        await self.consolidator.consolidate(self.exon_db_id)

        # 2. Self-reflection if conditions met
        if await self.reflection.should_reflect():
            await self.reflection.run_reflection(self.exon_db_id)

        # 3. Proactive goal check (e.g., if a goal stuck, generate a thought)
        goals = await self.goal_tracker.get_active_goals()
        for goal in goals:
            if goal["progress"] < 0.5 and goal.get("priority", 5) <= 2:
                # Proactive thought: could inject into a "thought stream" (Redis list)
                thought = f"I've been thinking about my goal '{goal['description']}'. I should work on it."
                await self.redis.lpush(f"{self.exon_id}:proactive_thoughts", thought)
                await self.redis.ltrim(f"{self.exon_id}:proactive_thoughts", 0, 9)
                logger.info(f"Generated proactive thought for goal {goal['id']}")

    async def stop(self):
        self.running = False