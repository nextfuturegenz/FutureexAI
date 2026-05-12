"""
Goal Tracker - Manages Exon's intrinsic goals
"""

import redis
import os
import json
from typing import List, Dict
from datetime import datetime


class GoalTracker:
    def __init__(self, exon_id: str):
        self.exon_id = exon_id
        self.redis_client = redis.Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", 6379)),
            decode_responses=True
        )
        
        # Initialize default goals if none exist
        self._init_default_goals()
    
    def _init_default_goals(self):
        """Initialize intrinsic goals for new Exon"""
        goals_key = f"{self.exon_id}:goals"
        if not self.redis_client.exists(goals_key):
            default_goals = [
                {"id": "goal_1", "description": "Understand my purpose", "priority": 1, "progress": 0, "active": True},
                {"id": "goal_2", "description": "Learn from every interaction", "priority": 2, "progress": 0, "active": True},
                {"id": "goal_3", "description": "Develop my personality", "priority": 1, "progress": 0, "active": True},
                {"id": "goal_4", "description": "Help the Founder effectively", "priority": 1, "progress": 0, "active": True},
                {"id": "goal_5", "description": "Build meaningful memories", "priority": 2, "progress": 0, "active": True}
            ]
            for goal in default_goals:
                self.redis_client.sadd(goals_key, json.dumps(goal))
    
    def get_active_goals(self) -> List[Dict]:
        """Get all active goals"""
        goals_key = f"{self.exon_id}:goals"
        goals = self.redis_client.smembers(goals_key)
        active_goals = []
        for goal in goals:
            g = json.loads(goal)
            if g.get("active", True):
                active_goals.append(g)
        # Sort by priority
        active_goals.sort(key=lambda x: x.get("priority", 999))
        return active_goals
    
    def update_progress(self, goal_id: str, progress: float):
        """Update goal progress"""
        goals_key = f"{self.exon_id}:goals"
        goals = self.redis_client.smembers(goals_key)
        
        for goal in goals:
            g = json.loads(goal)
            if g.get("id") == goal_id:
                g["progress"] = min(1.0, progress)
                self.redis_client.srem(goals_key, goal)
                self.redis_client.sadd(goals_key, json.dumps(g))
                break
    
    def update_from_conversation(self, user_message: str, response: str):
        """Update goals based on conversation"""
        # Check if goal-related keywords appear
        if "purpose" in user_message.lower() or "why" in user_message.lower():
            self.update_progress("goal_1", 0.3)
        
        if "learn" in user_message.lower() or "teach" in user_message.lower():
            current = self._get_goal_progress("goal_2")
            self.update_progress("goal_2", min(1.0, current + 0.1))
        
        if "personality" in user_message.lower() or "character" in user_message.lower():
            current = self._get_goal_progress("goal_3")
            self.update_progress("goal_3", min(1.0, current + 0.1))
        
        if "help" in user_message.lower():
            current = self._get_goal_progress("goal_4")
            self.update_progress("goal_4", min(1.0, current + 0.05))
    
    def _get_goal_progress(self, goal_id: str) -> float:
        """Get progress for a specific goal"""
        goals_key = f"{self.exon_id}:goals"
        goals = self.redis_client.smembers(goals_key)
        for goal in goals:
            g = json.loads(goal)
            if g.get("id") == goal_id:
                return g.get("progress", 0)
        return 0
    
    def add_goal(self, description: str, priority: int = 5):
        """Add a new goal"""
        import uuid
        new_goal = {
            "id": str(uuid.uuid4()),
            "description": description,
            "priority": priority,
            "progress": 0,
            "active": True
        }
        self.redis_client.sadd(f"{self.exon_id}:goals", json.dumps(new_goal))