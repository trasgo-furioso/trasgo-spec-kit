"""Unit tests for bundle/extensions/trasgospec/scripts/bash/status-change.sh.

Tests validate the status management script's JSON contract output per
specs/009-spec-lifecycle-management/contracts/status-change-contract.md.

Each test class creates a controlled project structure in tmp_path,
runs the script via subprocess, and asserts the JSON output.
"""

import json
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATUS_CHANGE_SCRIPT = PROJECT_ROOT / "bundle" / "extensions" / "trasgospec" / "scripts" / "bash" / "status-change.sh"

VALID_PHASES = [
    "Discovery", "Opportunity", "Planning", "Ready to Dev",
    "In Progress", "In Review", "Delivered", "Blocked",
]


def make_specify_project(project_dir: Path, feature_dir: str = None):
    """Create a minimal .specify directory with optional feature.json."""
    specify = project_dir / ".specify"
    specify.mkdir(parents=True, exist_ok=True)
    if feature_dir:
        (specify / "feature.json").write_text(
            json.dumps({"feature_directory": feature_dir})
        )


def create_spec_with_status(project_dir: Path, feature_dir: str, status: str):
    """Create a spec.md with a Status field."""
    spec_dir = project_dir / feature_dir
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(
        f"# Feature Specification: Test\n\n**Status**: {status}\n\n**Created**: 2026-08-09\n"
    )
    return spec_dir


def create_prd_with_status(project_dir: Path, feature_dir: str, status: str,
                           complete: bool = True):
    """Create a prd.md with a Status field and optionally all required sections."""
    spec_dir = project_dir / feature_dir
    spec_dir.mkdir(parents=True, exist_ok=True)
    content = f"# PRD: Test PRD\n\n**Created**: 2026-08-09\n**Status**: {status}\n\n"
    if complete:
        content += (
            "## Problem Statement\n\n"
            "**Pain Point**: Something hurts\n\n"
            "**Who**: Developers\n\n"
            "**Current Alternatives**: Nothing\n\n"
            "**Desired Outcome**: Something better\n\n"
            "## Jobs to Be Done\n\n"
            "- When I do X, I want to Y, so I can Z\n\n"
            "## Assumptions\n\n"
            "- Assumption one\n"
        )
    else:
        content += "## Problem Statement\n\n**Pain Point**: Something hurts\n"
    (spec_dir / "prd.md").write_text(content)
    return spec_dir


def run_status_change(project_dir: Path, *args) -> dict:
    """Run status-change.sh and return parsed JSON."""
    cmd = ["bash", str(STATUS_CHANGE_SCRIPT)] + list(args)
    result = subprocess.run(
        cmd,
        cwd=project_dir,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout.strip()), result.returncode


# ---------------------------------------------------------------------------
# US3: Set status to a valid phase
# ---------------------------------------------------------------------------
class TestSetStatus:
    """Verify the script sets status to valid lifecycle phases."""

    def test_sets_status_to_valid_phase(self, tmp_path):
        make_specify_project(tmp_path, "specs/001-test")
        create_spec_with_status(tmp_path, "specs/001-test", "Draft")
        data, rc = run_status_change(tmp_path, "set", "planning")
        assert data["success"] is True
        assert data["new_status"] == "Planning"
        # Verify file was actually updated
        content = (tmp_path / "specs/001-test/spec.md").read_text()
        assert "**Status**: Planning" in content

    def test_rejects_invalid_phase(self, tmp_path):
        make_specify_project(tmp_path, "specs/001-test")
        create_spec_with_status(tmp_path, "specs/001-test", "Draft")
        data, rc = run_status_change(tmp_path, "set", "bogus")
        assert data["success"] is False
        assert "valid_phases" in data

    def test_selects_spec_over_prd(self, tmp_path):
        make_specify_project(tmp_path, "specs/001-test")
        create_spec_with_status(tmp_path, "specs/001-test", "Draft")
        create_prd_with_status(tmp_path, "specs/001-test", "Discovery")
        data, rc = run_status_change(tmp_path, "set", "planning")
        assert data["file"] == "spec.md"
        assert data["old_status"] == "Draft"

    def test_selects_prd_when_no_spec(self, tmp_path):
        make_specify_project(tmp_path, "specs/001-test")
        create_prd_with_status(tmp_path, "specs/001-test", "Discovery")
        data, rc = run_status_change(tmp_path, "set", "opportunity")
        assert data["file"] == "prd.md"

    def test_sets_blocked_status(self, tmp_path):
        make_specify_project(tmp_path, "specs/001-test")
        create_spec_with_status(tmp_path, "specs/001-test", "Planning")
        data, rc = run_status_change(tmp_path, "set", "blocked")
        assert data["success"] is True
        assert data["new_status"] == "Blocked"

    def test_case_insensitive_input(self, tmp_path):
        make_specify_project(tmp_path, "specs/001-test")
        create_spec_with_status(tmp_path, "specs/001-test", "Draft")
        data, rc = run_status_change(tmp_path, "set", "PLANNING")
        assert data["success"] is True
        assert data["new_status"] == "Planning"

    def test_multi_word_phase(self, tmp_path):
        make_specify_project(tmp_path, "specs/001-test")
        create_spec_with_status(tmp_path, "specs/001-test", "Planning")
        data, rc = run_status_change(tmp_path, "set", "ready to dev")
        assert data["success"] is True
        assert data["new_status"] == "Ready to Dev"

    def test_hyphenated_phase_input(self, tmp_path):
        make_specify_project(tmp_path, "specs/001-test")
        create_spec_with_status(tmp_path, "specs/001-test", "Planning")
        data, rc = run_status_change(tmp_path, "set", "ready-to-dev")
        assert data["success"] is True
        assert data["new_status"] == "Ready to Dev"


# ---------------------------------------------------------------------------
# US3: Validate action
# ---------------------------------------------------------------------------
class TestValidateStatus:
    """Verify the validate action reports current status."""

    def test_validate_reports_current_status(self, tmp_path):
        make_specify_project(tmp_path, "specs/001-test")
        create_spec_with_status(tmp_path, "specs/001-test", "In Progress")
        data, rc = run_status_change(tmp_path, "validate")
        assert data["success"] is True
        assert data["old_status"] == "In Progress"
