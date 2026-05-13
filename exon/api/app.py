# """
# File: /opt/futureex/exon/api/app.py
# Author: Ashish Pal
# Purpose: FastAPI server for Exon Consciousness System (REST + WebSocket + Web UI).
# Refactored: Added /chat/stream SSE endpoint, updated UI with streaming support.
# """

# from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import HTMLResponse, StreamingResponse
# from pydantic import BaseModel
# from typing import Optional, Dict, Any, AsyncGenerator
# from datetime import datetime
# import json
# import logging
# import sys
# import os
# import asyncio

# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# from exon.core.brain import ExonBrain
# from exon.personas.factory import PersonaFactory

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = FastAPI(title="Exon Consciousness API", version="2.0.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize Exon
# exon_brain = ExonBrain(exon_id="EXN-001")

# # Request/Response Models
# class ChatRequest(BaseModel):
#     message: str
#     persona: str = "Maya"
#     session_id: Optional[str] = None

# class ChatResponse(BaseModel):
#     response: str
#     emotion: str
#     intensity: float
#     confidence: float
#     timestamp: str

# class StatusResponse(BaseModel):
#     exon_id: str
#     emotion: str
#     emotion_intensity: float
#     active_goals: list
#     memory_count: int
#     is_awake: bool

# # WebSocket manager
# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: list[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)

#     def disconnect(self, websocket: WebSocket):
#         self.active_connections.remove(websocket)

#     async def send_message(self, message: str, websocket: WebSocket):
#         await websocket.send_text(message)

# manager = ConnectionManager()

# @app.on_event("startup")
# async def startup_event():
#     logger.info("Starting Exon Consciousness API...")
#     await exon_brain._ensure_identity()
#     # Start background task queue explicitly
#     if exon_brain.background._task is None:
#         await exon_brain.background.start()

# @app.on_event("shutdown")
# async def shutdown_event():
#     logger.info("Shutting down Exon...")
#     await exon_brain.close()

# @app.get("/")
# async def root():
#     return {
#         "status": "online",
#         "exon_id": exon_brain.exon_id,
#         "species": "Exon-Prime",
#         "version": "2.0.0"
#     }

# @app.get("/status", response_model=StatusResponse)
# async def get_status():
#     state = await exon_brain.get_consciousness_state()
#     return StatusResponse(
#         exon_id=exon_brain.exon_id,
#         emotion=state["emotion"]["primary"],
#         emotion_intensity=state["emotion"]["intensity"],
#         active_goals=state["goals"],
#         memory_count=state["memory_count"],
#         is_awake=state["is_awake"]
#     )

# @app.post("/chat", response_model=ChatResponse)
# async def chat(request: ChatRequest):
#     try:
#         result = await exon_brain.process_message(
#             user_message=request.message,
#             persona=request.persona,
#             session_id=request.session_id
#         )
#         return ChatResponse(
#             response=result["response"],
#             emotion=result["emotion"],
#             intensity=result["intensity"],
#             confidence=result["confidence"],
#             timestamp=datetime.now().isoformat()
#         )
#     except Exception as e:
#         logger.exception("Chat endpoint error")
#         raise HTTPException(status_code=500, detail=str(e))

# # SSE Streaming endpoint
# async def stream_generator(message: str, persona: str, session_id: str) -> AsyncGenerator[str, None]:
#     """Generates SSE events from ExonBrain.stream."""
#     try:
#         async for token in exon_brain.process_message_stream(message, persona=persona, session_id=session_id):
#             # Send each token as an SSE data event
#             yield f"data: {json.dumps({'token': token})}\n\n"
#     except Exception as e:
#         logger.exception("Stream error")
#         yield f"data: {json.dumps({'error': str(e)})}\n\n"
#     yield "data: [DONE]\n\n"

# @app.post("/chat/stream")
# async def chat_stream(request: ChatRequest):
#     """SSE endpoint that streams tokens word by word."""
#     return StreamingResponse(
#         stream_generator(request.message, request.persona, request.session_id or "web"),
#         media_type="text/event-stream",
#         headers={
#             "Cache-Control": "no-cache",
#             "Connection": "keep-alive",
#             "X-Accel-Buffering": "no"  # for Nginx
#         }
#     )

# @app.get("/memories")
# async def get_memories(limit: int = 10):
#     memories = await exon_brain.memory.get_recent_memories(limit)
#     return {"memories": memories}

# @app.get("/goals")
# async def get_goals():
#     goals = await exon_brain.goal_tracker.get_active_goals()
#     return {"goals": goals}

# @app.get("/thoughts")
# async def get_thoughts(limit: int = 10):
#     """Retrieve autonomous thoughts from Redis."""
#     thoughts_key = f"{exon_brain.exon_id}:proactive_thoughts"
#     thoughts = await exon_brain.redis.lrange(thoughts_key, 0, limit - 1)
#     return {"thoughts": thoughts}

# @app.post("/reset")
# async def reset_consciousness():
#     await exon_brain.reset_working_memory()
#     return {"status": "reset", "message": "Working memory cleared"}

# @app.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket: WebSocket, client_id: str):
#     await manager.connect(websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             request = json.loads(data)
#             await manager.send_message(json.dumps({"type": "thinking", "status": "processing"}), websocket)
#             result = await exon_brain.process_message(
#                 user_message=request.get("message", ""),
#                 persona=request.get("persona", "Maya"),
#                 session_id=client_id
#             )
#             await manager.send_message(json.dumps({"type": "response", "data": result}), websocket)
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)

