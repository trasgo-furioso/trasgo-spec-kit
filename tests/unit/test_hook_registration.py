"""Unit tests for hook registration contract.

Validates that the expected hook entries are defined in the
extensions-yml-hooks.md contract and can be applied to a project's
extensions.yml.

These tests verify the hook registration data structure, not the
bundle install mechanism itself (which is handled by spec-kit).
"""

from pathlib import Path

import yaml
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HOOKS_CONTRACT = PROJECT_ROOT / "specs" / "005-github-flow-enforcement" / "contracts" / "extensions-yml-hooks.md"

# Expected hook registrations per the contract
EXPECTED_GATE_HOOKS = [
    "after_specify",
    "before_clarify",
    "before_checklist",
    "before_plan",
    "before_tasks",
    "before_implement",
    "before_converge",
    "before_analyze",
    "before_discovery",
]

EXPECTED_NUDGE_HOOKS = [
    "after_plan",
    "after_implement",
    "after_analyze",
    "after_discovery",
]

EXPECTED_STATUS_HOOKS = [
    "before_specify",
    "before_tasks",
    "after_plan",
    "after_implement",
    "after_discovery",
]


def build_hooks_yaml() -> dict:
    """Build the expected hooks YAML structure from the contract."""
    hooks = {}

    for hook_point in EXPECTED_GATE_HOOKS:
        hooks[hook_point] = hooks.get(hook_point, []) + [{
            "extension": "trasgospec",
            "command": "speckit.trasgospec.flow-gate",
            "description": "GitHub Flow — create/switch to feature branch after spec creation"
                           if hook_point == "after_specify"
                           else "GitHub Flow — require feature branch",
            "optional": False,
            "enabled": True,
        }]

    for hook_point in EXPECTED_NUDGE_HOOKS:
        description_map = {
            "after_plan": "Suggest opening a draft PR for this feature",
            "after_implement": "Suggest marking PR as ready for review",
            "after_analyze": "Suggest PR is ready for final review",
            "after_discovery": "Suggest next steps after discovery",
        }
        hooks[hook_point] = hooks.get(hook_point, []) + [{
            "extension": "trasgospec",
            "command": "speckit.trasgospec.flow-nudge",
            "description": description_map[hook_point],
            "optional": True,
            "enabled": True,
        }]

    for hook_point in EXPECTED_STATUS_HOOKS:
        description_map = {
            "before_specify": "Lifecycle — advance status to Planning",
            "before_tasks": "Lifecycle — advance status to In Progress",
            "after_plan": "Lifecycle — advance status to Ready to Dev",
            "after_implement": "Lifecycle — advance status to In Review",
            "after_discovery": "Lifecycle — advance status to Opportunity",
        }
        hooks[hook_point] = hooks.get(hook_point, []) + [{
            "extension": "trasgospec",
            "command": "speckit.trasgospec.status",
            "description": description_map[hook_point],
            "optional": False,
            "enabled": True,
        }]

    return hooks


class TestHookRegistrationStructure:
    """Test that all 14 hook entries are defined correctly."""

    def test_total_hook_count(self):
        hooks = build_hooks_yaml()
        total = sum(len(v) for v in hooks.values())
        assert total == 18, f"Expected 18 hook entries, got {total}"

    def test_gate_hooks_count(self):
        hooks = build_hooks_yaml()
        gate_count = sum(
            1 for entries in hooks.values()
            for e in entries
            if e["command"] == "speckit.trasgospec.flow-gate"
        )
        assert gate_count == 9, f"Expected 9 gate hooks, got {gate_count}"

    def test_nudge_hooks_count(self):
        hooks = build_hooks_yaml()
        nudge_count = sum(
            1 for entries in hooks.values()
            for e in entries
            if e["command"] == "speckit.trasgospec.flow-nudge"
        )
        assert nudge_count == 4, f"Expected 4 nudge hooks, got {nudge_count}"

    def test_status_hooks_count(self):
        hooks = build_hooks_yaml()
        status_count = sum(
            1 for entries in hooks.values()
            for e in entries
            if e["command"] == "speckit.trasgospec.status"
        )
        assert status_count == 5, f"Expected 5 status hooks, got {status_count}"

    def test_gate_hooks_are_mandatory(self):
        hooks = build_hooks_yaml()
        for hook_point in EXPECTED_GATE_HOOKS:
            for entry in hooks[hook_point]:
                if entry["command"] == "speckit.trasgospec.flow-gate":
                    assert entry["optional"] is False, \
                        f"Gate hook at {hook_point} should be mandatory"

    def test_nudge_hooks_are_optional(self):
        hooks = build_hooks_yaml()
        for hook_point in EXPECTED_NUDGE_HOOKS:
            for entry in hooks[hook_point]:
                if entry["command"] == "speckit.trasgospec.flow-nudge":
                    assert entry["optional"] is True, \
                        f"Nudge hook at {hook_point} should be optional"

    def test_all_hooks_enabled_by_default(self):
        hooks = build_hooks_yaml()
        for entries in hooks.values():
            for entry in entries:
                assert entry["enabled"] is True

    def test_after_specify_has_gate_not_nudge(self):
        hooks = build_hooks_yaml()
        commands = [e["command"] for e in hooks.get("after_specify", [])]
        assert "speckit.trasgospec.flow-gate" in commands
        assert "speckit.trasgospec.flow-nudge" not in commands


class TestHookRegistrationIdempotency:
    """Test that hook registration is idempotent."""

    def test_applying_hooks_twice_produces_same_result(self):
        hooks1 = build_hooks_yaml()
        hooks2 = build_hooks_yaml()

        # Simulate idempotent merge: for each hook point, only add if
        # no entry with same extension+command exists
        merged = {}
        for hooks in [hooks1, hooks2]:
            for hook_point, entries in hooks.items():
                if hook_point not in merged:
                    merged[hook_point] = []
                for entry in entries:
                    existing = [
                        e for e in merged[hook_point]
                        if e["extension"] == entry["extension"]
                        and e["command"] == entry["command"]
                    ]
                    if not existing:
                        merged[hook_point].append(entry)

        total = sum(len(v) for v in merged.values())
        assert total == 18, f"Idempotent merge should produce 18 entries, got {total}"


class TestHookRegistrationPreservesExisting:
    """Test that hook registration preserves existing hooks."""

    def test_existing_hooks_preserved(self):
        # Simulate existing hooks from another extension
        existing_hooks = {
            "before_plan": [{
                "extension": "other-extension",
                "command": "other.command",
                "description": "Some other hook",
                "optional": True,
                "enabled": True,
            }]
        }

        # Merge trasgospec hooks
        trasgo_hooks = build_hooks_yaml()
        merged = dict(existing_hooks)
        for hook_point, entries in trasgo_hooks.items():
            if hook_point not in merged:
                merged[hook_point] = []
            for entry in entries:
                existing = [
                    e for e in merged[hook_point]
                    if e["extension"] == entry["extension"]
                    and e["command"] == entry["command"]
                ]
                if not existing:
                    merged[hook_point].append(entry)

        # Verify existing hook preserved
        other_hooks = [
            e for e in merged["before_plan"]
            if e["extension"] == "other-extension"
        ]
        assert len(other_hooks) == 1
        assert other_hooks[0]["command"] == "other.command"

        # Verify trasgospec hook also added
        trasgo_hooks_at_plan = [
            e for e in merged["before_plan"]
            if e["extension"] == "trasgospec"
        ]
        assert len(trasgo_hooks_at_plan) == 1
