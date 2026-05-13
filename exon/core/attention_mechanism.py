"""
File: /opt/futureex/exon/core/attention_mechanism.py
Author: Ashish Pal
Purpose: Dynamically weight recent memories, goals, and lessons when building prompts.
"""

import json
import logging
from typing import List, Dict, Tuple
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class AttentionMechanism:
    def __init__(self, exon_id: str, redis_client: redis.Redis):
        self.exon_id = exon_id
        self.redis = redis_client

    async def get_attended_context(self, user_message: str, max_items: int = 3) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Return attended (weighted) memories, goals, lessons."""
        # Get raw data
        raw_memories = await self.redis.lrange(f"{self.exon_id}:memory:recent", 0, 9)
        raw_goals = await self.redis.smembers(f"{self.exon_id}:goals")
        raw_lessons = await self.redis.lrange(f"{self.exon_id}:lessons", 0, 9)

        # Score each memory by relevance to user_message (simple keyword overlap)
        scored_memories = []
        for mem_json in raw_memories:
            mem = json.loads(mem_json)
            score = self._relevance_score(mem["user"], user_message)
            scored_memories.append((score, mem))
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        top_memories = [m for _, m in scored_memories[:max_items]]

        # Score goals similarly
        scored_goals = []
        for goal_json in raw_goals:
            goal = json.loads(goal_json)
            score = self._relevance_score(goal["description"], user_message)
            scored_goals.append((score, goal))
        scored_goals.sort(key=lambda x: x[0], reverse=True)
        top_goals = [g for _, g in scored_goals[:max_items]]

        # Lessons
        scored_lessons = []
        for less_json in raw_lessons:
            less = json.loads(less_json)
            score = self._relevance_score(less["lesson"], user_message)
            scored_lessons.append((score, less))
        scored_lessons.sort(key=lambda x: x[0], reverse=True)
        top_lessons = [l for _, l in scored_lessons[:max_items]]

        return top_memories, top_goals, top_lessons

    def _relevance_score(self, text: str, query: str) -> float:
        """Simple TF-IDF style overlap. In production, use embeddings."""
        query_tokens = set(query.lower().split())
        text_tokens = set(text.lower().split())
        overlap = len(query_tokens & text_tokens)
        return overlap / (len(query_tokens) + 1e-6)