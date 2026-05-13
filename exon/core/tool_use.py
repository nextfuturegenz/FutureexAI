"""
File: /opt/futureex/exon/core/tool_use.py
Author: Ashish Pal
Purpose: Tools: calculator, web search (main DuckDuckGo HTML + suggestions), time, Wikipedia.
"""

import asyncio
import logging
import re
import random
from datetime import datetime
from typing import Dict, Any, Optional, List
import redis.asyncio as redis
import aiohttp
from bs4 import BeautifulSoup
from simpleeval import simple_eval
import wikipedia

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

class ToolUse:
    def __init__(self, exon_id: str, redis_client: redis.Redis):
        self.exon_id = exon_id
        self.redis = redis_client
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session

    async def detect_tool_intent(self, user_message: str, response: str = "") -> Optional[Dict]:
        msg = user_message.lower()
        # Calculator
        if re.search(r'(calculate|math|what is|compute|solve)', msg) or re.search(r'[\d\+\-\*\/\(\)]{3,}', msg):
            expr = self._extract_expression(msg)
            if expr:
                return {"tool": "calculator", "expression": expr}
        # Web search – extract clean query
        search_match = re.search(r'(?:search|google|find|look up|tell me about)\s+(?:for\s+)?(.+)', msg, re.IGNORECASE)
        if search_match:
            query = search_match.group(1).strip()
            query = re.sub(r'[.?!]+$', '', query)
            if query:
                return {"tool": "web_search", "query": query}
        # Also if user asks a plain factual question
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
                result = await self._web_search(query)
                if "No results found" in result:
                    # Also get suggestions
                    suggestions = await self._get_search_suggestions(query)
                    if suggestions:
                        result += f"\n\nTry these alternative searches:\n• " + "\n• ".join(suggestions[:3])
                return result
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

    async def _web_search(self, query: str, max_results: int = 3) -> str:
        """Search DuckDuckGo main HTML (more robust)."""
        for attempt in range(2):
            try:
                url = "https://html.duckduckgo.com/html/"
                params = {"q": query}
                session = await self._get_session()
                async with session.get(url, params=params, timeout=15) as resp:
                    if resp.status == 200:
                        html = await resp.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        results = []
                        # Main results are in <a class="result__a">
                        for result_link in soup.select('a.result__a'):
                            title = result_link.get_text(strip=True)
                            # Find parent .result__snippet
                            snippet_tag = result_link.find_parent('div', class_='result')
                            if snippet_tag:
                                snippet_div = snippet_tag.find('a', class_='result__snippet')
                            else:
                                snippet_div = None
                            snippet = snippet_div.get_text(strip=True) if snippet_div else ""
                            results.append({"title": title, "snippet": snippet})
                            if len(results) >= max_results:
                                break
                        if results:
                            formatted = [f"• {r['title']}\n  {r['snippet'][:300]}" for r in results]
                            return f"Search results for '{query}':\n\n" + "\n\n".join(formatted)
                        else:
                            await asyncio.sleep(1)
                            continue
                    else:
                        logger.warning(f"HTTP {resp.status} for {query}")
                        await asyncio.sleep(1)
            except Exception as e:
                logger.warning(f"Search attempt {attempt+1} failed: {e}")
                await asyncio.sleep(1)
        return f"No results found for '{query}'."

    async def _get_search_suggestions(self, query: str) -> List[str]:
        """Get related search suggestions from DuckDuckGo's suggestions API."""
        try:
            url = f"https://duckduckgo.com/ac/?q={query}&type=list"
            session = await self._get_session()
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Format: [{"phrase": "suggestion1"}, ...]
                    suggestions = [item['phrase'] for item in data if 'phrase' in item]
                    return suggestions[:5]
        except Exception as e:
            logger.debug(f"Suggestions failed: {e}")
        return []

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
        """Cleaner injection – only if tool result is meaningful and different from original."""
        if not tool_result or tool_result.startswith("Tool error"):
            # Do not inject error messages that break conversation
            return original_response
        # Avoid duplication
        if "[System tool result:" in original_response:
            return original_response
        # Append on a new line
        return f"{original_response}\n\n{tool_result}"

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()