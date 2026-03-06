"""
tests/test_tools.py
────────────────────
Unit tests for the four ADK tools.
These test the raw Python callables — no ADK runtime required.
Run with: pytest tests/
"""

from __future__ import annotations

import pytest
from google.adk.tools import FunctionTool

# Import raw callables (not FunctionTool wrappers) — for logic tests
from tools.code_reader import code_reader_tool
from tools.architect   import architect_tool
from tools.coder       import coder_tool
from tools.devops      import devops_tool

# Import FunctionTool instances — for registration tests
from tools import (
    code_reader_fn_tool,
    architect_fn_tool,
    coder_fn_tool,
    devops_fn_tool,
)


# ── Tool Registration (catches the AttributeError that prompted this fix) ─────

class TestToolRegistration:
    """
    Verify that every _fn_tool export is a proper FunctionTool instance.
    This is the test that would have caught the original AttributeError:
      'function' object has no attribute 'name'
    """

    @pytest.mark.parametrize("tool,expected_name", [
        (code_reader_fn_tool, "code_reader_tool"),
        (architect_fn_tool,   "architect_tool"),
        (coder_fn_tool,       "coder_tool"),
        (devops_fn_tool,      "devops_tool"),
    ])
    def test_is_function_tool_instance(self, tool, expected_name):
        assert isinstance(tool, FunctionTool), (
            f"{expected_name}: expected FunctionTool, got {type(tool).__name__}"
        )

    @pytest.mark.parametrize("tool,expected_name", [
        (code_reader_fn_tool, "code_reader_tool"),
        (architect_fn_tool,   "architect_tool"),
        (coder_fn_tool,       "coder_tool"),
        (devops_fn_tool,      "devops_tool"),
    ])
    def test_has_name_attribute(self, tool, expected_name):
        """AgentFactory logs t.name — this must never raise AttributeError."""
        name = getattr(tool, "name", None) or getattr(tool, "func", tool).__name__
        assert name, f"Could not resolve a name for {expected_name}"

    def test_raw_callables_are_not_function_tools(self):
        """Raw callables must stay as plain functions for unit-test isolation."""
        for fn in (code_reader_tool, architect_tool, coder_tool, devops_tool):
            assert not isinstance(fn, FunctionTool), (
                f"{fn.__name__} should be a plain callable, not a FunctionTool"
            )


# ── CodeReader ────────────────────────────────────────────────────────────────

class TestCodeReaderTool:
    def test_returns_dict(self):
        result = code_reader_tool("https://github.com/test/repo")
        assert isinstance(result, dict)

    def test_repo_name_extracted(self):
        result = code_reader_tool("https://github.com/bank/legacy-app")
        assert result["repo_name"] == "legacy-app"

    def test_trailing_slash_handled(self):
        result = code_reader_tool("https://github.com/bank/legacy-app/")
        assert result["repo_name"] == "legacy-app"

    def test_required_keys_present(self):
        result = code_reader_tool("https://github.com/bank/app")
        for key in ("repo_name", "total_files", "file_tree", "file_contents",
                    "dependencies", "java_version", "loc_total"):
            assert key in result, f"Missing key: {key}"


# ── Architect ─────────────────────────────────────────────────────────────────

class TestArchitectTool:
    @pytest.fixture()
    def repo_analysis(self):
        return code_reader_tool("https://github.com/bank/app")

    def test_returns_dict(self, repo_analysis):
        result = architect_tool(repo_analysis)
        assert isinstance(result, dict)

    def test_bounded_contexts_non_empty(self, repo_analysis):
        result = architect_tool(repo_analysis)
        assert len(result["bounded_contexts"]) > 0

    def test_proposed_services_non_empty(self, repo_analysis):
        result = architect_tool(repo_analysis)
        assert len(result["proposed_services"]) > 0

    def test_mermaid_context_diagram_present(self, repo_analysis):
        result = architect_tool(repo_analysis, diagram_type="context")
        assert "context" in result["mermaid_diagrams"]
        assert "graph" in result["mermaid_diagrams"]["context"]

    def test_all_diagrams_generated(self, repo_analysis):
        result = architect_tool(repo_analysis, diagram_type="all")
        assert set(result["mermaid_diagrams"].keys()) == {"context", "class", "sequence"}


# ── Coder ─────────────────────────────────────────────────────────────────────

class TestCoderTool:
    @pytest.fixture()
    def service_spec(self):
        return {
            "service_name": "payment-service",
            "capabilities": ["initiate", "settle"],
            "owner_bc": "Payments",
        }

    def test_returns_dict(self, service_spec):
        result = coder_tool(service_spec)
        assert isinstance(result, dict)

    def test_source_files_generated(self, service_spec):
        result = coder_tool(service_spec)
        assert len(result["source_files"]) >= 3  # main, controller, service

    def test_test_files_generated(self, service_spec):
        result = coder_tool(service_spec)
        assert len(result["test_files"]) >= 2  # unit + integration

    def test_pom_xml_present(self, service_spec):
        result = coder_tool(service_spec)
        assert "<artifactId>payment-service</artifactId>" in result["pom_xml"]

    def test_java21_in_pom(self, service_spec):
        result = coder_tool(service_spec, java_version=21)
        assert "21" in result["pom_xml"]

    def test_unit_test_has_bigdecimal_overflow(self, service_spec):
        result = coder_tool(service_spec)
        unit_tests = " ".join(result["test_files"].values())
        assert "BigDecimal" in unit_tests, "BigDecimal overflow test must be present"


# ── DevOps ────────────────────────────────────────────────────────────────────

class TestDevOpsTool:
    def test_returns_dict(self):
        result = devops_tool("payment-service")
        assert isinstance(result, dict)

    def test_dockerfile_distroless(self):
        result = devops_tool("payment-service")
        assert "distroless" in result["dockerfile"]

    def test_dockerfile_non_root_user(self):
        result = devops_tool("payment-service")
        assert "10001" in result["dockerfile"]

    def test_deployment_has_liveness_probe(self):
        result = devops_tool("payment-service")
        assert "liveness" in result["deployment_yaml"]

    def test_deployment_has_readiness_probe(self):
        result = devops_tool("payment-service")
        assert "readiness" in result["deployment_yaml"]

    def test_secrets_no_plaintext(self):
        result = devops_tool("payment-service")
        # Must use Vault annotation, not base64 stringData
        assert "vault.hashicorp.com" in result["secrets_yaml"]
        assert "stringData" not in result["secrets_yaml"].lower() or \
               "# stringData" in result["secrets_yaml"]

    def test_hpa_has_cpu_and_memory_metrics(self):
        result = devops_tool("payment-service")
        assert "cpu" in result["hpa_yaml"]
        assert "memory" in result["hpa_yaml"]

    def test_configmap_has_otel_endpoint(self):
        result = devops_tool("payment-service")
        assert "OTEL_EXPORTER_OTLP_ENDPOINT" in result["configmap_yaml"]