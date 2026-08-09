"""Integration tests for the commit command.

Tests validate the end-to-end behavior of the commit command by
running commit.sh in a realistic git environment and verifying
the JSON output matches expected patterns.

US1: After creating files in a test repo, verify the commit
     command produces correct structured output for the AI to
     process.
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMMIT_SCRIPT = PROJECT_ROOT / "bundle" / "extensions" / "trasgospec" / "scripts" / "bash" / "commit.sh"


def init_git_repo(project_dir: Path, branch: str = "main"):
    """Initialize a git repo with an initial commit."""
    subprocess.run(["git", "init", "-b", branch], cwd=project_dir,
                    capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=project_dir,
                    capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=project_dir,
                    capture_output=True, check=True)
    (project_dir / ".gitkeep").write_text("")
    subprocess.run(["git", "add", "."], cwd=project_dir,
                    capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=project_dir,
                    capture_output=True, check=True)


def make_specify_project(project_dir: Path):
    """Create a minimal .specify directory with .gitignore."""
    (project_dir / ".specify").mkdir(parents=True, exist_ok=True)
    gitignore = project_dir / ".gitignore"
    gitignore.write_text(".specify/\n")


def run_commit_sh(project_dir: Path) -> dict:
    """Run commit.sh against a project directory and return parsed JSON."""
    result = subprocess.run(
        ["bash", str(COMMIT_SCRIPT)],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    return json.loads(result.stdout.strip())


class TestCommitIntegrationMultipleFiles:
    """T014: Integration test — commit command detects multiple file changes."""

    def test_multiple_new_files_detected(self, tmp_path):
        """After creating files in a test repo, the commit script detects them all."""
        # Arrange — set up repo and create multiple files
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        subprocess.run(["git", "add", ".gitignore"], cwd=tmp_path,
                        capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "add gitignore"], cwd=tmp_path,
                        capture_output=True, check=True)

        # Create files in different directories (simulating a skill run)
        specs_dir = tmp_path / "specs" / "test-feature"
        specs_dir.mkdir(parents=True)
        (specs_dir / "spec.md").write_text("# Feature Specification: Test\n")
        (specs_dir / "plan.md").write_text("# Plan\n")
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir(parents=True)
        (tests_dir / "test_feature.py").write_text("def test_pass(): pass\n")

        # Act
        result = run_commit_sh(tmp_path)

        # Assert — all new files detected
        assert result["has_changes"] is True
        new_paths = [f["path"] for f in result["new_files"]]
        assert "specs/test-feature/spec.md" in new_paths
        assert "specs/test-feature/plan.md" in new_paths
        assert "tests/test_feature.py" in new_paths

    def test_mixed_changes_detected(self, tmp_path):
        """Detects a mix of modified, new, and deleted files."""
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        (tmp_path / "existing.md").write_text("original")
        (tmp_path / "to-delete.txt").write_text("will go away")
        subprocess.run(["git", "add", "."], cwd=tmp_path,
                        capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "add files"], cwd=tmp_path,
                        capture_output=True, check=True)

        # Modify one, delete one, add new one
        (tmp_path / "existing.md").write_text("modified")
        os.remove(tmp_path / "to-delete.txt")
        (tmp_path / "brand-new.py").write_text("print('new')")

        # Act
        result = run_commit_sh(tmp_path)

        # Assert
        assert result["has_changes"] is True
        changed_paths = [f["path"] for f in result["changed_files"]]
        new_paths = [f["path"] for f in result["new_files"]]
        deleted_paths = [f["path"] for f in result["deleted_files"]]
        assert "existing.md" in changed_paths
        assert "brand-new.py" in new_paths
        assert "to-delete.txt" in deleted_paths

    def test_message_format_contract(self, tmp_path):
        """Each file entry has path and status fields matching the contract."""
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        subprocess.run(["git", "add", "."], cwd=tmp_path,
                        capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "clean"], cwd=tmp_path,
                        capture_output=True, check=True)
        (tmp_path / "readme.md").write_text("# README")

        # Act
        result = run_commit_sh(tmp_path)

        # Assert — each entry in new_files has path and status
        for entry in result["new_files"]:
            assert "path" in entry, "Entry missing 'path' field"
            assert "status" in entry, "Entry missing 'status' field"
            assert isinstance(entry["path"], str)
            assert isinstance(entry["status"], str)
