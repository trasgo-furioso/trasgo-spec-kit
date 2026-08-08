"""Integration tests for edge cases.

Tests cover error scenarios from spec edge cases section.
"""

import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_ROOT = PROJECT_ROOT / "bundle"


def run_specify(*args, cwd):
    """Run a specify CLI command and return the result."""
    return subprocess.run(
        ["specify", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


class TestIntegrationMismatch:
    """Given a project with non-claude integration and extension catalog,
    When specify bundle install trasgospec, Then extension still installs.

    Note: Extensions are integration-agnostic — they install regardless of
    the project's active integration. The bundle itself may be
    integration-specific, but its extension components are not filtered.
    """

    def test_mismatch_still_installs_extension(self, tmp_path, extension_catalog_url):
        # Arrange — init with a different integration
        project_dir = tmp_path / "speckit-project"
        project_dir.mkdir()
        init_result = run_specify(
            "init", "--here", "--integration", "cursor-agent",
            cwd=project_dir,
        )
        assert init_result.returncode == 0, f"init failed: {init_result.stdout}"

        # Add extension catalog so the extension can be resolved
        run_specify(
            "extension", "catalog", "add",
            extension_catalog_url,
            "--name", "trasgospec",
            "--install-allowed",
            cwd=project_dir,
        )

        # Act
        result = run_specify(
            "bundle", "install", str(BUNDLE_ROOT),
            cwd=project_dir,
        )

        # Assert — extensions are integration-agnostic, so they install
        assert result.returncode == 0


class TestMissingCatalogSource:
    """Given a clean project with NO catalog source,
    When specify bundle install trasgospec (by ID), Then fail with not found."""

    def test_missing_catalog_fails(self, clean_project):
        # Act — install by catalog ID without adding catalog source
        result = run_specify(
            "bundle", "install", "trasgospec",
            cwd=clean_project,
        )

        # Assert
        assert result.returncode != 0


class TestUnreachableCatalog:
    """Given a catalog pointing to stopped server,
    When specify bundle install trasgospec, Then fail with network error."""

    def test_unreachable_catalog_fails(self, clean_project):
        # Arrange — add catalog pointing to a port nothing is listening on
        run_specify(
            "bundle", "catalog", "add",
            "http://localhost:19999/catalog.json",
            "--policy", "install-allowed",
            cwd=clean_project,
        )

        # Act
        result = run_specify(
            "bundle", "install", "trasgospec",
            cwd=clean_project,
        )

        # Assert
        assert result.returncode != 0


class TestMissingExtensionCatalog:
    """Given a project with bundle catalog but NO extension catalog,
    When specify bundle install trasgospec, Then fail with extension not found."""

    def test_missing_extension_catalog_fails(self, clean_project):
        # Act — install from local path without extension catalog
        result = run_specify(
            "bundle", "install", str(BUNDLE_ROOT),
            cwd=clean_project,
        )

        # Assert — should fail because extension can't be resolved
        assert result.returncode != 0
