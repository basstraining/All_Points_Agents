"""All Points Operations Intelligence — Chatbot.

Chainlit app that bridges Claude API ↔ Arcade Gateway.
The Gateway is pre-configured with AllPoints MCP tools + Gmail/Slack/Slides.
Each prospect authenticates via email for per-user OAuth on personal tools.
"""

import logging

import chainlit as cl
from anthropic import AsyncAnthropic

from config import ANTHROPIC_API_KEY, ARCADE_API_KEY, GATEWAY_URL, MODEL, SYSTEM_PROMPT
from gateway import ArcadeGateway, ToolCallResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

anthropic = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

# Maximum tool-call rounds per message to prevent infinite loops
MAX_TOOL_ROUNDS = 10


@cl.on_chat_start
async def on_chat_start():
    """Initialize the session: collect email, connect to Gateway, discover tools."""

    # Collect email for per-user Arcade auth
    res = await cl.AskUserMessage(
        content=(
            "Welcome to **All Points Operations Intelligence**.\n\n"
            "Enter your email to get started:"
        ),
        timeout=300,
    ).send()

    if not res:
        await cl.Message(content="Session timed out. Please refresh to try again.").send()
        return

    user_email = res["output"].strip()

    # Connect to the pre-configured Arcade Gateway
    gateway = ArcadeGateway(
        gateway_url=GATEWAY_URL,
        api_key=ARCADE_API_KEY,
        user_id=user_email,
    )

    status_msg = cl.Message(content="Connecting to All Points systems...")
    await status_msg.send()

    try:
        mcp_tools = await gateway.list_tools()
        anthropic_tools = gateway.to_anthropic_format(mcp_tools)
    except Exception as e:
        logger.error(f"Failed to connect to Gateway: {e}")
        await cl.Message(
            content=f"Failed to connect to the Gateway. Check that the URL and API key are configured.\n\n`{e}`"
        ).send()
        return

    # Store session state
    cl.user_session.set("gateway", gateway)
    cl.user_session.set("tools", anthropic_tools)
    cl.user_session.set("messages", [])
    cl.user_session.set("user_email", user_email)

    tool_count = len(anthropic_tools)
    status_msg.content = f"Connected — **{tool_count} tools** available across shipping, billing, compliance, and more.\n\nHow can I help?"
    await status_msg.update()


@cl.on_message
async def on_message(message: cl.Message):
    """Handle a user message: call Claude, execute tool calls, stream response."""
    gateway: ArcadeGateway = cl.user_session.get("gateway")
    tools: list[dict] = cl.user_session.get("tools")
    messages: list[dict] = cl.user_session.get("messages")

    if not gateway or not tools:
        await cl.Message(content="Session not initialized. Please refresh and enter your email.").send()
        return

    # Append user message
    messages.append({"role": "user", "content": message.content})

    # Tool-calling loop: Claude may call tools multiple times before responding
    for _round in range(MAX_TOOL_ROUNDS):
        response = await anthropic.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )

        assistant_content = response.content
        messages.append({"role": "assistant", "content": assistant_content})

        # Separate text blocks and tool-use blocks
        text_parts = [block.text for block in assistant_content if block.type == "text"]
        tool_uses = [block for block in assistant_content if block.type == "tool_use"]

        # If there are no tool calls, we're done — send the final text
        if not tool_uses:
            if text_parts:
                await cl.Message(content="\n\n".join(text_parts)).send()
            break

        # Show any text that came before tool calls
        if text_parts:
            await cl.Message(content="\n\n".join(text_parts)).send()

        # Execute each tool call
        tool_results = []
        for tool_use in tool_uses:
            async with cl.Step(name=tool_use.name, type="tool") as step:
                step.input = tool_use.input

                try:
                    result: ToolCallResult = await gateway.call_tool(
                        tool_use.name, tool_use.input
                    )

                    if result.needs_auth:
                        # OAuth authorization needed — show link to prospect
                        step.output = "Authorization required"
                        auth_msg = (
                            f"**{tool_use.name}** needs access to your account.\n\n"
                            f"[Click here to authorize]({result.auth_url})\n\n"
                            f"Once authorized, try your request again."
                        )
                        await cl.Message(content=auth_msg).send()
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": f"Authorization required. The user has been shown an authorization link.",
                            "is_error": True,
                        })
                    elif result.is_error:
                        step.output = f"Error: {result.text}"
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": f"Error: {result.text}",
                            "is_error": True,
                        })
                    else:
                        step.output = _truncate(result.text, 2000)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": result.text,
                        })

                except Exception as e:
                    error_msg = str(e)
                    step.output = f"Error: {error_msg}"
                    logger.warning(f"Tool call {tool_use.name} failed: {error_msg}")

                    # Check if the exception itself contains an auth URL
                    if _is_auth_error(error_msg):
                        await cl.Message(
                            content=_format_auth_message(error_msg)
                        ).send()

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": f"Error: {error_msg}",
                        "is_error": True,
                    })

        # Feed tool results back to Claude
        messages.append({"role": "user", "content": tool_results})

    cl.user_session.set("messages", messages)


def _truncate(text: str, max_len: int) -> str:
    """Truncate text for display in the Chainlit step panel."""
    if len(text) <= max_len:
        return text
    return text[:max_len] + f"\n\n... ({len(text) - max_len} chars truncated)"


def _is_auth_error(error_msg: str) -> bool:
    """Check if an error indicates OAuth authorization is needed."""
    auth_keywords = ["authorization", "authenticate", "oauth", "login", "auth_url", "authorization_url"]
    lower = error_msg.lower()
    return any(kw in lower for kw in auth_keywords)


def _format_auth_message(error_msg: str) -> str:
    """Format an auth-required error into a user-friendly message."""
    # Try to extract a URL from the error message
    import re
    urls = re.findall(r'https?://\S+', error_msg)
    if urls:
        url = urls[0].rstrip('",}')
        return (
            f"This action requires authorization. "
            f"Please click the link below to connect your account:\n\n"
            f"[Authorize]({url})\n\n"
            f"Once authorized, try your request again."
        )
    return (
        f"This action requires authorization. "
        f"Please check your Arcade account to connect the required service, then try again.\n\n"
        f"Details: {error_msg}"
    )
