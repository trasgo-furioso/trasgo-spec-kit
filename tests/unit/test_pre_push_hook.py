"""Unit tests for .githooks/pre-push hook.

Tests validate the pre-push hook's behavior per
specs/003-bundle-build-ci/contracts/hook-exit-codes.md and
specs/003-bundle-build-ci/contracts/catalog-update.md.

Each test creates an isolated git repo in tmp_path with a fake
`specify` CLI stub, runs the hook script via subprocess with
simulated stdin, and asserts exit codes + side effects.
"""

import json
import os
import stat
import subprocess
import textwrap
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRE_PUSH_HOOK = PROJECT_ROOT / ".githooks" / "pre-push"


def make_git_repo(path: Path, remote_url: str = "git@github.com:test-owner/test-repo.git") -> Path:
    """Create a minimal git repo with .specify marker, bundle/, and a remote."""
    subprocess.run(["git", "init", str(path)], capture_output=True, check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "test@test.com"], capture_output=True, check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "Test"], capture_output=True, check=True)
    subprocess.run(["git", "-C", str(path), "remote", "add", "origin", remote_url], capture_output=True, check=True)
    (path / ".specify").mkdir()
    return path


def write_bundle_yml(path: Path, version: str = "0.3.0", bundle_id: str = "testbundle",
                     name: str = "Test Bundle", description: str = "A test bundle",
                     role: str = "developer"):
    """Write a bundle.yml to path/bundle/bundle.yml."""
    bundle_dir = path / "bundle"
    bundle_dir.mkdir(exist_ok=True)
    (bundle_dir / "bundle.yml").write_text(textwrap.dedent(f"""\
        schema_version: "1.0"

        bundle:
          id: {bundle_id}
          name: {name}
          version: "{version}"
          description: >-
            {description}
          role: {role}
    """))


def write_catalog_json(path: Path, bundle_id: str = "testbundle",
                       version: str = "0.1.0"):
    """Write an initial catalog.json."""
    catalog = {
        "schema_version": "1.0",
        "bundles": {
            bundle_id: {
                "id": bundle_id,
                "name": "Old Name",
                "description": "Old description",
                "version": version,
                "role": "developer",
                "download_url": f"https://example.com/{bundle_id}-{version}.zip"
            }
        }
    }
    (path / "catalog.json").write_text(json.dumps(catalog, indent=2) + "\n")


def create_specify_stub(path: Path, should_fail_validate: bool = False,
                        should_fail_build: bool = False):
    """Create a fake `specify` CLI script that simulates validate and build."""
    bin_dir = path / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    stub = bin_dir / "specify"

    build_action = ""
    if not should_fail_build:
        # Create a fake zip file to simulate bundle build output
        build_action = textwrap.dedent("""\
            # Extract bundle id and version from bundle.yml for zip filename
            bundle_dir=""
            output_dir=""
            while [ $# -gt 0 ]; do
                case "$1" in
                    --path) shift; bundle_dir="$1" ;;
                    --output) shift; output_dir="$1" ;;
                esac
                shift
            done
            if [ -n "$bundle_dir" ] && [ -n "$output_dir" ]; then
                bid=$(grep '  id:' "$bundle_dir/bundle.yml" | head -1 | sed 's/.*: *//')
                bver=$(grep '  version:' "$bundle_dir/bundle.yml" | head -1 | sed 's/.*: *"\\{0,1\\}\\([^"]*\\)"\\{0,1\\}/\\1/')
                touch "$output_dir/${bid}-${bver}.zip"
            fi
        """)

    validate_exit = "1" if should_fail_validate else "0"
    build_exit = "1" if should_fail_build else "0"

    stub.write_text(textwrap.dedent(f"""\
        #!/usr/bin/env bash
        case "$1" in
            bundle)
                shift
                case "$1" in
                    validate)
                        shift
                        exit {validate_exit}
                        ;;
                    build)
                        shift
                        {build_action}
                        exit {build_exit}
                        ;;
                esac
                ;;
        esac
        exit 0
    """))
    stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
    return bin_dir


def make_initial_commit(path: Path):
    """Stage everything and make an initial commit."""
    subprocess.run(["git", "-C", str(path), "add", "-A"], capture_output=True, check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-m", "initial"],
                   capture_output=True, check=True)


