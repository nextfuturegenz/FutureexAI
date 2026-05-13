# """
# File: /opt/futureex/exon/core/tool_use.py
# Author: Ashish Pal
# Purpose: Provide tools: calculator (safe), web search (DuckDuckGo), current time, Wikipedia summary.
#          All tools are async, with error handling and fallbacks.
# """

# import asyncio
# import logging
# import re
# from datetime import datetime
# from typing import Dict, Any, Optional
# import redis.asyncio as redis

# # Tool libraries (installed via requirements.txt)
# from duckduckgo_search import DDGS
# import wikipedia
# from simpleeval import simple_eval

# logger = logging.getLogger(__name__)

# class ToolUse:
#     def __init__(self, exon_id: str, redis_client: redis.Redis):
#         self.exon_id = exon_id
#         self.redis = redis_client

#     # ------------------------------------------------------------------
#     # Intent Detection (keyword‑based, can be extended with LLM later)
#     # ------------------------------------------------------------------
#     async def detect_tool_intent(self, user_message: str, response: str = "") -> Optional[Dict]:
#         """Identify which tool (if any) should be invoked based on user message."""
#         msg = user_message.lower()

#         # Calculator
#         if re.search(r'(calculate|math|what is|compute|solve|equals?)', msg) or \
#            re.search(r'[\d\+\-\*\/\(\)]+', msg):
#             expr = self._extract_expression(msg)
#             if expr:
#                 return {"tool": "calculator", "expression": expr}

#         # Web search
#         if re.search(r'(search|google|find online|look up|find information about)', msg):
#             return {"tool": "web_search", "query": user_message}

#         # Current time / date
#         if re.search(r'(time|current time|what time|date|today|what day)', msg):
#             return {"tool": "current_time"}

#         # Wikipedia
#         if re.search(r'(wikipedia|who is|what is a|define|tell me about)', msg):
#             # Extract likely topic: after "who is", "what is", etc.
#             topic = self._extract_wikipedia_topic(user_message)
#             if topic:
#                 return {"tool": "wikipedia", "topic": topic}
#             else:
#                 # Fallback: use whole message as topic (clean)
#                 return {"tool": "wikipedia", "topic": user_message}

#         return None

#     # ------------------------------------------------------------------
#     # Helper: expression extraction for calculator
#     # ------------------------------------------------------------------
#     def _extract_expression(self, text: str) -> str:
#         """Extract a mathematical expression from user message."""
#         # Look for patterns like "calculate 2+2" or "what is 3*4"
#         patterns = [
#             r'calculate\s+([\d\s\+\-\*\/\(\)]+)',
#             r'what is\s+([\d\s\+\-\*\/\(\)]+)',
#             r'math\s+([\d\s\+\-\*\/\(\)]+)',
#             r'solve\s+([\d\s\+\-\*\/\(\)]+)',
#             r'([\d\+\-\*\/\(\)]+)'
#         ]
#         for pat in patterns:
#             match = re.search(pat, text, re.IGNORECASE)
#             if match:
#                 expr = match.group(1).strip()
#                 # Remove any trailing non‑math characters (e.g., punctuation)
#                 expr = re.sub(r'[^0-9+\-*/()\s]', '', expr)
#                 if expr:
#                     return expr
#         return ""

#     # ------------------------------------------------------------------
#     # Helper: extract Wikipedia topic
#     # ------------------------------------------------------------------
#     def _extract_wikipedia_topic(self, message: str) -> Optional[str]:
#         """Extract likely Wikipedia topic from query like "who is Albert Einstein"."""
#         msg = message.lower()
#         patterns = [
#             r'who is\s+(.+)',
#             r'what is\s+(.+)',
#             r'wikipedia\s+(.+)',
#             r'define\s+(.+)',
#             r'tell me about\s+(.+)'
#         ]
#         for pat in patterns:
#             match = re.search(pat, msg, re.IGNORECASE)
#             if match:
#                 topic = match.group(1).strip()
#                 # Remove question words
#                 topic = re.sub(r'(please|\?|\.)$', '', topic).strip()
#                 return topic
#         return None

