# Implementation Plan: GitHub Flow Enforcement

**Branch**: `005-github-flow-enforcement` | **Date**: 2026-08-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/005-github-flow-enforcement/spec.md`

## Summary

Enforce GitHub Flow branching discipline through two new trasgospec extension commands — `flow-gate` (mandatory `before_*` hook) and `flow-nudge` (optional `after_*` hook) — registered in `.specify/extensions.yml` on bundle install. A shared `flow_context.sh` script provides deterministic git state as JSON. The `gh` CLI integration is configurable via extension input with graceful fallback to output-only mode.

## Technical Context

**Language/Version**: Bash 3.2+ (macOS compatibility, per constitution), Python 3.x for tests

**Primary Dependencies**: git (required), gh CLI (optional, for PR operations)

**Storage**: N/A — reads git state and `.specify/feature.json`; writes to `.specify/extensions.yml` during install

**Testing**: pytest (per constitution)

**Target Platform**: macOS/Linux (any system with bash 3.2+ and git)

**Project Type**: CLI extension bundle (spec-kit bundle)

**Performance Goals**: Flow context JSON output within 2 seconds on repos up to 10,000 commits

**Constraints**: No `mapfile`, no `readarray`, no process substitution; must source `common.sh` opportunistically with inline fallback; must use `set -euo pipefail`

**Scale/Scope**: 8 hook registrations (before_*) + 3 hook registrations (after_*) = 11 hook entries in extensions.yml; 2 new command files; 2 new scripts (flow-context + flow-gate/nudge share context); updates to extension.yml and bundle.yml

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Composition Over Creation | PASS | Uses existing spec-kit hook mechanism; new commands follow the extension two-part pattern |
| II. Spec Kit Native | PASS | Leverages hook lifecycle (`before_*`/`after_*`) already built into skills; no duplication |
| III. Documentation-Driven Development | PASS | Hook mechanism documented in skill templates; extension pattern documented in constitution |
| IV. Idempotent & Traceable | PASS | Hook registration must be idempotent (FR-020); bundle install/uninstall tracked |
| V. Version-Pinned Distribution | PASS | Bundle version bumped in bundle.yml and extension.yml |
| VI. Test-Driven Development | PASS | All implementation must follow TDD cycle with pytest |

No violations. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/005-github-flow-enforcement/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── flow-context-output.md
│   └── extensions-yml-hooks.md
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
bundle/extensions/trasgospec/
├── extension.yml                              # Updated: add flow-gate and flow-nudge commands
├── commands/
│   ├── speckit.trasgospec.hello.md             # Existing (unchanged)
│   ├── speckit.trasgospec.roadmap.md           # Existing (unchanged)
│   ├── speckit.trasgospec.flow-gate.md         # NEW: branch gating command
│   └── speckit.trasgospec.flow-nudge.md        # NEW: PR nudge command
└── scripts/bash/
    ├── scan-specs.sh                          # Existing (unchanged)
    ├── flow-context.sh                        # NEW: shared git state → JSON
    └── flow-nudge.sh                          # NEW: PR state detection → JSON

tests/unit/
├── test_flow_context.py                       # NEW: flow-context.sh contract tests
├── test_flow_gate.py                          # NEW: flow-gate behavior tests
├── test_flow_nudge.py                         # NEW: flow-nudge behavior tests
└── test_extension_manifests.py                # Existing: update expected command count
```

**Structure Decision**: Follows existing bundle layout. New commands and scripts placed alongside existing ones. The `flow-context.sh` script is shared (sourced by `flow-gate` and `flow-nudge` command files via their respective scripts). `flow-nudge.sh` is a separate script because it needs to query PR state via `gh`, which is distinct from the git-local state in `flow-context.sh`.

## Post-Phase 1 Constitution Re-Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Composition Over Creation | PASS | Two extension commands + hook registrations; no modification to existing skills |
| II. Spec Kit Native | PASS | Pure hook-based integration |
| III. Documentation-Driven Development | PASS | Contracts document JSON output and hook registration format |
| IV. Idempotent & Traceable | PASS | Hook registration designed to be idempotent |
| V. Version-Pinned Distribution | PASS | Version bump from 0.2.0 to 0.3.0 planned |
| VI. Test-Driven Development | PASS | Three new test files, TDD cycle enforced |
