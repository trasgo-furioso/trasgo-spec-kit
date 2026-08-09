"""Shared pytest fixtures for integration tests.

Provides HTTP server for catalog simulation, clean Spec Kit project
creation, and catalog source setup helpers.
"""

import http.server
import json
import os
import subprocess
import threading
from pathlib import Path

import yaml
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_ROOT = PROJECT_ROOT / "bundle"
EXTENSION_DIR = BUNDLE_ROOT / "extensions" / "trasgospec"
CATALOG_PORT = 8888


def _read_bundle_metadata():
    """Read version and command count from bundle manifests."""
    with open(BUNDLE_ROOT / "bundle.yml") as f:
        bundle_data = yaml.safe_load(f)
    with open(EXTENSION_DIR / "extension.yml") as f:
        ext_data = yaml.safe_load(f)
    version = bundle_data["bundle"]["version"]
    command_count = len(ext_data["provides"]["commands"])
    return version, command_count


_BUNDLE_VERSION, _COMMAND_COUNT = _read_bundle_metadata()

# Test bundle catalog that points download_url to the local HTTP server
_TEST_BUNDLE_CATALOG = {
    "schema_version": "1.0",
    "bundles": {
        "trasgospec": {
            "id": "trasgospec",
            "name": "Trasgo Spec Kit",
            "description": "Scaffold Spec Kit bundle for the claude integration",
            "version": _BUNDLE_VERSION,
            "role": "developer",
            "download_url": f"http://localhost:{CATALOG_PORT}/trasgospec-{_BUNDLE_VERSION}.zip",
        }
    },
}

# Test extension catalog that points download_url to the local HTTP server
_TEST_EXTENSION_CATALOG = {
    "schema_version": "1.0",
    "updated_at": "2026-08-08T00:00:00Z",
    "extensions": {
        "trasgospec": {
            "name": "Trasgo Spec Kit",
            "id": "trasgospec",
            "version": _BUNDLE_VERSION,
            "description": "Journey-first product specification commands.",
            "author": "Trasgo Furioso",
            "download_url": f"http://localhost:{CATALOG_PORT}/trasgospec-extension-{_BUNDLE_VERSION}.zip",
            "license": "MIT",
            "category": "utility",
            "effect": "read-only",
            "requires": {"speckit_version": ">=0.15.0"},
            "provides": {"commands": _COMMAND_COUNT},
            "tags": ["specification"],
            "verified": False,
        }
    },
}


class _CatalogHandler(http.server.SimpleHTTPRequestHandler):
    """Serves catalogs and artifacts from the project root directory."""

    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=str(PROJECT_ROOT), **kwargs)

    def do_GET(self):
        if self.path == "/test-catalog.json":
            self._serve_json(_TEST_BUNDLE_CATALOG)
        elif self.path == "/test-ext-catalog.json":
            self._serve_json(_TEST_EXTENSION_CATALOG)
        else:
            super().do_GET()

    def _serve_json(self, data):
        payload = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(payload))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        pass  # silence request logs during tests


@pytest.fixture(scope="session")
def catalog_server():
    """Session-scoped HTTP server serving catalogs and artifacts on localhost:8888."""
    server = http.server.HTTPServer(("localhost", CATALOG_PORT), _CatalogHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()


@pytest.fixture(scope="session")
def catalog_url(catalog_server):
    """Returns the URL to the test bundle catalog served by the local HTTP server."""
    return f"http://localhost:{CATALOG_PORT}/test-catalog.json"


@pytest.fixture(scope="session")
def extension_catalog_url(catalog_server):
    """Returns the URL to the test extension catalog served by the local HTTP server."""
    return f"http://localhost:{CATALOG_PORT}/test-ext-catalog.json"


@pytest.fixture
def clean_project(tmp_path):
    """Creates a clean Spec Kit project via `specify init --here --integration claude`."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    result = subprocess.run(
        ["specify", "init", "--here", "--integration", "claude"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"specify init failed: {result.stdout}"
    return project_dir


@pytest.fixture
def project_with_catalog(clean_project, catalog_url, extension_catalog_url):
    """Clean project with both bundle and extension catalog sources added."""
    # Add bundle catalog
    result = subprocess.run(
        [
            "specify", "bundle", "catalog", "add",
            catalog_url,
            "--policy", "install-allowed",
        ],
        cwd=clean_project,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"bundle catalog add failed: {result.stderr}"

    # Add extension catalog
    result = subprocess.run(
        [
            "specify", "extension", "catalog", "add",
            extension_catalog_url,
            "--name", "trasgospec",
            "--install-allowed",
        ],
        cwd=clean_project,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"extension catalog add failed: {result.stderr}"

    return clean_project


@pytest.fixture
def project_with_extension_catalog(clean_project, extension_catalog_url):
    """Clean project with only the extension catalog source added."""
    result = subprocess.run(
        [
            "specify", "extension", "catalog", "add",
            extension_catalog_url,
            "--name", "trasgospec",
            "--install-allowed",
        ],
        cwd=clean_project,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"extension catalog add failed: {result.stderr}"
    return clean_project


def run_specify(*args, cwd):
    """Helper to run a specify CLI command and return the result."""
    return subprocess.run(
        ["specify", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
