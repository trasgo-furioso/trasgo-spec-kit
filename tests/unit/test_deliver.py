"""Unit tests for bundle/extensions/trasgospec/scripts/bash/deliver.sh.

Tests validate the deliver script's JSON contract output (renamed from flow-nudge.sh)
and verify extension.yml hook registrations use optional: false.

Each test creates a controlled project structure in tmp_path,
runs the script via subprocess, and asserts the JSON output.
"""

import json
import subprocess
from pathlib import Path

import pytest
import re

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DELIVER_SCRIPT = PROJECT_ROOT / "bundle" / "extensions" / "trasgospec" / "scripts" / "bash" / "deliver.sh"
EXTENSION_YML = PROJECT_ROOT / "bundle" / "extensions" / "trasgospec" / "extension.yml"
PR_TEMPLATE = PROJECT_ROOT / "bundle" / "presets" / "trasgospec" / "templates" / "pr-template.md"
COMMIT_TEMPLATE = PROJECT_ROOT / "bundle" / "presets" / "trasgospec" / "templates" / "commit-template.md"


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


def run_deliver(project_dir: Path, env_override: dict = None) -> dict:
    """Run deliver.sh against a project directory and return parsed JSON."""
    env = dict(subprocess.os.environ)
    if env_override:
        env.update(env_override)
    result = subprocess.run(
        ["bash", str(DELIVER_SCRIPT)],
        cwd=project_dir,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, f"Script failed (exit {result.returncode}): {result.stderr}"
    return json.loads(result.stdout.strip())


class TestDeliverJsonContract:
    """T004: Verify deliver.sh produces valid JSON with required fields."""

    def test_output_is_valid_json(self, tmp_path):
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        create_feature_json(tmp_path, "specs/012-test")
        create_spec_with_branch(tmp_path, "specs/012-test", "012-test")
        subprocess.run(["git", "checkout", "-b", "012-test"], cwd=tmp_path,
                        capture_output=True, check=True)

        result = run_deliver(tmp_path)

        assert "flow_context" in result
        assert "gh_available" in result
        assert "gh_integration" in result
        assert "has_open_pr" in result
        assert "pr_is_draft" in result
        assert "pr_number" in result
        assert "pr_url" in result
        assert "inferred_phase" in result
        assert "suggested_action" in result

    def test_exits_code_zero(self, tmp_path):
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        create_feature_json(tmp_path, "specs/012-test")
        create_spec_with_branch(tmp_path, "specs/012-test", "012-test")
        subprocess.run(["git", "checkout", "-b", "012-test"], cwd=tmp_path,
                        capture_output=True, check=True)

        env = dict(subprocess.os.environ)
        result = subprocess.run(
            ["bash", str(DELIVER_SCRIPT)],
            cwd=tmp_path, capture_output=True, text=True, env=env,
        )
        assert result.returncode == 0


class TestDeliverHookRegistrations:
    """T011: Verify all deliver hooks in extension.yml have optional: false."""

    def test_all_deliver_hooks_are_mandatory(self):
        content = EXTENSION_YML.read_text()
        # Find all blocks that reference deliver command
        # Pattern: command: "speckit.trasgospec.deliver" followed by optional: <value>
        deliver_blocks = re.findall(
            r'command:\s*"speckit\.trasgospec\.deliver"\s*\n\s*optional:\s*(true|false)',
            content
        )
        assert len(deliver_blocks) >= 4, (
            f"Expected at least 4 deliver hook registrations, found {len(deliver_blocks)}"
        )
        for i, val in enumerate(deliver_blocks):
            assert val == "false", (
                f"Deliver hook registration #{i+1} has optional: {val}, expected false"
            )


class TestPrTemplateExists:
    """T015: Verify pr-template.md exists and has required frontmatter."""

    def test_pr_template_exists(self):
        assert PR_TEMPLATE.exists(), f"pr-template.md not found at {PR_TEMPLATE}"

    def test_pr_template_has_title_in_frontmatter(self):
        content = PR_TEMPLATE.read_text()
        assert "title:" in content, "pr-template.md missing title in frontmatter"
        assert "{{spec_title}}" in content, "pr-template.md missing {{spec_title}} placeholder"


class TestCommitTemplateExists:
    """T019: Verify commit-template.md exists."""

    def test_commit_template_exists(self):
        assert COMMIT_TEMPLATE.exists(), f"commit-template.md not found at {COMMIT_TEMPLATE}"


class TestDeliverFallback:
    """T023: Verify deliver.sh exits code 0 when gh is not available."""

    def test_exits_zero_without_gh(self, tmp_path):
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        create_feature_json(tmp_path, "specs/012-test")
        create_spec_with_branch(tmp_path, "specs/012-test", "012-test")
        subprocess.run(["git", "checkout", "-b", "012-test"], cwd=tmp_path,
                        capture_output=True, check=True)

        # Use minimal PATH without gh
        git_path = subprocess.run(["which", "git"], capture_output=True, text=True).stdout.strip()
        git_dir = str(Path(git_path).parent)
        minimal_path = f"{git_dir}:/usr/bin:/bin"

        env = dict(subprocess.os.environ)
        env["PATH"] = minimal_path
        result = subprocess.run(
            ["bash", str(DELIVER_SCRIPT)],
            cwd=tmp_path, capture_output=True, text=True, env=env,
        )
        assert result.returncode == 0

    def test_has_suggested_action_without_gh(self, tmp_path):
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        create_feature_json(tmp_path, "specs/012-test")
        create_spec_with_branch(tmp_path, "specs/012-test", "012-test")
        (tmp_path / "specs" / "012-test" / "plan.md").write_text("# Plan\n")
        subprocess.run(["git", "checkout", "-b", "012-test"], cwd=tmp_path,
                        capture_output=True, check=True)

        git_path = subprocess.run(["which", "git"], capture_output=True, text=True).stdout.strip()
        git_dir = str(Path(git_path).parent)
        minimal_path = f"{git_dir}:/usr/bin:/bin"

        result = run_deliver(tmp_path, env_override={"PATH": minimal_path})
        assert result["suggested_action"] in ("create_draft", "mark_ready", "final_review", "none")
