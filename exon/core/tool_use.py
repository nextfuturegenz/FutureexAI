# # """
# # File: /opt/futureex/exon/core/tool_use.py
# # Author: Ashish Pal
# # Purpose: Tools: calculator, web search (Brave Search API), time, Wikipedia.
# # Refactored: Fixed calculator detection, switched to Brave Search.
# # """

# # import asyncio
# # import logging
# # import re
# # import random
# # import os
# # from datetime import datetime
# # from typing import Dict, Any, Optional, List
# # import redis.asyncio as redis
# # import aiohttp
# # from simpleeval import simple_eval
# # import wikipedia

# # logger = logging.getLogger(__name__)

# # # Brave Search API free tier (2,000 queries/month)
# # BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY", "")
# # BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"

# # class ToolUse:
# #     def __init__(self, exon_id: str, redis_client: redis.Redis):
# #         self.exon_id = exon_id
# #         self.redis = redis_client
# #         self._session: Optional[aiohttp.ClientSession] = None

# #     async def _get_session(self) -> aiohttp.ClientSession:
# #         if self._session is None or self._session.closed:
# #             headers = {"Accept": "application/json"}
# #             if BRAVE_API_KEY:
# #                 headers["X-Subscription-Token"] = BRAVE_API_KEY
# #             self._session = aiohttp.ClientSession(headers=headers)
# #         return self._session

# #     async def detect_tool_intent(self, user_message: str, response: str = "") -> Optional[Dict]:
# #         msg = user_message.lower()

# #         # Calculator: only trigger if there is a digit AND an operator, or explicit "calculate"
# #         calc_words = ["calculate", "compute", "solve", "math"]
# #         if any(w in msg for w in calc_words) or re.search(r'[\d]+\s*[\+\-\*\/]\s*[\d]+', msg):
# #             expr = self._extract_expression(user_message)
# #             if expr:
# #                 return {"tool": "calculator", "expression": expr}

# #         # Web search
# #         search_match = re.search(r'(?:search|google|find|look up|tell me about)\s+(?:for\s+)?(.+)', msg, re.IGNORECASE)
# #         if search_match:
# #             query = search_match.group(1).strip()
# #             query = re.sub(r'[.?!]+$', '', query)
# #             if query:
# #                 return {"tool": "web_search", "query": query}
# #         # Factual question pattern (but not captured by local knowledge)
# #         if re.match(r'^(what|who|where|when|how)\s+', msg) and len(msg.split()) > 3:
# #             return {"tool": "web_search", "query": user_message}

# #         # Current time
# #         if re.search(r'(time|current time|what time|date|today|what day)', msg):
# #             return {"tool": "current_time"}

# #         # Wikipedia
# #         if re.search(r'(wikipedia|who is|what is a|define|tell me about)', msg):
# #             topic = self._extract_wikipedia_topic(user_message)
# #             if topic:
# #                 return {"tool": "wikipedia", "topic": topic}

# #         return None

# #     def _extract_expression(self, text: str) -> Optional[str]:
# #         """Extract a mathematical expression from text."""
# #         # Look for patterns like "calculate 15 * 3", "what is 2+2", or any arithmetic with digits
# #         patterns = [
# #             r'calculate\s+([\d\s\+\-\*\/\(\)\.]+)',
# #             r'what is\s+([\d\s\+\-\*\/\(\)\.]+)',
# #             r'math\s+([\d\s\+\-\*\/\(\)\.]+)',
# #             r'solve\s+([\d\s\+\-\*\/\(\)\.]+)',
# #             r'compute\s+([\d\s\+\-\*\/\(\)\.]+)',
# #             # general arithmetic: digits with at least one operator
# #             r'([\d\.]+\s*[\+\-\*\/]\s*[\d\.]+(?:\s*[\+\-\*\/]\s*[\d\.]+)*)',
# #         ]
# #         for pat in patterns:
# #             match = re.search(pat, text, re.IGNORECASE)
# #             if match:
# #                 expr = match.group(1).strip()
# #                 # Remove any non-math characters except digits, operators, spaces, parens, decimal
# #                 expr = re.sub(r'[^0-9+\-*/()\s.]', '', expr)
# #                 # Ensure it contains at least one digit and one operator
# #                 if re.search(r'\d', expr) and re.search(r'[\+\-\*/]', expr):
# #                     return expr
# #         return None

