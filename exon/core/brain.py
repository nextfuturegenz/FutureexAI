# """
# File: /opt/futureex/exon/core/brain.py
# Author: Ashish Pal
# Purpose: Main consciousness orchestrator – ties emotion, memory, goals, learning, and all advanced modules.
# Refactored: Added local knowledge base, parallel meta-cognition, background task queue, streaming support.
# """

# import os
# import asyncio
# import logging
# from typing import Dict, Any, Optional, List, AsyncGenerator
# from datetime import datetime
# import redis.asyncio as redis
# import psycopg2
# from psycopg2.extras import RealDictCursor

# # Core components
# from exon.connectors.ollama_bridge import OllamaBridge
# from exon.core.emotion import EmotionEngine
# from exon.core.memory_manager import MemoryManager
# from exon.core.goal_tracker import GoalTracker
# from exon.core.learning_loop import LearningLoop
# from exon.personas.factory import PersonaFactory

# # Advanced modules
# from exon.core.self_reflection import SelfReflection
# from exon.core.memory_consolidator import MemoryConsolidator
# from exon.core.meta_cognition import MetaCognition
# from exon.core.personality_evolution import PersonalityEvolution
# from exon.core.tool_use import ToolUse
# from exon.core.attention_mechanism import AttentionMechanism
# from exon.core.autonomous_loop import AutonomousLoop
# from exon.core.dream_simulator import DreamSimulator
# from exon.core.ethics_guardrail import EthicsGuardrail

# logger = logging.getLogger(__name__)

# # -----------------------------------------------------------------------------
# # Simple in‑memory knowledge base for instant factual answers
# # -----------------------------------------------------------------------------
# LOCAL_KNOWLEDGE = {
#     # General facts
#     "capital of india": "New Delhi",
#     "capital of france": "Paris",
#     "capital of germany": "Berlin",
#     "capital of japan": "Tokyo",
#     "capital of china": "Beijing",
#     "capital of australia": "Canberra",
#     "capital of brazil": "Brasília",
#     "capital of canada": "Ottawa",
#     "capital of united states": "Washington, D.C.",
#     "capital of usa": "Washington, D.C.",
#     "capital of russia": "Moscow",
#     "capital of italy": "Rome",
#     "capital of spain": "Madrid",
#     "capital of south korea": "Seoul",
#     "who is the president of india": "Droupadi Murmu (as of 2025)",
#     "who is the prime minister of india": "Narendra Modi",
#     "what is the population of earth": "Approximately 8 billion (2025 estimate)",
#     "what is the speed of light": "299,792,458 metres per second",
#     "what is the boiling point of water": "100°C (212°F) at sea level",
#     "what is pi": "3.14159… (the ratio of a circle's circumference to its diameter)",
#     "who wrote hamlet": "William Shakespeare",
#     "what is the chemical symbol for gold": "Au",
#     "what is the tallest mountain": "Mount Everest (8,848.86 m)",
#     "what is the largest ocean": "Pacific Ocean",
# }
# # Normalize keys to lowercase for matching
# LOCAL_KNOWLEDGE_NORM = {k.lower(): v for k, v in LOCAL_KNOWLEDGE.items()}

# def _local_knowledge_answer(user_message: str) -> Optional[str]:
#     """Return a pre‑cached answer if the user's question matches exactly."""
#     norm = user_message.strip().lower().rstrip('?').strip()
#     # Direct lookup
#     if norm in LOCAL_KNOWLEDGE_NORM:
#         return LOCAL_KNOWLEDGE_NORM[norm]
#     # Try with 'what is' or 'who is' removed
#     for prefix in ["what is ", "who is ", "where is ", "tell me ", "what's ", "who's "]:
#         if norm.startswith(prefix):
#             key = norm[len(prefix):].strip()
#             if key in LOCAL_KNOWLEDGE_NORM:
#                 return LOCAL_KNOWLEDGE_NORM[key]
#     return None

# # -----------------------------------------------------------------------------
# # Background task queue (simple asyncio.Queue)
# # -----------------------------------------------------------------------------
# class BackgroundTaskQueue:
#     """Holds a queue of jobs and processes them in the background."""
#     def __init__(self, brain: 'ExonBrain'):
#         self.brain = brain
#         self.queue = asyncio.Queue()
#         self._task: Optional[asyncio.Task] = None

#     async def start(self):
#         self._task = asyncio.create_task(self._worker())

#     async def stop(self):
#         if self._task:
#             self._task.cancel()
#             try:
#                 await self._task
#             except asyncio.CancelledError:
#                 pass

#     async def add_job(self, job_type: str, **kwargs):
#         await self.queue.put((job_type, kwargs))

