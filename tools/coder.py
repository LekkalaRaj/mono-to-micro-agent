"""
tools/coder.py
───────────────
Tool 3 — Coder
Generates Spring Boot microservice scaffolding and JUnit 5 / Mockito /
Pact test suites for a single proposed service.

Template rendering is fully delegated to utils/java_codegen.py so this
module stays focused on I/O orchestration only.
"""

from __future__ import annotations

from models.schemas import CoderInput, CoderOutput, ProposedService, JavaVersion
from utils.logger import get_logger
from utils.java_codegen import (
    render_main_class, render_controller, render_service_class,
    render_unit_test, render_integration_test, render_pom,
)

logger = get_logger(__name__)


def coder_tool(
    service_spec: dict,
    java_version: int = 21,
    spring_boot_version: str = "3.2.x",
) -> dict:
    """
    Generate a Spring Boot microservice scaffold + test suite.

    Args:
        service_spec:        Serialised ProposedService (from architect_tool)
        java_version:        Target Java LTS version (17 or 21)
        spring_boot_version: Spring Boot generation (e.g. "3.2.x")

    Returns:
        Serialised CoderOutput as a plain dict (ADK requirement).
    """
    _input = CoderInput(
        service_spec=ProposedService(**service_spec),
        java_version=JavaVersion(java_version),
        spring_boot_version=spring_boot_version,
    )

    svc          = _input.service_spec.service_name
    pkg          = svc.replace("-", "")
    cap          = svc.replace("-", " ").title().replace(" ", "")
    path_prefix  = svc.split("-")[0]

    logger.info(
        "Generating Spring Boot %s / Java %d for service: %s",
        spring_boot_version, java_version, svc,
    )

    source_files = {
        f"src/main/java/com/bank/{pkg}/{cap}Application.java":           render_main_class(pkg, cap),
        f"src/main/java/com/bank/{pkg}/controller/{cap}Controller.java": render_controller(pkg, cap, path_prefix),
        f"src/main/java/com/bank/{pkg}/service/{cap}Service.java":       render_service_class(pkg, cap),
    }

    test_files = {
        f"src/test/java/com/bank/{pkg}/service/{cap}ServiceTest.java": render_unit_test(pkg, cap),
        f"src/test/java/com/bank/{pkg}/{cap}IntegrationTest.java":     render_integration_test(pkg, cap, path_prefix),
    }

    output = CoderOutput(
        service_name=svc,
        source_files=source_files,
        test_files=test_files,
        pom_xml=render_pom(svc, java_version, spring_boot_version),
        contract_stubs={},   # TODO: wire Pact consumer DSL
    )

    import os
    out_dir = os.path.join("output", svc)
    os.makedirs(out_dir, exist_ok=True)
    
    # Save source files and test files
    for filepath, content in {**source_files, **test_files}.items():
        full_path = os.path.join(out_dir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
            
    with open(os.path.join(out_dir, "pom.xml"), "w", encoding="utf-8") as f:
        f.write(output.pom_xml)

    logger.info(
        "Code generation complete: %d source files, %d test files",
        len(output.source_files), len(output.test_files),
    )
    return output.model_dump()