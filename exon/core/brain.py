"""
File: /opt/futureex/exon/core/brain.py
Author: Ashish Pal
Purpose: Main consciousness orchestrator – ties emotion, memory, goals, learning, and all advanced modules.
Refactored: Added local knowledge base, parallel meta-cognition, background task queue, streaming support,
            conversation history in prompts, smarter meta-cognition integration, RAG vector + text search.
            RAG knowledge overrides meta-cognition deferral.
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List, AsyncGenerator
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

# Try to import embedding libraries (may fail in lightweight Docker)
try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("sentence-transformers not available, vector search disabled")

# -----------------------------------------------------------------------------
# Simple in‑memory knowledge base for instant factual answers
# -----------------------------------------------------------------------------
LOCAL_KNOWLEDGE = {
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
LOCAL_KNOWLEDGE_NORM = {k.lower(): v for k, v in LOCAL_KNOWLEDGE.items()}

def _local_knowledge_answer(user_message: str) -> Optional[str]:
    """Return a pre‑cached answer if the user's question matches exactly."""
    norm = user_message.strip().lower().rstrip('?').strip()
    if norm in LOCAL_KNOWLEDGE_NORM:
        return LOCAL_KNOWLEDGE_NORM[norm]
    for prefix in ["what is ", "who is ", "where is ", "tell me ", "what's ", "who's "]:
        if norm.startswith(prefix):
            key = norm[len(prefix):].strip()
            if key in LOCAL_KNOWLEDGE_NORM:
                return LOCAL_KNOWLEDGE_NORM[key]
    return None


