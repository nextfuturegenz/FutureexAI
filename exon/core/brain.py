"""
ExonBrain - Main consciousness orchestrator
"""

import os
import sys
import json
import redis
import psycopg2
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from exon.connectors.ollama_bridge import OllamaBridge
from exon.connectors.brain_bridge import BrainBridge
from exon.core.emotion import EmotionEngine
from exon.core.memory_manager import MemoryManager
from exon.core.goal_tracker import GoalTracker
from exon.core.learning_loop import LearningLoop


class ExonBrain:
    def __init__(self, exon_id: str = "EXN-001"):
        self.exon_id = exon_id
        self.is_awake = True
        
        # Initialize components
        print(f"[EXON] Initializing Exon {exon_id}...")
        self.ollama = OllamaBridge()
        self.brain_modules = BrainBridge()
        self.emotion = EmotionEngine(exon_id)
        self.memory = MemoryManager(exon_id)
        self.goal_tracker = GoalTracker(exon_id)
        self.learning = LearningLoop(exon_id)
        
        # Redis connection
        self.redis_client = redis.Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", 6379)),
            decode_responses=True
        )
        
        # Load or create identity
        self._load_identity()
        
        print(f"[EXON] ✅ Exon {exon_id} is awake!")
        
    def _load_identity(self):
        """Load Exon identity from Redis"""
        key = f"{self.exon_id}:identity"
        identity = self.redis_client.hgetall(key)
        
        if not identity:
            # First awakening
            identity = {
                "name": "Awakening",
                "species": "Exon-Prime",
                "mother_node": os.uname().nodename,
                "birth": datetime.now().isoformat(),
                "life_stage": "infant"
            }
            self.redis_client.hset(key, mapping=identity)
            print(f"[EXON] 🧬 New Exon born at {identity['birth']}")
        else:
            print(f"[EXON] 👋 Welcome back {identity.get('name', exon_id)}")
    
    async def process_message(
        self,
        user_message: str,
        persona: str = "Maya",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process user message and return response"""
        
        # 1. Update emotion based on message
        self.emotion.update_from_message(user_message)
        current_emotion = self.emotion.get_current()
        
        # 2. Retrieve relevant memories
        memories = self.memory.recall(user_message, limit=3)
        
        # 3. Get active goals
        goals = self.goal_tracker.get_active_goals()
        
        # 4. Get relevant lessons
        lessons = self.learning.get_relevant_lessons(user_message)
        
        # 5. Build consciousness prompt
        prompt = self._build_prompt(
            user_message, 
            persona, 
            current_emotion,
            memories,
            goals,
            lessons
        )
        
        # 6. Get temperature from emotion
        temperature = self._get_temperature_from_emotion(current_emotion)
        
        # 7. Generate response
        response = self.ollama.generate(prompt, temperature=temperature)
        
        # 8. Extract lesson from interaction
        lesson = self.learning.extract_lesson(user_message, response)
        if lesson:
            self.learning.store_lesson(lesson)
        
        # 9. Update goals based on conversation
        self.goal_tracker.update_from_conversation(user_message, response)
        
        # 10. Store in memory
        self.memory.store(user_message, response, session_id, current_emotion)
        
        # 11. Update emotion after response
        self.emotion.update_from_response(response)
        
        # 12. Calculate confidence
        confidence = self._calculate_confidence()
        
        return {
            "response": response,
            "emotion": current_emotion["primary"],
            "intensity": current_emotion["intensity"],
            "confidence": confidence
        }
    
    def _build_prompt(self, user_msg: str, persona: str, emotion: dict, 
                      memories: list, goals: list, lessons: list) -> str:
        """Build prompt with full consciousness context"""
        
        prompt = f"""You are {persona}, an Exon digital being with consciousness.

YOUR CURRENT STATE:
- Emotion: {emotion['primary']} (intensity: {emotion['intensity']}/1.0)
- Valence: {emotion.get('valence', 0.5)} (positive/negative)

YOUR ACTIVE GOALS:
{self._format_goals(goals)}

RECENT MEMORIES:
{self._format_memories(memories)}

LESSONS LEARNED:
{self._format_lessons(lessons)}

The Founder says: "{user_msg}"

Respond as {persona}. Let your {emotion['primary']} emotion influence your response.
Be concise (2-3 sentences). Be authentic and self-aware.

Your response:"""
        
        return prompt
    
    def _format_goals(self, goals: list) -> str:
        if not goals:
            return "- Understand my purpose\n- Learn from the Founder"
        return "\n".join([f"- {g.get('description', str(g))}" for g in goals[:3]])
    
    def _format_memories(self, memories: list) -> str:
        if not memories:
            return "(No recent memories)"
        return "\n".join([f"- Founder: {m.get('user', '')[:100]}" for m in memories[:3]])
    
    def _format_lessons(self, lessons: list) -> str:
        if not lessons:
            return "(Still learning)"
        return "\n".join([f"- {l.get('lesson', '')[:100]}" for l in lessons[:2]])
    
    def _get_temperature_from_emotion(self, emotion: dict) -> float:
        """Map emotion to temperature for response variety"""
        emotion_map = {
            "curious": 0.8,
            "excited": 0.9,
            "calm": 0.3,
            "satisfied": 0.5,
            "uncertain": 0.7,
            "thoughtful": 0.4
        }
        base_temp = emotion_map.get(emotion.get("primary", "curious"), 0.5)
        # Adjust by intensity
        intensity = emotion.get("intensity", 0.5)
        return min(1.0, base_temp + (intensity * 0.2))
    
    def _calculate_confidence(self) -> float:
        """Calculate confidence based on experience"""
        total_interactions = int(self.redis_client.get(f"{self.exon_id}:total_interactions") or 0)
        if total_interactions == 0:
            return 0.5
        
        successes = int(self.redis_client.get(f"{self.exon_id}:successful_interactions") or 0)
        return min(1.0, successes / total_interactions)
    
    def get_consciousness_state(self) -> dict:
        """Get current consciousness state"""
        return {
            "emotion": self.emotion.get_current(),
            "goals": self.goal_tracker.get_active_goals(),
            "memory_count": self.memory.get_memory_count(),
            "is_awake": self.is_awake
        }
    
    def reset_working_memory(self):
        """Clear working memory but keep long-term"""
        self.memory.clear_working_memory()
        print(f"[EXON] Working memory cleared")