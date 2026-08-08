"""Integration tests for User Story 2: Roadmap for Empty or Single-Spec Projects.

Tests follow Given (Arrange) / When (Act) / Then (Assert) pattern.
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


def make_specify_project(project_dir: Path):
    """Create a minimal .specify directory."""
    (project_dir / ".specify").mkdir(parents=True, exist_ok=True)


class TestEmptySpecsDirectory:
    """T019 AS-1: Given no specs/ directory, Then empty specs array."""

    def test_no_specs_directory_returns_empty_array(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        assert result["specs"] == []
        assert result["specs_dir"] == "specs"


class TestEmptySpecsDirExists:
    """T020 AS-1 variant: Given empty specs/ directory, Then empty specs array."""

    def test_empty_specs_dir_returns_empty_array(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        assert result["specs"] == []


class TestSingleSpec:
    """T021 AS-2: Given exactly one spec, Then JSON contains exactly one entry."""

    def test_single_spec_returns_one_entry(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        spec_dir = tmp_path / "specs" / "001-only-feature"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text(
            "# Feature Specification: Only Feature\n\n"
            "**Status**: Draft\n\n"
            "**Created**: 2026-08-08\n"
        )

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        assert len(result["specs"]) == 1
        assert result["specs"][0]["title"] == "Only Feature"
