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
    file_filter: str = Field(".java", description="File extension to collect")


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
    name:             str
    responsibilities: list[str]
    entities:         list[str]


class CouplingHotspot(BaseModel):
    class_name: str
    reason:     str
    severity:   Severity


class ProposedService(BaseModel):
    service_name: str
    capabilities: list[str]
    owner_bc:     str


class StranglerFigPhase(BaseModel):
    phase:                int
    action:               str
    monolith_traffic_pct: int = Field(ge=0, le=100)


class StranglerFigPlan(BaseModel):
    strategy: str
    phases:   list[StranglerFigPhase]


class ArchitectInput(BaseModel):
    repo_analysis: CodeReaderOutput
    diagram_type:  DiagramType = DiagramType.ALL


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