# #     def _extract_wikipedia_topic(self, message: str) -> Optional[str]:
# #         msg = message.lower()
# #         patterns = [
# #             r'who is\s+(.+)',
# #             r'what is\s+(.+)',
# #             r'wikipedia\s+(.+)',
# #             r'define\s+(.+)',
# #             r'tell me about\s+(.+)'
# #         ]
# #         for pat in patterns:
# #             match = re.search(pat, msg, re.IGNORECASE)
# #             if match:
# #                 topic = match.group(1).strip()
# #                 topic = re.sub(r'(please|\?|\.)$', '', topic).strip()
# #                 return topic
# #         return None

# #     async def execute_tool(self, tool_spec: Dict) -> str:
# #         tool = tool_spec.get("tool")
# #         try:
# #             if tool == "calculator":
# #                 expr = tool_spec.get("expression", "")
# #                 if not expr:
# #                     return "No calculation expression found."
# #                 return await self._safe_calculate(expr)
# #             elif tool == "web_search":
# #                 query = tool_spec.get("query", "")
# #                 if not query:
# #                     return "No search query provided."
# #                 return await self._web_search_brave(query)
# #             elif tool == "current_time":
# #                 return await self._get_current_time()
# #             elif tool == "wikipedia":
# #                 topic = tool_spec.get("topic", "")
# #                 if not topic:
# #                     return "No Wikipedia topic provided."
# #                 return await self._wikipedia_summary(topic)
# #             else:
# #                 return f"Tool '{tool}' not recognized."
# #         except Exception as e:
# #             logger.exception(f"Tool execution error: {e}")
# #             return f"Tool error: {str(e)}"

# #     async def _safe_calculate(self, expression: str) -> str:
# #         try:
# #             result = simple_eval(expression)
# #             if isinstance(result, float):
# #                 result = round(result, 6)
# #             return f"Calculation result: {result}"
# #         except Exception as e:
# #             return f"Could not calculate '{expression}': {str(e)}"

# #     async def _web_search_brave(self, query: str, max_results: int = 3) -> str:
# #         """Brave Search API (free tier)."""
# #         if not BRAVE_API_KEY:
# #             logger.warning("No BRAVE_API_KEY set; falling back to dummy response")
# #             return f"(Brave Search not configured. Please set BRAVE_API_KEY.)"

# #         session = await self._get_session()
# #         params = {"q": query, "count": max_results}
# #         try:
# #             async with session.get(BRAVE_SEARCH_URL, params=params, timeout=15) as resp:
# #                 if resp.status != 200:
# #                     logger.error(f"Brave Search error {resp.status}: {await resp.text()}")
# #                     return f"Search failed (status {resp.status})."
# #                 data = await resp.json()
# #                 web_results = data.get("web", {}).get("results", [])
# #                 if not web_results:
# #                     return f"No results found for '{query}'."
# #                 formatted = []
# #                 for r in web_results[:max_results]:
# #                     title = r.get("title", "")
# #                     description = r.get("description", "")
# #                     url = r.get("url", "")
# #                     formatted.append(f"• {title}\n  {description[:300]}\n  {url}")
# #                 return f"Search results for '{query}':\n\n" + "\n\n".join(formatted)
# #         except Exception as e:
# #             logger.error(f"Brave search exception: {e}")
# #             return f"Search error: {str(e)}"

# #     async def _get_current_time(self) -> str:
# #         now = datetime.now()
# #         return f"Current local time is {now.strftime('%A, %B %d, %Y at %I:%M %p')}"