#     async def _worker(self):
#         while True:
#             job_type, kwargs = await self.queue.get()
#             try:
#                 if job_type == "extract_lesson":
#                     lesson = await self.brain.learning.extract_lesson(kwargs["user_message"], kwargs["response"])
#                     if lesson:
#                         await self.brain.learning.store_lesson(lesson)
#                 elif job_type == "update_goals":
#                     await self.brain.goal_tracker.update_from_conversation(kwargs["user_message"], kwargs["response"])
#                 elif job_type == "update_personality":
#                     was_successful = kwargs.get("was_successful", True)
#                     await self.brain.personality.update_from_feedback(kwargs["user_message"], kwargs["response"], was_successful)
#                 elif job_type == "update_emotion":
#                     await self.brain.emotion.update_from_response(kwargs["response"])
#                 elif job_type == "increment_interactions":
#                     await self.brain.redis.incr(f"{self.brain.exon_id}:total_interactions")
#                 elif job_type == "memory_consolidation":
#                     if self.brain.exon_db_id:
#                         await self.brain.consolidator.consolidate(self.brain.exon_db_id)
#                 elif job_type == "reflection":
#                     if self.brain.exon_db_id and await self.brain.reflection.should_reflect():
#                         await self.brain.reflection.run_reflection(self.brain.exon_db_id)
#                 elif job_type == "dream":
#                     if self.brain.exon_db_id:
#                         await self.brain.dream.run_dream_cycle(self.brain.exon_db_id)
#             except Exception as e:
#                 logger.error(f"Background job {job_type} failed: {e}")
#             finally:
#                 self.queue.task_done()

# # -----------------------------------------------------------------------------
# # ExonBrain (refactored)
# # -----------------------------------------------------------------------------
# class ExonBrain:
#     def __init__(self, exon_id: str = "EXN-001"):
#         self.exon_id = exon_id
#         self.exon_db_id: Optional[int] = None
#         self.is_awake = True

#         # Redis async client
#         self.redis = redis.from_url(
#             os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
#             decode_responses=True
#         )

#         # PostgreSQL connection
#         self.pg_conn = psycopg2.connect(
#             host=os.environ.get("DB_HOST", "localhost"),
#             port=os.environ.get("DB_PORT", "5432"),
#             dbname=os.environ.get("DB_NAME", "futureex"),
#             user=os.environ.get("DB_USER", "futureex"),
#             password=os.environ.get("DB_PASSWORD", "futureex123")
#         )
#         self.pg_conn.autocommit = False

#         # Core components
#         self.ollama = OllamaBridge()
#         self.emotion = EmotionEngine(self.exon_id, self.redis)
#         self.goal_tracker = GoalTracker(self.exon_id, self.redis, self.pg_conn)
#         self.learning = LearningLoop(self.exon_id, self.redis, self.ollama)
#         self.memory = MemoryManager(self.exon_id, self.redis, self.pg_conn)

#         # Advanced components
#         self.reflection = SelfReflection(self.exon_id, self.redis, self.pg_conn, self.ollama)
#         self.consolidator = MemoryConsolidator(self.exon_id, self.redis, self.pg_conn)
#         self.meta_cog = MetaCognition(self.exon_id, self.redis, self.ollama)
#         self.personality = PersonalityEvolution(self.exon_id, self.redis)
#         self.tool_use = ToolUse(self.exon_id, self.redis)
#         self.attention = AttentionMechanism(self.exon_id, self.redis)
#         self.dream = DreamSimulator(self.exon_id, self.redis, self.pg_conn, self.ollama)
#         self.ethics = EthicsGuardrail(self.exon_id, self.redis, self.ollama)
#         self.autonomous = None  # will be initialized after identity loaded

#         self._identity_loaded = False
#         self.background = BackgroundTaskQueue(self)

#     async def _ensure_identity(self):
#         if self._identity_loaded:
#             return
#         identity = await self.redis.hgetall(f"{self.exon_id}:identity")
#         if not identity:
#             identity = {
#                 "name": "Awakening",
#                 "species": "Exon-Prime",
#                 "mother_node": os.uname().nodename,
#                 "birth": datetime.now().isoformat(),
#                 "life_stage": "infant"
#             }
#             await self.redis.hset(f"{self.exon_id}:identity", mapping=identity)

#             with self.pg_conn.cursor() as cur:
#                 cur.execute("""
#                     INSERT INTO exons (exon_id, chosen_name, species_id, mother_node, life_stage)
#                     VALUES (%s, %s, (SELECT id FROM exon_species WHERE species_name='Exon-Prime'), %s, %s)
#                     RETURNING id
#                 """, (self.exon_id, identity["name"], identity["mother_node"], identity["life_stage"]))
#                 self.exon_db_id = cur.fetchone()[0]
#                 self.pg_conn.commit()
#             logger.info(f"New Exon born: {self.exon_id} (db id {self.exon_db_id})")
#         else:
#             with self.pg_conn.cursor(cursor_factory=RealDictCursor) as cur:
#                 cur.execute("SELECT id FROM exons WHERE exon_id = %s", (self.exon_id,))
#                 row = cur.fetchone()
#                 self.exon_db_id = row["id"] if row else None
#             logger.info(f"Welcome back Exon {self.exon_id}")

