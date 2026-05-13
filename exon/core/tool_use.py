"""
File: /opt/futureex/exon/core/tool_use.py
Author: Ashish Pal
Purpose: Allow Exon to call external tools (web search, calculator, database) to achieve goals.
"""

import json
import logging
import subprocess
import aiohttp
from typing import Dict, Any, Optional
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class ToolUse:
    def __init__(self, exon_id: str, redis_client: redis.Redis):
        self.exon_id = exon_id
        self.redis = redis_client

    async def detect_tool_intent(self, user_message: str, response: str) -> Optional[Dict]:
        """Use Ollama to decide if a tool is needed."""
        # Simplified: keyword detection; in production use a small LLM prompt.
        msg = user_message.lower()
        if "calculate" in msg or "math" in msg:
            return {"tool": "calculator", "expression": self._extract_expression(msg)}
        if "search" in msg or "google" in msg or "find" in msg:
            return {"tool": "web_search", "query": user_message}
        if "database" in msg or "query" in msg:
            return {"tool": "db_query", "query": user_message}
        return None

    def _extract_expression(self, text: str) -> str:
        # Very naive extraction – in production use regex or LLM
        words = text.split()
        for w in words:
            if any(op in w for op in ['+', '-', '*', '/']):
                return w
        return ""

    async def execute_tool(self, tool_spec: Dict) -> str:
        tool = tool_spec.get("tool")
        if tool == "calculator":
            expr = tool_spec.get("expression")
            try:
                result = eval(expr)  # Danger: only use in safe environment
                return f"The result is {result}"
            except Exception as e:
                return f"Calculation error: {e}"
        elif tool == "web_search":
            # Placeholder – integrate with a search API (DuckDuckGo, etc.)
            return "Web search not yet implemented."
        elif tool == "db_query":
            return "Database query not yet implemented."
        else:
            return "Tool not recognized."

    async def inject_tool_result(self, original_response: str, tool_result: str) -> str:
        """Merge tool result into response."""
        return f"{original_response}\n\n[System tool result: {tool_result}]"