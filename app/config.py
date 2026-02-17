"""Configuration for the All Points chatbot."""

import os
from pathlib import Path

# Anthropic
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")

# Arcade Gateway (pre-configured with AllPoints tools + Gmail/Slack/Slides)
GATEWAY_URL = os.environ.get("ARCADE_GATEWAY_URL", "https://api.arcade.dev/mcp/allpoints-demo")
ARCADE_API_KEY = os.environ.get("ARCADE_API_KEY", "")

# Load system prompt from file
_prompt_path = Path(__file__).resolve().parent.parent / "claude_project_prompt.md"
if _prompt_path.exists():
    SYSTEM_PROMPT = _prompt_path.read_text()
else:
    SYSTEM_PROMPT = "You are an operations assistant for All Points ATL, a 3PL company."
