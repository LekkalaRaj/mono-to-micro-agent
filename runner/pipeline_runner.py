"""
runner/pipeline_runner.py
──────────────────────────
PipelineRunner encapsulates the ADK Runner, session lifecycle, and the
streaming event loop.  Callers interact with a single clean async method:

    results = await PipelineRunner().run(github_url)

Event handling and progress logging are isolated here — agents and tools
stay completely unaware of how results are surfaced.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import AsyncIterator

from google.adk.runners import Runner
from google.genai        import types as genai_types

from config.settings       import get_settings
from orchestrator.pipeline import build_orchestrator
from runner.session import get_session_service, create_session
from utils.logger        import get_logger

logger   = get_logger(__name__)
settings = get_settings()


@dataclass
class MigrationResult:
    """Structured result returned after a completed pipeline run."""
    github_url:   str
    session_id:   str
    final_output: str                   = ""
    phase_outputs: dict[str, str]       = field(default_factory=dict)
    success:      bool                  = False
    error:        str                   = ""


class PipelineRunner:
    """
    Manages a single end-to-end migration pipeline execution.

    Usage
    ─────
        runner = PipelineRunner()
        result = await runner.run("https://github.com/org/legacy-app")
    """

    def __init__(self, user_id: str | None = None) -> None:
        self._orchestrator  = build_orchestrator()
        self._session_svc   = get_session_service()
        self._user_id       = user_id or settings.default_user_id

        self._runner = Runner(
            agent=self._orchestrator,
            app_name=settings.app_name,
            session_service=self._session_svc,
        )

    async def run(self, github_url: str) -> MigrationResult:
        """
        Execute the full 4-phase migration pipeline for the given repository.

        Args:
            github_url: GitHub repository URL to analyse and migrate.

        Returns:
            MigrationResult with final output and per-phase artefacts.
        """
        self._print_banner(github_url)

        session = await create_session(self._user_id)
        result  = MigrationResult(github_url=github_url, session_id=session.id)

        initial_message = self._build_initial_message(github_url)

        try:
            async for event in self._runner.run_async(
                user_id=self._user_id,
                session_id=session.id,
                new_message=initial_message,
            ):
                self._handle_event(event, result)

            result.success = True
            logger.info("Pipeline completed successfully for: %s", github_url)

        except Exception as exc:  # noqa: BLE001
            result.error = str(exc)
            logger.error("Pipeline failed: %s", exc, exc_info=True)

        self._print_footer(result)
        return result

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _build_initial_message(github_url: str) -> genai_types.Content:
        return genai_types.Content(
            role="user",
            parts=[
                genai_types.Part(
                    text=(
                        f"Begin the full 4-phase migration analysis for:\n\n"
                        f"  {github_url}\n\n"
                        "Execute all phases sequentially. Produce complete artefacts "
                        "for each phase and include a timestamped DECISION_LOG."
                    )
                )
            ],
        )

    @staticmethod
    def _handle_event(event: object, result: MigrationResult) -> None:
        """Log streaming events and capture final output + phase artefacts."""
        author = getattr(event, "author", None)

        if author:
            logger.info("[%s] event received", author)

        content = getattr(event, "content", None)
        if content and hasattr(content, "parts"):
            for part in content.parts:
                text = getattr(part, "text", None)
                if text:
                    preview = text[:200] + ("..." if len(text) > 200 else "")
                    logger.debug("[%s] %s", author or "?", preview)

                    # Capture per-agent output keyed by agent name
                    if author:
                        result.phase_outputs[author] = text

        if hasattr(event, "is_final_response") and event.is_final_response():
            if content and hasattr(content, "parts"):
                result.final_output = "".join(
                    getattr(p, "text", "") for p in content.parts
                )
            logger.info("Final response received.")

    @staticmethod
    def _print_banner(github_url: str) -> None:
        print("\n" + "═" * 72)
        print("  LEGACY-TO-CLOUD-NATIVE ARCHITECT — Google ADK Pipeline v2")
        print("═" * 72)
        print(f"  Repository : {github_url}")
        print(f"  Phases     : Discovery → Decomposition → Implementation → DevOps")
        print("═" * 72 + "\n")

    @staticmethod
    def _print_footer(result: MigrationResult) -> None:
        status = "✅ SUCCESS" if result.success else f"❌ FAILED — {result.error}"
        print("\n" + "─" * 72)
        print(f"  Pipeline complete  |  {status}")
        print(f"  Session ID : {result.session_id}")
        print("─" * 72 + "\n")