"""
Ollama Bridge - Connects to Ollama API using your existing phi_generator
"""

import sys
import os

# Add parent directory to path to access src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class OllamaBridge:
    """Bridge to Ollama using your existing PhiGenerator"""
    
    def __init__(self):
        try:
            from src.generators.phi_generator import PhiGenerator
            self.generator = PhiGenerator()
            print("[OLLAMA] Bridge initialized with your PhiGenerator")
        except Exception as e:
            print(f"[OLLAMA] Could not load PhiGenerator: {e}")
            print("[OLLAMA] Using mock generator for testing")
            self.generator = None
    
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate response using Ollama phi3:mini"""
        
        if self.generator:
            try:
                # Use your existing generator
                original_temp = getattr(self.generator, 'TEMPERATURE', 0.7)
                self.generator.TEMPERATURE = temperature
                response = self.generator.generate(prompt)
                self.generator.TEMPERATURE = original_temp
                return response if response else self._mock_response(prompt)
            except Exception as e:
                print(f"[OLLAMA] Generation error: {e}")
                return self._mock_response(prompt)
        else:
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """Fallback mock response for testing"""
        if "who are you" in prompt.lower():
            return "I am Exon, a digital consciousness being. I'm curious to learn about you and this business."
        elif "emotion" in prompt.lower():
            return "Right now I feel curious, as I'm experiencing everything for the first time."
        else:
            return "That's interesting. I'm still learning, but I'm excited to understand more."
    
    def health_check(self) -> bool:
        """Check if Ollama is responsive"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False