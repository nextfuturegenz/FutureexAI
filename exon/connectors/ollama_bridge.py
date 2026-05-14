"""
File: /opt/futureex/exon/connectors/ollama_bridge.py
Author: Ashish Pal
Purpose: Async bridge to Ollama API.
Refactored v3:
  - Structured DEBUG logging with timing on every call
  - Logs prompt length and response length
  - Logs retry attempts clearly
  - stream logs token count and first-token latency
"""

import aiohttp
import asyncio
import os
import json
import logging
import time
from typing import AsyncGenerator

logger = logging.getLogger(__name__)


class OllamaBridge:
    def __init__(self):
        self.ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.environ.get("OLLAMA_MODEL", "mistral:latest")
        self.timeout = aiohttp.ClientTimeout(total=120)
        self.stream_timeout = aiohttp.ClientTimeout(total=180, sock_read=60)
        self.max_retries = 2
        self.retry_delay = 1.0
        logger.debug(f"[ollama] host={self.ollama_host} model={self.model}")

    async def generate(self, prompt: str, temperature: float = 0.7) -> str:
        t_start = time.perf_counter()
        logger.debug(f"[ollama] generate: model={self.model} temp={temperature:.2f} "
                     f"prompt_len={len(prompt)}")

        for attempt in range(self.max_retries):
            t_attempt = time.perf_counter()
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    payload = {
                        "model": self.model,
                        "prompt": prompt,
                        "temperature": temperature,
                        "stream": False,
                    }
                    async with session.post(
                        f"{self.ollama_host}/api/generate", json=payload
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            response = data.get("response", "").strip()
                            elapsed = (time.perf_counter() - t_start) * 1000
                            logger.info(f"[ollama] generate OK in {elapsed:.0f}ms – "
                                        f"{len(response)} chars returned")
                            if data.get("eval_count") and data.get("eval_duration"):
                                tps = data["eval_count"] / (data["eval_duration"] / 1e9)
                                logger.debug(f"[ollama] throughput: {tps:.1f} tok/s "
                                             f"({data['eval_count']} tokens)")
                            return response
                        else:
                            text = await resp.text()
                            logger.error(f"[ollama] HTTP {resp.status} on attempt {attempt+1}: "
                                         f"{text[:200]}")
                            if attempt == self.max_retries - 1:
                                raise Exception(f"Ollama returned {resp.status}")

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                attempt_elapsed = (time.perf_counter() - t_attempt) * 1000
                logger.warning(f"[ollama] attempt {attempt+1}/{self.max_retries} failed "
                                f"after {attempt_elapsed:.0f}ms: {type(e).__name__}: {e}")
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.debug(f"[ollama] retrying in {delay:.1f}s…")
                    await asyncio.sleep(delay)
                else:
                    raise Exception(
                        f"Ollama unreachable at {self.ollama_host} "
                        f"after {self.max_retries} attempts"
                    ) from e
        return ""

    async def generate_stream(
        self, prompt: str, temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        t_start = time.perf_counter()
        logger.debug(f"[ollama] generate_stream: model={self.model} temp={temperature:.2f} "
                     f"prompt_len={len(prompt)}")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": True,
        }
        first_token = True
        token_count = 0

        try:
            async with aiohttp.ClientSession(timeout=self.stream_timeout) as session:
                async with session.post(
                    f"{self.ollama_host}/api/generate", json=payload
                ) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        raise Exception(
                            f"Ollama streaming error {resp.status}: {text[:200]}"
                        )

                    buffer = ""
                    async for chunk in resp.content.iter_chunks():
                        if chunk:
                            try:
                                data = chunk[0].decode("utf-8")
                                buffer += data
                                lines = buffer.split("\n")
                                buffer = lines.pop()  # keep incomplete line

                                for line in lines:
                                    if not line.strip():
                                        continue
                                    try:
                                        obj = json.loads(line)
                                        token = obj.get("response", "")
                                        if token:
                                            if first_token:
                                                ttft = (time.perf_counter() - t_start) * 1000
                                                logger.debug(
                                                    f"[ollama] first token in {ttft:.0f}ms"
                                                )
                                                first_token = False
                                            token_count += 1
                                            yield token
                                        if obj.get("done", False):
                                            elapsed = (time.perf_counter() - t_start) * 1000
                                            logger.info(
                                                f"[ollama] stream done – {token_count} tokens "
                                                f"in {elapsed:.0f}ms"
                                            )
                                            if obj.get("eval_count") and obj.get("eval_duration"):
                                                tps = obj["eval_count"] / (obj["eval_duration"] / 1e9)
                                                logger.debug(f"[ollama] stream throughput: {tps:.1f} tok/s")
                                            return
                                    except json.JSONDecodeError:
                                        continue
                            except Exception:
                                continue

        except asyncio.TimeoutError:
            elapsed = (time.perf_counter() - t_start) * 1000
            logger.warning(f"[ollama] stream timed out after {elapsed:.0f}ms "
                           f"({token_count} tokens received)")
        except Exception as e:
            elapsed = (time.perf_counter() - t_start) * 1000
            logger.error(f"[ollama] stream error after {elapsed:.0f}ms: {e}")
            raise

    async def health_check(self) -> bool:
        t0 = time.perf_counter()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.ollama_host}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    ok = resp.status == 200
                    elapsed = (time.perf_counter() - t0) * 1000
                    if ok:
                        logger.debug(f"[ollama] health_check OK in {elapsed:.0f}ms")
                    else:
                        logger.warning(f"[ollama] health_check failed: HTTP {resp.status}")
                    return ok
        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            logger.warning(f"[ollama] health_check exception after {elapsed:.0f}ms: {e}")
            return False