"""
agents/base.py
───────────────
AgentFactory — a single, consistent way to build LlmAgent instances.

Benefits
────────
• All agents share the same model, output-key convention, and logging.
• Swapping the default model (e.g., for a higher-capacity Gemini variant)
  requires a one-line change here, not edits scattered across agent files.
• New agents are created with AgentFactory.create(...) — no boilerplate.
• Raw callables passed as tools are automatically wrapped in FunctionTool,
  so agents never break regardless of whether callers pass the function or
  the pre-wrapped instance.
"""

from __future__ import annotations

import inspect
from typing import Callable, Union

from google.adk.agents import LlmAgent
from google.adk.tools  import FunctionTool

from config.settings import get_settings
from utils.logger import get_logger

logger   = get_logger(__name__)
settings = get_settings()

# Accept either a pre-wrapped FunctionTool or a bare callable
ToolLike = Union[FunctionTool, Callable]


def _resolve_tool(tool: ToolLike) -> FunctionTool:
    """
    Ensure *tool* is a FunctionTool instance.

    If a raw callable is passed (e.g. during testing or accidental direct
    import), wrap it automatically and emit a warning so the caller knows
    to fix the import.
    """
    if isinstance(tool, FunctionTool):
        return tool
    if callable(tool):
        logger.warning(
            "Raw callable '%s' passed as a tool — auto-wrapping in FunctionTool. "
            "Import the pre-built FunctionTool instance from tools/__init__.py instead.",
            getattr(tool, "__name__", repr(tool)),
        )
        return FunctionTool(func=tool)
    raise TypeError(
        f"Expected a FunctionTool or callable, got {type(tool).__name__!r}: {tool!r}"
    )


def _tool_label(tool: FunctionTool) -> str:
    """Return a display name for a FunctionTool safe for logging."""
    # FunctionTool exposes .name in most ADK versions; fall back gracefully.
    return getattr(tool, "name", None) or getattr(tool, "func", tool).__name__


class AgentFactory:
    """Creates LlmAgent instances with a consistent, settings-driven configuration."""

    @staticmethod
    def create(
        name:        str,
        instruction: str,
        tools:       list[ToolLike],
        output_key:  str,
        description: str = "",
        model:       str | None = None,
    ) -> LlmAgent:
        """
        Build and return a configured LlmAgent.

        Args:
            name:        Unique agent identifier (used in ADK event.author).
            instruction: Full system prompt for this agent.
            tools:       List of FunctionTool instances (or raw callables —
                         they will be auto-wrapped with a warning).
            output_key:  Session-state key where the agent writes its result.
            description: Human-readable summary (shown in orchestrator logs).
            model:       Gemini model ID; defaults to settings.default_model.
        """
        resolved_model  = model or settings.default_model
        resolved_tools  = [_resolve_tool(t) for t in tools]
        tool_names      = [_tool_label(t) for t in resolved_tools]

        logger.info(
            "Creating agent: %s  model=%s  tools=%s",
            name, resolved_model, tool_names,
        )

        return LlmAgent(
            name=name,
            model=resolved_model,
            instruction=instruction,
            tools=resolved_tools,
            output_key=output_key,
            description=description or name,
        )