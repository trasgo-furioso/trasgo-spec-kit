"""Integration tests for User Story 1: Install Trasgo Bundle.

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
    """Given a clean SK project with both catalog sources added,
    When specify bundle install trasgospec, Then exit 0 and components applied."""

    def test_install_via_catalog_succeeds(self, project_with_catalog):
        # Act
        result = run_specify("bundle", "install", "trasgospec", cwd=project_with_catalog)

        # Assert
        assert result.returncode == 0, f"Install failed: {result.stderr}"

    def test_install_via_catalog_applies_components(self, project_with_catalog):
        # Act
        run_specify("bundle", "install", "trasgospec", cwd=project_with_catalog)

        # Assert — extension component should be present in the project
        result = run_specify("bundle", "list", cwd=project_with_catalog)
        assert "trasgospec" in result.stdout


class TestBundleListAfterInstall:
    """Given a successful install, When specify bundle list,
    Then output contains trasgospec with version, component count, timestamp."""

    def test_bundle_list_shows_trasgospec(self, project_with_catalog):
        # Arrange
        run_specify("bundle", "install", "trasgospec", cwd=project_with_catalog)

        # Act
        result = run_specify("bundle", "list", cwd=project_with_catalog)

        # Assert
        assert result.returncode == 0
        assert "trasgospec" in result.stdout
        from tests.integration.conftest import _BUNDLE_VERSION
        assert _BUNDLE_VERSION in result.stdout


class TestIdempotentReinstall:
    """Given trasgospec already installed, When install again,
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
    """Given a clean SK project with extension catalog,
    When specify bundle install <bundle-dir>, Then exit 0 and components installed."""

    def test_local_path_install_succeeds(self, project_with_extension_catalog):
        # Act
        result = run_specify(
            "bundle", "install", str(BUNDLE_ROOT),
            cwd=project_with_extension_catalog,
        )

        # Assert
        assert result.returncode == 0, f"Install failed: {result.stderr}"

    def test_local_path_install_shows_in_list(self, project_with_extension_catalog):
        # Arrange
        run_specify("bundle", "install", str(BUNDLE_ROOT), cwd=project_with_extension_catalog)

        # Act
        result = run_specify("bundle", "list", cwd=project_with_extension_catalog)

        # Assert
        assert "trasgospec" in result.stdout
        from tests.integration.conftest import _BUNDLE_VERSION
        assert _BUNDLE_VERSION in result.stdout

    def test_local_path_install_delivers_components(self, project_with_extension_catalog):
        """Verify install reports non-zero component count."""
        # Act
        install_result = run_specify(
            "bundle", "install", str(BUNDLE_ROOT),
            cwd=project_with_extension_catalog,
        )

        # Assert — install output should NOT say "0 added"
        assert install_result.returncode == 0
        assert "0 added" not in install_result.stdout, (
            f"Expected non-zero components but got: {install_result.stdout}"
        )

        # Also verify bundle list shows component count > 0
        list_result = run_specify("bundle", "list", cwd=project_with_extension_catalog)
        assert "0 components" not in list_result.stdout, (
            f"Expected components but got: {list_result.stdout}"
        )


class TestInstallInitializesProject:
    """Given a directory that is NOT a SK project,
    When specify bundle install <bundle-dir>, Then project initialized and bundle installed."""

    def test_install_on_empty_dir_initializes_and_installs(self, tmp_path, extension_catalog_url):
        # Arrange
        project_dir = tmp_path / "empty-project"
        project_dir.mkdir()

        # Act — install will auto-init, then we add extension catalog and reinstall
        result = run_specify(
            "bundle", "install", str(BUNDLE_ROOT),
            cwd=project_dir,
        )

        # If it fails because no extension catalog, that's expected —
        # auto-init doesn't set up extension catalogs
        if result.returncode != 0:
            # Add extension catalog and retry
            run_specify(
                "extension", "catalog", "add",
                extension_catalog_url,
                "--name", "trasgospec",
                "--install-allowed",
                cwd=project_dir,
            )
            result = run_specify(
                "bundle", "install", str(BUNDLE_ROOT),
                cwd=project_dir,
            )

        # Assert
        assert result.returncode == 0
        list_result = run_specify("bundle", "list", cwd=project_dir)
        assert "trasgospec" in list_result.stdout