# #     async def _wikipedia_summary(self, topic: str, sentences: int = 2) -> str:
# #         try:
# #             loop = asyncio.get_running_loop()
# #             summary = await loop.run_in_executor(None, self._sync_wikipedia, topic, sentences)
# #             return f"Wikipedia summary for '{topic}':\n{summary}"
# #         except wikipedia.exceptions.DisambiguationError as e:
# #             options = e.options[:3]
# #             return f"'{topic}' is ambiguous. Did you mean: {', '.join(options)} ?"
# #         except wikipedia.exceptions.PageError:
# #             return f"No Wikipedia page found for '{topic}'."
# #         except Exception as e:
# #             return f"Could not retrieve Wikipedia summary: {str(e)}"

# #     def _sync_wikipedia(self, topic: str, sentences: int) -> str:
# #         wikipedia.set_lang("en")
# #         return wikipedia.summary(topic, sentences=sentences)

# #     async def inject_tool_result(self, original_response: str, tool_result: str) -> str:
# #         if not tool_result or tool_result.startswith("Tool error"):
# #             return original_response
# #         # Avoid duplication
# #         if "[System tool result:" in original_response:
# #             return original_response
# #         return f"{original_response}\n\n{tool_result}"

# #     async def close(self):
# #         if self._session and not self._session.closed:
# #             await self._session.close()


# """
# File: /opt/futureex/exon/core/tool_use.py
# Author: Ashish Pal
# Purpose: Tools: calculator, web search (duckduckgo_search DDGS library), time, Wikipedia.
# Refactored: Fixed calculator detection, switched from Brave/DDG HTML scraping to duckduckgo_search.
# """

# import asyncio
# import logging
# import re
# from datetime import datetime
# from typing import Dict, Any, Optional, List
# import redis.asyncio as redis
# from simpleeval import simple_eval
# import wikipedia
# from duckduckgo_search import DDGS

# logger = logging.getLogger(__name__)


# class ToolUse:
#     def __init__(self, exon_id: str, redis_client: redis.Redis):
#         self.exon_id = exon_id
#         self.redis = redis_client

#     # ------------------------------------------------------------------
#     # Detection
#     # ------------------------------------------------------------------
#     async def detect_tool_intent(self, user_message: str, response: str = "") -> Optional[Dict]:
#         msg = user_message.lower()

#         # --- Calculator: only trigger if digits + operator present, or explicit "calculate" ---
#         calc_words = ["calculate", "compute", "solve", "math"]
#         if any(w in msg for w in calc_words) or re.search(r'[\d]+\s*[\+\-\*\/]\s*[\d]+', msg):
#             expr = self._extract_expression(user_message)
#             if expr:
#                 return {"tool": "calculator", "expression": expr}

#         # --- Web search ---
#         search_match = re.search(
#             r'(?:search|google|find|look up|tell me about)\s+(?:for\s+)?(.+)',
#             msg, re.IGNORECASE
#         )
#         if search_match:
#             query = search_match.group(1).strip().rstrip('?!.')
#             if query:
#                 return {"tool": "web_search", "query": query}
#         # Factual question pattern
#         if re.match(r'^(what|who|where|when|how)\s+', msg) and len(msg.split()) > 3:
#             return {"tool": "web_search", "query": user_message}

#         # --- Current time ---
#         if re.search(r'(time|current time|what time|date|today|what day)', msg):
#             return {"tool": "current_time"}

#         # --- Wikipedia ---
#         if re.search(r'(wikipedia|who is|what is a|define|tell me about)', msg):
#             topic = self._extract_wikipedia_topic(user_message)
#             if topic:
#                 return {"tool": "wikipedia", "topic": topic}

#         return None

