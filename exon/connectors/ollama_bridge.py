"""
File: /opt/futureex/exon/connectors/ollama_bridge.py
Author: Ashish Pal
Purpose: Async bridge to Ollama API (phi3:mini). Handles retries, timeouts, and no mock fallback.
"""

import aiohttp
import asyncio
import os
import logging

logger = logging.getLogger(__name__)

class OllamaBridge:
    def __init__(self):
        self.ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.environ.get("OLLAMA_MODEL", "phi3:mini")
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.max_retries = 3
        self.retry_delay = 1.0

    async def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate response with retries. Raises exception on failure."""
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    payload = {
                        "model": self.model,
                        "prompt": prompt,
                        "temperature": temperature,
                        "stream": False
                    }
                    async with session.post(f"{self.ollama_host}/api/generate", json=payload) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data.get("response", "").strip()
                        else:
                            text = await resp.text()
                            logger.error(f"Ollama error {resp.status}: {text}")
                            if attempt == self.max_retries - 1:
                                raise Exception(f"Ollama returned {resp.status}")
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.warning(f"Attempt {attempt+1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                else:
                    raise Exception(f"Ollama unreachable after {self.max_retries} tries") from e
        return ""  # never reached

    async def health_check(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_host}/api/tags", timeout=5) as resp:
                    return resp.status == 200
        except Exception:
            return False