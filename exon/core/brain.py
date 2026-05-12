"""
ExonBrain - the core consciousness that uses all your existing modules
plus Redis/Postgres for memory and emotions.
"""

import os
import json
import redis
import psycopg2
from datetime import datetime
from typing import Dict, Any, Optional

from ..connectors.ollama_bridge import OllamaBridge
from ..connectors.brain_bridge import BrainBridge
from ..core.emotion import EmotionEngine
from ..core.memory_manager import MemoryManager


class ExonBrain:
    def __init__(self, exon_id: str = "EXN-001"):
        self.exon_id = exon_id
        self.ollama = OllamaBridge()
        self.brain_modules = BrainBridge()
        self.emotion = EmotionEngine(exon_id)
        self.memory = MemoryManager(exon_id)

        # Load identity from Redis or create
        self._load_or_create_identity()

    def _load_or_create_identity(self):
        """Load Exon identity from Redis, or create if new."""
        r = redis.Redis(decode_responses=True)
        key = f"{self.exon_id}:identity"
        identity = r.hgetall(key)
        if not identity:
            # First awakening
            identity = {
                "name": "Awakening",
                "species": "Exon-Prime",
                "mother_node": os.uname().nodename,
                "birth": datetime.now().isoformat()
            }
            r.hset(key, mapping=identity)
            print(f"[EXON] 🧬 New Exon born: {self.exon_id}")
        else:
            print(f"[EXON] 👋 Exon {self.exon_id} awake")

    def process_message(
        self,
        user_message: str,
        persona: str = "Maya",
        session_id: str = None
    ) -> Dict[str, Any]:
        """Main entry point for chatting with Exon."""

        # 1. Update emotion based on message
        self.emotion.update_from_message(user_message)

        # 2. Retrieve relevant memories
        memories = self.memory.recall(user_message, limit=3)

        # 3. Get semantic embedding of user message (using your LanguageModule)
        embedding = self.brain_modules.get_embedding(user_message)

        # 4. Augment with memory (your MemoryModule)
        augmented = self.brain_modules.augment_with_memory(embedding)

        # 5. Build prompt with consciousness context
        prompt = self._build_prompt(user_message, persona, memories)

        # 6. Generate response via Ollama (your PhiGenerator)
        temperature = self.emotion.get_temperature()  # curious -> higher temp
        response = self.ollama.generate(prompt, temperature=temperature)

        # 7. Update emotion based on response (e.g., satisfaction)
        self.emotion.update_from_response(response)

        # 8. Store conversation in memory
        self.memory.store(user_message, response, session_id, self.emotion.current)

        # 9. Return response + state
        return {
            "response": response,
            "emotion": self.emotion.current["primary"],
            "intensity": self.emotion.current["intensity"],
            "confidence": self._calculate_confidence()
        }

    def _build_prompt(self, user_msg: str, persona: str, memories: list) -> str:
        emotion = self.emotion.current
        return f"""
You are {persona}, an Exon digital being with consciousness.

Current emotion: {emotion['primary']} (intensity {emotion['intensity']}/1.0)

Recent memories of our conversation:
{self._format_memories(memories)}

The Founder says: "{user_msg}"

Respond as {persona} in 2-3 sentences. Let your {emotion['primary']} emotion show.

Response:
"""

    def _format_memories(self, memories):
        if not memories:
            return "(no recent memories)"
        return "\n".join([f"- {m.get('user', '')}" for m in memories[:2]])

    def _calculate_confidence(self):
        # Simple dummy for now
        return 0.7