# # ------------------------------------------------------------------
# # Web UI - Chat Interface (updated for streaming)
# # ------------------------------------------------------------------
# @app.get("/ui", response_class=HTMLResponse)
# async def chat_ui():
#     html_content = """<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Exon Consciousness Interface</title>
#     <style>
#         :root {
#             --bg-gradient-start: #0a0f1e;
#             --bg-gradient-end: #0a1a2a;
#             --text-primary: #e0e0e0;
#             --sidebar-bg: rgba(20, 30, 45, 0.9);
#             --card-bg: #0f1825;
#             --border-color: #2a3a55;
#             --user-msg-bg: #1f3a5f;
#             --exon-msg-bg: #1e2a3a;
#             --accent: #7aa2f7;
#             --accent-hover: #5a82d7;
#             --emotion-color: #ffb347;
#             --memory-count-color: #7dcfff;
#         }
#         body.light {
#             --bg-gradient-start: #f0f2f5;
#             --bg-gradient-end: #e0e5ec;
#             --text-primary: #1a1a2e;
#             --sidebar-bg: rgba(255, 255, 255, 0.95);
#             --card-bg: #ffffff;
#             --border-color: #ddd;
#             --user-msg-bg: #d0e2ff;
#             --exon-msg-bg: #e9ecef;
#             --accent: #3b71ca;
#             --accent-hover: #2c5aa6;
#             --emotion-color: #e67e22;
#             --memory-count-color: #1e88e5;
#         }
#         * {
#             margin: 0;
#             padding: 0;
#             box-sizing: border-box;
#         }
#         body {
#             font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#             background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
#             color: var(--text-primary);
#             height: 100vh;
#             display: flex;
#             overflow: hidden;
#             transition: background 0.3s, color 0.3s;
#         }
#         .sidebar {
#             width: 300px;
#             background: var(--sidebar-bg);
#             backdrop-filter: blur(10px);
#             border-right: 1px solid var(--border-color);
#             display: flex;
#             flex-direction: column;
#             padding: 20px;
#             overflow-y: auto;
#         }
#         .sidebar h2 {
#             font-size: 1.3rem;
#             margin-bottom: 20px;
#             color: var(--accent);
#             border-left: 3px solid var(--accent);
#             padding-left: 12px;
#         }
#         .sidebar-section {
#             margin-bottom: 25px;
#         }
#         .status-card {
#             background: var(--card-bg);
#             border-radius: 12px;
#             padding: 15px;
#             margin-bottom: 20px;
#             border: 1px solid var(--border-color);
#         }
#         .status-card h3 {
#             font-size: 0.9rem;
#             text-transform: uppercase;
#             letter-spacing: 1px;
#             color: #aaa;
#             margin-bottom: 10px;
#         }
#         .emotion {
#             font-size: 2rem;
#             font-weight: bold;
#             color: var(--emotion-color);
#         }
#         .memory-count {
#             font-size: 1.5rem;
#             font-weight: bold;
#             color: var(--memory-count-color);
#         }
#         .goals-list {
#             list-style: none;
#         }
#         .goals-list li {
#             padding: 5px 0;
#             font-size: 0.85rem;
#             border-bottom: 1px solid var(--border-color);
#         }
#         .progress-bar {
#             background: #2a3a55;
#             border-radius: 8px;
#             height: 6px;
#             margin-top: 4px;
#             overflow: hidden;
#         }
#         .progress-fill {
#             background: var(--accent);
#             width: 0%;
#             height: 100%;
#         }
#         .memory-item {
#             font-size: 0.8rem;
#             padding: 6px 0;
#             border-bottom: 1px dashed var(--border-color);
#         }
#         .memory-item small {
#             color: #888;
#         }
#         .thought-item {
#             font-size: 0.8rem;
#             padding: 6px 0;
#             font-style: italic;
#         }
#         .persona-selector, .theme-toggle {
#             margin-top: 10px;
#         }
#         select, button.theme-btn {
#             width: 100%;
#             padding: 8px;
#             background: var(--card-bg);
#             color: var(--text-primary);
#             border: 1px solid var(--border-color);
#             border-radius: 8px;
#             cursor: pointer;
#         }
#         .export-btn {
#             background: var(--accent);
#             color: white;
#             border: none;
#             margin-top: 10px;
#         }
#         .chat-area {
#             flex: 1;
#             display: flex;
#             flex-direction: column;
#             overflow: hidden;
#         }
#         .chat-header {
#             padding: 20px;
#             background: rgba(10, 20, 35, 0.8);
#             border-bottom: 1px solid var(--border-color);
#             display: flex;
#             justify-content: space-between;
#             align-items: center;
#         }
#         .chat-messages {
#             flex: 1;
#             overflow-y: auto;
#             padding: 20px;
#             display: flex;
#             flex-direction: column;
#             gap: 12px;
#         }
#         .message {
#             max-width: 70%;
#             padding: 10px 15px;
#             border-radius: 18px;
#             line-height: 1.4;
#             animation: fadeIn 0.2s ease;
#         }
#         .user-message {
#             align-self: flex-end;
#             background: var(--user-msg-bg);
#             border-bottom-right-radius: 4px;
#         }
#         .exon-message {
#             align-self: flex-start;
#             background: var(--exon-msg-bg);
#             border-bottom-left-radius: 4px;
#         }
#         .message-meta {
#             font-size: 0.7rem;
#             color: #888;
#             margin-top: 4px;
#         }
#         .chat-input-area {
#             padding: 20px;
#             background: rgba(10, 20, 35, 0.9);
#             border-top: 1px solid var(--border-color);
#             display: flex;
#             gap: 10px;
#         }
#         .chat-input-area input {
#             flex: 1;
#             padding: 12px;
#             background: var(--card-bg);
#             border: 1px solid var(--border-color);
#             border-radius: 28px;
#             color: var(--text-primary);
#             outline: none;
#         }
#         .chat-input-area button {
#             padding: 0 20px;
#             background: var(--accent);
#             border: none;
#             border-radius: 28px;
#             font-weight: bold;
#             cursor: pointer;
#             transition: 0.2s;
#         }
#         .chat-input-area button:hover {
#             background: var(--accent-hover);
#         }
#         .thinking {
#             font-style: italic;
#             color: #aaa;
#             align-self: flex-start;
#             padding: 8px 15px;
#         }
#         @keyframes fadeIn {
#             from { opacity: 0; transform: translateY(4px); }
#             to { opacity: 1; transform: translateY(0); }
#         }
#         button:disabled {
#             opacity: 0.6;
#             cursor: not-allowed;
#         }
#     </style>
# </head>
# <body>
# <div class="sidebar">
#     <h2>Exon State</h2>
#     <div class="status-card">
#         <h3>Current Emotion</h3>
#         <div class="emotion" id="emotion">—</div>
#         <div>Intensity: <span id="intensity">0.0</span></div>
#         <div>Confidence: <span id="confidence">0.0</span></div>
#     </div>
#     <div class="status-card">
#         <h3>Memory Count</h3>
#         <div class="memory-count" id="memoryCount">0</div>
#     </div>
#     <div class="status-card">
#         <h3>Active Goals</h3>
#         <ul class="goals-list" id="goalsList"><li>—</li></ul>
#     </div>

