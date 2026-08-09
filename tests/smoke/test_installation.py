"""Smoke tests for trasgospec bundle installation.

Verifies the full user-facing installation flow:
  git init → specify init → bundle catalog add → bundle install → verify

Requires network access to raw.githubusercontent.com and the
current branch pushed to origin.
"""

import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Detect current branch from the real repo (not tmp_path)
_branch_result = subprocess.run(
    ["git", "branch", "--show-current"],
    cwd=PROJECT_ROOT,
    capture_output=True,
    text=True,
)
BRANCH = _branch_result.stdout.strip() or "main"
CATALOG_URL = (
    f"https://raw.githubusercontent.com/trasgo-furioso/"
    f"trasgo-spec-kit/{BRANCH}/catalog.json"
)


def run_specify(*args, cwd):
    """Run a specify CLI command and return the result."""
    return subprocess.run(
        ["specify", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def assert_command_ok(result, label):
    """Assert a specify command succeeded with a descriptive message."""
    assert result.returncode == 0, (
        f"{label} failed (exit {result.returncode})\n"
        f"  stdout: {result.stdout.strip()}\n"
        f"  stderr: {result.stderr.strip()}\n"
        f"  args: {result.args}"
    )


@pytest.fixture
def clean_project(tmp_path):
    """Create a clean git repo with specify init."""
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
    result = run_specify("init", "--here", "--integration", "claude", "--force", cwd=tmp_path)
    assert_command_ok(result, "specify init")
    return tmp_path


@pytest.fixture
def project_with_bundle(clean_project):
    """Clean project with trasgospec bundle installed."""
    result = run_specify("bundle", "catalog", "add", CATALOG_URL, cwd=clean_project)
    assert_command_ok(result, f"bundle catalog add {CATALOG_URL}")
    result = run_specify("bundle", "install", "trasgospec", cwd=clean_project)
    assert_command_ok(result, "bundle install trasgospec")
    return clean_project


class TestBundleInstallation:
    """Smoke test: install trasgospec from the current branch's catalog."""

    def test_add_catalog(self, clean_project):
        result = run_specify("bundle", "catalog", "add", CATALOG_URL, cwd=clean_project)
        assert_command_ok(result, f"bundle catalog add {CATALOG_URL}")

    def test_install_bundle(self, clean_project):
        run_specify("bundle", "catalog", "add", CATALOG_URL, cwd=clean_project)
        result = run_specify("bundle", "install", "trasgospec", cwd=clean_project)
        assert_command_ok(result, "bundle install trasgospec")

    def test_bundle_list_shows_trasgospec(self, project_with_bundle):
        result = run_specify("bundle", "list", cwd=project_with_bundle)
        assert_command_ok(result, "bundle list")
        assert "trasgospec" in result.stdout, (
            f"'trasgospec' not found in bundle list output:\n{result.stdout}"
        )

    def test_extension_list_shows_trasgospec(self, project_with_bundle):
        result = run_specify("extension", "list", cwd=project_with_bundle)
        assert_command_ok(result, "extension list")
        assert "trasgospec" in result.stdout, (
            f"'trasgospec' not found in extension list output:\n{result.stdout}"
        )
