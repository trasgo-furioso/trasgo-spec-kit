# Implementation Plan: Audit and Logs

**Branch**: `011-audit-and-logs` | **Date**: 2026-08-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/011-audit-and-logs/spec.md`

## Summary

Add automatic git commits after every artifact-producing skill invocation. A new two-part extension command (`speckit.trasgospec.audit-commit`) detects changed/new files in the feature's spec directory, generates one-liner descriptions by inspecting diffs, and creates a single commit per skill invocation with a `[speckit:audit]` tag. Registered as `after_*` hooks with priority 20 (runs last).

## Technical Context

**Language/Version**: Bash 3.2+ (macOS default), matching all existing scripts

**Primary Dependencies**: git (always available in trasgospec projects), `.specify/feature.json` (locates spec directory)

**Storage**: N/A — uses git commits as the persistence mechanism

**Testing**: pytest (unit tests for the bash script, integration tests for the hook chain)

**Target Platform**: macOS (bash 3.2+), Linux

**Project Type**: CLI extension (Spec Kit bundle)

**Performance Goals**: N/A — hook runs once per skill invocation

**Constraints**: No `mapfile`/`readarray` (bash 3.2), must use `set -euo pipefail`, must walk up to find `.specify` root

**Scale/Scope**: 8 hook registrations (one per artifact-producing skill)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Composition Over Creation | PASS | New extension command using the documented two-part pattern (command + script) |
| II. Spec Kit Native | PASS | Uses Spec Kit extension hooks, no duplication of existing features |
| III. Documentation-Driven Development | PASS | Design follows established patterns from flow-nudge, flow-gate, discovery |
| IV. Idempotent & Traceable | PASS | Hook is idempotent — running with no changes produces "No artifact changes" message |
| V. Version-Pinned Distribution | PASS | Command registered in extension.yml with explicit version |
| VI. Test-Driven Development | PASS | Tests written first via pytest |

No violations. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/011-audit-and-logs/
├── prd.md
├── spec.md
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
bundle/extensions/trasgospec/
├── extension.yml                                    # MODIFY: add audit-commit command + after_* hooks
├── commands/
│   └── speckit.trasgospec.audit-commit.md            # NEW: command file (AI instructions)
└── scripts/bash/
    └── audit-commit.sh                              # NEW: script file (deterministic logic)

tests/
├── unit/
│   └── test_audit_commit.py                         # NEW: unit tests for audit-commit.sh
└── integration/
    └── test_audit_commit_integration.py             # NEW: integration tests for hook chain
```

**Structure Decision**: Follows the existing extension two-part pattern. One new command file and one new script file, plus hook registrations in extension.yml.
