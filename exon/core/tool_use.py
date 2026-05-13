"""
File: /opt/futureex/exon/core/tool_use.py
Author: Ashish Pal
Purpose: Tools: calculator, web search (Brave Search API), time, Wikipedia.
Refactored: Fixed calculator detection, switched to Brave Search.
"""

import asyncio
import logging
import re
import random
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
import redis.asyncio as redis
import aiohttp
from simpleeval import simple_eval
import wikipedia

logger = logging.getLogger(__name__)

# Brave Search API free tier (2,000 queries/month)
BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY", "")
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"

class ToolUse:
    def __init__(self, exon_id: str, redis_client: redis.Redis):
        self.exon_id = exon_id
        self.redis = redis_client
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            headers = {"Accept": "application/json"}
            if BRAVE_API_KEY:
                headers["X-Subscription-Token"] = BRAVE_API_KEY
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session

    async def detect_tool_intent(self, user_message: str, response: str = "") -> Optional[Dict]:
        msg = user_message.lower()

        # Calculator: only trigger if there is a digit AND an operator, or explicit "calculate"
        calc_words = ["calculate", "compute", "solve", "math"]
        if any(w in msg for w in calc_words) or re.search(r'[\d]+\s*[\+\-\*\/]\s*[\d]+', msg):
            expr = self._extract_expression(user_message)
            if expr:
                return {"tool": "calculator", "expression": expr}

        # Web search
        search_match = re.search(r'(?:search|google|find|look up|tell me about)\s+(?:for\s+)?(.+)', msg, re.IGNORECASE)
        if search_match:
            query = search_match.group(1).strip()
            query = re.sub(r'[.?!]+$', '', query)
            if query:
                return {"tool": "web_search", "query": query}
        # Factual question pattern (but not captured by local knowledge)
        if re.match(r'^(what|who|where|when|how)\s+', msg) and len(msg.split()) > 3:
            return {"tool": "web_search", "query": user_message}

        # Current time
        if re.search(r'(time|current time|what time|date|today|what day)', msg):
            return {"tool": "current_time"}

        # Wikipedia
        if re.search(r'(wikipedia|who is|what is a|define|tell me about)', msg):
            topic = self._extract_wikipedia_topic(user_message)
            if topic:
                return {"tool": "wikipedia", "topic": topic}

        return None

    def _extract_expression(self, text: str) -> Optional[str]:
        """Extract a mathematical expression from text."""
        # Look for patterns like "calculate 15 * 3", "what is 2+2", or any arithmetic with digits
        patterns = [
            r'calculate\s+([\d\s\+\-\*\/\(\)\.]+)',
            r'what is\s+([\d\s\+\-\*\/\(\)\.]+)',
            r'math\s+([\d\s\+\-\*\/\(\)\.]+)',
            r'solve\s+([\d\s\+\-\*\/\(\)\.]+)',
            r'compute\s+([\d\s\+\-\*\/\(\)\.]+)',
            # general arithmetic: digits with at least one operator
            r'([\d\.]+\s*[\+\-\*\/]\s*[\d\.]+(?:\s*[\+\-\*\/]\s*[\d\.]+)*)',
        ]
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                expr = match.group(1).strip()
                # Remove any non-math characters except digits, operators, spaces, parens, decimal
                expr = re.sub(r'[^0-9+\-*/()\s.]', '', expr)
                # Ensure it contains at least one digit and one operator
                if re.search(r'\d', expr) and re.search(r'[\+\-\*/]', expr):
                    return expr
        return None

    def _extract_wikipedia_topic(self, message: str) -> Optional[str]:
        msg = message.lower()
        patterns = [
            r'who is\s+(.+)',
            r'what is\s+(.+)',
            r'wikipedia\s+(.+)',
            r'define\s+(.+)',
            r'tell me about\s+(.+)'
        ]
        for pat in patterns:
            match = re.search(pat, msg, re.IGNORECASE)
            if match:
                topic = match.group(1).strip()
                topic = re.sub(r'(please|\?|\.)$', '', topic).strip()
                return topic
        return None

    async def execute_tool(self, tool_spec: Dict) -> str:
        tool = tool_spec.get("tool")
        try:
            if tool == "calculator":
                expr = tool_spec.get("expression", "")
                if not expr:
                    return "No calculation expression found."
                return await self._safe_calculate(expr)
            elif tool == "web_search":
                query = tool_spec.get("query", "")
                if not query:
                    return "No search query provided."
                return await self._web_search_brave(query)
            elif tool == "current_time":
                return await self._get_current_time()
            elif tool == "wikipedia":
                topic = tool_spec.get("topic", "")
                if not topic:
                    return "No Wikipedia topic provided."
                return await self._wikipedia_summary(topic)
            else:
                return f"Tool '{tool}' not recognized."
        except Exception as e:
            logger.exception(f"Tool execution error: {e}")
            return f"Tool error: {str(e)}"

    async def _safe_calculate(self, expression: str) -> str:
        try:
            result = simple_eval(expression)
            if isinstance(result, float):
                result = round(result, 6)
            return f"Calculation result: {result}"
        except Exception as e:
            return f"Could not calculate '{expression}': {str(e)}"

    async def _web_search_brave(self, query: str, max_results: int = 3) -> str:
        """Brave Search API (free tier)."""
        if not BRAVE_API_KEY:
            logger.warning("No BRAVE_API_KEY set; falling back to dummy response")
            return f"(Brave Search not configured. Please set BRAVE_API_KEY.)"

        session = await self._get_session()
        params = {"q": query, "count": max_results}
        try:
            async with session.get(BRAVE_SEARCH_URL, params=params, timeout=15) as resp:
                if resp.status != 200:
                    logger.error(f"Brave Search error {resp.status}: {await resp.text()}")
                    return f"Search failed (status {resp.status})."
                data = await resp.json()
                web_results = data.get("web", {}).get("results", [])
                if not web_results:
                    return f"No results found for '{query}'."
                formatted = []
                for r in web_results[:max_results]:
                    title = r.get("title", "")
                    description = r.get("description", "")
                    url = r.get("url", "")
                    formatted.append(f"• {title}\n  {description[:300]}\n  {url}")
                return f"Search results for '{query}':\n\n" + "\n\n".join(formatted)
        except Exception as e:
            logger.error(f"Brave search exception: {e}")
            return f"Search error: {str(e)}"

    async def _get_current_time(self) -> str:
        now = datetime.now()
        return f"Current local time is {now.strftime('%A, %B %d, %Y at %I:%M %p')}"

    async def _wikipedia_summary(self, topic: str, sentences: int = 2) -> str:
        try:
            loop = asyncio.get_running_loop()
            summary = await loop.run_in_executor(None, self._sync_wikipedia, topic, sentences)
            return f"Wikipedia summary for '{topic}':\n{summary}"
        except wikipedia.exceptions.DisambiguationError as e:
            options = e.options[:3]
            return f"'{topic}' is ambiguous. Did you mean: {', '.join(options)} ?"
        except wikipedia.exceptions.PageError:
            return f"No Wikipedia page found for '{topic}'."
        except Exception as e:
            return f"Could not retrieve Wikipedia summary: {str(e)}"

    def _sync_wikipedia(self, topic: str, sentences: int) -> str:
        wikipedia.set_lang("en")
        return wikipedia.summary(topic, sentences=sentences)

    async def inject_tool_result(self, original_response: str, tool_result: str) -> str:
        if not tool_result or tool_result.startswith("Tool error"):
            return original_response
        # Avoid duplication
        if "[System tool result:" in original_response:
            return original_response
        return f"{original_response}\n\n{tool_result}"

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()