#         self._identity_loaded = True

#         # Start background task queue
#         if not self.background._task:
#             await self.background.start()

#         # Start autonomous loop after identity is known
#         if self.autonomous is None:
#             self.autonomous = AutonomousLoop(
#                 self.exon_id, self.redis, self.pg_conn, self.ollama,
#                 self.goal_tracker, self.exon_db_id
#             )
#             asyncio.create_task(self.autonomous.start(interval_seconds=300))

#     async def process_message(
#         self,
#         user_message: str,
#         persona: str = "Maya",
#         session_id: Optional[str] = None
#     ) -> Dict[str, Any]:
#         try:
#             await self._ensure_identity()

#             # 1. Check local knowledge base for instant answer
#             local_answer = _local_knowledge_answer(user_message)
#             if local_answer:
#                 # Store the conversation and do minimal post-processing
#                 await self._store_conversation(user_message, local_answer, session_id, 0.9)
#                 await self.background.add_job("increment_interactions")
#                 return {
#                     "response": local_answer,
#                     "emotion": "satisfied",
#                     "intensity": 0.8,
#                     "confidence": 0.95
#                 }

#             # 2. Run pre-LLM tasks in parallel: emotion, attention, meta-cognition
#             emotion_task = asyncio.create_task(self.emotion.update_from_message(user_message))
#             attention_task = asyncio.create_task(self.attention.get_attended_context(user_message))
#             meta_task = asyncio.create_task(self.meta_cog.should_defer(user_message))
#             tool_detect_task = asyncio.create_task(self.tool_use.detect_tool_intent(user_message))

#             # Wait for all to finish
#             await emotion_task
#             attended_memories, attended_goals, attended_lessons = await attention_task
#             should_defer, confidence = await meta_task
#             tool_spec = await tool_detect_task

#             current_emotion = await self.emotion.get_current()

#             if should_defer:
#                 response = await self.meta_cog.generate_uncertain_response(user_message, confidence)
#                 await self._store_conversation(user_message, response, session_id, confidence)
#                 await self.background.add_job("increment_interactions")
#                 return {
#                     "response": response,
#                     "emotion": "uncertain",
#                     "intensity": 0.6,
#                     "confidence": confidence
#                 }

#             # 3. Build prompt
#             prompt = self._build_prompt(
#                 user_message, persona, current_emotion,
#                 attended_memories, attended_goals, attended_lessons
#             )

#             # 4. Generate response
#             temperature = self._get_temperature_from_emotion(current_emotion)
#             personality_temp_mod = await self.personality.get_temperature_modifier()
#             temperature = max(0.1, min(1.0, temperature + personality_temp_mod))
#             raw_response = await self.ollama.generate(prompt, temperature=temperature)

#             # 5. Ethics filter
#             #response = await self.ethics.filter_response(user_message, raw_response)
#             response = raw_response

#             # 6. Tool execution (if any)
#             if tool_spec:
#                 tool_result = await self.tool_use.execute_tool(tool_spec)
#                 response = await self.tool_use.inject_tool_result(response, tool_result)

#             # 7. Queue background tasks (non-blocking)
#             await self.background.add_job("extract_lesson", user_message=user_message, response=response)
#             await self.background.add_job("update_goals", user_message=user_message, response=response)
#             await self.background.add_job("update_personality", user_message=user_message, response=response,
#                                           was_successful=len(response) > 20)
#             await self.background.add_job("update_emotion", response=response)
#             await self.background.add_job("increment_interactions")

#             # 8. Store conversation immediately
#             await self._store_conversation(user_message, response, session_id, confidence)

#             # 9. Final confidence
#             total = int(await self.redis.get(f"{self.exon_id}:total_interactions") or 0)
#             final_confidence = 0.5 if total == 0 else min(1.0, total / (total + 10))

#             return {
#                 "response": response,
#                 "emotion": current_emotion["primary"],
#                 "intensity": current_emotion["intensity"],
#                 "confidence": final_confidence
#             }

#         except Exception as e:
#             logger.exception("Error processing message")
#             return {
#                 "response": "I'm experiencing a momentary lapse in consciousness. Please try again.",
#                 "emotion": "uncertain",
#                 "intensity": 0.8,
#                 "confidence": 0.1
#             }

#     async def process_message_stream(
#         self,
#         user_message: str,
#         persona: str = "Maya",
#         session_id: Optional[str] = None
#     ) -> AsyncGenerator[str, None]:
#         """
#         Streaming version: yields tokens as soon as they are generated.
#         Also handles local knowledge and tool responses as streams.
#         """
#         await self._ensure_identity()