def make_bundle_change_commit(path: Path, filename: str = "test.txt"):
    """Make a commit that modifies a file in bundle/."""
    bundle_dir = path / "bundle"
    bundle_dir.mkdir(exist_ok=True)
    (bundle_dir / filename).write_text("change\n")
    subprocess.run(["git", "-C", str(path), "add", f"bundle/{filename}"],
                   capture_output=True, check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-m", "bundle change"],
                   capture_output=True, check=True)


def make_non_bundle_commit(path: Path):
    """Make a commit that only modifies files outside bundle/."""
    (path / "README.md").write_text("docs change\n")
    subprocess.run(["git", "-C", str(path), "add", "README.md"],
                   capture_output=True, check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-m", "docs change"],
                   capture_output=True, check=True)


def get_head_sha(path: Path) -> str:
    result = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"],
                           capture_output=True, text=True, check=True)
    return result.stdout.strip()


def run_hook(path: Path, stdin_text: str, env_extra: dict = None) -> subprocess.CompletedProcess:
    """Run the pre-push hook with simulated stdin."""
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["bash", str(PRE_PUSH_HOOK)],
        cwd=path,
        input=stdin_text,
        capture_output=True,
        text=True,
        env=env,
    )


def build_stdin(local_sha: str, remote_sha: str = None,
                remote_ref: str = "refs/heads/main") -> str:
    """Build stdin line for pre-push hook."""
    zero = "0000000000000000000000000000000000000000"
    if remote_sha is None:
        remote_sha = zero
    return f"refs/heads/main {local_sha} {remote_ref} {remote_sha}\n"


# ---------------------------------------------------------------------------
# T004: Bundle change detection and validate+build execution
# ---------------------------------------------------------------------------


class TestBundleChangeDetection:
    """Verify hook detects bundle/ changes and ignores non-bundle changes."""

    def test_detects_bundle_changes_and_runs_build(self, tmp_path):
        """Hook should trigger when commits include bundle/ file changes."""
        repo = make_git_repo(tmp_path)
        write_bundle_yml(repo)
        write_catalog_json(repo)
        bin_dir = create_specify_stub(repo)
        make_initial_commit(repo)

        initial_sha = get_head_sha(repo)
        make_bundle_change_commit(repo)
        head_sha = get_head_sha(repo)

        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}
        stdin = build_stdin(head_sha, initial_sha)
        result = run_hook(repo, stdin, env_extra=env)

        # First push blocks (exit 6) after creating build commit
        assert result.returncode == 6
        assert "[bundle-build] Validating bundle..." in result.stderr
        assert "[bundle-build] Building bundle..." in result.stderr
        assert "Run 'git push' again" in result.stderr

    def test_skips_non_bundle_changes(self, tmp_path):
        """Hook should exit silently when no bundle/ files changed."""
        repo = make_git_repo(tmp_path)
        write_bundle_yml(repo)
        make_initial_commit(repo)

        initial_sha = get_head_sha(repo)
        make_non_bundle_commit(repo)
        head_sha = get_head_sha(repo)

        stdin = build_stdin(head_sha, initial_sha)
        result = run_hook(repo, stdin)

        assert result.returncode == 0
        assert result.stderr == ""

    def test_retry_push_succeeds_after_build_commit(self, tmp_path):
        """Second push should succeed because HEAD is already a build commit."""
        repo = make_git_repo(tmp_path)
        write_bundle_yml(repo)
        write_catalog_json(repo)
        bin_dir = create_specify_stub(repo)
        make_initial_commit(repo)

        initial_sha = get_head_sha(repo)
        make_bundle_change_commit(repo)
        head_sha = get_head_sha(repo)

        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}
        stdin = build_stdin(head_sha, initial_sha)

        # First push: builds and blocks
        result1 = run_hook(repo, stdin, env_extra=env)
        assert result1.returncode == 6

        # Second push: HEAD is now "chore: build bundle v*", should skip
        new_head = get_head_sha(repo)
        stdin2 = build_stdin(new_head, initial_sha)
        result2 = run_hook(repo, stdin2, env_extra=env)
        assert result2.returncode == 0

    def test_skips_push_to_non_main_branch(self, tmp_path):
        """Hook should skip when pushing to a branch other than main."""
        repo = make_git_repo(tmp_path)
        write_bundle_yml(repo)
        make_initial_commit(repo)

        initial_sha = get_head_sha(repo)
        make_bundle_change_commit(repo)
        head_sha = get_head_sha(repo)

        stdin = f"refs/heads/feature {head_sha} refs/heads/feature {initial_sha}\n"
        result = run_hook(repo, stdin)

        assert result.returncode == 0
        assert result.stderr == ""


