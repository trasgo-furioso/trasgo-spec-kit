"""Integration tests for User Story 1: View Project Roadmap.

Tests follow Given (Arrange) / When (Act) / Then (Assert) pattern
mapped from spec acceptance scenarios.
"""

import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCAN_SPECS_SCRIPT = PROJECT_ROOT / "bundle" / "scripts" / "bash" / "scan-specs.sh"


def run_scan_specs(project_dir: Path) -> dict:
    """Run scan-specs.sh against a project directory and return parsed JSON."""
    result = subprocess.run(
        ["bash", str(SCAN_SPECS_SCRIPT)],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    return json.loads(result.stdout.strip())


def create_spec(specs_dir: Path, name: str, title: str, status: str, created: str):
    """Create a spec directory with a well-formed spec.md."""
    spec_dir = specs_dir / name
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(
        f"# Feature Specification: {title}\n\n"
        f"**Status**: {status}\n\n"
        f"**Created**: {created}\n"
    )


def make_specify_project(project_dir: Path):
    """Create a minimal .specify directory."""
    (project_dir / ".specify").mkdir(parents=True, exist_ok=True)


class TestViewProjectRoadmap:
    """T012 AS-1: Given 3 specs, When script runs, Then all 3 in output."""

    def test_three_specs_all_present_in_output(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        specs = tmp_path / "specs"
        create_spec(specs, "001-alpha", "Alpha Feature", "Draft", "2026-08-01")
        create_spec(specs, "002-beta", "Beta Feature", "In Progress", "2026-08-02")
        create_spec(specs, "003-gamma", "Gamma Feature", "Complete", "2026-08-03")

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        assert len(result["specs"]) == 3
        for spec in result["specs"]:
            for field in ("id", "title", "status", "created"):
                assert field in spec
                assert isinstance(spec[field], str)
                assert len(spec[field]) > 0


class TestRoadmapStatusReflection:
    """T013 AS-2: Given specs with various statuses, Then each reflected accurately."""

    def test_statuses_accurately_reflected(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        specs = tmp_path / "specs"
        create_spec(specs, "001-draft", "Draft Feature", "Draft", "2026-08-01")
        create_spec(specs, "002-progress", "Progress Feature", "In Progress", "2026-08-02")
        create_spec(specs, "003-complete", "Complete Feature", "Complete", "2026-08-03")

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        status_map = {s["id"]: s["status"] for s in result["specs"]}
        assert status_map["001-draft"] == "Draft"
        assert status_map["002-progress"] == "In Progress"
        assert status_map["003-complete"] == "Complete"


class TestRoadmapOrdering:
    """T014 AS-3: Given sequential numbering, Then listed in number order."""

    def test_specs_ordered_by_directory_name(self, tmp_path):
        # Arrange — create out of order
        make_specify_project(tmp_path)
        specs = tmp_path / "specs"
        create_spec(specs, "003-gamma", "Gamma", "Draft", "2026-08-03")
        create_spec(specs, "001-alpha", "Alpha", "Draft", "2026-08-01")
        create_spec(specs, "002-beta", "Beta", "Draft", "2026-08-02")

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        ids = [s["id"] for s in result["specs"]]
        assert ids == ["001-alpha", "002-beta", "003-gamma"]
