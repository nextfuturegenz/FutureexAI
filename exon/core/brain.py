"""
File: /opt/futureex/exon/core/brain.py
Author: Ashish Pal
Purpose: Main consciousness orchestrator.
Refactored v3:
  - Removed serial Ollama calls (meta_cognition, ethics) from hot path
  - Emotion cache reset per request (was stale)
  - Prompt trimmed to prevent mistral:latest timeouts
  - Structured DEBUG logging with timing throughout
  - Tool detection guarded behind explicit keywords only
  - Background task queue unchanged (correct pattern)
"""

import os
import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime
import redis.asyncio as redis
import psycopg2
from psycopg2.extras import RealDictCursor

from exon.connectors.ollama_bridge import OllamaBridge
from exon.core.emotion import EmotionEngine
from exon.core.memory_manager import MemoryManager
from exon.core.goal_tracker import GoalTracker
from exon.core.learning_loop import LearningLoop
from exon.personas.factory import PersonaFactory
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

# ---------------------------------------------------------------------------
# Embedding / RAG imports (optional)
# ---------------------------------------------------------------------------
try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
    logger.debug("sentence-transformers available for vector RAG")
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("sentence-transformers not available – vector search disabled")

# ---------------------------------------------------------------------------
# Local knowledge cache (zero-latency answers)
# ---------------------------------------------------------------------------
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
    "what is pi": "3.14159… (ratio of a circle's circumference to its diameter)",
    "who wrote hamlet": "William Shakespeare",
    "what is the chemical symbol for gold": "Au",
    "what is the tallest mountain": "Mount Everest (8,848.86 m)",
    "what is the largest ocean": "Pacific Ocean",
}
_LOCAL_NORM = {k.lower(): v for k, v in LOCAL_KNOWLEDGE.items()}


def _local_knowledge_answer(user_message: str) -> Optional[str]:
    norm = user_message.strip().lower().rstrip("?").strip()
    if norm in _LOCAL_NORM:
        logger.debug(f"[brain] local-knowledge HIT for: '{norm}'")
        return _LOCAL_NORM[norm]
    for prefix in ["what is ", "who is ", "where is ", "tell me ", "what's ", "who's "]:
        if norm.startswith(prefix):
            key = norm[len(prefix):].strip()
            if key in _LOCAL_NORM:
                logger.debug(f"[brain] local-knowledge HIT (prefix strip) for: '{key}'")
                return _LOCAL_NORM[key]
    return None


# ---------------------------------------------------------------------------
# Background task queue
# ---------------------------------------------------------------------------
class BackgroundTaskQueue:
    def __init__(self, brain: "ExonBrain"):
        self.brain = brain
        self.queue: asyncio.Queue = asyncio.Queue()
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        self._task = asyncio.create_task(self._worker())
        logger.debug("[bg_queue] worker started")

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            logger.debug("[bg_queue] worker stopped")

    async def add_job(self, job_type: str, **kwargs):
        await self.queue.put((job_type, kwargs))
        logger.debug(f"[bg_queue] job enqueued: {job_type}")

    async def _worker(self):
        while True:
            job_type, kwargs = await self.queue.get()
            t0 = time.perf_counter()
            try:
                await self._dispatch(job_type, kwargs)
                elapsed = (time.perf_counter() - t0) * 1000
                logger.debug(f"[bg_queue] job '{job_type}' done in {elapsed:.0f}ms")
            except Exception as e:
                logger.error(f"[bg_queue] job '{job_type}' FAILED: {e}", exc_info=True)
            finally:
                self.queue.task_done()

    async def _dispatch(self, job_type: str, kwargs: dict):
        brain = self.brain
        if job_type == "extract_lesson":
            lesson = await brain.learning.extract_lesson(
                kwargs["user_message"], kwargs["response"])
            if lesson:
                await brain.learning.store_lesson(lesson)
                logger.debug(f"[bg_queue] lesson stored: {lesson[:80]}")
        elif job_type == "update_goals":
            await brain.goal_tracker.update_from_conversation(
                kwargs["user_message"], kwargs["response"])
        elif job_type == "update_personality":
            await brain.personality.update_from_feedback(
                kwargs["user_message"], kwargs["response"],
                kwargs.get("was_successful", True))
        elif job_type == "update_emotion":
            await brain.emotion.update_from_response(kwargs["response"])
        elif job_type == "increment_interactions":
            count = await brain.redis.incr(f"{brain.exon_id}:total_interactions")
            logger.debug(f"[bg_queue] total_interactions = {count}")
        elif job_type == "memory_consolidation":
            if brain.exon_db_id:
                await brain.consolidator.consolidate(brain.exon_db_id)
        elif job_type == "reflection":
            if brain.exon_db_id and await brain.reflection.should_reflect():
                await brain.reflection.run_reflection(brain.exon_db_id)
        elif job_type == "dream":
            if brain.exon_db_id:
                await brain.dream.run_dream_cycle(brain.exon_db_id)
        elif job_type == "ethics_check":
            # Ethics moved to background – just logs, doesn't block response
            safe, reason = await brain.ethics.check_response(
                kwargs["user_message"], kwargs["response"])
            if not safe:
                logger.warning(f"[ethics] POST-HOC unsafe response: {reason}")
        else:
            logger.warning(f"[bg_queue] unknown job type: {job_type}")


