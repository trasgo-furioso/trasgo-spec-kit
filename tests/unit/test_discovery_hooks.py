"""Unit tests for discovery command hook dispatch blocks.

Validates that the discovery command file and extension.yml contain
the required hook infrastructure for before_discovery and after_discovery.
"""

from pathlib import Path

import yaml
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMMAND_FILE = PROJECT_ROOT / "bundle" / "extensions" / "trasgospec" / "commands" / "speckit.trasgospec.discovery.md"
EXTENSION_YML = PROJECT_ROOT / "bundle" / "extensions" / "trasgospec" / "extension.yml"


@pytest.fixture
def command_content():
    return COMMAND_FILE.read_text()


@pytest.fixture
def extension_yml():
    return yaml.safe_load(EXTENSION_YML.read_text())


class TestDiscoveryCommandPreHooks:
    """T008: Command file contains Pre-Execution Checks section."""

    def test_has_pre_execution_checks_section(self, command_content):
        assert "## Pre-Execution Checks" in command_content

    def test_pre_hooks_before_goal(self, command_content):
        pre_idx = command_content.index("Pre-Execution Checks")
        goal_idx = command_content.index("## Goal")
        assert pre_idx < goal_idx, "Pre-Execution Checks must appear before Goal"


class TestDiscoveryCommandPostHooks:
    """T009: Command file contains Mandatory Post-Execution Hooks section."""

    def test_has_post_execution_hooks_section(self, command_content):
        assert "## Mandatory Post-Execution Hooks" in command_content

    def test_post_hooks_before_done_when(self, command_content):
        post_idx = command_content.index("Mandatory Post-Execution Hooks")
        done_idx = command_content.index("## Done When")
        assert post_idx < done_idx, "Post-Execution Hooks must appear before Done When"


class TestDiscoveryHookKeys:
    """T010: Command file references correct hook keys."""

    def test_references_before_discovery_key(self, command_content):
        assert "hooks.before_discovery" in command_content

    def test_references_after_discovery_key(self, command_content):
        assert "hooks.after_discovery" in command_content


class TestDiscoveryAbortGuard:
    """T011: Post-hooks block contains abort guard."""

    def test_abort_guard_present(self, command_content):
        post_section_start = command_content.index("Mandatory Post-Execution Hooks")
        post_section = command_content[post_section_start:]
        assert "aborted" in post_section.lower() or "skip this section" in post_section.lower(), \
            "Post-hooks must contain abort guard for aborted sessions"


class TestDiscoveryHookProtocol:
    """T012: Command file contains hook dispatch protocol."""

    def test_has_execute_command_directive(self, command_content):
        assert "EXECUTE_COMMAND" in command_content

    def test_has_optional_flag_handling(self, command_content):
        assert "optional" in command_content.lower()

    def test_has_mandatory_hook_block(self, command_content):
        assert "Mandatory hook" in command_content or "**Mandatory hook**" in command_content


class TestDiscoveryDotToHyphen:
    """T013: Command file contains dot-to-hyphen mapping instruction (FR-006)."""

    def test_dot_to_hyphen_instruction(self, command_content):
        assert "replace dots" in command_content.lower() or \
               "dots (`.`) with hyphens (`-`)" in command_content


class TestExtensionYmlAfterDiscovery:
    """T017-T018: extension.yml contains after_discovery hooks."""

    def test_after_discovery_key_exists(self, extension_yml):
        hooks = extension_yml.get("hooks", {})
        assert "after_discovery" in hooks, "extension.yml must have after_discovery hooks"

    def test_after_discovery_has_status_command(self, extension_yml):
        hooks = extension_yml["hooks"]["after_discovery"]
        if not isinstance(hooks, list):
            hooks = [hooks]
        status_entries = [h for h in hooks if h.get("command") == "speckit.trasgospec.status"]
        assert len(status_entries) == 1, "after_discovery must have speckit.trasgospec.status"
        assert status_entries[0]["optional"] is False, "status hook must be mandatory"
        assert "Opportunity" in status_entries[0].get("description", ""), \
            "status hook description must mention Opportunity"


class TestExtensionYmlBeforeDiscovery:
    """T020-T021: extension.yml contains before_discovery hooks."""

    def test_before_discovery_key_exists(self, extension_yml):
        hooks = extension_yml.get("hooks", {})
        assert "before_discovery" in hooks, "extension.yml must have before_discovery hooks"

    def test_before_discovery_has_flow_gate(self, extension_yml):
        hooks = extension_yml["hooks"]["before_discovery"]
        if not isinstance(hooks, list):
            hooks = [hooks]
            if isinstance(hooks[0], dict) and "command" in hooks[0]:
                pass
            else:
                hooks = [extension_yml["hooks"]["before_discovery"]]
        # Handle both single dict and list formats
        hook = hooks[0] if isinstance(hooks, list) else hooks
        assert hook.get("command") == "speckit.trasgospec.flow-gate", \
            "before_discovery must use speckit.trasgospec.flow-gate"
        assert hook.get("optional") is False, \
            "before_discovery flow-gate must be mandatory"
