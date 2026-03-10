"""
models/schemas.py
─────────────────
Pydantic v2 data contracts for every tool input/output.
All inter-agent data flows through these models — no raw dicts at boundaries.
Adding a new field here automatically propagates type-safety to all consumers.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


# ─────────────────────────────────────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────────────────────────────────────

class DiagramType(str, Enum):
    CONTEXT  = "context"
    CLASS    = "class"
    SEQUENCE = "sequence"
    ALL      = "all"


class Severity(str, Enum):
    LOW      = "LOW"
    MEDIUM   = "MEDIUM"
    HIGH     = "HIGH"
    CRITICAL = "CRITICAL"


class JavaVersion(int, Enum):
    V17 = 17
    V21 = 21


# ─────────────────────────────────────────────────────────────────────────────
# Tool 1 — CodeReader
# ─────────────────────────────────────────────────────────────────────────────

class CodeReaderInput(BaseModel):
    github_url:  str = Field(..., description="Full GitHub repository URL")
    file_filter: str = Field(".java,.xml,.yml,.yaml,.properties,.sql,.md", description="File extension to collect (comma-separated)")


class CodeReaderOutput(BaseModel):
    repo_name:     str
    total_files:   int
    file_tree:     list[str]
    file_contents: dict[str, str]   = Field(default_factory=dict)
    dependencies:  list[str]        = Field(default_factory=list)
    java_version:  str              = "unknown"
    loc_total:     int              = 0
    note:          Optional[str]    = None


# ─────────────────────────────────────────────────────────────────────────────
# Tool 2 — Architect
# ─────────────────────────────────────────────────────────────────────────────

class BoundedContext(BaseModel):
    name:             str = Field(..., description="Name of the bounded context")
    responsibilities: list[str] = Field(default_factory=list, description="List of strings detailing responsibilities (must be an array/list, not a single string)")
    entities:         list[str] = Field(default_factory=list, description="List of domain entities")


class CouplingHotspot(BaseModel):
    class_name: str      = Field("Unknown", description="The exact name of the offending class")
    reason:     str      = Field("Unknown", description="Reason for being a hotspot")
    severity:   Severity = Field(Severity.MEDIUM, description="Severity level")


class ProposedService(BaseModel):
    service_name: str = Field(..., description="Name of the proposed microservice")
    capabilities: list[str] = Field(default_factory=list, description="List of string capabilities (must be an array/list, not a single string)")
    owner_bc:     str = Field(..., description="Owner bounded context")


class StranglerFigPhase(BaseModel):
    phase:                int = Field(0, description="The sequence number of the phase (e.g. 1, 2, 3)")
    action:               str = Field("Migration step", description="Description of the action taken in this phase")
    monolith_traffic_pct: int = Field(0, description="Percentage of traffic remaining on the monolith", ge=0, le=100)


class StranglerFigPlan(BaseModel):
    strategy: str = Field("Strangler Fig", description="High-level migration strategy.")
    phases:   list[StranglerFigPhase] = Field(default_factory=list, description="List of phases for the migration.")


class ArchitectInput(BaseModel):
    bounded_contexts:     list[BoundedContext] = Field(..., description="Identified bounded contexts based on code structure")
    god_classes:          list[str]            = Field(default_factory=list, description="List of identified God Classes (>500 LOC, >10 public methods, etc)")
    coupling_hotspots:    list[CouplingHotspot] = Field(default_factory=list, description="Coupling Hotspot map")
    proposed_services:    list[ProposedService] = Field(..., description="Proposed microservices decomposition")
    strangler_fig_plan:   StranglerFigPlan     = Field(..., description="Strangler Fig routing plan")
    mermaid_context_diagram: str = Field(..., description="Mermaid.js system context diagram representing the whole architecture")
    mermaid_class_diagram:   str = Field(..., description="Mermaid.js class diagram detailing low-level and high-level class interactions")
    mermaid_sequence_diagram: str = Field(..., description="Mermaid.js sequence diagram showing interaction across bounded contexts")
    architecture_documentation: str = Field(..., description="Detailed Markdown documentation describing the monolithic architecture and proposed decomposition")


class ArchitectOutput(BaseModel):
    bounded_contexts:     list[BoundedContext]
    god_classes:          list[str]            = Field(default_factory=list)
    coupling_hotspots:    list[CouplingHotspot] = Field(default_factory=list)
    proposed_services:    list[ProposedService]
    strangler_fig_plan:   StranglerFigPlan
    mermaid_diagrams:     dict[str, str]
    readme_decomposition: str


# ─────────────────────────────────────────────────────────────────────────────
# Tool 3 — Coder
# ─────────────────────────────────────────────────────────────────────────────

class CoderInput(BaseModel):
    service_spec:        ProposedService
    java_version:        JavaVersion = JavaVersion.V21
    spring_boot_version: str         = "3.2.x"


class CoderOutput(BaseModel):
    service_name:   str
    source_files:   dict[str, str]   = Field(default_factory=dict)
    test_files:     dict[str, str]   = Field(default_factory=dict)
    pom_xml:        str
    contract_stubs: dict[str, str]   = Field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Tool 4 — DevOps
# ─────────────────────────────────────────────────────────────────────────────

class DevOpsInput(BaseModel):
    service_name: str
    replicas:     int = Field(2, ge=1)
    port:         int = Field(8080, ge=1024, le=65535)


class DevOpsOutput(BaseModel):
    service_name:   str
    dockerfile:     str
    helm_chart_yaml: str
    deployment_yaml: str
    service_yaml:    str
    ingress_yaml:    str
    configmap_yaml:  str
    secrets_yaml:    str
    hpa_yaml:        str