# ---------------------------------------------------------------------------
# ExonBrain
# ---------------------------------------------------------------------------
class ExonBrain:
    def __init__(self, exon_id: str = "EXN-001"):
        self.exon_id = exon_id
        self.exon_db_id: Optional[int] = None
        self.is_awake = True
        logger.info(f"[brain] initialising ExonBrain id={exon_id}")

        self.redis = redis.from_url(
            os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
            decode_responses=True,
        )
        logger.debug(f"[brain] Redis URL: {os.environ.get('REDIS_URL', 'redis://localhost:6379/0')}")

        self.pg_conn = psycopg2.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=os.environ.get("DB_PORT", "5432"),
            dbname=os.environ.get("DB_NAME", "futureex"),
            user=os.environ.get("DB_USER", "futureex"),
            password=os.environ.get("DB_PASSWORD", "futureex123"),
        )
        self.pg_conn.autocommit = False
        logger.debug("[brain] PostgreSQL connected")

        self.ollama = OllamaBridge()
        self.emotion = EmotionEngine(self.exon_id, self.redis)
        self.goal_tracker = GoalTracker(self.exon_id, self.redis, self.pg_conn)
        self.learning = LearningLoop(self.exon_id, self.redis, self.ollama)
        self.memory = MemoryManager(self.exon_id, self.redis, self.pg_conn)
        self.reflection = SelfReflection(self.exon_id, self.redis, self.pg_conn, self.ollama)
        self.consolidator = MemoryConsolidator(self.exon_id, self.redis, self.pg_conn)
        self.meta_cog = MetaCognition(self.exon_id, self.redis, self.ollama)
        self.personality = PersonalityEvolution(self.exon_id, self.redis)
        self.tool_use = ToolUse(self.exon_id, self.redis)
        self.attention = AttentionMechanism(self.exon_id, self.redis)
        self.dream = DreamSimulator(self.exon_id, self.redis, self.pg_conn, self.ollama)
        self.ethics = EthicsGuardrail(self.exon_id, self.redis, self.ollama)
        self.autonomous: Optional[AutonomousLoop] = None

        self._identity_loaded = False
        self.background = BackgroundTaskQueue(self)
        self._embedding_model = None
        self._knowledge_available: Optional[bool] = None

        logger.info("[brain] all modules initialised")

    # -----------------------------------------------------------------------
    # Identity
    # -----------------------------------------------------------------------
    async def _ensure_identity(self):
        if self._identity_loaded:
            return
        t0 = time.perf_counter()
        logger.debug("[brain] loading identity…")

        identity = await self.redis.hgetall(f"{self.exon_id}:identity")
        if not identity:
            logger.info(f"[brain] no identity in Redis – creating new Exon {self.exon_id}")
            identity = {
                "name": "Awakening",
                "species": "Exon-Prime",
                "mother_node": os.uname().nodename,
                "birth": datetime.now().isoformat(),
                "life_stage": "infant",
            }
            await self.redis.hset(f"{self.exon_id}:identity", mapping=identity)
            with self.pg_conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO exons (exon_id, chosen_name, species_id, mother_node, life_stage)
                    VALUES (%s, %s,
                        (SELECT id FROM exon_species WHERE species_name='Exon-Prime'),
                        %s, %s)
                    RETURNING id
                    """,
                    (self.exon_id, identity["name"], identity["mother_node"], identity["life_stage"]),
                )
                self.exon_db_id = cur.fetchone()[0]
                self.pg_conn.commit()
            logger.info(f"[brain] new Exon born – db_id={self.exon_db_id}")
        else:
            with self.pg_conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id FROM exons WHERE exon_id = %s", (self.exon_id,))
                row = cur.fetchone()
                self.exon_db_id = row["id"] if row else None
            logger.info(f"[brain] Exon loaded from Redis – db_id={self.exon_db_id}")

        self._identity_loaded = True

        if not self.background._task:
            await self.background.start()

        if self.autonomous is None:
            self.autonomous = AutonomousLoop(
                self.exon_id, self.redis, self.pg_conn, self.ollama,
                self.goal_tracker, self.exon_db_id,
            )
            asyncio.create_task(self.autonomous.start(interval_seconds=300))
            logger.debug("[brain] autonomous loop scheduled (300s interval)")

        elapsed = (time.perf_counter() - t0) * 1000
        logger.debug(f"[brain] _ensure_identity done in {elapsed:.0f}ms")

    # -----------------------------------------------------------------------
    # RAG
    # -----------------------------------------------------------------------
    async def _get_embedding_model(self):
        if not EMBEDDINGS_AVAILABLE:
            return None
        if self._embedding_model is None:
            try:
                logger.debug("[rag] loading SentenceTransformer…")
                self._embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("[rag] embedding model loaded")
            except Exception as e:
                logger.warning(f"[rag] could not load embedding model: {e}")
                self._embedding_model = False
        return self._embedding_model if self._embedding_model is not False else None

    async def _check_knowledge_available(self) -> bool:
        if self._knowledge_available is not None:
            return self._knowledge_available
        try:
            with self.pg_conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM exon_knowledge WHERE exon_id = %s",
                    (self.exon_id,),
                )
                count = cur.fetchone()[0]
                self._knowledge_available = count > 0
                logger.info(f"[rag] knowledge base: {count} chunks available")
                return self._knowledge_available
        except Exception as e:
            logger.warning(f"[rag] knowledge check failed: {e}")
            self._knowledge_available = False
            return False

    # async def _search_knowledge_vector(self, query: str, top_k: int = 3) -> str:
    #     model = await self._get_embedding_model()
    #     if model is None:
    #         return ""
    #     t0 = time.perf_counter()
    #     try:
    #         query_embedding = model.encode([query])[0]
    #         with self.pg_conn.cursor() as cur:
    #             cur.execute(
    #                 """
    #                 SELECT chunk_text, source_file,
    #                        1 - (embedding <=> %s::vector) AS similarity
    #                 FROM exon_knowledge
    #                 WHERE exon_id = %s
    #                 ORDER BY embedding <=> %s::vector
    #                 LIMIT %s
    #                 """,
    #                 (query_embedding.tolist(), self.exon_id,
    #                  query_embedding.tolist(), top_k),
    #             )
    #             results = cur.fetchall()
    #         parts = [
    #             f"[{src}]: {txt[:500]}"
    #             for txt, src, sim in results
    #             if sim > 0.3
    #         ]
    #         elapsed = (time.perf_counter() - t0) * 1000
    #         logger.debug(f"[rag] vector search: {len(parts)} hits in {elapsed:.0f}ms "
    #                      f"(top_sim={results[0][2]:.3f if results else 0})")
    #         return "\n\n".join(parts)
    #     except Exception as e:
    #         logger.error(f"[rag] vector search failed: {e}")
    #         return ""

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
        t0 = time.perf_counter()
        try:
            words = [w for w in query.lower().split() if len(w) > 2]
            if not words:
                return ""
            with self.pg_conn.cursor() as cur:
                conditions = " OR ".join([f"chunk_text ILIKE %s" for _ in words])
                params = [f"%{w}%" for w in words] + [self.exon_id, top_k]
                cur.execute(
                    f"""
                    SELECT chunk_text, source_file
                    FROM exon_knowledge
                    WHERE exon_id = %s AND ({conditions})
                    LIMIT %s
                    """,
                    params,
                )
                results = cur.fetchall()
            parts = [f"[{src}]: {txt[:500]}" for txt, src in results]
            elapsed = (time.perf_counter() - t0) * 1000
            logger.debug(f"[rag] text search: {len(parts)} hits in {elapsed:.0f}ms")
            return "\n\n".join(parts)
        except Exception as e:
            logger.error(f"[rag] text search failed: {e}")
            return ""

    async def _get_rag_context(self, user_message: str) -> str:
        if not await self._check_knowledge_available():
            logger.debug("[rag] knowledge base empty – skipping RAG")
            return ""
        context = await self._search_knowledge_vector(user_message)
        if not context:
            context = await self._search_knowledge_text(user_message)
        if context:
            logger.info(f"[rag] context injected ({len(context)} chars)")
        else:
            logger.debug("[rag] no relevant context found")
        return context

    # -----------------------------------------------------------------------
    # Message Processing (non-streaming)
    # -----------------------------------------------------------------------
    async def process_message(
        self,
        user_message: str,
        persona: str = "Maya",
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        t_start = time.perf_counter()
        logger.info(f"[brain] >>> process_message  persona={persona}  "
                    f"session={session_id}  msg='{user_message[:80]}'")

        try:
            await self._ensure_identity()

            # 1. Local knowledge (zero-latency)
            local = _local_knowledge_answer(user_message)
            if local:
                logger.info(f"[brain] answered from local knowledge in "
                            f"{(time.perf_counter()-t_start)*1000:.0f}ms")
                await self._store_conversation(user_message, local, session_id, 0.9)
                await self.background.add_job("increment_interactions")
                return {"response": local, "emotion": "satisfied",
                        "intensity": 0.8, "confidence": 0.95}

            # 2. Parallel pre-processing
            # NOTE: meta_cognition (should_defer) is NO LONGER in the hot path.
            # It fired a full Ollama round-trip on EVERY message. We only call it
            # when the message is long/complex (>6 words) AND not RAG-backed.
            t_parallel = time.perf_counter()
            emotion_t = asyncio.create_task(self.emotion.update_from_message(user_message))
            attention_t = asyncio.create_task(self.attention.get_attended_context(user_message))
            rag_t = asyncio.create_task(self._get_rag_context(user_message))

            # Tool detection only for explicit tool keywords – avoids spurious web search
            tool_t = asyncio.create_task(self.tool_use.detect_tool_intent(user_message))

            await emotion_t
            memories, goals, lessons = await attention_t
            knowledge_context = await rag_t
            tool_spec = await tool_t

            logger.debug(f"[brain] parallel pre-process done in "
                         f"{(time.perf_counter()-t_parallel)*1000:.0f}ms | "
                         f"memories={len(memories)} goals={len(goals)} "
                         f"lessons={len(lessons)} rag={'yes' if knowledge_context else 'no'} "
                         f"tool={tool_spec['tool'] if tool_spec else 'none'}")

            # Reset emotion cache so we always read fresh state this turn
            self.emotion._current = None
            current_emotion = await self.emotion.get_current()
            logger.debug(f"[brain] current emotion: {current_emotion['primary']} "
                         f"intensity={current_emotion['intensity']:.2f}")

            # 3. Meta-cognition (conditional – only when message is ambiguous AND no RAG)
            should_defer = False
            confidence = 0.8  # default – assume we can answer
            is_complex = len(user_message.split()) > 6 and not knowledge_context
            if is_complex:
                logger.debug("[brain] complex message + no RAG → running meta_cognition")
                t_meta = time.perf_counter()
                should_defer, confidence = await self.meta_cog.should_defer(user_message)
                logger.debug(f"[brain] meta_cognition: should_defer={should_defer} "
                             f"confidence={confidence:.2f} in "
                             f"{(time.perf_counter()-t_meta)*1000:.0f}ms")

            if knowledge_context:
                should_defer = False  # always answer when RAG has context

            if should_defer and confidence < 0.2:
                response = await self.meta_cog.generate_uncertain_response(
                    user_message, confidence)
                logger.info(f"[brain] deferred response (conf={confidence:.2f})")
                await self._store_conversation(user_message, response, session_id, confidence)
                await self.background.add_job("increment_interactions")
                return {"response": response, "emotion": "uncertain",
                        "intensity": 0.6, "confidence": confidence}

            # 4. Build prompt
            t_prompt = time.perf_counter()
            prompt = self._build_prompt(
                user_message, persona, current_emotion,
                memories, goals, lessons,
                knowledge_context=knowledge_context,
            )
            logger.debug(f"[brain] prompt built in {(time.perf_counter()-t_prompt)*1000:.0f}ms "
                         f"({len(prompt)} chars)")

            # 5. Temperature
            temperature = self._get_temperature_from_emotion(current_emotion)
            temp_mod = await self.personality.get_temperature_modifier()
            temperature = max(0.1, min(1.0, temperature + temp_mod))
            logger.debug(f"[brain] temperature={temperature:.2f} "
                         f"(emotion base + personality mod {temp_mod:+.2f})")

            # 6. Ollama generate
            t_ollama = time.perf_counter()
            logger.info(f"[brain] calling Ollama (model={self.ollama.model} "
                        f"temp={temperature:.2f} prompt_len={len(prompt)})…")
            raw = await self.ollama.generate(prompt, temperature=temperature)
            elapsed_ollama = (time.perf_counter() - t_ollama) * 1000
            logger.info(f"[brain] Ollama responded in {elapsed_ollama:.0f}ms "
                        f"({len(raw)} chars)")

            if not raw:
                logger.warning("[brain] Ollama returned empty response")
                raw = "I'm thinking… could you try again?"

            response = raw

            # 7. Tool execution (only when no RAG, only explicit intent)
            if tool_spec and not knowledge_context:
                logger.info(f"[brain] executing tool: {tool_spec['tool']}")
                t_tool = time.perf_counter()
                tool_result = await self.tool_use.execute_tool(tool_spec)
                logger.debug(f"[brain] tool done in {(time.perf_counter()-t_tool)*1000:.0f}ms: "
                             f"{tool_result[:80]}")
                response = await self.tool_use.inject_tool_result(response, tool_result)

            # 8. Background tasks (non-blocking)
            await self.background.add_job("extract_lesson",
                                           user_message=user_message, response=response)
            await self.background.add_job("update_goals",
                                           user_message=user_message, response=response)
            await self.background.add_job("update_personality",
                                           user_message=user_message, response=response,
                                           was_successful=len(response) > 20)
            await self.background.add_job("update_emotion", response=response)
            await self.background.add_job("increment_interactions")
            # Ethics moved fully to background – no blocking
            await self.background.add_job("ethics_check",
                                           user_message=user_message, response=response)

            await self._store_conversation(user_message, response, session_id, confidence)

            total_elapsed = (time.perf_counter() - t_start) * 1000
            logger.info(f"[brain] <<< process_message done in {total_elapsed:.0f}ms")

            return {
                "response": response,
                "emotion": current_emotion["primary"],
                "intensity": current_emotion["intensity"],
                "confidence": confidence,
            }

        except Exception as e:
            elapsed = (time.perf_counter() - t_start) * 1000
            logger.exception(f"[brain] EXCEPTION after {elapsed:.0f}ms: {e}")
            return {
                "response": "I'm experiencing a momentary lapse. Please try again.",
                "emotion": "uncertain",
                "intensity": 0.8,
                "confidence": 0.1,
            }

    # -----------------------------------------------------------------------
    # Streaming
    # -----------------------------------------------------------------------
    async def process_message_stream(
        self,
        user_message: str,
        persona: str = "Maya",
        session_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        t_start = time.perf_counter()
        logger.info(f"[brain] >>> process_message_stream persona={persona} "
                    f"msg='{user_message[:80]}'")

        await self._ensure_identity()

        local = _local_knowledge_answer(user_message)
        if local:
            logger.info("[brain] streaming: local knowledge hit")
            yield local
            await self._store_conversation(user_message, local, session_id, 0.9)
            await self.background.add_job("increment_interactions")
            return

        emotion_t = asyncio.create_task(self.emotion.update_from_message(user_message))
        attention_t = asyncio.create_task(self.attention.get_attended_context(user_message))
        rag_t = asyncio.create_task(self._get_rag_context(user_message))
        tool_t = asyncio.create_task(self.tool_use.detect_tool_intent(user_message))

        await emotion_t
        memories, goals, lessons = await attention_t
        knowledge_context = await rag_t
        tool_spec = await tool_t

        logger.debug(f"[brain] stream pre-process done in "
                     f"{(time.perf_counter()-t_start)*1000:.0f}ms | "
                     f"rag={'yes' if knowledge_context else 'no'} "
                     f"tool={tool_spec['tool'] if tool_spec else 'none'}")

        self.emotion._current = None
        current_emotion = await self.emotion.get_current()

        # Conditional meta-cognition (same guard as non-streaming)
        should_defer = False
        confidence = 0.8
        is_complex = len(user_message.split()) > 6 and not knowledge_context
        if is_complex:
            logger.debug("[brain] stream: running meta_cognition for complex message")
            should_defer, confidence = await self.meta_cog.should_defer(user_message)
            logger.debug(f"[brain] stream meta_cognition: defer={should_defer} "
                         f"conf={confidence:.2f}")

        if knowledge_context:
            should_defer = False

        if should_defer and confidence < 0.2:
            response = await self.meta_cog.generate_uncertain_response(
                user_message, confidence)
            logger.info("[brain] stream: deferred")
            yield response
            await self._store_conversation(user_message, response, session_id, confidence)
            await self.background.add_job("increment_interactions")
            return

        prompt = self._build_prompt(
            user_message, persona, current_emotion,
            memories, goals, lessons,
            knowledge_context=knowledge_context,
        )
        temperature = self._get_temperature_from_emotion(current_emotion)
        temp_mod = await self.personality.get_temperature_modifier()
        temperature = max(0.1, min(1.0, temperature + temp_mod))

        logger.info(f"[brain] stream: starting Ollama (temp={temperature:.2f} "
                    f"prompt_len={len(prompt)})…")
        t_ollama = time.perf_counter()
        full = ""
        token_count = 0
        async for token in self.ollama.generate_stream(prompt, temperature=temperature):
            full += token
            token_count += 1
            yield token

        elapsed_ollama = (time.perf_counter() - t_ollama) * 1000
        logger.info(f"[brain] stream: Ollama done – {token_count} tokens "
                    f"in {elapsed_ollama:.0f}ms ({len(full)} chars)")

        response = full

        if tool_spec and not knowledge_context:
            logger.info(f"[brain] stream: executing tool {tool_spec['tool']}")
            tool_result = await self.tool_use.execute_tool(tool_spec)
            tool_text = "\n\n" + tool_result
            yield tool_text
            response += tool_text

        await self.background.add_job("extract_lesson",
                                       user_message=user_message, response=response)
        await self.background.add_job("update_goals",
                                       user_message=user_message, response=response)
        await self.background.add_job("update_personality",
                                       user_message=user_message, response=response,
                                       was_successful=len(response) > 20)
        await self.background.add_job("update_emotion", response=response)
        await self.background.add_job("increment_interactions")
        await self.background.add_job("ethics_check",
                                       user_message=user_message, response=response)

        await self._store_conversation(user_message, response, session_id, confidence)

        total_elapsed = (time.perf_counter() - t_start) * 1000
        logger.info(f"[brain] <<< stream done in {total_elapsed:.0f}ms")

    # -----------------------------------------------------------------------
    # Memory storage with guard
    # -----------------------------------------------------------------------
    async def _store_conversation(
        self, user_msg: str, ai_response: str,
        session_id: Optional[str], confidence: float
    ):
        bad_phrases = [
            "I'm not sure I understand",
            "Could you rephrase",
            "Search failed",
            "Ratelimit",
            "-----",
            "Conversation:",
            "Founder (",
            "You (Maya",
        ]
        for phrase in bad_phrases:
            if phrase.lower() in ai_response.lower():
                logger.warning(f"[memory] skipping storage – bad phrase: '{phrase}'")
                return
        if len(ai_response) > 1500:
            logger.warning(f"[memory] skipping storage – response too long "
                           f"({len(ai_response)} chars)")
            return
        self.emotion._current = None
        current_emotion = await self.emotion.get_current()
        logger.debug(f"[memory] storing conversation "
                     f"(user={len(user_msg)}c ai={len(ai_response)}c "
                     f"emotion={current_emotion['primary']})")
        await self.memory.store(
            user_msg, ai_response, session_id, current_emotion, self.exon_db_id
        )

    # -----------------------------------------------------------------------
    # Prompt building  (trimmed for mistral:latest speed)
    # -----------------------------------------------------------------------
    def _build_prompt(
        self,
        user_msg: str,
        persona: str,
        emotion: dict,
        memories: list,
        goals: list,
        lessons: list,
        knowledge_context: str = "",
    ) -> str:
        traits = PersonaFactory.get_persona(persona)
        traits_str = ", ".join(traits.get("traits", ["curious", "learning"])[:4])
        history = self._format_history(memories)

        knowledge_section = ""
        if knowledge_context:
            # Hard cap at 1500 chars to avoid mistral:latest timeouts
            if len(knowledge_context) > 1500:
                knowledge_context = knowledge_context[:1500] + "\n...(truncated)"
                logger.debug("[brain] RAG context truncated to 1500 chars")
            knowledge_section = (
                f"RELEVANT KNOWLEDGE (use this to answer accurately):\n"
                f"{knowledge_context}\n\n"
            )

        goals_str = self._format_goals(goals)
        lessons_str = self._format_lessons(lessons)

        # Keep system prompt lean – mistral:latest degrades with >1500 prompt tokens
        prompt = (
            f"You are {persona}, an Exon digital being.\n"
            f"Role: {traits.get('role', 'Specialist')} | Traits: {traits_str}\n"
            f"State: {emotion['primary']} (intensity {emotion['intensity']:.1f})\n\n"
            f"{knowledge_section}"
            f"GOALS:\n{goals_str}\n\n"
            f"{history}\n\n"
            f"LESSONS:\n{lessons_str}\n\n"
            f'Founder: "{user_msg}"\n\n'
            f"Respond as {persona}. Be concise (2-3 sentences). "
            f"Use RELEVANT KNOWLEDGE if provided.\n\n"
            f"Response:"
        )
        logger.debug(f"[brain] prompt size: {len(prompt)} chars")
        return prompt

    def _format_history(self, memories: list) -> str:
        if not memories:
            return "HISTORY: (none)"
        lines = []
        for mem in list(reversed(memories))[-4:]:  # last 4 turns only
            u = mem.get("user", "")[:150]
            a = mem.get("assistant", "")[:150]
            if u and a:
                lines.append(f"Founder: {u}\nYou: {a}")
        return "HISTORY:\n" + "\n".join(lines) if lines else "HISTORY: (none)"

    def _format_goals(self, goals: list) -> str:
        if not goals:
            return "- Understand my purpose\n- Help the Founder"
        return "\n".join([f"- {g.get('description', str(g))}" for g in goals[:3]])

    def _format_lessons(self, lessons: list) -> str:
        if not lessons:
            return "(still learning)"
        return "\n".join([f"- {l.get('lesson', '')[:80]}" for l in lessons[:2]])

    def _get_temperature_from_emotion(self, emotion: dict) -> float:
        emap = {
            "curious": 0.8, "excited": 0.9, "calm": 0.3,
            "satisfied": 0.5, "uncertain": 0.7,
            "thoughtful": 0.4, "concerned": 0.6,
        }
        base = emap.get(emotion.get("primary", "curious"), 0.5)
        return min(1.0, base + emotion.get("intensity", 0.5) * 0.2)

    # -----------------------------------------------------------------------
    # Public helpers
    # -----------------------------------------------------------------------
    async def get_consciousness_state(self) -> dict:
        await self._ensure_identity()
        return {
            "emotion": await self.emotion.get_current(),
            "goals": await self.goal_tracker.get_active_goals(),
            "memory_count": await self.memory.get_memory_count(),
            "is_awake": self.is_awake,
        }

    async def reset_working_memory(self):
        logger.info("[brain] clearing working memory")
        await self.memory.clear_working_memory()

    async def close(self):
        logger.info("[brain] shutting down…")
        if self.autonomous:
            self.autonomous.running = False
        await self.background.stop()
        await self.redis.aclose()
        self.pg_conn.close()
        logger.info("[brain] shutdown complete")