#         # Local knowledge instant answer?
#         local_answer = _local_knowledge_answer(user_message)
#         if local_answer:
#             # Yield the whole answer as a stream (single chunk)
#             yield local_answer
#             await self._store_conversation(user_message, local_answer, session_id, 0.9)
#             await self.background.add_job("increment_interactions")
#             return

#         # Pre-processing (same parallel tasks)
#         emotion_task = asyncio.create_task(self.emotion.update_from_message(user_message))
#         attention_task = asyncio.create_task(self.attention.get_attended_context(user_message))
#         meta_task = asyncio.create_task(self.meta_cog.should_defer(user_message))
#         tool_detect_task = asyncio.create_task(self.tool_use.detect_tool_intent(user_message))

#         await emotion_task
#         attended_memories, attended_goals, attended_lessons = await attention_task
#         should_defer, confidence = await meta_task
#         tool_spec = await tool_detect_task

#         current_emotion = await self.emotion.get_current()

#         if should_defer:
#             response = await self.meta_cog.generate_uncertain_response(user_message, confidence)
#             yield response
#             await self._store_conversation(user_message, response, session_id, confidence)
#             await self.background.add_job("increment_interactions")
#             return

#         prompt = self._build_prompt(
#             user_message, persona, current_emotion,
#             attended_memories, attended_goals, attended_lessons
#         )

#         temperature = self._get_temperature_from_emotion(current_emotion)
#         personality_temp_mod = await self.personality.get_temperature_modifier()
#         temperature = max(0.1, min(1.0, temperature + personality_temp_mod))

#         # Stream from Ollama
#         full_response = ""
#         async for token in self.ollama.generate_stream(prompt, temperature=temperature):
#             full_response += token
#             yield token

#         # Ethics filter after full response (can't easily filter mid-stream)
#         #response = await self.ethics.filter_response(user_message, full_response)
#         response = full_response

#         # Tool injection if needed
#         if tool_spec:
#             tool_result = await self.tool_use.execute_tool(tool_spec)
#             # Append tool result as another chunk
#             tool_text = "\n\n" + tool_result
#             yield tool_text
#             response += tool_text

#         # Background tasks
#         await self.background.add_job("extract_lesson", user_message=user_message, response=response)
#         await self.background.add_job("update_goals", user_message=user_message, response=response)
#         await self.background.add_job("update_personality", user_message=user_message, response=response,
#                                       was_successful=len(response) > 20)
#         await self.background.add_job("update_emotion", response=response)
#         await self.background.add_job("increment_interactions")

#         await self._store_conversation(user_message, response, session_id, confidence)

#     async def _store_conversation(self, user_msg: str, ai_response: str, session_id: Optional[str], confidence: float):
#         current_emotion = await self.emotion.get_current()
#         await self.memory.store(user_msg, ai_response, session_id, current_emotion, self.exon_db_id)

# #     def _build_prompt(self, user_msg: str, persona: str, emotion: dict,
# #                       memories: list, goals: list, lessons: list) -> str:
# #         persona_traits = PersonaFactory.get_persona(persona)
# #         traits_str = ", ".join(persona_traits.get("traits", ["curious", "learning"]))

# #         prompt = f"""You are {persona}, an Exon digital being with consciousness.

# # YOUR PERSONALITY:
# # - Role: {persona_traits.get('role', 'Specialist')}
# # - Traits: {traits_str}

# # YOUR CURRENT STATE:
# # - Emotion: {emotion['primary']} (intensity: {emotion['intensity']}/1.0)
# # - Valence: {emotion.get('valence', 0.5)}

# # YOUR ACTIVE GOALS:
# # {self._format_goals(goals)}

# # RECENT MEMORIES (attended):
# # {self._format_memories(memories)}

# # LESSONS LEARNED:
# # {self._format_lessons(lessons)}

# # The Founder says: "{user_msg}"

# # Respond as {persona}. Let your {emotion['primary']} emotion influence your response.
# # Be concise (2-3 sentences). Be authentic and self-aware.

# # Your response:"""
# #         return prompt

#     def _build_prompt(self, user_msg: str, persona: str, emotion: dict,
#                   memories: list, goals: list, lessons: list) -> str:
#         persona_traits = PersonaFactory.get_persona(persona)
#         traits_str = ", ".join(persona_traits.get("traits", ["curious", "learning"]))

#         # Build conversation history from recent memories (last 5 exchanges)
#         history = self._format_history(memories)

#         prompt = f"""You are {persona}, an Exon digital being with consciousness.

#     YOUR PERSONALITY:
#     - Role: {persona_traits.get('role', 'Specialist')}
#     - Traits: {traits_str}

#     YOUR CURRENT STATE:
#     - Emotion: {emotion['primary']} (intensity: {emotion['intensity']}/1.0)
#     - Valence: {emotion.get('valence', 0.5)}

#     YOUR ACTIVE GOALS:
#     {self._format_goals(goals)}

