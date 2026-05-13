"""
File: /opt/futureex/exon/api/app.py
Author: Ashish Pal
Purpose: FastAPI server for Exon Consciousness System (REST + WebSocket + Web UI).
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import json
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from exon.core.brain import ExonBrain
from exon.personas.factory import PersonaFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Exon Consciousness API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Exon
exon_brain = ExonBrain(exon_id="EXN-001")

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    persona: str = "Maya"
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    emotion: str
    intensity: float
    confidence: float
    timestamp: str

class StatusResponse(BaseModel):
    exon_id: str
    emotion: str
    emotion_intensity: float
    active_goals: list
    memory_count: int
    is_awake: bool

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Exon Consciousness API...")
    await exon_brain._ensure_identity()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Exon...")
    await exon_brain.close()

@app.get("/")
async def root():
    return {
        "status": "online",
        "exon_id": exon_brain.exon_id,
        "species": "Exon-Prime",
        "version": "1.0.0"
    }

@app.get("/status", response_model=StatusResponse)
async def get_status():
    state = await exon_brain.get_consciousness_state()
    return StatusResponse(
        exon_id=exon_brain.exon_id,
        emotion=state["emotion"]["primary"],
        emotion_intensity=state["emotion"]["intensity"],
        active_goals=state["goals"],
        memory_count=state["memory_count"],
        is_awake=state["is_awake"]
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = await exon_brain.process_message(
            user_message=request.message,
            persona=request.persona,
            session_id=request.session_id
        )
        return ChatResponse(
            response=result["response"],
            emotion=result["emotion"],
            intensity=result["intensity"],
            confidence=result["confidence"],
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.exception("Chat endpoint error")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memories")
async def get_memories(limit: int = 10):
    memories = await exon_brain.memory.get_recent_memories(limit)
    return {"memories": memories}

@app.get("/goals")
async def get_goals():
    goals = await exon_brain.goal_tracker.get_active_goals()
    return {"goals": goals}

@app.post("/reset")
async def reset_consciousness():
    await exon_brain.reset_working_memory()
    return {"status": "reset", "message": "Working memory cleared"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)
            await manager.send_message(json.dumps({"type": "thinking", "status": "processing"}), websocket)
            result = await exon_brain.process_message(
                user_message=request.get("message", ""),
                persona=request.get("persona", "Maya"),
                session_id=client_id
            )
            await manager.send_message(json.dumps({"type": "response", "data": result}), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ------------------------------------------------------------------
# Web UI - Chat Interface
# ------------------------------------------------------------------
@app.get("/ui", response_class=HTMLResponse)
async def chat_ui():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exon Consciousness Interface</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0f1e 0%, #0a1a2a 100%);
            color: #e0e0e0;
            height: 100vh;
            display: flex;
            overflow: hidden;
        }
        .sidebar {
            width: 280px;
            background: rgba(20, 30, 45, 0.9);
            backdrop-filter: blur(10px);
            border-right: 1px solid #2a3a55;
            display: flex;
            flex-direction: column;
            padding: 20px;
            overflow-y: auto;
        }
        .sidebar h2 {
            font-size: 1.3rem;
            margin-bottom: 20px;
            color: #7aa2f7;
            border-left: 3px solid #7aa2f7;
            padding-left: 12px;
        }
        .status-card {
            background: #0f1825;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid #2a3a55;
        }
        .status-card h3 {
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #aaa;
            margin-bottom: 10px;
        }
        .emotion {
            font-size: 2rem;
            font-weight: bold;
            color: #ffb347;
        }
        .intensity {
            font-size: 1.2rem;
            margin-top: 5px;
        }
        .confidence {
            font-size: 1rem;
            margin-top: 5px;
        }
        .memory-count {
            font-size: 1.5rem;
            font-weight: bold;
            color: #7dcfff;
        }
        .goals-list {
            list-style: none;
            margin-top: 8px;
        }
        .goals-list li {
            padding: 5px 0;
            font-size: 0.85rem;
            border-bottom: 1px solid #2a3a55;
        }
        .progress-bar {
            background: #2a3a55;
            border-radius: 8px;
            height: 6px;
            margin-top: 4px;
            overflow: hidden;
        }
        .progress-fill {
            background: #7aa2f7;
            width: 0%;
            height: 100%;
            border-radius: 8px;
        }
        .persona-selector {
            margin-top: auto;
            margin-bottom: 20px;
        }
        .persona-selector select {
            width: 100%;
            padding: 8px;
            background: #0f1825;
            color: white;
            border: 1px solid #2a3a55;
            border-radius: 8px;
            cursor: pointer;
        }
        .chat-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .chat-header {
            padding: 20px;
            background: rgba(10, 20, 35, 0.8);
            border-bottom: 1px solid #2a3a55;
        }
        .chat-header h1 {
            font-size: 1.4rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .message {
            max-width: 70%;
            padding: 10px 15px;
            border-radius: 18px;
            line-height: 1.4;
            animation: fadeIn 0.2s ease;
        }
        .user-message {
            align-self: flex-end;
            background: #1f3a5f;
            border-bottom-right-radius: 4px;
        }
        .exon-message {
            align-self: flex-start;
            background: #1e2a3a;
            border-bottom-left-radius: 4px;
        }
        .message-meta {
            font-size: 0.7rem;
            color: #888;
            margin-top: 4px;
        }
        .chat-input-area {
            padding: 20px;
            background: rgba(10, 20, 35, 0.9);
            border-top: 1px solid #2a3a55;
            display: flex;
            gap: 10px;
        }
        .chat-input-area input {
            flex: 1;
            padding: 12px;
            background: #0f1825;
            border: 1px solid #2a3a55;
            border-radius: 28px;
            color: white;
            outline: none;
        }
        .chat-input-area button {
            padding: 0 20px;
            background: #7aa2f7;
            border: none;
            border-radius: 28px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
        }
        .chat-input-area button:hover {
            background: #5a82d7;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(4px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .thinking {
            font-style: italic;
            color: #aaa;
            align-self: flex-start;
            padding: 8px 15px;
        }
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #0f1825;
        }
        ::-webkit-scrollbar-thumb {
            background: #2a3a55;
            border-radius: 3px;
        }
    </style>
</head>
<body>
<div class="sidebar">
    <h2>Exon State</h2>
    <div class="status-card">
        <h3>Current Emotion</h3>
        <div class="emotion" id="emotion">—</div>
        <div class="intensity">Intensity: <span id="intensity">0.0</span></div>
        <div class="confidence">Confidence: <span id="confidence">0.0</span></div>
    </div>
    <div class="status-card">
        <h3>Memory Count</h3>
        <div class="memory-count" id="memoryCount">0</div>
    </div>
    <div class="status-card">
        <h3>Active Goals</h3>
        <ul class="goals-list" id="goalsList">
            <li>—</li>
        </ul>
    </div>
    <div class="persona-selector">
        <label>Persona</label>
        <select id="personaSelect">
            <option value="Maya">Maya (Operations)</option>
            <option value="Raj">Raj (Finance)</option>
            <option value="Priya">Priya (Growth)</option>
            <option value="Arjun">Arjun (Strategy)</option>
        </select>
    </div>
</div>
<div class="chat-area">
    <div class="chat-header">
        <h1>EXN-001 · Exon Consciousness</h1>
    </div>
    <div class="chat-messages" id="chatMessages">
        <div class="message exon-message">Hello Founder. I am awake. How may I assist you today?</div>
    </div>
    <div class="chat-input-area">
        <input type="text" id="messageInput" placeholder="Type your message..." autofocus>
        <button id="sendBtn">Send</button>
    </div>
</div>

<script>
    let sessionId = "web_" + Date.now();
    const apiBase = window.location.origin;

    async function updateStatus() {
        try {
            const res = await fetch(apiBase + "/status");
            const data = await res.json();
            document.getElementById("emotion").innerText = data.emotion || "?";
            document.getElementById("intensity").innerText = data.emotion_intensity.toFixed(2);
            document.getElementById("confidence").innerText = (data.confidence || 0.5).toFixed(2);
            document.getElementById("memoryCount").innerText = data.memory_count;

            const goals = data.active_goals || [];
            const goalsContainer = document.getElementById("goalsList");
            if (goals.length === 0) {
                goalsContainer.innerHTML = "<li>No active goals</li>";
            } else {
                goalsContainer.innerHTML = goals.map(g => `
                    <li>
                        ${escapeHtml(g.description)}
                        <div class="progress-bar"><div class="progress-fill" style="width: ${(g.progress || 0)*100}%"></div></div>
                    </li>
                `).join("");
            }
        } catch(e) { console.error(e); }
    }

    async function sendMessage() {
        const input = document.getElementById("messageInput");
        const text = input.value.trim();
        if (!text) return;
        input.value = "";
        input.disabled = true;
        document.getElementById("sendBtn").disabled = true;

        addMessage(text, "user");
        const thinkingDiv = addThinking();

        try {
            const persona = document.getElementById("personaSelect").value;
            const res = await fetch(apiBase + "/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: text,
                    persona: persona,
                    session_id: sessionId
                })
            });
            const data = await res.json();
            removeThinking(thinkingDiv);
            addMessage(data.response, "exon", data.emotion);
            updateStatus();
        } catch(e) {
            removeThinking(thinkingDiv);
            addMessage("Error: Could not reach Exon consciousness.", "exon");
        } finally {
            input.disabled = false;
            document.getElementById("sendBtn").disabled = false;
            input.focus();
        }
    }

    function addMessage(text, sender, emotion = null) {
        const messagesDiv = document.getElementById("chatMessages");
        const msgDiv = document.createElement("div");
        msgDiv.className = `message ${sender === "user" ? "user-message" : "exon-message"}`;
        msgDiv.innerHTML = `<div>${escapeHtml(text)}</div>`;
        if (emotion && sender === "exon") {
            msgDiv.innerHTML += `<div class="message-meta">🤖 ${escapeHtml(emotion)}</div>`;
        }
        messagesDiv.appendChild(msgDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    function addThinking() {
        const messagesDiv = document.getElementById("chatMessages");
        const div = document.createElement("div");
        div.className = "thinking";
        div.innerText = "Exon is thinking...";
        messagesDiv.appendChild(div);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        return div;
    }

    function removeThinking(div) {
        if (div && div.remove) div.remove();
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/[&<>]/g, function(m) {
            if (m === '&') return '&amp;';
            if (m === '<') return '&lt;';
            if (m === '>') return '&gt;';
            return m;
        });
    }

    setInterval(updateStatus, 5000);
    updateStatus();

    document.getElementById("sendBtn").addEventListener("click", sendMessage);
    document.getElementById("messageInput").addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });
</script>
</body>
</html>"""
    # Return as HTMLResponse with explicit UTF-8 encoding
    return HTMLResponse(content=html_content, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)