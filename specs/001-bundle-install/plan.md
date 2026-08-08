# Implementation Plan: Bundle Install

**Branch**: `001-bundle-install` | **Date**: 2026-08-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-bundle-install/spec.md`

## Summary

Create a minimal scaffold Spec Kit bundle that is installable via
self-hosted catalog, with automated build and distribution. The bundle
declares a single `/trasgospec` hello skill targeting the `claude`
integration. Distribution uses a catalog JSON file hosted as a raw
GitHub file. A local pre-push git hook automates validation, build,
catalog update, and artifact commit on every push containing bundle
changes. Acceptance criteria from user stories translate into pytest
integration tests (Given/When/Then → Arrange/Act/Assert) written
before implementation. Python dependencies are dev-only; the installed
bundle contains no Python code.

## Technical Context

**Language/Version**: YAML + Markdown (bundle artifacts), Bash 3.2+
(macOS-compatible pre-push hook and setup script), Python 3.11+
(dev-only testing)

**Primary Dependencies**:
- `specify` CLI (Spec Kit bundle management)
- `pytest` (dev-only, integration tests)
- Git 2.9+ (`core.hooksPath` support)

**Storage**: File-based bundle manifest, catalog, and zip artifact

**Testing**: pytest — integration tests follow Given/When/Then from
acceptance scenarios, mapped to Arrange/Act/Assert pattern. Tests
shell out to `specify` CLI commands and verify outputs. Bash scripts
tested via `subprocess.run()`.

**Target Platform**: Spec Kit projects using the `claude` integration;
macOS / Linux developer workstations

**Project Type**: Spec Kit bundle (distribution package) + developer
tooling (git hooks)

**Performance Goals**: Bundle install is a one-time CLI operation.
Hook execution under 10 seconds for typical bundle builds.

**Constraints**: Bundle MUST NOT contain Python code or dev
dependencies. Bundle artifact (`.zip`) contains only YAML, Markdown,
and JSON files. Bash 3.2+ portability (macOS default). No jq/yq
required.

**Scale/Scope**: Scaffold — 1 skill, 1 bundle manifest, 1 catalog
file, 1 pre-push hook, 1 setup script. Designed to grow incrementally.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1
design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Composition Over Creation | PASS | Bundle composes a skill (SK component type); no runtime behavior added. Hook uses existing `specify bundle validate` and `specify bundle build` commands. |
| II. Spec Kit Native | PASS | Uses `bundle.yml`, `specify bundle` CLI, catalog stack — all SK primitives |
| III. Documentation-Driven | PASS | Consulted SK bundle docs; bundle.yml structure and catalog format researched |
| IV. Idempotent & Traceable | PASS | SK handles idempotency and provenance via its bundle install machinery. Setup script is idempotent. Hook produces deterministic output. |
| V. Version-Pinned Distribution | PASS | `bundle.yml` provides section pins component versions explicitly. Catalog entry version synced from manifest. |
| VI. Test-Driven Development | PASS | Tests written first via pytest; bash scripts tested via subprocess pattern |

All gates pass. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/001-bundle-install/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── bundle-manifest.md
│   ├── catalog-file.md
│   ├── catalog-update.md
│   └── hook-exit-codes.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
trasgospec/                         # Project root
├── bundle/                         # Bundle source (input for specify bundle build)
│   ├── bundle.yml                  # Bundle manifest (FR-001)
│   ├── README.md                   # Bundle README (required by build)
│   └── skills/
│       └── trasgospec/
│           └── SKILL.md            # /trasgospec hello command (FR-011)
├── catalog.json                    # Self-hosted catalog (FR-010)
├── .githooks/
│   └── pre-push                    # Pre-push hook script (FR-013–FR-022)
├── scripts/
│   └── setup.sh                    # Developer setup script (FR-023–FR-024)
├── tests/                          # Dev-only (NOT in bundle artifact)
│   ├── unit/
│   │   ├── test_pre_push_hook.py   # Hook unit tests
│   │   └── test_setup.py           # Setup script tests
│   └── integration/
│       ├── conftest.py             # Shared fixtures
│       ├── test_us1_install.py     # US1 acceptance scenarios
│       └── test_edge_cases.py      # Edge case scenarios
├── requirements-dev.txt            # pytest (dev-only)
├── .python-version                 # Python version for pyenv
├── .envrc                          # direnv: auto-activate .venv on cd
├── .gitignore                      # .venv/, __pycache__/, *.pyc, dist/
├── .specify/                       # Default SK assets (NOT bundled)
├── .claude/
│   └── skills/
│       └── speckit-*/              # Default SK skills (NOT bundled)
└── specs/                          # Feature specs (NOT bundled)
```

**Structure Decisions**:
- Bundle source files live in `bundle/` (separate from project root) so
  `specify bundle build --path bundle/` produces a clean artifact
  without dev files.
- `catalog.json` lives at the project root for HTTP serving during
  tests.
- `.githooks/` is a tracked directory (git convention) separate from
  `bundle/scripts/bash/` which holds bundle-distributed scripts. The
  hook and setup script are internal developer tools, not
  consumer-facing bundle features.
- Tests are at `tests/` with unit and integration subdirectories.
- The `.venv/` is auto-activated via direnv.
