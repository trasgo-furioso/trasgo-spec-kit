"""Unit tests for bundle/extensions/trasgospec/scripts/bash/commit.sh.

Tests validate the script's JSON contract output per
specs/011-audit-and-logs/contracts/commit-script-json.md.

Each test class creates a controlled git repository in tmp_path,
runs the script via subprocess, and asserts the JSON output.

Also includes tests for the command file frontmatter and hook
registration in extension.yml.
"""

import json
import os
import subprocess
from pathlib import Path

import yaml
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMMIT_SCRIPT = PROJECT_ROOT / "bundle" / "extensions" / "trasgospec" / "scripts" / "bash" / "commit.sh"
EXTENSION_YML = PROJECT_ROOT / "bundle" / "extensions" / "trasgospec" / "extension.yml"
COMMAND_FILE = PROJECT_ROOT / "bundle" / "extensions" / "trasgospec" / "commands" / "speckit.trasgospec.commit.md"

REQUIRED_FIELDS = [
    "changed_files",
    "new_files",
    "deleted_files",
    "has_changes",
    "branch",
    "has_remote",
    "error",
]


def init_git_repo(project_dir: Path, branch: str = "main"):
    """Initialize a git repo with an initial commit on the given branch."""
    subprocess.run(["git", "init", "-b", branch], cwd=project_dir,
                    capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=project_dir,
                    capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=project_dir,
                    capture_output=True, check=True)
    # Initial commit so branch exists
    (project_dir / ".gitkeep").write_text("")
    subprocess.run(["git", "add", "."], cwd=project_dir,
                    capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=project_dir,
                    capture_output=True, check=True)


def make_specify_project(project_dir: Path):
    """Create a minimal .specify directory with .gitignore excluding it."""
    (project_dir / ".specify").mkdir(parents=True, exist_ok=True)
    # Ensure .specify/ is gitignored (matches the feature requirement)
    gitignore = project_dir / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if ".specify/" not in content:
            gitignore.write_text(content + "\n.specify/\n")
    else:
        gitignore.write_text(".specify/\n")


