# Implementation Plan: Spec Lifecycle Management

**Branch**: `009-spec-lifecycle-management` | **Date**: 2026-08-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/009-spec-lifecycle-management/spec.md`

## Summary

Add structured lifecycle tracking to trasgospec features. Extends `scan-specs.sh` to scan prd.md files (not just spec.md), adds title extraction from `# PRD:` headings, and surfaces all features on the roadmap regardless of lifecycle phase. Introduces a status management extension command (`trasgospec.roadmap.status.change`) following the two-part pattern, and registers hook entries in `extension.yml` to auto-advance status at key workflow transitions.

## Technical Context

**Language/Version**: Bash 3.2+ (scripts), Python 3.x (tests), Markdown (commands/skills)

**Primary Dependencies**: Spec Kit extension framework, git CLI (for unblock via `git log`)

**Storage**: Markdown files (`**Status**:` field in prd.md / spec.md)

**Testing**: pytest (unit tests in `tests/unit/`, integration tests in `tests/integration/`)

**Target Platform**: macOS / Linux (bash 3.2+ compatibility)

**Project Type**: CLI extension bundle

**Performance Goals**: N/A (local filesystem scanning, sub-second operations)

**Constraints**: Bash 3.2+ (no `mapfile`, no `readarray`), single-line JSON on stdout, `set -euo pipefail`

**Scale/Scope**: Single-user projects with <100 feature directories

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Composition Over Creation | PASS | New command follows extension two-part pattern. Extends existing `scan-specs.sh` rather than creating parallel scanner. |
| II. Spec Kit Native | PASS | Uses existing hook infrastructure in `extensions.yml`. Status field uses same markdown pattern as existing spec.md. |
| III. Documentation-Driven Development | PASS | Design informed by existing patterns in flow-gate, flow-nudge, scan-specs. |
| IV. Idempotent & Traceable | PASS | Status writes are idempotent (setting same status twice = no-op). Hook registrations follow existing pattern. |
| V. Version-Pinned Distribution | PASS | New command registered in `extension.yml` with version tracking. |
| VI. Test-Driven Development | PASS | Tests written first per TDD cycle. Unit tests for script, acceptance tests per spec scenarios. |

## Project Structure

### Documentation (this feature)

```text
specs/009-spec-lifecycle-management/
├── prd.md
├── spec.md
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── status-change-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
bundle/extensions/trasgospec/
├── extension.yml                                      # Add status-change command + hook registrations
├── commands/
│   └── speckit.trasgospec.roadmap.status.change.md    # NEW: status management command
└── scripts/bash/
    ├── scan-specs.sh                                   # MODIFY: scan prd.md, extract # PRD: title
    └── status-change.sh                               # NEW: status management script

.specify/extensions/trasgospec/scripts/bash/
    └── scan-specs.sh                                   # MODIFY: same changes (installed copy)

.claude/skills/
    └── speckit-trasgospec-roadmap-status-change/       # NEW: skill file for status command
        └── SKILL.md

tests/unit/
├── test_scan_specs.py                                  # MODIFY: add PRD scanning tests
└── test_status_change.py                              # NEW: status management tests
```

**Structure Decision**: Extends existing bundle structure. No new top-level directories. One new extension command + script pair following the established two-part pattern.
