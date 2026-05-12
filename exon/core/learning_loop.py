"""
Learning Loop - Extract lessons from interactions
"""

import redis
import os
import json
from typing import Optional, Dict, List


class LearningLoop:
    def __init__(self, exon_id: str):
        self.exon_id = exon_id
        self.redis_client = redis.Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", 6379)),
            decode_responses=True
        )
    
    def extract_lesson(self, user_message: str, response: str) -> Optional[str]:
        """Extract a lesson from the interaction"""
        # Simple rule-based lesson extraction
        # In production, use Ollama to extract lessons
        
        if "thank" in user_message.lower():
            return "I learned that helping the Founder creates positive feedback"
        
        if "wrong" in user_message.lower() or "incorrect" in user_message.lower():
            return "I learned that I should be more careful with my responses"
        
        if "learn" in user_message.lower():
            return "I learned that the Founder wants to teach me new things"
        
        if "?" in user_message and len(user_message) > 50:
            return "I learned that complex questions require thoughtful responses"
        
        return None
    
    def store_lesson(self, lesson: str):
        """Store a learned lesson"""
        lesson_entry = {
            "lesson": lesson,
            "timestamp": str(__import__('datetime').datetime.now()),
            "reinforcement_count": 1
        }
        
        # Store in Redis
        self.redis_client.lpush(f"{self.exon_id}:lessons", json.dumps(lesson_entry))
        self.redis_client.ltrim(f"{self.exon_id}:lessons", 0, 99)  # Keep last 100
    
    def get_relevant_lessons(self, context: str, limit: int = 3) -> List[Dict]:
        """Get lessons relevant to current context"""
        lessons = []
        all_lessons = self.redis_client.lrange(f"{self.exon_id}:lessons", 0, -1)
        
        for lesson in all_lessons:
            try:
                l = json.loads(lesson)
                # Simple keyword matching
                if any(word in context.lower() for word in l.get("lesson", "").lower().split()[:3]):
                    lessons.append(l)
            except:
                pass
        
        return lessons[:limit]
    
    def reinforce_lesson(self, lesson: str, was_successful: bool):
        """Reinforce or weaken a lesson based on outcome"""
        # Find and update lesson
        all_lessons = self.redis_client.lrange(f"{self.exon_id}:lessons", 0, -1)
        
        for i, lesson_json in enumerate(all_lessons):
            l = json.loads(lesson_json)
            if l.get("lesson") == lesson:
                l["reinforcement_count"] = l.get("reinforcement_count", 1) + 1
                l["last_reinforced"] = str(__import__('datetime').datetime.now())
                l["successful"] = was_successful
                
                # Update in Redis
                self.redis_client.lset(f"{self.exon_id}:lessons", i, json.dumps(l))
                break