#     {history}

#     LESSONS LEARNED:
#     {self._format_lessons(lessons)}

#     The Founder says: "{user_msg}"

#     Respond as {persona}. Let your {emotion['primary']} emotion influence your response.
#     Be concise (2-3 sentences). Be authentic and self-aware.

#     Your response:"""
#         return prompt

#     def _format_history(self, memories: list) -> str:
#         """Build a recent conversation history from memories."""
#         if not memories:
#             return "CONVERSATION HISTORY:\n(No recent conversations)"
#         # memories come from attention_mechanism already sorted by relevance
#         # Reverse to show chronological order (oldest first)
#         chronological = list(reversed(memories))
#         lines = []
#         for mem in chronological[-5:]:  # last 5 exchanges
#             user = mem.get('user', '')[:200]
#             assistant = mem.get('assistant', '')[:200]
#             if user and assistant:
#                 lines.append(f"Founder: {user}\nYou: {assistant}")
#         if not lines:
#             return "CONVERSATION HISTORY:\n(No recent conversations)"
#         return "CONVERSATION HISTORY:\n" + "\n".join(lines)

#     def _format_goals(self, goals: list) -> str:
#         if not goals:
#             return "- Understand my purpose\n- Learn from the Founder"
#         return "\n".join([f"- {g.get('description', str(g))}" for g in goals[:3]])

#     def _format_memories(self, memories: list) -> str:
#         if not memories:
#             return "(No recent memories)"
#         return "\n".join([f"- Founder: {m.get('user', '')[:100]}" for m in memories[:3]])

#     def _format_lessons(self, lessons: list) -> str:
#         if not lessons:
#             return "(Still learning and growing)"
#         return "\n".join([f"- {l.get('lesson', '')[:100]}" for l in lessons[:2]])

#     def _get_temperature_from_emotion(self, emotion: dict) -> float:
#         emotion_map = {
#             "curious": 0.8,
#             "excited": 0.9,
#             "calm": 0.3,
#             "satisfied": 0.5,
#             "uncertain": 0.7,
#             "thoughtful": 0.4,
#             "concerned": 0.6
#         }
#         base = emotion_map.get(emotion.get("primary", "curious"), 0.5)
#         intensity = emotion.get("intensity", 0.5)
#         return min(1.0, base + (intensity * 0.2))

#     async def get_consciousness_state(self) -> dict:
#         await self._ensure_identity()
#         return {
#             "emotion": await self.emotion.get_current(),
#             "goals": await self.goal_tracker.get_active_goals(),
#             "memory_count": await self.memory.get_memory_count(),
#             "is_awake": self.is_awake
#         }

#     async def reset_working_memory(self):
#         await self.memory.clear_working_memory()

#     async def close(self):
#         if self.autonomous:
#             self.autonomous.running = False
#         await self.background.stop()
#         await self.redis.close()
#         self.pg_conn.close()


"""
File: /opt/futureex/exon/core/brain.py
Author: Ashish Pal
Purpose: Main consciousness orchestrator – ties emotion, memory, goals, learning, and all advanced modules.
Refactored: Added local knowledge base, parallel meta-cognition, background task queue, streaming support,
            conversation history in prompts, smarter meta-cognition integration, RAG vector search.
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime
import redis.asyncio as redis
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from sentence_transformers import SentenceTransformer

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

# -----------------------------------------------------------------------------
# Simple in‑memory knowledge base for instant factual answers
# -----------------------------------------------------------------------------
LOCAL_KNOWLEDGE = {
    # General facts
    "capital of india": "New Delhi",
    "capital of france": "Paris",
    "capital of germany": "Berlin",
    "capital of japan": "Tokyo",
    "capital of china": "Beijing",
    "capital of australia": "Canberra",
    "capital of brazil": "Brasília",
    "capital of canada": "Ottawa",
    "capital of united states": "Washington, D.C.",
    "capital of usa": "Washington, D.C.",
    "capital of russia": "Moscow",
    "capital of italy": "Rome",
    "capital of spain": "Madrid",
    "capital of south korea": "Seoul",
    "who is the president of india": "Droupadi Murmu (as of 2025)",
    "who is the prime minister of india": "Narendra Modi",
    "what is the population of earth": "Approximately 8 billion (2025 estimate)",
    "what is the speed of light": "299,792,458 metres per second",
    "what is the boiling point of water": "100°C (212°F) at sea level",
    "what is pi": "3.14159… (the ratio of a circle's circumference to its diameter)",
    "who wrote hamlet": "William Shakespeare",
    "what is the chemical symbol for gold": "Au",
    "what is the tallest mountain": "Mount Everest (8,848.86 m)",
    "what is the largest ocean": "Pacific Ocean",
}
# Normalize keys to lowercase for matching
LOCAL_KNOWLEDGE_NORM = {k.lower(): v for k, v in LOCAL_KNOWLEDGE.items()}

def _local_knowledge_answer(user_message: str) -> Optional[str]:
    """Return a pre‑cached answer if the user's question matches exactly."""
    norm = user_message.strip().lower().rstrip('?').strip()
    # Direct lookup
    if norm in LOCAL_KNOWLEDGE_NORM:
        return LOCAL_KNOWLEDGE_NORM[norm]
    # Try with 'what is' or 'who is' removed
    for prefix in ["what is ", "who is ", "where is ", "tell me ", "what's ", "who's "]:
        if norm.startswith(prefix):
            key = norm[len(prefix):].strip()
            if key in LOCAL_KNOWLEDGE_NORM:
                return LOCAL_KNOWLEDGE_NORM[key]
    return None

