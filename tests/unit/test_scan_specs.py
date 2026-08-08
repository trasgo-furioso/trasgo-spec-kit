"""Unit tests for bundle/extensions/trasgospec-roadmap/scripts/bash/scan-specs.sh.

Tests validate the script's JSON contract output per
specs/002-roadmap-visualization/contracts/scan-specs-output.md.

Each test class creates a controlled project structure in tmp_path,
runs the script via subprocess, and asserts the JSON output.
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCAN_SPECS_SCRIPT = PROJECT_ROOT / "bundle" / "extensions" / "trasgospec" / "scripts" / "bash" / "scan-specs.sh"


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


def create_spec(specs_dir: Path, name: str, title: str = None,
                status: str = None, created: str = None, empty: bool = False):
    """Helper to create a spec directory with spec.md containing given fields."""
    spec_dir = specs_dir / name
    spec_dir.mkdir(parents=True, exist_ok=True)
    if empty:
        (spec_dir / "spec.md").write_text("")
        return spec_dir
    lines = []
    if title is not None:
        lines.append(f"# Feature Specification: {title}")
    if status is not None:
        lines.append(f"\n**Status**: {status}")
    if created is not None:
        lines.append(f"\n**Created**: {created}")
    (spec_dir / "spec.md").write_text("\n".join(lines) + "\n")
    return spec_dir


def make_specify_project(project_dir: Path):
    """Create a minimal .specify directory so the script can find the repo root."""
    (project_dir / ".specify").mkdir(parents=True, exist_ok=True)


class TestSpecsDirectoryDiscovery:
    """T004: Test specs directory discovery and empty-state handling."""

    def test_outputs_valid_json_with_specs_dir_field(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()
        create_spec(tmp_path / "specs", "001-test", "Test", "Draft", "2026-01-01")

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        assert "specs_dir" in result
        assert result["specs_dir"] == "specs"

    def test_empty_specs_array_when_no_specs_directory(self, tmp_path):
        # Arrange — no specs/ directory at all
        make_specify_project(tmp_path)

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        assert result["specs"] == []

    def test_empty_specs_array_when_specs_directory_is_empty(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        assert result["specs"] == []


class TestSpecDirectoryIteration:
    """T005: Test directory filtering and sorting."""

    def test_discovers_only_directories_with_spec_md(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        specs = tmp_path / "specs"
        create_spec(specs, "001-valid", "Valid", "Draft", "2026-01-01")
        # Create directory without spec.md
        (specs / "002-no-spec").mkdir(parents=True)

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        ids = [s["id"] for s in result["specs"]]
        assert "001-valid" in ids
        assert "002-no-spec" not in ids

    def test_sorts_by_directory_name_ascending(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        specs = tmp_path / "specs"
        create_spec(specs, "003-gamma", "Gamma", "Draft", "2026-01-03")
        create_spec(specs, "001-alpha", "Alpha", "Draft", "2026-01-01")
        create_spec(specs, "002-beta", "Beta", "Draft", "2026-01-02")

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        ids = [s["id"] for s in result["specs"]]
        assert ids == ["001-alpha", "002-beta", "003-gamma"]

    def test_skips_hidden_directories(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        specs = tmp_path / "specs"
        create_spec(specs, "001-valid", "Valid", "Draft", "2026-01-01")
        hidden = specs / ".git"
        hidden.mkdir(parents=True)
        (hidden / "spec.md").write_text("# Feature Specification: Hidden\n")

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        ids = [s["id"] for s in result["specs"]]
        assert ".git" not in ids
        assert len(ids) == 1


class TestMetadataExtraction:
    """T006: Test metadata field extraction and fallbacks."""

    def test_extracts_all_fields_from_well_formed_spec(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        specs = tmp_path / "specs"
        create_spec(specs, "001-bundle-install", "Bundle Install", "Draft", "2026-08-07")

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        spec = result["specs"][0]
        assert spec["id"] == "001-bundle-install"
        assert spec["title"] == "Bundle Install"
        assert spec["status"] == "Draft"
        assert spec["created"] == "2026-08-07"

    def test_fallback_title_when_heading_missing(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        spec_dir = tmp_path / "specs" / "001-my-feature"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("**Status**: Draft\n**Created**: 2026-01-01\n")

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        spec = result["specs"][0]
        assert spec["title"] == "001-my-feature"

    def test_fallback_status_when_field_missing(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        spec_dir = tmp_path / "specs" / "001-test"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Feature Specification: Test\n**Created**: 2026-01-01\n")

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        assert result["specs"][0]["status"] == "Unknown"

    def test_fallback_created_when_field_missing(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        spec_dir = tmp_path / "specs" / "001-test"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Feature Specification: Test\n**Status**: Draft\n")

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        assert result["specs"][0]["created"] == "Unknown"

    def test_empty_spec_file_produces_all_fallbacks(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        create_spec(tmp_path / "specs", "001-empty", empty=True)

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        spec = result["specs"][0]
        assert spec["id"] == "001-empty"
        assert spec["title"] == "001-empty"
        assert spec["status"] == "Unknown"
        assert spec["created"] == "Unknown"


class TestJsonOutputContract:
    """T007: Test JSON output format and special character handling."""

    def test_output_is_valid_single_line_json(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        specs = tmp_path / "specs"
        create_spec(specs, "001-test", "Test", "Draft", "2026-01-01")

        # Act
        result = subprocess.run(
            ["bash", str(SCAN_SPECS_SCRIPT)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        # Assert
        lines = result.stdout.strip().split("\n")
        assert len(lines) == 1, f"Expected single line, got {len(lines)}"
        data = json.loads(lines[0])
        assert "specs_dir" in data
        assert "specs" in data

    def test_json_has_required_schema_fields(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        specs = tmp_path / "specs"
        create_spec(specs, "001-test", "Test Feature", "In Progress", "2026-08-08")

        # Act
        result = run_scan_specs(tmp_path)

        # Assert — top-level fields
        assert isinstance(result["specs_dir"], str)
        assert isinstance(result["specs"], list)
        # Per-spec fields
        spec = result["specs"][0]
        for field in ("id", "title", "status", "created"):
            assert field in spec, f"Missing field: {field}"
            assert isinstance(spec[field], str)

    def test_json_escape_handles_special_characters(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        spec_dir = tmp_path / "specs" / "001-special"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text(
            '# Feature Specification: Title with "quotes" & backslash\\\n'
            '**Status**: Draft\n'
            '**Created**: 2026-01-01\n'
        )

        # Act
        result = run_scan_specs(tmp_path)

        # Assert — should parse without error; title should contain the special chars
        spec = result["specs"][0]
        assert '"quotes"' in spec["title"] or "quotes" in spec["title"]


class TestTimestampNaming:
    """T028: Verify script works with timestamp-based directory naming."""

    def test_timestamp_directories_sorted_correctly(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        specs = tmp_path / "specs"
        create_spec(specs, "20260808-143022-feature-b", "Feature B", "Draft", "2026-08-08")
        create_spec(specs, "20260807-091500-feature-a", "Feature A", "Draft", "2026-08-07")
        create_spec(specs, "20260809-200000-feature-c", "Feature C", "In Progress", "2026-08-09")

        # Act
        result = run_scan_specs(tmp_path)

        # Assert — sorted by directory name (timestamp ascending)
        ids = [s["id"] for s in result["specs"]]
        assert ids == [
            "20260807-091500-feature-a",
            "20260808-143022-feature-b",
            "20260809-200000-feature-c",
        ]
        assert result["specs"][0]["title"] == "Feature A"
        assert result["specs"][2]["status"] == "In Progress"
