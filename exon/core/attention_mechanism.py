"""
File: /opt/futureex/exon/core/attention_mechanism.py
Author: Ashish Pal
Purpose: Dynamically weight recent memories, goals, and lessons when building prompts.
Refactored v3:
  - Added DEBUG logging with timing and hit counts
  - Graceful handling of malformed JSON in Redis lists
  - Logged relevance scores for top results
"""

import json
import logging
import time
from typing import List, Dict, Tuple
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class AttentionMechanism:
    def __init__(self, exon_id: str, redis_client: redis.Redis):
        self.exon_id = exon_id
        self.redis = redis_client

    async def get_attended_context(
        self, user_message: str, max_items: int = 3
    ) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        t0 = time.perf_counter()

        # Fetch raw data from Redis
        raw_memories = await self.redis.lrange(f"{self.exon_id}:memory:recent", 0, 9)
        raw_goals = await self.redis.smembers(f"{self.exon_id}:goals")
        raw_lessons = await self.redis.lrange(f"{self.exon_id}:lessons", 0, 9)

        logger.debug(f"[attention] raw counts – memories={len(raw_memories)} "
                     f"goals={len(raw_goals)} lessons={len(raw_lessons)}")

        # Score memories
        scored_memories = []
        for mem_json in raw_memories:
            try:
                mem = json.loads(mem_json)
                score = self._relevance_score(mem.get("user", ""), user_message)
                scored_memories.append((score, mem))
            except json.JSONDecodeError as e:
                logger.debug(f"[attention] skipping malformed memory JSON: {e}")
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        top_memories = [m for _, m in scored_memories[:max_items]]

        # Score goals
        scored_goals = []
        for goal_json in raw_goals:
            try:
                goal = json.loads(goal_json)
                score = self._relevance_score(goal.get("description", ""), user_message)
                scored_goals.append((score, goal))
            except json.JSONDecodeError as e:
                logger.debug(f"[attention] skipping malformed goal JSON: {e}")
        scored_goals.sort(key=lambda x: x[0], reverse=True)
        top_goals = [g for _, g in scored_goals[:max_items]]

        # Score lessons
        scored_lessons = []
        for less_json in raw_lessons:
            try:
                less = json.loads(less_json)
                score = self._relevance_score(less.get("lesson", ""), user_message)
                scored_lessons.append((score, less))
            except json.JSONDecodeError as e:
                logger.debug(f"[attention] skipping malformed lesson JSON: {e}")
        scored_lessons.sort(key=lambda x: x[0], reverse=True)
        top_lessons = [l for _, l in scored_lessons[:max_items]]

        elapsed = (time.perf_counter() - t0) * 1000
        logger.debug(
            f"[attention] attended context in {elapsed:.0f}ms – "
            f"top_memories={len(top_memories)} "
            f"top_goals={len(top_goals)} "
            f"top_lessons={len(top_lessons)}"
            + (f" | top_mem_score={scored_memories[0][0]:.2f}" if scored_memories else "")
        )

        return top_memories, top_goals, top_lessons

    def _relevance_score(self, text: str, query: str) -> float:
        """Token overlap score. In production, swap for embeddings."""
        query_tokens = set(query.lower().split())
        text_tokens = set(text.lower().split())
        overlap = len(query_tokens & text_tokens)
        score = overlap / (len(query_tokens) + 1e-6)
        return score