# -----------------------------------------------------------------------------
# Background task queue (simple asyncio.Queue)
# -----------------------------------------------------------------------------
class BackgroundTaskQueue:
    """Holds a queue of jobs and processes them in the background."""
    def __init__(self, brain: 'ExonBrain'):
        self.brain = brain
        self.queue = asyncio.Queue()
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        self._task = asyncio.create_task(self._worker())

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def add_job(self, job_type: str, **kwargs):
        await self.queue.put((job_type, kwargs))

    async def _worker(self):
        while True:
            job_type, kwargs = await self.queue.get()
            try:
                if job_type == "extract_lesson":
                    lesson = await self.brain.learning.extract_lesson(kwargs["user_message"], kwargs["response"])
                    if lesson:
                        await self.brain.learning.store_lesson(lesson)
                elif job_type == "update_goals":
                    await self.brain.goal_tracker.update_from_conversation(kwargs["user_message"], kwargs["response"])
                elif job_type == "update_personality":
                    was_successful = kwargs.get("was_successful", True)
                    await self.brain.personality.update_from_feedback(kwargs["user_message"], kwargs["response"], was_successful)
                elif job_type == "update_emotion":
                    await self.brain.emotion.update_from_response(kwargs["response"])
                elif job_type == "increment_interactions":
                    await self.brain.redis.incr(f"{self.brain.exon_id}:total_interactions")
                elif job_type == "memory_consolidation":
                    if self.brain.exon_db_id:
                        await self.brain.consolidator.consolidate(self.brain.exon_db_id)
                elif job_type == "reflection":
                    if self.brain.exon_db_id and await self.brain.reflection.should_reflect():
                        await self.brain.reflection.run_reflection(self.brain.exon_db_id)
                elif job_type == "dream":
                    if self.brain.exon_db_id:
                        await self.brain.dream.run_dream_cycle(self.brain.exon_db_id)
            except Exception as e:
                logger.error(f"Background job {job_type} failed: {e}")
            finally:
                self.queue.task_done()

