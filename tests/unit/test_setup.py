"""Unit tests for scripts/setup.sh.

Tests validate the setup script configures git core.hooksPath,
is idempotent, and handles error cases.
"""

import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SETUP_SCRIPT = PROJECT_ROOT / "scripts" / "setup.sh"


def make_git_repo_with_githooks(path: Path) -> Path:
    """Create a git repo with a .githooks/ directory."""
    subprocess.run(["git", "init", str(path)], capture_output=True, check=True)
    (path / ".githooks").mkdir()
    return path


def run_setup(path: Path) -> subprocess.CompletedProcess:
    """Run the setup script."""
    return subprocess.run(
        ["bash", str(SETUP_SCRIPT)],
        cwd=path,
        capture_output=True,
        text=True,
    )


def get_hooks_path(path: Path) -> str:
    """Get the configured core.hooksPath."""
    result = subprocess.run(
        ["git", "-C", str(path), "config", "core.hooksPath"],
        capture_output=True, text=True,
    )
    return result.stdout.strip()


class TestSetupScript:
    """Verify setup script configures git hooks correctly."""

    def test_configures_hooks_path(self, tmp_path):
        """Setup should set core.hooksPath to .githooks."""
        make_git_repo_with_githooks(tmp_path)

        result = run_setup(tmp_path)

        assert result.returncode == 0
        assert get_hooks_path(tmp_path) == ".githooks"

    def test_idempotent_second_run(self, tmp_path):
        """Running setup twice should succeed without errors."""
        make_git_repo_with_githooks(tmp_path)

        result1 = run_setup(tmp_path)
        result2 = run_setup(tmp_path)

        assert result1.returncode == 0
        assert result2.returncode == 0
        assert get_hooks_path(tmp_path) == ".githooks"

    def test_exits_with_error_outside_git_repo(self, tmp_path):
        """Setup should fail with clear error when not in a git repo."""
        # tmp_path is NOT a git repo
        result = run_setup(tmp_path)

        assert result.returncode != 0
        assert "git" in result.stderr.lower() or "not" in result.stderr.lower()
