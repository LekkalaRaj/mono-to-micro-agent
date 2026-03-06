"""
agents/devops_agent.py
───────────────────────
DevOpsSpecialistAgent — Phase IV (Infrastructure & Deployment).
"""

from agents.base import AgentFactory
from prompts.devops import DEVOPS_SYSTEM_PROMPT
from tools import devops_fn_tool


devops_agent = AgentFactory.create(
    name="DevOpsSpecialistAgent",
    instruction=DEVOPS_SYSTEM_PROMPT,
    tools=[devops_fn_tool],
    output_key="devops_result",
    description=(
        "Produces distroless Dockerfiles, production Helm charts, K8s manifests, "
        "HPA configs, and Strangler Fig NGINX traffic routing plans."
    ),
)