#     # ------------------------------------------------------------------
#     # Tool Execution (async with thread pools for sync libraries)
#     # ------------------------------------------------------------------
#     async def execute_tool(self, tool_spec: Dict) -> str:
#         """Run the requested tool and return a human‑readable result."""
#         tool = tool_spec.get("tool")
#         try:
#             if tool == "calculator":
#                 expr = tool_spec.get("expression", "")
#                 if not expr:
#                     return "No calculation expression found."
#                 result = await self._safe_calculate(expr)
#                 return f"Calculation result: {result}"

#             elif tool == "web_search":
#                 query = tool_spec.get("query", "")
#                 if not query:
#                     return "No search query provided."
#                 results = await self._web_search(query)
#                 return results

#             elif tool == "current_time":
#                 tz = tool_spec.get("timezone", "local")
#                 return await self._get_current_time(tz)

#             elif tool == "wikipedia":
#                 topic = tool_spec.get("topic", "")
#                 if not topic:
#                     return "No Wikipedia topic provided."
#                 summary = await self._wikipedia_summary(topic)
#                 return summary

#             else:
#                 return f"Tool '{tool}' not recognized."

#         except Exception as e:
#             logger.exception(f"Tool execution error: {e}")
#             return f"Tool error: {str(e)}"

#     # ------------------------------------------------------------------
#     # Individual Tool Implementations (async wrappers)
#     # ------------------------------------------------------------------
#     async def _safe_calculate(self, expression: str) -> str:
#         """Safe calculator using simpleeval (no eval)."""
#         try:
#             # simple_eval handles basic arithmetic, no dangerous functions
#             result = simple_eval(expression)
#             # Format float nicely
#             if isinstance(result, float):
#                 result = round(result, 6)
#             return str(result)
#         except Exception as e:
#             logger.warning(f"Calculator error: {e}")
#             return f"Could not calculate '{expression}': {str(e)}"

#     async def _web_search(self, query: str, max_results: int = 3) -> str:
#         """Search DuckDuckGo and return formatted snippets."""
#         try:
#             # DuckDuckGo search is synchronous – run in thread pool
#             loop = asyncio.get_running_loop()
#             results = await loop.run_in_executor(None, self._sync_ddg_search, query, max_results)
#             if not results:
#                 return f"No results found for '{query}'."
#             formatted = []
#             for r in results:
#                 title = r.get('title', 'No title')
#                 body = r.get('body', '')[:300]
#                 formatted.append(f"• {title}\n  {body}")
#             return f"Search results for '{query}':\n\n" + "\n\n".join(formatted)
#         except Exception as e:
#             logger.error(f"Web search failed: {e}")
#             return f"Web search unavailable: {str(e)}"

#     def _sync_ddg_search(self, query: str, max_results: int) -> list:
#         """Synchronous DuckDuckGo search (runs in thread)."""
#         with DDGS() as ddgs:
#             results = list(ddgs.text(query, max_results=max_results))
#             return results

#     async def _get_current_time(self, timezone: str = "local") -> str:
#         """Return current local time (server time)."""
#         now = datetime.now()
#         return f"Current {timezone} time is {now.strftime('%A, %B %d, %Y at %I:%M %p')}"

#     async def _wikipedia_summary(self, topic: str, sentences: int = 2) -> str:
#         """Fetch a short summary from Wikipedia."""
#         try:
#             loop = asyncio.get_running_loop()
#             summary = await loop.run_in_executor(None, self._sync_wikipedia, topic, sentences)
#             return f"Wikipedia summary for '{topic}':\n{summary}"
#         except wikipedia.exceptions.DisambiguationError as e:
#             options = e.options[:3]
#             return f"'{topic}' is ambiguous. Did you mean: {', '.join(options)} ?"
#         except wikipedia.exceptions.PageError:
#             return f"No Wikipedia page found for '{topic}'."
#         except Exception as e:
#             logger.warning(f"Wikipedia error: {e}")
#             return f"Could not retrieve Wikipedia summary: {str(e)}"

