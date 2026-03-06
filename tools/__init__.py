"""
tools/__init__.py
──────────────────
Single registration point for all ADK tools.

TWO DISTINCT NAMESPACES — never mix them:
  *_fn_tool  → FunctionTool instances  → used by agents (tools=[...])
  *_tool     → raw callables           → used by unit tests only

Adding a new tool:
  1. Implement it in tools/your_tool.py  (returns plain dict)
  2. Import the function below
  3. Create a FunctionTool wrapper with the _fn_tool suffix
  4. Add both to __all__ in the correct section
"""

from google.adk.tools import FunctionTool

# ── Raw callables (unit-test friendly, no ADK dependency) ─────────────────────
from .code_reader import code_reader_tool
from .architect   import architect_tool
from .coder       import coder_tool
from .devops      import devops_tool

# ── ADK FunctionTool instances (pass these to agents, never the raw functions) ─
code_reader_fn_tool: FunctionTool = FunctionTool(func=code_reader_tool)
architect_fn_tool:   FunctionTool = FunctionTool(func=architect_tool)
coder_fn_tool:       FunctionTool = FunctionTool(func=coder_tool)
devops_fn_tool:      FunctionTool = FunctionTool(func=devops_tool)

__all__ = [
    # ── For agents ──────────────────────────────────────────────────────────
    "code_reader_fn_tool",
    "architect_fn_tool",
    "coder_fn_tool",
    "devops_fn_tool",
    # ── For unit tests only ─────────────────────────────────────────────────
    "code_reader_tool",
    "architect_tool",
    "coder_tool",
    "devops_tool",
]