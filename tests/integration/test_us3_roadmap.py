"""Integration tests for User Story 3: Graceful Handling of Incomplete Specs.

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


class TestMissingStatusField:
    """T023 AS-1: Given spec missing Status field, Then status is 'Unknown'."""

    def test_missing_status_falls_back_to_unknown(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        spec_dir = tmp_path / "specs" / "001-no-status"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text(
            "# Feature Specification: No Status Feature\n\n"
            "**Created**: 2026-08-08\n"
        )

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        assert result["specs"][0]["status"] == "Unknown"
        assert result["specs"][0]["title"] == "No Status Feature"
        assert result["specs"][0]["created"] == "2026-08-08"


class TestDirectoryWithoutSpecFile:
    """T024 AS-2: Given directory without spec.md, Then skipped."""

    def test_directory_without_spec_md_is_skipped(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        specs = tmp_path / "specs"
        # Valid spec
        valid = specs / "001-valid"
        valid.mkdir(parents=True)
        (valid / "spec.md").write_text(
            "# Feature Specification: Valid\n\n**Status**: Draft\n\n**Created**: 2026-08-08\n"
        )
        # Invalid — no spec.md
        (specs / "002-no-spec").mkdir(parents=True)
        (specs / "002-no-spec" / "README.md").write_text("Not a spec\n")

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        ids = [s["id"] for s in result["specs"]]
        assert "001-valid" in ids
        assert "002-no-spec" not in ids
        assert len(result["specs"]) == 1


class TestEmptySpecFile:
    """T025 Edge: Given completely empty spec.md, Then all fallbacks used."""

    def test_empty_spec_uses_all_fallbacks(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        spec_dir = tmp_path / "specs" / "001-empty"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("")

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        spec = result["specs"][0]
        assert spec["id"] == "001-empty"
        assert spec["title"] == "001-empty"
        assert spec["status"] == "Unknown"
        assert spec["created"] == "Unknown"


class TestNonSpecSubdirectories:
    """T026 Edge: Given non-spec directories (.git, __pycache__), Then ignored."""

    def test_hidden_and_non_spec_dirs_ignored(self, tmp_path):
        # Arrange
        make_specify_project(tmp_path)
        specs = tmp_path / "specs"
        # Valid spec
        valid = specs / "001-valid"
        valid.mkdir(parents=True)
        (valid / "spec.md").write_text(
            "# Feature Specification: Valid\n\n**Status**: Draft\n\n**Created**: 2026-08-08\n"
        )
        # Non-spec directories
        (specs / "__pycache__").mkdir(parents=True)
        (specs / ".git").mkdir(parents=True)
        # __pycache__ with a spec.md (should still be included — it has spec.md)
        # Actually per spec: "we consider a spec directory the one that has a spec file on it"
        # __pycache__ without spec.md should be ignored

        # Act
        result = run_scan_specs(tmp_path)

        # Assert
        ids = [s["id"] for s in result["specs"]]
        assert ids == ["001-valid"]
        assert "__pycache__" not in ids
        assert ".git" not in ids
