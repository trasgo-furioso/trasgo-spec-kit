"""Unit tests for bundle.yml manifest structure.

Validates that bundle.yml declares extensions (not skills) and that
extension references match the actual extension.yml files on disk.
"""

from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_ROOT = PROJECT_ROOT / "bundle"
BUNDLE_YML = BUNDLE_ROOT / "bundle.yml"
EXTENSIONS_DIR = BUNDLE_ROOT / "extensions"


def load_bundle_manifest() -> dict:
    """Load and parse bundle.yml."""
    assert BUNDLE_YML.exists(), f"bundle.yml not found at {BUNDLE_YML}"
    return yaml.safe_load(BUNDLE_YML.read_text())


class TestBundleProvidesExtensions:
    """US1: Bundle manifest must declare extensions, not skills."""

    def test_provides_extensions_key_exists(self):
        manifest = load_bundle_manifest()
        assert "provides" in manifest
        assert "extensions" in manifest["provides"], (
            "bundle.yml must declare provides.extensions"
        )

    def test_provides_skills_key_absent(self):
        manifest = load_bundle_manifest()
        assert "skills" not in manifest.get("provides", {}), (
            "bundle.yml must not declare provides.skills"
        )

    def test_at_least_one_extension_declared(self):
        manifest = load_bundle_manifest()
        extensions = manifest["provides"]["extensions"]
        assert len(extensions) >= 1


class TestBundleExtensionIdsMatchFiles:
    """US1: Extension IDs in bundle.yml must match extension.yml files on disk."""

    def test_all_declared_extensions_have_manifest(self):
        manifest = load_bundle_manifest()
        for ext in manifest["provides"]["extensions"]:
            ext_id = ext["id"]
            ext_manifest_path = EXTENSIONS_DIR / ext_id / "extension.yml"
            assert ext_manifest_path.exists(), (
                f"Extension '{ext_id}' declared in bundle.yml but "
                f"extension.yml not found at {ext_manifest_path}"
            )

    def test_declared_ids_match_manifest_ids(self):
        manifest = load_bundle_manifest()
        for ext in manifest["provides"]["extensions"]:
            ext_id = ext["id"]
            ext_manifest = yaml.safe_load(
                (EXTENSIONS_DIR / ext_id / "extension.yml").read_text()
            )
            assert ext_manifest["extension"]["id"] == ext_id, (
                f"ID mismatch: bundle.yml says '{ext_id}' but "
                f"extension.yml says '{ext_manifest['extension']['id']}'"
            )


class TestBundleExtensionVersionsMatch:
    """US1: Extension versions in bundle.yml must match extension.yml versions."""

    def test_versions_match(self):
        manifest = load_bundle_manifest()
        for ext in manifest["provides"]["extensions"]:
            ext_id = ext["id"]
            bundle_version = ext["version"]
            ext_manifest = yaml.safe_load(
                (EXTENSIONS_DIR / ext_id / "extension.yml").read_text()
            )
            ext_version = ext_manifest["extension"]["version"]
            assert bundle_version == ext_version, (
                f"Version mismatch for '{ext_id}': bundle.yml says "
                f"'{bundle_version}' but extension.yml says '{ext_version}'"
            )
