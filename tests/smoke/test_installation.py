"""Smoke tests for trasgospec bundle installation.

Verifies the full user-facing installation flow:
  git init → specify init → bundle add → bundle install → verify

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


@pytest.fixture
def clean_project(tmp_path):
    """Create a clean git repo with specify init."""
    subprocess.run(
        ["git", "init"],
        cwd=tmp_path,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=tmp_path,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=tmp_path,
        capture_output=True,
    )
    result = run_specify("init", "--here", "--integration", "claude", "--force", cwd=tmp_path)
    assert result.returncode == 0, f"specify init failed: {result.stderr}"
    return tmp_path


class TestBundleInstallation:
    """Smoke test: install trasgospec from the current branch's catalog."""

    def test_add_catalog(self, clean_project):
        result = run_specify("bundle", "catalog", "add", CATALOG_URL, cwd=clean_project)
        assert result.returncode == 0, f"bundle catalog add failed: {result.stderr}"

    def test_install_bundle(self, clean_project):
        run_specify("bundle", "catalog", "add", CATALOG_URL, cwd=clean_project)
        result = run_specify("bundle", "install", "trasgospec", cwd=clean_project)
        assert result.returncode == 0, f"bundle install failed: {result.stderr}"

    def test_bundle_list_shows_trasgospec(self, clean_project):
        run_specify("bundle", "catalog", "add", CATALOG_URL, cwd=clean_project)
        run_specify("bundle", "install", "trasgospec", cwd=clean_project)
        result = run_specify("bundle", "list", cwd=clean_project)
        assert result.returncode == 0
        assert "trasgospec" in result.stdout

    def test_extension_list_shows_trasgospec(self, clean_project):
        run_specify("bundle", "catalog", "add", CATALOG_URL, cwd=clean_project)
        run_specify("bundle", "install", "trasgospec", cwd=clean_project)
        result = run_specify("extension", "list", cwd=clean_project)
        assert result.returncode == 0
        assert "trasgospec" in result.stdout
