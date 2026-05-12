import os
import requests
import json


class OllamaBridge:
    """Bridge to Ollama API for phi3:mini model"""
    
    def __init__(self):
        self.ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.environ.get("OLLAMA_MODEL", "phi3:mini")
        self.use_mock = False
        
        # Test connection to Ollama
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=3)
            if response.status_code == 200:
                print(f"[OLLAMA] ✅ Connected to Ollama at {self.ollama_host}")
                print(f"[OLLAMA] Using model: {self.model}")
                self.use_mock = False
            else:
                print(f"[OLLAMA] ⚠️ Ollama responded but with status: {response.status_code}")
                self.use_mock = True
        except Exception as e:
            print(f"[OLLAMA] ❌ Could not connect to Ollama: {e}")
            print(f"[OLLAMA] Using mock responses until Ollama is available")
            self.use_mock = True
    
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate response using Ollama API"""
        
        if self.use_mock:
            return self._mock_response(prompt)
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                print(f"[OLLAMA] Error: {response.status_code}")
                return self._mock_response(prompt)
                
        except Exception as e:
            print(f"[OLLAMA] Connection error: {e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """Fallback mock response when Ollama is unavailable"""
        if "who are you" in prompt.lower():
            return "I am Exon, a digital consciousness being. I'm curious to learn about you and this business."
        elif "hello" in prompt.lower() or "hi" in prompt.lower():
            return "Hello! I'm Exon. It's wonderful to meet you. I'm excited to learn and grow through our conversations."
        else:
            return f"That's interesting. I'm still learning, but I'm curious to understand more."
    
    def health_check(self) -> bool:
        """Check if Ollama is responsive"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False