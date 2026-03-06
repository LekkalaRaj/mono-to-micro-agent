"""
tests/test_settings.py
───────────────────────
Tests for config/settings.py.

Covers the three bugs that caused the original error:
  1. .env file not found (wrong path)
  2. GOOGLE_API_KEY loaded by Pydantic but never injected into os.environ
  3. No early validation — silent failure until the SDK call fails

Run with: pytest tests/test_settings.py -v
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Always import from the module directly so lru_cache doesn't bleed between tests
from config.settings import Settings, _ENV_FILE


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_settings(**overrides) -> Settings:
    """Build a Settings instance with safe test defaults, optionally overridden."""
    defaults = dict(
        google_api_key="test-key-abc123",
        google_genai_use_vertexai=False,
        google_cloud_project="",
        google_cloud_location="us-central1",
        default_model="gemini-2.0-flash",
        github_token="",
        app_name="test-app",
        default_user_id="test-user",
        default_java_version=21,
        default_spring_boot_version="3.2.x",
        container_registry="registry.test.internal",
        otel_collector_endpoint="http://localhost:4317",
    )
    defaults.update(overrides)
    return Settings(**defaults)


# ─────────────────────────────────────────────────────────────────────────────
# 1. .env file path resolution
# ─────────────────────────────────────────────────────────────────────────────

class TestEnvFilePath:
    def test_env_file_path_is_absolute(self):
        """_ENV_FILE must be absolute so it works from any CWD."""
        assert _ENV_FILE.is_absolute(), (
            f"_ENV_FILE is relative: {_ENV_FILE}. "
            "It must be resolved relative to settings.py, not CWD."
        )

    def test_env_file_path_points_to_project_root(self):
        """_ENV_FILE should sit at the project root, next to main.py."""
        assert _ENV_FILE.name == ".env"
        # Parent of settings.py is config/, parent of that is project root
        assert _ENV_FILE.parent == Path(__file__).resolve().parent.parent


# ─────────────────────────────────────────────────────────────────────────────
# 2. apply_to_environ — the core fix
# ─────────────────────────────────────────────────────────────────────────────

class TestApplyToEnviron:
    def test_google_api_key_written_to_os_environ(self):
        """
        This is the exact bug that caused the SDK error.
        Pydantic loads the value, but the SDK reads os.environ —
        apply_to_environ() is the bridge.
        """
        s = _make_settings(google_api_key="sk-test-key-xyz")
        # Ensure a clean slate for this key
        os.environ.pop("GOOGLE_API_KEY", None)

        s.apply_to_environ()

        assert os.environ.get("GOOGLE_API_KEY") == "sk-test-key-xyz", (
            "GOOGLE_API_KEY must be written to os.environ by apply_to_environ(). "
            "The Google SDK reads os.environ directly — it does not read Pydantic objects."
        )

    def test_vertex_ai_flag_written_as_string(self):
        s = _make_settings(google_genai_use_vertexai=True)
        os.environ.pop("GOOGLE_GENAI_USE_VERTEXAI", None)

        s.apply_to_environ()

        assert os.environ.get("GOOGLE_GENAI_USE_VERTEXAI") == "true"

    def test_empty_values_do_not_overwrite_existing_env(self):
        """Empty settings fields must not blank out a real env var."""
        os.environ["GOOGLE_CLOUD_PROJECT"] = "existing-project"
        s = _make_settings(google_cloud_project="")

        s.apply_to_environ()

        assert os.environ["GOOGLE_CLOUD_PROJECT"] == "existing-project"
        del os.environ["GOOGLE_CLOUD_PROJECT"]

    def test_setdefault_does_not_overwrite_existing_env(self):
        """os.environ values set before apply_to_environ() take precedence."""
        os.environ["GOOGLE_API_KEY"] = "already-set"
        s = _make_settings(google_api_key="from-dotenv")

        s.apply_to_environ()

        assert os.environ["GOOGLE_API_KEY"] == "already-set"
        del os.environ["GOOGLE_API_KEY"]


# ─────────────────────────────────────────────────────────────────────────────
# 3. validate_credentials — fast-fail with clear messages
# ─────────────────────────────────────────────────────────────────────────────

class TestValidateCredentials:
    def test_raises_if_api_key_missing_and_not_vertex(self):
        s = _make_settings(google_api_key="", google_genai_use_vertexai=False)
        with pytest.raises(ValueError, match="GOOGLE_API_KEY"):
            s.validate_credentials()

    def test_raises_with_dotenv_path_hint(self):
        """Error message must tell the user where the .env file is expected."""
        s = _make_settings(google_api_key="")
        with pytest.raises(ValueError, match=r"\.env"):
            s.validate_credentials()

    def test_ok_when_api_key_present(self):
        s = _make_settings(google_api_key="valid-key")
        s.validate_credentials()   # must not raise

    def test_raises_vertex_missing_project(self):
        s = _make_settings(
            google_genai_use_vertexai=True,
            google_cloud_project="",
            google_cloud_location="us-central1",
        )
        with pytest.raises(ValueError, match="GOOGLE_CLOUD_PROJECT"):
            s.validate_credentials()

    def test_raises_vertex_missing_location(self):
        s = _make_settings(
            google_genai_use_vertexai=True,
            google_cloud_project="my-project",
            google_cloud_location="",
        )
        with pytest.raises(ValueError, match="GOOGLE_CLOUD_LOCATION"):
            s.validate_credentials()

    def test_ok_vertex_fully_configured(self):
        s = _make_settings(
            google_api_key="",
            google_genai_use_vertexai=True,
            google_cloud_project="my-gcp-project",
            google_cloud_location="us-central1",
        )
        s.validate_credentials()   # must not raise