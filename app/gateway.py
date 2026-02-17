"""Arcade Gateway MCP client.

Connects to the Arcade Gateway via Streamable HTTP (MCP protocol),
discovers available tools, and executes tool calls.
Auth is per-user: the API key authenticates the app, the User-ID
isolates OAuth tokens per prospect.
"""

import logging
import re
from dataclasses import dataclass, field

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

logger = logging.getLogger(__name__)


class ArcadeGateway:
    """Thin MCP client wrapper for the Arcade Gateway."""

    def __init__(self, gateway_url: str, api_key: str, user_id: str):
        self.gateway_url = gateway_url
        self.api_key = api_key
        self.user_id = user_id
        self._tools_cache = None

    def _make_http_client(self) -> httpx.AsyncClient:
        """Create an httpx client with Arcade auth headers."""
        return httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Arcade-User-ID": self.user_id,
            },
            timeout=60.0,
        )

    async def list_tools(self) -> list:
        """Discover available tools from the Gateway. Caches on first call."""
        if self._tools_cache is not None:
            return self._tools_cache

        async with self._make_http_client() as http_client:
            async with streamable_http_client(
                self.gateway_url, http_client=http_client
            ) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.list_tools()
                    self._tools_cache = result.tools
                    return self._tools_cache

    async def call_tool(self, name: str, arguments: dict) -> "ToolCallResult":
        """Execute a tool call through the Gateway.

        Returns a ToolCallResult with the text output and metadata about
        whether authorization is required.
        """
        async with self._make_http_client() as http_client:
            async with streamable_http_client(
                self.gateway_url, http_client=http_client
            ) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(name, arguments)

                    # Check for authorization elicitation in the result
                    auth_url = _extract_auth_url(result)
                    if auth_url:
                        return ToolCallResult(
                            text=f"Authorization required for {name}.",
                            needs_auth=True,
                            auth_url=auth_url,
                        )

                    if not result.content:
                        return ToolCallResult(text="")

                    parts = []
                    for block in result.content:
                        if hasattr(block, "text"):
                            parts.append(block.text)
                        else:
                            parts.append(str(block))

                    is_error = getattr(result, "isError", False)
                    return ToolCallResult(
                        text="\n".join(parts),
                        is_error=is_error,
                    )

    def clear_tools_cache(self):
        """Force re-discovery of tools on next list_tools() call."""
        self._tools_cache = None

    @staticmethod
    def to_anthropic_format(mcp_tools: list) -> list[dict]:
        """Convert MCP tool definitions to Anthropic API tool format.

        MCP uses `inputSchema`, Anthropic uses `input_schema`.
        """
        anthropic_tools = []
        for tool in mcp_tools:
            schema = tool.inputSchema if hasattr(tool, "inputSchema") else {}
            anthropic_tools.append({
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": schema,
            })
        return anthropic_tools


@dataclass
class ToolCallResult:
    """Result from a Gateway tool call."""
    text: str = ""
    is_error: bool = False
    needs_auth: bool = False
    auth_url: str = ""


def _extract_auth_url(result) -> str | None:
    """Check if a call_tool result is an OAuth elicitation response.

    Arcade uses MCP's URL Elicitation pattern — the response may contain
    an authorization URL when the user hasn't yet authorized a service.
    This checks multiple places the URL might appear.
    """
    # Check meta/structured fields for elicitation data
    meta = getattr(result, "meta", None) or {}
    if isinstance(meta, dict):
        if "url" in meta:
            return meta["url"]
        if "authorization_url" in meta:
            return meta["authorization_url"]

    # Check structuredContent
    structured = getattr(result, "structuredContent", None) or {}
    if isinstance(structured, dict):
        if "url" in structured and structured.get("mode") == "url":
            return structured["url"]

    # Check if any text content contains an auth URL pattern
    if result.content:
        for block in result.content:
            text = getattr(block, "text", "")
            if not text:
                continue
            # Look for common auth URL patterns in text responses
            auth_patterns = [
                r'https?://accounts\.google\.com/o/oauth\S+',
                r'https?://\S*arcade\S*/auth\S*',
                r'https?://\S*oauth\S+authorize\S*',
                r'https?://login\.\S+',
            ]
            for pattern in auth_patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group(0).rstrip('",})')

    return None
