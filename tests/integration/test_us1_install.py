"""Integration tests for User Story 1: Install Trasgo Bundle from Self-Hosted Catalog.

Tests follow Given (Arrange) / When (Act) / Then (Assert) pattern
mapped from spec acceptance scenarios.
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


class TestInstallViaCatalog:
    """T009: Given a clean SK project with catalog source added,
    When specify bundle install trasgospec, Then exit 0 and components applied."""

    def test_install_via_catalog_succeeds(self, project_with_catalog):
        # Act
        result = run_specify("bundle", "install", "trasgospec", cwd=project_with_catalog)

        # Assert
        assert result.returncode == 0, f"Install failed: {result.stderr}"

    def test_install_via_catalog_applies_components(self, project_with_catalog):
        # Act
        run_specify("bundle", "install", "trasgospec", cwd=project_with_catalog)

        # Assert — skill component should be present in the project
        result = run_specify("bundle", "list", cwd=project_with_catalog)
        assert "trasgospec" in result.stdout


class TestBundleListAfterInstall:
    """T010: Given a successful install, When specify bundle list,
    Then output contains trasgospec with version, component count, timestamp."""

    def test_bundle_list_shows_trasgospec(self, project_with_catalog):
        # Arrange
        run_specify("bundle", "install", "trasgospec", cwd=project_with_catalog)

        # Act
        result = run_specify("bundle", "list", cwd=project_with_catalog)

        # Assert
        assert result.returncode == 0
        assert "trasgospec" in result.stdout
        assert "0.1.0" in result.stdout


class TestIdempotentReinstall:
    """T011: Given trasgospec already installed, When install again,
    Then exit 0, no errors, no duplicate components."""

    def test_reinstall_succeeds_without_errors(self, project_with_catalog):
        # Arrange
        run_specify("bundle", "install", "trasgospec", cwd=project_with_catalog)

        # Act
        result = run_specify("bundle", "install", "trasgospec", cwd=project_with_catalog)

        # Assert
        assert result.returncode == 0

    def test_reinstall_produces_no_duplicates(self, project_with_catalog):
        # Arrange
        run_specify("bundle", "install", "trasgospec", cwd=project_with_catalog)

        # Act
        run_specify("bundle", "install", "trasgospec", cwd=project_with_catalog)

        # Assert
        result = run_specify("bundle", "list", cwd=project_with_catalog)
        assert result.stdout.count("trasgospec") == 1


class TestInstallFromLocalPath:
    """T012: Given a clean SK project, When specify bundle install <bundle-dir>,
    Then exit 0 and bundle list shows trasgospec."""

    def test_local_path_install_succeeds(self, clean_project):
        # Act
        result = run_specify(
            "bundle", "install", str(BUNDLE_ROOT),
            cwd=clean_project,
        )

        # Assert
        assert result.returncode == 0

    def test_local_path_install_shows_in_list(self, clean_project):
        # Arrange
        run_specify("bundle", "install", str(BUNDLE_ROOT), cwd=clean_project)

        # Act
        result = run_specify("bundle", "list", cwd=clean_project)

        # Assert
        assert "trasgospec" in result.stdout
        assert "0.1.0" in result.stdout


class TestInstallInitializesProject:
    """T013: Given a directory that is NOT a SK project,
    When specify bundle install <bundle-dir>, Then project initialized and bundle installed."""

    def test_install_on_empty_dir_initializes_and_installs(self, tmp_path):
        # Arrange
        project_dir = tmp_path / "empty-project"
        project_dir.mkdir()

        # Act
        result = run_specify(
            "bundle", "install", str(BUNDLE_ROOT),
            cwd=project_dir,
        )

        # Assert
        assert result.returncode == 0
        list_result = run_specify("bundle", "list", cwd=project_dir)
        assert "trasgospec" in list_result.stdout
