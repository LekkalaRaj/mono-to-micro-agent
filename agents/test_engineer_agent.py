"""
agents/test_engineer_agent.py
──────────────────────────────
TestEngineerAgent — Phase III (Implementation & Test Engineering).
"""

from agents.base import AgentFactory
from prompts.test_engineer     import TEST_ENGINEER_SYSTEM_PROMPT
from tools import coder_fn_tool


test_engineer_agent = AgentFactory.create(
    name="TestEngineerAgent",
    instruction=TEST_ENGINEER_SYSTEM_PROMPT,
    tools=[coder_fn_tool],
    output_key="implementation_result",
    description=(
        "Generates Spring Boot microservice stubs and comprehensive JUnit 5 test "
        "suites (unit, integration, contract) for each bounded context."
    ),
)