"""
orchestrator/pipeline.py
─────────────────────────
Assembles the SequentialAgent orchestrator from the three sub-agents.

Why SequentialAgent?
────────────────────
Phase III (code generation) depends on Phase II's bounded context list.
Phase IV (DevOps) depends on Phase III's service names.
A SequentialAgent guarantees this dependency order with zero custom logic.

Extending the pipeline
──────────────────────
1. Create your new agent in agents/your_agent.py.
2. Import it here and append to _PIPELINE_AGENTS.
The orchestrator automatically includes it in the next run.
"""

from __future__ import annotations

from google.adk.agents import SequentialAgent

from agents.analyst_agent import analyst_agent
from agents.test_engineer_agent import test_engineer_agent
from agents.devops_agent    import devops_agent
from utils.logger  import get_logger

logger = get_logger(__name__)

# ── Ordered list of sub-agents — edit this list to add/remove/reorder phases ──
_PIPELINE_AGENTS = [
    analyst_agent,        # Phase I + II
    test_engineer_agent,  # Phase III
    devops_agent,         # Phase IV
    # ← Add new agents here, e.g.: security_scanner_agent
]


def build_orchestrator() -> SequentialAgent:
    """
    Build and return the master SequentialAgent orchestrator.
    Called once at startup; the result is reused for all sessions.
    """
    agent_names = [a.name for a in _PIPELINE_AGENTS]
    logger.info("Building orchestrator with agents: %s", agent_names)

    return SequentialAgent(
        name="MigrationOrchestrator",
        description=(
            "Master Architect that orchestrates the full 4-phase Java monolith "
            "migration pipeline: Discovery → Decomposition → Implementation → DevOps."
        ),
        sub_agents=_PIPELINE_AGENTS,
    )