"""
MCP Client for Google Calendar.
Spawns mcp_server.py as a subprocess over stdio and returns its tools
as LangChain-compatible tools via langchain-mcp-adapters.
"""
import sys
import os
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

_SERVER_SCRIPT = str(Path(__file__).resolve().parent.parent.parent / "mcp_server.py")


async def get_calendar_tools() -> List:
    """
    Connect to the Google Calendar MCP server and return its tools.
    Returns empty list if connection fails (agents fall back gracefully).
    """
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient

        client = MultiServerMCPClient({
            "google-calendar": {
                "command": sys.executable,
                "args": [_SERVER_SCRIPT],
                "transport": "stdio",
                "env": {**os.environ},
            }
        })
        tools = await client.get_tools()
        logger.info(f"MCP tools loaded: {[t.name for t in tools]}")
        return tools
    except Exception as e:
        logger.warning(f"MCP client failed: {e}")
        return []