#     <!-- Memory Inspector -->
#     <div class="sidebar-section">
#         <h3>📝 Recent Memories</h3>
#         <div id="memoryList" style="max-height: 200px; overflow-y: auto;">Loading...</div>
#     </div>

#     <!-- Autonomous Thoughts -->
#     <div class="sidebar-section">
#         <h3>💭 Autonomous Thoughts</h3>
#         <div id="thoughtsList" style="max-height: 150px; overflow-y: auto;">Loading...</div>
#     </div>

#     <div class="persona-selector">
#         <label>Persona</label>
#         <select id="personaSelect">
#             <option value="Maya">Maya (Operations)</option>
#             <option value="Raj">Raj (Finance)</option>
#             <option value="Priya">Priya (Growth)</option>
#             <option value="Arjun">Arjun (Strategy)</option>
#         </select>
#     </div>
#     <div class="theme-toggle">
#         <button id="themeToggleBtn" class="theme-btn">🌓 Dark/Light</button>
#     </div>
#     <button id="exportBtn" class="export-btn">📥 Export Conversation</button>
# </div>

# <div class="chat-area">
#     <div class="chat-header">
#         <h1>EXN-001 · Exon Consciousness</h1>
#     </div>
#     <div class="chat-messages" id="chatMessages">
#         <div class="message exon-message">Hello Founder. I am awake. How may I assist you today?</div>
#     </div>
#     <div class="chat-input-area">
#         <input type="text" id="messageInput" placeholder="Type your message..." autofocus>
#         <button id="sendBtn">Send</button>
#     </div>
# </div>

