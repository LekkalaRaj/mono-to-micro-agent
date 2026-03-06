# 🏗️ MonoToMicro (M2M) Agent

# 🏗️ Legacy-to-Cloud-Native Architect — Google ADK Multi-Agent System

> Modular, extensible Strangler Fig automation for Java monolith → microservices migration.

---

## Package Structure

```
mono-to-micro-agent/
│
├── config/
│   └── settings.py          # Pydantic BaseSettings — single source of truth
│
├── models/
│   └── schemas.py           # All Pydantic I/O contracts for every tool
│
├── utils/
│   ├── logger.py            # Structured logging (get_logger(__name__))
│   ├── java_codegen.py      # Spring Boot / JUnit source templates
│   └── k8s_codegen.py       # Dockerfile / Helm / K8s YAML templates
│
├── tools/
│   ├── code_reader.py       # Tool 1 — GitHub repo fetcher
│   ├── architect.py         # Tool 2 — DDD decomposition + Mermaid diagrams
│   ├── coder.py             # Tool 3 — Spring Boot scaffold + JUnit tests
│   └── devops.py            # Tool 4 — Dockerfile + Helm + K8s manifests
│
├── prompts/
│   ├── master.py            # Shared foundational system prompt
│   ├── analyst.py           # Phase I + II prompt
│   ├── test_engineer.py     # Phase III prompt
│   └── devops.py            # Phase IV prompt
│
├── agents/
│   ├── base.py              # AgentFactory — consistent LlmAgent construction
│   ├── analyst_agent.py     # CodeAnalystAgent    (Phase I + II)
│   ├── test_engineer_agent.py # TestEngineerAgent  (Phase III)
│   └── devops_agent.py      # DevOpsSpecialistAgent (Phase IV)
│
├── orchestrator/
│   └── pipeline.py          # SequentialAgent — assembles the pipeline
│
├── runner/
│   ├── session.py           # Session service factory (swap backend here)
│   └── pipeline_runner.py   # PipelineRunner — event loop + result capture
│
├── tests/
│   └── test_tools.py        # pytest unit tests for all four tools
│
├── main.py                  # CLI entry point
├── requirements.txt
└── .env.example
```

---

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env          # add GOOGLE_API_KEY and GITHUB_TOKEN
python main.py https://github.com/your-org/legacy-banking-monolith
```

Run tests (no ADK runtime needed):
```bash
pytest tests/ -v
```

---

## Extension Recipes

### Add a new agent (e.g. Security Scanner)

**1. Create the prompt** — `prompts/security_scanner.py`
```python
SECURITY_SCANNER_PROMPT = "You are a security specialist. Scan for OWASP Top 10..."
```

**2. Create the tool** — `tools/security_scanner.py`
```python
def security_scanner_tool(source_files: dict) -> dict:
    ...
```
Register in `tools/__init__.py`:
```python
from .security_scanner import security_scanner_tool
security_scanner_fn_tool = FunctionTool(func=security_scanner_tool)
```

**3. Create the agent** — `agents/security_scanner_agent.py`
```python
from mono_to_micro_agent.agents.base import AgentFactory
from mono_to_micro_agent.prompts.security_scanner import SECURITY_SCANNER_PROMPT
from mono_to_micro_agent.tools import security_scanner_fn_tool

security_scanner_agent = AgentFactory.create(
    name="SecurityScannerAgent",
    instruction=SECURITY_SCANNER_PROMPT,
    tools=[security_scanner_fn_tool],
    output_key="security_result",
)
```

**4. Register in the pipeline** — `orchestrator/pipeline.py`
```python
from mono_to_micro_agent.agents.security_scanner_agent import security_scanner_agent

_PIPELINE_AGENTS = [
    analyst_agent,
    test_engineer_agent,
    devops_agent,
    security_scanner_agent,   # ← append here
]
```

That's it. No other files change.

---

### Swap the LLM model

In `.env`:
```
DEFAULT_MODEL=gemini-1.5-pro-002
```
All agents pick up the change via `get_settings()` — no code changes.

### Switch to Vertex AI

In `.env`:
```
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=your-project
GOOGLE_CLOUD_LOCATION=us-central1
```

### Swap session backend (e.g., Firestore)

Edit `runner/session.py` only — replace `InMemorySessionService` with
`FirestoreSessionService`. Nothing else changes.

---

## Module Responsibilities (Single Responsibility Principle)

| Module | Does | Does NOT |
|--------|------|----------|
| `config/settings.py` | Load env vars | Touch agents or tools |
| `models/schemas.py` | Define data shapes | Contain business logic |
| `utils/java_codegen.py` | Render Java templates | Call APIs or agents |
| `utils/k8s_codegen.py` | Render K8s YAML | Call APIs or agents |
| `tools/*.py` | Orchestrate I/O, call utils | Render templates directly |
| `prompts/*.py` | Define agent instructions | Contain Python logic |
| `agents/*.py` | Instantiate LlmAgents | Define tools or prompts |
| `orchestrator/pipeline.py` | Assemble SequentialAgent | Run the event loop |
| `runner/pipeline_runner.py` | Manage sessions & stream events | Build agents or tools |
| `main.py` | CLI arg parsing + asyncio.run | Business logic |