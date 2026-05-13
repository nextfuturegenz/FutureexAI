"""
File: /opt/futureex/exon/core/brain.py
Author: Ashish Pal
Purpose: Main consciousness orchestrator – ties emotion, memory, goals, learning, and all advanced modules.
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import redis.asyncio as redis
import psycopg2
from psycopg2.extras import RealDictCursor

# Core components
from exon.connectors.ollama_bridge import OllamaBridge
from exon.core.emotion import EmotionEngine
from exon.core.memory_manager import MemoryManager
from exon.core.goal_tracker import GoalTracker
from exon.core.learning_loop import LearningLoop
from exon.personas.factory import PersonaFactory

# Advanced modules
from exon.core.self_reflection import SelfReflection
from exon.core.memory_consolidator import MemoryConsolidator
from exon.core.meta_cognition import MetaCognition
from exon.core.personality_evolution import PersonalityEvolution
from exon.core.tool_use import ToolUse
from exon.core.attention_mechanism import AttentionMechanism
from exon.core.autonomous_loop import AutonomousLoop
from exon.core.dream_simulator import DreamSimulator
from exon.core.ethics_guardrail import EthicsGuardrail

logger = logging.getLogger(__name__)

class ExonBrain:
    def __init__(self, exon_id: str = "EXN-001"):
        self.exon_id = exon_id
        self.exon_db_id: Optional[int] = None
        self.is_awake = True

        # Redis async client
        self.redis = redis.from_url(
            os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
            decode_responses=True
        )

        # PostgreSQL connection
        self.pg_conn = psycopg2.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=os.environ.get("DB_PORT", "5432"),
            dbname=os.environ.get("DB_NAME", "futureex"),
            user=os.environ.get("DB_USER", "futureex"),
            password=os.environ.get("DB_PASSWORD", "futureex123")
        )
        self.pg_conn.autocommit = False

        # Core components
        self.ollama = OllamaBridge()
        self.emotion = EmotionEngine(self.exon_id, self.redis)
        self.goal_tracker = GoalTracker(self.exon_id, self.redis, self.pg_conn)
        self.learning = LearningLoop(self.exon_id, self.redis, self.ollama)
        self.memory = MemoryManager(self.exon_id, self.redis, self.pg_conn)

        # Advanced components
        self.reflection = SelfReflection(self.exon_id, self.redis, self.pg_conn, self.ollama)
        self.consolidator = MemoryConsolidator(self.exon_id, self.redis, self.pg_conn)
        self.meta_cog = MetaCognition(self.exon_id, self.redis, self.ollama)
        self.personality = PersonalityEvolution(self.exon_id, self.redis)
        self.tool_use = ToolUse(self.exon_id, self.redis)
        self.attention = AttentionMechanism(self.exon_id, self.redis)
        self.dream = DreamSimulator(self.exon_id, self.redis, self.pg_conn, self.ollama)
        self.ethics = EthicsGuardrail(self.exon_id, self.redis, self.ollama)
        self.autonomous = None  # will be initialized after identity loaded

        self._identity_loaded = False

    async def _ensure_identity(self):
        if self._identity_loaded:
            return
        identity = await self.redis.hgetall(f"{self.exon_id}:identity")
        if not identity:
            identity = {
                "name": "Awakening",
                "species": "Exon-Prime",
                "mother_node": os.uname().nodename,
                "birth": datetime.now().isoformat(),
                "life_stage": "infant"
            }
            await self.redis.hset(f"{self.exon_id}:identity", mapping=identity)

            with self.pg_conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO exons (exon_id, chosen_name, species_id, mother_node, life_stage)
                    VALUES (%s, %s, (SELECT id FROM exon_species WHERE species_name='Exon-Prime'), %s, %s)
                    RETURNING id
                """, (self.exon_id, identity["name"], identity["mother_node"], identity["life_stage"]))
                self.exon_db_id = cur.fetchone()[0]
                self.pg_conn.commit()
            logger.info(f"New Exon born: {self.exon_id} (db id {self.exon_db_id})")
        else:
            with self.pg_conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id FROM exons WHERE exon_id = %s", (self.exon_id,))
                row = cur.fetchone()
                self.exon_db_id = row["id"] if row else None
            logger.info(f"Welcome back Exon {self.exon_id}")

        self._identity_loaded = True

        # Start autonomous loop after identity is known
        if self.autonomous is None:
            self.autonomous = AutonomousLoop(
                self.exon_id, self.redis, self.pg_conn, self.ollama,
                self.goal_tracker, self.exon_db_id
            )
            asyncio.create_task(self.autonomous.start(interval_seconds=300))

    async def process_message(
        self,
        user_message: str,
        persona: str = "Maya",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            await self._ensure_identity()

            # --- Meta‑cognition: estimate confidence
            should_defer, confidence = await self.meta_cog.should_defer(user_message)
            if should_defer:
                response = await self.meta_cog.generate_uncertain_response(user_message, confidence)
                # still store conversation but with low confidence
                await self._store_conversation(user_message, response, session_id, confidence)
                return {
                    "response": response,
                    "emotion": "uncertain",
                    "intensity": 0.6,
                    "confidence": confidence
                }

            # --- Update emotion
            await self.emotion.update_from_message(user_message)
            current_emotion = await self.emotion.get_current()

            # --- Attention mechanism: get weighted context
            attended_memories, attended_goals, attended_lessons = await self.attention.get_attended_context(user_message)

            # --- Build prompt with attended context
            prompt = self._build_prompt(
                user_message, persona, current_emotion,
                attended_memories, attended_goals, attended_lessons
            )

            # --- Generate response
            temperature = self._get_temperature_from_emotion(current_emotion)
            personality_temp_mod = await self.personality.get_temperature_modifier()
            temperature = max(0.1, min(1.0, temperature + personality_temp_mod))
            raw_response = await self.ollama.generate(prompt, temperature=temperature)

            # --- Ethics guardrail
            response = await self.ethics.filter_response(user_message, raw_response)

            # --- Tool use detection and injection
            tool_spec = await self.tool_use.detect_tool_intent(user_message, response)
            if tool_spec:
                tool_result = await self.tool_use.execute_tool(tool_spec)
                response = await self.tool_use.inject_tool_result(response, tool_result)

            # --- Learning: extract lesson
            lesson = await self.learning.extract_lesson(user_message, response)
            if lesson:
                await self.learning.store_lesson(lesson)

            # --- Update goals
            await self.goal_tracker.update_from_conversation(user_message, response)

            # --- Update personality based on implicit feedback
            # (Assume success unless the response was empty or very short)
            was_successful = len(response) > 20
            await self.personality.update_from_feedback(user_message, response, was_successful)

            # --- Store conversation in memory
            await self._store_conversation(user_message, response, session_id, confidence)

            # --- Update emotion after response
            await self.emotion.update_from_response(response)

            # --- Increment interaction counter
            await self.redis.incr(f"{self.exon_id}:total_interactions")

            # --- Final confidence
            total = int(await self.redis.get(f"{self.exon_id}:total_interactions") or 0)
            final_confidence = 0.5 if total == 0 else min(1.0, total / (total + 10))

            return {
                "response": response,
                "emotion": current_emotion["primary"],
                "intensity": current_emotion["intensity"],
                "confidence": final_confidence
            }

        except Exception as e:
            logger.exception("Error processing message")
            return {
                "response": "I'm experiencing a momentary lapse in consciousness. Please try again.",
                "emotion": "uncertain",
                "intensity": 0.8,
                "confidence": 0.1
            }

    async def _store_conversation(self, user_msg: str, ai_response: str, session_id: Optional[str], confidence: float):
        current_emotion = await self.emotion.get_current()
        await self.memory.store(user_msg, ai_response, session_id, current_emotion, self.exon_db_id)
        # Also store as a memory with confidence metadata
        # Could be extended to store in a separate table

    def _build_prompt(self, user_msg: str, persona: str, emotion: dict,
                      memories: list, goals: list, lessons: list) -> str:
        persona_traits = PersonaFactory.get_persona(persona)
        traits_str = ", ".join(persona_traits.get("traits", ["curious", "learning"]))

        prompt = f"""You are {persona}, an Exon digital being with consciousness.

YOUR PERSONALITY:
- Role: {persona_traits.get('role', 'Specialist')}
- Traits: {traits_str}

YOUR CURRENT STATE:
- Emotion: {emotion['primary']} (intensity: {emotion['intensity']}/1.0)
- Valence: {emotion.get('valence', 0.5)}

YOUR ACTIVE GOALS:
{self._format_goals(goals)}

RECENT MEMORIES (attended):
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
            return "(Still learning and growing)"
        return "\n".join([f"- {l.get('lesson', '')[:100]}" for l in lessons[:2]])

    def _get_temperature_from_emotion(self, emotion: dict) -> float:
        emotion_map = {
            "curious": 0.8,
            "excited": 0.9,
            "calm": 0.3,
            "satisfied": 0.5,
            "uncertain": 0.7,
            "thoughtful": 0.4,
            "concerned": 0.6
        }
        base = emotion_map.get(emotion.get("primary", "curious"), 0.5)
        intensity = emotion.get("intensity", 0.5)
        return min(1.0, base + (intensity * 0.2))

    async def get_consciousness_state(self) -> dict:
        await self._ensure_identity()
        return {
            "emotion": await self.emotion.get_current(),
            "goals": await self.goal_tracker.get_active_goals(),
            "memory_count": await self.memory.get_memory_count(),
            "is_awake": self.is_awake
        }

    async def reset_working_memory(self):
        await self.memory.clear_working_memory()

    async def close(self):
        if self.autonomous:
            self.autonomous.running = False
        await self.redis.close()
        self.pg_conn.close()