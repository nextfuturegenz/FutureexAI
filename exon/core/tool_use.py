"""
File: /opt/futureex/exon/core/tool_use.py
Author: Ashish Pal
Purpose: Tools: calculator, web search (DuckDuckGo + fallback), time, Wikipedia.
         Extracts search query from natural language.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional
import redis.asyncio as redis
import aiohttp
from bs4 import BeautifulSoup
from simpleeval import simple_eval
import wikipedia

logger = logging.getLogger(__name__)

class ToolUse:
    def __init__(self, exon_id: str, redis_client: redis.Redis):
        self.exon_id = exon_id
        self.redis = redis_client
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            )
        return self._session

    # ------------------------------------------------------------------
    # Intent detection (with better query extraction)
    # ------------------------------------------------------------------
    async def detect_tool_intent(self, user_message: str, response: str = "") -> Optional[Dict]:
        msg = user_message.lower()
        # Calculator
        if re.search(r'(calculate|math|what is|compute|solve|equals?)', msg) or re.search(r'[\d\+\-\*\/\(\)]+', msg):
            expr = self._extract_expression(msg)
            if expr:
                return {"tool": "calculator", "expression": expr}
        # Web search (extract clean query)
        search_match = re.search(r'(?:search|google|find|look up|tell me about)\s+(?:for\s+)?(.+)', msg, re.IGNORECASE)
        if search_match:
            query = search_match.group(1).strip()
            # Remove any trailing punctuation
            query = re.sub(r'[.?!]+$', '', query)
            if query:
                return {"tool": "web_search", "query": query}
        # Also if user just asks a plain question without keyword, we could still search, but only if it's a clear fact question
        if re.match(r'^(what|who|where|when|how)\s+', msg) and len(msg.split()) > 3:
            # Convert whole message to query
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

    def _extract_expression(self, text: str) -> str:
        patterns = [
            r'calculate\s+([\d\s\+\-\*\/\(\)]+)',
            r'what is\s+([\d\s\+\-\*\/\(\)]+)',
            r'math\s+([\d\s\+\-\*\/\(\)]+)',
            r'solve\s+([\d\s\+\-\*\/\(\)]+)',
            r'([\d\+\-\*\/\(\)]+)'
        ]
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                expr = match.group(1).strip()
                expr = re.sub(r'[^0-9+\-*/()\s]', '', expr)
                if expr:
                    return expr
        return ""

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

    # ------------------------------------------------------------------
    # Tool execution
    # ------------------------------------------------------------------
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
                return await self._web_search(query)
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

    # ------------------------------------------------------------------
    # Calculator (safe)
    # ------------------------------------------------------------------
    async def _safe_calculate(self, expression: str) -> str:
        try:
            result = simple_eval(expression)
            if isinstance(result, float):
                result = round(result, 6)
            return f"Calculation result: {result}"
        except Exception as e:
            return f"Could not calculate '{expression}': {str(e)}"

    # ------------------------------------------------------------------
    # Web search (DuckDuckGo Lite with retries & fallback to direct HTML)
    # ------------------------------------------------------------------
    async def _web_search(self, query: str, max_results: int = 3) -> str:
        """Search DuckDuckGo using the lite version with retry."""
        # First try: use the same lite endpoint but with proper query encoding
        for attempt in range(2):
            try:
                url = "https://lite.duckduckgo.com/lite/"
                params = {"q": query}
                session = await self._get_session()
                async with session.get(url, params=params, timeout=15) as resp:
                    if resp.status == 200:
                        html = await resp.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        results = []
                        for snippet_row in soup.find_all('tr', class_='result-snippet'):
                            link_row = snippet_row.find_previous_sibling('tr', class_='result-link')
                            if not link_row:
                                continue
                            link_tag = link_row.find('a')
                            if not link_tag:
                                continue
                            title = link_tag.get_text(strip=True)
                            snippet = snippet_row.get_text(strip=True)
                            results.append({"title": title, "snippet": snippet})
                            if len(results) >= max_results:
                                break
                        if results:
                            formatted = [f"• {r['title']}\n  {r['snippet'][:300]}" for r in results]
                            return f"Search results for '{query}':\n\n" + "\n\n".join(formatted)
                        else:
                            # No results, maybe try again with a different approach
                            if attempt == 0:
                                await asyncio.sleep(1)
                                continue
                            return f"No results found for '{query}'. Try a different search term."
            except Exception as e:
                logger.warning(f"Search attempt {attempt+1} failed: {e}")
                await asyncio.sleep(1)
        return f"Web search temporarily unavailable. Please try again later."

    # ------------------------------------------------------------------
    # Time and Wikipedia
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Result injection
    # ------------------------------------------------------------------
    async def inject_tool_result(self, original_response: str, tool_result: str) -> str:
        if "[System tool result:" in original_response:
            return original_response
        return f"{original_response}\n\n[System tool result: {tool_result}]"

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()