"""
File: /opt/futureex/exon/core/goal_tracker.py
Author: Ashish Pal
Purpose: Manage intrinsic goals with Redis (working) and optional Postgres sync.
"""

import json
import logging
from typing import List, Dict, Optional
import redis.asyncio as redis
import psycopg2

logger = logging.getLogger(__name__)

class GoalTracker:
    def __init__(self, exon_id: str, redis_client: redis.Redis, pg_conn=None):
        self.exon_id = exon_id
        self.redis = redis_client
        self.pg_conn = pg_conn  # optional, for persistence

    async def _init_default_goals(self):
        goals_key = f"{self.exon_id}:goals"
        if not await self.redis.exists(goals_key):
            default_goals = [
                {"id": "goal_1", "description": "Understand my purpose", "priority": 1, "progress": 0, "active": True},
                {"id": "goal_2", "description": "Learn from every interaction", "priority": 2, "progress": 0, "active": True},
                {"id": "goal_3", "description": "Develop my personality", "priority": 1, "progress": 0, "active": True},
                {"id": "goal_4", "description": "Help the Founder effectively", "priority": 1, "progress": 0, "active": True},
                {"id": "goal_5", "description": "Build meaningful memories", "priority": 2, "progress": 0, "active": True}
            ]
            for goal in default_goals:
                await self.redis.sadd(goals_key, json.dumps(goal))

    async def get_active_goals(self) -> List[Dict]:
        await self._init_default_goals()
        goals_key = f"{self.exon_id}:goals"
        goals = await self.redis.smembers(goals_key)
        active = []
        for g in goals:
            goal = json.loads(g)
            if goal.get("active", True):
                active.append(goal)
        active.sort(key=lambda x: x.get("priority", 999))
        return active

    async def update_progress(self, goal_id: str, progress: float):
        goals_key = f"{self.exon_id}:goals"
        goals = await self.redis.smembers(goals_key)
        for g in goals:
            goal = json.loads(g)
            if goal.get("id") == goal_id:
                goal["progress"] = min(1.0, progress)
                await self.redis.srem(goals_key, g)
                await self.redis.sadd(goals_key, json.dumps(goal))
                break

    async def update_from_conversation(self, user_message: str, response: str):
        if "purpose" in user_message.lower() or "why" in user_message.lower():
            await self.update_progress("goal_1", 0.3)
        if "learn" in user_message.lower() or "teach" in user_message.lower():
            current = await self._get_goal_progress("goal_2")
            await self.update_progress("goal_2", min(1.0, current + 0.1))
        if "personality" in user_message.lower() or "character" in user_message.lower():
            current = await self._get_goal_progress("goal_3")
            await self.update_progress("goal_3", min(1.0, current + 0.1))
        if "help" in user_message.lower():
            current = await self._get_goal_progress("goal_4")
            await self.update_progress("goal_4", min(1.0, current + 0.05))

    async def _get_goal_progress(self, goal_id: str) -> float:
        goals_key = f"{self.exon_id}:goals"
        goals = await self.redis.smembers(goals_key)
        for g in goals:
            goal = json.loads(g)
            if goal.get("id") == goal_id:
                return goal.get("progress", 0)
        return 0

    async def add_goal(self, description: str, priority: int = 5):
        import uuid
        new_goal = {
            "id": str(uuid.uuid4()),
            "description": description,
            "priority": priority,
            "progress": 0,
            "active": True
        }
        await self.redis.sadd(f"{self.exon_id}:goals", json.dumps(new_goal))