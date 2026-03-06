"""
agents/analyst_agent.py
────────────────────────
CodeAnalystAgent — Phase I (Discovery) + Phase II (Decomposition).
"""

from agents.base    import AgentFactory
from prompts.analyst import ANALYST_SYSTEM_PROMPT
from tools import code_reader_fn_tool, architect_fn_tool


analyst_agent = AgentFactory.create(
    name="CodeAnalystAgent",
    instruction=ANALYST_SYSTEM_PROMPT,
    tools=[code_reader_fn_tool, architect_fn_tool],
    output_key="analysis_result",
    description=(
        "Reads the Java repository, identifies bounded contexts, God Classes, "
        "coupling hotspots, and produces DDD decomposition + Mermaid diagrams."
    ),
)