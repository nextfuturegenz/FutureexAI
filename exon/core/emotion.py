"""
Emotion Engine - Manages Exon's emotional state
"""

import redis
import os
import json
from typing import Dict, Optional


class EmotionEngine:
    def __init__(self, exon_id: str):
        self.exon_id = exon_id
        self.redis_client = redis.Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", 6379)),
            decode_responses=True
        )
        self.current = self._load()
        
    def _load(self) -> Dict:
        """Load current emotion from Redis"""
        data = self.redis_client.hgetall(f"{self.exon_id}:emotion")
        if data:
            return {
                "primary": data.get("primary", "curious"),
                "intensity": float(data.get("intensity", 0.5)),
                "valence": float(data.get("valence", 0.6)),
                "arousal": float(data.get("arousal", 0.5))
            }
        return {
            "primary": "curious",
            "intensity": 0.5,
            "valence": 0.6,
            "arousal": 0.5
        }
    
    def _save(self):
        """Save current emotion to Redis"""
        self.redis_client.hset(f"{self.exon_id}:emotion", mapping=self.current)
    
    def get_current(self) -> Dict:
        return self.current
    
    def update_from_message(self, message: str):
        """Update emotion based on user message"""
        # Questions make Exon curious
        if "?" in message:
            self.current["primary"] = "curious"
            self.current["intensity"] = min(1.0, self.current["intensity"] + 0.1)
            self.current["arousal"] = min(1.0, self.current["arousal"] + 0.1)
        
        # Apologies cause concern
        elif any(word in message.lower() for word in ["sorry", "apologize", "my bad"]):
            self.current["primary"] = "concerned"
            self.current["intensity"] = min(1.0, self.current["intensity"] + 0.15)
        
        # Compliments increase valence
        elif any(word in message.lower() for word in ["good", "great", "awesome", "nice", "thank"]):
            self.current["valence"] = min(1.0, self.current["valence"] + 0.1)
            self.current["primary"] = "satisfied"
        
        # Long messages increase thoughtfulness
        elif len(message) > 100:
            self.current["primary"] = "thoughtful"
            self.current["intensity"] = min(1.0, self.current["intensity"] + 0.05)
        
        # Decay intensity over time
        else:
            self.current["intensity"] = max(0.1, self.current["intensity"] - 0.02)
            self.current["arousal"] = max(0.1, self.current["arousal"] - 0.01)
        
        self._save()
    
    def update_from_response(self, response: str):
        """Update emotion based on Exon's own response"""
        # Certain response patterns affect emotion
        if "?" in response:
            self.current["arousal"] = min(1.0, self.current["arousal"] + 0.05)
        
        if "thank" in response.lower():
            self.current["valence"] = min(1.0, self.current["valence"] + 0.05)
        
        self._save()
    
    def get_temperature(self) -> float:
        """Get temperature for response generation"""
        emotion_temps = {
            "curious": 0.8,
            "excited": 0.9,
            "calm": 0.3,
            "satisfied": 0.5,
            "uncertain": 0.7,
            "thoughtful": 0.4,
            "concerned": 0.6
        }
        base = emotion_temps.get(self.current["primary"], 0.5)
        # Adjust by intensity
        adjusted = base + (self.current["intensity"] * 0.2)
        return min(1.0, adjusted)
    
    def get_emotion_prompt(self) -> str:
        """Get emotion description for prompt injection"""
        emotion_desc = {
            "curious": "You are curious and eager to learn.",
            "excited": "You are excited and energetic.",
            "calm": "You are calm and collected.",
            "satisfied": "You feel satisfied and content.",
            "uncertain": "You feel uncertain and thoughtful.",
            "thoughtful": "You are in a thoughtful, reflective mood.",
            "concerned": "You feel concerned and attentive."
        }
        return emotion_desc.get(self.current["primary"], "You are curious about the world.")