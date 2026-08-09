# Implementation Plan: Audit and Logs

**Branch**: `011-audit-and-logs` | **Date**: 2026-08-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/011-audit-and-logs/spec.md` (revised)

## Summary

Add a reusable commit command (`speckit.trasgospec.commit`) that performs the full git cycle: detect repo-wide changes, use AI judgment to decide what to include, stage, commit with structured `<path> - <description>` messages, and push. Registered as `after_*` hooks with priority 20 for all artifact-producing skills. Also adds `.specify/` to `.gitignore` since it is user-environment state.

## Technical Context

**Language/Version**: Bash 3.2+ (macOS default), matching all existing scripts

**Primary Dependencies**: git (always available in trasgospec projects)

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
| IV. Idempotent & Traceable | PASS | Hook is idempotent — running with no changes produces "No changes to commit." |
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
├── contracts/
│   ├── commit-script-json.md
│   └── extension-yml-hooks.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
bundle/extensions/trasgospec/
├── extension.yml                                    # MODIFY: add commit command + after_* hooks
├── commands/
│   └── speckit.trasgospec.commit.md                  # NEW: command file (AI instructions)
└── scripts/bash/
    └── commit.sh                                    # NEW: script file (deterministic git status/diff)

.gitignore                                           # MODIFY: add .specify/

tests/
├── unit/
│   └── test_commit.py                               # NEW: unit tests for commit.sh
└── integration/
    └── test_commit_integration.py                   # NEW: integration tests for hook chain
```

**Structure Decision**: Follows the existing extension two-part pattern. One new command file and one new script file, `.gitignore` update, plus hook registrations in extension.yml.