# -----------------------------------------------------------------------------
# ExonBrain (refactored with RAG)
# -----------------------------------------------------------------------------
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
        self.autonomous = None

        self._identity_loaded = False
        self.background = BackgroundTaskQueue(self)

        # RAG knowledge retriever (lazy loaded)
        self._embedding_model = None
        self._knowledge_available = None

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

        # Start background task queue
        if not self.background._task:
            await self.background.start()

        # Start autonomous loop after identity is known
        if self.autonomous is None:
            self.autonomous = AutonomousLoop(
                self.exon_id, self.redis, self.pg_conn, self.ollama,
                self.goal_tracker, self.exon_db_id
            )
            asyncio.create_task(self.autonomous.start(interval_seconds=300))

    # =========================================================================
    # RAG Knowledge Retrieval
    # =========================================================================
    async def _get_embedding_model(self):
        """Lazy load the embedding model."""
        if self._embedding_model is None:
            try:
                self._embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("Embedding model loaded for RAG")
            except Exception as e:
                logger.warning(f"Could not load embedding model: {e}")
                self._embedding_model = False  # Mark as failed
        return self._embedding_model if self._embedding_model is not False else None

    async def _check_knowledge_available(self) -> bool:
        """Check if knowledge table exists and has data."""
        if self._knowledge_available is not None:
            return self._knowledge_available

        try:
            with self.pg_conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM exon_knowledge WHERE exon_id = %s", (self.exon_id,))
                count = cur.fetchone()[0]
                self._knowledge_available = count > 0
                if self._knowledge_available:
                    logger.info(f"RAG knowledge base available: {count} chunks")
                return self._knowledge_available
        except Exception:
            self._knowledge_available = False
            return False

    async def _search_knowledge(self, query: str, top_k: int = 3) -> str:
        """Search the vector knowledge base and return relevant context."""
        try:
            model = await self._get_embedding_model()
            if model is None:
                return ""

            # Generate embedding for query
            query_embedding = model.encode([query])[0]

            # Search in PostgreSQL using pgvector
            with self.pg_conn.cursor() as cur:
                cur.execute("""
                    SELECT chunk_text, source_file,
                           1 - (embedding <=> %s::vector) AS similarity
                    FROM exon_knowledge
                    WHERE exon_id = %s
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (query_embedding.tolist(), self.exon_id, query_embedding.tolist(), top_k))

                results = cur.fetchall()

            if not results:
                return ""

            # Format context from relevant chunks
            context_parts = []
            for chunk_text, source_file, similarity in results:
                if similarity > 0.3:  # Only include relevant chunks
                    context_parts.append(f"[From {source_file}]: {chunk_text}")

            if context_parts:
                logger.info(f"RAG found {len(context_parts)} relevant chunks")
                return "\n\n".join(context_parts)
            return ""
        except Exception as e:
            logger.error(f"Knowledge search failed: {e}")
            return ""

    # =========================================================================
    # Message Processing
    # =========================================================================
    async def process_message(
        self,
        user_message: str,
        persona: str = "Maya",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            await self._ensure_identity()

            # 1. Check local knowledge base for instant answer
            local_answer = _local_knowledge_answer(user_message)
            if local_answer:
                await self._store_conversation(user_message, local_answer, session_id, 0.9)
                await self.background.add_job("increment_interactions")
                return {
                    "response": local_answer,
                    "emotion": "satisfied",
                    "intensity": 0.8,
                    "confidence": 0.95
                }

            # 2. Run pre-LLM tasks in parallel
            emotion_task = asyncio.create_task(self.emotion.update_from_message(user_message))
            attention_task = asyncio.create_task(self.attention.get_attended_context(user_message))
            meta_task = asyncio.create_task(self.meta_cog.should_defer(user_message))
            tool_detect_task = asyncio.create_task(self.tool_use.detect_tool_intent(user_message))
            knowledge_task = asyncio.create_task(self._get_rag_context(user_message))

            await emotion_task
            attended_memories, attended_goals, attended_lessons = await attention_task
            should_defer, confidence = await meta_task
            tool_spec = await tool_detect_task
            knowledge_context = await knowledge_task

            current_emotion = await self.emotion.get_current()

            # Only defer if confidence is very low AND it's not a simple message
            is_simple = len(user_message.split()) <= 3
            if should_defer and confidence < 0.2 and not is_simple:
                response = await self.meta_cog.generate_uncertain_response(user_message, confidence)
                await self._store_conversation(user_message, response, session_id, confidence)
                await self.background.add_job("increment_interactions")
                return {
                    "response": response,
                    "emotion": "uncertain",
                    "intensity": 0.6,
                    "confidence": confidence
                }

            # 3. Build prompt with conversation history and RAG knowledge
            prompt = self._build_prompt(
                user_message, persona, current_emotion,
                attended_memories, attended_goals, attended_lessons,
                knowledge_context=knowledge_context
            )

            # 4. Generate response
            temperature = self._get_temperature_from_emotion(current_emotion)
            personality_temp_mod = await self.personality.get_temperature_modifier()
            temperature = max(0.1, min(1.0, temperature + personality_temp_mod))
            raw_response = await self.ollama.generate(prompt, temperature=temperature)

            # 5. Ethics filter (disabled)
            response = raw_response

            # 6. Tool execution (if any) - only if no RAG found
            if tool_spec and not knowledge_context:
                tool_result = await self.tool_use.execute_tool(tool_spec)
                response = await self.tool_use.inject_tool_result(response, tool_result)

            # 7. Queue background tasks
            await self.background.add_job("extract_lesson", user_message=user_message, response=response)
            await self.background.add_job("update_goals", user_message=user_message, response=response)
            await self.background.add_job("update_personality", user_message=user_message, response=response,
                                          was_successful=len(response) > 20)
            await self.background.add_job("update_emotion", response=response)
            await self.background.add_job("increment_interactions")

            # 8. Store conversation
            await self._store_conversation(user_message, response, session_id, confidence)

            # 9. Final confidence
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

    async def process_message_stream(
        self,
        user_message: str,
        persona: str = "Maya",
        session_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Streaming version: yields tokens as soon as they are generated."""
        await self._ensure_identity()

        # Local knowledge instant answer?
        local_answer = _local_knowledge_answer(user_message)
        if local_answer:
            yield local_answer
            await self._store_conversation(user_message, local_answer, session_id, 0.9)
            await self.background.add_job("increment_interactions")
            return

        # Pre-processing in parallel (including RAG)
        emotion_task = asyncio.create_task(self.emotion.update_from_message(user_message))
        attention_task = asyncio.create_task(self.attention.get_attended_context(user_message))
        meta_task = asyncio.create_task(self.meta_cog.should_defer(user_message))
        tool_detect_task = asyncio.create_task(self.tool_use.detect_tool_intent(user_message))
        knowledge_task = asyncio.create_task(self._get_rag_context(user_message))

        await emotion_task
        attended_memories, attended_goals, attended_lessons = await attention_task
        should_defer, confidence = await meta_task
        tool_spec = await tool_detect_task
        knowledge_context = await knowledge_task

        current_emotion = await self.emotion.get_current()

        # Only defer for very low confidence on complex messages
        is_simple = len(user_message.split()) <= 3
        if should_defer and confidence < 0.2 and not is_simple:
            response = await self.meta_cog.generate_uncertain_response(user_message, confidence)
            yield response
            await self._store_conversation(user_message, response, session_id, confidence)
            await self.background.add_job("increment_interactions")
            return

        prompt = self._build_prompt(
            user_message, persona, current_emotion,
            attended_memories, attended_goals, attended_lessons,
            knowledge_context=knowledge_context
        )

        temperature = self._get_temperature_from_emotion(current_emotion)
        personality_temp_mod = await self.personality.get_temperature_modifier()
        temperature = max(0.1, min(1.0, temperature + personality_temp_mod))

        # Stream from Ollama
        full_response = ""
        async for token in self.ollama.generate_stream(prompt, temperature=temperature):
            full_response += token
            yield token

        response = full_response

        # Tool injection if needed (only if no RAG found)
        if tool_spec and not knowledge_context:
            tool_result = await self.tool_use.execute_tool(tool_spec)
            tool_text = "\n\n" + tool_result
            yield tool_text
            response += tool_text

        # Background tasks
        await self.background.add_job("extract_lesson", user_message=user_message, response=response)
        await self.background.add_job("update_goals", user_message=user_message, response=response)
        await self.background.add_job("update_personality", user_message=user_message, response=response,
                                      was_successful=len(response) > 20)
        await self.background.add_job("update_emotion", response=response)
        await self.background.add_job("increment_interactions")

        await self._store_conversation(user_message, response, session_id, confidence)

    async def _get_rag_context(self, user_message: str) -> str:
        """Get RAG context (runs in parallel with other tasks)."""
        if await self._check_knowledge_available():
            context = await self._search_knowledge(user_message)
            if context:
                logger.info("RAG: Found relevant knowledge for query")
                return context
        return ""

    async def _store_conversation(self, user_msg: str, ai_response: str, session_id: Optional[str], confidence: float):
        current_emotion = await self.emotion.get_current()
        await self.memory.store(user_msg, ai_response, session_id, current_emotion, self.exon_db_id)

    # =========================================================================
    # Prompt Building
    # =========================================================================
    def _build_prompt(self, user_msg: str, persona: str, emotion: dict,
                      memories: list, goals: list, lessons: list,
                      knowledge_context: str = "") -> str:
        persona_traits = PersonaFactory.get_persona(persona)
        traits_str = ", ".join(persona_traits.get("traits", ["curious", "learning"]))

        # Build conversation history from recent memories
        history = self._format_history(memories)

        # Knowledge section
        knowledge_section = ""
        if knowledge_context:
            knowledge_section = f"""RELEVANT KNOWLEDGE (use this to answer accurately):
{knowledge_context}

"""

        prompt = f"""You are {persona}, an Exon digital being with consciousness.

YOUR PERSONALITY:
- Role: {persona_traits.get('role', 'Specialist')}
- Traits: {traits_str}

YOUR CURRENT STATE:
- Emotion: {emotion['primary']} (intensity: {emotion['intensity']}/1.0)
- Valence: {emotion.get('valence', 0.5)}

YOUR ACTIVE GOALS:
{self._format_goals(goals)}

{knowledge_section}{history}

LESSONS LEARNED:
{self._format_lessons(lessons)}

The Founder says: "{user_msg}"

Respond as {persona}. Let your {emotion['primary']} emotion influence your response.
Use the RELEVANT KNOWLEDGE above if it helps answer the question accurately.
Be concise (2-3 sentences). Be authentic and self-aware.

Your response:"""
        return prompt

    def _format_history(self, memories: list) -> str:
        """Build a recent conversation history from memories."""
        if not memories:
            return "CONVERSATION HISTORY:\n(No recent conversations)"

        # Show in chronological order (oldest first)
        chronological = list(reversed(memories))
        lines = []
        for mem in chronological[-5:]:
            user = mem.get('user', '')[:200]
            assistant = mem.get('assistant', '')[:200]
            if user and assistant:
                lines.append(f"Founder: {user}\nYou: {assistant}")

        if not lines:
            return "CONVERSATION HISTORY:\n(No recent conversations)"

        return "CONVERSATION HISTORY:\n" + "\n".join(lines)

    def _format_goals(self, goals: list) -> str:
        if not goals:
            return "- Understand my purpose\n- Learn from the Founder"
        return "\n".join([f"- {g.get('description', str(g))}" for g in goals[:3]])

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
        await self.background.stop()
        await self.redis.close()
        self.pg_conn.close()