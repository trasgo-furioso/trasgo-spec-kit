# Implementation Plan: Discovery Command Hooks

**Branch**: `010-discovery-hooks` | **Date**: 2026-08-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/010-discovery-hooks/spec.md`

## Summary

Add `before_discovery` and `after_discovery` hook dispatch to the discovery command (`speckit.trasgospec.discovery`), bringing it into parity with all other Spec Kit skills. The implementation copies the exact hook dispatch pattern from speckit-plan and speckit-specify, adapting only the hook key names. It registers three hook entries in `.specify/extensions.yml` (flow-gate for branch gating, status for Discovery-to-Opportunity transition, flow-nudge for PR suggestion) and declares those hooks in the bundle's `extension.yml`. No new scripts or commands are created — this is a wiring exercise composing existing infrastructure.

## Technical Context

**Language/Version**: Bash 3.2+ (scripts), Python 3.x (tests), Markdown (commands/skills)

**Primary Dependencies**: Existing commands `speckit.trasgospec.flow-gate`, `speckit.trasgospec.status`, `speckit.trasgospec.flow-nudge`; Spec Kit hook dispatch pattern

**Storage**: `.specify/extensions.yml` (YAML), markdown command/skill files

**Testing**: pytest (`.venv/bin/pytest`)

**Target Platform**: macOS / Linux (bash 3.2+)

**Project Type**: CLI extension bundle

**Performance Goals**: N/A (hook dispatch is instantaneous)

**Constraints**: No new bash scripts. No new extension commands. Changes limited to markdown command files and YAML config.

**Scale/Scope**: Single-user projects

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Composition Over Creation | PASS | Reuses existing flow-gate, status, and flow-nudge commands; copies established hook dispatch pattern |
| II. Spec Kit Native | PASS | Uses Spec Kit's hook dispatch protocol verbatim |
| III. Documentation-Driven Development | PASS | Pattern sourced from speckit-plan and speckit-specify SKILL.md files |
| IV. Idempotent & Traceable | PASS | Hook registrations are declarative YAML; adding same entries is idempotent |
| V. Version-Pinned Distribution | PASS | No new version dependencies introduced |
| VI. Test-Driven Development | PASS | Tests written first for YAML structure and command file content |

## Project Structure

### Documentation (this feature)

```text
specs/010-discovery-hooks/
├── spec.md
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── hook-registration.md
│   └── command-blocks.md
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
bundle/extensions/trasgospec/
├── extension.yml                                        # MODIFY: add before_discovery + after_discovery hook declarations
├── commands/
│   └── speckit.trasgospec.discovery.md                  # MODIFY: add Pre-Execution Checks + Mandatory Post-Execution Hooks sections
└── scripts/bash/
    └── discovery.sh                                     # NO CHANGE

.specify/
├── extensions.yml                                       # NO CHANGE: it's managed by speckit
└── extensions/trasgospec/scripts/bash/
    └── discovery.sh                                     # NO CHANGE

.claude/skills/
└── speckit-trasgospec-discovery/
    └── SKILL.md                                         # NO CHANGE: it's managed by speckit

tests/unit/
├── test_hook_registration.py                            # MODIFY: add discovery hook entry tests
└── test_discovery_hooks.py                              # NEW: test command file contains hook dispatch blocks
```

**Structure Decision**: Extends existing bundle structure. No new directories except `specs/010-discovery-hooks/contracts/`. One test file added. Four existing files modified.
