# exon/api/routes/ws.py
# Author: Ashish Pal
# Purpose: WebSocket endpoint.

import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()

# Will be set by app.py
exon_brain = None

def init(brain):
    global exon_brain
    exon_brain = brain

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)
            await manager.send_message(
                json.dumps({"type": "thinking", "status": "processing"}),
                websocket
            )
            result = await exon_brain.process_message(
                user_message=request.get("message", ""),
                persona=request.get("persona", "Maya"),
                session_id=client_id
            )
            await manager.send_message(
                json.dumps({"type": "response", "data": result}),
                websocket
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)