"""Unit tests for bundle/extensions/trasgospec/scripts/bash/discovery.sh.

Tests validate the script's JSON contract output per
specs/007-conversational-discovery/contracts/discovery-script-contract.md.

Each test class creates a controlled project structure in tmp_path,
runs the script via subprocess, and asserts the JSON output.
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DISCOVERY_SCRIPT = PROJECT_ROOT / "bundle" / "extensions" / "trasgospec" / "scripts" / "bash" / "discovery.sh"

REQUIRED_FIELDS = ["spec_dir", "spec_number", "slug", "prd_path", "feature_json_updated"]


def make_specify_project(project_dir: Path):
    """Create a minimal .specify directory."""
    (project_dir / ".specify").mkdir(parents=True, exist_ok=True)


def create_spec_dir(specs_dir: Path, name: str):
    """Create a numbered spec directory (no spec.md needed for discovery tests)."""
    spec_dir = specs_dir / name
    spec_dir.mkdir(parents=True, exist_ok=True)
    return spec_dir


def run_discovery(project_dir: Path, slug_hint: str = None) -> dict:
    """Run discovery.sh against a project directory and return parsed JSON."""
    cmd = ["bash", str(DISCOVERY_SCRIPT), "--json"]
    if slug_hint:
        cmd.append(slug_hint)
    result = subprocess.run(
        cmd,
        cwd=project_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    return json.loads(result.stdout.strip())


# ---------------------------------------------------------------------------
# T004: Sequential numbering logic
# ---------------------------------------------------------------------------
class TestSequentialNumbering:
    """Verify the script computes the correct next sequential number."""

    def test_no_existing_specs_yields_001(self, tmp_path):
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()
        data = run_discovery(tmp_path, "test-feature")
        assert data["spec_number"] == "001"

    def test_single_existing_spec_yields_next(self, tmp_path):
        make_specify_project(tmp_path)
        create_spec_dir(tmp_path / "specs", "001-first")
        data = run_discovery(tmp_path, "test-feature")
        assert data["spec_number"] == "002"

    def test_gaps_in_numbering_uses_max_plus_one(self, tmp_path):
        make_specify_project(tmp_path)
        specs = tmp_path / "specs"
        create_spec_dir(specs, "001-first")
        create_spec_dir(specs, "004-fourth")
        create_spec_dir(specs, "005-fifth")
        data = run_discovery(tmp_path, "test-feature")
        assert data["spec_number"] == "006"

    def test_existing_007_yields_008(self, tmp_path):
        make_specify_project(tmp_path)
        specs = tmp_path / "specs"
        create_spec_dir(specs, "007-seventh")
        data = run_discovery(tmp_path, "test-feature")
        assert data["spec_number"] == "008"

    def test_no_specs_dir_creates_it(self, tmp_path):
        make_specify_project(tmp_path)
        data = run_discovery(tmp_path, "test-feature")
        assert data["spec_number"] == "001"
        assert (tmp_path / "specs" / "001-test-feature").is_dir()


# ---------------------------------------------------------------------------
# T005: Directory creation and prd.md scaffold
# ---------------------------------------------------------------------------
class TestDirectoryAndScaffold:
    """Verify the script creates the directory and scaffolds prd.md."""

    def test_creates_spec_directory(self, tmp_path):
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()
        data = run_discovery(tmp_path, "my-feature")
        spec_dir = tmp_path / data["spec_dir"]
        assert spec_dir.is_dir()

    def test_creates_prd_md(self, tmp_path):
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()
        data = run_discovery(tmp_path, "my-feature")
        prd_path = tmp_path / data["prd_path"]
        assert prd_path.is_file()

    def test_prd_scaffold_has_required_sections(self, tmp_path):
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()
        data = run_discovery(tmp_path, "my-feature")
        prd_content = (tmp_path / data["prd_path"]).read_text()
        assert "## Problem Statement" in prd_content
        assert "**Pain Point**:" in prd_content
        assert "**Who**:" in prd_content
        assert "**Current Alternatives**:" in prd_content
        assert "**Desired Outcome**:" in prd_content
        assert "## Jobs to Be Done" in prd_content
        assert "## Assumptions" in prd_content
        assert "## Research Findings" in prd_content

    def test_prd_scaffold_has_title(self, tmp_path):
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()
        data = run_discovery(tmp_path, "my-feature")
        prd_content = (tmp_path / data["prd_path"]).read_text()
        assert prd_content.startswith("# PRD: My Feature")

    def test_prd_scaffold_has_dates(self, tmp_path):
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()
        data = run_discovery(tmp_path, "my-feature")
        prd_content = (tmp_path / data["prd_path"]).read_text()
        assert "**Created**:" in prd_content
        assert "**Discovery Session**:" in prd_content


# ---------------------------------------------------------------------------
# T006: feature.json update
# ---------------------------------------------------------------------------
class TestFeatureJsonUpdate:
    """Verify the script updates .specify/feature.json."""

    def test_updates_feature_json(self, tmp_path):
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()
        data = run_discovery(tmp_path, "my-feature")
        feature_json = json.loads((tmp_path / ".specify" / "feature.json").read_text())
        assert feature_json["feature_directory"] == data["spec_dir"]

    def test_feature_json_updated_flag(self, tmp_path):
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()
        data = run_discovery(tmp_path, "my-feature")
        assert data["feature_json_updated"] is True


# ---------------------------------------------------------------------------
# T007: JSON output contract
# ---------------------------------------------------------------------------
class TestJsonContract:
    """Verify the script emits valid JSON with all required fields."""

    def test_all_required_fields_present(self, tmp_path):
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()
        data = run_discovery(tmp_path, "test-feature")
        for field in REQUIRED_FIELDS:
            assert field in data, f"Missing field: {field}"

    def test_field_types(self, tmp_path):
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()
        data = run_discovery(tmp_path, "test-feature")
        assert isinstance(data["spec_dir"], str)
        assert isinstance(data["spec_number"], str)
        assert isinstance(data["slug"], str)
        assert isinstance(data["prd_path"], str)
        assert isinstance(data["feature_json_updated"], bool)

    def test_spec_number_is_zero_padded(self, tmp_path):
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()
        data = run_discovery(tmp_path, "test-feature")
        assert len(data["spec_number"]) == 3
        assert data["spec_number"] == "001"

    def test_prd_path_matches_spec_dir(self, tmp_path):
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()
        data = run_discovery(tmp_path, "test-feature")
        assert data["prd_path"] == f"{data['spec_dir']}/prd.md"


# ---------------------------------------------------------------------------
# T008: Slug-hint handling
# ---------------------------------------------------------------------------
class TestSlugHint:
    """Verify slug derivation from hint or fallback."""

    def test_slug_from_hint(self, tmp_path):
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()
        data = run_discovery(tmp_path, "My Cool Feature")
        assert data["slug"] == "my-cool-feature"

    def test_slug_strips_special_chars(self, tmp_path):
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()
        data = run_discovery(tmp_path, "Hello, World! (v2)")
        assert data["slug"] == "hello-world-v2"

    def test_slug_underscores_become_hyphens(self, tmp_path):
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()
        data = run_discovery(tmp_path, "my_cool_feature")
        assert data["slug"] == "my-cool-feature"

    def test_no_slug_hint_uses_timestamp(self, tmp_path):
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()
        data = run_discovery(tmp_path)
        # Timestamp slug should match YYYYMMDD-HHMMSS pattern
        assert len(data["slug"]) == 15  # 20260808-123456
        assert "-" in data["slug"]

    def test_slug_in_directory_name(self, tmp_path):
        make_specify_project(tmp_path)
        (tmp_path / "specs").mkdir()
        data = run_discovery(tmp_path, "api-caching")
        assert data["spec_dir"] == "specs/001-api-caching"
