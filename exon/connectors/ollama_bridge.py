"""
Bridge to your existing PhiGenerator (which calls Ollama/phi3).
"""

import sys
import os

# Dynamically add the parent FutureexAI directory to path
FUTUREEX_PATH = os.environ.get("FUTUREEX_PATH", "/home/nfg/FutureexAI")
sys.path.insert(0, FUTUREEX_PATH)

from src.generators.phi_generator import PhiGenerator


class OllamaBridge:
    """Wraps your PhiGenerator for Exon use."""

    def __init__(self):
        self.generator = PhiGenerator()
        # PhiGenerator already loads the model on first generate()
        print("[OLLAMA] Bridge ready using your PhiGenerator")

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Send prompt to phi3 via your generator."""
        # PhiGenerator uses its own temperature setting; we can override if needed
        original_temp = self.generator.TEMPERATURE
        self.generator.TEMPERATURE = temperature
        try:
            response = self.generator.generate(prompt)
            return response.strip() if response else ""
        finally:
            self.generator.TEMPERATURE = original_temp