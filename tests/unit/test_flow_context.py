"""Unit tests for bundle/extensions/trasgospec/scripts/bash/flow-context.sh.

Tests validate the script's JSON contract output per
specs/005-github-flow-enforcement/contracts/flow-context-output.md.

Each test class creates a controlled git repository in tmp_path,
runs the script via subprocess, and asserts the JSON output.
"""

import json
import os
import subprocess
import time
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FLOW_CONTEXT_SCRIPT = PROJECT_ROOT / "bundle" / "extensions" / "trasgospec" / "scripts" / "bash" / "flow-context.sh"

REQUIRED_FIELDS = [
    "current_branch",
    "is_main",
    "spec_dir",
    "expected_branch",
    "spec_branch_match",
    "branch_age_days",
    "commits_behind_main",
    "uncommitted_changes",
]


def init_git_repo(project_dir: Path, branch: str = "main"):
    """Initialize a git repo with an initial commit on the given branch."""
    subprocess.run(["git", "init", "-b", branch], cwd=project_dir,
                    capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=project_dir,
                    capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=project_dir,
                    capture_output=True, check=True)
    # Initial commit so main branch exists
    (project_dir / ".gitkeep").write_text("")
    subprocess.run(["git", "add", "."], cwd=project_dir,
                    capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=project_dir,
                    capture_output=True, check=True)


def make_specify_project(project_dir: Path):
    """Create a minimal .specify directory."""
    (project_dir / ".specify").mkdir(parents=True, exist_ok=True)


def create_feature_json(project_dir: Path, feature_dir: str):
    """Create .specify/feature.json pointing to a feature directory."""
    specify_dir = project_dir / ".specify"
    specify_dir.mkdir(parents=True, exist_ok=True)
    (specify_dir / "feature.json").write_text(
        json.dumps({"feature_directory": feature_dir})
    )


def create_spec_with_branch(project_dir: Path, spec_dir: str, branch_name: str):
    """Create a spec.md with a Feature Branch field."""
    spec_path = project_dir / spec_dir
    spec_path.mkdir(parents=True, exist_ok=True)
    (spec_path / "spec.md").write_text(
        f"# Feature Specification: Test Feature\n\n"
        f"**Feature Branch**: `{branch_name}`\n\n"
        f"**Status**: Draft\n"
    )


