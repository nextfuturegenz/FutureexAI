# """
# File: /opt/futureex/exon/connectors/ollama_bridge.py
# Author: Ashish Pal
# Purpose: Async bridge to Ollama API – works inside Docker containers.
# Refactored: Added streaming generation method.
# """

# import aiohttp
# import asyncio
# import os
# import json
# import logging
# from typing import AsyncGenerator

# logger = logging.getLogger(__name__)

# class OllamaBridge:
#     def __init__(self):
#         # Allow override; inside Docker, set to http://host.docker.internal:11434
#         self.ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
#         self.model = os.environ.get("OLLAMA_MODEL", "phi3:mini")
#         self.timeout = aiohttp.ClientTimeout(total=60)  # increased for slower models
#         self.max_retries = 3
#         self.retry_delay = 1.0

#     async def generate(self, prompt: str, temperature: float = 0.7) -> str:
#         for attempt in range(self.max_retries):
#             try:
#                 async with aiohttp.ClientSession(timeout=self.timeout) as session:
#                     payload = {
#                         "model": self.model,
#                         "prompt": prompt,
#                         "temperature": temperature,
#                         "stream": False
#                     }
#                     async with session.post(f"{self.ollama_host}/api/generate", json=payload) as resp:
#                         if resp.status == 200:
#                             data = await resp.json()
#                             return data.get("response", "").strip()
#                         else:
#                             text = await resp.text()
#                             logger.error(f"Ollama error {resp.status}: {text}")
#                             if attempt == self.max_retries - 1:
#                                 raise Exception(f"Ollama returned {resp.status}")
#             except (aiohttp.ClientError, asyncio.TimeoutError) as e:
#                 logger.warning(f"Attempt {attempt+1} failed: {e}")
#                 if attempt < self.max_retries - 1:
#                     await asyncio.sleep(self.retry_delay * (2 ** attempt))
#                 else:
#                     raise Exception(f"Ollama unreachable at {self.ollama_host} after {self.max_retries} tries") from e
#         return ""

#     async def generate_stream(self, prompt: str, temperature: float = 0.7) -> AsyncGenerator[str, None]:
#         """Stream tokens from Ollama as they are generated."""
#         payload = {
#             "model": self.model,
#             "prompt": prompt,
#             "temperature": temperature,
#             "stream": True
#         }
#         async with aiohttp.ClientSession(timeout=self.timeout) as session:
#             async with session.post(f"{self.ollama_host}/api/generate", json=payload) as resp:
#                 if resp.status != 200:
#                     text = await resp.text()
#                     raise Exception(f"Ollama streaming error {resp.status}: {text}")
#                 # The Ollama API returns one JSON object per line
#                 async for line in resp.content:
#                     if line:
#                         try:
#                             data = json.loads(line)
#                             token = data.get("response", "")
#                             if token:
#                                 yield token
#                             if data.get("done", False):
#                                 break
#                         except json.JSONDecodeError:
#                             continue

#     async def health_check(self) -> bool:
#         try:
#             async with aiohttp.ClientSession() as session:
#                 async with session.get(f"{self.ollama_host}/api/tags", timeout=5) as resp:
#                     return resp.status == 200
#         except Exception:
#             return False

"""
File: /opt/futureex/exon/connectors/ollama_bridge.py
Author: Ashish Pal
Purpose: Async bridge to Ollama API – works inside Docker containers.
Refactored: Added streaming generation method, increased timeouts for RAG.
"""

import aiohttp
import asyncio
import os
import json
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

class OllamaBridge:
    def __init__(self):
        self.ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.environ.get("OLLAMA_MODEL", "phi3:mini")
        self.timeout = aiohttp.ClientTimeout(total=120)  # Increased to 120s for RAG
        self.stream_timeout = aiohttp.ClientTimeout(total=180, sock_read=60)  # Streaming timeout
        self.max_retries = 2
        self.retry_delay = 1.0

    async def generate(self, prompt: str, temperature: float = 0.7) -> str:
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    payload = {
                        "model": self.model,
                        "prompt": prompt,
                        "temperature": temperature,
                        "stream": False
                    }
                    async with session.post(
                        f"{self.ollama_host}/api/generate", json=payload
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data.get("response", "").strip()
                        else:
                            text = await resp.text()
                            logger.error(f"Ollama error {resp.status}: {text[:200]}")
                            if attempt == self.max_retries - 1:
                                raise Exception(f"Ollama returned {resp.status}")
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.warning(f"Attempt {attempt+1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                else:
                    raise Exception(
                        f"Ollama unreachable at {self.ollama_host} after {self.max_retries} tries"
                    ) from e
        return ""

    async def generate_stream(self, prompt: str, temperature: float = 0.7) -> AsyncGenerator[str, None]:
        """Stream tokens from Ollama as they are generated."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": True
        }
        try:
            async with aiohttp.ClientSession(timeout=self.stream_timeout) as session:
                async with session.post(
                    f"{self.ollama_host}/api/generate", json=payload
                ) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        raise Exception(f"Ollama streaming error {resp.status}: {text[:200]}")
                    
                    buffer = ""
                    async for chunk in resp.content.iter_chunks():
                        if chunk:
                            try:
                                data = chunk[0].decode('utf-8')
                                buffer += data
                                lines = buffer.split('\n')
                                buffer = lines.pop()  # Keep incomplete line in buffer
                                
                                for line in lines:
                                    if line.strip():
                                        try:
                                            obj = json.loads(line)
                                            token = obj.get("response", "")
                                            if token:
                                                yield token
                                            if obj.get("done", False):
                                                return
                                        except json.JSONDecodeError:
                                            continue
                            except Exception:
                                continue
        except asyncio.TimeoutError:
            logger.warning("Stream timed out, returning partial response")
        except Exception as e:
            logger.error(f"Stream error: {e}")
            raise

    async def health_check(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.ollama_host}/api/tags", timeout=5
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False