class TestValidateAndBuild:
    """Verify hook runs specify validate and build, and blocks on failure."""

    def test_blocks_push_on_validation_failure(self, tmp_path):
        """Hook should exit 1 when specify bundle validate fails."""
        repo = make_git_repo(tmp_path)
        write_bundle_yml(repo)
        write_catalog_json(repo)
        bin_dir = create_specify_stub(repo, should_fail_validate=True)
        make_initial_commit(repo)

        initial_sha = get_head_sha(repo)
        make_bundle_change_commit(repo)
        head_sha = get_head_sha(repo)

        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}
        stdin = build_stdin(head_sha, initial_sha)
        result = run_hook(repo, stdin, env_extra=env)

        assert result.returncode == 1
        assert "ERROR" in result.stderr or "validation failed" in result.stderr.lower()

    def test_blocks_push_when_specify_missing(self, tmp_path):
        """Hook should exit 3 when specify CLI is not on PATH."""
        repo = make_git_repo(tmp_path)
        write_bundle_yml(repo)
        make_initial_commit(repo)

        initial_sha = get_head_sha(repo)
        make_bundle_change_commit(repo)
        head_sha = get_head_sha(repo)

        # Use a PATH that doesn't include specify
        env = {"PATH": "/usr/bin:/bin"}
        stdin = build_stdin(head_sha, initial_sha)
        result = run_hook(repo, stdin, env_extra=env)

        assert result.returncode == 3
        assert "specify CLI not found" in result.stderr


# ---------------------------------------------------------------------------
# T005: Catalog update and auto-commit creation
# ---------------------------------------------------------------------------


class TestCatalogUpdate:
    """Verify catalog.json is updated with correct fields after build."""

    def test_updates_catalog_version_and_url(self, tmp_path):
        """After build, catalog.json should have new version and download URL."""
        repo = make_git_repo(tmp_path)
        write_bundle_yml(repo, version="0.3.0", bundle_id="testbundle")
        write_catalog_json(repo, bundle_id="testbundle", version="0.1.0")
        bin_dir = create_specify_stub(repo)
        make_initial_commit(repo)

        initial_sha = get_head_sha(repo)
        make_bundle_change_commit(repo)
        head_sha = get_head_sha(repo)

        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}
        stdin = build_stdin(head_sha, initial_sha)
        result = run_hook(repo, stdin, env_extra=env)

        assert result.returncode == 6
        catalog = json.loads((repo / "catalog.json").read_text())
        bundle = catalog["bundles"]["testbundle"]
        assert bundle["version"] == "0.3.0"
        assert "raw.githubusercontent.com" in bundle["download_url"]
        assert "test-owner/test-repo" in bundle["download_url"]
        assert "testbundle-0.3.0.zip" in bundle["download_url"]

    def test_syncs_name_description_role(self, tmp_path):
        """After build, catalog.json should sync name, description, role from bundle.yml."""
        repo = make_git_repo(tmp_path)
        write_bundle_yml(repo, version="0.3.0", bundle_id="testbundle",
                        name="New Name", description="New description", role="admin")
        write_catalog_json(repo, bundle_id="testbundle", version="0.1.0")
        bin_dir = create_specify_stub(repo)
        make_initial_commit(repo)

        initial_sha = get_head_sha(repo)
        make_bundle_change_commit(repo)
        head_sha = get_head_sha(repo)

        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}
        stdin = build_stdin(head_sha, initial_sha)
        result = run_hook(repo, stdin, env_extra=env)

        assert result.returncode == 6
        catalog = json.loads((repo / "catalog.json").read_text())
        bundle = catalog["bundles"]["testbundle"]
        assert bundle["name"] == "New Name"
        assert bundle["role"] == "admin"


