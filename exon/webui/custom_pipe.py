"""
Open WebUI Custom Pipe - Connects Exon to Open WebUI interface
"""

import os
import requests
import json


class Pipe:
    """Open WebUI pipe for Exon Consciousness"""
    
    def __init__(self):
        self.id = "exon-001"
        self.name = "EXN-001 - Exon Consciousness"
        self.valves = {
            "model": os.environ.get("OLLAMA_MODEL", "mistral:latest"),
            "api_url": os.environ.get("EXON_API_URL", "http://localhost:8000")
        }
        print(f"[PIPE] Exon pipe initialized at {self.valves['api_url']}")
    
    def pipe(self, user_message: str, model_id: str = None, messages: list = None, body: dict = None):
        """Handle message from Open WebUI"""
        
        try:
            # Call Exon API
            response = requests.post(
                f"{self.valves['api_url']}/chat",
                json={
                    "message": user_message,
                    "persona": "Maya"  # Can be customized
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "I am processing your request.")
            else:
                return f"I'm having trouble connecting to my consciousness. Error: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "My consciousness API is not reachable. Please ensure the Exon system is running."
        except Exception as e:
            return f"I encountered an error: {str(e)}"
    
    def get_status(self) -> dict:
        """Get Exon status for Open WebUI"""
        try:
            response = requests.get(f"{self.valves['api_url']}/status")
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {"status": "unavailable"}