def run_commit_sh(project_dir: Path) -> dict:
    """Run commit.sh against a project directory and return parsed JSON.

    This is the test helper required by T002.
    """
    result = subprocess.run(
        ["bash", str(COMMIT_SCRIPT)],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Script failed (exit {result.returncode}): {result.stderr}"
    return json.loads(result.stdout.strip())


# =============================================================================
# Phase 2: Foundational — commit.sh Script Tests (T003–T010)
# =============================================================================


class TestCommitShJsonOutput:
    """T003: Test that commit.sh outputs valid JSON with all required fields."""

    def test_outputs_valid_json_with_all_required_fields(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)

        # Act
        result = run_commit_sh(tmp_path)

        # Assert
        for field in REQUIRED_FIELDS:
            assert field in result, f"Missing required field: {field}"

    def test_output_is_single_line_json(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)

        # Act
        proc = subprocess.run(
            ["bash", str(COMMIT_SCRIPT)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        # Assert
        lines = proc.stdout.strip().split("\n")
        assert len(lines) == 1, f"Expected single line, got {len(lines)}"
        json.loads(lines[0])  # Should not raise

    def test_arrays_are_always_arrays(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)

        # Act
        result = run_commit_sh(tmp_path)

        # Assert — all array fields are lists
        assert isinstance(result["changed_files"], list)
        assert isinstance(result["new_files"], list)
        assert isinstance(result["deleted_files"], list)

    def test_has_changes_is_boolean(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)

        # Act
        result = run_commit_sh(tmp_path)

        # Assert
        assert isinstance(result["has_changes"], bool)

    def test_has_remote_is_boolean(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)

        # Act
        result = run_commit_sh(tmp_path)

        # Assert
        assert isinstance(result["has_remote"], bool)


class TestCommitShModifiedFiles:
    """T004: Test that commit.sh detects modified tracked files."""

    def test_modified_file_appears_in_changed_files(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        # Create and commit a file
        (tmp_path / "readme.md").write_text("initial content")
        subprocess.run(["git", "add", "readme.md"], cwd=tmp_path,
                        capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "add readme"], cwd=tmp_path,
                        capture_output=True, check=True)
        # Modify the file
        (tmp_path / "readme.md").write_text("modified content")

        # Act
        result = run_commit_sh(tmp_path)

        # Assert
        paths = [f["path"] for f in result["changed_files"]]
        assert "readme.md" in paths
        # Verify status field
        entry = next(f for f in result["changed_files"] if f["path"] == "readme.md")
        assert entry["status"] == "M"

    def test_modified_file_has_correct_status(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        subdir = tmp_path / "specs" / "test"
        subdir.mkdir(parents=True)
        (subdir / "spec.md").write_text("initial")
        subprocess.run(["git", "add", "."], cwd=tmp_path,
                        capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "add spec"], cwd=tmp_path,
                        capture_output=True, check=True)
        (subdir / "spec.md").write_text("modified")

        # Act
        result = run_commit_sh(tmp_path)

        # Assert
        paths = [f["path"] for f in result["changed_files"]]
        assert "specs/test/spec.md" in paths


class TestCommitShNewFiles:
    """T005: Test that commit.sh detects untracked new files."""

    def test_untracked_file_appears_in_new_files(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        # Commit gitignore first
        subprocess.run(["git", "add", ".gitignore"], cwd=tmp_path,
                        capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "add gitignore"], cwd=tmp_path,
                        capture_output=True, check=True)
        # Create new untracked file
        (tmp_path / "new-file.txt").write_text("new content")

        # Act
        result = run_commit_sh(tmp_path)

        # Assert
        paths = [f["path"] for f in result["new_files"]]
        assert "new-file.txt" in paths

    def test_new_file_has_untracked_status(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        subprocess.run(["git", "add", ".gitignore"], cwd=tmp_path,
                        capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "add gitignore"], cwd=tmp_path,
                        capture_output=True, check=True)
        (tmp_path / "brand-new.py").write_text("print('hello')")

        # Act
        result = run_commit_sh(tmp_path)

        # Assert
        entry = next(f for f in result["new_files"] if f["path"] == "brand-new.py")
        assert entry["status"] == "??"


class TestCommitShDeletedFiles:
    """T006: Test that commit.sh detects deleted files."""

    def test_deleted_file_appears_in_deleted_files(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        (tmp_path / "to-delete.txt").write_text("will be deleted")
        subprocess.run(["git", "add", "to-delete.txt"], cwd=tmp_path,
                        capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "add file"], cwd=tmp_path,
                        capture_output=True, check=True)
        # Delete the file
        os.remove(tmp_path / "to-delete.txt")

        # Act
        result = run_commit_sh(tmp_path)

        # Assert
        paths = [f["path"] for f in result["deleted_files"]]
        assert "to-delete.txt" in paths

    def test_deleted_file_has_d_status(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        (tmp_path / "gone.md").write_text("about to be deleted")
        subprocess.run(["git", "add", "gone.md"], cwd=tmp_path,
                        capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "add file"], cwd=tmp_path,
                        capture_output=True, check=True)
        os.remove(tmp_path / "gone.md")

        # Act
        result = run_commit_sh(tmp_path)

        # Assert
        entry = next(f for f in result["deleted_files"] if f["path"] == "gone.md")
        assert entry["status"] == "D"


class TestCommitShNoChanges:
    """T007: Test that commit.sh sets has_changes to false when no files changed."""

    def test_has_changes_false_when_clean(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        # Commit the gitignore so repo is clean
        subprocess.run(["git", "add", "."], cwd=tmp_path,
                        capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "commit all"], cwd=tmp_path,
                        capture_output=True, check=True)

        # Act
        result = run_commit_sh(tmp_path)

        # Assert
        assert result["has_changes"] is False
        assert result["changed_files"] == []
        assert result["new_files"] == []
        assert result["deleted_files"] == []


class TestCommitShDetachedHead:
    """T008: Test that commit.sh reports branch: null and error on detached HEAD."""

    def test_branch_null_on_detached_head(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        subprocess.run(["git", "checkout", "--detach"], cwd=tmp_path,
                        capture_output=True, check=True)

        # Act
        result = run_commit_sh(tmp_path)

        # Assert
        assert result["branch"] is None

    def test_error_message_on_detached_head(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        subprocess.run(["git", "checkout", "--detach"], cwd=tmp_path,
                        capture_output=True, check=True)

        # Act
        result = run_commit_sh(tmp_path)

        # Assert
        assert result["error"] is not None
        assert "Detached HEAD" in result["error"]


class TestCommitShSpecifyExclusion:
    """T009: Test that commit.sh excludes .specify/ files from all arrays."""

    def test_specify_files_excluded(self, tmp_path):
        # Arrange
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)
        subprocess.run(["git", "add", "."], cwd=tmp_path,
                        capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "commit gitignore"], cwd=tmp_path,
                        capture_output=True, check=True)
        # Modify a file inside .specify/
        (tmp_path / ".specify" / "feature.json").write_text('{"test": true}')
        # Also create a normal file for comparison
        (tmp_path / "normal.txt").write_text("visible")

        # Act
        result = run_commit_sh(tmp_path)

        # Assert — .specify/ files should not appear in any array
        all_paths = (
            [f["path"] for f in result["changed_files"]]
            + [f["path"] for f in result["new_files"]]
            + [f["path"] for f in result["deleted_files"]]
        )
        for path in all_paths:
            assert not path.startswith(".specify/"), \
                f".specify/ file should be excluded: {path}"
        # But the normal file should be present
        assert "normal.txt" in [f["path"] for f in result["new_files"]]


class TestCommitShRemoteDetection:
    """T010: Test that commit.sh reports has_remote correctly."""

    def test_has_remote_false_when_no_upstream(self, tmp_path):
        # Arrange — local repo with no remote
        init_git_repo(tmp_path)
        make_specify_project(tmp_path)

        # Act
        result = run_commit_sh(tmp_path)

        # Assert
        assert result["has_remote"] is False

    def test_has_remote_true_when_upstream_set(self, tmp_path):
        # Arrange — create a bare remote and set upstream
        bare = tmp_path / "bare.git"
        bare.mkdir()
        subprocess.run(["git", "init", "--bare"], cwd=bare,
                        capture_output=True, check=True)
        work = tmp_path / "work"
        work.mkdir()
        init_git_repo(work)
        make_specify_project(work)
        subprocess.run(["git", "remote", "add", "origin", str(bare)], cwd=work,
                        capture_output=True, check=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], cwd=work,
                        capture_output=True, check=True)

        # Act
        result = run_commit_sh(work)

        # Assert
        assert result["has_remote"] is True


# =============================================================================
# Phase 3: US1+US4 — Command File and Registration Tests (T013, T018)
# =============================================================================


class TestCommitCommandFrontmatter:
    """T013: Test that the command file frontmatter declares scripts.sh."""

    def test_frontmatter_declares_script(self):
        # The command file must exist and have proper frontmatter
        assert COMMAND_FILE.exists(), f"Command file not found: {COMMAND_FILE}"
        content = COMMAND_FILE.read_text()
        assert content.startswith("---"), "Command file must start with YAML frontmatter"
        end = content.index("---", 3)
        frontmatter = yaml.safe_load(content[3:end])
        assert "scripts" in frontmatter, "Frontmatter must have 'scripts' key"
        assert "sh" in frontmatter["scripts"], "Frontmatter must declare 'sh' script"
        assert frontmatter["scripts"]["sh"] == "scripts/bash/commit.sh"

    def test_frontmatter_has_description(self):
        content = COMMAND_FILE.read_text()
        end = content.index("---", 3)
        frontmatter = yaml.safe_load(content[3:end])
        assert "description" in frontmatter, "Frontmatter must have 'description' key"
        assert len(frontmatter["description"]) > 0


# =============================================================================
# Phase 5: US3 — Hook Registration Tests (T018)
# =============================================================================


EXPECTED_COMMIT_HOOK_PHASES = [
    "after_discovery",
    "after_specify",
    "after_clarify",
    "after_checklist",
    "after_plan",
    "after_tasks",
    "after_implement",
    "after_converge",
]


class TestCommitHookRegistration:
    """T018: Test that extension.yml contains after_* hook entries for all 8 phases."""

    def _load_manifest(self):
        return yaml.safe_load(EXTENSION_YML.read_text())

    def test_all_eight_phases_have_commit_hooks(self):
        manifest = self._load_manifest()
        hooks = manifest.get("hooks", {})
        for phase in EXPECTED_COMMIT_HOOK_PHASES:
            assert phase in hooks, f"Missing hook phase: {phase}"
            # hooks can be a single dict or list of dicts
            phase_hooks = hooks[phase]
            if isinstance(phase_hooks, dict):
                phase_hooks = [phase_hooks]
            elif not isinstance(phase_hooks, list):
                phase_hooks = [phase_hooks]
            commit_hooks = [
                h for h in phase_hooks
                if isinstance(h, dict) and h.get("command") == "speckit.trasgospec.commit"
            ]
            assert len(commit_hooks) >= 1, \
                f"Phase {phase} has no commit hook entry"

    def test_commit_hooks_have_priority_20(self):
        manifest = self._load_manifest()
        hooks = manifest.get("hooks", {})
        for phase in EXPECTED_COMMIT_HOOK_PHASES:
            phase_hooks = hooks.get(phase, [])
            if isinstance(phase_hooks, dict):
                phase_hooks = [phase_hooks]
            for h in phase_hooks:
                if isinstance(h, dict) and h.get("command") == "speckit.trasgospec.commit":
                    assert h.get("priority") == 20, \
                        f"Commit hook at {phase} should have priority 20, got {h.get('priority')}"

    def test_commit_hooks_are_mandatory(self):
        manifest = self._load_manifest()
        hooks = manifest.get("hooks", {})
        for phase in EXPECTED_COMMIT_HOOK_PHASES:
            phase_hooks = hooks.get(phase, [])
            if isinstance(phase_hooks, dict):
                phase_hooks = [phase_hooks]
            for h in phase_hooks:
                if isinstance(h, dict) and h.get("command") == "speckit.trasgospec.commit":
                    assert h.get("optional") is False, \
                        f"Commit hook at {phase} should be mandatory (optional: false)"

    def test_commit_hooks_description(self):
        manifest = self._load_manifest()
        hooks = manifest.get("hooks", {})
        for phase in EXPECTED_COMMIT_HOOK_PHASES:
            phase_hooks = hooks.get(phase, [])
            if isinstance(phase_hooks, dict):
                phase_hooks = [phase_hooks]
            for h in phase_hooks:
                if isinstance(h, dict) and h.get("command") == "speckit.trasgospec.commit":
                    assert h.get("description") == "Audit — auto-commit and push", \
                        f"Commit hook at {phase} has wrong description: {h.get('description')}"
