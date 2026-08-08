"""Unit tests for extension manifest structure and file references.

Validates that each extension in the bundle has a well-formed extension.yml
and that all files referenced by the manifest exist on disk.
"""

from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXTENSIONS_DIR = PROJECT_ROOT / "bundle" / "extensions"

REQUIRED_EXTENSION_FIELDS = {"id", "name", "version", "description"}
REQUIRED_COMMAND_FIELDS = {"name", "file", "description"}


def load_extension_manifest(extension_id: str) -> dict:
    """Load and parse an extension.yml manifest."""
    manifest_path = EXTENSIONS_DIR / extension_id / "extension.yml"
    assert manifest_path.exists(), f"extension.yml not found at {manifest_path}"
    return yaml.safe_load(manifest_path.read_text())


class TestTrasgospecManifest:
    """Validate trasgospec extension manifest structure."""

    def test_manifest_exists(self):
        manifest_path = EXTENSIONS_DIR / "trasgospec" / "extension.yml"
        assert manifest_path.exists()

    def test_schema_version(self):
        manifest = load_extension_manifest("trasgospec")
        assert manifest["schema_version"] == "1.0"

    def test_required_extension_fields(self):
        manifest = load_extension_manifest("trasgospec")
        ext = manifest["extension"]
        for field in REQUIRED_EXTENSION_FIELDS:
            assert field in ext, f"Missing required field: {field}"

    def test_extension_id_matches_directory(self):
        manifest = load_extension_manifest("trasgospec")
        assert manifest["extension"]["id"] == "trasgospec"

    def test_requires_speckit_version(self):
        manifest = load_extension_manifest("trasgospec")
        assert "requires" in manifest
        assert "speckit_version" in manifest["requires"]

    def test_provides_four_commands(self):
        manifest = load_extension_manifest("trasgospec")
        assert "provides" in manifest
        commands = manifest["provides"]["commands"]
        assert len(commands) == 4

    def test_command_fields(self):
        manifest = load_extension_manifest("trasgospec")
        for cmd in manifest["provides"]["commands"]:
            for field in REQUIRED_COMMAND_FIELDS:
                assert field in cmd, f"Command missing required field: {field}"

    def test_hello_command_registered(self):
        manifest = load_extension_manifest("trasgospec")
        names = [c["name"] for c in manifest["provides"]["commands"]]
        assert "speckit.trasgospec.hello" in names

    def test_roadmap_command_registered(self):
        manifest = load_extension_manifest("trasgospec")
        names = [c["name"] for c in manifest["provides"]["commands"]]
        assert "speckit.trasgospec.roadmap" in names

    def test_command_files_exist(self):
        """Verify all command files referenced in the manifest exist on disk."""
        manifest = load_extension_manifest("trasgospec")
        ext_dir = EXTENSIONS_DIR / "trasgospec"
        for cmd in manifest["provides"]["commands"]:
            cmd_path = ext_dir / cmd["file"]
            assert cmd_path.exists(), f"Command file not found: {cmd_path}"

    def test_script_files_exist(self):
        """Verify script files referenced in command frontmatter exist on disk."""
        manifest = load_extension_manifest("trasgospec")
        ext_dir = EXTENSIONS_DIR / "trasgospec"
        for cmd in manifest["provides"]["commands"]:
            cmd_path = ext_dir / cmd["file"]
            content = cmd_path.read_text()
            if content.startswith("---"):
                end = content.index("---", 3)
                frontmatter = yaml.safe_load(content[3:end])
                if frontmatter and "scripts" in frontmatter:
                    for script_path in frontmatter["scripts"].values():
                        full_path = ext_dir / script_path
                        assert full_path.exists(), f"Script not found: {full_path}"
