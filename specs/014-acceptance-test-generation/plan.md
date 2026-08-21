# Implementation Plan: Acceptance Test Generation

**Branch**: `014-acceptance-test-generation` | **Date**: 2026-08-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/014-acceptance-test-generation/spec.md`

## Summary

Create a new bundle extension command `speckit.trasgospec.acceptance-tests` that converts Given/When/Then acceptance scenarios from spec.md into Playwright E2E test files. The command is AI-agent-only (no bash script), following the `speckit.trasgospec.hello` precedent. It also ships two new preset templates: `acceptance-test-template` (test file structure) and `testing-surface-contract` (selector contract format). The command is invoked by `/speckit-implement` during task execution and generates tests organized by user story with Page Object Model composition, accessibility-first selectors, and `test.step()` GWT structure.

## Technical Context

**Language/Version**: Markdown (command file) — the command is an AI agent instruction document, not executable code

**Primary Dependencies**: Spec Kit bundle system (commands, presets, templates), Playwright (target output framework)

**Storage**: File system — generates `.spec.ts`, `.page.ts`, `fixtures.ts` files into the consumer project's e2e directory

**Testing**: No unit tests for the command file itself (AI-only command). Validation through manual invocation and acceptance scenarios. The *generated output* is validated by Playwright Test.

**Target Platform**: Any web project using Playwright for E2E testing

**Project Type**: Bundle extension (command file + preset templates)

**Performance Goals**: N/A — file generation by AI agent

**Constraints**: Must follow Spec Kit bundle conventions; command file + templates only; no bash scripts

**Scale/Scope**: Single command file, 2 preset templates, 1 extension manifest update

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Composition Over Creation | PASS | Composes Spec Kit primitives: command, preset templates, template resolution stack |
| II. Spec Kit Native | PASS | Uses presets, templates, bundle distribution — no parallel systems |
| III. Documentation-Driven | PASS | Command file IS the documentation; follows existing command patterns |
| IV. Idempotent & Traceable | PASS | Idempotent generation (SC-005); traceability headers in output |
| V. Version-Pinned | PASS | Declared in bundle.yml with explicit version |
| VI. Test-Driven | N/A | AI-only command has no deterministic script to unit test. Validation via acceptance scenarios. |
| VII. Template-Driven | PASS | Ships acceptance-test-template and testing-surface-contract templates; user-overridable via `.specify/templates/overrides/` |
| VIII. Bundle-Native | PASS | Extension command + preset templates — correct component types declared in bundle.yml |

No violations. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/014-acceptance-test-generation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── command-file.md
│   ├── acceptance-test-template.md
│   └── testing-surface-contract-template.md
└── tasks.md
```

### Source Code (repository root)

```text
bundle/
├── extensions/trasgospec/
│   ├── extension.yml                                          # UPDATE: add new command entry
│   └── commands/
│       └── speckit.trasgospec.acceptance-tests.md              # NEW: AI agent command file
└── presets/trasgospec/
    └── templates/
        ├── acceptance-test-template.md                        # NEW: test file output structure
        └── testing-surface-contract.md                        # NEW: selector contract format
```

**Structure Decision**: This feature adds 1 command file and 2 template files to the existing bundle structure. No new directories, no new scripts, no new source code beyond these 3 files + 1 manifest update.