class TestAutoCommit:
    """Verify hook creates a separate build commit with artifacts."""

    def test_creates_separate_build_commit(self, tmp_path):
        """Hook should create a new commit containing zip and catalog.json."""
        repo = make_git_repo(tmp_path)
        write_bundle_yml(repo, version="0.3.0", bundle_id="testbundle")
        write_catalog_json(repo, bundle_id="testbundle", version="0.1.0")
        bin_dir = create_specify_stub(repo)
        make_initial_commit(repo)

        initial_sha = get_head_sha(repo)
        make_bundle_change_commit(repo)
        pre_hook_sha = get_head_sha(repo)

        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}
        stdin = build_stdin(pre_hook_sha, initial_sha)
        result = run_hook(repo, stdin, env_extra=env)

        assert result.returncode == 6

        # Verify a new commit was created
        post_hook_sha = get_head_sha(repo)
        assert post_hook_sha != pre_hook_sha

        # Verify commit message
        log_result = subprocess.run(
            ["git", "-C", str(repo), "log", "--oneline", "-1"],
            capture_output=True, text=True, check=True,
        )
        assert "chore: build bundle v0.3.0" in log_result.stdout

    def test_original_commits_preserved(self, tmp_path):
        """The developer's original commits should remain intact."""
        repo = make_git_repo(tmp_path)
        write_bundle_yml(repo, version="0.3.0", bundle_id="testbundle")
        write_catalog_json(repo, bundle_id="testbundle", version="0.1.0")
        bin_dir = create_specify_stub(repo)
        make_initial_commit(repo)

        initial_sha = get_head_sha(repo)
        make_bundle_change_commit(repo)

        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}
        stdin = build_stdin(get_head_sha(repo), initial_sha)
        result = run_hook(repo, stdin, env_extra=env)

        assert result.returncode == 6

        # Verify original commit still exists in log
        log_result = subprocess.run(
            ["git", "-C", str(repo), "log", "--oneline", "-3"],
            capture_output=True, text=True, check=True,
        )
        assert "bundle change" in log_result.stdout
        assert "initial" in log_result.stdout

    def test_zip_artifact_exists_after_build(self, tmp_path):
        """The zip file should exist at repo root after a successful build."""
        repo = make_git_repo(tmp_path)
        write_bundle_yml(repo, version="0.3.0", bundle_id="testbundle")
        write_catalog_json(repo, bundle_id="testbundle", version="0.1.0")
        bin_dir = create_specify_stub(repo)
        make_initial_commit(repo)

        initial_sha = get_head_sha(repo)
        make_bundle_change_commit(repo)

        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}
        stdin = build_stdin(get_head_sha(repo), initial_sha)
        result = run_hook(repo, stdin, env_extra=env)

        assert result.returncode == 6
        assert (repo / "testbundle-0.3.0.zip").exists()


# ---------------------------------------------------------------------------
# T014: Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Verify edge case handling for missing catalog.json and parse errors."""

    def test_creates_catalog_from_scratch_when_missing(self, tmp_path):
        """Hook should create catalog.json if it doesn't exist."""
        repo = make_git_repo(tmp_path)
        write_bundle_yml(repo, version="0.1.0", bundle_id="testbundle",
                        name="Test Bundle", description="A test bundle", role="developer")
        # No catalog.json written
        bin_dir = create_specify_stub(repo)
        make_initial_commit(repo)

        initial_sha = get_head_sha(repo)
        make_bundle_change_commit(repo)

        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}
        stdin = build_stdin(get_head_sha(repo), initial_sha)
        result = run_hook(repo, stdin, env_extra=env)

        assert result.returncode == 6
        assert (repo / "catalog.json").exists()
        catalog = json.loads((repo / "catalog.json").read_text())
        assert catalog["schema_version"] == "1.0"
        assert catalog["bundles"]["testbundle"]["version"] == "0.1.0"
        assert "raw.githubusercontent.com" in catalog["bundles"]["testbundle"]["download_url"]

    def test_exits_when_bundle_yml_missing(self, tmp_path):
        """Hook should exit 4 when bundle.yml is missing."""
        repo = make_git_repo(tmp_path)
        # Create bundle dir with a file but no bundle.yml
        bundle_dir = repo / "bundle"
        bundle_dir.mkdir()
        (bundle_dir / "test.txt").write_text("test\n")
        bin_dir = create_specify_stub(repo)
        make_initial_commit(repo)

        initial_sha = get_head_sha(repo)
        (bundle_dir / "test.txt").write_text("changed\n")
        subprocess.run(["git", "-C", str(repo), "add", "bundle/test.txt"],
                      capture_output=True, check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-m", "bundle change"],
                      capture_output=True, check=True)

        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}
        stdin = build_stdin(get_head_sha(repo), initial_sha)
        result = run_hook(repo, stdin, env_extra=env)

        assert result.returncode == 4
        assert "bundle.yml" in result.stderr
