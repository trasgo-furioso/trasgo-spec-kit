"""Smoke tests for trasgospec bundle installation.

Verifies the full user-facing installation flow:
  git init → specify init → catalog add → bundle install → verify

Requires network access to raw.githubusercontent.com and the
current branch pushed to origin.
"""

import json
import subprocess
import urllib.request
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Detect current branch from the real repo (not tmp_path)
_branch_result = subprocess.run(
    ["git", "branch", "--show-current"],
    cwd=PROJECT_ROOT,
    capture_output=True,
    text=True,
)
BRANCH = _branch_result.stdout.strip() or "main"
BUNDLE_CATALOG_URL = (
    f"https://raw.githubusercontent.com/trasgo-furioso/"
    f"trasgo-spec-kit/{BRANCH}/catalog.json"
)
EXTENSION_CATALOG_URL = (
    f"https://raw.githubusercontent.com/trasgo-furioso/"
    f"trasgo-spec-kit/{BRANCH}/extension-catalog.json"
)
PRESET_CATALOG_URL = (
    f"https://raw.githubusercontent.com/trasgo-furioso/"
    f"trasgo-spec-kit/{BRANCH}/preset-catalog.json"
)

# Read expected version from local bundle.yml
_EXPECTED_VERSION = "0.6.0"
_bundle_yml = PROJECT_ROOT / "bundle" / "bundle.yml"
if _bundle_yml.exists():
    for _line in _bundle_yml.read_text().splitlines():
        _line = _line.strip()
        if _line.startswith("version:"):
            _EXPECTED_VERSION = _line.split(":", 1)[1].strip().strip('"').strip("'")
            break


def run_specify(*args, cwd):
    """Run a specify CLI command and return the result."""
    return subprocess.run(
        ["specify", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def assert_command_ok(result, label):
    """Assert a specify command succeeded with a descriptive message."""
    assert result.returncode == 0, (
        f"{label} failed (exit {result.returncode})\n"
        f"  stdout: {result.stdout.strip()}\n"
        f"  stderr: {result.stderr.strip()}\n"
        f"  args: {result.args}"
    )


@pytest.fixture
def clean_project(tmp_path):
    """Create a clean git repo with specify init."""
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
    result = run_specify("init", "--here", "--integration", "claude", "--force", cwd=tmp_path)
    assert_command_ok(result, "specify init")
    return tmp_path


@pytest.fixture
def project_with_catalogs(clean_project):
    """Clean project with bundle and extension catalogs added."""
    result = run_specify("bundle", "catalog", "add", BUNDLE_CATALOG_URL, cwd=clean_project)
    assert_command_ok(result, f"bundle catalog add {BUNDLE_CATALOG_URL}")
    result = run_specify(
        "extension", "catalog", "add", EXTENSION_CATALOG_URL,
        "--name", "trasgospec", "--install-allowed",
        cwd=clean_project,
    )
    assert_command_ok(result, f"extension catalog add {EXTENSION_CATALOG_URL}")
    result = run_specify(
        "preset", "catalog", "add", PRESET_CATALOG_URL,
        "--name", "trasgospec", "--install-allowed",
        cwd=clean_project,
    )
    assert_command_ok(result, f"preset catalog add {PRESET_CATALOG_URL}")
    return clean_project


@pytest.fixture
def project_with_bundle(project_with_catalogs):
    """Project with trasgospec bundle installed."""
    result = run_specify("bundle", "install", "trasgospec", cwd=project_with_catalogs)
    assert_command_ok(result, "bundle install trasgospec")
    return project_with_catalogs


class TestBundleInstallation:
    """Smoke test: install trasgospec from the current branch's catalog."""

    def test_add_bundle_catalog(self, clean_project):
        result = run_specify("bundle", "catalog", "add", BUNDLE_CATALOG_URL, cwd=clean_project)
        assert_command_ok(result, f"bundle catalog add {BUNDLE_CATALOG_URL}")

    def test_add_extension_catalog(self, clean_project):
        result = run_specify(
            "extension", "catalog", "add", EXTENSION_CATALOG_URL,
            "--name", "trasgospec", "--install-allowed",
            cwd=clean_project,
        )
        assert_command_ok(result, f"extension catalog add {EXTENSION_CATALOG_URL}")

    def test_catalog_version_matches_bundle(self):
        """Verify GitHub CDN serves the expected catalog version (not a stale cache)."""
        with urllib.request.urlopen(BUNDLE_CATALOG_URL) as resp:
            catalog = json.loads(resp.read())
        served_version = catalog["bundles"]["trasgospec"]["version"]
        assert served_version == _EXPECTED_VERSION, (
            f"GitHub CDN is serving catalog v{served_version} but bundle.yml has v{_EXPECTED_VERSION}. "
            f"This is likely a CDN cache issue (max-age=300s). Wait ~5 minutes and retry.\n"
            f"  catalog URL: {BUNDLE_CATALOG_URL}\n"
            f"  download_url: {catalog['bundles']['trasgospec']['download_url']}"
        )

    def test_install_bundle(self, project_with_catalogs):
        result = run_specify("bundle", "install", "trasgospec", cwd=project_with_catalogs)
        assert_command_ok(result, "bundle install trasgospec")

    def test_bundle_list_shows_trasgospec(self, project_with_bundle):
        result = run_specify("bundle", "list", cwd=project_with_bundle)
        assert_command_ok(result, "bundle list")
        assert "trasgospec" in result.stdout, (
            f"'trasgospec' not found in bundle list output:\n{result.stdout}"
        )

    def test_extension_list_shows_trasgospec(self, project_with_bundle):
        result = run_specify("extension", "list", cwd=project_with_bundle)
        assert_command_ok(result, "extension list")
        assert "trasgospec" in result.stdout, (
            f"'trasgospec' not found in extension list output:\n{result.stdout}"
        )
