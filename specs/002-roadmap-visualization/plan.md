# Implementation Plan: Roadmap Visualization

**Branch**: `002-roadmap-visualization` | **Date**: 2026-08-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-roadmap-visualization/spec.md`

## Summary

Add a `/trasgospec-roadmap` skill to the Trasgo Spec Kit bundle that scans
the project's `specs/` directory, extracts metadata (title, status, creation
date) from each `spec.md`, and returns a markdown table summarizing the
project roadmap. The skill is a Spec Kit skill component — a Markdown
instruction file with no runtime code. Spec statuses are free-form text
(no official enum); the skill reads whatever value is in the `**Status**:`
field. Integration tests follow the same pytest + `specify` CLI pattern
established in 001-bundle-install.

## Technical Context

**Language/Version**: Markdown (skill definition), YAML (bundle manifest
update), Python 3.11+ (dev-only testing)

**Primary Dependencies**:
- `specify` CLI (Spec Kit skill invocation and bundle management)
- `pytest` (dev-only, integration tests)

**Storage**: N/A (reads existing `spec.md` files from filesystem)

**Testing**: pytest — integration tests map acceptance scenarios
(Given/When/Then) to Arrange/Act/Assert. Tests create temp projects with
spec directories and invoke the skill via the AI agent.

**Target Platform**: Spec Kit projects using the `claude` integration

**Project Type**: Spec Kit bundle skill (distribution component)

**Performance Goals**: Results returned in under 5 seconds for up to 50
specs (SC-001)

**Constraints**: Skill is a Markdown instruction file only — no executable
code in the bundle. The AI agent interprets the instructions and performs
the filesystem scan at invocation time.

**Scale/Scope**: 1 new skill added to existing bundle. Bundle version
bump from 0.1.0 to 0.2.0.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Composition Over Creation | PASS | Skill is a SK component type (Markdown instructions); no runtime behavior added to the bundle itself |
| II. Spec Kit Native | PASS | Uses SK skill format, `bundle.yml` provides section, and SK conventions for spec directory structure |
| III. Documentation-Driven | PASS | Researched SK skill format, spec template fields, and status lifecycle before designing |
| IV. Idempotent & Traceable | PASS | Read-only skill; does not modify any files. Bundle install remains idempotent via SK machinery |
| V. Version-Pinned Distribution | PASS | New skill version-pinned in `bundle.yml` provides section |

All gates pass. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/002-roadmap-visualization/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
bundle/
├── bundle.yml                          # Updated: add trasgospec-roadmap skill
└── skills/
    ├── trasgospec/
    │   └── SKILL.md                    # Existing hello command (unchanged)
    └── trasgospec-roadmap/
        └── SKILL.md                    # NEW: roadmap visualization skill

tests/
└── integration/
    ├── conftest.py                     # Shared fixtures (reuse from 001)
    ├── test_us1_install.py             # Existing (unchanged)
    ├── test_edge_cases.py              # Existing (unchanged)
    └── test_us1_roadmap.py             # NEW: roadmap acceptance tests
```

**Structure Decision**: New skill follows the same pattern as the existing
`trasgospec` skill — a `SKILL.md` file in `bundle/skills/<skill-id>/`.
The bundle manifest (`bundle.yml`) is updated to declare the new skill in
the `provides.skills` list. Tests go in the existing `tests/integration/`
directory.
