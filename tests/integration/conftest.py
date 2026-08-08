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

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_ROOT = PROJECT_ROOT / "bundle"
CATALOG_PORT = 8888

# Test catalog that points download_url to the local HTTP server
_TEST_CATALOG = {
    "schema_version": "1.0",
    "bundles": {
        "trasgospec": {
            "id": "trasgospec",
            "name": "Trasgo Spec Kit",
            "description": "Scaffold Spec Kit bundle for the claude integration",
            "version": "0.1.0",
            "role": "developer",
            "download_url": f"http://localhost:{CATALOG_PORT}/trasgospec-0.1.0.zip",
        }
    },
}


class _CatalogHandler(http.server.SimpleHTTPRequestHandler):
    """Serves files from the project root directory.

    Serves test-catalog.json (generated) and trasgospec-0.1.0.zip (built artifact).
    """

    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=str(PROJECT_ROOT), **kwargs)

    def do_GET(self):
        if self.path == "/test-catalog.json":
            payload = json.dumps(_TEST_CATALOG).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(payload))
            self.end_headers()
            self.wfile.write(payload)
        else:
            super().do_GET()

    def log_message(self, format, *args):
        pass  # silence request logs during tests


@pytest.fixture(scope="session")
def catalog_server():
    """Session-scoped HTTP server serving catalog and artifacts on localhost:8888."""
    server = http.server.HTTPServer(("localhost", CATALOG_PORT), _CatalogHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()


@pytest.fixture(scope="session")
def catalog_url(catalog_server):
    """Returns the URL to the test catalog served by the local HTTP server."""
    return f"http://localhost:{CATALOG_PORT}/test-catalog.json"


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
def project_with_catalog(clean_project, catalog_url):
    """Clean project with Trasgo catalog source already added."""
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
    assert result.returncode == 0, f"catalog add failed: {result.stderr}"
    return clean_project


def run_specify(*args, cwd):
    """Helper to run a specify CLI command and return the result."""
    return subprocess.run(
        ["specify", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