#     def _extract_expression(self, text: str) -> Optional[str]:
#         """Extract a mathematical expression from text."""
#         patterns = [
#             r'calculate\s+([\d\s\+\-\*\/\(\)\.]+)',
#             r'what is\s+([\d\s\+\-\*\/\(\)\.]+)',
#             r'math\s+([\d\s\+\-\*\/\(\)\.]+)',
#             r'solve\s+([\d\s\+\-\*\/\(\)\.]+)',
#             r'compute\s+([\d\s\+\-\*\/\(\)\.]+)',
#             r'([\d\.]+\s*[\+\-\*\/]\s*[\d\.]+(?:\s*[\+\-\*\/]\s*[\d\.]+)*)',
#         ]
#         for pat in patterns:
#             match = re.search(pat, text, re.IGNORECASE)
#             if match:
#                 expr = match.group(1).strip()
#                 expr = re.sub(r'[^0-9+\-*/()\s.]', '', expr)
#                 if re.search(r'\d', expr) and re.search(r'[\+\-\*/]', expr):
#                     return expr
#         return None

#     def _extract_wikipedia_topic(self, message: str) -> Optional[str]:
#         msg = message.lower()
#         patterns = [
#             r'who is\s+(.+)',
#             r'what is\s+(.+)',
#             r'wikipedia\s+(.+)',
#             r'define\s+(.+)',
#             r'tell me about\s+(.+)',
#         ]
#         for pat in patterns:
#             match = re.search(pat, msg, re.IGNORECASE)
#             if match:
#                 topic = match.group(1).strip().rstrip('?!.')
#                 return topic
#         return None

#     # ------------------------------------------------------------------
#     # Execution
#     # ------------------------------------------------------------------
#     async def execute_tool(self, tool_spec: Dict) -> str:
#         tool = tool_spec.get("tool")
#         try:
#             if tool == "calculator":
#                 expr = tool_spec.get("expression", "")
#                 if not expr:
#                     return "No calculation expression found."
#                 return await self._safe_calculate(expr)
#             elif tool == "web_search":
#                 query = tool_spec.get("query", "")
#                 if not query:
#                     return "No search query provided."
#                 return await self._web_search_ddg(query)
#             elif tool == "current_time":
#                 return await self._get_current_time()
#             elif tool == "wikipedia":
#                 topic = tool_spec.get("topic", "")
#                 if not topic:
#                     return "No Wikipedia topic provided."
#                 return await self._wikipedia_summary(topic)
#             else:
#                 return f"Tool '{tool}' not recognized."
#         except Exception as e:
#             logger.exception(f"Tool execution error: {e}")
#             return f"Tool error: {str(e)}"

#     async def _safe_calculate(self, expression: str) -> str:
#         try:
#             result = simple_eval(expression)
#             if isinstance(result, float):
#                 result = round(result, 6)
#             return f"Calculation result: {result}"
#         except Exception as e:
#             return f"Could not calculate '{expression}': {str(e)}"

#     async def _web_search_ddg(self, query: str, max_results: int = 3) -> str:
#         """
#         Use the duckduckgo_search library (DDGS class) for free, no‑API‑key web search.
#         Runs synchronously in a thread executor to avoid blocking the async loop.
#         """
#         loop = asyncio.get_running_loop()
#         try:
#             results = await loop.run_in_executor(
#                 None,
#                 lambda: DDGS().text(query, region="us-en", safesearch="moderate", max_results=max_results)
#             )
#         except Exception as e:
#             logger.error(f"DDGS search failed: {e}")
#             return f"Search failed: {str(e)}"

#         if not results:
#             return f"No results found for '{query}'."

#         formatted = []
#         for r in results[:max_results]:
#             title = r.get("title", "")
#             body = r.get("body", "")[:300]
#             href = r.get("href", "")
#             formatted.append(f"• {title}\n  {body}\n  {href}")

#         return f"Search results for '{query}':\n\n" + "\n\n".join(formatted)

#     async def _get_current_time(self) -> str:
#         now = datetime.now()
#         return f"Current local time is {now.strftime('%A, %B %d, %Y at %I:%M %p')}"

#     async def _wikipedia_summary(self, topic: str, sentences: int = 2) -> str:
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
#             return f"Could not retrieve Wikipedia summary: {str(e)}"

#     def _sync_wikipedia(self, topic: str, sentences: int) -> str:
#         wikipedia.set_lang("en")
#         return wikipedia.summary(topic, sentences=sentences)

