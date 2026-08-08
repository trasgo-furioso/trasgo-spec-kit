# Implementation Plan: Conversational Discovery Command

**Branch**: `007-conversational-discovery` | **Date**: 2026-08-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/007-conversational-discovery/spec.md`

## Summary

Add a `speckit-trasgospec-discovery` command that guides users through interactive problem exploration before spec generation. The command follows the existing two-part extension pattern: a deterministic script (`discovery.sh`) handles spec directory creation and numbering, while a command file (`speckit.trasgospec.discovery.md`) contains AI agent instructions for the conversational loop, vagueness challenging, criteria-based completion, incremental persistence, and optional web research. The output is a structured `prd.md` that serves as enriched input to `/speckit-specify`.

## Technical Context

**Language/Version**: Bash 3.2+ (script), Markdown (command file — AI agent instructions)

**Primary Dependencies**: Spec Kit extension mechanism, existing `common.sh` helpers, Perplexity-based `/research` skill (for web research mode)

**Storage**: Filesystem — `prd.md` persisted in `specs/<NNN-slug>/`

**Testing**: pytest (unit tests for script, integration tests for end-to-end flow)

**Target Platform**: macOS/Linux (bash 3.2+ compatibility)

**Project Type**: CLI extension (bundle component)

**Performance Goals**: N/A — interactive command, human-paced

**Constraints**: No `mapfile`, no `readarray`, no process substitution (bash 3.2 compatibility). Script must be deterministic (no AI calls).

**Scale/Scope**: Single-user CLI invocation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Composition Over Creation | PASS | Uses extension pattern; composes existing primitives (commands, scripts, /research skill) |
| II. Spec Kit Native | PASS | Uses existing extension mechanism; does not duplicate Spec Kit functionality |
| III. Documentation-Driven | PASS | Design informed by existing command patterns (roadmap, flow-gate, flow-nudge) |
| IV. Idempotent & Traceable | PASS | Sequential numbering for traceability; directory creation is idempotent |
| V. Version-Pinned Distribution | PASS | No new unpinned dependencies introduced |
| VI. Test-Driven Development | PASS | Script testable via pytest; command testable via invocation |

## Project Structure

### Documentation (this feature)

```text
specs/007-conversational-discovery/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── discovery-script-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
bundle/extensions/trasgospec/
├── extension.yml                                    # ADD: discovery command entry
├── commands/
│   └── speckit.trasgospec.discovery.md               # NEW: command file (AI instructions)
└── scripts/bash/
    └── discovery.sh                                  # NEW: deterministic script

tests/
├── unit/
│   └── test_discovery.py                             # NEW: script unit tests
└── integration/
    └── test_discovery_integration.py                 # NEW: end-to-end tests
```

**Structure Decision**: Follows the existing single-project layout. Two new files in `bundle/extensions/trasgospec/` (command + script), one modification to `extension.yml`, and new test files under `tests/`.

## Complexity Tracking

No constitution violations. No complexity justification needed.
