"""Unit tests for the flow-gate command behavior.

The flow-gate command uses flow-context.sh output to decide whether to
block (on main) or pass (on feature branch). These tests validate the
flow-context.sh output provides the data the command file needs to make
gate decisions.

Since the command file is AI-driven markdown, we test the script layer:
flow-context.sh produces JSON that encodes the gate decision inputs.
"""

import json
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FLOW_CONTEXT_SCRIPT = PROJECT_ROOT / "bundle" / "extensions" / "trasgospec" / "scripts" / "bash" / "flow-context.sh"


def init_git_repo(project_dir: Path, branch: str = "main"):
    """Initialize a git repo with an initial commit on the given branch."""
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


class TestFlowGateBlocksOnMain:
    """T014: Test flow-gate blocks when on main (is_main=true → gate should block)."""

    def test_gate_block_data_on_main(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        create_feature_json(tmp_path, "specs/005-test")
        create_spec_with_branch(tmp_path, "specs/005-test", "005-test")

        # Act
        result = run_flow_context(tmp_path)

        # Assert — command file should block based on these values
        assert result["is_main"] is True
        assert result["current_branch"] == "main"
        assert result["expected_branch"] == "005-test"

    def test_gate_block_data_on_main_without_feature_json(self, tmp_path):
        # Arrange — no feature.json, gate should still detect main
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)

        # Act
        result = run_flow_context(tmp_path)

        # Assert
        assert result["is_main"] is True
        assert result["expected_branch"] is None


class TestFlowGatePassesOnFeatureBranch:
    """T015: Test flow-gate passes when on correct feature branch."""

    def test_gate_pass_data_on_matching_feature_branch(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        create_feature_json(tmp_path, "specs/005-test")
        create_spec_with_branch(tmp_path, "specs/005-test", "005-test")
        subprocess.run(["git", "checkout", "-b", "005-test"], cwd=tmp_path,
                        capture_output=True, check=True)

        # Act
        result = run_flow_context(tmp_path)

        # Assert — command file should pass based on these values
        assert result["is_main"] is False
        assert result["current_branch"] == "005-test"
        assert result["spec_branch_match"] is True

    def test_gate_pass_on_any_non_main_branch(self, tmp_path):
        # Arrange — different branch, no spec context
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        subprocess.run(["git", "checkout", "-b", "some-branch"], cwd=tmp_path,
                        capture_output=True, check=True)

        # Act
        result = run_flow_context(tmp_path)

        # Assert
        assert result["is_main"] is False
        assert result["current_branch"] == "some-branch"


class TestFlowGateMismatchWarning:
    """T016: Test mismatch warning when branch doesn't match expected_branch."""

    def test_mismatch_data_when_wrong_branch(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        create_feature_json(tmp_path, "specs/005-test")
        create_spec_with_branch(tmp_path, "specs/005-test", "005-test")
        subprocess.run(["git", "checkout", "-b", "wrong-branch"], cwd=tmp_path,
                        capture_output=True, check=True)

        # Act
        result = run_flow_context(tmp_path)

        # Assert — command file should warn based on these values
        assert result["is_main"] is False
        assert result["spec_branch_match"] is False
        assert result["expected_branch"] == "005-test"
        assert result["current_branch"] == "wrong-branch"


class TestFlowGateDetachedHead:
    """T017: Test flow-gate blocks on detached HEAD."""

    def test_gate_block_data_on_detached_head(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        subprocess.run(["git", "checkout", "--detach"], cwd=tmp_path,
                        capture_output=True, check=True)

        # Act
        result = run_flow_context(tmp_path)

        # Assert — command file should block: no branch name
        assert result["current_branch"] is None
        assert result["is_main"] is False