#     # ------------------------------------------------------------------
#     # Injection
#     # ------------------------------------------------------------------
#     async def inject_tool_result(self, original_response: str, tool_result: str) -> str:
#         if not tool_result or tool_result.startswith("Tool error"):
#             return original_response
#         if "[System tool result:" in original_response:
#             return original_response
#         return f"{original_response}\n\n{tool_result}"

"""
File: /opt/futureex/exon/core/tool_use.py
Author: Ashish Pal
Purpose: Tools: calculator, web search (DDGS → Playwright fallback), time, Wikipedia.
Refactored: DDGS library with headless Chromium fallback via Playwright.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
import redis.asyncio as redis
from simpleeval import simple_eval
import wikipedia
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


class ToolUse:
    def __init__(self, exon_id: str, redis_client: redis.Redis):
        self.exon_id = exon_id
        self.redis = redis_client
        self._web_browser = None  # Lazy loaded

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------
    async def detect_tool_intent(self, user_message: str, response: str = "") -> Optional[Dict]:
        msg = user_message.lower()

            # Skip web search for emotional/greeting questions
        emotional_patterns = [
            r'how are you',
            r'how do you feel',
            r'how is your day',
            r'what\'s up',
            r'how are things',
        ]
        for pattern in emotional_patterns:
            if re.search(pattern, msg):
                return None  # Don't trigger any tool for these

        # --- Calculator ---
        calc_words = ["calculate", "compute", "solve", "math"]
        if any(w in msg for w in calc_words) or re.search(r'[\d]+\s*[\+\-\*\/]\s*[\d]+', msg):
            expr = self._extract_expression(user_message)
            if expr:
                return {"tool": "calculator", "expression": expr}

        # --- Web search ---
        search_match = re.search(
            r'(?:search|google|find|look up)\s+(?:for\s+)?(.+)',
            msg, re.IGNORECASE
        )
        if search_match:
            query = search_match.group(1).strip().rstrip('?!.')
            if query:
                return {"tool": "web_search", "query": query}
        # Factual question pattern (but not "tell me about" which RAG handles)
        if re.match(r'^(what|who|where|when|how)\s+', msg) and len(msg.split()) > 3:
            return {"tool": "web_search", "query": user_message}
        # Explicit "tell me about" only triggers if RAG is empty (handled in brain.py)
        if re.search(r'(tell me about)\s+(.+)', msg, re.IGNORECASE):
            topic = re.search(r'tell me about\s+(.+)', msg, re.IGNORECASE).group(1).strip()
            if topic and len(topic.split()) <= 3:  # Short topics go to web search
                return {"tool": "web_search", "query": topic}

        # --- Current time ---
        if re.search(r'(time|current time|what time|date|today|what day)', msg):
            return {"tool": "current_time"}

        # --- Wikipedia ---
        if re.search(r'(wikipedia|define)', msg):
            topic = self._extract_wikipedia_topic(user_message)
            if topic:
                return {"tool": "wikipedia", "topic": topic}

        return None

    def _extract_expression(self, text: str) -> Optional[str]:
        """Extract a mathematical expression from text."""
        patterns = [
            r'calculate\s+([\d\s\+\-\*\/\(\)\.]+)',
            r'what is\s+([\d\s\+\-\*\/\(\)\.]+)',
            r'math\s+([\d\s\+\-\*\/\(\)\.]+)',
            r'solve\s+([\d\s\+\-\*\/\(\)\.]+)',
            r'compute\s+([\d\s\+\-\*\/\(\)\.]+)',
            r'([\d\.]+\s*[\+\-\*\/]\s*[\d\.]+(?:\s*[\+\-\*\/]\s*[\d\.]+)*)',
        ]
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                expr = match.group(1).strip()
                expr = re.sub(r'[^0-9+\-*/()\s.]', '', expr)
                if re.search(r'\d', expr) and re.search(r'[\+\-\*/]', expr):
                    return expr
        return None

    def _extract_wikipedia_topic(self, message: str) -> Optional[str]:
        msg = message.lower()
        patterns = [
            r'who is\s+(.+)',
            r'what is a\s+(.+)',
            r'wikipedia\s+(.+)',
            r'define\s+(.+)',
        ]
        for pat in patterns:
            match = re.search(pat, msg, re.IGNORECASE)
            if match:
                topic = match.group(1).strip().rstrip('?!.')
                return topic
        return None

    # ------------------------------------------------------------------
    # Execution
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
                return await self._web_search_with_fallback(query)
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

    # ------------------------------------------------------------------
    # Web Search - DDGS first, Playwright fallback
    # ------------------------------------------------------------------
    async def _web_search_with_fallback(self, query: str, max_results: int = 3) -> str:
        """Try DDGS first, fall back to headless browser if rate-limited."""
        
        # 1. Try DDGS library
        result = await self._web_search_ddg(query, max_results)
        if result and "Ratelimit" not in result and "Search failed" not in result:
            return result
        
        logger.info("DDGS failed or rate-limited, trying headless browser...")
        
        # 2. Fall back to Playwright browser
        result = await self._web_search_browser(query, max_results)
        if result:
            return result
        
        return f"Sorry, I couldn't find any results for '{query}'. Please try a different search term."

    async def _web_search_ddg(self, query: str, max_results: int = 3) -> str:
        """Use duckduckgo_search library."""
        loop = asyncio.get_running_loop()
        try:
            results = await loop.run_in_executor(
                None,
                lambda: DDGS().text(
                    query, 
                    region="us-en", 
                    safesearch="moderate", 
                    max_results=max_results,
                    timelimit="y"  # Last year results
                )
            )
        except Exception as e:
            logger.warning(f"DDGS search error: {e}")
            return f"Search failed: {str(e)}"

        if not results:
            return ""

        formatted = []
        for r in results[:max_results]:
            title = r.get("title", "")
            body = r.get("body", "")[:300]
            href = r.get("href", "")
            formatted.append(f"• {title}\n  {body}\n  {href}")

        return f"Search results for '{query}':\n\n" + "\n\n".join(formatted)

    async def _web_search_browser(self, query: str, max_results: int = 3) -> str:
        """Search using Playwright headless Chromium."""
        try:
            from exon.core.web_browser import WebBrowser
            
            browser = WebBrowser()
            await browser.start()
            
            try:
                results = await browser.search(query, max_results)
            finally:
                await browser.close()
            
            if not results:
                return ""
            
            formatted = []
            for r in results[:max_results]:
                title = r.get("title", "")
                snippet = r.get("snippet", "")[:300]
                url = r.get("url", "")
                formatted.append(f"• {title}\n  {snippet}\n  {url}")
            
            return f"Search results for '{query}':\n\n" + "\n\n".join(formatted)
            
        except ImportError:
            logger.warning("Playwright not installed, browser search unavailable")
            return ""
        except Exception as e:
            logger.error(f"Browser search failed: {e}")
            return ""

    # ------------------------------------------------------------------
    # Time & Wikipedia
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
            return f"'{topic}' is ambiguous. Did you mean: {', '.join(options)}?"
        except wikipedia.exceptions.PageError:
            return f"No Wikipedia page found for '{topic}'."
        except Exception as e:
            return f"Could not retrieve Wikipedia summary: {str(e)}"

    def _sync_wikipedia(self, topic: str, sentences: int) -> str:
        wikipedia.set_lang("en")
        return wikipedia.summary(topic, sentences=sentences)

    # ------------------------------------------------------------------
    # Injection
    # ------------------------------------------------------------------
    async def inject_tool_result(self, original_response: str, tool_result: str) -> str:
        if not tool_result or tool_result.startswith("Tool error"):
            return original_response
        if "Search failed:" in tool_result or "Ratelimit" in tool_result:
            return original_response  # Don't inject failure messages
        if "[System tool result:" in original_response:
            return original_response
        return f"{original_response}\n\n{tool_result}"