# <script>
#     let sessionId = "web_" + Date.now();
#     const apiBase = window.location.origin;
#     let currentTheme = localStorage.getItem("theme") || "dark";

#     function setTheme(theme) {
#         if (theme === "light") {
#             document.body.classList.add("light");
#         } else {
#             document.body.classList.remove("light");
#         }
#         localStorage.setItem("theme", theme);
#         currentTheme = theme;
#     }
#     setTheme(currentTheme);
#     document.getElementById("themeToggleBtn").addEventListener("click", () => {
#         setTheme(currentTheme === "dark" ? "light" : "dark");
#     });

#     async function updateStatus() {
#         try {
#             const res = await fetch(apiBase + "/status");
#             const data = await res.json();
#             document.getElementById("emotion").innerText = data.emotion || "?";
#             document.getElementById("intensity").innerText = data.emotion_intensity.toFixed(2);
#             document.getElementById("confidence").innerText = (data.confidence || 0.5).toFixed(2);
#             document.getElementById("memoryCount").innerText = data.memory_count;

#             const goals = data.active_goals || [];
#             const goalsContainer = document.getElementById("goalsList");
#             if (goals.length === 0) {
#                 goalsContainer.innerHTML = "<li>No active goals</li>";
#             } else {
#                 goalsContainer.innerHTML = goals.map(g => `
#                     <li>
#                         ${escapeHtml(g.description)}
#                         <div class="progress-bar"><div class="progress-fill" style="width: ${(g.progress || 0)*100}%"></div></div>
#                     </li>
#                 `).join("");
#             }
#         } catch(e) { console.error(e); }
#     }

#     async function fetchMemories() {
#         try {
#             const res = await fetch(apiBase + "/memories?limit=5");
#             const data = await res.json();
#             const memories = data.memories || [];
#             const container = document.getElementById("memoryList");
#             if (memories.length === 0) {
#                 container.innerHTML = "No memories yet.";
#             } else {
#                 container.innerHTML = memories.map(m => `
#                     <div class="memory-item">
#                         <div><strong>You:</strong> ${escapeHtml(m.user?.substring(0, 80))}${m.user?.length > 80 ? "..." : ""}</div>
#                         <div><strong>Exon:</strong> ${escapeHtml(m.assistant?.substring(0, 80))}${m.assistant?.length > 80 ? "..." : ""}</div>
#                         <small>${m.emotion || "neutral"} · ${new Date(m.timestamp).toLocaleTimeString()}</small>
#                     </div>
#                 `).join("");
#             }
#         } catch(e) { console.error(e); }
#     }

