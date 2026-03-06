"""
config/settings.py
──────────────────
Single source of truth for all runtime configuration.

HOW ENV LOADING WORKS
─────────────────────
pydantic-settings reads the .env file into Python objects, but the
Google ADK / google-genai SDK reads credentials directly from os.environ
at the moment it initialises its HTTP client — it never touches Pydantic.

This module solves that by:
  1. Locating the .env file relative to *this file* (not CWD) so it works
     regardless of where `python main.py` is invoked from.
  2. After pydantic-settings loads the values, _apply_to_environ() writes
     the Google-specific vars back into os.environ so the SDK finds them.

ADDING NEW SETTINGS
───────────────────
  • Add a Field(...) to Settings.
  • If the SDK reads it from os.environ (not via Pydantic), add it to
    _ENVIRON_MAP in _apply_to_environ() below.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib   import Path

from pydantic             import Field, field_validator
from pydantic_settings    import BaseSettings, SettingsConfigDict

# Resolve .env relative to this file, not the process CWD.
# Works correctly whether you run `python main.py` from the project root,
# a subdirectory, or via pytest from any location.
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """Application-wide settings — loaded from .env then os.environ."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Google / Gemini ───────────────────────────────────────────────────────
    google_api_key: str = Field(
        default="",
        description="Google AI Studio API key (required unless using Vertex AI)",
    )
    google_genai_use_vertexai: bool = Field(
        default=False,
        description="Set true to use Vertex AI instead of AI Studio",
    )
    google_cloud_project:  str = Field(default="", description="GCP project (Vertex only)")
    google_cloud_location: str = Field(default="us-central1", description="GCP region (Vertex only)")

    # ── Model selection ───────────────────────────────────────────────────────
    default_model: str = Field(
        default="gemini-2.0-flash",
        description="Gemini model ID; use gemini-1.5-pro-002 for larger context",
    )

    # ── GitHub ────────────────────────────────────────────────────────────────
    github_token: str = Field(default="", description="GitHub PAT for private repos")

    # ── Runner / session ──────────────────────────────────────────────────────
    app_name:        str = Field(default="legacy-migration-architect")
    default_user_id: str = Field(default="architect-operator-001")

    # ── Java / Spring defaults ────────────────────────────────────────────────
    default_java_version:        int = Field(default=21, description="17 or 21")
    default_spring_boot_version: str = Field(default="3.2.x")

    # ── Container registry ────────────────────────────────────────────────────
    container_registry: str = Field(
        default="registry.bank.internal",
        description="Internal OCI registry prefix",
    )

    # ── Observability ─────────────────────────────────────────────────────────
    otel_collector_endpoint: str = Field(
        default="http://otel-collector:4317",
        description="OpenTelemetry gRPC collector endpoint",
    )

    # ── Validation ────────────────────────────────────────────────────────────
    @field_validator("google_api_key")
    @classmethod
    def _require_api_key_or_vertex(cls, v: str, info: object) -> str:
        """
        Defer the 'must have credentials' check to _validate_credentials()
        after the full object is constructed, so we can inspect both fields.
        Pydantic validators run field-by-field, so we just pass through here.
        """
        return v

    def validate_credentials(self) -> None:
        """
        Call once at startup.  Raises ValueError with a clear, actionable
        message if neither AI Studio nor Vertex AI credentials are present.
        """
        using_vertex = self.google_genai_use_vertexai
        if using_vertex:
            missing = [
                f for f, v in [
                    ("GOOGLE_CLOUD_PROJECT",  self.google_cloud_project),
                    ("GOOGLE_CLOUD_LOCATION", self.google_cloud_location),
                ]
                if not v
            ]
            if missing:
                raise ValueError(
                    "GOOGLE_GENAI_USE_VERTEXAI=true but the following are not set:\n"
                    + "\n".join(f"  • {m}" for m in missing)
                    + "\nAdd them to your .env file or export them as environment variables."
                )
        else:
            if not self.google_api_key:
                raise ValueError(
                    "GOOGLE_API_KEY is not set.\n"
                    "Fix: add  GOOGLE_API_KEY=your_key  to your .env file, or:\n"
                    f"  Expected .env location: {_ENV_FILE}\n"
                    "  Current .env exists: "
                    + str(_ENV_FILE.exists())
                    + "\n\nAlternatively set GOOGLE_GENAI_USE_VERTEXAI=true and "
                    "provide GOOGLE_CLOUD_PROJECT + GOOGLE_CLOUD_LOCATION."
                )

    def apply_to_environ(self) -> None:
        """
        Write Google-SDK-relevant settings into os.environ so that the
        google-genai / ADK HTTP clients find them at initialisation time.

        The Google SDK reads these env vars directly — it does NOT read from
        Pydantic objects — so this bridge call is mandatory.

        Called automatically by get_settings() on first load.
        """
        # Map: os.environ key  →  settings value
        _ENVIRON_MAP: dict[str, str] = {
            "GOOGLE_API_KEY":            self.google_api_key,
            "GOOGLE_GENAI_USE_VERTEXAI": "true" if self.google_genai_use_vertexai else "false",
            "GOOGLE_CLOUD_PROJECT":      self.google_cloud_project,
            "GOOGLE_CLOUD_LOCATION":     self.google_cloud_location,
            "GITHUB_TOKEN":          self.github_token,
        }
        for key, value in _ENVIRON_MAP.items():
            if value:                       # don't overwrite with empty strings
                os.environ.setdefault(key, value)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the validated, singleton Settings instance.

    On first call:
      1. Loads .env from the project root (path-safe, not CWD-dependent).
      2. Validates that credentials are present.
      3. Writes Google env vars into os.environ for the SDK to find.
    Subsequent calls return the cached instance at zero cost.
    """
    s = Settings()
    s.validate_credentials()   # fail fast with a clear message
    s.apply_to_environ()       # make the SDK find the key
    return s