#     def _sync_wikipedia(self, topic: str, sentences: int) -> str:
#         """Synchronous Wikipedia fetch (runs in thread)."""
#         # Set language (English)
#         wikipedia.set_lang("en")
#         return wikipedia.summary(topic, sentences=sentences)

#     # ------------------------------------------------------------------
#     # Tool Result Injection
#     # ------------------------------------------------------------------
#     async def inject_tool_result(self, original_response: str, tool_result: str) -> str:
#         """Insert tool result into the response in a clean way."""
#         # Avoid duplicate injection if tool already used
#         if "[System tool result:" in original_response:
#             return original_response
#         return f"{original_response}\n\n[System tool result: {tool_result}]"


"""
File: /opt/futureex/exon/core/tool_use.py
Author: Ashish Pal
Purpose: Provide tools: calculator, web search (DuckDuckGo Lite), current time, Wikipedia summary.
         Web search uses direct HTTP to DuckDuckGo Lite – no external library, no rate limit issues.
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

    async def detect_tool_intent(self, user_message: str, response: str = "") -> Optional[Dict]:
        msg = user_message.lower()
        # Calculator
        if re.search(r'(calculate|math|what is|compute|solve|equals?)', msg) or re.search(r'[\d\+\-\*\/\(\)]+', msg):
            expr = self._extract_expression(msg)
            if expr:
                return {"tool": "calculator", "expression": expr}
        # Web search
        if re.search(r'(search|google|find online|look up|find information about)', msg):
            return {"tool": "web_search", "query": user_message}
        # Current time
        if re.search(r'(time|current time|what time|date|today|what day)', msg):
            return {"tool": "current_time"}
        # Wikipedia
        if re.search(r'(wikipedia|who is|what is a|define|tell me about)', msg):
            topic = self._extract_wikipedia_topic(user_message)
            if topic:
                return {"tool": "wikipedia", "topic": topic}
            else:
                return {"tool": "wikipedia", "topic": user_message}
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

    async def _safe_calculate(self, expression: str) -> str:
        try:
            result = simple_eval(expression)
            if isinstance(result, float):
                result = round(result, 6)
            return f"Calculation result: {result}"
        except Exception as e:
            return f"Could not calculate '{expression}': {str(e)}"

    async def _web_search(self, query: str, max_results: int = 3) -> str:
        """Search DuckDuckGo using the lite (text) version."""
        try:
            url = "https://lite.duckduckgo.com/lite/"
            params = {"q": query}
            session = await self._get_session()
            async with session.get(url, params=params, timeout=15) as resp:
                if resp.status != 200:
                    return f"Search failed with status {resp.status}"
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                results = []
                # DuckDuckGo Lite uses tables: each result is in a <tr class="result-snippet">
                for snippet_row in soup.find_all('tr', class_='result-snippet'):
                    link_row = snippet_row.find_previous_sibling('tr', class_='result-link')
                    if not link_row:
                        continue
                    link_tag = link_row.find('a')
                    if not link_tag:
                        continue
                    title = link_tag.get_text(strip=True)
                    url = link_tag.get('href')
                    snippet = snippet_row.get_text(strip=True)
                    results.append({"title": title, "snippet": snippet, "url": url})
                    if len(results) >= max_results:
                        break
                if not results:
                    return f"No results found for '{query}'."
                formatted = []
                for r in results:
                    formatted.append(f"• {r['title']}\n  {r['snippet'][:300]}")
                return f"Search results for '{query}':\n\n" + "\n\n".join(formatted)
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return f"Web search unavailable: {str(e)}"

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
        if "[System tool result:" in original_response:
            return original_response
        return f"{original_response}\n\n[System tool result: {tool_result}]"

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()