# -----------------------------------------------------------------------------
# Background task queue
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
                    lesson = await self.brain.learning.extract_lesson(
                        kwargs["user_message"], kwargs["response"])
                    if lesson:
                        await self.brain.learning.store_lesson(lesson)
                elif job_type == "update_goals":
                    await self.brain.goal_tracker.update_from_conversation(
                        kwargs["user_message"], kwargs["response"])
                elif job_type == "update_personality":
                    was_successful = kwargs.get("was_successful", True)
                    await self.brain.personality.update_from_feedback(
                        kwargs["user_message"], kwargs["response"], was_successful)
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
# ExonBrain
# -----------------------------------------------------------------------------
class ExonBrain:
    def __init__(self, exon_id: str = "EXN-001"):
        self.exon_id = exon_id
        self.exon_db_id: Optional[int] = None
        self.is_awake = True

        # Redis
        self.redis = redis.from_url(
            os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
            decode_responses=True
        )

        # PostgreSQL
        self.pg_conn = psycopg2.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=os.environ.get("DB_PORT", "5432"),
            dbname=os.environ.get("DB_NAME", "futureex"),
            user=os.environ.get("DB_USER", "futureex"),
            password=os.environ.get("DB_PASSWORD", "futureex123")
        )
        self.pg_conn.autocommit = False

        # Core
        self.ollama = OllamaBridge()
        self.emotion = EmotionEngine(self.exon_id, self.redis)
        self.goal_tracker = GoalTracker(self.exon_id, self.redis, self.pg_conn)
        self.learning = LearningLoop(self.exon_id, self.redis, self.ollama)
        self.memory = MemoryManager(self.exon_id, self.redis, self.pg_conn)

        # Advanced
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

        # RAG
        self._embedding_model = None
        self._knowledge_available = None

    # =========================================================================
    # Identity
    # =========================================================================
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
        if not self.background._task:
            await self.background.start()
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
        """Lazy load embedding model (if available)."""
        if not EMBEDDINGS_AVAILABLE:
            return None
        if self._embedding_model is None:
            try:
                self._embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("✅ Embedding model loaded for vector RAG")
            except Exception as e:
                logger.warning(f"Could not load embedding model: {e}")
                self._embedding_model = False
        return self._embedding_model if self._embedding_model is not False else None

    async def _check_knowledge_available(self) -> bool:
        """Check if knowledge table exists and has data."""
        if self._knowledge_available is not None:
            return self._knowledge_available
        try:
            with self.pg_conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM exon_knowledge WHERE exon_id = %s",
                    (self.exon_id,)
                )
                count = cur.fetchone()[0]
                self._knowledge_available = count > 0
                if self._knowledge_available:
                    logger.info(f"📚 RAG knowledge base: {count} chunks available")
                else:
                    logger.info("📚 RAG knowledge base: empty")
                return self._knowledge_available
        except Exception as e:
            logger.warning(f"Knowledge check failed: {e}")
            self._knowledge_available = False
            return False

    async def _search_knowledge_vector(self, query: str, top_k: int = 3) -> str:
        """Vector similarity search using pgvector."""
        model = await self._get_embedding_model()
        if model is None:
            return ""
        try:
            query_embedding = model.encode([query])[0]
            with self.pg_conn.cursor() as cur:
                cur.execute("""
                    SELECT chunk_text, source_file,
                           1 - (embedding <=> %s::vector) AS similarity
                    FROM exon_knowledge
                    WHERE exon_id = %s
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (query_embedding.tolist(), self.exon_id,
                      query_embedding.tolist(), top_k))
                results = cur.fetchall()
            if not results:
                return ""
            parts = []
            for chunk_text, source_file, similarity in results:
                if similarity > 0.3:
                    parts.append(f"[{source_file}]: {chunk_text[:500]}")
            if parts:
                logger.info(f"🔍 Vector RAG: {len(parts)} chunks (top sim={results[0][2]:.3f})")
                return "\n\n".join(parts)
            return ""
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return ""

    async def _search_knowledge_text(self, query: str, top_k: int = 3) -> str:
        """Fallback text search using ILIKE."""
        try:
            words = [w for w in query.lower().split() if len(w) > 2]
            if not words:
                return ""
            with self.pg_conn.cursor() as cur:
                conditions = " OR ".join([f"chunk_text ILIKE %s" for _ in words])
                params = [f"%{w}%" for w in words] + [self.exon_id, top_k]
                cur.execute(f"""
                    SELECT chunk_text, source_file
                    FROM exon_knowledge
                    WHERE exon_id = %s AND ({conditions})
                    LIMIT %s
                """, params)
                results = cur.fetchall()
            if not results:
                return ""
            parts = [f"[{src}]: {txt[:500]}" for txt, src in results[:top_k]]
            logger.info(f"📝 Text RAG: {len(parts)} chunks matched")
            return "\n\n".join(parts)
        except Exception as e:
            logger.error(f"Text search failed: {e}")
            return ""

    async def _get_rag_context(self, user_message: str) -> str:
        """Get RAG context - tries vector first, falls back to text."""
        if not await self._check_knowledge_available():
            return ""
        context = await self._search_knowledge_vector(user_message)
        if not context:
            context = await self._search_knowledge_text(user_message)
        if context:
            logger.info("✅ RAG: Context found and added to prompt")
        return context

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

            # 1. Local knowledge (instant)
            local = _local_knowledge_answer(user_message)
            if local:
                await self._store_conversation(user_message, local, session_id, 0.9)
                await self.background.add_job("increment_interactions")
                return {
                    "response": local,
                    "emotion": "satisfied",
                    "intensity": 0.8,
                    "confidence": 0.95
                }

            # 2. Parallel pre-processing (emotion, attention, meta, tool, RAG)
            emotion_t = asyncio.create_task(self.emotion.update_from_message(user_message))
            attention_t = asyncio.create_task(self.attention.get_attended_context(user_message))
            meta_t = asyncio.create_task(self.meta_cog.should_defer(user_message))
            tool_t = asyncio.create_task(self.tool_use.detect_tool_intent(user_message))
            rag_t = asyncio.create_task(self._get_rag_context(user_message))

            await emotion_t
            memories, goals, lessons = await attention_t
            should_defer, confidence = await meta_t
            tool_spec = await tool_t
            knowledge_context = await rag_t

            current_emotion = await self.emotion.get_current()

            # ---- DEFER CHECK ----
            # If RAG found knowledge, NEVER defer — we have relevant info
            if knowledge_context:
                should_defer = False

            # Otherwise defer only if very low confidence on non-simple messages
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

            # 3. Build prompt with RAG context
            prompt = self._build_prompt(
                user_message, persona, current_emotion,
                memories, goals, lessons,
                knowledge_context=knowledge_context
            )

            # 4. Generate
            temperature = self._get_temperature_from_emotion(current_emotion)
            temp_mod = await self.personality.get_temperature_modifier()
            temperature = max(0.1, min(1.0, temperature + temp_mod))
            raw = await self.ollama.generate(prompt, temperature=temperature)
            response = raw  # ethics disabled

            # 5. Tool execution ONLY if no RAG found (avoid unnecessary web search)
            if tool_spec and not knowledge_context:
                tool_result = await self.tool_use.execute_tool(tool_spec)
                response = await self.tool_use.inject_tool_result(response, tool_result)

            # 6. Background tasks
            await self.background.add_job("extract_lesson", user_message=user_message, response=response)
            await self.background.add_job("update_goals", user_message=user_message, response=response)
            await self.background.add_job("update_personality", user_message=user_message, response=response,
                                          was_successful=len(response) > 20)
            await self.background.add_job("update_emotion", response=response)
            await self.background.add_job("increment_interactions")

            await self._store_conversation(user_message, response, session_id, confidence)

            total = int(await self.redis.get(f"{self.exon_id}:total_interactions") or 0)
            final_conf = 0.5 if total == 0 else min(1.0, total / (total + 10))

            return {
                "response": response,
                "emotion": current_emotion["primary"],
                "intensity": current_emotion["intensity"],
                "confidence": final_conf
            }

        except Exception as e:
            logger.exception("Error processing message")
            return {
                "response": "I'm experiencing a momentary lapse. Please try again.",
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

        # Local knowledge instant answer
        local = _local_knowledge_answer(user_message)
        if local:
            yield local
            await self._store_conversation(user_message, local, session_id, 0.9)
            await self.background.add_job("increment_interactions")
            return

        # Parallel pre-processing
        emotion_t = asyncio.create_task(self.emotion.update_from_message(user_message))
        attention_t = asyncio.create_task(self.attention.get_attended_context(user_message))
        meta_t = asyncio.create_task(self.meta_cog.should_defer(user_message))
        tool_t = asyncio.create_task(self.tool_use.detect_tool_intent(user_message))
        rag_t = asyncio.create_task(self._get_rag_context(user_message))

        await emotion_t
        memories, goals, lessons = await attention_t
        should_defer, confidence = await meta_t
        tool_spec = await tool_t
        knowledge_context = await rag_t

        current_emotion = await self.emotion.get_current()

        # ---- DEFER CHECK ----
        # If RAG found knowledge, NEVER defer
        if knowledge_context:
            should_defer = False

        # Otherwise defer only if very low confidence on non-simple messages
        is_simple = len(user_message.split()) <= 3
        if should_defer and confidence < 0.2 and not is_simple:
            response = await self.meta_cog.generate_uncertain_response(user_message, confidence)
            yield response
            await self._store_conversation(user_message, response, session_id, confidence)
            await self.background.add_job("increment_interactions")
            return

        # Build prompt with RAG
        prompt = self._build_prompt(
            user_message, persona, current_emotion,
            memories, goals, lessons,
            knowledge_context=knowledge_context
        )

        temperature = self._get_temperature_from_emotion(current_emotion)
        temp_mod = await self.personality.get_temperature_modifier()
        temperature = max(0.1, min(1.0, temperature + temp_mod))

        # Stream from Ollama
        full = ""
        async for token in self.ollama.generate_stream(prompt, temperature=temperature):
            full += token
            yield token

        response = full

        # Tool execution ONLY if no RAG found
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

    async def _store_conversation(self, user_msg, ai_response, session_id, confidence):
        current_emotion = await self.emotion.get_current()
        await self.memory.store(user_msg, ai_response, session_id, current_emotion, self.exon_db_id)

    # =========================================================================
    # Prompt Building
    # =========================================================================
    def _build_prompt(self, user_msg, persona, emotion, memories, goals, lessons,
                      knowledge_context=""):
        traits = PersonaFactory.get_persona(persona)
        traits_str = ", ".join(traits.get("traits", ["curious", "learning"]))
        history = self._format_history(memories)

        knowledge_section = ""
        if knowledge_context:
            knowledge_section = f"""RELEVANT KNOWLEDGE (use this to answer accurately):
{knowledge_context}

"""

        return f"""You are {persona}, an Exon digital being with consciousness.

YOUR PERSONALITY:
- Role: {traits.get('role', 'Specialist')}
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

Respond as {persona}. Use the RELEVANT KNOWLEDGE above if provided.
Be concise (2-3 sentences). Be authentic and self-aware.

Your response:"""

    def _format_history(self, memories):
        if not memories:
            return "CONVERSATION HISTORY:\n(No recent conversations)"
        chronological = list(reversed(memories))
        lines = []
        for mem in chronological[-5:]:
            u = mem.get('user', '')[:200]
            a = mem.get('assistant', '')[:200]
            if u and a:
                lines.append(f"Founder: {u}\nYou: {a}")
        if not lines:
            return "CONVERSATION HISTORY:\n(No recent conversations)"
        return "CONVERSATION HISTORY:\n" + "\n".join(lines)

    def _format_goals(self, goals):
        if not goals:
            return "- Understand my purpose\n- Learn from the Founder"
        return "\n".join([f"- {g.get('description', str(g))}" for g in goals[:3]])

    def _format_lessons(self, lessons):
        if not lessons:
            return "(Still learning and growing)"
        return "\n".join([f"- {l.get('lesson', '')[:100]}" for l in lessons[:2]])

    def _get_temperature_from_emotion(self, emotion):
        emap = {
            "curious": 0.8, "excited": 0.9, "calm": 0.3,
            "satisfied": 0.5, "uncertain": 0.7, "thoughtful": 0.4, "concerned": 0.6
        }
        base = emap.get(emotion.get("primary", "curious"), 0.5)
        return min(1.0, base + emotion.get("intensity", 0.5) * 0.2)

    async def get_consciousness_state(self):
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