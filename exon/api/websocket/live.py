"""Live WebSocket handlers"""

from fastapi import WebSocket
import json

class LiveWebSocket:
    def __init__(self):
        self.connections = []

    async def handle_connection(self, websocket: WebSocket, exon_brain):
        await websocket.accept()
        self.connections.append(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                msg = json.loads(data)
                
                # Stream thinking process
                await websocket.send_json({"type": "thinking", "content": "Processing..."})
                
                # Get response
                result = await exon_brain.process_message(
                    msg.get("message", ""),
                    msg.get("persona", "Maya")
                )
                
                # Stream response
                await websocket.send_json({"type": "response", "data": result})
                
        except Exception as e:
            self.connections.remove(websocket)