def run_flow_context(project_dir: Path) -> dict:
    """Run flow-context.sh against a project directory and return parsed JSON."""
    result = subprocess.run(
        ["bash", str(FLOW_CONTEXT_SCRIPT)],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Script failed (exit {result.returncode}): {result.stderr}"
    return json.loads(result.stdout.strip())


class TestFlowContextValidJson:
    """T004: Test flow-context.sh outputs valid JSON with all required fields."""

    def test_outputs_valid_json_with_all_required_fields(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)

        # Act
        result = run_flow_context(tmp_path)

        # Assert
        for field in REQUIRED_FIELDS:
            assert field in result, f"Missing required field: {field}"

    def test_output_is_single_line_json(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)

        # Act
        proc = subprocess.run(
            ["bash", str(FLOW_CONTEXT_SCRIPT)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        # Assert
        lines = proc.stdout.strip().split("\n")
        assert len(lines) == 1, f"Expected single line, got {len(lines)}"
        json.loads(lines[0])  # Should not raise


class TestFlowContextMainBranch:
    """T005: Test flow-context.sh reports is_main correctly."""

    def test_is_main_true_on_main_branch(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)

        # Act
        result = run_flow_context(tmp_path)

        # Assert
        assert result["is_main"] is True
        assert result["current_branch"] == "main"

    def test_is_main_false_on_feature_branch(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        subprocess.run(["git", "checkout", "-b", "my-feature"], cwd=tmp_path,
                        capture_output=True, check=True)

        # Act
        result = run_flow_context(tmp_path)

        # Assert
        assert result["is_main"] is False
        assert result["current_branch"] == "my-feature"


class TestFlowContextDetachedHead:
    """T006: Test flow-context.sh reports current_branch as null on detached HEAD."""

    def test_current_branch_null_on_detached_head(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        # Detach HEAD
        subprocess.run(["git", "checkout", "--detach"], cwd=tmp_path,
                        capture_output=True, check=True)

        # Act
        result = run_flow_context(tmp_path)

        # Assert
        assert result["current_branch"] is None
        assert result["is_main"] is False


class TestFlowContextExpectedBranch:
    """T007: Test flow-context.sh reads expected_branch from spec.md."""

    def test_reads_expected_branch_from_spec_md(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        create_feature_json(tmp_path, "specs/005-test-feature")
        create_spec_with_branch(tmp_path, "specs/005-test-feature", "005-test-feature")

        # Act
        result = run_flow_context(tmp_path)

        # Assert
        assert result["expected_branch"] == "005-test-feature"

    def test_expected_branch_preserves_exact_value(self, tmp_path):
        # Arrange — branch name with no prefix, just as written
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        create_feature_json(tmp_path, "specs/005-my-feature")
        create_spec_with_branch(tmp_path, "specs/005-my-feature", "custom/branch-name")

        # Act
        result = run_flow_context(tmp_path)

        # Assert — no prefix added, value used as-is
        assert result["expected_branch"] == "custom/branch-name"


class TestFlowContextBranchMatch:
    """T008: Test spec_branch_match when current branch matches expected_branch."""

    def test_spec_branch_match_true_when_matching(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        create_feature_json(tmp_path, "specs/005-test")
        create_spec_with_branch(tmp_path, "specs/005-test", "005-test")
        subprocess.run(["git", "checkout", "-b", "005-test"], cwd=tmp_path,
                        capture_output=True, check=True)

        # Act
        result = run_flow_context(tmp_path)

        # Assert
        assert result["spec_branch_match"] is True

    def test_spec_branch_match_false_when_not_matching(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        create_feature_json(tmp_path, "specs/005-test")
        create_spec_with_branch(tmp_path, "specs/005-test", "005-test")
        subprocess.run(["git", "checkout", "-b", "wrong-branch"], cwd=tmp_path,
                        capture_output=True, check=True)

        # Act
        result = run_flow_context(tmp_path)

        # Assert
        assert result["spec_branch_match"] is False


class TestFlowContextNoFeatureJson:
    """T009: Test spec_branch_match is null when feature.json is missing."""

    def test_spec_branch_match_null_when_no_feature_json(self, tmp_path):
        # Arrange — no feature.json
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)

        # Act
        result = run_flow_context(tmp_path)

        # Assert
        assert result["spec_dir"] is None
        assert result["expected_branch"] is None
        assert result["spec_branch_match"] is None


class TestFlowContextNoFeatureBranchField:
    """T010: Test expected_branch is null when spec.md has no Feature Branch field."""

    def test_expected_branch_null_when_field_missing(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        create_feature_json(tmp_path, "specs/005-test")
        spec_dir = tmp_path / "specs" / "005-test"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text(
            "# Feature Specification: Test\n\n**Status**: Draft\n"
        )

        # Act
        result = run_flow_context(tmp_path)

        # Assert
        assert result["spec_dir"] == "specs/005-test"
        assert result["expected_branch"] is None
        assert result["spec_branch_match"] is None


class TestFlowContextBranchAgeAndDivergence:
    """T011: Test branch_age_days and commits_behind_main computation."""

    def test_branch_age_zero_on_main(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)

        # Act
        result = run_flow_context(tmp_path)

        # Assert
        assert result["branch_age_days"] == 0
        assert result["commits_behind_main"] == 0

    def test_commits_behind_main_detected(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        # Create feature branch
        subprocess.run(["git", "checkout", "-b", "my-feature"], cwd=tmp_path,
                        capture_output=True, check=True)
        # Go back to main and add a commit
        subprocess.run(["git", "checkout", "main"], cwd=tmp_path,
                        capture_output=True, check=True)
        (tmp_path / "new-file.txt").write_text("content")
        subprocess.run(["git", "add", "new-file.txt"], cwd=tmp_path,
                        capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "main commit"], cwd=tmp_path,
                        capture_output=True, check=True)
        # Switch back to feature branch
        subprocess.run(["git", "checkout", "my-feature"], cwd=tmp_path,
                        capture_output=True, check=True)

        # Act
        result = run_flow_context(tmp_path)

        # Assert
        assert result["commits_behind_main"] == 1

    def test_uncommitted_changes_detected(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        (tmp_path / "dirty-file.txt").write_text("uncommitted")

        # Act
        result = run_flow_context(tmp_path)

        # Assert
        assert result["uncommitted_changes"] is True

    def test_no_uncommitted_changes_when_clean(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)

        # Act
        result = run_flow_context(tmp_path)

        # Assert
        assert result["uncommitted_changes"] is False