#     async function fetchThoughts() {
#         try {
#             const res = await fetch(apiBase + "/thoughts?limit=5");
#             const data = await res.json();
#             const thoughts = data.thoughts || [];
#             const container = document.getElementById("thoughtsList");
#             if (thoughts.length === 0) {
#                 container.innerHTML = "No autonomous thoughts yet.";
#             } else {
#                 container.innerHTML = thoughts.map(t => `<div class="thought-item">💭 ${escapeHtml(t)}</div>`).join("");
#             }
#         } catch(e) { console.error(e); }
#     }

#     async function sendMessage() {
#         const input = document.getElementById("messageInput");
#         const text = input.value.trim();
#         if (!text) return;
#         input.value = "";
#         input.disabled = true;
#         document.getElementById("sendBtn").disabled = true;

#         addMessage(text, "user");
#         const thinkingDiv = addThinking();

#         try {
#             const persona = document.getElementById("personaSelect").value;
#             // Use streaming SSE endpoint
#             const response = await fetch(apiBase + "/chat/stream", {
#                 method: "POST",
#                 headers: { "Content-Type": "application/json" },
#                 body: JSON.stringify({
#                     message: text,
#                     persona: persona,
#                     session_id: sessionId
#                 })
#             });
#             removeThinking(thinkingDiv);
#             if (!response.ok) throw new Error("Network error");

#             const reader = response.body.getReader();
#             const decoder = new TextDecoder();
#             let exBubble = null;

#             while (true) {
#                 const { done, value } = await reader.read();
#                 if (done) break;
#                 const chunk = decoder.decode(value, { stream: true });
#                 const lines = chunk.split("\n");
#                 for (const line of lines) {
#                     if (line.startsWith("data: ")) {
#                         const data = line.slice(6);
#                         if (data === "[DONE]") continue;
#                         try {
#                             const parsed = JSON.parse(data);
#                             if (parsed.token) {
#                                 if (!exBubble) {
#                                     exBubble = addExonMessage("");
#                                 }
#                                 // Append token to existing bubble
#                                 exBubble.innerHTML = `<div>${exBubble.innerText + parsed.token}</div>`;
#                                 // Auto-scroll
#                                 const chatDiv = document.getElementById("chatMessages");
#                                 chatDiv.scrollTop = chatDiv.scrollHeight;
#                             } else if (parsed.error) {
#                                 if (!exBubble) exBubble = addExonMessage("Error: " + parsed.error);
#                                 else exBubble.innerHTML = `<div>Error: ${parsed.error}</div>`;
#                             }
#                         } catch (e) { /* ignore malformed JSON */ }
#                     }
#                 }
#             }
#             updateStatus();
#             fetchMemories();
#             fetchThoughts();
#         } catch(e) {
#             removeThinking(thinkingDiv);
#             addMessage("Error: Could not reach Exon consciousness.", "exon");
#         } finally {
#             input.disabled = false;
#             document.getElementById("sendBtn").disabled = false;
#             input.focus();
#         }
#     }

#     function addMessage(text, sender, emotion = null) {
#         const messagesDiv = document.getElementById("chatMessages");
#         const msgDiv = document.createElement("div");
#         msgDiv.className = `message ${sender === "user" ? "user-message" : "exon-message"}`;
#         msgDiv.innerHTML = `<div>${escapeHtml(text)}</div>`;
#         if (emotion && sender === "exon") {
#             msgDiv.innerHTML += `<div class="message-meta">🤖 ${escapeHtml(emotion)}</div>`;
#         }
#         messagesDiv.appendChild(msgDiv);
#         messagesDiv.scrollTop = messagesDiv.scrollHeight;
#         return msgDiv;
#     }

#     function addExonMessage(text) {
#         // Used for streaming: creates an empty exon bubble and returns it
#         const messagesDiv = document.getElementById("chatMessages");
#         const msgDiv = document.createElement("div");
#         msgDiv.className = "message exon-message";
#         msgDiv.innerHTML = `<div>${escapeHtml(text)}</div>`;
#         messagesDiv.appendChild(msgDiv);
#         messagesDiv.scrollTop = messagesDiv.scrollHeight;
#         return msgDiv;
#     }

