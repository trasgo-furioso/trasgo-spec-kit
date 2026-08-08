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
    """T019: Given a project with non-claude integration,
    When specify bundle install trasgospec, Then no components are applied.

    Note: The specify CLI does not abort on integration mismatch for
    local path installs — it succeeds but applies 0 components.
    """

    def test_mismatch_installs_zero_components(self, tmp_path):
        # Arrange — init with a different integration
        project_dir = tmp_path / "speckit-project"
        project_dir.mkdir()
        init_result = run_specify(
            "init", "--here", "--integration", "cursor-agent",
            cwd=project_dir,
        )
        assert init_result.returncode == 0, f"init failed: {init_result.stdout}"

        # Act
        result = run_specify(
            "bundle", "install", str(BUNDLE_ROOT),
            cwd=project_dir,
        )

        # Assert — install succeeds but applies 0 components
        assert "0 added" in result.stdout


class TestMissingCatalogSource:
    """T020: Given a clean project with NO catalog source,
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
    """T021: Given a catalog pointing to stopped server,
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
