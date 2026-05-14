"""
File: /opt/futureex/exon/api/app.py
Author: Ashish Pal
Purpose: FastAPI server for Exon Consciousness System.
Refactored v3:
  - LOG_LEVEL env var controls verbosity (set LOG_LEVEL=DEBUG for full traces)
  - Startup logs each step with timing
  - Request middleware logs every request/response with latency
"""

import logging
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from exon.core.brain import ExonBrain
from exon.api.routes import chat, status, ws
from exon.api.ui.serve_ui import serve_ui

# ---------------------------------------------------------------------------
# Logging setup
# Set LOG_LEVEL=DEBUG in your .env to see all internal traces.
# Default is INFO.
# ---------------------------------------------------------------------------
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)
logger.info(f"[app] logging level: {LOG_LEVEL}")

app = FastAPI(title="Exon Consciousness API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request timing middleware
# ---------------------------------------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    t0 = time.perf_counter()
    logger.debug(f"[http] → {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        elapsed = (time.perf_counter() - t0) * 1000
        logger.info(f"[http] ← {request.method} {request.url.path} "
                    f"status={response.status_code} {elapsed:.0f}ms")
        return response
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        logger.error(f"[http] ✗ {request.method} {request.url.path} "
                     f"ERROR after {elapsed:.0f}ms: {e}")
        raise

# ---------------------------------------------------------------------------
# Brain initialisation
# ---------------------------------------------------------------------------
logger.info("[app] creating ExonBrain…")
exon_brain = ExonBrain(exon_id="EXN-001")

chat.init(exon_brain)
status.init(exon_brain)
ws.init(exon_brain)

# Static UI
ui_dir = os.path.join(os.path.dirname(__file__), "ui")
app.mount("/ui/static", StaticFiles(directory=ui_dir), name="ui_static")

app.include_router(chat.router)
app.include_router(status.router)
app.include_router(ws.router)


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    t0 = time.perf_counter()
    logger.info("[app] startup: ensuring identity…")
    await exon_brain._ensure_identity()

    if exon_brain.background._task is None:
        await exon_brain.background.start()

    # Auto-ingest knowledge
    knowledge_dir = os.environ.get(
        "KNOWLEDGE_DIR",
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "knowledge",
        ),
    )
    if os.path.exists(knowledge_dir):
        logger.info(f"[app] ingesting knowledge from {knowledge_dir}…")
        try:
            from exon.scripts.ingest_knowledge import ingest_knowledge
            await ingest_knowledge(knowledge_dir, clear_first=False,
                                   exon_id=exon_brain.exon_id)
            logger.info("[app] knowledge ingestion complete")
        except Exception as e:
            logger.warning(f"[app] knowledge ingestion skipped: {e}")
    else:
        logger.info(f"[app] no knowledge directory at {knowledge_dir}")

    ollama_ok = await exon_brain.ollama.health_check()
    if ollama_ok:
        logger.info(f"[app] Ollama reachable at {exon_brain.ollama.ollama_host} "
                    f"model={exon_brain.ollama.model}")
    else:
        logger.warning(f"[app] Ollama NOT reachable at {exon_brain.ollama.ollama_host} – "
                       f"responses will fail until Ollama is running")

    elapsed = (time.perf_counter() - t0) * 1000
    logger.info(f"[app] startup complete in {elapsed:.0f}ms")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("[app] shutdown: closing brain…")
    await exon_brain.close()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
async def root():
    return {
        "status": "online",
        "exon_id": exon_brain.exon_id,
        "species": "Exon-Prime",
        "version": "3.0.0",
        "ollama_model": exon_brain.ollama.model,
    }


@app.get("/ui", response_class=HTMLResponse)
async def chat_ui():
    return await serve_ui()


@app.get("/debug")
async def debug_state():
    """Quick endpoint to dump internal state for debugging."""
    state = await exon_brain.get_consciousness_state()
    identity = await exon_brain.redis.hgetall(f"{exon_brain.exon_id}:identity")
    total = await exon_brain.redis.get(f"{exon_brain.exon_id}:total_interactions") or "0"
    bg_queue_size = exon_brain.background.queue.qsize()
    return {
        "identity": identity,
        "state": state,
        "total_interactions": int(total),
        "background_queue_size": bg_queue_size,
        "ollama_host": exon_brain.ollama.ollama_host,
        "ollama_model": exon_brain.ollama.model,
        "exon_db_id": exon_brain.exon_db_id,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("API_PORT", 8000)),
        log_level=LOG_LEVEL.lower(),
    )