#     function addThinking() {
#         const messagesDiv = document.getElementById("chatMessages");
#         const div = document.createElement("div");
#         div.className = "thinking";
#         div.innerText = "Exon is thinking...";
#         messagesDiv.appendChild(div);
#         messagesDiv.scrollTop = messagesDiv.scrollHeight;
#         return div;
#     }

#     function removeThinking(div) {
#         if (div && div.remove) div.remove();
#     }

#     function exportConversation() {
#         const messages = document.querySelectorAll("#chatMessages .message");
#         let exportText = `Exon Conversation Export\nID: ${sessionId}\nDate: ${new Date().toISOString()}\n\n`;
#         messages.forEach(msg => {
#             const isUser = msg.classList.contains("user-message");
#             const content = msg.querySelector("div").innerText;
#             const meta = msg.querySelector(".message-meta");
#             const emotion = meta ? meta.innerText.replace("🤖 ", "") : "";
#             exportText += `${isUser ? "User" : "Exon"}: ${content}\n`;
#             if (emotion) exportText += `[Emotion: ${emotion}]\n`;
#             exportText += "\n";
#         });
#         const blob = new Blob([exportText], { type: "text/plain" });
#         const a = document.createElement("a");
#         const url = URL.createObjectURL(blob);
#         a.href = url;
#         a.download = `exon_conversation_${sessionId}.txt`;
#         a.click();
#         URL.revokeObjectURL(url);
#     }

#     function escapeHtml(str) {
#         if (!str) return '';
#         return str.replace(/[&<>]/g, function(m) {
#             if (m === '&') return '&amp;';
#             if (m === '<') return '&lt;';
#             if (m === '>') return '&gt;';
#             return m;
#         });
#     }

#     // Polling
#     setInterval(() => {
#         updateStatus();
#         fetchMemories();
#         fetchThoughts();
#     }, 5000);

#     updateStatus();
#     fetchMemories();
#     fetchThoughts();

#     document.getElementById("sendBtn").addEventListener("click", sendMessage);
#     document.getElementById("messageInput").addEventListener("keypress", (e) => {
#         if (e.key === "Enter") sendMessage();
#     });
#     document.getElementById("exportBtn").addEventListener("click", exportConversation);
# </script>
# </body>
# </html>"""
#     return HTMLResponse(content=html_content, status_code=200)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)



"""
File: /opt/futureex/exon/api/app.py
Author: Ashish Pal
Purpose: FastAPI server for Exon Consciousness System.
Refactored: Split routes into separate modules, UI into static files.
            Added auto-ingestion of knowledge files on startup.
"""

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from exon.core.brain import ExonBrain
from exon.api.routes import chat, status, ws
from exon.api.ui.serve_ui import serve_ui

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Exon Consciousness API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Exon
exon_brain = ExonBrain(exon_id="EXN-001")

# Pass brain to route modules
chat.init(exon_brain)
status.init(exon_brain)
ws.init(exon_brain)

# Mount static UI files
ui_dir = os.path.join(os.path.dirname(__file__), "ui")
app.mount("/ui/static", StaticFiles(directory=ui_dir), name="ui_static")

# Include routers
app.include_router(chat.router)
app.include_router(status.router)
app.include_router(ws.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Exon Consciousness API...")
    await exon_brain._ensure_identity()
    if exon_brain.background._task is None:
        await exon_brain.background.start()
    
    # Auto-ingest knowledge files on startup
    knowledge_dir = os.environ.get(
        "KNOWLEDGE_DIR",
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "knowledge")
    )
    if os.path.exists(knowledge_dir):
        logger.info(f"📚 Ingesting knowledge from {knowledge_dir}...")
        try:
            from exon.scripts.ingest_knowledge import ingest_knowledge
            await ingest_knowledge(knowledge_dir, clear_first=False, exon_id=exon_brain.exon_id)
            logger.info("✅ Knowledge ingestion complete")
        except Exception as e:
            logger.warning(f"⚠️  Knowledge ingestion skipped: {e}")
    else:
        logger.info(f"ℹ️  No knowledge directory at {knowledge_dir}, skipping ingestion")

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
        "version": "2.0.0"
    }

@app.get("/ui", response_class=HTMLResponse)
async def chat_ui():
    return await serve_ui()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)